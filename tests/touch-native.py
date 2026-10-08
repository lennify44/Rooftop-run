"""Touch controls through Firefox's own touch pipeline (native touch points, as from a finger),
with the browser set up like a phone: coarse pointer, touch events, landscape phone size.
python touch-native.py"""
import os, sys, time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

PAGE = 'file://' + os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'index.html') + '#test'
opts = Options()
opts.add_argument('-headless')
for k, v in {'ui.primaryPointerCapabilities': 1, 'ui.allPointerCapabilities': 1,   # coarse pointer, no hover
             'dom.w3c_touch_events.enabled': 1, 'dom.w3c_pointer_events.enabled': True}.items():
    opts.set_preference(k, v)
d = webdriver.Firefox(options=opts, service=Service(service_args=['--allow-system-access']))   # chrome context for native touch
d.set_window_size(844, 390)
js = d.execute_script

TOUCH = """
const [id, state, x, y] = arguments;
const win = Services.wm.getMostRecentWindow('navigator:browser'); const u = win.windowUtils;
const b = win.gBrowser.selectedBrowser; const r = b.getBoundingClientRect(); const s = win.devicePixelRatio;
const st = { down: u.TOUCH_CONTACT, move: u.TOUCH_CONTACT, up: u.TOUCH_REMOVE }[state];
u.sendNativeTouchPoint(id, st, (win.mozInnerScreenX + r.left + x) * s, (win.mozInnerScreenY + r.top + y) * s, 1, 90, null);
"""
def touch(pid, state, x, y):
    d.set_context('chrome'); d.execute_script(TOUCH, pid, state, x, y); d.set_context('content')
def drag(pid, x0, y0, x1, y1, steps=8, hold=False):
    touch(pid, 'down', x0, y0); time.sleep(0.05)
    for i in range(1, steps + 1):
        touch(pid, 'move', x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps); time.sleep(0.03)
    if not hold: touch(pid, 'up', x1, y1)
def tap(pid, x, y):
    touch(pid, 'down', x, y); time.sleep(0.08); touch(pid, 'up', x, y); time.sleep(0.3)
def center(el_id):
    return js(f"const r = document.getElementById('{el_id}').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]")

failed = 0
def check(name, ok, info=''):
    global failed
    failed += 0 if ok else 1
    print('  ' + ('ok  ' if ok else 'FAIL'), name, info)

try:
    d.get(PAGE); time.sleep(3)
    check('phone detected (coarse pointer): touch help shown, mouse settings hidden',
          js("return document.body.classList.contains('touch') && !document.getElementById('touchhelp').hidden && document.getElementById('mouserow').hidden"))
    tap(1, *center('go'))
    check('tapping Play starts the game', js('return rooftop.running'))
    check('touch buttons visible', js("return !document.getElementById('touch').hidden"))

    z0 = js('return rooftop.p.z')
    drag(2, 120, 300, 120, 230, hold=True); time.sleep(0.5)          # left thumb pushed up to the edge
    v = js('return Math.hypot(rooftop.p.vx, rooftop.p.vz)')
    check('left thumb pushed to the edge sprints forward', abs(v - 9.2) < 0.3 and js('return rooftop.p.z') < z0 - 1, f'{v:.1f} m/s')
    y0 = js('return rooftop.yaw')
    drag(3, 600, 200, 660, 200)                                      # right thumb drags while the left one holds
    check('right thumb turns the view while moving (two fingers)', js('return rooftop.yaw') - y0 < -0.2,
          f"yaw change {js('return rooftop.yaw') - y0:.3f}")
    touch(2, 'up', 120, 230); time.sleep(0.4)
    v = js('return Math.hypot(rooftop.p.vx, rooftop.p.vz)')
    check('lifting the left thumb stops', v < 0.5, f'{v:.1f} m/s')

    js('rooftop.respawn(false)'); time.sleep(0.3)
    jx, jy = center('t-jump')
    touch(4, 'down', jx, jy); time.sleep(0.15)
    check('Jump button jumps', js('return rooftop.p.y') > 0.4, f"y = {js('return rooftop.p.y'):.2f}")
    touch(4, 'up', jx, jy); time.sleep(0.8)

    check('page did not scroll or zoom', js('return scrollX === 0 && scrollY === 0 && visualViewport.scale === 1'),
          js('return [scrollX, scrollY, visualViewport.scale]'))
    tap(5, *center('t-pause'))
    check('Pause button pauses', not js('return rooftop.running') and js("return !document.getElementById('menu').hidden"))
    check('no error banner', js("return document.getElementById('err').hidden"), js("return document.getElementById('err').textContent"))
finally:
    d.quit()
print('failures:', failed)
sys.exit(1 if failed else 0)
