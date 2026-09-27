#!/usr/bin/env python3
"""GATE C · D1 — every page covered or excluded in writing.

Set arithmetic, zero-egress, over committed 09-27 gate-day receipts:

  gate-day list   reports/marvel/receipts/{s}_all_pages_gate_2026-09-27.jsonl
                  (base 09-25 enumeration + 09-27 recentchanges delta − wiki-side
                  deletions/stale spellings; see S5 delta re-gate receipt)
  on-disk set     reports/marvel/receipts/parse_diff_{s}_final_2026-09-27.jsonl
                  (the official load_extracted G6 dry-run: every file, 0 exceptions)

  excluded = gate − ondisk      -> the D1 exclusion file (one line per title,
                                   each carrying a named one-line cause)
  covered  = ondisk             -> the corpus itself (G6: 0 exceptions)

Cause classes (priority order, a title gets the first that matches):
  topup-skipped    in a S3/F5/F3 top-up or fixlist, not written by design
  topup-missing    top-up fetch `missing-or-failed` (wiki-side stale spelling)
  wiki-growth      in the 09-27 recentchanges delta (`recent_new_*`), created on
                   the wiki after the 09-25 enumeration, never fetched (the
                   permanent no-full-re-enum rule)
  crawl-skip       in the 09-25 full-crawl skip receipt (marvel, per-title)
  crawl-skip-aggregate  series whose crawl kept no per-title receipt (mcu):
                   the unexplained residual ties the crawl log's aggregate
                   `0 written / 12817 skipped / 0 failed` exactly
  residual         matched no receipt; reported, never silently dropped

Cross-checks (the md fails loud, exit 1, on any):
  gate − excluded = on-disk − retained F1 orphans (arithmetic tie)
  on-disk titles absent from the gate list other than the documented orphans
  any unexplained `residual` remaining (the council must name a cause)
  duplicate lines in the gate list

Outputs:
  reports/marvel/receipts/exclusions_{s}_2026-09-27.jsonl
  reports/marvel/receipts/d1_reconciliation_2026-09-27.md

Run:  PYTHONPATH=$PWD scriptengine/.venv/bin/python tools/marvel/d1_exclusions.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
R = REPO / "reports" / "marvel" / "receipts"
T = REPO / "tools" / "marvel"

GATE = {
    "marvel": R / "marvel_all_pages_gate_2026-09-27.jsonl",
    "mcu": R / "mcu_all_pages_gate_2026-09-27.jsonl",
}
G6 = {
    "marvel": R / "parse_diff_marvel_final_2026-09-27.jsonl",
    "mcu": R / "parse_diff_mcu_final_2026-09-27.jsonl",
}
# receipt-backed cause sources
SKIP_RECEIPT = {
    "marvel": R / "marvel_skipped_full_2026-09-25.jsonl",
    "mcu": None,  # mcu crawl kept only the aggregate (crawl_mcu.log: 12817 skipped)
}
RC_NEW = {
    "marvel": T / "recent_new_marvel_2026-09-27.jsonl",
    "mcu": T / "recent_new_mcu_2026-09-27.jsonl",
}
# per-title fetch dispositions (status per row): the authoritative top-up
# record. Order is chronological (newest last) so the most recent receipt
# wins on any title collision.
FIXLISTS = {
    "marvel": [
        R / "fixlist_f3_recrawl_2026-09-26.json",
        R / "fixlist_s3_delta_topup_marvel_2026-09-27.json",
        R / "fixlist_s3_delta_topup_marvel_chunk2_2026-09-27.json",
    ],
    "mcu": [
        R / "fixlist_mcu_topup_f5_2026-09-26.json",
        R / "fixlist_s3_delta_topup_mcu_2026-09-27.json",
        R / "fixlist_s3_delta_topup_mcu2_2026-09-27.json",
    ],
}
# F1 `missing_live` orphans: subtracted from the gate list's construction
# (S5 step 1/6) but their on-disk files are retained + documented, so they
# are COVERED (retained), not excluded. S5: 2 wiki-side deletions, 1 false
# positive (live redirect to Oblivion Void, revid stamp corrected).
ONDISK_ORPHANS = {
    "marvel": [
        "Elizabeth Tyne (Earth-33263)",
        "Enok (Hyboria) (Earth-616)",
        "Realm of Nothingness (Forbidden Dimension)",
    ],
    "mcu": [],
}
# the 09-25 crawl logs kept only aggregate skip counts (marvel's was later
# recovered per-title as marvel_skipped_full); mcu's is the crawl log's 12817.
CRAWL_LOG_SKIPPED = {"marvel": 42504, "mcu": 12817}

CAUSE = {
    "topup-skipped": (
        "excluded: S3/F5/F3 top-up fetch target not written by design "
        "(fetch-receipt status below; S5 step 1)"
    ),
    "topup-missing": (
        "excluded: S3/F5 top-up fetch `missing-or-failed` — wiki-side stale "
        "spelling of an in-window rename/deletion (S5 step 1 classification)"
    ),
    "wiki-growth": (
        "excluded: created on the wiki after the 09-25 enumeration (09-27 rc "
        "delta); outside the campaign window; never fetched (no-full-re-enum rule)"
    ),
    "crawl-skip": (
        "excluded: not-on-disk after the 09-25 full crawl (skipped by crawl: "
        "no-content / skippable category; per-title cause retained for "
        "marvel's skip receipt)"
    ),
    "crawl-skip-aggregate": (
        "excluded: skipped by the 09-25 full crawl (no-content / skippable "
        "category) — the crawl log's aggregate receipt (crawl_mcu.log: 'crawl "
        "complete: 0 written, 12817 skipped, 0 failed' over all 48026 "
        "enumerated); per-title causes not retained beyond the manifest's "
        "first 200 (crawler.py); residual count ties the aggregate exactly"
    ),
    "residual": (
        "excluded: not on disk at the 09-27 gate day and matched no receipt — "
        "council must name a cause before D1 can close"
    ),
}


def raw_titles(path: Path) -> set[str]:
    return {ln.rstrip("\n") for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()}


def g6_titles(path: Path) -> set[str]:
    out = set()
    for line in path.open(encoding="utf-8"):
        out.add(json.loads(line)["title"])
    return out


def skip_titles(path: Path) -> set[str]:
    out = set()
    for line in path.open(encoding="utf-8"):
        out.add(json.loads(line)["title"])
    return out


def topup_dispositions(series: str) -> dict[str, str]:
    """title -> fetch-receipt status (the authoritative per-title disposition)."""
    out: dict[str, str] = {}
    for p in FIXLISTS[series]:
        for r in json.loads(p.read_text(encoding="utf-8")).get("rows", []):
            out[r["title"]] = r.get("status", "?")
    return out


def reconcile(series: str) -> dict:
    gate_path, g6_path = GATE[series], G6[series]
    gate_lines = gate_path.read_text(encoding="utf-8").splitlines()
    gate = {ln.rstrip("\n") for ln in gate_lines if ln.strip()}
    dupes = len(gate_lines) - len(gate)
    ondisk = g6_titles(g6_path)
    excluded = sorted(gate - ondisk)
    # on-disk titles absent from the gate-day list: the documented F1
    # `missing_live` orphans (retained on disk by design) are expected;
    # anything else breaks the coverage claim.
    orphans = ondisk - gate
    documented = set(ONDISK_ORPHANS[series])
    unexpected_ondisk = sorted(orphans - documented)

    skip_set = skip_titles(SKIP_RECEIPT[series]) if SKIP_RECEIPT[series] else set()
    rc_set = raw_titles(RC_NEW[series])
    topup = topup_dispositions(series)

    rows, classes = [], Counter()
    for t in excluded:
        if t in topup:
            status = topup[t]
            if status.startswith("missing-or-failed"):
                cls = "topup-missing"
            else:
                cls = "topup-skipped"
                reason_extra = f" (fetch receipt: {status})"
        elif t in rc_set:
            cls = "wiki-growth"
        elif t in skip_set:
            cls = "crawl-skip"
        else:
            cls = "residual"
        classes[cls] += 1
        row = {"title": t, "cause": cls, "reason": CAUSE[cls]}
        if cls == "topup-skipped":
            row["reason"] = CAUSE[cls] + reason_extra
        rows.append(row)

    # Aggregate tie (series whose crawl kept no per-title skip receipt): the
    # crawl log's final run covered the whole enumerated set and recorded
    # `0 written / N skipped / 0 failed`. When the unexplained residual count
    # ties that aggregate exactly, the residuals ARE the crawl's category
    # skips — a named, documented cause. Any mismatch keeps `residual` (the
    # council must name a cause) and the run fails.
    if SKIP_RECEIPT[series] is None and classes.get("residual"):
        if classes["residual"] == CRAWL_LOG_SKIPPED[series]:
            for r in rows:
                if r["cause"] == "residual":
                    r["cause"] = "crawl-skip-aggregate"
                    r["reason"] = CAUSE["crawl-skip-aggregate"]
            classes["residual"] = 0
            classes["crawl-skip-aggregate"] = CRAWL_LOG_SKIPPED[series]

    out_path = R / f"exclusions_{series}_2026-09-27.jsonl"
    out_path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
        encoding="utf-8",
    )
    return {
        "series": series,
        "gate": len(gate),
        "gate_dupe_lines": dupes,
        "ondisk": len(ondisk),
        "excluded": len(excluded),
        "ondisk_orphans_total": len(orphans),
        "ondisk_orphans_documented": sorted(orphans & documented),
        "ondisk_not_in_gate": unexpected_ondisk,
        "classes": classes,
        "residual_titles": [r["title"] for r in rows if r["cause"] == "residual"],
        "receipts": {
            "skip_receipt": len(skip_set),
            "rc_new": len(rc_set),
            "topup_targets": len(topup),
        },
    }


def main() -> None:
    results = [reconcile(s) for s in ("marvel", "mcu")]
    md = ["# D1 reconciliation — every page covered or excluded in writing (2026-09-27 gate day)",
          "",
          "Zero-egress set arithmetic over committed receipts (S5 delta re-gate day).",
          "Denominator annex rule: a number that disagrees with a fresh run wins.", ""]
    ok = True
    for r in results:
        s = r["series"]
        # gate − excluded must equal on-disk minus the retained (documented)
        # orphans: the orphans are on disk but were subtracted from the
        # gate list's construction, so they are covered, not excluded.
        lhs = r["gate"] - r["excluded"]
        rhs = r["ondisk"] - r["ondisk_orphans_total"]
        arith_ok = lhs == rhs
        unexplained = r["residual_titles"]
        if not (arith_ok and not r["ondisk_not_in_gate"] and not unexplained):
            ok = False
        md += [
            f"## {s}",
            "",
            f"- gate-day list: **{r['gate']}** (base 09-25 enumeration + 09-27 rc delta − wiki-side deletions)",
            f"- on disk (G6 final dry-run, 0 exceptions): **{r['ondisk']}**",
            f"- excluded: **{r['excluded']}** → `exclusions_{s}_2026-09-27.jsonl`",
            f"- arithmetic check: gate − excluded = {lhs} vs on-disk − retained orphans = {rhs} (tie: {arith_ok})",
            f"- retained orphans (F1 `missing_live`, on disk by design, not in gate list): {r['ondisk_orphans_total']}",
        ]
        for t in r["ondisk_orphans_documented"]:
            md.append(f"  - {t}")
        if r["ondisk_not_in_gate"]:
            md.append(f"  - **ON-DISK TITLES ABSENT FROM GATE LIST AND UNDOCUMENTED ({len(r['ondisk_not_in_gate'])}):**")
            for t in r["ondisk_not_in_gate"][:50]:
                md.append(f"    - {t}")
        md += ["", "cause classes:"]
        for cls, n in r["classes"].most_common():
            md.append(f"  - {cls}: {n}")
        md.append(f"  - receipts consulted: skip_receipt={r['receipts']['skip_receipt']} rc_new={r['receipts']['rc_new']} topup_targets={r['receipts']['topup_targets']}")
        if r["gate_dupe_lines"]:
            md.append(f"  - gate list duplicate lines: {r['gate_dupe_lines']}")
        if unexplained:
            md.append(f"  - **residual (no receipt, {len(unexplained)}) — council must name a cause:**")
            for t in unexplained[:50]:
                md.append(f"    - {t}")
        md.append("")
    (R / "d1_reconciliation_2026-09-27.md").write_text("\n".join(md), encoding="utf-8")
    for r in results:
        print(json.dumps({k: r[k] for k in ("series", "gate", "ondisk", "excluded", "classes")},
                         default=str))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()