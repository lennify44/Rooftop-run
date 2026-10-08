"""Real-mouse check on a GNOME (Wayland) desktop: opens a visible Firefox full screen and
moves the real pointer through GNOME's remote-desktop interface, so the movement takes
the same path as a physical mouse (compositor -> Firefox -> page). Run it while you are
at the computer and keep your hands off the mouse until Firefox closes (about a minute).

Writes the measurements to tests/real-mouse-result.json and prints a summary."""
import functools, http.server, json, os, sys, tempfile, threading, time
from gi.repository import Gio, GLib
from selenium import webdriver
from selenium.webdriver.common.by import By

HERE = os.path.dirname(os.path.abspath(__file__))
GAME_DIR = os.path.dirname(HERE)


def serve(directory):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=directory)
    handler.log_message = lambda *a: None
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


# The game on one origin, a host page on another; "localhost" vs "127.0.0.1" makes the
# frame cross-site, like claude.ai's artifact frame.
game = serve(GAME_DIR)
host_dir = tempfile.mkdtemp()
frame_src = f'http://localhost:{game.server_port}/index.html#test'
with open(os.path.join(host_dir, 'frame.html'), 'w') as f:
    f.write('<!doctype html><meta charset="utf-8"><style>html,body{margin:0;height:100%;background:#ddd}'
            '#f{position:absolute;left:80px;top:80px;width:calc(100% - 160px);height:calc(100% - 160px);border:0}</style>'
            f'<iframe id="f" sandbox="allow-scripts allow-same-origin allow-pointer-lock" src="{frame_src}"></iframe>')
host = serve(host_dir)

bus = Gio.bus_get_sync(Gio.BusType.SESSION)
rd = Gio.DBusProxy.new_sync(bus, 0, None, 'org.gnome.Mutter.RemoteDesktop', '/org/gnome/Mutter/RemoteDesktop',
                            'org.gnome.Mutter.RemoteDesktop')
path = rd.call_sync('CreateSession', None, 0, -1).unpack()[0]
ses = Gio.DBusProxy.new_sync(bus, 0, None, 'org.gnome.Mutter.RemoteDesktop', path, 'org.gnome.Mutter.RemoteDesktop.Session')
ses.call_sync('Start', None, 0, -1)


def move(dx, dy):
    ses.call_sync('NotifyPointerMotionRelative', GLib.Variant('(dd)', (float(dx), float(dy))), 0, -1)


def sweep(n, dx, dy, pause):
    for _ in range(n):
        move(dx, dy)
        time.sleep(pause)


RECORD = """window.__mv = [];
addEventListener('mousemove', e => __mv.push([e.movementX, e.movementY, e.clientX, e.clientY, rooftop.locked ? 1 : 0, rooftop.mouseMode]), true);"""
STATE = "return {yaw: rooftop.yaw, locked: rooftop.locked, mode: rooftop.mouseMode, running: rooftop.running}"

# (name, pointer motion per step, steps, seconds between steps): expected total in px
PHASES = [('fast right', (10, 0), 20, 0.008), ('slow right (sub-pixel steps)', (0.4, 0), 100, 0.004),
          ('fast left', (-10, 0), 20, 0.008), ('hold still', (0, 0), 0, 0.5)]

d = webdriver.Firefox()
results = []
try:
    d.fullscreen_window()
    cases = [('page, capture', f'http://127.0.0.1:{game.server_port}/index.html#test', False, 'capture'),
             ('page, follow cursor', f'http://127.0.0.1:{game.server_port}/index.html#test', False, 'follow'),
             ('cross-site frame (like claude.ai), capture', f'http://127.0.0.1:{host.server_port}/frame.html', True, 'capture'),
             ('cross-site frame (like claude.ai), follow cursor', f'http://127.0.0.1:{host.server_port}/frame.html', True, 'follow')]
    for name, url, framed, mode in cases:
        d.switch_to.default_content()
        d.get('about:blank'); d.get(url); time.sleep(3)
        sweep(8, 25, 15, 0.01); sweep(8, -25, -15, 0.01)          # pointer over the window
        if framed:
            d.switch_to.frame(d.find_element(By.ID, 'f'))
        d.execute_script(f"localStorage.removeItem('rooftop-mouse'); document.getElementById('m-{mode}').click()")
        d.find_element(By.ID, 'go').click()
        time.sleep(1.0)
        d.execute_script(RECORD)
        case = {'case': name, 'start': d.execute_script(STATE), 'phases': []}
        for pname, (dx, dy), n, pause in PHASES:
            d.execute_script('__mv.length = 0')
            y0 = d.execute_script('return rooftop.yaw')
            if n:
                sweep(n, dx, dy, pause)
            else:
                time.sleep(pause)
            time.sleep(0.3)
            mv = d.execute_script('return __mv')
            st = d.execute_script(STATE)
            mx = [e[0] for e in mv]
            case['phases'].append({
                'phase': pname, 'pointerMovedPx': round(dx * n, 1), 'events': len(mv),
                'zeroMovementEvents': sum(1 for e in mv if e[0] == 0 and e[1] == 0),
                'sumMovementX': sum(mx), 'maxAbsMovement': max([abs(v) for e in mv for v in e[:2]] or [0]),
                'clientXSpan': (mv[-1][2] - mv[0][2]) if mv else 0,
                'yawChange': round(st['yaw'] - y0, 3), 'lockedAfter': st['locked'], 'modeAfter': st['mode'],
                'firstEvents': mv[:6]})
        d.execute_script('document.exitPointerLock && document.exitPointerLock()')
        time.sleep(0.3)
        results.append(case)
finally:
    d.quit()
    ses.call_sync('Stop', None, 0, -1)
    game.shutdown(); host.shutdown()

out = os.path.join(HERE, 'real-mouse-result.json')
with open(out, 'w') as f:
    json.dump(results, f, indent=1)
for c in results:
    print(c['case'], '| start:', c['start'])
    for p in c['phases']:
        print(f"   {p['phase']:30s} moved {p['pointerMovedPx']:>6} px -> {p['events']:>3} events, {p['zeroMovementEvents']:>3} zero, "
              f"sum movementX {p['sumMovementX']:>5}, max {p['maxAbsMovement']:>4}, yaw {p['yawChange']:>7}, "
              f"locked {p['lockedAfter']}, mode {p['modeAfter']}")
print('saved', out)
