"""Touch controls (Fire Escape layout) with synthetic finger input at phone size: python touch.py
Left half: floating stick. Right half: jump zone (tap/hold), Slide circle inside it, rolling
from Slide onto the jump zone jumps out of the slide; any right-hand drag turns the camera."""
import os, sys, time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = 'file://' + os.path.join(os.path.dirname(HERE), 'index.html') + '#test'

opts = Options(); opts.add_argument('-headless')
d = webdriver.Firefox(options=opts)
js = d.execute_script
failed = 0


def check(name, ok, info=''):
    global failed
    failed += 0 if ok else 1
    print('  ' + ('ok  ' if ok else 'FAIL'), name, info)


def finger(el_id, kind, x, y, pid):
    js(f"""document.getElementById('{el_id}').dispatchEvent(new PointerEvent('{kind}', {{ pointerType: 'touch', pointerId: {pid},
        clientX: {x}, clientY: {y}, bubbles: true, cancelable: true }}))""")


def center(el_id):
    return js(f"const r = document.getElementById('{el_id}').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]")


st = lambda: js('return {y: rooftop.p.y, vy: rooftop.p.vy, v: Math.hypot(rooftop.p.vx, rooftop.p.vz), yaw: rooftop.yaw, slide: rooftop.p.slideT > 0, crouch: rooftop.p.crouch}')

try:
    d.set_window_size(844, 390)   # phone, landscape
    d.get(PAGE); time.sleep(3)
    js("localStorage.clear()"); d.refresh(); time.sleep(3)
    finger('zone-l', 'pointerdown', 10, 10, 99); finger('zone-l', 'pointerup', 10, 10, 99)
    check('first touch switches to touch controls', js("return document.body.classList.contains('touch')"))
    check('keyboard help hidden, mouse settings hidden',
          js("return document.getElementById('keyshelp').hidden && document.getElementById('mouserow').hidden"))
    js("document.getElementById('go').click()"); time.sleep(0.4)
    check('touch layer shown while playing', js("return rooftop.running && !document.getElementById('touch').hidden"))
    W, Hh = js('return [innerWidth, innerHeight]')

    z0 = js('return rooftop.p.z')
    finger('zone-l', 'pointerdown', 120, 200, 11)
    finger('zone-l', 'pointermove', 120, 170, 11); time.sleep(0.6)
    v1 = st()['v']
    finger('zone-l', 'pointermove', 120, 90, 11); time.sleep(0.3)       # past the rim: the stick follows
    v2 = st()['v']
    check('stick half push walks', abs(v1 - 5.8) < 0.3, f'{v1:.1f} m/s')
    check('stick pushed to the edge runs', abs(v2 - 9.2) < 0.3, f'{v2:.1f} m/s')
    check('stick follows the thumb past the rim', js("return parseFloat(document.getElementById('stick').style.top)") < 200 - 60 - 20)
    check('player moved forward', js('return rooftop.p.z') < z0 - 2)
    finger('zone-l', 'pointerup', 120, 90, 11); time.sleep(0.4)

    js('rooftop.respawn(false)'); time.sleep(0.3)
    a = st()
    finger('zone-r', 'pointerdown', W * 0.75, Hh * 0.12, 12); finger('zone-r', 'pointermove', W * 0.75 + 60, Hh * 0.12, 12); finger('zone-r', 'pointerup', W * 0.75 + 60, Hh * 0.12, 12)
    time.sleep(0.2); b = st()
    check('drag in the top strip turns the view', abs((b['yaw'] - a['yaw']) + 0.36) < 0.02, f"yaw change {b['yaw'] - a['yaw']:.3f}")
    check('and does not jump', b['y'] < 0.05, f"y = {b['y']:.2f}")

    jx, jy = center('b-jump')
    finger('zone-r', 'pointerdown', jx, jy, 13); time.sleep(0.15)
    check('tap in the jump zone jumps', st()['y'] > 0.5, f"y = {st()['y']:.2f}")
    y0 = st()['yaw']
    finger('zone-r', 'pointermove', jx - 40, jy, 13)
    check('dragging the jump finger also turns the view', st()['yaw'] - y0 > 0.2, f"yaw change {st()['yaw'] - y0:.3f}")
    finger('zone-r', 'pointerup', jx - 40, jy, 13); time.sleep(1.0)

    # slide jump: run, put the thumb on Slide, roll it onto the jump zone
    js('rooftop.respawn(false)'); time.sleep(0.3)
    finger('zone-l', 'pointerdown', 120, 200, 14); finger('zone-l', 'pointermove', 120, 90, 14); time.sleep(0.5)
    sx, sy = center('b-slide')
    finger('zone-r', 'pointerdown', sx, sy, 15); time.sleep(0.1)
    c = st()
    check('Slide circle slides while running', c['slide'], c)
    jx, jy = center('b-jump')
    finger('zone-r', 'pointermove', jx, jy, 15); time.sleep(0.06)
    e = st()
    check('rolling from Slide onto the jump zone jumps out of the slide, keeping its speed', e['vy'] > 2 and e['v'] > 9.5, e)
    finger('zone-r', 'pointerup', jx, jy, 15); finger('zone-l', 'pointerup', 120, 90, 14); time.sleep(1.0)

    cam0 = js('return rooftop.cam')
    tx, ty = center('t-cam'); finger('t-cam', 'pointerdown', tx, ty, 16); finger('t-cam', 'pointerup', tx, ty, 16)
    check('Cam button switches the camera', js('return rooftop.cam') != cam0, f"{cam0} -> {js('return rooftop.cam')}")
    tx, ty = center('t-pause'); finger('t-pause', 'pointerdown', tx, ty, 17); finger('t-pause', 'pointerup', tx, ty, 17); time.sleep(0.2)
    check('Pause button pauses', not js('return rooftop.running') and js("return !document.getElementById('menu').hidden"))
    check('touch layer hidden in the menu', js("return document.getElementById('touch').hidden"))
    check('no error banner', js("return document.getElementById('err').hidden"), js("return document.getElementById('err').textContent"))

    d.set_window_size(500, 900); time.sleep(0.5)   # portrait
    check('no sideways scrolling in portrait', not js('return document.documentElement.scrollWidth > innerWidth'))
finally:
    d.quit()
print('failures:', failed)
sys.exit(1 if failed else 0)
