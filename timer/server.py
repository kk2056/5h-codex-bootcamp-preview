"""Serve the timer preview on loopback only. No third-party packages."""

from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from state import apply_action, get_state, pause_after_server_restart


HOST = "127.0.0.1"
PORT = int(os.environ.get("BOOTCAMP_TIMER_PORT", "4173"))
INDEX = Path(__file__).with_name("index.html")
ALLOWED_ORIGINS = {f"http://{HOST}:{PORT}", f"http://localhost:{PORT}"}


class Handler(BaseHTTPRequestHandler):
    server_version = "BootcampTimer/0.1"

    def _headers(self, content_type: str, length: int) -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        if content_type.startswith("text/html"):
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
                "connect-src 'self'; img-src 'self' data:; font-src 'self'; base-uri 'none'; "
                "form-action 'self'; frame-ancestors 'none'",
            )
        self.end_headers()

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/":
            body = INDEX.read_bytes()
            self._headers("text/html; charset=utf-8", len(body))
            self.wfile.write(body)
            return
        if path == "/api/state":
            self._json(200, get_state())
            return
        self._json(404, {"error": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        if urlparse(self.path).path != "/api/action":
            self._json(404, {"error": "Not found"})
            return
        if self.headers.get("Origin") not in ALLOWED_ORIGINS:
            self._json(403, {"error": "Only the local timer page can change the timer."})
            return
        try:
            length = min(int(self.headers.get("Content-Length", "0")), 1024)
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            action = body.get("action") if isinstance(body, dict) else None
            state = apply_action(str(action))
            self._json(200, state)
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            self._json(400, {"error": str(exc)})

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[timer] {fmt % args}", file=sys.stderr)


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    pause_after_server_restart()
    print(f"5H Bootcamp timer: http://{HOST}:{PORT}")
    print("Local only. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nTimer preview stopped.")
    finally:
        server.server_close()
