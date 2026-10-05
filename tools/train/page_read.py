#!/usr/bin/env python3
"""Read a wiki page from a series' local crawl, for the manual inline
verifier (plan/UNIVERSAL_DATASET_PLAN.md, "Labeler + verification protocol":
"open the exact wiki page(s) for every character / arc / event / ability
involved (local crawl, read in <=500-char chunks)"). Read-only, zero LLM.

    # the page's type, lead and section list (an alias resolves to its page)
    scriptengine/.venv/bin/python tools/train/page_read.py --series opm "Saitama"
    # one section in 500-char chunks (by number from the list, or by title)
    scriptengine/.venv/bin/python tools/train/page_read.py --series opm "Saitama" --section 3
    scriptengine/.venv/bin/python tools/train/page_read.py --series opm "Saitama" --section History --offset 500
"""
import argparse
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
CHUNK = 500


def find_doc(con, series, title):
    row = con.execute("select id, title, page_type, lead from documents where title = ?", (title,)).fetchone()
    if row:
        return row
    row = con.execute("select id, title, page_type, lead from documents where lower(title) = lower(?)",
                      (title,)).fetchone()
    if row:
        return row
    from verify_row_wiki import Wiki  # the same alias resolver the drafter's checks use
    for page in Wiki(str(ROOT / "series" / series / "facts.db")).resolve(title)[:1]:
        return con.execute("select id, title, page_type, lead from documents where title = ?", (page,)).fetchone()
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", required=True)
    ap.add_argument("title")
    ap.add_argument("--section", default=None, help="section number (from the list) or title")
    ap.add_argument("--offset", type=int, default=0)
    a = ap.parse_args()
    con = sqlite3.connect(f"file:{ROOT / 'series' / a.series / 'facts.db'}?mode=ro", uri=True)
    doc = find_doc(con, a.series, a.title)
    if not doc:
        hits = con.execute("select title from documents where title like ? limit 10", (f"%{a.title}%",)).fetchall()
        print(f"no page {a.title!r} in {a.series}." + (" Similar: " + "; ".join(h[0] for h in hits) if hits else ""))
        return 1
    doc_id, title, ptype, lead = doc
    secs = con.execute("select ordinal, title, breadcrumb, word_count, text from sections "
                       "where document_id = ? order by ordinal", (doc_id,)).fetchall()
    if a.section is None:
        print(f"PAGE: {title}  (type: {ptype or '?'})")
        lead = (lead or "").strip()
        print(f"LEAD: {lead[:CHUNK]}" + (" ..." if len(lead) > CHUNK else ""))
        print("SECTIONS (number | breadcrumb | words):")
        for i, (_o, _t, crumb, wc, _x) in enumerate(secs, 1):
            print(f"  {i} | {crumb} | {wc}")
        return 0
    pick = None
    if a.section.isdigit() and 1 <= int(a.section) <= len(secs):
        pick = secs[int(a.section) - 1]
    else:
        pick = next((s for s in secs if s[1].lower() == a.section.lower()), None) or \
            next((s for s in secs if a.section.lower() in s[2].lower()), None)
    if not pick:
        print(f"no section {a.section!r} on {title}; run without --section for the list")
        return 1
    text = (pick[4] or "").strip()
    part = text[a.offset:a.offset + CHUNK]
    print(f"PAGE: {title} | SECTION: {pick[2]} | chars {a.offset}-{a.offset + len(part)} of {len(text)}")
    print(part)
    if a.offset + CHUNK < len(text):
        print(f"[more: --offset {a.offset + CHUNK}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
