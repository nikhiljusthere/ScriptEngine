"""D6 falsifiable ranking probe (chairman remain #1, re-vote council).

Pre-registration: reports/csm/receipts/d6_probe/PROBE_PREDICT.md (written
BEFORE this run; fresh-context certified with FAIL->fixes applied).
This runner executes P1/P2/P3 and writes PROBE_RESULT.json. Exit 0 =
probe executed cleanly (GREEN or RED per the registered rules);
exit 3 = harness failure (no verdict).

Prediction under test: row csm-dim-arcb-05 is RED solely because its gold
chunk (id 4988, "Katana Man arc / Synopsis", carries all 3 expect terms)
is ranked out of the width-8 qa bundle by the character card.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

os.environ.setdefault("CENSUS_DEVICE", "cuda")
os.environ.setdefault("SCRIPTENGINE_DEVICE", os.environ["CENSUS_DEVICE"])

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.census_dimensions import judge  # noqa: E402
from scriptengine.api.main import ContextRequest  # noqa: E402
from scriptengine.api.main import context as context_endpoint  # noqa: E402
from scriptengine.config import get_settings, series_paths  # noqa: E402
from scriptengine.eval.span_recall import served_text  # noqa: E402
from scriptengine.retrieve.hybrid import HybridRetriever  # noqa: E402

ROW_ID = "csm-dim-arcb-05"
GOLD_ID = 4988
OUT = ROOT / "reports/csm/receipts/d6_probe/PROBE_RESULT.json"
POST486 = ROOT / "reports/csm/census_widened_csm_results.jsonl"


def sh(args: list[str]) -> str:
    return subprocess.run(args, capture_output=True, text=True,
                          cwd=str(ROOT), check=True).stdout.strip()


def scan48(settings, paths, out: Path, t0: float) -> int:
    """Grade every amended dim+abl row with subject=item[subject] set.

    Measurement only: the official no-hint grade is untouched. Returns 0
    with per-row flips in PROBE3_RESULT.json; per-row ERRORs counted
    separately (p23 convention), never as green.
    """
    from collections import Counter
    reg = [json.loads(l) for l in
           (ROOT / "reports/csm/census_v1_floor_triage.jsonl").read_text().splitlines()
           if l.strip()]
    ids = [r["id"] for r in reg
           if r.get("bucket") in ("dim", "abl")
           and (r.get("triage") or "").startswith("NAMED-LIMIT (D6-close")]
    post = {json.loads(l)["id"]: json.loads(l)
            for l in POST486.read_text().splitlines() if l.strip()}
    rows, errs = [], 0
    for rid in ids:
        item = post[rid]
        try:
            bundle = context_endpoint(ContextRequest(
                series="csm", query=item["q"], mode="qa",
                subject=item.get("subject")))
            v = judge(item, served_text(bundle))
            rows.append({"id": rid, "class": item["class"],
                         "subject": item.get("subject"),
                         "baseline": "MECH_RED",
                         "verdict": v["verdict"], "hits": v["hits"],
                         "missing": v["missing"],
                         "flipped": v["verdict"] == "MECH_GREEN"})
        except Exception as e:
            errs += 1
            rows.append({"id": rid, "class": item["class"],
                         "subject": item.get("subject"),
                         "baseline": "MECH_RED", "verdict": "ERROR",
                         "hits": [], "missing": list(item["expect"]),
                         "flipped": False, "error": f"{type(e).__name__}: {e}"})
    flips = sum(1 for r in rows if r["flipped"])
    by_class = Counter()
    for r in rows:
        by_class[(r["class"], r["verdict"])] += 1
    res = {"n": len(rows), "flips": flips, "errors": errs,
           "by_class": [f"{c} {v}: {n}" for (c, v), n in sorted(by_class.items())],
           "prediction_met": flips >= 40 and errs == 0,
           "rows": rows, "seconds": round(time.time() - t0, 1)}
    out.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print(json.dumps({"scan48_flips": f"{flips}/{len(rows)}",
                      "errors": errs, "prediction_met": res["prediction_met"],
                      "by_class": res["by_class"],
                      "seconds": res["seconds"]}))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--row", default=ROW_ID)
    ap.add_argument("--subject", default=None)
    ap.add_argument("--focus", default=None)
    ap.add_argument("--out", default="PROBE_RESULT.json")
    ap.add_argument("--scan48", action="store_true",
                    help="grade all amended dim+abl rows with subject set")
    args = ap.parse_args()
    t0 = time.time()
    res: dict = {"row": args.row, "gold_chunk": GOLD_ID,
                 "subject": args.subject, "focus": args.focus,
                 "predictions": {}, "observations": {},
                 "probe_verdict": None, "error": None}
    out = ROOT / "reports/csm/receipts/d6_probe" / args.out
    try:
        settings = get_settings()
        paths = series_paths("csm", settings)
        if args.scan48:
            return scan48(settings, paths, out, t0)
        item = {json.loads(l)["id"]: json.loads(l)
                for l in POST486.read_text().splitlines() if l.strip()}[args.row]
        q = item["q"]

        res["build"] = {
            "git_head": sh(["git", "rev-parse", "HEAD"]),
            "git_status": sh(["git", "status", "--short"]),
            "git_diff_stat": sh(["git", "diff", "--stat"]),
            "device": os.environ["CENSUS_DEVICE"],
            "final_top_k": settings.final_top_k,
            "events": None, "chunks": None,
        }
        db = sqlite3.connect(f"file:{paths.facts_db}?mode=ro", uri=True)
        res["build"]["events"] = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        res["build"]["chunks"] = db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        grow = db.execute(
            "SELECT doc_title, breadcrumb, level, text FROM chunks WHERE id = ?",
            (GOLD_ID,)).fetchone()
        assert grow is not None, "gold chunk 4988 unresolvable (corpus drift)"
        gdoc, gcrumb, glevel, gtext = grow
        assert gdoc == "Katana Man arc" and "Synopsis" in gcrumb, "gold pin mismatch"
        for term in item["expect"]:
            assert term in gtext, f"gold chunk lost term: {term[:40]}"
        res["observations"]["gold_pin"] = {
            "doc_title": gdoc, "breadcrumb": gcrumb, "level": glevel,
            "chars": len(gtext), "carries_all_3_terms": True}

        # P1: reproduce the verdict through the exact p23 path (+subject).
        bundle = context_endpoint(ContextRequest(
            series="csm", query=q, mode="qa", subject=args.subject))
        p1 = judge(item, served_text(bundle))
        res["observations"]["P1"] = {
            "verdict": p1["verdict"], "missing": p1["missing"],
            "bundle_beats": len(bundle.get("beats") or []),
            "beat_docs": [b.get("doc_title", "") for b in (bundle.get("beats") or [])][:12]}

        # P2: rank of the gold chunk at product width (8) and wide (50).
        retr = HybridRetriever(paths, settings)
        try:
            r8 = retr.search(q, top_k=8, focus=args.focus)
            ids8 = [p.chunk_id for p in r8.passages]
            drop8 = [p.chunk_id for p in r8.dropped]
            r50 = retr.search(q, top_k=50, focus=args.focus)
            ids50 = [p.chunk_id for p in r50.passages]
            drop50 = [p.chunk_id for p in r50.dropped]
        finally:
            retr.close()
        rank50 = ids50.index(GOLD_ID) + 1 if GOLD_ID in ids50 else None
        res["observations"]["P2"] = {
            "gold_in_top8": GOLD_ID in ids8,
            "gold_in_dropped8": GOLD_ID in drop8,
            "gold_rank_top50": rank50,
            "gold_in_dropped50": GOLD_ID in drop50,
            "top8_docs": [p.doc_title for p in r8.passages],
            "n_dropped8": len(drop8)}

        # P3: counterfactual bundle = P1 bundle + gold beat.
        mod = dict(bundle)
        mod["beats"] = list(bundle.get("beats") or []) + [{
            "title": f"{gdoc} / {gcrumb}", "doc_title": gdoc,
            "breadcrumb": gcrumb, "text": gtext}]
        p3 = judge(item, served_text(mod))
        res["observations"]["P3"] = {
            "verdict": p3["verdict"], "hits": p3["hits"], "missing": p3["missing"]}

        p1_red = p1["verdict"] == "MECH_RED" and len(p1["missing"]) == 3
        p2_buried = (GOLD_ID not in ids8 and GOLD_ID in drop8
                     and rank50 is not None and 9 <= rank50 <= 50)
        p3_green = (p3["verdict"] == "MECH_GREEN" and len(p3["hits"]) == 3)
        res["predictions"] = {"P1_RED_missing3": p1_red,
                              "P2_buried_rank9_50": p2_buried,
                              "P3_GREEN_hits3": p3_green}
        res["probe_verdict"] = ("GREEN" if (p1_red and p2_buried and p3_green)
                                else "RED")
        res["seconds"] = round(time.time() - t0, 1)
        out.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
        print(json.dumps({"probe": res["probe_verdict"], **res["predictions"],
                          "rank50": rank50, "seconds": res["seconds"]}))
        return 0
    except Exception as e:  # harness failure: no verdict
        res["error"] = f"{type(e).__name__}: {e}"
        out.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
        print(f"PROBE HARNESS FAILURE: {e}")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
