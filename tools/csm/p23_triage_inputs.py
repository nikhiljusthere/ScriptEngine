"""Triage inputs for the P2.1 sweep residuals (council #31 pre-registered scope).

Model-free. Reads the five P2.1 ledgers + `series/csm/facts.db` and writes,
under `reports/csm/p21_sweep_2026-09-17/triage/`:

- qa_p1.jsonl / qa_p2.jsonl   the 261 qa misses (identical to
                              `../misses_qa.jsonl`, asserted) joined with the
                              auto door's per-line verdict: p1 = first half of
                              the both-miss rows, p2 = the rest + the auto-only
                              rows (qa miss, auto HIT — the product path works).
- floor_sample.jsonl          narrative + roster residuals: the FULL per-cell
                              histogram plus a first-`CAP`-per-cell sample
                              (panel order), each sampled row carrying a
                              deterministic class + reason (the floor's
                              class/reason is structural, not judged).
- meta.json                   counts, shas, ledger commit stamps.

The qa judgment (defect vs by-design residual, root cause) is NOT done here —
that is the row-by-row triage the subagents perform on qa_p1/p2. The floor
class+reason IS deterministic (verdict + page_type + returned_docs), which is
why it is emitted here instead of being judged.

Usage:
    python tools/csm/p23_triage_inputs.py
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/csm"))

from p21_sweep_report import DOORS, HELDOUT_H8, LEDGERS, PANEL_H8, key, load  # noqa: E402

OUT = ROOT / "reports/csm/p21_sweep_2026-09-17/triage"
DB = ROOT / "series/csm/facts.db"
MISS = ("MISS_DOC", "MISS_SPAN", "ERROR")
CAP = 5  # sampled rows per (door, page_type, verdict) cell
FLOOR_DOORS = ("narrative", "roster")
FLAT: dict[str, str] = {}  # filled in main() before pre_triage runs (corpus-dup branch)


def pre_triage(r: dict) -> str:
    # verbatim copy of p21_sweep_report.py pre_triage (nested there, not
    # importable) — asserted identical below via the 261-row check
    s = r["sentence"]
    if s.lstrip().startswith("|") or " | " in s:
        return "table-row"
    base = r["title"].split("/")[0]
    if r["verdict"] == "MISS_DOC" and any(
            d and d != r["title"] and d.split("/")[0] == base for d in r.get("returned_docs", [])):
        return "near-page"
    from scriptengine.eval.span_recall import decite, norm  # deferred: only the corpus-dup branch needs it
    needle = decite(norm(s))
    if any(needle in txt for t, txt in FLAT.items() if t != r["title"]):
        return "corpus-duplicate"
    if len(s.split()) < 10:
        return "short"
    return "rank-miss" if r["verdict"] == "MISS_DOC" else "span-miss" if r["verdict"] == "MISS_SPAN" else "error"


def floor_class(r: dict, page_type: str | None) -> tuple[str, str]:
    v = r["verdict"]
    if v == "TRUNCATED":
        return ("truncation-budget", "top-k beats cap (budget design, A17: not a miss)")
    if v == "MISS_SPAN":
        return ("span-floor", "page served, line outside the served beats; floor door, documented not a regression target")
    base = r["title"].split("/")[0]
    near = any(d and d != r["title"] and d.split("/")[0] == base for d in r.get("returned_docs", []))
    if near:
        return ("near-page-floor", "right subject, wrong page (sibling served); floor door serving weakness")
    if (page_type or "").endswith(("box",)) or (page_type or "").startswith(("episode", "chapter", "story_arcs", "organization", "volume")):
        return ("box-type-floor", f"verbatim {page_type} line on a floor door; structurally low-yield (A17)")
    return ("rank-floor", f"page absent from top-k on the {r['door']} door; floor, not a regression target")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ledgers = {d: load(LEDGERS / f"sweep_{d}_{PANEL_H8}.jsonl") for d in FLOOR_DOORS + ("qa", "auto")}

    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    page_type = dict(con.execute("select title, page_type from documents"))
    doc_text: dict[str, list[str]] = {}
    for title, text in con.execute(
            "select d.title, c.text from chunks c join documents d on d.id = c.document_id"):
        doc_text.setdefault(title, []).append(text)
    from scriptengine.eval.span_recall import decite, norm  # noqa: E402
    FLAT.update({t: decite(norm(" \n ".join(parts))) for t, parts in doc_text.items()})

    # -- qa misses + auto join -------------------------------------------------
    auto_by_key = {key(r): r for r in ledgers["auto"]}
    qa_rows = []
    for r in ledgers["qa"]:
        if r["verdict"] not in MISS:
            continue
        a = auto_by_key.get(key(r))
        qa_rows.append({
            "pre_triage": pre_triage(r), "verdict": r["verdict"], "title": r["title"],
            "page_type": page_type.get(r["title"]), "breadcrumb": r["breadcrumb"],
            "sentence": r["sentence"], "returned_docs": r.get("returned_docs", []),
            "error": r.get("error"),
            "auto_verdict": a["verdict"] if a else "NOT_IN_LEDGER",
            "auto_mode_routed": a.get("mode_routed") if a else None,
            "both_miss": bool(a) and a["verdict"] != "HIT",
        })
    assert len(qa_rows) == 261, f"qa misses {len(qa_rows)} != 261 (drift from the report)"

    # identical-to-misses_qa.jsonl check: same field set, same content
    report_misses = load(OUT.parent / "misses_qa.jsonl")
    mine = [{k: m[k] for k in ("pre_triage", "verdict", "title", "page_type", "breadcrumb",
                               "sentence", "returned_docs", "error")} for m in qa_rows]
    sort_key = lambda m: (m["pre_triage"], m["title"], m["breadcrumb"])
    assert json.dumps(sorted(mine, key=sort_key), ensure_ascii=False) == \
        json.dumps(sorted(report_misses, key=sort_key), ensure_ascii=False), \
        "pre_triage drift vs the committed misses_qa.jsonl"

    both = [m for m in qa_rows if m["both_miss"]]
    auto_only = [m for m in qa_rows if not m["both_miss"]]
    n1 = len(both) // 2
    p1, p2 = both[:n1], both[n1:] + auto_only

    def dump(name: str, rows: list[dict]) -> None:
        (OUT / name).write_text("".join(json.dumps(m, ensure_ascii=False) + "\n" for m in rows))

    dump("qa_p1.jsonl", p1)
    dump("qa_p2.jsonl", p2)

    # -- floor sample (narrative + roster) --------------------------------------
    cells: dict[tuple[str, str, str], list[dict]] = {}
    hist: dict[tuple[str, str, str], int] = {}
    for d in FLOOR_DOORS:
        for r in ledgers[d]:
            if r["verdict"] == "HIT":
                continue
            c = (d, page_type.get(r["title"]) or "?", r["verdict"])
            hist[c] = hist.get(c, 0) + 1
            cells.setdefault(c, []).append(r)
    sample_rows = []
    for (d, pt, v), rows in sorted(cells.items()):
        for r in rows[:CAP]:
            cls, reason = floor_class({**r, "door": d}, pt)
            sample_rows.append({
                "door": d, "page_type": pt, "verdict": v, "cell_total": hist[(d, pt, v)],
                "class": cls, "reason": reason, "title": r["title"], "breadcrumb": r["breadcrumb"],
                "sentence": r["sentence"], "returned_docs": r.get("returned_docs", []),
                "truncated": r.get("truncated"),
            })
    dump("floor_sample.jsonl", sample_rows)

    def sha(p: Path) -> str:
        return hashlib.sha256(p.read_bytes()).hexdigest()

    meta = {
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "panel_h8": PANEL_H8, "heldout_h8": HELDOUT_H8,
        "ledger_commits": {d: dict(Counter(r["commit"] for r in ledgers[d])) for d in ledgers},
        "qa_misses": len(qa_rows), "both_miss": len(both), "auto_only": len(auto_only),
        "split": {"qa_p1": len(p1), "qa_p2": len(p2)},
        "floor": {"doors": list(FLOOR_DOORS), "cells": len(cells), "sampled_rows": len(sample_rows),
                  "cap_per_cell": CAP, "residual_rows": sum(hist.values()),
                  "histogram": {f"{d}|{pt}|{v}": n for (d, pt, v), n in sorted(hist.items())}},
        "shas": {p.name: sha(p) for p in sorted(OUT.glob("*.jsonl")) if p.name != "meta.json"},
    }
    (OUT / "meta.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(f"qa misses {len(qa_rows)} (both {len(both)} / auto-only {len(auto_only)}) "
          f"-> p1 {len(p1)}, p2 {len(p2)}; floor {len(cells)} cells, {len(sample_rows)} sampled, "
          f"{sum(hist.values())} residual rows total")


if __name__ == "__main__":
    main()