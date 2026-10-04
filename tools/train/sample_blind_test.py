#!/usr/bin/env python3
"""Sample the FRESH blind test for the FLAWLESS plan (section 2b honesty rule):
100 gen-2 windows from JJK holdout pages that are NOT in gold v5 (Claude never
read them), 50 eventish / 50 not, seeded, written as bake-off-shaped inputs
(production user messages). Adjudicated blind (passage only) AFTER guideline
v2 is frozen; drafters are scored on it once.

    python tools/train/sample_blind_test.py [--n 100] [--seed 20261005]
"""
import argparse, json, random, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "tools/train"))
from scriptengine.ingest import events as ev  # noqa: E402
from scriptengine.ingest.windows import CURRENT_GEN, build_windows  # noqa: E402
from scriptengine.stores.facts import FactStore  # noqa: E402
import emit_windows, eventish  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--seed", type=int, default=20261005)
    a = ap.parse_args()
    T = ROOT / "series/jjk/training"
    holdout = set()
    for f in ("v1/dev.jsonl", "v1/test.jsonl"):
        holdout |= {json.loads(l)["page"] for l in open(T / f)}
    seen = {json.loads(l)["page"] for l in open(T / "gold_v5/gold_test_v5.jsonl")}
    pages = holdout - seen
    store = FactStore(ROOT / "series/jjk/facts.db")
    system = ev.system_prompt(ev.eventive_verbs(store))
    pool = {True: [], False: []}
    for page, label, text in emit_windows.universe(store):
        if page not in pages:
            continue
        for w in build_windows(page, label, text, gen=CURRENT_GEN):
            pool[eventish.is_eventish(w.text)].append((page, label, w))
    rng = random.Random(a.seed)
    pick = rng.sample(pool[True], min(a.n // 2, len(pool[True]))) + \
        rng.sample(pool[False], min(a.n - a.n // 2, len(pool[False])))
    out = T / "gold_v6_blind/blind_in.jsonl"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        for page, label, w in pick:
            section = "" if label == "lead" else label
            user = ev._TEMPLATE.format(series="jjk", page=page, section=section, passage=w.text)
            f.write(json.dumps({"id": w.id, "page": page, "section": section,
                                "messages": [{"role": "system", "content": system},
                                             {"role": "user", "content": user}]},
                               ensure_ascii=False) + "\n")
    print(json.dumps({"pages_available": len(pages), "eventish_pool": len(pool[True]),
                      "other_pool": len(pool[False]), "written": len(pick),
                      "distinct_pages": len({p for p, _, _ in pick}), "out": str(out)}))


if __name__ == "__main__":
    main()
