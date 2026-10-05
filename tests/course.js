// Plays every leg of the course; each line says whether and how it can be done.
// ---------- run the course ----------
const path = B.filter(b => b.kind !== 'wall' && b.kind !== 'bar');
const walls = B.filter(b => b.kind === 'wall');
const bars = B.filter(b => b.kind === 'bar');
const pads = B.filter(b => b.kind === 'pad');
const goal = G.goal;
const roof = path.find(b => b.w > 10);
const name = b => (b.cpIndex ? 'CP' + b.cpIndex : b.kind === 'goal' ? 'goal' : b.kind + '#' + B.indexOf(b));
const next = b => B[B.indexOf(b) + 1];
for (let i = 0; i + 1 < path.length; i++) {
  const A = path[i], Bt = path[i + 1];
  const label = name(A) + ' -> ' + name(Bt);
  if (A.kind === 'pad' || Bt.kind === 'pad' || A === roof || Bt === roof) continue;   // handled below
  if (A.cpIndex && next(A).kind === 'wall' && next(next(A)).kind === 'wall') {
    for (const v of [0, 1, 2.5]) report.push({ leg: label + ` (chimney, wall-jump when vy < ${v})`, ...chimney(A, Bt, v) });
    continue;
  }
  const wallBefore = walls.find(w => next(w) === Bt);
  if (wallBefore) {
    report.push({ leg: label + ' (wall run, run off the end)', ...wallrun(A, wallBefore, Bt, 'runoff') });
    report.push({ leg: label + ' (wall run + wall jump at the end)', ...wallrun(A, wallBefore, Bt, 'walljump') });
    continue;
  }
  if (A.kind === 'move' || Bt.kind === 'move') {
    const r = {};
    for (const walk of [false, true]) {
      let n = 0;
      for (let k = 0; k < 24; k++) if (leg({ A, Bt, phase: 50 + k * 0.731, walk }).ok) n++;
      r[walk ? 'walk' : 'sprint'] = n + '/24 start moments work';
    }
    report.push({ leg: label + ' (moving)', ...r });
    continue;
  }
  const r = {};
  for (const walk of [false, true]) {
    const ok = [0, 0.2, 0.4, 0.7].filter(e => leg({ A, Bt, early: e, walk }).ok);
    r[walk ? 'walk' : 'sprint'] = ok.length ? 'jump ' + ok.join('/') + ' m before edge' : 'NO';
  }
  report.push({ leg: label, rise: +(top(Bt) - top(A)).toFixed(1), ...r });
}
// pad chains
{
  const p1 = pads[0], from = path[path.indexOf(p1) - 1], to = path[path.indexOf(p1) + 1];
  for (const walk of [false, true]) for (const e of [0, 0.3])
    report.push({ leg: `${name(from)} -> pad -> ${name(to)} (${walk ? 'walk' : 'sprint'}, early ${e})`, ...leg({ A: from, targets: [p1, to], early: e, walk }) });
  const p2 = pads[1], p3 = pads[2], from2 = path[path.indexOf(p2) - 1], to2 = path[path.indexOf(p3) + 1];
  for (const walk of [false, true]) for (const e of [0, 0.3])
    report.push({ leg: `${name(from2)} -> pad -> pad -> ${name(to2)} (${walk ? 'walk' : 'sprint'}, early ${e})`, ...leg({ A: from2, targets: [p2, p3, to2], early: e, walk }) });
}
// slide roof
{
  const A = path[path.indexOf(roof) - 1];
  for (const f of [1.5, 2.5, 3.5]) report.push({ leg: `${name(A)} -> roof -> goal (slide jump, slide ${f} m before edge)`, ...slide(A, roof, bars, goal, f) });
  report.push({ leg: 'roof -> goal, plain sprint jump (must fail)', ...leg({ A: roof, Bt: goal, start: [roof.x + roof.w / 2 - 3, roof.z] }) });
}
