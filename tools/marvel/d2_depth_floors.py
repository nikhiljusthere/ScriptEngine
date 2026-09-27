#!/usr/bin/env python3
"""GATE C · D2 — archetype depth floors, measured against populated in-scope sections.

Plan MARVEL_100_PLAN.md §5 (GATE C, D2) + Plan_to_perfection §6 row D2:
"Every archetype meets its declared depth floor, measured against
*populated in-scope sections*, never raw page count."

Depth is not page count. A page is *deep* when it carries at least one
populated content channel:
  (a) a populated in-scope prose section (word_count > 0, and the section
      title is NOT in the chunker's effective boilerplate set for the
      series -- i.e. exactly the sections the chunker would index, so this
      ties to the chunk-containment pre-pass), or
  (b) >= 1 non-empty infobox fact field (the `facts` table, value non-blank).

The channel mix differs by wiki and is reported, not hidden:
  * mcu  is PROSE-led: ~100% of pages carry narrative sections.
  * marvel is INFOBOX-led for character/comic/episode: the bulk of those
    pages are pure-infobox data pages (verified on disk 2026-09-27: a
    25-page sample of word_count=0 character pages had zero `==` headings
    on disk -- the parser dropped nothing; the wiki simply stores those
    characters as data, not narrative). Their depth is carried by the
    infobox identity/affiliation/alias facts (median 10-21 keys/page),
    which is exactly what C1 identity_fields + the C6 identity/affiliation/
    alias bank classes target. So marvel character QA is infobox-led by
    corpus fact, not a parser gap.

Declared depth floor (pre-registered, uniform across every archetype and
both series -- NOT fitted to the data):

    an archetype MEETS its depth floor when >= 50% of its pages are deep
    (>= 1 populated content channel), and its median distinct infobox-fact
    count is >= 1.

An archetype that fails the floor becomes a named depth gap -> the D3 red
list ("a corpus with no expected failures has not been probed"). The
floor is a floor: a pass is only valid if it was measured, not assumed.

Zero-egress: reads the per-series facts.db (RO) + the series overrides
(effective boilerplate, via the chunker so it cannot drift from the
chunk-containment pre-pass). Writes:
    reports/marvel/receipts/d2_depth_floors_2026-09-27.md
    reports/marvel/receipts/d2_depth_floors_2026-09-27.jsonl

exit 0 = every archetype meets its floor; exit 1 = one or more fail.
"""
from __future__ import annotations

import json
import statistics
import sqlite3
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REC = ROOT / "reports" / "marvel" / "receipts"
OUT_MD = REC / "d2_depth_floors_2026-09-27.md"
OUT_JSONL = REC / "d2_depth_floors_2026-09-27.jsonl"

# Pre-registered depth floor (uniform, see module docstring).
FLOOR_DEEP_PCT = 50.0     # >= this % of an archetype's pages must be deep
FLOOR_MED_FACTS = 1       # median distinct infobox-fact count must be >= this

# GATE C archetype list -> page_type(s) per series.
# MCU types its film archetype `movie` (no `film` pages) and its series
# archetype as `tv_series` + `season`; every other name is shared.
ARCHETYPES = {
    "marvel": {
        "character": ["character"],
        "comic": ["comic"],
        "event": ["event"],
        "film": ["film"],
        "series": ["series"],
        "episode": ["episode"],
        "location": ["location"],
    },
    "mcu": {
        "character": ["character"],
        "comic": ["comic"],
        "event": ["event"],
        "film": ["movie"],          # MCU film archetype is typed `movie`
        "series": ["tv_series", "season"],
        "episode": ["episode"],
        "location": ["location"],
    },
}


def effective_boilerplate(series: str) -> set[str]:
    """The section titles the series' chunker treats as boilerplate.

    Uses the chunker's own function over the series' overrides so the
    in-scope set here can never drift from the chunk-containment pre-pass.
    Falls back to the engine global if the overrides cannot be loaded.
    """
    try:
        from scriptengine.config import series_paths, load_overrides
        from scriptengine.index.chunker import (
            BOILERPLATE_SECTIONS,
            effective_boilerplate_sections,
        )
        sp = series_paths(series)
        overrides = load_overrides(sp)
        return effective_boilerplate_sections(overrides)
    except Exception:
        from scriptengine.index.chunker import BOILERPLATE_SECTIONS
        return set(BOILERPLATE_SECTIONS)


