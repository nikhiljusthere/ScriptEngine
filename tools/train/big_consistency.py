"""Consistency check for the big-window review: reviewed windows that share sentences
(the same passage cut at different offsets, or repeated on several pages) must carry
the same final rows for the shared part. Prints every pair whose rows differ.

usage: python big_consistency.py   (SCRIPTENGINE_ROOT overrides the checkout)
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault("SCRIPTENGINE_ROOT", str(Path(__file__).resolve().parents[2]))
import big_flags as bf  # noqa: E402

br = bf.br


def main():
    rows, c, pas = br.jl(br.LABELS), br.cursor(), br.passages()
    final = {a["id"]: a["after"] for a in br.jl(br.AUDIT)}
    sent_of = {}
    for i, r in enumerate(rows[:c], 1):
        for x in bf.sentences(pas[r["id"]]):
            if len(x) > 60:
                sent_of.setdefault(bf.norm(x), []).append(i)
    pairs = {}
    for lst in sent_of.values():
        for a in lst:
            for b in lst:
                if a < b:
                    pairs[(a, b)] = pairs.get((a, b), 0) + 1
    diff = 0
    for (a, b), n in sorted(pairs.items()):
        if n < 2:
            continue
        ra, rb = rows[a - 1], rows[b - 1]
        nb = {bf.norm(y) for y in bf.sentences(pas[rb["id"]])}
        shared = [x for x in bf.sentences(pas[ra["id"]]) if bf.norm(x) in nb]

        def keys(r):
            return {(e["subject"], e["verb"], e["object"]) for e in final.get(r["id"], r["events"])
                    if any(e["quote"] in s for s in shared)}
        ka, kb = keys(ra), keys(rb)
        if ka != kb:
            diff += 1
            print(f"b{a}~b{b} ({n} shared sentences) DIFF\n  only b{a}: {sorted(ka - kb, key=str)}"
                  f"\n  only b{b}: {sorted(kb - ka, key=str)}")
    print(f"{sum(1 for v in pairs.values() if v >= 2)} overlapping pairs, {diff} inconsistent")


if __name__ == "__main__":
    main()
