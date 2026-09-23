#!/usr/bin/env python3
"""P2-extract section pre-filter: does a wiki section describe an event, ability
or state change (i.e. should the 27B extraction pass look at it)?

Judged by the local fast lane (decider-0.8b via the Jev gateway, :8018) — one
plain question per section. Measured pattern on this model: clearly-yes
content scores >= 0.5, noise <= 0.15, so the default keep threshold is 0.3.

Usage:
    python tools/jev/section_prefilter.py --series jjk --limit 200   # probe
    python tools/jev/section_prefilter.py --series jjk --workers 4   # full
    python tools/jev/section_prefilter.py --series csm --workers 4   # campaign

Output: <out>.jsonl (one line per section) + a summary line on stdout with
sensitivity against sections that produced kept events (when the series db has
an `events` table) and the keep rate (selectivity).

Nothing is written to the corpus or bank. The output is a sorting aid: the
27B extraction pass runs only on sections the filter keeps; a wrongly dropped
event section is lost content, so the sensitivity number is the pass bar.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path.home() / "ScriptEngine"
sys.path.insert(0, str(ROOT))

JEV_URL = os.environ.get("SCRIPTENGINE_JEV_URL", "http://127.0.0.1:8018/v1/systemone")
QUESTION = (
    "Does this wiki section contain a concrete event that happened, a named "
    "ability or power, or a change in a character's state or status? "
    "Answer no for general background, lists, quotes, or trivia without "
    "events, abilities, or state changes."
)
TEXT_CHARS = 4_000  # decider state cap is 8,192 tokens; 4k chars is well inside


def db_path(series: str) -> Path:
    candidates = []
    repo = Path.home() / "ScriptEngine"
    if repo.exists():
        candidates.append(repo)
    candidates.append(Path.cwd())
    for root in candidates:
        p = root / "series" / series / "facts.db"
        if p.exists():
            return p
    return candidates[0] / "series" / series / "facts.db"


def load_sections(db: Path):
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        sections = con.execute(
            "SELECT s.id, d.title AS doc, s.title, s.text, s.word_count "
            "FROM sections s JOIN documents d ON d.id = s.document_id"
        ).fetchall()
        event_secs = set()
        try:
            event_secs = {r[0] for r in con.execute("SELECT DISTINCT section_id FROM events")}
        except sqlite3.OperationalError:
            pass  # series without an events table (no ground truth yet)
    finally:
        con.close()
    return sections, event_secs


def ask(state: dict) -> float:
    body = json.dumps({"model": "jev-latest", "state": state,
                      "questions": {"q": {"type": "noul", "instructions": QUESTION}}}).encode()
    req = urllib.request.Request(JEV_URL, data=body, headers={
        "Content-Type": "application/json", "Authorization": "Bearer local"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read())
    p = data["answers"]["q"]["noul"]
    return p if isinstance(p, float) else 1.0  # fail-open: keep on any error shape


def judge(row: tuple) -> float:
    sid, doc, title, text, wc = row
    try:
        return ask({"title": title, "text": (text or "")[:TEXT_CHARS]})
    except Exception:
        return 1.0  # fail-open: any error keeps the section


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--series", default="jjk")
    ap.add_argument("--limit", type=int, default=0, help="judge only the first N sections (probe)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=None, help="results jsonl (default <series>_prefilter_<ts>.jsonl in cwd)")
    args = ap.parse_args(argv)

    db = db_path(args.series)
    if not db.exists():
        print(f"no facts db at {db}", file=sys.stderr)
        return 1
    sections, event_secs = load_sections(db)
    if args.limit:
        sections = sections[:args.limit]
    out = Path(args.out) if args.out else Path(f"{args.series}_prefilter_{time.strftime('%Y%m%d-%H%M%S')}.jsonl")

    todo = [(sid, doc, title, text, wc) for sid, doc, title, text, wc in sections]
    results: list[dict] = []
    t0 = time.time()
    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for row, p in zip(todo, pool.map(judge, todo)):
            results.append({"id": f"{args.series}-sec-{row[0]}", "section_id": row[0], "doc": row[1], "title": row[2],
                            "p": round(p, 4), "keep": p >= 0.3, "has_events": row[0] in event_secs,
                            "word_count": row[4]})
            done += 1
            if done % 250 == 0:
                rate = done / (time.time() - t0)
                eta = (len(todo) - done) / rate / 60 if rate else 0
                print(f"  {done}/{len(todo)} ({rate:.1f}/s, eta {eta:.1f} min)", file=sys.stderr, flush=True)

    with out.open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    kept = [r for r in results if r["keep"]]
    pos = [r for r in results if r["has_events"]]
    hit = [r for r in kept if r["has_events"]]
    miss = [r for r in pos if not r["keep"]]
    print(f"\n{len(results)} sections judged in {(time.time() - t0) / 60:.1f} min -> {out}")
    print(f"keep rate (selectivity): {len(kept)}/{len(results)} = {len(kept) / max(1, len(results)):.1%}")
    if pos:
        print(f"sensitivity vs event sections: {len(hit)}/{len(pos)} = {len(hit) / len(pos):.1%}")
        if miss:
            print(f"MISSED event sections ({len(miss)}): " + ", ".join(r["id"] for r in miss[:20]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())