"""P2.3 + P2.2 grader (council #31 P-2/P-5) — in-process, CUDA, model-unloaded.

Grades the two pre-registered banks against the live engine, through the
EXACT function the /context endpoint serves (`scriptengine.api.main.context`
— for the auto door that includes the router + the roster/relations
fallbacks), so the grade is the product path, not a re-implementation:

P-5 / P2.3  reports/csm/census_widened_csm.json (486 writer-shaped items:
            v1 60 + v2 50 + ability-pool 376) through mode="qa"
            -> reports/csm/census_widened_csm_results.jsonl
P-2 / P2.2  reports/csm/bar_audit_p14_preregistered.json (26 panel-line
            cases over the 6 D6 classes) through BOTH doors:
              qa   = the pre-registered control arm (primary verdict)
              auto = the product path (R-9-contingent supplement, P-3)
            -> reports/csm/bar_audit_p14_results.jsonl

Judge rule (both banks, tools/census_dimensions.py judge(), same MECH_GREEN
rule as the frozen v1/v2 censuses): >= 2 of 3 expect terms (case-insensitive)
in the served bundle text => MECH_GREEN. The v2 grader
(tools/census_dimensions_csm_v2_grade.py) and its frozen results file are
untouched — this script is standalone by the same rule (see its header).

Device: CUDA, whole card, Qwen down (a CPU run is ~an order of magnitude
slower and violates the GPU-only rule; CENSUS_DEVICE is honored but cuda is
the only sane value here).

Usage:
    CENSUS_DEVICE=cuda python tools/csm/p23_grader.py [--smoke]
--smoke grades the first 3 items of each bank/door (the handoff pre-check:
exercises model load + the endpoint import + judge mechanics in <5 min).
Exit 0 = all graded (ERROR rows counted and reported); exit 3 = ERRORs > 10 %
of graded items (a quietly-wrong run — halt, diagnose, do not ship).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

# MUST precede the census_dimensions import: that module does
# `os.environ.setdefault("SCRIPTENGINE_DEVICE", os.environ.get("CENSUS_DEVICE", "cpu"))`
# at module scope, so importing it for judge() silently pins the whole process
# to CPU unless the device is already chosen (the 2026-09-12 v2 run went to CPU
# for exactly this reason — the device is printed, not assumed, below).
os.environ.setdefault("CENSUS_DEVICE", "cuda")
os.environ.setdefault("SCRIPTENGINE_DEVICE", os.environ["CENSUS_DEVICE"])

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.census_dimensions import judge  # noqa: E402  same MECH_GREEN rule as v1/v2

from scriptengine.api.main import context as context_endpoint  # noqa: E402
from scriptengine.api.main import ContextRequest  # noqa: E402
from scriptengine.eval.span_recall import served_text  # noqa: E402

WIDENED = ROOT / "reports/csm/census_widened_csm.json"
BAR = ROOT / "reports/csm/bar_audit_p14_preregistered.json"
WIDENED_RESULTS = ROOT / "reports/csm/census_widened_csm_results.jsonl"
BAR_RESULTS = ROOT / "reports/csm/bar_audit_p14_results.jsonl"
SERIES = "csm"


def grade_item(
    item: dict,
    mode: str,
    subject: str | None = None,
    token_budget: int | None = None,
    top_k: int | None = None,
) -> dict:
    """One probe through the endpoint function (the product path).

    `subject` (the page the question is authored against) is what the
    campaign's own scorer sends (`eval/canon_gold.py::ask`); the no-hint
    P2.3 run left it None, which is the stricter instrument the D32
    red-split re-probes against. `token_budget`/`top_k` unset = the
    endpoint defaults (the P2.3 shape); pass 60000/50 for the campaign
    instrument (`page_campaign.py::score_facts`).
    """
    rec = {k: item[k] for k in ("id", "class", "subject", "q", "expect")}
    rec["door"] = mode
    try:
        req = {"series": SERIES, "query": item["q"], "mode": mode, "subject": subject}
        if token_budget is not None:
            req["token_budget"] = token_budget
        if top_k is not None:
            req["top_k"] = top_k
        bundle = context_endpoint(ContextRequest(**req))
        routed = bundle.get("routed")
        if routed:
            rec["routed_mode"] = routed.get("mode")
        rec.update(judge(item, served_text(bundle)))
        rec["error"] = None
    except Exception as e:
        rec.update({"hits": [], "missing": list(item["expect"]), "verdict": "ERROR",
                    "error": f"{type(e).__name__}: {e}", "served": ""})
    return rec


def dump(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="grade the first 3 of each bank/door only")
    args = ap.parse_args()
    limit = 3 if args.smoke else None

    print(f"device={os.environ['SCRIPTENGINE_DEVICE']} (CENSUS_DEVICE={os.environ['CENSUS_DEVICE']})", flush=True)
    t0 = time.time()

    # -- P-5: widened bank, qa door -------------------------------------------
    items = json.loads(WIDENED.read_text())["items"][:limit] if limit else json.loads(WIDENED.read_text())["items"]
    widened = []
    for i, item in enumerate(items, 1):
        rec = grade_item(item, "qa")
        widened.append(rec)
        print(f"  W {i:3d}/{len(items)} {rec['id']} [{rec['class']}] {rec['verdict']} "
              f"{rec.get('missing', [])} {rec['q'][:50]}", flush=True)

    # -- P-2: bar audit, both doors --------------------------------------------
    bar = json.loads(BAR.read_text())["items"][:limit] if limit else json.loads(BAR.read_text())["items"]
    bar_recs = []
    for i, item in enumerate(bar, 1):
        qa = grade_item(item, "qa")
        auto = grade_item(item, "auto")
        rec = {k: item[k] for k in ("id", "class", "subject", "q", "expect", "panel_line")}
        rec["verdict_qa"] = qa["verdict"]
        rec["verdict_auto"] = auto["verdict"]
        rec["hits_qa"], rec["missing_qa"] = qa["hits"], qa["missing"]
        rec["hits_auto"], rec["missing_auto"] = auto["hits"], auto["missing"]
        rec["routed_mode"] = auto.get("routed_mode")
        rec["error_qa"], rec["error_auto"] = qa["error"], auto["error"]
        rec["served_qa"] = qa.get("served", "")
        bar_recs.append(rec)
        print(f"  B {i:2d}/{len(bar)} {rec['id']} [{rec['class']}] "
              f"qa={rec['verdict_qa']} auto={rec['verdict_auto']} "
              f"(routed {rec.get('routed_mode')}) {rec['q'][:45]}", flush=True)

    dump(WIDENED_RESULTS, widened)
    dump(BAR_RESULTS, bar_recs)

    def green(rs: list[dict], key: str | None) -> int:
        return sum(1 for r in rs if (r.get(key) if key else r.get("verdict")) == "MECH_GREEN")

    w_err = sum(1 for r in widened if r["verdict"] == "ERROR")
    b_err = sum(1 for r in bar_recs if r["error_qa"] or r["error_auto"])
    print(f"widened qa      {green(widened, None)}/{len(widened)} mech-green ({w_err} errors)")
    print(f"bar-audit qa    {green(bar_recs, 'verdict_qa')}/{len(bar_recs)} mech-green")
    print(f"bar-audit auto  {green(bar_recs, 'verdict_auto')}/{len(bar_recs)} mech-green (R-9-contingent)")
    print(f"-> {WIDENED_RESULTS.name} + {BAR_RESULTS.name} ({time.time() - t0:.0f}s)")
    errs, total = w_err + b_err * 2, len(widened) + 2 * len(bar_recs)
    print(f"{errs}/{total} probe errors")
    if total and errs / total > 0.10:
        print("HALT: error rate > 10% (a quietly-wrong run)")
        sys.exit(3)


if __name__ == "__main__":
    main()