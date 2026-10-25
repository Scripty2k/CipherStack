"""CipherStack local launcher.

Starts the FastAPI backend, which also serves the prebuilt React frontend from
``frontend/dist`` on the same origin. No Node.js is required at runtime.

Usage:
    python run.py [--port 8000] [--host 127.0.0.1] [--no-browser]
"""

from __future__ import annotations

import argparse
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

import uvicorn

RELEASE_ROOT = Path(__file__).resolve().parent.parent
STATIC_INDEX = RELEASE_ROOT / "frontend" / "dist" / "index.html"


def _port_is_free(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def _pick_port(host: str, preferred: int) -> int:
    for candidate in range(preferred, preferred + 20):
        if _port_is_free(host, candidate):
            return candidate
    raise SystemExit(f"No free port found in range {preferred}-{preferred + 19}.")


def _open_browser_later(url: str, delay: float = 1.5) -> None:
    def _open() -> None:
        time.sleep(delay)
        try:
            webbrowser.open(url)
        except Exception:  # noqa: BLE001 - opening a browser must never crash the server
            pass

    threading.Thread(target=_open, daemon=True).start()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run CipherStack locally.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Preferred port (default: 8000)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open a browser window")
    args = parser.parse_args(argv)

    if not STATIC_INDEX.is_file():
        print(
            "ERROR: frontend/dist/index.html was not found.\n"
            "       The release archive is incomplete. Re-download it, or build the\n"
            "       frontend with `npm install && npm run build` inside frontend/.",
            file=sys.stderr,
        )
        return 1

    port = _pick_port(args.host, args.port)
    url = f"http://{args.host}:{port}"

    print("=" * 62)
    print("  CipherStack - HTTP Security Header Auditor")
    print("=" * 62)
    print(f"  UI + API : {url}")
    print(f"  API docs : {url}/docs")
    print("  Press Ctrl+C to stop.")
    print("=" * 62)

    if not args.no_browser:
        _open_browser_later(url)

    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=port,
        log_level="info",
        access_log=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
