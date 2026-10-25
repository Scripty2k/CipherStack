#!/usr/bin/env bash
# CipherStack - local launcher for macOS and Linux.
#
# First run creates .venv and installs the Python dependencies.
# The bundled backend serves both the API and the prebuilt frontend.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$ROOT/.venv"
PY="$VENV/bin/python"
REQ="$ROOT/backend/requirements.txt"
STAMP="$VENV/.deps-installed"
PORT="${PORT:-8000}"

echo
echo " ============================================================"
echo "   CipherStack - HTTP Security Header Auditor"
echo " ============================================================"
echo

if [[ ! -f "$ROOT/backend/run.py" || ! -f "$ROOT/frontend/dist/index.html" ]]; then
    echo " ERROR: This folder looks incomplete."
    echo "        Expected backend/run.py and frontend/dist/index.html."
    exit 1
fi

if [[ ! -x "$PY" ]]; then
    echo " [1/3] Looking for Python 3.11 - 3.13 ..."
    BASEPY=""
    for candidate in python3.13 python3.12 python3.11 python3 python; do
        if command -v "$candidate" >/dev/null 2>&1; then
            if "$candidate" -c 'import sys; sys.exit(0 if (3,11) <= sys.version_info[:2] <= (3,13) else 1)' 2>/dev/null; then
                BASEPY="$candidate"
                echo "       Found $("$candidate" --version 2>&1)."
                break
            fi
        fi
    done

    if [[ -z "$BASEPY" ]]; then
        echo
        echo " ERROR: No supported Python interpreter was found."
        echo "        CipherStack needs Python 3.11, 3.12 or 3.13."
        echo "        Python 3.14 is not supported yet."
        exit 1
    fi

    echo
    echo " [2/3] Creating the virtual environment ..."
    "$BASEPY" -m venv "$VENV"
fi

if [[ ! -f "$STAMP" ]]; then
    echo
    echo " [3/3] Installing dependencies (first run only) ..."
    "$PY" -m pip install --upgrade pip --quiet --disable-pip-version-check
    "$PY" -m pip install --quiet --disable-pip-version-check -r "$REQ"
    : > "$STAMP"
fi

echo
echo " Starting CipherStack on http://127.0.0.1:$PORT"
echo " Press Ctrl+C to stop."
echo
exec "$PY" "$ROOT/backend/run.py" --port "$PORT"
