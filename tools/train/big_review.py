#!/usr/bin/env python3
"""Claude's review of the single-pass 35B labels (owner 2026-10-07: "review
every window as it lands ... this 12000 dataset will also be flawless").

labels.jsonl is append-only, written by label_single.py in a shuffled
order; the review cursor counts how many of its lines Claude has read.
Corrections never edit labels.jsonl: they are logged to big_audit.jsonl
({id, before, after, why}); the reviewed set = the first <cursor> lines
with the latest correction per id applied (reviewed_labels()).

    big_review.py --status
    big_review.py --next 30 [--chars 900]     # print unreviewed windows
    big_review.py --fix FILE.json              # [{id, events:[...], why}], gated
    big_review.py --mark N                     # N lines reviewed
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "train"))
BIG = ROOT / "series/universal/training/big"
LABELS, AUDIT, CURSOR = BIG / "labels.jsonl", BIG / "big_audit.jsonl", BIG / "review_cursor.txt"
SRC = [ROOT / "series" / s / "training/labels/big_in.jsonl" for s in ("marvel", "mcu")]


def jl(p):
    return [json.loads(l) for l in open(p)] if Path(p).exists() else []


def cursor():
    try:
        return int(CURSOR.read_text().strip())
    except (OSError, ValueError):
        return 0


def passages():
    return {r["id"]: r["messages"][1]["content"].split("Passage:\n", 1)[1] for p in SRC for r in jl(p)}


def reviewed_labels():
    """The reviewed windows with Claude's corrections applied (latest wins)."""
    fixes = {}
    for a in jl(AUDIT):
        fixes[a["id"]] = a["after"]
    out = []
    for r in jl(LABELS)[:cursor()]:
        if r["id"] in fixes:
            r = {**r, "events": fixes[r["id"]], "reviewed_fix": True}
        out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--next", type=int, default=0)
    ap.add_argument("--chars", type=int, default=1200)
    ap.add_argument("--fix")
    ap.add_argument("--mark", type=int)
    a = ap.parse_args()
    rows = jl(LABELS)
    c = cursor()
    if a.fix:
        import label_single
        import verify_row_wiki as vrw
        pas = passages()
        byid = {r["id"]: r for r in rows}
        wikis = {}
        for f in json.load(open(a.fix)):
            r = byid[f["id"]]
            wiki = wikis.setdefault(r["series"], vrw.Wiki(str(ROOT / "series" / r["series"] / "facts.db")))
            ev = [{k: e.get(k) for k in ("quote", "subject", "verb", "object")} for e in f["events"]]
            kept, dropped = label_single.gate(ev, pas[f["id"]], wiki)
            if dropped or len(kept) != len(ev):
                print(f"REFUSED {f['id']}: {[(d.get('subject'), d.get('verb'), d.get('object'), d['why']) for d in dropped]}"
                      f" kept {len(kept)}/{len(ev)}")
                continue
            prev = [x for x in jl(AUDIT) if x["id"] == f["id"]]
            before = prev[-1]["after"] if prev else r["events"]
            with open(AUDIT, "a") as fh:
                fh.write(json.dumps({"id": f["id"], "series": r["series"], "page": r["page"],
                                     "before": before, "after": ev, "why": f["why"]}, ensure_ascii=False) + "\n")
            print(f"FIXED {f['id']} ({len(before)} -> {len(ev)} rows)")
    if a.mark is not None:
        CURSOR.write_text(str(min(a.mark, len(rows))))
        print(f"reviewed through {min(a.mark, len(rows))}")
    if a.next:
        pas = passages()
        for i, r in enumerate(rows[c:c + a.next], c + 1):
            ev = [(e["subject"], e["verb"], e["object"], e["quote"][:50]) for e in r["events"]]
            head = f"===== b{i} {r['page']} / {r['section']}" + ("" if r["ok"] else "  [PARSE FAIL]")
            print(head + "\n" + pas[r["id"]][:a.chars])
            print(" ROWS", ev if ev else "[]")
            if r.get("dropped"):
                print(" GATE-DROPPED", [(d.get("subject"), d.get("verb"), d.get("object"), d.get("why")) for d in r["dropped"]])
        print(f"[printed b{c+1}..b{min(c + a.next, len(rows))} of {len(rows)}; mark with --mark {min(c + a.next, len(rows))}]")
    if a.status or not (a.next or a.fix or a.mark is not None):
        fixes = len({x["id"] for x in jl(AUDIT)})
        print(f"labeled {len(rows)} | reviewed {c} | waiting {len(rows) - c} | windows corrected {fixes}")


if __name__ == "__main__":
    main()
