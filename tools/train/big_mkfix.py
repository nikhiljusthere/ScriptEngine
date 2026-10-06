"""Compact review edits -> bfix.json for tools/train/big_review.py --fix.

usage: python big_mkfix.py edits.txt bfix.json   (SCRIPTENGINE_ROOT overrides the checkout)

Format (one block per corrected window):
  @<b-number> <why>
  keep                      start from the 35B's rows (else start empty)
  r Old=>New                rename an end in every kept row
  - S|verb|O                drop a row (O '-' = null)
  + S|verb|O|quote          add a row
Exact duplicates and symmetric met/fought duplicates are dropped (the gate refuses them).
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SCRIPTENGINE_ROOT", Path(__file__).resolve().parents[2]))
LABELS = ROOT / "series/universal/training/big/labels.jsonl"


def key(r):
    return (r["subject"], r["verb"], r["object"])


def main():
    src, out = sys.argv[1], sys.argv[2]
    lines = open(LABELS).read().splitlines()
    fixes, cur = [], None
    for raw in open(src):
        s = raw.rstrip("\n")
        if not s.strip() or s.lstrip().startswith("#"):
            continue
        if s.startswith("@"):
            n, _, why = s[1:].partition(" ")
            row = json.loads(lines[int(n) - 1])
            cur = {"id": row["id"], "why": why.strip(), "events": [], "_src": row["events"], "_n": n}
            fixes.append(cur)
        elif s.strip() == "keep":
            cur["events"] = [dict(e) for e in cur["_src"]]
        elif s.startswith("r "):
            old, new = s[2:].split("=>")
            for e in cur["events"]:
                for f in ("subject", "object"):
                    if e[f] == old.strip():
                        e[f] = new.strip()
        elif s.startswith("- "):
            p = [x.strip() for x in s[2:].split("|")]
            k = (p[0], p[1], None if p[2] == "-" else p[2])
            before = len(cur["events"])
            cur["events"] = [e for e in cur["events"] if key(e) != k]
            if len(cur["events"]) == before:
                sys.exit(f"b{cur['_n']}: no row to drop: {k}")
        elif s.startswith("+ "):
            p = [x.strip() for x in s[2:].split("|", 3)]
            cur["events"].append({"quote": p[3], "subject": p[0], "verb": p[1],
                                  "object": None if p[2] == "-" else p[2]})
        else:
            sys.exit(f"bad line: {s}")
    for f in fixes:
        f.pop("_src")
        f.pop("_n")
        uniq = []
        for e in f["events"]:
            ks = {key(u) for u in uniq}
            if e["verb"] in ("met", "fought"):
                ks |= {(u["object"], u["verb"], u["subject"]) for u in uniq}
            if key(e) not in ks:
                uniq.append(e)
        f["events"] = uniq
    json.dump(fixes, open(out, "w"), ensure_ascii=False, indent=0)
    print(f"{len(fixes)} windows -> {out}")


if __name__ == "__main__":
    main()
