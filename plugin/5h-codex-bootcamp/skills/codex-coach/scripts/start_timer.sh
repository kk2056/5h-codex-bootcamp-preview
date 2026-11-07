#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd)
SKILL_ROOT=$(CDPATH= cd "$SCRIPT_DIR/.." && pwd)
BOOTCAMP_WORKSPACE=$(pwd)
export BOOTCAMP_WORKSPACE

if command -v python3 >/dev/null 2>&1 && python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 9))'; then
  exec python3 "$SKILL_ROOT/assets/timer/server.py"
fi

if command -v python >/dev/null 2>&1 && python -c 'import sys; raise SystemExit(sys.version_info < (3, 9))'; then
  exec python "$SKILL_ROOT/assets/timer/server.py"
fi

echo "Python 3.9 or newer is required. Install Python before starting the timer." >&2
exit 1
