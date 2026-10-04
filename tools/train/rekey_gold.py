#!/usr/bin/env python3
"""Re-key the adjudicated gold onto the new sentence grid (windowing-100,
2026-09-30).

Each gold600.jsonl record (old window id, page, section, passage in the
user message) is mapped onto the grid by the council's mechanical rule:
the record's passage located on its section's (or lead's) sentence grid,
and the re-keyable invariant is the window whose span covers that
location -- stable across re-ingests by the window's sentence hashes,
never by the id.

Per the council's ruling on the 333:

* a positive record whose passage sits in ONE new window and whose rows'
  quotes all sit in one window each KEEPS its adjudicated status;
* rows whose quotes the grid does not carry in one window DROP for
  re-extraction (the record's assistant answer is rewritten to the kept
  rows, so the file stays consumable by build_trainset.py);
* a record whose passage straddles a new boundary drops whole;
* every EMPTY adjudication is flagged `reread` -- those empties were
  judged on contaminated multi-topic windows, and the re-read itself is
  the 35B data phase, not coding.

Unmapped records (the section's text changed under a re-crawl) drop for
re-extraction too: a gold row whose source no longer says what it said is
not gold.

    python tools/train/rekey_gold.py --series jjk
            --gold series/jjk/training/gold600/gold600.jsonl
            --out  series/jjk/training/gold600/gold600.gen2.jsonl
            [--report series/jjk/training/gold600/gold600.gen2.report.json]
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scriptengine.ingest.windows import (  # noqa: E402
    CURRENT_GEN,
    build_windows,
    quote_grid_span,
    quote_window,
)
from scriptengine.ingest.wikitext import strip_markup  # noqa: E402
from scriptengine.stores.facts import FactStore  # noqa: E402


def passage_of(record):
    """The record's read passage: everything after `Passage:\n` in the
    user message (the campaign's own message shape)."""
    user = record["messages"][1]["content"]
    at = user.find("Passage:\n")
    return user[at + len("Passage:\n"):].strip() if at >= 0 else ""


def rows_of(record):
    """The record's adjudicated rows; [] for an empty adjudication."""
    try:
        return json.loads(record["messages"][2]["content"]).get("events") or []
    except (json.JSONDecodeError, ValueError, AttributeError):
        return None  # unparseable: refuse, never guess


def grid_texts_for(store, record):
    """The grid texts the record's passage may have been cut from: the
    page's lead when the record carries no section, or every same-titled
    section's text in ordinal order when it does (the wiki has pages with
    sections sharing a title, and the record was read from one of them).
    Cleaned exactly the way emit_windows.universe builds its grid -- lead
    through strip_markup, sections raw (the extractor reads section text
    as stored; only the lead is markup-cleaned), so a re-keyed window id
    is the builder's id for the universe's text, never for a different
    cleaning. [] = the source no longer exists (re-crawl), the record is
    unmapped."""
    page = (record.get("page") or "").strip()
    section = (record.get("section") or "").strip()
    if not section:
        row = store.connection.execute(
            "SELECT lead FROM documents WHERE title = ? COLLATE NOCASE", (page,)
        ).fetchone()
        lead = strip_markup((row["lead"] or "") if row else "").strip()
        return [lead] if lead else []
    rows = store.connection.execute(
        "SELECT s.text FROM sections s JOIN documents d ON s.document_id = d.id"
        " WHERE d.title = ? COLLATE NOCASE AND s.title = ? COLLATE NOCASE"
        " ORDER BY s.ordinal",
        (page, section),
    ).fetchall()
    return [t for t in ((r["text"] or "").strip() for r in rows) if t]


def rekey_record(record, store, grids):
    """One record -> (out_records, status, rows_kept, rows_dropped).

    The council's mechanical rule (spec b): the record maps onto the grid
    by its sentence hashes; a ROW keeps its adjudicated status while its
    quote sits in one new window, and rows are regrouped under the
    window(s) that carry them. Statuses:

    * kept        -- one covering window, every row in it, the record is
                     re-expressed on that window (or already was);
    * reexpressed -- the rows scattered over several windows (or some were
                     dropped): one output record per covering window;
    * reread      -- an empty adjudication in one covering window, flagged
                     for the 35B re-read;
    * straddle    -- an empty adjudication whose passage straddles: its
                     re-read is the new windows themselves, emitted by
                     emit_windows.py; nothing to keep here;
    * unmapped    -- the source text no longer says what it said (a
                     re-crawl); the record is not gold."""
    page = (record.get("page") or "").strip()
    label = (record.get("section") or "").strip() or "lead"
    key = (page, label)
    texts = grid_texts_for(store, record)
    passage = passage_of(record)
    rows = rows_of(record)
    if not texts or not passage or rows is None:
        return [], "unmapped", 0, 0

    # Which same-titled section the record was read from: the one(s) whose
    # text still carries the passage (the verbatim predicate's own folding).
    # Usually one; [] = the source no longer says what it said (re-crawl),
    # the record is unmapped.
    hits = []
    for text in texts:
        wkey = (key[0], key[1], text)
        if wkey not in grids:
            grids[wkey] = build_windows(page, label, text, gen=CURRENT_GEN)
        if not grids[wkey]:
            continue
        if quote_grid_span(text, passage) is not None:
            hits.append((text, grids[wkey]))
    if not hits:
        return [], "unmapped", 0, 0
    # Same passage in two same-titled sections: the record's rows locate
    # where the record actually lived -- take the hit that keeps the most.
    def kept_count(hit):
        text, windows = hit
        return sum(
            1 for row in rows
            if quote_window(page, label, text, str(row.get("quote") or "").strip(),
                           windows=windows) is not None
        )
    text, windows = max(hits, key=kept_count) if len(hits) > 1 else hits[0]
    user_prefix = record["messages"][1]["content"].split("Passage:\n", 1)[0] + "Passage:\n"

    # Where the record's own passage sits: the new windows whose spans
    # cover it. Usually one, or NONE when a 4,000-char slice straddles
    # sub-topic cuts -- the rows still locate per window and the record
    # re-expresses, it is not unmapped.
    span = quote_grid_span(text, passage)
    covering = [
        w for w in windows
        if span is not None and w.s_start <= span[0] and span[1] <= w.s_end
    ]

    def reexpress(window, kept_rows, status):
        out = dict(record)
        out["id"] = window.id
        out["gen"] = CURRENT_GEN
        out["section"] = "" if window.section == "lead" else window.section
        out["rekey"] = {
            "old_id": record.get("id"), "new_id": window.id,
            "status": status, "rows_kept": len(kept_rows),
            "rows_dropped": len(rows) - len(kept_rows),
        }
        out["messages"] = [
            out["messages"][0],
            {"role": "user", "content": user_prefix + window.text},
            {"role": "assistant",
             "content": json.dumps({"events": kept_rows}, ensure_ascii=False)},
        ]
        return out

    if not rows:
        if len(covering) == 1:
            return [reexpress(covering[0], [], "reread")], "reread", 0, 0
        return [], "straddle", 0, 0  # the re-read is the covering windows

    kept, dropped = [], 0
    by_window = {}
    for row in rows:
        quote = str(row.get("quote") or "").strip()
        window = quote_window(page, label, text, quote, windows=windows)
        if window is None:
            dropped += 1
            continue
        kept.append(row)
        by_window.setdefault(window.id, (window, []))[1].append(row)

    if not by_window:
        return [], "rows_dropped", 0, len(rows)
    # One covering window, every row kept in it: a clean keep. Anything
    # else (rows scattered over windows, or some dropped) is re-expressed
    # per window -- one training record per window, the shape the new
    # reads have.
    status = "kept" if (
        len(by_window) == 1 and dropped == 0 and len(covering) == 1
    ) else "reexpressed"
    out = [
        reexpress(window, kept_rows, status)
        for window, kept_rows in by_window.values()
    ]
    return out, status, len(kept), dropped


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--series", default="jjk")
    ap.add_argument("--gold",
                    default="series/jjk/training/gold600/gold600.jsonl")
    ap.add_argument("--out",
                    default="series/jjk/training/gold600/gold600.gen2.jsonl")
    ap.add_argument("--report", default=None,
                    help="write the per-record receipt here")
    a = ap.parse_args()

    db = ROOT / "series" / a.series / "facts.db"
    if not db.exists():
        sys.exit(f"{a.series} is not indexed (no {db}); run `index` first")
    gold = [json.loads(line) for line in open(a.gold) if line.strip()]

    tally = Counter()
    rows_kept = rows_dropped = 0
    out_records = []
    report_lines = []
    with FactStore(db) as store:
        grids = {}
        for record in gold:
            outs, status, k, d = rekey_record(record, store, grids)
            tally[status] += 1
            rows_kept += k
            rows_dropped += d
            out_records.extend(outs)
            report_lines.append({
                "old_id": record.get("id"), "page": record.get("page"),
                "section": record.get("section"), "status": status,
                "new_ids": [o["rekey"]["new_id"] for o in outs],
                "rows_kept": k, "rows_dropped": d,
            })

    Path(a.out).write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out_records),
        encoding="utf-8",
    )
    receipt = {
        "gold": a.gold, "out": a.out, "gen": CURRENT_GEN,
        "records": len(gold), **dict(tally),
        "rows_kept": rows_kept, "rows_dropped": rows_dropped,
        "note": "reread records are the 35B data phase (re-read on the new "
                "grid); straddle/unmapped/rows_dropped drop for re-extraction",
    }
    if a.report:
        Path(a.report).write_text(
            json.dumps({"receipt": receipt, "records": report_lines},
                       indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())