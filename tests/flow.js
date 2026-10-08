// Game flow: checkpoints in order, finish, best time, respawn, practice, pause.
const out = [];
const check = (name, cond, extra) => out.push({ check: name, ok: !!cond, ...(extra ? { info: extra } : {}) });
const path = B.filter(b => b.kind !== 'wall' && b.kind !== 'bar');
const pads = B.filter(b => b.kind === 'pad'), bars = B.filter(b => b.kind === 'bar');
const roof = path.find(b => b.w > 10);
try { localStorage.removeItem('rooftop-best-v3'); } catch (e) {}
G.startFrom(0);            // full run: resets state, running = true
G.running = false;         // the bot steps physics itself
const menuHidden = () => document.getElementById('menu').hidden;
check('start hides the menu', menuHidden());
// play every leg in order, stopping at the goal
for (let i = 0; i + 1 < path.length; i++) {
  const A = path[i], Bt = path[i + 1];
  if (Bt.kind === 'pad' || A.kind === 'pad' || A === roof || Bt === roof || Bt === G.goal) continue;
  let r;
  if (A.cpIndex && B[B.indexOf(A) + 1].kind === 'wall' && B[B.indexOf(A) + 2].kind === 'wall') r = chimney(A, Bt, 1);
  else if (B[B.indexOf(Bt) - 1].kind === 'wall') r = wallrun(A, B[B.indexOf(Bt) - 1], Bt, 'runoff');
  else if (A.kind === 'move' || Bt.kind === 'move') { for (let k = 0; k < 24 && !(r = leg({ A, Bt, phase: 50 + k * 0.731 })).ok; k++); }
  else r = leg({ A, Bt });
  if (!r.ok) out.push({ leg: B.indexOf(A) + '->' + B.indexOf(Bt), ok: false, r });
  if (Bt.cpIndex) check('checkpoint ' + Bt.cpIndex + ' registered', G.cpReached === Bt.cpIndex, G.cpReached);
}
leg({ A: path[path.indexOf(pads[0]) - 1], targets: [pads[0], path[path.indexOf(pads[0]) + 1]] });
check('checkpoint 7 via pad', G.cpReached === 7, G.cpReached);
leg({ A: path[path.indexOf(pads[1]) - 1], targets: [pads[1], pads[2], path[path.indexOf(pads[2]) + 1]] });
check('checkpoint 8 via pads', G.cpReached === 8, G.cpReached);
const s = slide(path[path.indexOf(roof) - 1], roof, bars, G.goal, 2.5);
check('reached the goal', s.ok, s);
check('finish() ran', G.finished);
check('menu shown after finish', !menuHidden());
check('finish message', /Gold roof reached/.test(document.getElementById('msg').textContent), document.getElementById('msg').textContent);
check('Play button says Run again', document.getElementById('go').textContent === 'Run again');
let best = null; try { best = JSON.parse(localStorage.getItem('rooftop-best-v3')); } catch (e) {}
check('best run saved with 8 splits', best && best.splits && best.splits.filter(x => x != null).length === 8, best && { time: best.time, splits: best.splits.length });
// fall + respawn
G.startFrom(3); G.running = false;
check('practice start sets checkpoint 3', G.cpReached === 3 && Math.abs(p.x - G.checkpoints[2].x) < 0.01);
const f0 = G.falls;
place(p.x + 30, p.y + 2, p.z);          // over the void
for (let i = 0; i < 400 && G.falls === f0; i++) step();
check('falling respawns at the checkpoint', G.falls === f0 + 1 && Math.abs(p.x - G.checkpoints[2].x) < 0.01, { falls: G.falls, x: p.x });
// R key while running
G.running = true;
p.x += 1.5;
dispatchEvent(new KeyboardEvent('keydown', { code: 'KeyR' })); dispatchEvent(new KeyboardEvent('keyup', { code: 'KeyR' }));
check('R returns to the checkpoint', Math.abs(p.x - G.checkpoints[2].x) < 0.01);
dispatchEvent(new KeyboardEvent('keydown', { code: 'Space' }));
check('Space sets a buffered jump while running', p.buffer > 0);
dispatchEvent(new KeyboardEvent('keyup', { code: 'Space' }));
// pause / resume
dispatchEvent(new KeyboardEvent('keydown', { code: 'KeyP' })); dispatchEvent(new KeyboardEvent('keyup', { code: 'KeyP' }));
check('P pauses', !G.running && !menuHidden() && document.getElementById('go').textContent === 'Resume');
document.getElementById('go').click();
check('Resume continues the practice run', G.running && G.cpReached === 3 && menuHidden());
G.running = false;
// practice finish must not overwrite the best
const bestBefore = localStorage.getItem('rooftop-best-v3');
G.startFrom(8); G.running = false;
slide(path[path.indexOf(roof) - 1], roof, bars, G.goal, 2.5);
check('practice run finishes', G.finished);
check('practice run does not change the best', localStorage.getItem('rooftop-best-v3') === bestBefore);
check('practice finish message', /practising from checkpoint 8/.test(document.getElementById('msg').textContent), document.getElementById('msg').textContent);
check('no error banner', document.getElementById('err').hidden, document.getElementById('err').textContent);
report = out;
