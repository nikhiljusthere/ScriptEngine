#!/usr/bin/env python3
"""The named consumer of the held-out 200 (COUNCIL_csm-3 Ruling 7).

The held-out split is a bare row array (`panel_csm.json.heldout.json`) that
the executing agent never opens -- the sweep that grades a fix must not be
chosen by the fixer (§9a). This wrapper is the *only* door into it, and it
runs in the validation session, never in a fix session: it validates the
side file's shape, stamps its own hash, and hands it to
`chunk-containment --panel` (which recomputes and enforces the hash),
writing results to the validation folder.

Usage (from the repo root):
    python tools/csm/panel_heldout.py --series csm --door qa [--sanity N]
    [--out VALIDATION_FOLDER]

Exit codes: 0 = sweep ran (see the table + the folder's
sweep_<door>_<panelhash8>.jsonl, R-CSM3B-2);
1 = side file is not the pinned held-out shape (re-pin the panel);
3 = the CLI's dead-door sanity halt.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOLDOUT = REPO / "reports/csm/panel_csm.json.heldout.json"
PIN = REPO / "reports/csm/panel_csm.json"
EXPECTED_ROWS = 200


def main() -> int:
    args = argparse.ArgumentParser(description=__doc__).parse_args()
    rows = json.loads(HOLDOUT.read_text(encoding="utf-8"))
    if not (isinstance(rows, list) and len(rows) == EXPECTED_ROWS
            and all(isinstance(r, list) and len(r) == 3
                    and all(isinstance(v, str) for v in r) for r in rows)):
        print(f"held-out side file is not {EXPECTED_ROWS} (title, section, "
              f"sentence) rows: {HOLDOUT} -- re-pin the panel before "
              f"validating.")
        return 1
    # The pin's sweep rows and the held-out rows must be disjoint; the side
    # file is what the pin carved out, so a drift here means a re-pin.
    pin = json.loads(PIN.read_text(encoding="utf-8"))
    if set(map(tuple, rows)) & set(map(tuple, pin["panel"])):
        print("held-out rows overlap the sweep panel -- the split drifted; "
              "re-pin the panel.")
        return 1
    out = args.out or str(REPO / "reports" / "csm" / "heldout_validation")
    cmd = [sys.executable, "-m", "scriptengine.cli", "chunk-containment",
           "--series", args.series, "--panel", str(HOLDOUT),
           "--door", args.door, "--out", out]
    if args.sanity:
        cmd += ["--sanity", str(args.sanity)]
    print(" ".join(cmd))
    return subprocess.call(cmd, cwd=REPO)


if __name__ == "__main__":
    sys.exit(main())