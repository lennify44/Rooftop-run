"""Touch controls with synthetic finger input at phone size: python touch.py"""
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


def finger(target, kind, x, y, pid):
    js(f"""{target}.dispatchEvent(new PointerEvent('{kind}', {{ pointerType: 'touch', pointerId: {pid},
        clientX: {x}, clientY: {y}, bubbles: true, cancelable: true }}))""")


try:
    d.set_window_size(844, 390)   # phone, landscape
    d.get(PAGE); time.sleep(3)
    finger('document.body', 'pointerdown', 10, 10, 99); finger('document.body', 'pointerup', 10, 10, 99)
    check('first touch switches to touch controls', js("return document.body.classList.contains('touch')"))
    check('keyboard help hidden, mouse settings hidden',
          js("return document.getElementById('keyshelp').hidden && document.getElementById('mouserow').hidden"))
    js("document.getElementById('go').click()"); time.sleep(0.4)
    check('touch buttons shown while playing', js("return rooftop.running && !document.getElementById('touch').hidden"))

    pad = "document.getElementById('touch')"
    z0 = js('return rooftop.p.z')
    finger(pad, 'pointerdown', 120, 260, 11)
    finger(pad, 'pointermove', 120, 230, 11); time.sleep(0.6)
    v1 = js('return Math.hypot(rooftop.p.vx, rooftop.p.vz)')
    finger(pad, 'pointermove', 120, 190, 11); time.sleep(0.25)
    v2 = js('return Math.hypot(rooftop.p.vx, rooftop.p.vz)')
    check('stick half push walks', abs(v1 - 5.8) < 0.2, f'{v1:.1f} m/s')
    check('stick pushed to the edge sprints', abs(v2 - 9.2) < 0.2, f'{v2:.1f} m/s')
    check('player moved forward', js('return rooftop.p.z') < z0 - 2)
    finger(pad, 'pointerup', 120, 190, 11)

    y0 = js('return rooftop.yaw')
    finger(pad, 'pointerdown', 600, 200, 12); finger(pad, 'pointermove', 660, 200, 12); finger(pad, 'pointerup', 660, 200, 12)
    dy = js('return rooftop.yaw') - y0
    check('right-hand drag turns the view', abs(dy + 0.36) < 0.01, f'{dy:.3f} rad for 60 px')

    js('rooftop.respawn(false)'); time.sleep(0.3)
    finger("document.getElementById('t-jump')", 'pointerdown', 780, 330, 13); time.sleep(0.15)
    check('Jump button jumps', js('return rooftop.p.y') > 0.5, f"y = {js('return rooftop.p.y'):.2f}")
    finger("document.getElementById('t-jump')", 'pointerup', 780, 330, 13)

    js("document.getElementById('t-pause').click()"); time.sleep(0.2)
    check('Pause button pauses', not js('return rooftop.running') and js("return !document.getElementById('menu').hidden"))
    check('touch buttons hidden in the menu', js("return document.getElementById('touch').hidden"))
    check('no error banner', js("return document.getElementById('err').hidden"))

    d.set_window_size(500, 900); time.sleep(0.5)   # portrait
    check('no sideways scrolling in portrait', not js('return document.documentElement.scrollWidth > innerWidth'))
finally:
    d.quit()
print('failures:', failed)
sys.exit(1 if failed else 0)
