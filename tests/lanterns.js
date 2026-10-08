// Every lantern can be collected: plays the leg it hangs over (several take-off timings where
// that applies) and reports whether it was collected and how close the runner's body passed.
const path = B.filter(b => b.kind !== 'wall' && b.kind !== 'bar');
const walls = B.filter(b => b.kind === 'wall'), bars = B.filter(b => b.kind === 'bar'), pads = B.filter(b => b.kind === 'pad');
const cps = n => G.checkpoints[n - 1];
const roof = path.find(b => b.w > 10);

function segDist(l, a, c) {                       // lantern to the line between two pieces, seen from above
  const ex = c.x - a.x, ez = c.z - a.z, L2 = ex * ex + ez * ez || 1;
  const t = Math.max(0, Math.min(1, ((l.x - a.x) * ex + (l.z - a.z) * ez) / L2));
  return Math.hypot(l.x - (a.x + ex * t), l.z - (a.z + ez * t));
}
function attempt(l, fn) {
  l.got = false; l.mesh.visible = true;
  let md = 1e9, at = null;
  const upd = G.update;
  G.update = (dt, t) => {
    upd(dt, t);
    const d = Math.hypot(l.x - p.x, l.y - (p.y + p.h / 2), l.z - p.z);
    if (d < md) { md = d; at = [+(p.y + p.h / 2 - l.y).toFixed(2)]; }
  };
  let r;
  try { r = fn(); } finally { G.update = upd; }
  return { got: l.got, closest: +md.toFixed(2), bodyMinusLantern: at && at[0], legOk: r && r.ok };
}

for (const l of G.lanterns) {
  const row = { lantern: l.where };
  if (l.where === 'wall run') {
    const w = walls.find(x => x.runnable);
    Object.assign(row, attempt(l, () => wallrun(cps(5), w, B[B.indexOf(w) + 1], 'runoff')));
  } else if (l.where === 'chimney') {
    const C = cps(6);
    Object.assign(row, attempt(l, () => chimney(C, B[B.indexOf(C) + 3], 1)));
  } else if (l.where === 'bounce pads') {
    Object.assign(row, attempt(l, () => leg({ A: cps(7), targets: [pads[1], pads[2], cps(8)] })));
  } else if (l.where === 'slide roof') {
    Object.assign(row, attempt(l, () => slide(cps(8), roof, bars, G.goal, 2.5)));
  } else if (l.where === 'moving slabs') {
    const slab = path.filter(b => b.kind === 'move')[1], from = path[path.indexOf(slab) - 1];
    let best = null, n = 0;
    for (let k = 0; k < 12; k++) {
      const res = attempt(l, () => {
        const r = leg({ A: from, Bt: slab, phase: 50 + k * 0.731 });
        if (r.ok) { clearKeys(); for (let i = 0; i < 3 * 180; i++) step(); }   // ride the slab for 3 s
        return r;
      });
      if (res.got) n++;
      if (!best || res.closest < best.closest) best = res;
    }
    Object.assign(row, best, { gotInStarts: n + '/12' });
  } else {
    let A = null, Bt = null, bd = 1e9;
    for (let i = 0; i + 1 < path.length; i++) {
      const d = segDist(l, path[i], path[i + 1]);
      if (d < bd) { bd = d; A = path[i]; Bt = path[i + 1]; }
    }
    const tries = [0, 0.2, 0.4].map(e => attempt(l, () => leg({ A, Bt, early: e })));
    Object.assign(row, tries[0], { gotWithJumpEarly: [0, 0.2, 0.4].filter((e, i) => tries[i].got).join('/') || 'none' });
    row.ok = tries.some(t => t.got);
  }
  if (row.ok === undefined) row.ok = row.got || (row.gotInStarts && !row.gotInStarts.startsWith('0/'));
  report.push(row);
}
