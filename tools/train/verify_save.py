#!/usr/bin/env python3
"""Save ONE manually verified window (plan/VERIFY_POOLS_BRIEF.md). The
verifier writes its decision for the window as a JSON file and this checks it
mechanically before appending it to the pool's verified log -- it never
decides anything, it only refuses a malformed or unfaithful record:

* the window id exists in the pool's drafter input and is not saved yet;
* every final row's quote is VERBATIM in the window, its verb is one of the
  12, `awakened` has a null object and every other verb an object;
* every draft row has a verdict (keep / fix / reject) and a reason;
* pages_consulted is non-empty whenever the window has any row;
* every final row passes the drafter's own mechanical end checks
  (draft_v2.check_rows: class / plural crowd / indefinite / pronoun ends, a
  group row not split into members, self-rows) and no end is a species-like
  page -- `species` on JJK, `race` on OPM (the first audit, 2026-10-05: the
  verifier kept "Saitama met The Subterranean People", a race page) --
  checked with the leading article stripped.

Auditor mode (Claude only): --replace swaps a saved record for a corrected one
and logs both, with --why, to <pool>_audit.jsonl.

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


SPECIES_LIKE = {"species", "race", "races"}


def end_errors(series, final, text):
    """The drafter's mechanical end checks, applied to the verifier's rows."""
    sys.path.insert(0, str(ROOT / "tools" / "train"))
    import re
    import draft_v2
    import verify_row_wiki as vrw
    wiki = vrw.Wiki(str(ROOT / "series" / series / "facts.db"))
    # Only the END checks bind the verifier. The drafter's two wording
    # heuristics (bare modal -> drop; defeated without a DEFEAT lexeme ->
    # fought) are switched off here: a verifier who read the pages outranks
    # them ("Drive Knight finishes off the monster" is G.1 defeated YES but
    # has no DEFEAT lexeme -- audit 2).
    draft_v2.MODAL = re.compile(r"(?!x)x")
    draft_v2.DEFEAT = re.compile(r"")
    errs = []
    rows = [{k: r.get(k) for k in ("quote", "subject", "verb", "object")} for r in final]
    kept, dropped = draft_v2.check_rows(rows, text, wiki, vrw.BAD_END | SPECIES_LIKE)
    for d in dropped:
        errs.append(f"row {d.get('subject')!r} {d.get('verb')} {d.get('object')!r}: {d['why']}")
    if len(kept) != len(rows) and not dropped:
        errs.append("a row is a group end or a duplicate: write one row per named member, no repeats "
                    f"(the checked rows would be {[(k['subject'], k['verb'], k['object']) for k in kept]})")
    for r in rows:
        for end in (r["subject"], r["object"]):
            if not end:
                continue
            bare = re.sub(r"(?i)^(the|a|an)\s+", "", end.strip())
            exact = [p for p in wiki.resolve(bare) if p.lower() == bare.lower()]
            if exact and wiki.label.get(exact[0]) in SPECIES_LIKE:
                errs.append(f"end {end!r} is a {wiki.label.get(exact[0])} page (a class, never an end; G.2)")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", required=True)
    ap.add_argument("--pool", default="pool", help="pool (train) or test")
    ap.add_argument("decision")
    ap.add_argument("--replace", action="store_true", help="auditor: replace the saved record")
    ap.add_argument("--why", default="", help="auditor: the reason for the replacement")
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
    saved = [json.loads(l) for l in open(out)] if out.exists() else []
    if any(r["id"] == wid for r in saved) and not a.replace:
        sys.exit(f"REFUSED: window {wid} is already saved in {out}")
    if a.replace and not (any(r["id"] == wid for r in saved) and a.why.strip()):
        sys.exit("REFUSED: --replace needs a saved window and --why")
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
    errs += end_errors(a.series, d.get("final") or [], text)
    if errs:
        sys.exit("REFUSED:\n" + "\n".join(errs))
    import time
    rec = {"id": wid, "page": windows[wid]["page"], "section": windows[wid]["section"], **d,
           "saved_at": time.strftime("%Y-%m-%d %H:%M:%S")}  # the live monitor's feed order
    if a.replace:
        old = next(r for r in saved if r["id"] == wid)
        with open(lab / f"{a.pool}_audit.jsonl", "a") as f:
            f.write(json.dumps({"id": wid, "why": a.why, "before": old, "after": rec}, ensure_ascii=False) + "\n")
        with open(out, "w") as f:
            for r in saved:
                f.write(json.dumps(rec if r["id"] == wid else r, ensure_ascii=False) + "\n")
        print(f"REPLACED {wid} (logged to {a.pool}_audit.jsonl)")
        return 0
    with open(out, "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    n = sum(1 for _ in open(out))
    print(f"SAVED {wid} ({len(d.get('final') or [])} rows) -> {out} [{n}/{len(windows)}]")


if __name__ == "__main__":
    sys.exit(main())
