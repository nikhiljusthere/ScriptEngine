#!/usr/bin/env python3
"""Inputs for the labeler bake-off (plan/UNIVERSAL_DATASET_PLAN.md, "Labeler
choice", owner 2026-10-04: "prove the 35B before using it").

Every gen-2 window covering the blind JJK passage test gold
(recall_gold_v3/gold_test_v4.gen2.json), rendered as the extractor's own
user message, so each candidate labeler (27B-Q8, 35B, 27B-NVFP4 reference)
reads exactly the production unit and `tools/eval_extraction.py` scores the
union per passage. Zero LLM.

    python tools/train/bakeoff_inputs.py --series jjk --out bakeoff_in.jsonl
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools" / "train"))

from scriptengine.ingest import events as ev  # noqa: E402
from scriptengine.ingest.windows import CURRENT_GEN, build_windows  # noqa: E402
from scriptengine.stores.facts import FactStore  # noqa: E402
import emit_windows  # noqa: E402


def covering_ids(gold):
    """The window ids the passage units are scored over, in file order."""
    units = gold["units"] if "units" in gold else [
        v for v in gold.values() if isinstance(v, dict) and "core" in v]
    ids = []
    for unit in units:
        for w in unit.get("windows") or []:
            wid = w["id"] if isinstance(w, dict) else w
            if wid not in ids:
                ids.append(wid)
    return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", default="jjk")
    ap.add_argument("--gold", default=None)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    base = ROOT / "series" / a.series
    gold_path = Path(a.gold) if a.gold else base / "training/recall_gold_v3/gold_test_v4.gen2.json"
    want = covering_ids(json.loads(gold_path.read_text()))
    if not want:
        sys.exit(f"{gold_path}: no covering windows found")
    store = FactStore(base / "facts.db")
    system = ev.system_prompt(ev.eventive_verbs(store))
    found = {}
    wanted = set(want)
    for page, label, text in emit_windows.universe(store):
        for w in build_windows(page, label, text, gen=CURRENT_GEN):
            if w.id in wanted and w.id not in found:
                # The lead reads with an empty section title in production.
                section = "" if label == "lead" else label
                user = ev._TEMPLATE.format(series=a.series, page=page,
                                           section=section, passage=w.text)
                found[w.id] = {"id": w.id, "page": page, "section": section,
                               "messages": [{"role": "system", "content": system},
                                            {"role": "user", "content": user}]}
    missing = [i for i in want if i not in found]
    with open(a.out, "w") as f:
        for wid in want:
            if wid in found:
                f.write(json.dumps(found[wid], ensure_ascii=False) + "\n")
    print(json.dumps({"gold": str(gold_path), "windows_wanted": len(want),
                      "written": len(want) - len(missing), "missing": missing[:20]}))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
