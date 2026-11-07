#!/usr/bin/env python3
"""Start the local preview service if it is not already answering on loopback."""

from __future__ import annotations

import os
import json
import subprocess
import sys
import time
from hashlib import sha256
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, build_opener


PRODUCT_ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = PRODUCT_ROOT / "timer" / "server.py"
LOG_PATH = PRODUCT_ROOT / "progress" / "timer-server.log"
PORT = int(os.environ.get("BOOTCAMP_TIMER_PORT", "4173"))
URL = f"http://127.0.0.1:{PORT}/api/state"
STATE_PATH = PRODUCT_ROOT / "progress" / "progress.json"
EXPECTED_INSTANCE_ID = sha256(str(STATE_PATH.resolve()).encode("utf-8")).hexdigest()[:16]
DIRECT_HTTP = build_opener(ProxyHandler({}))


def probe_server() -> str:
    try:
        with DIRECT_HTTP.open(URL, timeout=0.5) as response:
            payload = json.load(response)
            return "ready" if response.status == 200 and isinstance(payload, dict) and payload.get("instance_id") == EXPECTED_INSTANCE_ID else "other"
    except HTTPError:
        return "other"
    except (ValueError, TypeError):
        return "other"
    except (URLError, TimeoutError, OSError):
        return "offline"


def main() -> int:
    if sys.version_info < (3, 9):
        print("Python 3.9 or newer is required to start the timer.", file=sys.stderr)
        return 2

    status = probe_server()
    if status == "ready":
        print(f"Timer ready at http://127.0.0.1:{PORT}")
        return 0
    if status == "other":
        print(f"端口 {PORT} 已被另一份课程或服务使用。请先关闭旧计时器，再继续。", file=sys.stderr)
        return 3

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    log_file = LOG_PATH.open("ab", buffering=0)
    options = {
        "args": [sys.executable, str(SERVER_PATH)],
        "cwd": str(PRODUCT_ROOT),
        "stdin": subprocess.DEVNULL,
        "stdout": log_file,
        "stderr": subprocess.STDOUT,
        "close_fds": True,
    }
    if os.name == "nt":
        options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
    else:
        options["start_new_session"] = True
    try:
        subprocess.Popen(**options)
    finally:
        log_file.close()

    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        status = probe_server()
        if status == "ready":
            print(f"Timer ready at http://127.0.0.1:{PORT}")
            return 0
        if status == "other":
            print(f"端口 {PORT} 已被另一份课程或服务使用。请先关闭旧计时器，再继续。", file=sys.stderr)
            return 3
        time.sleep(0.1)

    print(f"Timer did not start. Check {LOG_PATH} for the local error.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
