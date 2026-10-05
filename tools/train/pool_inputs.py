#!/usr/bin/env python3
"""Drafter inputs for a universal pool (plan/UNIVERSAL_DATASET_PLAN.md, the
labeling step after the frozen drafter, plan/FLAWLESS_LABELING_PLAN.md
section 11).

Each pool window (series/<s>/training/opencode/<pool>_windows.jsonl, emitted
by tools/train/emit_windows.py, its text re-derivable by dataset gate D2) is
rendered as the extractor's own system + user message for its series, so
tools/train/draft_v2.py reads exactly the production unit — the same shape
tools/train/bakeoff_inputs.py writes for the JJK gold. Zero LLM.

    python tools/train/pool_inputs.py --series opm \
        --windows series/opm/training/opencode/opm_windows.jsonl \
        --out series/opm/training/labels/pool_in.jsonl
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scriptengine.ingest import events as ev  # noqa: E402
from scriptengine.stores.facts import FactStore  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", required=True)
    ap.add_argument("--windows", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    store = FactStore(ROOT / "series" / a.series / "facts.db")
    system = ev.system_prompt(ev.eventive_verbs(store))
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(a.windows) as src, open(out, "w") as f:
        for line in src:
            w = json.loads(line)
            user = ev._TEMPLATE.format(series=a.series, page=w["page"],
                                       section=w.get("section") or "", passage=w["passage"])
            f.write(json.dumps({"id": w["id"], "page": w["page"], "section": w.get("section") or "",
                                "stratum": w.get("stratum"),
                                "messages": [{"role": "system", "content": system},
                                             {"role": "user", "content": user}]},
                               ensure_ascii=False) + "\n")
            n += 1
    print(json.dumps({"series": a.series, "windows": n, "out": str(out)}))


if __name__ == "__main__":
    sys.exit(main())
