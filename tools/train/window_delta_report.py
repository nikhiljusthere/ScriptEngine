"""Window-count delta report (2026-09-30, windowing-100 council process gate).

The builder is pure, so the whole store runs through it at zero LLM cost
before the 300k-page scale-out is priced on the new grid: this reports how
many whole-sentence windows the new grid costs against the old
character-sliced 4000/300 windows, section by section. Nobody prices the
cost delta; this is how that blind spot gets killed without spending a
single token.

    python tools/train/window_delta_report.py --db series/jjk/facts.db [--json out.json] [--limit N]

Zero LLM, zero writes to the store. The report's ``over_cap_windows`` and
``oversized_windows`` must agree: the only way a grid window exceeds the
2,000-char cap is a single oversized sentence, and that window is counted,
not hidden (the window is a view, and a view cannot hide a character).
"""
import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scriptengine.ingest.abilities import _windows  # noqa: E402
from scriptengine.ingest.windows import (  # noqa: E402
    DEFAULT_CAP_CHARS,
    DEFAULT_CARRY_CHARS,
    build_windows,
    section_subtopics,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True, help="the store's facts.db")
    ap.add_argument("--json", dest="out", help="also write the report as JSON here")
    ap.add_argument(
        "--limit",
        type=int,
        default=0,
        help="count only the first N sections (0 = all)",
    )
    a = ap.parse_args()

    con = sqlite3.connect(str(a.db))
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT d.title AS page, s.title AS section, s.text"
        " FROM sections s JOIN documents d ON d.id = s.document_id"
        " WHERE COALESCE(LENGTH(s.text), 0) > 0"
        " ORDER BY d.title COLLATE NOCASE, s.ordinal, s.id"
    ).fetchall()
    if a.limit:
        rows = rows[: a.limit]

    total_old = 0
    total_new = 0
    total_sub = 0
    over_cap = 0
    oversized = 0
    per_section = []
    for row in rows:
        text = row["text"]
        old = _windows(text)
        windows = build_windows(row["page"], row["section"], text)
        subs = len(section_subtopics(text))
        wide = [w for w in windows if w.chars > DEFAULT_CAP_CHARS]
        single = [w for w in wide if w.s_start == w.s_end]
        total_old += len(old)
        total_new += len(windows)
        total_sub += subs
        over_cap += len(wide)
        oversized += len(single)
        per_section.append(
            {
                "page": row["page"],
                "section": row["section"],
                "chars": len(text),
                "subtopics": subs,
                "old_windows": len(old),
                "new_windows": len(windows),
                "over_cap": len(wide),
            }
        )

    report = {
        "db": str(a.db),
        "cap_chars": DEFAULT_CAP_CHARS,
        "carry_chars": DEFAULT_CARRY_CHARS,
        "sections_with_text": len(rows),
        "subtopics": total_sub,
        "old_windows": total_old,
        "new_windows": total_new,
        "delta": total_new - total_old,
        "over_cap_windows": over_cap,
        "oversized_windows": oversized,
        "sections": per_section,
    }

    print(
        f"{report['sections_with_text']} sections, "
        f"{total_old} old (4000/300 char-sliced) windows -> "
        f"{total_new} new (grid) windows "
        f"({report['delta']:+d}); {total_sub} sub-topics; "
        f"{over_cap} over-cap windows, {oversized} of them a single "
        f"oversized sentence."
    )
    if a.out:
        out = Path(a.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"report: {out}")


if __name__ == "__main__":
    main()