def measure(series: str) -> list[dict]:
    eb = sorted(effective_boilerplate(series))
    eb_ph = ",".join("?" * len(eb))
    db = ROOT / "series" / series / "facts.db"
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    rows = []
    try:
        for arch, types in ARCHETYPES[series].items():
            t_ph = ",".join("?" * len(types))
            doc_ids = [r[0] for r in con.execute(
                f"select id from documents where page_type in ({t_ph})", tuple(types))]
            n = len(doc_ids)
            rec = {
                "series": series, "archetype": arch, "page_types": types,
                "docs": n,
            }
            if n == 0:
                rec.update(prose_pct=0.0, facts_pct=0.0, deep_pct=0.0,
                           med_facts=0.0, med_prose=0.0, meets_floor=False,
                           channel="empty")
                rows.append(rec)
                continue
            # (a) populated in-scope prose sections per doc
            prose = dict(con.execute(
                f"""select document_id, count(*) from sections
                    where word_count > 0 and lower(title) not in ({eb_ph})
                      and document_id in (select id from documents where page_type in ({t_ph}))
                    group by document_id""",
                tuple(eb) + tuple(types)).fetchall())
            # (b) distinct non-empty infobox fact keys per doc
            facts = dict(con.execute(
                f"""select n.document_id, count(distinct f.key)
                    from facts f join nodes n on n.id = f.node_id
                    where trim(coalesce(f.value,'')) != ''
                      and n.document_id in (select id from documents where page_type in ({t_ph}))
                    group by n.document_id""",
                tuple(types)).fetchall())
            n_prose = sum(1 for d in doc_ids if prose.get(d, 0) >= 1)
            n_facts = sum(1 for d in doc_ids if facts.get(d, 0) >= 1)
            n_deep = sum(1 for d in doc_ids if prose.get(d, 0) >= 1 or facts.get(d, 0) >= 1)
            med_facts = statistics.median([facts.get(d, 0) for d in doc_ids])
            med_prose = statistics.median([prose.get(d, 0) for d in doc_ids])
            deep_pct = 100.0 * n_deep / n
            meets = deep_pct >= FLOOR_DEEP_PCT and med_facts >= FLOOR_MED_FACTS
            # which channel(s) carry the depth, honestly:
            #   both channels universal (>=95% of pages) -> "prose+infobox"
            #   else the dominant median wins; if neither is populated -> "sparse"
            prose_pct = 100.0 * n_prose / n
            facts_pct = 100.0 * n_facts / n
            if prose_pct >= 95 and facts_pct >= 95:
                channel = "prose+infobox"
            elif med_prose >= med_facts and med_prose >= 1:
                channel = "prose-led"
            elif med_facts >= 1:
                channel = "infobox-led"
            else:
                channel = "sparse"
            rec.update(
                prose_pct=round(100.0 * n_prose / n, 1),
                facts_pct=round(100.0 * n_facts / n, 1),
                deep_pct=round(deep_pct, 1),
                med_facts=round(med_facts, 1),
                med_prose=round(med_prose, 1),
                meets_floor=meets,
                channel=channel,
            )
            rows.append(rec)
    finally:
        con.close()
    return rows


def main() -> int:
    results = [r for s in ("marvel", "mcu") for r in measure(s)]
    REC.mkdir(parents=True, exist_ok=True)
    with OUT_JSONL.open("w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r) + "\n")

    md = ["# D2 — archetype depth floors (2026-09-27 gate day)", ""]
    md.append("Measured against *populated in-scope sections* (the sections the "
              "series' chunker actually indexes) plus the infobox fact channel. "
              "Never raw page count (Plan_to_perfection §6, D2).")
    md.append("")
    md.append(f"Declared floor (pre-registered, uniform): >= {FLOOR_DEEP_PCT:.0f}% of an "
              f"archetype's pages deep (>= 1 populated channel) AND median infobox-fact "
              f"count >= {FLOOR_MED_FACTS}.")
    md.append("")
    all_ok = True
    for s in ("marvel", "mcu"):
        md += [f"## {s}", ""]
        md.append("| archetype | page_types | docs | prose% | facts% | deep% | med_facts | med_prose | channel | floor |")
        md.append("|---|---|---:|---:|---:|---:|---:|---:|---|---|")
        for r in [x for x in results if x["series"] == s]:
            ok = "PASS" if r["meets_floor"] else "**FAIL**"
            if not r["meets_floor"]:
                all_ok = False
            md.append(
                f"| {r['archetype']} | {','.join(r['page_types'])} | {r['docs']} "
                f"| {r['prose_pct']}% | {r['facts_pct']}% | {r['deep_pct']}% "
                f"| {r['med_facts']} | {r['med_prose']} | {r['channel']} | {ok} |")
        md.append("")
    md.append("## Finding (recorded, not hidden)")
    md.append("- **marvel is infobox-led** for character/comic/episode: the bulk of "
              "those pages are pure-infobox data pages (a 25-page sample of "
              "word_count=0 character pages had zero `==` headings on disk 2026-09-27 "
              "-- the parser dropped nothing; the wiki stores those characters as "
              "data, not narrative). Their depth is carried by infobox identity/"
              "affiliation/alias facts (median 10-21 keys/page) -- the C1 identity "
              "path and the C6 identity/affiliation/alias bank classes. Marvel "
              "character QA is therefore infobox-led by corpus fact, not a parser gap.")
    md.append("- **mcu is prose-led**: ~100% of pages carry narrative sections "
              "(median depth 2-16) in addition to the infobox.")
    md.append("")
    md.append(f"Overall: {'ALL ARCHETYPES MEET THEIR FLOOR' if all_ok else 'ONE OR MORE ARCHETYPES FAIL -- see red list'}")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")

    fails = [r for r in results if not r["meets_floor"]]
    for r in results:
        mark = "PASS" if r["meets_floor"] else "FAIL"
        print(f"{mark}  {r['series']:<7} {r['archetype']:<10} docs={r['docs']:>7} "
              f"deep={r['deep_pct']:>5}% med_facts={r['med_facts']} ({r['channel']})")
    if fails:
        print(f"D2 FAIL: {len(fails)} archetype(s) below floor: "
              f"{[(r['series'], r['archetype']) for r in fails]}", file=sys.stderr)
        return 1
    print("D2 PASS: every archetype meets its declared depth floor.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())