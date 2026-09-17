"""Tabulate a finished P2.1 sweep into a report directory (model-free, read-only).

Reads the five sweep ledgers `tools/csm/p21_sweep.sh` writes and emits the
A17 grading inputs the runner's receipt names:

- door_verdicts.json      per-door verdict counts over the full panel
- auto_routing.json       auto door (full + heldout): router choice x verdict
- misses_qa.jsonl         the qa miss file (MISS_DOC + MISS_SPAN + ERROR), each
                          row with a MECHANICAL pre-triage class (below)
- residuals_by_type.json  narrative / roster / auto residuals by verdict x the
                          line's page type x top-level section
- a7_dimension_check.json the 26 bar-audit anchored panel lines
                          (bar_audit_p14_preregistered.json) looked up per door:
                          chairman #30 A7 re-grades P2.2 only if a miss shifts
                          a D6 dimension

The pre-triage is mechanical, not a judged triage: it sorts the qa misses into
shape classes so the row-by-row reading starts from groups, it does not assign
the reason. Classes, first match wins:
  table-row        the probe line is a pipe-delimited table row, not prose
  near-page        MISS_DOC, but a returned doc shares the line's base page
                   ("Denji" for "Denji/History"): the right subject, wrong page
  corpus-duplicate the decited line is also verbatim on another page, so the
                   query is genuinely ambiguous about which page is wanted
  short            under 10 words: little signal to retrieve on
  rank-miss        MISS_DOC otherwise (a ranking problem)
  span-miss        MISS_SPAN otherwise (page reached, line not in its beats)

Usage:
    python tools/csm/p21_sweep_report.py --out reports/csm/<run dir>
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scriptengine.eval.span_recall import decite, norm  # noqa: E402

LEDGERS = ROOT / "reports/span-recall/csm"
PANEL_H8 = "e3d73720"
HELDOUT_H8 = "ec15e0d8"
DOORS = ("qa", "narrative", "roster", "auto")
BAR_AUDIT = ROOT / "reports/csm/bar_audit_p14_preregistered.json"
DB = ROOT / "series/csm/facts.db"
MISS = ("MISS_DOC", "MISS_SPAN", "ERROR")


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open() if line.strip()]


def key(row: dict) -> tuple[str, str, str]:
    return row["title"], row["breadcrumb"], row["sentence"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    ledgers = {d: load(LEDGERS / f"sweep_{d}_{PANEL_H8}.jsonl") for d in DOORS}
    heldout = load(LEDGERS / f"sweep_auto_{HELDOUT_H8}.jsonl")

    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    page_type = dict(con.execute("select title, page_type from documents"))
    doc_text: dict[str, list[str]] = defaultdict(list)
    for title, text in con.execute(
            "select d.title, c.text from chunks c join documents d on d.id = c.document_id"):
        doc_text[title].append(text)
    flat = {t: decite(norm(" \n ".join(parts))) for t, parts in doc_text.items()}

    def write(name: str, obj) -> None:
        (args.out / name).write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")

    # -- per-door verdicts ---------------------------------------------------
    verdicts = {d: dict(Counter(r["verdict"] for r in rows)) for d, rows in ledgers.items()}
    verdicts["auto-heldout"] = dict(Counter(r["verdict"] for r in heldout))
    for d, rows in [*ledgers.items(), ("auto-heldout", heldout)]:
        verdicts[d]["rows"] = len(rows)
        verdicts[d]["hit_rate"] = round(100 * verdicts[d].get("HIT", 0) / len(rows), 4)
        verdicts[d]["commits"] = dict(Counter(r["commit"] for r in rows))
        verdicts[d]["devices"] = dict(Counter(r["device"] for r in rows))
    write("door_verdicts.json", verdicts)

    # -- auto routing --------------------------------------------------------
    routing = {}
    for label, rows in (("auto_full", ledgers["auto"]), ("auto_heldout", heldout)):
        by: dict[str, Counter] = defaultdict(Counter)
        for r in rows:
            by[r["mode_routed"]][r["verdict"]] += 1
        routing[label] = {
            m: {**dict(c), "n": sum(c.values()), "share": round(100 * sum(c.values()) / len(rows), 2),
                "hit_rate": round(100 * c["HIT"] / sum(c.values()), 2)}
            for m, c in sorted(by.items(), key=lambda kv: -sum(kv[1].values()))
        }
    # the counterfactual the routing leak implies: the same line through forced qa
    qa_by_key = {key(r): r["verdict"] for r in ledgers["qa"]}
    cf = Counter()
    for r in ledgers["auto"]:
        cf[(r["mode_routed"], r["verdict"], qa_by_key.get(key(r)))] += 1
    routing["auto_vs_forced_qa"] = {
        "auto_miss_but_qa_hit": sum(n for (m, v, q), n in cf.items() if v != "HIT" and q == "HIT"),
        "auto_hit_but_qa_miss": sum(n for (m, v, q), n in cf.items() if v == "HIT" and q != "HIT"),
        "both_hit": sum(n for (m, v, q), n in cf.items() if v == "HIT" and q == "HIT"),
        "both_miss": sum(n for (m, v, q), n in cf.items() if v != "HIT" and q != "HIT"),
    }
    write("auto_routing.json", routing)

    # -- qa miss file + mechanical pre-triage ---------------------------------
    def pre_triage(r: dict) -> str:
        s = r["sentence"]
        if s.lstrip().startswith("|") or " | " in s:
            return "table-row"
        base = r["title"].split("/")[0]
        if r["verdict"] == "MISS_DOC" and any(
                d and d != r["title"] and d.split("/")[0] == base for d in r.get("returned_docs", [])):
            return "near-page"
        needle = decite(norm(s))
        if any(needle in txt for t, txt in flat.items() if t != r["title"]):
            return "corpus-duplicate"
        if len(s.split()) < 10:
            return "short"
        return "rank-miss" if r["verdict"] == "MISS_DOC" else "span-miss" if r["verdict"] == "MISS_SPAN" else "error"

    qa_miss = []
    for r in ledgers["qa"]:
        if r["verdict"] in MISS:
            qa_miss.append({
                "pre_triage": pre_triage(r), "verdict": r["verdict"], "title": r["title"],
                "page_type": page_type.get(r["title"]), "breadcrumb": r["breadcrumb"],
                "sentence": r["sentence"], "returned_docs": r.get("returned_docs", []),
                "error": r.get("error"),
            })
    qa_miss.sort(key=lambda m: (m["pre_triage"], m["title"], m["breadcrumb"]))
    (args.out / "misses_qa.jsonl").write_text(
        "".join(json.dumps(m, ensure_ascii=False) + "\n" for m in qa_miss))

    # -- residuals by page type / section (narrative, roster, auto) ------------
    residuals = {}
    for d in ("narrative", "roster", "auto"):
        by_type: dict[str, Counter] = defaultdict(Counter)
        by_sec: dict[str, Counter] = defaultdict(Counter)
        for r in ledgers[d]:
            by_type[page_type.get(r["title"]) or "?"][r["verdict"]] += 1
            by_sec[r["breadcrumb"].split(" / ")[0]][r["verdict"]] += 1
        residuals[d] = {
            "by_page_type": {k: dict(v) for k, v in sorted(by_type.items(), key=lambda kv: -sum(kv[1].values()))},
            "by_top_section": {k: dict(v) for k, v in sorted(by_sec.items(), key=lambda kv: -sum(kv[1].values()))[:25]},
        }
    write("residuals_by_type.json", residuals)

    # -- A7: do the misses shift a bar-audit dimension? -------------------------
    bar = json.loads(BAR_AUDIT.read_text())
    idx = {d: {key(r): r["verdict"] for r in rows} for d, rows in ledgers.items()}
    a7 = []
    for item in bar["items"]:
        k = tuple(item["panel_line"])
        a7.append({"id": item["id"], "class": item["class"], "panel_line": item["panel_line"],
                   **{d: idx[d].get(k, "NOT_IN_LEDGER") for d in DOORS}})
    by_class: dict[str, Counter] = defaultdict(Counter)
    for row in a7:
        for d in DOORS:
            by_class[row["class"]][f"{d}:{row[d]}"] += 1
    write("a7_dimension_check.json", {"items": a7, "by_class": {c: dict(v) for c, v in by_class.items()}})

    # -- stdout summary (the numbers REPORT.md quotes) --------------------------
    print(json.dumps(verdicts, indent=1))
    print(json.dumps(routing, indent=1))
    print("qa pre-triage:", dict(Counter(m["pre_triage"] for m in qa_miss)))
    print("qa misses by page_type:", dict(Counter(m["page_type"] for m in qa_miss)))
    print("qa misses by top section:", Counter(m["breadcrumb"].split(" / ")[0] for m in qa_miss).most_common(12))
    print("A7 by class:", json.dumps({c: dict(v) for c, v in by_class.items()}, indent=1))


if __name__ == "__main__":
    main()
