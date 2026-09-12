"""Grade reports/csm/census_dimensions_csm_v2.json against the live engine.

Standalone, deliberately: tools/census_dimensions.py hardcodes its bank/results
paths per series (_census_paths), and the v1 CSM census + results file is the
frozen Phase-1 gate record (referenced by GATE.md, the 5.4 re-adjudication
receipts, COUNCIL_csm_p14_close.md). This script reuses the same judge() rule
and serving path (build_context -> served_text, mode="qa", in-process) but
reads a different bank and writes a different results file, so grading v2
cannot perturb the v1 record a reboot or reviewer might read.

Usage: CENSUS_DEVICE=cuda python tools/census_dimensions_csm_v2_grade.py
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

# MUST precede the census_dimensions import: that module does
# `os.environ.setdefault("SCRIPTENGINE_DEVICE", os.environ.get("CENSUS_DEVICE", "cpu"))`
# at module scope, so importing it for judge() silently pins the whole process
# to CPU unless the device is already chosen. This campaign runs model work on
# CUDA (a CPU census run is ~an order of magnitude slower and violates the
# GPU-only rule), so default to cuda here and let the caller override.
os.environ.setdefault("CENSUS_DEVICE", "cuda")
os.environ.setdefault("SCRIPTENGINE_DEVICE", os.environ["CENSUS_DEVICE"])

from tools.census_dimensions import judge  # noqa: E402  same MECH_GREEN/RED rule as v1

from scriptengine.api.context import build_context  # noqa: E402
from scriptengine.config import series_paths  # noqa: E402
from scriptengine.eval.span_recall import served_text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "reports/csm/census_dimensions_csm_v2.json"
RESULTS = ROOT / "reports/csm/census_dimensions_csm_v2_results.jsonl"


def main() -> None:
    paths = series_paths("csm")
    # Printed, not assumed: the 2026-09-12 run silently went to CPU because the
    # device was an import side effect nobody could see in the log.
    print(f"device={os.environ['SCRIPTENGINE_DEVICE']} "
          f"(CENSUS_DEVICE={os.environ['CENSUS_DEVICE']})", flush=True)
    data = json.loads(BANK.read_text())
    items = data["items"]
    t0 = time.time()
    results = []
    for i, item in enumerate(items, 1):
        try:
            bundle = build_context(paths, item["q"], mode="qa")
            text = served_text(bundle)
            rec = judge(item, text)
            rec["error"] = None
        except Exception as e:
            rec = {**{k: item[k] for k in ("id", "class", "subject", "q", "expect")},
                   "hits": [], "missing": list(item["expect"]),
                   "verdict": "ERROR", "error": f"{type(e).__name__}: {e}", "served": ""}
        results.append(rec)
        print(f"  {i:3d}/{len(items)} {rec['id']} [{rec['class']}] "
              f"{rec['verdict']} {rec.get('missing', [])} {rec['q'][:55]}")
    RESULTS.write_text("\n".join(json.dumps(r) for r in results) + "\n")

    by_cls: dict[str, list[dict]] = {}
    for r in results:
        by_cls.setdefault(r["class"], []).append(r)
    for cls, rs in by_cls.items():
        green = sum(1 for r in rs if r["verdict"] == "MECH_GREEN")
        print(f"{cls:22s} {green}/{len(rs)} mech-green")
    reds = [r for r in results if r["verdict"] in ("MECH_RED", "ERROR")]
    print(f"\n{len(reds)} reds -> {RESULTS.name} ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
