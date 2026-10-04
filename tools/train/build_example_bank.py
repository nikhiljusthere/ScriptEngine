#!/usr/bin/env python3
"""The worked-example bank for drafter v2 (plan/FLAWLESS_LABELING_PLAN.md
sections 5 and 6b: "show, don't tell").

Each example is one gen-2 window from the gold v5 adjudication with its
correct rows and the lesson it teaches — a model miss (FN), a model false
positive (FP) or an earned empty with tempting wording. Drafter v2 retrieves
the examples closest to a window's own wording; it never shows a window its
own page (leave-page-out), so a dev score is not inflated by its own answer.

    python tools/train/build_example_bank.py
        -> series/jjk/training/gold_v5/example_bank.jsonl
"""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
G5 = ROOT / "series/jjk/training/gold_v5"
BAKE = ROOT / "series/jjk/training/bakeoff/bakeoff_in.jsonl"

# Earned empties whose wording tempts a false row (intent, threats, plans,
# capability, a meeting already in progress) — negatives are first-class.
TEMPTING_EMPTY_UNITS = {"W7", "W11", "W12", "W19", "W30", "W48", "W57", "W83", "W93"}


def main():
    text, meta = {}, {}
    for line in open(BAKE):
        r = json.loads(line)
        text[r["id"]] = r["messages"][1]["content"].split("Passage:\n", 1)[1]
        meta[r["id"]] = (r["page"], r["section"])
    gold = {json.loads(l)["id"]: json.loads(l) for l in open(G5 / "gold_test_v5.jsonl")}
    decisions = [json.loads(l) for l in open(G5 / "decisions_001.jsonl")]

    bank, seen = [], set()
    for d in decisions:
        lessons = d.get("model_fn", []) + d.get("model_fp", [])
        notes = d.get("notes", "")
        windows = defaultdict(list)
        for e in d["events"]:
            windows[e["w"]].append(e)
        wanted = set(windows)
        if d["unit"] in TEMPTING_EMPTY_UNITS:
            # the unit's windows with no row: earned, tempting empties
            wanted |= {w for w in gold if d["unit"] in gold[w].get("units", [])}
        for wid in sorted(wanted):
            if wid in seen or wid not in gold:  # partial windows are not in gold
                continue
            rows = gold[wid]["events"]
            if not rows and d["unit"] not in TEMPTING_EMPTY_UNITS:
                continue
            if not lessons and rows and not any(
                    k in notes for k in ("IMPLICIT", "precedent", "v2", "not ", "=")):
                continue
            seen.add(wid)
            why = "; ".join(f"{e['s']} {e['v']} {e['o']}: {e['why']}" for e in windows.get(wid, []))
            bank.append({
                "id": wid, "unit": d["unit"], "page": meta[wid][0], "section": meta[wid][1],
                "window": text[wid],
                "rows": [{k: r[k] for k in ("quote", "subject", "verb", "object")} for r in rows],
                "why": why or "no event: " + notes,
                "lesson": "; ".join(lessons) or notes,
                "tokens": sorted(set(re.findall(r"[a-z]{3,}", text[wid].lower()))),
            })
    out = G5 / "example_bank.jsonl"
    with open(out, "w") as f:
        for b in bank:
            f.write(json.dumps(b, ensure_ascii=False) + "\n")
    print(json.dumps({"examples": len(bank),
                      "empty": sum(1 for b in bank if not b["rows"]),
                      "rows": sum(len(b["rows"]) for b in bank), "out": str(out)}))


if __name__ == "__main__":
    main()
