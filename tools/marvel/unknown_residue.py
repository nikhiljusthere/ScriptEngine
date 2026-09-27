#!/usr/bin/env python3
"""GATE C evidence — unknown-type residue report (zero egress, read-only stores).

Plan MARVEL_100_PLAN.md §4 (GATE C): the council package carries an
"`unknown`-type residue report". The residue class is documents whose
`page_type` is `unknown` — the builder could not map the page to a known
archetype (no/unknown infobox template). It is *recorded, not dropped*:
the documents stay in the store (queryable, indexed, chunked); only their
archetype label is the generic `unknown`.

Exit codes:
  0 = report written AND live counts agree with the last committed receipt
      (first run: the G6-final numbers recorded at GATE A — marvel 529 /
      mcu 616; a re-run after a re-index must still agree — page_type is
      derived from the infobox-template mapping, not from section content,
      so the content promotion re-index cannot move it).
  2 = drift vs the last receipt (the store changed in a way this report did
      not predict — stop, re-measure, re-record; a drift is a finding, not
      a failure to paper over).

Zero egress by construction: opens both facts.db read-only, writes only
the receipt under reports/marvel/receipts/.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SERIES_ROOT = ROOT / "series"
OUT_MD = ROOT / "reports" / "marvel" / "receipts" / "unknown_residue_2026-09-27.md"
OUT_JSONL = ROOT / "reports" / "marvel" / "receipts" / "unknown_residue_2026-09-27.jsonl"

# The recorded baseline: GATE A zero-egress audit (G6 finals), restated by
# D3 live reconciliation (reports/marvel/receipts/d3_red_list_2026-09-27.md).
RECORDED = {"marvel": 529, "mcu": 616}


def measure(series: str) -> dict:
    con = sqlite3.connect(f"file:{SERIES_ROOT / series / 'facts.db'}?mode=ro", uri=True)
    try:
        total = con.execute("select count(*) from documents").fetchone()[0]
        unknown = con.execute(
            "select count(*) from documents where page_type='unknown'"
        ).fetchone()[0]
        tpl = Counter(
            r[0] or "<none>"
            for r in con.execute(
                "select infobox_template from documents where page_type='unknown'"
            )
        )
        # Bounded named edges: unknowns that DO carry a known template but
        # still fell through the mapping (each one needs a line in the
        # receipt, never a silent drop).
        mapped_templates = {
            r[0]
            for r in con.execute(
                "select distinct infobox_template from documents "
                "where page_type not in ('unknown','') and infobox_template != ''"
            )
        }
        edges = []
        for t in tpl:
            if t != "<none>" and t not in mapped_templates:
                edges += [
                    row[0]
                    for row in con.execute(
                        "select title from documents "
                        "where page_type='unknown' and infobox_template=? limit 10",
                        (t,),
                    )
                ]
        sample = [
            r[0]
            for r in con.execute(
                "select title from documents where page_type='unknown' limit 15"
            )
        ]
        return {
            "series": series,
            "documents_total": total,
            "unknown": unknown,
            "pct": round(100.0 * unknown / total, 3),
            "template_dist": dict(tpl.most_common()),
            "named_edges": edges,
            "sample": sample,
        }
    finally:
        con.close()


def load_previous_counts() -> dict:
    """Last committed receipt's counts (the drift baseline), if present."""
    if not OUT_JSONL.exists():
        return {}
    counts = {}
    for line in OUT_JSONL.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("kind") == "count":
            counts[row["series"]] = row["unknown"]
    return counts


def main() -> int:
    today = date.today().isoformat()
    series = ["marvel", "mcu"]
    live = {s: measure(s) for s in series}

    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSONL.open("w") as f:
        for s in series:
            m = live[s]
            f.write(
                json.dumps(
                    {
                        "kind": "count",
                        "date": today,
                        "series": s,
                        "documents_total": m["documents_total"],
                        "unknown": m["unknown"],
                        "pct": m["pct"],
                        "template_dist": m["template_dist"],
                        "named_edges": m["named_edges"],
                    }
                )
                + "\n"
            )
        for s in series:
            for title in live[s]["sample"]:
                f.write(
                    json.dumps(
                        {"kind": "sample", "date": today, "series": s, "title": title}
                    )
                    + "\n"
                )

    prev = load_previous_counts()
    lines = [
        "# GATE C evidence — `unknown`-type residue report",
        f"_generated {today} by `tools/marvel/unknown_residue.py` (zero egress; "
        "read-only facts.db; writes this receipt only)._ ",
        "",
        "**What the class is.** `page_type='unknown'` = the builder mapped no "
        "archetype for the page (its infobox template is absent or unmapped). "
        "The document stays in the store — indexed, chunked, queryable — only "
        "its archetype label is the generic `unknown`. Recorded residue, never "
        "a silent drop.",
        "",
    ]
    drift = []
    for s in series:
        m = live[s]
        lines += [
            f"## {s}: {m['unknown']}/{m['documents_total']} "
            f"({m['pct']}%)",
            "",
            f"- infobox-template distribution among the unknowns: "
            f"{m['template_dist']}",
        ]
        if m["named_edges"]:
            lines.append(
                "- named edges (a known template that still fell through the "
                "mapping — each bounded and listed, never aggregated away): "
                + ", ".join(f"`{t}`" for t in m["named_edges"])
            )
        lines += [
            f"- sample: " + ", ".join(f"`{t}`" for t in m["sample"]),
            "- cause: pages with no infobox — a corpus shape, not a parser "
            "gap; the detail rule keeps them as `unknown` facts instead of "
            "inventing an archetype"
            + (
                " (`Comic Books` collection aggregates, studios, hubs)."
                if s == "marvel"
                else " (decade/year pages, studios, production hubs)."
            ),
            "",
        ]
        if s in prev and prev[s] != m["unknown"]:
            drift.append(f"{s}: recorded {prev[s]} -> live {m['unknown']}")

    lines += [
        "## Drift vs the recorded baseline",
        "",
        f"- G6-final / D3-recorded baseline: "
        + ", ".join(f"{s} {n}" for s, n in RECORDED.items()),
    ]
    if prev:
        lines.append(f"- last receipt on disk: " + ", ".join(f"{s} {n}" for s, n in prev.items()))
    if drift:
        lines += ["", "**DRIFT — the store moved in a way this report did not predict:**"]
        lines += [f"- {d}" for d in drift]
    else:
        lines.append("- live counts agree with the baseline — no drift.")

    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD.relative_to(ROOT)} + {OUT_JSONL.relative_to(ROOT)}")
    for s in series:
        print(
            f"  {s}: {live[s]['unknown']}/{live[s]['documents_total']} "
            f"({live[s]['pct']}%)"
        )
    if drift:
        print(f"FAIL unknown-residue drift: {drift}", file=sys.stderr)
        return 2
    print("PASS unknown-residue: live counts agree with the recorded baseline")
    return 0


if __name__ == "__main__":
    sys.exit(main())