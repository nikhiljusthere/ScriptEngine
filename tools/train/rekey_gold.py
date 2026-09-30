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


def grid_text_for(store, record):
    """The grid the record's passage was cut from: its section's text, or
    the page's lead when the record carries no section. None = the
    source no longer exists (re-crawl), the record is unmapped."""
    page = (record.get("page") or "").strip()
    section = (record.get("section") or "").strip()
    if not section:
        row = store.connection.execute(
            "SELECT lead FROM documents WHERE title = ? COLLATE NOCASE", (page,)
        ).fetchone()
        lead = (row["lead"] or "").strip() if row else ""
        return lead or None
    row = store.connection.execute(
        "SELECT s.text FROM sections s JOIN documents d ON s.document_id = d.id"
        " WHERE d.title = ? COLLATE NOCASE AND s.title = ? COLLATE NOCASE"
        " ORDER BY s.ordinal",
        (page, section),
    ).fetchone()
    text = (row["text"] or "").strip() if row else ""
    return text or None


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
    text = grid_text_for(store, record)
    passage = passage_of(record)
    if text is None or not passage or rows_of(record) is None:
        return [], "unmapped", 0, 0
    if key not in grids:
        grids[key] = build_windows(page, label, text, gen=CURRENT_GEN)
    windows = grids[key]
    if not windows:
        return [], "unmapped", 0, 0

    rows = rows_of(record)
    user_prefix = record["messages"][1]["content"].split("Passage:\n", 1)[0] + "Passage:\n"

    # Where the record's own passage sits: the new windows whose spans
    # cover it (usually one, or several when a 4,000-char slice spans
    # cuts).
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