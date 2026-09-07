"""X2.e 3b: per-dimension retrieval-not-extraction census (JJK D6 campaign).

The frozen 140-question bank (14 classes x 10, reports/comprehension/
census_3b_dimensions.json) through the qa door, in-process -- the same path
the :8000 /context endpoint uses. No subject anchor: a natural writer
question goes through auto-routing, which is the stricter honest test.

Mechanical pass: each question carries 3 `expect` terms (the distinctive
answer content); >=2 present in the served bundle text is MECH_GREEN.
Every MECH_RED is a triage item: the judging agent re-reads the saved
bundle excerpt and rules (a) green-mechanical-miss (answer present, terms
wrong) or (b) genuinely red -- then classifies the red: paragraph present
in source (chunking/retrieval defect) vs content unserved from anywhere
(an owed layer, Phase 4).

Usage:
  CENSUS_DEVICE=cuda python tools/census_dimensions.py [--anchored]
--anchored re-runs only the MECH_REDs with subject=<the question's subject>
to split routing defects from content defects.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

DEVICE = os.environ.get("CENSUS_DEVICE", "cpu")
os.environ.setdefault("SCRIPTENGINE_DEVICE", DEVICE)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scriptengine"))

from scriptengine.config import series_paths            # noqa: E402
from scriptengine.api.context import build_context      # noqa: E402
from eval.span_recall import served_text                # noqa: E402

BANK = ROOT / "reports/comprehension/census_3b_dimensions.json"
RESULTS = ROOT / "reports/comprehension/census_3b_results.jsonl"
TEXT_CAP = 3000


def judge(item: dict, text: str) -> dict:
    low = text.lower()
    hits = [t for t in item["expect"] if t.lower() in low]
    return {
        **{k: item[k] for k in ("id", "class", "subject", "q", "expect")},
        "hits": hits,
        "missing": [t for t in item["expect"] if t not in hits],
        "verdict": "MECH_GREEN" if len(hits) >= 2 else "MECH_RED",
        "served": text[:TEXT_CAP],
    }


def run(anchored: bool, prev: list[dict] | None = None) -> None:
    paths = series_paths("jjk")
    items = json.loads(BANK.read_text())
    if anchored and prev:
        reds = {r["id"] for r in prev if r.get("verdict") == "MECH_RED"}
        items = [i for i in items if i["id"] in reds]
    t0 = time.time()
    results = list(prev or [])
    prev_ids = {r["id"] for r in prev or []}
    for i, item in enumerate(items, 1):
        try:
            bundle = build_context(
                paths, item["q"], mode="qa",
                subject=item["subject"] if anchored else None,
            )
            text = served_text(bundle)
            rec = judge(item, text)
            rec["error"] = None
            rec["anchored"] = anchored
        except Exception as e:
            rec = {**{k: item[k] for k in ("id", "class", "subject", "q", "expect")},
                   "hits": [], "missing": list(item["expect"]),
                   "verdict": "ERROR", "error": f"{type(e).__name__}: {e}",
                   "served": "", "anchored": anchored}
        if rec["id"] in prev_ids:
            results = [r for r in results if r["id"] != rec["id"]]
        results.append(rec)
        if i % 20 == 0 or rec["verdict"] != "MECH_GREEN":
            print(f"  {i:3d}/{len(items)} {rec['id']} [{rec['class']}] "
                  f"{rec['verdict']} {rec.get('missing', [])} {rec['q'][:55]}")
    RESULTS.write_text("\n".join(json.dumps(r) for r in results) + "\n")

    by_cls: dict[str, list[dict]] = {}
    for r in results:
        if r["id"] not in prev_ids or anchored:
            by_cls.setdefault(r["class"], []).append(r)
    for cls in ("Personality", "Overview", "Trivia", "Appearance", "Cursed Technique",
                "History", "Physical Prowess", "Intelligence", "Abilities and Powers",
                "Cursed Energy", "Equipment", "Quotes", "Outcomes", "Causality"):
        rs = by_cls.get(cls, [])
        if not rs:
            continue
        green = sum(1 for r in rs if r["verdict"] == "MECH_GREEN")
        print(f"{cls:22s} {green}/{len(rs)} mech-green")
    reds = [r for r in results if r["verdict"] in ("MECH_RED", "ERROR")]
    print(f"\n{len(reds)} reds to judge -> {RESULTS.name} "
          f"({time.time() - t0:.0f}s)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--anchored", action="store_true",
                    help="re-run the MECH_REDs with a subject anchor")
    args = ap.parse_args()
    prev = None
    if args.anchored:
        if RESULTS.exists():
            prev = [json.loads(line) for line in RESULTS.read_text().splitlines() if line]
        else:
            print("No previous results; run without --anchored first.")
            return
    run(args.anchored, prev)


if __name__ == "__main__":
    main()