"""Build the ability-dimension census pair set (P3.A) from the section inventory.

Companion to ``census_545_pairs.json``. For every character / character_synopsis
page, take each section whose *leaf* breadcrumb (the last `` / `` component) is
one of the five plan ability dimensions (``plan/Plan_to_perfection.md`` §P3:
Cursed Technique, Cursed Energy, Physical Prowess, Intelligence, Abilities and
Powers) and emit one pair per (page, dimension):

    {"dimension": ..., "page": <character>, "name": <character>, "question": ...}

Why leaf-based, not the exact-breadcrumb match the earlier "300" used: the
ability sections form a *nested tree* on most pages (a level-2 "Abilities and
Powers" parent with level-3 children like "Abilities and Powers / Cursed
Technique"). An exact-breadcrumb match on ``cursed technique`` sees only the
flat top-level sections and silently misses every nested child, so the pool
built that way under-counts. The census must catch both forms.

The five dimensions and their question templates are the plan's, not invented
here. This file is data, not logic: re-run it after any re-crawl so the census
pool tracks the wiki.

Usage:
    python tools/build_ability_pairs.py [--series jjk] [--out PATH]
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Plan §P3 ability dimensions. Leaf breadcrumb (lower-cased, last " / "
# component) -> dimension. Variants fold into their canonical dim; a leaf not
# listed (e.g. a specific sub-ability like "Flight" or "Intangible") is NOT one
# of the five dims and is left out of the pool on purpose.
LEAF_TO_DIM = {
    "cursed technique": "Cursed Technique",
    "cursed techniques": "Cursed Technique",
    "cursed energy": "Cursed Energy",
    "physical prowess": "Physical Prowess",
    "intelligence": "Intelligence",
    "great intellect": "Intelligence",
    "abilities and powers": "Abilities and Powers",
    "powers & abilities": "Abilities and Powers",
    "abilities": "Abilities and Powers",
}

# Fixed question per dimension (the plan's "consumer" query), with the name
# interpolated. Cursed Technique probes for *mechanics*, not just names -- that
# is the 3B fork (extract mechanics vs. widen the name inventory).
QUESTION = {
    "Cursed Technique": "What cursed techniques does {name} use, and how do they work?",
    "Cursed Energy": "How is {name}'s cursed energy described?",
    "Physical Prowess": "How is {name}'s physical prowess described?",
    "Intelligence": "How is {name}'s intelligence described?",
    "Abilities and Powers": "What abilities and powers does {name} have?",
}


def leaf(breadcrumb: str) -> str:
    # breadcrumb is "Page / Parent / Child" or a bare top-level title.
    return re.sub(r"\s+", " ", (breadcrumb or "").strip()).split(" / ")[-1].strip().lower()


def build(series: str) -> list:
    db = ROOT / "series" / series / "facts.db"
    con = sqlite3.connect(str(db))
    con.row_factory = sqlite3.Row
    rows = con.execute(
        """
        SELECT d.title AS page, c.breadcrumb AS crumb
        FROM sections c JOIN documents d ON c.document_id = d.id
        WHERE d.page_type IN ('character', 'character_synopsis')
        """
    ).fetchall()
    con.close()

    # One pair per (page, dim): a page may carry the same dim as a flat section
    # AND a nested child; the question is the same, so collapse to one.
    seen: dict = {}
    for r in rows:
        dim = LEAF_TO_DIM.get(leaf(r["crumb"]))
        if dim is None:
            continue
        key = (r["page"], dim)
        if key not in seen:
            seen[key] = {
                "dimension": dim,
                "page": r["page"],
                "name": r["page"],
                "question": QUESTION[dim].format(name=r["page"]),
            }
    pairs = sorted(seen.values(), key=lambda p: (p["name"], p["dimension"]))
    return pairs


def summarize(pairs: list) -> None:
    by_dim: dict = {}
    pages = set()
    for p in pairs:
        by_dim[p["dimension"]] = by_dim.get(p["dimension"], 0) + 1
        pages.add(p["page"])
    print(f"ability pool: {len(pairs)} pairs across {len(pages)} pages", flush=True)
    for dim in ("Cursed Technique", "Cursed Energy", "Physical Prowess",
                "Intelligence", "Abilities and Powers"):
        print(f"  {dim:<20} {by_dim.get(dim, 0)}", flush=True)
    print("\nnote: 'Abilities and Powers' is the level-2 parent of the other four "
          "on nested pages, so its pairs overlap the children's pages (a page "
          "carries the parent and its children). Read per-page, not as "
          "disjoint sets.", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="build the ability-dimension census pool")
    ap.add_argument("--series", default="jjk")
    ap.add_argument("--out", default=str(Path(__file__).with_name("census_ability_pairs.json")))
    args = ap.parse_args()
    pairs = build(args.series)
    json.dump(pairs, open(args.out, "w"), indent=1)
    summarize(pairs)


if __name__ == "__main__":
    main()