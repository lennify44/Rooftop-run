// Shared helpers for the course tests: a bot that plays legs of the course with
// the game's own physics (window.rooftop, exposed when the page URL ends in #test).
const G = window.rooftop, p = G.p, B = G.boxes;
G.running = false;
let DT = 1 / 180;                 // one physics substep at 60 fps
let T = 0;
const keys = G.keys;
const top = b => b.y + b.h / 2;
function clearKeys() { for (const k in keys) keys[k] = false; }
function step() { T += DT; G.update(DT, T); }
function place(x, y, z) {
  Object.assign(p, { x, y, z, vx: 0, vy: 0, vz: 0, ground: null, wasGround: null, h: 1.7, crouch: false,
    slideT: 0, slideCD: 0, wallT: 0, buffer: 0, coyote: 0, jumpCut: false, run: 1.8 });
}
function aim(tx, tz) { G.yaw = Math.atan2(-(tx - p.x), -(tz - p.z)); }
function onTop(b, x, z, m = 0) { return Math.abs(x - b.x) <= b.w / 2 - m && Math.abs(z - b.z) <= b.d / 2 - m; }
function jump() { p.buffer = 0.12; keys.Space = true; }
function settle(n = 20) { for (let i = 0; i < n; i++) step(); }
const pt = v => (typeof v === 'function' ? v() : v);
// where a player looks when heading for box t: the near part of its top, 1 m in from the edge
function aimPoint(t, nextT) {
  if (t.kind === 'pad' && nextT) {        // springboard: aim past the middle so speed carries into the bounce
    const dx = nextT.x - t.x, dz = nextT.z - t.z, L = Math.hypot(dx, dz) || 1;
    return [t.x + dx / L * (t.w / 2 - 0.3), t.z + dz / L * (t.d / 2 - 0.3)];
  }
  const mx = Math.min(0.35, t.w / 4), mz = Math.min(0.35, t.d / 4);
  let ax = Math.max(t.x - t.w / 2 + mx, Math.min(t.x + t.w / 2 - mx, p.x));
  let az = Math.max(t.z - t.d / 2 + mz, Math.min(t.z + t.d / 2 - mz, p.z));
  const dx = t.x - ax, dz = t.z - az, L = Math.hypot(dx, dz);
  if (L > 0) { const k = Math.min(1, 1 / L); ax += dx * k; az += dz * k; }
  return [ax, az];
}

function farSide(A, tx, tz, m = 0.35) {
  const dx = A.x - tx, dz = A.z - tz, L = Math.hypot(dx, dz) || 1;
  const ux = dx / L, uz = dz / L;
  let s = 0;
  while (onTop(A, A.x + ux * (s + 0.02), A.z + uz * (s + 0.02), m)) s += 0.02;
  return [A.x + ux * s, A.z + uz * s];
}

// Air control like a skilled player: work out the horizontal velocity that lands on
// the near part of `cur`, then face and press W along the change still needed.
function airControl(cur, sprint, nextT) {
  const ap = aimPoint(cur, nextT);
  const dy = p.y - top(cur), disc = p.vy * p.vy + 56 * dy;
  const speed = sprint ? 9.2 : 5.8;
  let dvx, dvz;
  if (disc >= 0) {
    const tl = Math.max(0.05, (p.vy + Math.sqrt(disc)) / 28);
    dvx = (ap[0] - p.x) / tl - p.vx; dvz = (ap[1] - p.z) / tl - p.vz;
  } else {
    const dx = ap[0] - p.x, dz = ap[1] - p.z, L = Math.hypot(dx, dz) || 1;
    dvx = dx / L * speed - p.vx; dvz = dz / L * speed - p.vz;
  }
  const dl = Math.hypot(dvx, dvz);
  keys.KeyS = keys.KeyA = keys.KeyD = false;
  if (dl < 0.15) { keys.KeyW = false; keys.ShiftLeft = false; return; }
  const dx = dvx / dl, dz = dvz / dl;
  const b = p.vx * dx + p.vz * dz, c = p.vx * p.vx + p.vz * p.vz - speed * speed;
  const lam = -b + Math.sqrt(Math.max(0, b * b - c));
  const wx = p.vx + lam * dx, wz = p.vz + lam * dz;
  G.yaw = Math.atan2(-wx, -wz);
  keys.KeyW = true; keys.ShiftLeft = sprint;
}

// Run-and-jump leg with air control like a player: aims at the current target,
// brakes (S) in the air when the landing would overshoot it, pushes on when short.
// o.targets: boxes to touch in order (pads, then the landing box). o.walk: no sprint.
function leg(o) {
  const { A } = o;
  const targets = o.targets || [o.Bt];
  const Bt = targets[targets.length - 1];
  if (o.phase !== undefined) { T = o.phase; G.update(0, T); }
  const long = A.w / A.d > 4 || A.d / A.w > 4;              // a beam: run along it first
  const runTo = () => {
    const t0 = targets[0];
    if (!long) return aimPoint(t0, targets[1]);
    return A.d > A.w ? [A.x, A.z + Math.sign(t0.z - A.z) * A.d / 2] : [A.x + Math.sign(t0.x - A.x) * A.w / 2, A.z];
  };
  const r = runTo();
  const s = o.start || farSide(A, r[0], r[1]);
  place(s[0], top(A), s[1]);
  clearKeys(); settle();
  let jumped = false, t = 0, ti = 0, prevVy = 0;
  const early = o.early || 0;
  while (t < (o.maxT || 6)) {
    const cur = targets[ti];
    if (!jumped) {
      const rr = runTo(); aim(rr[0], rr[1]);
      keys.KeyW = true; keys.ShiftLeft = !o.walk;
      const sp = Math.hypot(p.vx, p.vz) || 1;
      const ax = p.x + p.vx / sp * early, az = p.z + p.vz / sp * early;
      if (!p.ground || (early > 0 && p.ground === A && !onTop(A, ax, az, -0.3))) { jump(); jumped = true; }
    } else {
      airControl(cur, !o.walk, targets[ti + 1]);
    }
    step(); t += DT;
    if (p.ground === Bt) return { ok: true };
    if (p.vy > 15 && prevVy < 5 && targets[ti].kind === 'pad') ti = Math.min(ti + 1, targets.length - 1);   // bounced: next target
    prevVy = p.vy;
    if (p.ground && p.ground !== A && !targets.includes(p.ground)) return { ok: false, why: 'landed on #' + B.indexOf(p.ground) };
    if (p.y < Math.min(top(A), top(Bt), ...targets.map(top)) - 4) return { ok: false, why: 'fell', at: [+p.x.toFixed(1), +p.y.toFixed(1), +p.z.toFixed(1)] };
  }
  return { ok: false, why: 'timeout' };
}

