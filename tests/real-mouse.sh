#!/bin/bash
# Real-mouse check on GNOME: visible Firefox, real pointer movement. Hands off the mouse
# until Firefox closes. Needs PyGObject from the system Python, so the venv sees system packages.
set -e
cd "$(dirname "$0")"
VENV="${XDG_CACHE_HOME:-$HOME/.cache}/rooftop-run-realmouse"
[ -x "$VENV/bin/python" ] || { python3 -m venv --system-site-packages "$VENV" && "$VENV/bin/pip" install -q selenium; }
"$VENV/bin/python" real-mouse.py
