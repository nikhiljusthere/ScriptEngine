#!/usr/bin/env python3
"""Save ONE manually verified window (plan/VERIFY_POOLS_BRIEF.md). The
verifier writes its decision for the window as a JSON file and this checks it
mechanically before appending it to the pool's verified log -- it never
decides anything, it only refuses a malformed or unfaithful record:

* the window id exists in the pool's drafter input and is not saved yet;
* every final row's quote is VERBATIM in the window, its verb is one of the
  12, `awakened` has a null object and every other verb an object;
* every draft row has a verdict (keep / fix / reject) and a reason;
* pages_consulted is non-empty whenever the window has any row.

    scriptengine/.venv/bin/python tools/train/verify_save.py --series opm --pool pool decision.json

decision.json:
{"id": "...", "draft": [{"row": {...}, "verdict": "keep|fix|reject", "reason": "...",
  "fixed": {...}}], "added": [{"row": {...}, "reason": "..."}],
 "pages_consulted": ["Page / Section", ...], "final": [{quote, subject, verb, object}, ...],
 "notes": "..."}
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERBS = {"fought", "defeated", "killed", "captured", "escaped", "saved", "betrayed",
         "sealed", "met", "arrived", "departed", "awakened"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", required=True)
    ap.add_argument("--pool", default="pool", help="pool (train) or test")
    ap.add_argument("decision")
    a = ap.parse_args()
    lab = ROOT / "series" / a.series / "training" / "labels"
    src = lab / ("pool_in.jsonl" if a.pool == "pool" else "test_in.jsonl")
    out = lab / f"{a.pool}_verified.jsonl"
    d = json.loads(Path(a.decision).read_text())
    windows = {}
    for line in open(src):
        r = json.loads(line)
        windows[r["id"]] = r
    errs = []
    wid = d.get("id")
    if wid not in windows:
        sys.exit(f"REFUSED: window {wid!r} is not in {src}")
    if out.exists() and any(json.loads(l)["id"] == wid for l in open(out)):
        sys.exit(f"REFUSED: window {wid} is already saved in {out}")
    text = windows[wid]["messages"][1]["content"].split("Passage:\n", 1)[1]
    for i, r in enumerate(d.get("final") or []):
        q, v, o = r.get("quote") or "", r.get("verb"), r.get("object")
        if not q or q not in text:
            errs.append(f"final[{i}]: quote not verbatim in the window: {q[:80]!r}")
        if v not in VERBS:
            errs.append(f"final[{i}]: verb {v!r} is not one of the 12")
        if v == "awakened" and o not in (None, ""):
            errs.append(f"final[{i}]: awakened takes a null object")
        if v != "awakened" and not o:
            errs.append(f"final[{i}]: {v} needs an object")
        if not r.get("subject"):
            errs.append(f"final[{i}]: no subject")
    for i, x in enumerate(d.get("draft") or []):
        if x.get("verdict") not in ("keep", "fix", "reject"):
            errs.append(f"draft[{i}]: verdict must be keep/fix/reject")
        if not str(x.get("reason") or "").strip():
            errs.append(f"draft[{i}]: no reason")
    for i, x in enumerate(d.get("added") or []):
        if not str(x.get("reason") or "").strip():
            errs.append(f"added[{i}]: no reason")
    if (d.get("final") or d.get("draft")) and not d.get("pages_consulted"):
        errs.append("pages_consulted is empty: open the pages for the window's ends")
    if errs:
        sys.exit("REFUSED:\n" + "\n".join(errs))
    rec = {"id": wid, "page": windows[wid]["page"], "section": windows[wid]["section"], **d}
    with open(out, "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    n = sum(1 for _ in open(out))
    print(f"SAVED {wid} ({len(d.get('final') or [])} rows) -> {out} [{n}/{len(windows)}]")


if __name__ == "__main__":
    sys.exit(main())
