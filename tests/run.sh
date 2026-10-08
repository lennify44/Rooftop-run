#!/bin/bash
# Runs every test in headless Firefox. The first run creates a Python venv with
# Selenium under ~/.cache/rooftop-run-tests.
set -e
cd "$(dirname "$0")"
VENV="${XDG_CACHE_HOME:-$HOME/.cache}/rooftop-run-tests"
[ -x "$VENV/bin/python" ] || { python3 -m venv "$VENV" && "$VENV/bin/pip" install -q selenium; }
"$VENV/bin/python" run.py course.js flow.js
"$VENV/bin/python" touch.py
"$VENV/bin/python" touch-native.py
"$VENV/bin/python" mouse.py
