"""Deterministic post-filter for extracted event rows (council 2026-09-29: the
student proposes, checks it cannot talk past decide what ships). No model.

Rejects, in order:
  verb      not one of the 12 (the student once wrote "released")
  shape     object missing (non-awakened) or present for awakened
  quote     not in the passage (verbatim, apostrophe-style repair allowed)
  end       subject/object resolves to exactly one wiki page of a type that is
            never an end (species = a class; chapter/episode/volume/... pages)
  duplicate same (s, v, o) twice, or both halves of a symmetric fought/met pair

`score` measures what the filter costs on adjudicated gold (correct rows it
rejects) and what it buys on a model's predictions (rows removed, precision).

    python tools/train/postfilter.py score --gold gold.jsonl
"""
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools" / "train"))
from scriptengine.ingest.verbatim import quoted_in  # noqa: E402
from gold_tools import VERBS, repair_quote  # noqa: E402

NEVER_END = {"species", "chapter", "episode", "volume", "music", "blu_ray_dvd", "game", "novel",
             "anime", "series", "stage_play", "story_arcs"}
SYMMETRIC = {"fought", "met"}


def _norm(x):
    return (x or "").strip().lower()


def filter_rows(rows, passage, wiki=None):
    """(kept, rejected[(row, reason)]) for one window's rows."""
    kept, rejected, seen = [], [], set()
    for e in rows:
        v = _norm(e.get("verb"))
        s, o = e.get("subject"), e.get("object")
        if v not in VERBS:
            rejected.append((e, "verb")); continue
        if (v == "awakened") != (o is None) or not s:
            rejected.append((e, "shape")); continue
        q = e.get("quote") or ""
        if not (quoted_in(q, passage) or repair_quote(q, passage)):
            rejected.append((e, "quote")); continue
        if wiki is not None:
            bad = False
            for end in (s, o):
                pages = wiki.resolve(end) if end else []
                if len(pages) == 1 and wiki.label[pages[0]] in NEVER_END:
                    bad = True
            if bad:
                rejected.append((e, "end")); continue
        key = (_norm(s), v, _norm(o))
        twin = (_norm(o), v, _norm(s))
        if key in seen or (v in SYMMETRIC and twin in seen):
            rejected.append((e, "duplicate")); continue
        seen.add(key)
        kept.append({**e, "verb": v})
    return kept, rejected


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["score"])
    ap.add_argument("--gold", required=True, help="adjudicated training records (export shape)")
    ap.add_argument("--no-wiki", action="store_true")
    a = ap.parse_args()
    wiki = None
    if not a.no_wiki:
        from verify_row_wiki import Wiki
        wiki = Wiki(ROOT / "series" / "jjk" / "facts.db")
    total, why = 0, {}
    for l in open(a.gold):
        r = json.loads(l)
        text = r["messages"][1]["content"].split("Passage:\n", 1)[1]
        ev = json.loads(r["messages"][2]["content"])["events"]
        total += len(ev)
        for e, reason in filter_rows(ev, text, wiki)[1]:
            why.setdefault(reason, []).append((r["id"], e))
    n = sum(len(v) for v in why.values())
    print(f"gold rows {total}; wrongly rejected {n} ({n / max(total, 1):.2%})")
    for reason, items in why.items():
        print(f"  {reason}: {len(items)}")
        for i, e in items[:6]:
            print(f"     {i} {e.get('subject')} ={e.get('verb')}=> {e.get('object')} | {str(e.get('quote'))[:70]}")


if __name__ == "__main__":
    main()