function wallrun(A, wall, L, variant) {
  const face = wall.x + wall.w / 2 + 0.3;                 // player centre when touching the inner face
  const entry = [face, wall.z - wall.d / 2 + 2.5];
  place(A.x, top(A), A.z - A.d / 2 + 0.4);
  clearKeys(); settle();
  keys.KeyW = true; keys.ShiftLeft = true;
  let jumped = false, touched = false, wj = false, t = 0, maxRun = 0;
  while (t < 5) {
    if (p.wallT > 0) touched = true;
    if (!touched) aim(entry[0], entry[1]);
    else if (p.z < wall.z + wall.d / 2 && !wj) G.yaw = Math.PI;       // straight along the wall (+z)
    else aim(L.x, L.z);
    if (!jumped && !p.ground) { jump(); jumped = true; }
    if (variant === 'walljump' && touched && !wj && p.wallT > 0 && p.z > wall.z + wall.d / 2 - 1.0) { jump(); wj = true; }
    step(); t += DT;
    if (p.wallRunning) maxRun += DT;
    if (p.ground === L) return { ok: true, wallRunTime: +maxRun.toFixed(2) };
    if (p.ground && p.ground !== A) return { ok: false, why: 'landed on #' + B.indexOf(p.ground) };
    if (p.y < top(L) - 4) return { ok: false, why: 'fell', at: [+p.x.toFixed(1), +p.y.toFixed(1), +p.z.toFixed(1)], touched, wallRunTime: +maxRun.toFixed(2) };
  }
  return { ok: false, why: 'timeout' };
}

function chimney(C, exit, trigVy) {
  place(C.x, top(C), C.z);
  clearKeys(); settle();
  G.yaw = Math.PI;                  // facing +z (towards the exit): KeyD moves -x, KeyA moves +x
  keys.KeyW = true;                 // walk to the exit end of the chimney first
  let t = 0;
  while (p.z < C.z + C.d / 2 - 1.3 && t < 2) { step(); t += DT; }
  keys.KeyW = false;
  for (let i = 0; i < 60; i++) { step(); t += DT; }     // come to a stop
  let side = 'KeyD', jumps = 0, exiting = false;
  keys[side] = true; jump();
  while (t < 10) {
    const apex = p.y + Math.max(0, p.vy) ** 2 / 56;
    if (!exiting && p.vy > 0 && apex > top(exit) + 1.0) { exiting = true; keys.KeyA = keys.KeyD = false; keys.KeyW = true; }
    if (!exiting && p.wallT > 0 && !p.ground && p.vy < trigVy) {
      jump(); jumps++;
      keys[side] = false; side = side === 'KeyD' ? 'KeyA' : 'KeyD'; keys[side] = true;
    }
    if (p.ground === C && t > 0.3) { jump(); }
    step(); t += DT;
    if (p.ground === exit) return { ok: true, wallJumps: jumps };
    if (p.y < top(C) - 4) return { ok: false, why: 'fell', wallJumps: jumps };
  }
  return { ok: false, why: 'timeout', maxY: +p.y.toFixed(2), wallJumps: jumps };
}

function slide(A, roof, bars, goal, finalAt) {
  place(A.x - A.w / 2 + 0.4, top(A), A.z);
  clearKeys(); settle();
  keys.KeyW = true; keys.ShiftLeft = true;
  let jumped = false, finalSlide = false, t = 0;
  const edge = roof.x + roof.w / 2;
  while (t < 6) {
    aim(goal.x, goal.z);
    const nearBar = bars.some(b => p.x > b.x - 3.2 && p.x < b.x + 0.9);
    if (!finalSlide && p.x > edge - finalAt) { finalSlide = true; keys.KeyC = false; step(); keys.KeyC = true; }
    else if (!finalSlide) keys.KeyC = nearBar;
    if (!jumped && !p.ground && p.x > edge - 1) { jump(); jumped = true; }
    step(); t += DT;
    if (p.ground === goal) return { ok: true, t: +t.toFixed(2), speedAtEnd: +Math.hypot(p.vx, p.vz).toFixed(1) };
    if (p.y < top(roof) - 4) return { ok: false, why: 'fell', at: [+p.x.toFixed(1), +p.z.toFixed(1)] };
    if (t > 1 && Math.hypot(p.vx, p.vz) < 0.5 && p.ground) return { ok: false, why: 'stuck', at: [+p.x.toFixed(1), +p.z.toFixed(1)], crouch: p.crouch };
  }
  return { ok: false, why: 'timeout', at: [+p.x.toFixed(1), +p.z.toFixed(1)] };
}

