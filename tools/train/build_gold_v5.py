#!/usr/bin/env python3
"""Build the window-level, quoted test gold v5 from Claude's passage-only
adjudication (plan/FLAWLESS_LABELING_PLAN.md section 2).

Input: series/jjk/training/gold_v5/decisions_*.jsonl — one line per old test
passage unit (W0..W99) with the adjudicated events {w, q, s, v, o, why,
optional?}. Output: series/jjk/training/gold_v5/gold_test_v5.jsonl — one
WINDOW record per gen-2 covering window, the shape tools/eval_extraction.py
scores per window with quote overlap:

    {"id", "page", "section", "events": [...], "optional": [...]}

Rules (each a hard failure, never a silent drop):
* every quote is verbatim in its window's text (the bake-off input carries the
  exact production user message, so the window text is the scored text);
* a window covered by two units (the old slices overlapped) gets the union of
  their rows, deduplicated on (subject, verb, object, quote);
* PARTIAL windows (extending past the old annotated slice) are EXCLUDED: only
  their read part was adjudicated, so an empty answer there is not earned.

    python tools/train/build_gold_v5.py
"""
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
G5 = ROOT / "series/jjk/training/gold_v5"
TEST = ROOT / "series/jjk/training/recall_gold_v3/gold_test_v4.gen2.json"
BAKE = ROOT / "series/jjk/training/bakeoff/bakeoff_in.jsonl"


def main():
    units = json.loads(TEST.read_text())
    windows = {}  # id -> {"partial": bool, "units": [...]}
    for key, unit in units.items():
        if not (key.startswith("W") and isinstance(unit, dict)):
            continue
        for w in unit["windows"]:
            rec = windows.setdefault(w["id"], {"partial": False, "units": []})
            rec["partial"] = rec["partial"] or bool(w.get("partial"))
            rec["units"].append(key)
    text, meta = {}, {}
    for line in open(BAKE):
        r = json.loads(line)
        text[r["id"]] = r["messages"][1]["content"].split("Passage:\n", 1)[1]
        meta[r["id"]] = (r["page"], r["section"])

    decided = {}
    for path in sorted(glob.glob(str(G5 / "decisions_*.jsonl"))):
        for line in open(path):
            d = json.loads(line)
            if d.get("amend") and d["unit"] in decided:
                # an amendment (later decisions file) adds rows to a unit
                # already adjudicated; the original log stays intact
                decided[d["unit"]]["events"].extend(d["events"])
            else:
                decided[d["unit"]] = d
    missing = sorted(set(k for k in units if k.startswith("W")) - set(decided))
    if missing:
        sys.exit(f"units not adjudicated: {missing}")

    rows, errors, demoted = {}, [], set()
    for unit, d in decided.items():
        for e in d["events"]:
            wid = e["w"]
            if wid not in text:
                errors.append(f"{unit}: window {wid} not in the bake-off inputs")
                continue
            if e.get("demote"):
                # a later decision moves an earlier core row to the
                # borderline tier (the row and its reason stay logged)
                demoted.add((wid, e["s"].lower(), e["v"], (e["o"] or "").lower(), e["q"]))
                continue
            if e["q"] not in text[wid]:
                errors.append(f"{unit}: quote not verbatim in {wid}: {e['q'][:80]!r}")
                continue
            row = {"quote": e["q"], "subject": e["s"], "verb": e["v"], "object": e["o"]}
            bucket = "optional" if e.get("optional") else "events"
            key = (row["subject"].lower(), row["verb"], (row["object"] or "").lower(), row["quote"])
            slot = rows.setdefault(wid, {"events": {}, "optional": {}})
            slot[bucket].setdefault(key, row)
    for wid, s_, v, o, q in demoted:
        key = (s_, v, o, q)
        slot = rows.get(wid, {}).get("events", {})
        if key not in slot:
            errors.append(f"demote: no core row {key} in {wid}")
            continue
        rows[wid]["optional"].setdefault(key, slot.pop(key))
    if errors:
        sys.exit("\n".join(errors))

    out, kept, partial_skipped, ev, opt = [], 0, 0, 0, 0
    for wid, info in windows.items():
        if info["partial"]:
            partial_skipped += 1
            continue
        slot = rows.get(wid, {"events": {}, "optional": {}})
        page, section = meta[wid]
        # The scorer locates quotes in `passage` (window records are
        # scored with quote overlap, so the window text must travel).
        rec = {"id": wid, "page": page, "section": section, "passage": text[wid],
               "events": list(slot["events"].values()),
               "optional": list(slot["optional"].values()),
               "units": info["units"]}
        ev += len(rec["events"]); opt += len(rec["optional"]); kept += 1
        out.append(rec)
    dest = G5 / "gold_test_v5.jsonl"
    with open(dest, "w") as f:
        for rec in out:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    receipt = {"windows": kept, "partial_excluded": partial_skipped,
               "core_events": ev, "optional_events": opt,
               "empty_windows": sum(1 for r in out if not r["events"] and not r["optional"]),
               "out": str(dest)}
    (G5 / "gold_test_v5.receipt.json").write_text(json.dumps(receipt, indent=1))
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
