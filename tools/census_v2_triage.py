"""Triage the v2 census reds: routing defect vs genuine content gap.

The v2 grading run sent every question through the qa door unanchored (the v1
convention). But the v2 bank is dominated by "what happens in <chapter|arc|
episode>" questions, which are narrative-shaped. A red there can mean either:

  ROUTING  — the content is in the corpus and a different door/anchor serves it
  CONTENT  — nothing serves it from anywhere (an owed extraction layer)

Telling them apart decides Phase 2's scope: a routing defect is a cheap engine
fix, a content gap is extraction GPU-days. So each red is re-tried three ways
and classified by the best result.

Usage: CENSUS_DEVICE=cuda python tools/census_v2_triage.py
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

os.environ.setdefault("CENSUS_DEVICE", "cuda")
os.environ.setdefault("SCRIPTENGINE_DEVICE", os.environ["CENSUS_DEVICE"])

from tools.census_dimensions import judge  # noqa: E402

from scriptengine.api.context import build_context  # noqa: E402
from scriptengine.config import series_paths  # noqa: E402
from scriptengine.eval.span_recall import served_text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RESULTS = Path(os.environ.get("TRIAGE_IN", ROOT / "reports/csm/census_dimensions_csm_v2_results.jsonl"))
OUT = Path(os.environ.get("TRIAGE_OUT", ROOT / "reports/csm/census_dimensions_csm_v2_triage.jsonl"))

# (label, mode, anchored) — the qa/unanchored baseline already ran.
ATTEMPTS = [
    ("qa+anchor", "qa", True),
    ("narrative", "narrative", False),
    ("narrative+anchor", "narrative", True),
]


def main() -> None:
    paths = series_paths("csm")
    print(f"device={os.environ['SCRIPTENGINE_DEVICE']}", flush=True)
    rows = [json.loads(line) for line in RESULTS.read_text().splitlines() if line]
    reds = [r for r in rows if r["verdict"] != "MECH_GREEN"]
    print(f"{len(reds)} reds to triage", flush=True)

    out = []
    t0 = time.time()
    for i, red in enumerate(reds, 1):
        item = {k: red[k] for k in ("id", "class", "subject", "q", "expect")}
        best = {"label": "none", "verdict": "MECH_RED", "hits": []}
        for label, mode, anchored in ATTEMPTS:
            try:
                bundle = build_context(
                    paths, item["q"], mode=mode,
                    subject=item["subject"] if anchored else None,
                )
                rec = judge(item, served_text(bundle))
            except Exception as e:
                rec = {"verdict": "ERROR", "hits": [], "error": f"{type(e).__name__}: {e}"}
            if len(rec.get("hits", [])) > len(best["hits"]):
                best = {"label": label, "verdict": rec["verdict"], "hits": rec["hits"]}
            if rec["verdict"] == "MECH_GREEN":
                break
        klass = "ROUTING" if best["verdict"] == "MECH_GREEN" else (
            "PARTIAL" if best["hits"] else "CONTENT")
        out.append({**item, "triage": klass, "recovered_by": best["label"],
                    "best_hits": best["hits"]})
        print(f"  {i:3d}/{len(reds)} {item['id']:<22} {klass:<8} via {best['label']}",
              flush=True)

    OUT.write_text("\n".join(json.dumps(r) for r in out) + "\n")
    import collections
    by = collections.Counter(r["triage"] for r in out)
    bycls = collections.defaultdict(collections.Counter)
    for r in out:
        bycls[r["class"]][r["triage"]] += 1
    print(f"\n=== triage ({time.time()-t0:.0f}s) ===")
    for k, v in by.items():
        print(f"  {k:<8} {v}")
    print("\nper class:")
    for cls, c in bycls.items():
        print(f"  {cls:<16} ROUTING={c['ROUTING']:>2} PARTIAL={c['PARTIAL']:>2} CONTENT={c['CONTENT']:>2}")
    print(f"\n-> {OUT.name}")


if __name__ == "__main__":
    main()
