"""D32 red-split probe: re-grade the P23 MECH_RED rows WITH the subject hint.

The campaign's own scorer (eval/canon_gold.py::ask) sends each question's
`subject` (the page hint); the P2.3 grader probed without it, which leaves
the qa door's R6 recall floor empty. This probe answers the D32 question:
of the 69 widened + 15 bar qa-door reds, which are no-hint-only failures?

In-process, CUDA, same endpoint function and judge rule as p23_grader.py
(Qwen may be up: the probe is short and bounded, the sanctioned headroom
borrow). Only the P23-red subset is re-graded, so one run is a few minutes.

Usage:
    python tools/csm/red_hint_probe.py [--smoke]

Writes:
    reports/csm/census_widened_csm_results_hints.jsonl
    reports/csm/bar_audit_p14_results_hints.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.csm.p23_grader import (  # noqa: E402
    BAR,
    BAR_RESULTS,
    WIDENED,
    grade_item,
)

WIDENED_HINTS = ROOT / "reports/csm/census_widened_csm_results_hints.jsonl"
BAR_HINTS = ROOT / "reports/csm/bar_audit_p14_results_hints.jsonl"
WIDENED_CAMPAIGN = ROOT / "reports/csm/census_widened_csm_results_hints_campaign.jsonl"
BAR_CAMPAIGN = ROOT / "reports/csm/bar_audit_p14_results_hints_campaign.jsonl"
# The campaign's own instrument (eval/canon_gold.py::ask via page-run):
CAMPAIGN_BUDGET = 60000
CAMPAIGN_TOP_K = 50


def red_ids(path: Path, key: str) -> list[str]:
    return [
        json.loads(line)["id"]
        for line in path.read_text().splitlines()
        if line.strip()
        and json.loads(line).get(key) == "MECH_RED"
    ]


def by_id(path: Path) -> dict:
    items = json.loads(path.read_text())["items"]
    return {item["id"]: item for item in items}


def dump(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument(
        "--campaign",
        action="store_true",
        help="re-probe the still-red rows at the campaign instrument "
        f"(subject + token_budget={CAMPAIGN_BUDGET} + top_k={CAMPAIGN_TOP_K})",
    )
    args = ap.parse_args()
    t0 = time.time()

    w_items = by_id(WIDENED)
    if args.campaign:
        w_reds = red_ids(WIDENED_HINTS, "verdict")
        out_w = WIDENED_CAMPAIGN
    else:
        w_reds = red_ids(WIDENED_HINTS.parent / "census_widened_csm_results.jsonl", "verdict")
        out_w = WIDENED_HINTS
    w_reds = [r for r in w_reds if r in w_items]
    if args.smoke:
        w_reds = w_reds[:3]
    print(
        f"widened: {len(w_reds)} rows re-graded"
        f"{' at the campaign instrument' if args.campaign else ' WITH subject'}",
        flush=True,
    )
    w_rows = []
    for i, rid in enumerate(w_reds, 1):
        item = w_items[rid]
        rec = grade_item(
            item,
            "qa",
            subject=item.get("subject"),
            token_budget=CAMPAIGN_BUDGET if args.campaign else None,
            top_k=CAMPAIGN_TOP_K if args.campaign else None,
        )
        w_rows.append(rec)
        print(f"  W {i:3d}/{len(w_reds)} {rid} {rec['verdict']} {rec['q'][:45]}", flush=True)
    dump(out_w, w_rows)

    b_items = by_id(BAR)
    if args.campaign:
        b_reds = red_ids(BAR_HINTS, "verdict_qa")
        out_b = BAR_CAMPAIGN
    else:
        b_reds = [r for r in red_ids(BAR_RESULTS, "verdict_qa") if r in b_items]
        out_b = BAR_HINTS
    b_reds = [r for r in b_reds if r in b_items]
    if args.smoke:
        b_reds = b_reds[:2]
    print(
        f"bar: {len(b_reds)} rows re-graded"
        f"{' at the campaign instrument' if args.campaign else ' WITH subject'}",
        flush=True,
    )
    b_rows = []
    for i, rid in enumerate(b_reds, 1):
        item = b_items[rid]
        qa = grade_item(
            item,
            "qa",
            subject=item.get("subject"),
            token_budget=CAMPAIGN_BUDGET if args.campaign else None,
            top_k=CAMPAIGN_TOP_K if args.campaign else None,
        )
        rec = {k: item[k] for k in ("id", "class", "subject", "q", "expect", "panel_line")}
        rec["verdict_qa"] = qa["verdict"]
        rec["hits_qa"], rec["missing_qa"] = qa["hits"], qa["missing"]
        rec["error_qa"] = qa["error"]
        rec["served_qa"] = qa.get("served", "")
        b_rows.append(rec)
        print(f"  B {i:2d}/{len(b_reds)} {rid} {rec['verdict_qa']} {rec['q'][:45]}", flush=True)
    dump(out_b, b_rows)

    def split(rows, key):
        flipped = sum(1 for r in rows if r.get(key) == "MECH_GREEN")
        errs = sum(1 for r in rows if r.get(key) == "ERROR")
        return flipped, errs

    wf, we = split(w_rows, "verdict")
    bf, be = split(b_rows, "verdict_qa")
    label = "campaign-instrument" if args.campaign else "hint"
    print(
        f"-> widened {wf}/{len(w_rows)} green ({label}, {we} errors); "
        f"bar {bf}/{len(b_rows)} green ({label}, {be} errors) "
        f"({time.time() - t0:.0f}s)",
        flush=True,
    )
    errs, total = we + be, len(w_rows) + len(b_rows)
    if total and errs / total > 0.10:
        print("HALT: error rate > 10% (a quietly-wrong run)")
        sys.exit(3)


if __name__ == "__main__":
    main()