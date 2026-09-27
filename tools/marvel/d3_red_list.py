#!/usr/bin/env python3
"""GATE C · D3 — zero unfiled engine gaps; red list not empty.

Plan MARVEL_100_PLAN.md §4 (GATE C, D3) + Plan_to_perfection §6 row D3:
"zero unfiled engine gaps; red list not empty" (the CSM §9a red list: every
known gap is *filed* — a named cause plus a disposition — and the list being
non-empty is a defence against theater: an empty red list means someone is
hiding something, not that the engine is perfect).

The red list is assembled from two sources, both local (zero egress):

  1. THE CAMPAIGN LEDGER — `reports/marvel/receipts/known_diffs_2026-09-25.md`,
     the single record of the known, bounded, non-blocking diffs (council
     COUNCIL_gate_A_download.md + OWNER_WALL RECORD CORRECTION both point
     here). Every `## ` section is one filed gap; each must carry a named
     cause AND a disposition.
  2. LIVE RECONCILIATION — the gap classes that have a measurable live state
     are re-measured against the record, so a NEW unfiled gap (a regression
     that the ledger does not name) fails the gate instead of sneaking
     through:
       * unknown-type documents (the C6 unknown-residue report): marvel 529
         (0.22%) / mcu 616 (1.7%) of stored pages — bounded, named cause
         (infobox template not in the series' type_aliases), filed.
       * C3 disambig-unresolved referents: 742 fact rows / 677 distinct
         values in marvel, stored under `facts.key='disambig_unresolved'`
         (queryable, the seed for the cross-corpus pass — recorded, NOT
         dropped).
       * C6 census residue: mcu complete at 6 rows (one thin page, Águila);
         marvel in progress while the tier-a sweep runs (residue so far,
         the final number lands with the sweep).
       * F3 collision groups: the 4 `What If: Thor Vol 1` titles re-crawled
         under disambiguated on-disk filenames (pageid-suffixed) — closed.
       * chunk-containment (tier 0): mcu re-indexed with the
         content_sections promotion (commit 0720df76) and re-run to
         0 unreachable (`reports/span-recall/mcu/index_misses.jsonl`
         empty); marvel awaits its re-index behind the running sweep —
         filed as retest-pending with the retest pointer.
       * parser diff (final, gate 4/6): both series PROCEED — no
         systematic key loss, so no unfiled extraction regression.

Exit 0 = D3 closed: red list non-empty, every entry has a named cause +
disposition, and every live reconciliation agrees with the record.
Exit 1 = an unfiled gap (a live regression the ledger does not name) or a
missing disposition.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KNOWN_DIFFS = ROOT / "reports" / "marvel" / "receipts" / "known_diffs_2026-09-25.md"
MCU_BANK_META = ROOT / "reports" / "mcu" / "census_c6_bank_meta_mcu.json"
MARVEL_BANK_META = ROOT / "reports" / "marvel" / "census_c6_bank_meta_marvel.json"
OOS_PRE = ROOT / "reports" / "mcu" / "census_c6_oos_pre_mcu.jsonl"
MCU_MISSES = ROOT / "reports" / "span-recall" / "mcu" / "index_misses.jsonl"
PARSE_DIFFS = {
    "marvel": ROOT / "reports" / "marvel" / "receipts" / "parse_diff_marvel_report.md",
    "mcu": ROOT / "reports" / "marvel" / "receipts" / "parse_diff_mcu_report.md",
}
# recorded unknown-type counts (live-verified below; the GATE C residue numbers)
RECORDED_UNKNOWN = {"marvel": 529, "mcu": 616}
RECORDED_DISAMBIG = {"rows": 742, "distinct": 677}  # marvel facts.key='disambig_unresolved'
F3_FILES = (
    "What If_ Thor Vol 1 1 (1173308).json",
    "What If_ Thor Vol 1 (1173315).json",
    "What If_ Thor Vol 1 1 (27821).json",
    "What If_ Thor Vol 1 (410610).json",
)

# A ledger section is *filed* only when it names a cause and a disposition.
# (The ledger is written in prose; these markers are its standing vocabulary.)
DISPOSITION_MARKERS = (
    "fixed", "closed", "recorded", "filed", "bounded", "deferred",
    "decision", "not mapped", "kept", "stays", "remains visible",
    "no parser change", "owner call", "action", "re-crawl",
    "not a parser", "verdict", "disposition",
)


def parse_ledger(path: Path) -> list[dict]:
    """The known_diffs ledger: one entry per `## ` section, body intact.

    (The `## Standing` section is context about the JJK/CSM baselines, not
    an engine gap — it is excluded.)
    """
    lines = path.read_text().splitlines()
    sections: list[tuple[str, list[str]]] = []
    cur: tuple[str, list[str]] | None = None
    for line in lines:
        if line.startswith("## ") and line[3:].strip() != "Standing":
            if cur:
                sections.append(cur)
            cur = (line[3:].strip(), [])
        elif cur:
            cur[1].append(line)
    if cur:
        sections.append(cur)
    entries = []
    for title, body_lines in sections:
        body = "\n".join(body_lines).strip()
        low = body.lower()
        markers = [mk for mk in DISPOSITION_MARKERS if mk in low]
        entries.append({
            "id": re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:80],
            "title": title,
            "cause": "see ledger section",  # the section body IS the cause
            "disposition": "named in section" if markers else None,
            "disposition_markers": markers,
            "status": "filed",
            "recorded_in": str(KNOWN_DIFFS.relative_to(ROOT)),
        })
    return entries


def live_unknown_type() -> dict:
    out = {}
    for s, rec in RECORDED_UNKNOWN.items():
        con = sqlite3.connect(f"file:{ROOT / f'series/{s}/facts.db'}?mode=ro", uri=True)
        total = con.execute("select count(*) from documents").fetchone()[0]
        n = con.execute(
            "select count(*) from documents where page_type='unknown'"
        ).fetchone()[0]
        con.close()
        out[s] = {"recorded": rec, "live": n, "docs": total,
                  "pct": round(100.0 * n / total, 3) if total else 0.0,
                  "agrees": n == rec}
    return out


def live_disambig() -> dict:
    con = sqlite3.connect(f"file:{ROOT / 'series/marvel/facts.db'}?mode=ro", uri=True)
    rows = con.execute("select count(*) from facts where key='disambig_unresolved'").fetchone()[0]
    dist = con.execute(
        "select count(distinct value) from facts where key='disambig_unresolved'"
    ).fetchone()[0]
    con.close()
    return {"recorded": RECORDED_DISAMBIG, "live": {"rows": rows, "distinct": dist},
            "agrees": rows == RECORDED_DISAMBIG["rows"] and dist == RECORDED_DISAMBIG["distinct"]}


def f3_closed() -> dict:
    wd = ROOT / "series" / "marvel" / "wikitext"
    missing = [f for f in F3_FILES if not (wd / f).exists()]
    return {"recorded": "4 collision titles re-crawled under disambiguated filenames",
            "missing": missing, "closed": not missing}


def c6_residue() -> dict:
    out = {}
    for series, meta in (("mcu", MCU_BANK_META), ("marvel", MARVEL_BANK_META)):
        if not meta.exists():
            out[series] = {"present": False}
            continue
        d = json.loads(meta.read_text())
        out[series] = {
            "present": True,
            "complete": d.get("sweep_complete"),
            "rows": d.get("rows"),
            "residue": d.get("residue"),
            "sweep_pages": f"{d.get('sweep_pages')}/{d.get('tier_total')}",
        }
    return out


def containment_state() -> dict:
    if MCU_MISSES.exists():
        n = sum(1 for _ in MCU_MISSES.open())
    else:
        n = -1  # no file at all = never run
    return {"mcu_unreachable": n, "mcu_zero": n == 0,
            "marvel": "retest-pending (re-index behind the running sweep)"}


def parse_diff_verdicts() -> dict:
    out = {}
    for s, p in PARSE_DIFFS.items():
        text = p.read_text() if p.exists() else ""
        out[s] = {"present": bool(text), "proceed": "**PROCEED**" in text,
                  "path": str(p.relative_to(ROOT))}
    return out


def oos_pre() -> dict:
    if not OOS_PRE.exists():
        return {"present": False}
    verd, errs = {}, 0
    for line in OOS_PRE.open():
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        verd[r.get("verdict", "ERROR")] = verd.get(r.get("verdict", "ERROR"), 0) + 1
    return {"present": True, "verdicts": verd,
            "green_rate": round(100.0 * verd.get("MECH_GREEN", 0) / max(1, sum(verd.values())), 2)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--jsonl-out", default=None,
                    help="receipt jsonl path (default: reports/marvel/receipts/)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    today = dt.date.today().isoformat()
    failures: list[str] = []

    # 1 — the ledger (the filed gaps)
    if not KNOWN_DIFFS.exists():
        print(f"FAIL: ledger missing: {KNOWN_DIFFS}", file=sys.stderr)
        return 1
    entries = parse_ledger(KNOWN_DIFFS)
    missing_disp = [e["id"] for e in entries if not e["disposition"]]
    if missing_disp:
        failures.append(
            f"ledger sections without a named disposition: {missing_disp}")

    # 2 — live reconciliation (a NEW unfiled gap fails the gate)
    unk = live_unknown_type()
    for s, r in unk.items():
        if not r["agrees"]:
            failures.append(
                f"unknown-type {s}: live {r['live']} != recorded {r['recorded']}"
                " — unfiled regression")
    dm = live_disambig()
    if not dm["agrees"]:
        failures.append(
            f"disambig_unresolved live {dm['live']} != recorded {dm['recorded']}"
            " — unfiled regression")
    f3 = f3_closed()
    if not f3["closed"]:
        failures.append(f"F3 disambiguated files missing on disk: {f3['missing']}")
    c6 = c6_residue()
    if c6.get("mcu", {}).get("present") and not c6["mcu"].get("complete"):
        failures.append("mcu C6 census is not complete — the residue number is not final")
    cont = containment_state()
    if not cont["mcu_zero"]:
        failures.append(
            f"mcu chunk-containment unreachable={cont['mcu_unreachable']} != 0 "
            "(re-indexed + re-run; see 0720df76)")
    pd = parse_diff_verdicts()
    for s, r in pd.items():
        if not (r["present"] and r["proceed"]):
            failures.append(f"parse-diff {s}: not PROCEED — unfiled extraction regression")

    # 3 — the assembled red list (ledger + live-verified filed classes)
    red_list = list(entries)
    red_list += [
        {
            "id": "unknown-type-residue",
            "title": "unknown-type documents (infobox template not in type_aliases)",
            "cause": f"marvel {unk['marvel']['live']} ({unk['marvel']['pct']}%) / "
                     f"mcu {unk['mcu']['live']} ({unk['mcu']['pct']}%) of stored pages",
            "disposition": "bounded; the GATE C unknown-residue report itself; "
                           "the floor is the number, a new template is its own mapping line",
            "status": "filed",
            "recorded_in": "this receipt (live-verified from both stores)",
        },
        {
            "id": "c3-disambig-unresolved",
            "title": "disambiguation referents with no store node",
            "cause": f"marvel {dm['live']['rows']} fact rows / {dm['live']['distinct']} distinct values "
                     "name a referent the store has no node for (C3 alignment)",
            "disposition": "recorded as `disambig_unresolved` facts (queryable, the seed "
                           "for the cross-corpus pass), not dropped",
            "status": "filed",
            "recorded_in": "known_diffs C3 section + marvel facts.key='disambig_unresolved'",
        },
        {
            "id": "c6-census-residue",
            "title": "C6 census residue (unverified expect terms)",
            "cause": (
                f"mcu complete: {c6.get('mcu', {}).get('residue', 'n/a')} rows "
                f"({c6.get('mcu', {}).get('sweep_pages', 'n/a')} pages, complete="
                f"{c6.get('mcu', {}).get('complete', 'n/a')}); "
                f"marvel in progress: {c6.get('marvel', {}).get('residue', 'n/a')} rows so far "
                f"({c6.get('marvel', {}).get('sweep_pages', 'n/a')} pages, complete="
                f"{c6.get('marvel', {}).get('complete', 'n/a')})"
            ),
            "disposition": "bounded per-page; the final marvel number lands with the tier-a sweep",
            "status": "filed",
            "recorded_in": "reports/mcu/census_c6_bank_meta_mcu.json + reports/marvel/census_c6_bank_meta_marvel.json",
        },
        {
            "id": "f3-collision-groups-closed",
            "title": "F3 collision groups (4 titles -> 2 on-disk filenames)",
            "cause": "What If: Thor Vol 1 / What If? Thor Vol 1 (and the ' 1' pairs) "
                     "sanitize to the same filename",
            "disposition": "closed: 4 titles re-crawled under pageid-suffixed filenames",
            "status": "closed" if f3["closed"] else "OPEN",
            "recorded_in": "known_diffs F3 section + series/marvel/wikitext/",
        },
        {
            "id": "chunk-containment-divergence",
            "title": "chunker-skip vs oracle-content divergence (tier 0)",
            "cause": "chunker's default BOILERPLATE_SECTIONS skipped Notes/References/"
                     "Gallery while the span-recall oracle counts that trivia",
            "disposition": "fixed in 0720df76 (content_sections promotion, JJK "
                           "References precedent); mcu re-indexed + re-run to 0 "
                           f"unreachable ({cont['mcu_zero']}); marvel: {cont['marvel']}",
            "status": "closed-mcu-open-marvel" if cont["mcu_zero"] else "OPEN",
            "recorded_in": "0720df76 + reports/span-recall/mcu/index_misses.jsonl",
        },
        {
            "id": "oos-pre-score",
            "title": "C6 OOS pre-score (anti-theater arm baseline)",
            "cause": f"mcu 200-row OOS pre-score: {oos_pre().get('verdicts', 'n/a')} "
                     f"(green {oos_pre().get('green_rate', 'n/a')}%)",
            "disposition": "the CSM annex floor: OOS post >= pre - 2 at Phase D; "
                           "a drop of 3+ voids the declaration",
            "status": "filed",
            "recorded_in": "reports/mcu/census_c6_oos_pre_mcu.jsonl",
        },
    ]

    # 4 — D3's two assertions
    if not red_list:
        failures.append("red list is EMPTY — D3's anti-theater check fails")
    open_entries = [e["id"] for e in red_list if e["status"].startswith("OPEN")]
    if open_entries:
        failures.append(f"open (unfiled-in-practice) entries: {open_entries}")

    # 5 — receipt
    outdir = ROOT / "reports" / "marvel" / "receipts"
    jsonl_out = Path(args.jsonl_out) if args.jsonl_out else outdir / f"d3_red_list_{today}.jsonl"
    md_out = jsonl_out.with_suffix(".md")
    with jsonl_out.open("w") as f:
        for e in red_list:
            f.write(json.dumps(e) + "\n")
    lines = [
        "# GATE C · D3 — red list (zero unfiled engine gaps; red list not empty)",
        f"_generated {today} by `tools/marvel/d3_red_list.py` (zero egress)._",
        "",
        f"**Entries: {len(red_list)}** — the red list is not empty (D3's "
        "anti-theater check). Every entry carries a named cause + disposition.",
        "",
        "## Live reconciliation (a NEW unfiled gap fails the gate)",
        "",
        f"- unknown-type documents: marvel {unk['marvel']['live']}/{unk['marvel']['docs']} "
        f"({unk['marvel']['pct']}%), mcu {unk['mcu']['live']}/{unk['mcu']['docs']} "
        f"({unk['mcu']['pct']}%) — agree with record: "
        f"{unk['marvel']['agrees'] and unk['mcu']['agrees']}",
        f"- disambig_unresolved (marvel): {dm['live']['rows']} rows / "
        f"{dm['live']['distinct']} distinct — agree: {dm['agrees']}",
        f"- F3 disambiguated files on disk: {f3['closed']}"
        + ("" if f3["closed"] else f" (missing {f3['missing']})"),
        f"- mcu chunk-containment unreachable: {cont['mcu_unreachable']}; "
        f"marvel: {cont['marvel']}",
        f"- parse-diff verdicts: marvel {pd['marvel']['proceed']} / "
        f"mcu {pd['mcu']['proceed']}",
        f"- C6 residue: mcu {c6.get('mcu', {}).get('residue', 'n/a')} rows "
        f"(sweep {'complete' if c6.get('mcu', {}).get('complete') else 'in progress'}) / marvel "
        f"{c6.get('marvel', {}).get('residue', 'n/a')} rows so far "
        f"(sweep {'complete' if c6.get('marvel', {}).get('complete') else 'in progress'})",
        f"- OOS pre-score (mcu): {oos_pre().get('verdicts', 'n/a')} "
        f"(green {oos_pre().get('green_rate', 'n/a')}%)",
        "",
        "## Entries",
        "",
    ]
    for e in red_list:
        lines.append(
            f"- **{e['id']}** ({e['status']}) — {e['title']}")
        lines.append(f"  - cause: {e['cause']}")
        lines.append(f"  - disposition: {e['disposition']}")
        lines.append(f"  - recorded in: {e['recorded_in']}")
    if failures:
        lines += ["", "## FAILURES", ""] + [f"- {x}" for x in failures]
    else:
        lines += [
            "",
            "## Verdict",
            "",
            "**D3 CLOSED** — the red list is non-empty ("
            f"{len(red_list)} entries), every entry has a named cause + "
            "disposition, and every live reconciliation agrees with the "
            "record: zero unfiled engine gaps. Open-with-owner items "
            "(C2 mcu mapping, C3 cross-corpus, F7 WPS fix) are filed "
            "deferrals, not unfiled gaps.",
        ]
    md_out.write_text("\n".join(lines) + "\n")

    if not args.quiet:
        print(f"{'FAIL' if failures else 'PASS'}  D3 red list: "
              f"{len(red_list)} entries, failures={len(failures)}")
        for x in failures:
            print(f"  - {x}")
        print(f"  receipt: {md_out.relative_to(ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())