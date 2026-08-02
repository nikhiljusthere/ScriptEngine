"""Starts the ScriptEngine API server manually.

Usage: python start_scriptengine.py
Stops with Ctrl+C or when the API process exits.
"""

import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VENV_PYTHON = BASE_DIR / "scriptengine" / ".venv" / "Scripts" / "python.exe"


def main() -> int:
    if not VENV_PYTHON.exists():
        print(f"Venv python not found: {VENV_PYTHON}", file=sys.stderr)
        return 1

    command = [str(VENV_PYTHON), "-m", "scriptengine.api.main"]
    print(f"Starting ScriptEngine: {BASE_DIR}")
    print("> " + " ".join(command))

    try:
        process = subprocess.run(command, cwd=BASE_DIR)
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0

    print(f"ScriptEngine exited with code {process.returncode}")
    return process.returncode


if __name__ == "__main__":
    sys.exit(main())
