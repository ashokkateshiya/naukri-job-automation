#!/bin/bash
# Run the daily Naukri automation routine (macOS / Linux)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Try to find a valid Python 3 executable
if command -v python3 &>/dev/null; then
    PY="python3"
elif command -v python &>/dev/null; then
    PY="python"
else
    echo "Error: Python 3 is not installed or not in your PATH."
    exit 1
fi

echo "Executing Daily Naukri Automation using $PY..."
"$PY" naukri_automator.py --daily
echo "Completed. Check last_run.log for details."
