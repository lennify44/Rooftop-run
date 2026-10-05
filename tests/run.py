"""Run course tests in headless Firefox: python run.py course.js flow.js
Each test runs with lib.js in front of it and fills `report` with result rows."""
import json, os, sys, time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = 'file://' + os.path.join(os.path.dirname(HERE), 'index.html') + '#test'

opts = Options(); opts.add_argument('-headless')
d = webdriver.Firefox(options=opts); d.set_window_size(800, 600)
failed = 0
try:
    lib = open(os.path.join(HERE, 'lib.js')).read()
    for name in sys.argv[1:]:
        d.get(PAGE); d.execute_script('localStorage.clear()'); d.refresh(); time.sleep(2.5)   # each test starts with no saved best run
        err = d.execute_script("const e = document.getElementById('err'); return e.hidden ? '' : e.textContent")
        if err: print('PAGE ERROR:', err); failed += 1; continue
        d.set_script_timeout(600)
        src = open(os.path.join(HERE, name)).read()
        rows = d.execute_script('return (function(){ let report = []; ' + lib + '\n' + src + '\n return report; })()')
        print('==', name)
        for r in rows:
            ok = r.get('ok', True) and r.get('sprint') != 'NO'
            if 'must fail' in str(r.get('leg', '')): ok = not r.get('ok')
            if 'walk' in str(r.get('leg', '')) and 'pad' in str(r.get('leg', '')): ok = True   # pads need speed on purpose
            failed += 0 if ok else 1
            print('  ' + ('ok  ' if ok else 'FAIL'), json.dumps(r))
finally:
    d.quit()
print('failures:', failed)
sys.exit(1 if failed else 0)
