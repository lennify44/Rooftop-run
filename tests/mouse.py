"""Mouse look with Firefox's native input path (headless): a capture that cannot hold the
pointer (it reports the pointer position instead of its movement, which sent the camera
straight up on a GNOME/Wayland Firefox) must switch to follow-cursor without the view running
off; a healthy capture must stay captured, including during fast flicks. python mouse.py"""
import os, sys, time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By

PAGE = 'file://' + os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'index.html') + '#test'
opts = Options(); opts.add_argument('-headless')
d = webdriver.Firefox(options=opts, service=Service(service_args=['--allow-system-access'])); d.set_window_size(1280, 800)
js = d.execute_script
MOVE = """const [x, y] = arguments; const win = Services.wm.getMostRecentWindow('navigator:browser'); const u = win.windowUtils;
const b = win.gBrowser.selectedBrowser; const r = b.getBoundingClientRect(); const s = win.devicePixelRatio;
u.sendNativeMouseEvent((win.mozInnerScreenX + r.left + x) * s, (win.mozInnerScreenY + r.top + y) * s, u.NATIVE_MOUSE_MESSAGE_MOVE, 0, 0, b, null);"""
def nmove(x, y):
    d.set_context('chrome'); d.execute_script(MOVE, x, y); d.set_context('content')
st = lambda: js('return {yaw: +rooftop.yaw.toFixed(3), pitch: +rooftop.pitch.toFixed(3), locked: rooftop.locked, mode: rooftop.mouseMode}')
fails = 0
def check(name, ok, info=''):
    global fails; fails += 0 if ok else 1; print(('ok   ' if ok else 'FAIL ') + name, info)
try:
    # 1) broken capture (pointer not held): native input
    d.get(PAGE); time.sleep(3)
    js("localStorage.clear()"); d.refresh(); time.sleep(3)
    nmove(300, 200)
    d.find_element(By.ID, 'go').click(); time.sleep(0.8)
    check('capture granted', st()['locked'])
    for i in range(10): nmove(300 + i * 5, 200); time.sleep(0.04)
    time.sleep(0.4); a = st()
    check('broken capture detected, switched to follow', a['mode'] == 'follow' and not a['locked'], a)
    check('camera did not run off while judging', abs(a['pitch']) < 0.1 and abs(a['yaw']) < 0.2, a)
    for i in range(15): nmove(360 + i * 10, 200); time.sleep(0.04)
    time.sleep(0.3); b = st()
    check('then moving right turns right', -0.45 < b['yaw'] - a['yaw'] < -0.2, f"yaw change {b['yaw'] - a['yaw']:.3f}")
    check('and horizontal moves leave pitch alone', abs(b['pitch'] - a['pitch']) < 0.02, b)
    for i in range(10): nmove(500, 200 - i * 10); time.sleep(0.04)
    time.sleep(0.3); c = st()
    check('moving up looks up, moving stops it', 0.15 < c['pitch'] - b['pitch'] < 0.3, f"pitch change {c['pitch'] - b['pitch']:.3f}")
    time.sleep(0.5); c2 = st()
    check('no drift when the mouse rests', c2['pitch'] == c['pitch'] and c2['yaw'] == c['yaw'])
    d.refresh(); time.sleep(3)
    check('follow mode remembered on reload', js('return rooftop.mouseMode') == 'follow')

    # 2) healthy capture: small real-mouse steps (synthetic, movement values as a working lock gives them)
    js("localStorage.clear()"); d.refresh(); time.sleep(3)
    d.find_element(By.ID, 'go').click(); time.sleep(0.8)
    y0 = st()['yaw']
    js("for (let i = 0; i < 40; i++) dispatchEvent(new MouseEvent('mousemove', {movementX: 3 + (i % 4), movementY: i % 3 - 1}))")
    e = st()
    check('healthy capture stays captured', e['mode'] == 'capture' and e['locked'], e)
    check('and turns by the reported movement', abs((e['yaw'] - y0) + 180 * 0.0022) < 0.02, f"yaw change {e['yaw'] - y0:.3f}")
    js("for (const v of [90, 110, 100, 95, 125, 105, 98, 102, 80, 60]) dispatchEvent(new MouseEvent('mousemove', {movementX: v, movementY: 5}))")
    f = st()
    check('a fast flick does not trigger the fallback', f['mode'] == 'capture' and f['locked'], f)
    check('and the flick turns the view', f['yaw'] - e['yaw'] < -1.5, f"yaw change {f['yaw'] - e['yaw']:.3f}")
    check('no error banner', js("return document.getElementById('err').hidden"))
finally:
    d.quit()
print('failures:', fails)
sys.exit(1 if fails else 0)
