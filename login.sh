#!/bin/bash
# One-time interactive login to Naukri (macOS / Linux)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if command -v python3 &>/dev/null; then
    PY="python3"
elif command -v python &>/dev/null; then
    PY="python"
else
    echo "Error: Python 3 is not installed or not in your PATH."
    exit 1
fi

echo "Opening browser for one-time Naukri login using $PY..."
"$PY" naukri_automator.py --login
