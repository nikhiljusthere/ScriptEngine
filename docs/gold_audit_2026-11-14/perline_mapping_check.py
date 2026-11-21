#!/usr/bin/env python3
"""Check the per-line benchmark's name -> candidate-number mapping (tools/train/perline_build.py `num`).

`num` returns the FIRST candidate, in alphabetical order, whose name or alias shares a word with the gold
name (eval_extraction.same). This script re-resolves every gold end with a stricter rule (exact form first,
then the shortest candidate whose own name contains all the name's words, battle / chapter pages last) and
reports how often the first-match answer differs, and what it picked instead.

    python perline_mapping_check.py --tools <repo>/tools --db STORE.db FILE.jsonl [--only-split dev]
"""
import argparse, collections, json, re, sys

ap = argparse.ArgumentParser()
ap.add_argument("--tools", required=True); ap.add_argument("--db", required=True); ap.add_argument("file")
ap.add_argument("--only-split", default=None); ap.add_argument("--series", default="jjk")
a = ap.parse_args()
sys.path.insert(0, a.tools); sys.path.insert(0, a.tools + "/train")
import eval_extraction as ee  # noqa: E402
from perline_candidates import candidates, load_store  # noqa: E402

store = load_store(a.db)
names, al = store[0], store[1]
NONPERSON = re.compile(r" vs\.? | & |^(Chapter|Episode|Volume|Season) |\bArc$|Incident$", re.I)
W = lambda s: set(re.findall(r"[a-z0-9']+", s.lower()))


def first_match(name, cand_ids):
    for n in cand_ids:
        if any(ee.same(name, x) for x in {names[n]} | al.get(n, set())): return n
    return None


def strict(name, cand_ids):
    best, key = None, None
    for n in cand_ids:
        forms = {names[n]} | al.get(n, set())
        if not any(ee.same(name, x) for x in forms): continue
        exact = any(" ".join(x.lower().split()) == " ".join(name.lower().split()) for x in forms)
        sub = W(name) <= W(names[n])
        k = (0 if exact else 1, 1 if NONPERSON.search(names[n]) else 0, 0 if sub else 1, len(W(names[n])), names[n])
        if key is None or k < key: best, key = n, k
    return best


rows = [json.loads(l) for l in open(a.file)]
rows = [r for r in rows if r.get("series") == a.series and (a.only_split is None or str(r.get("split", "")).startswith(a.only_split))]
tot = diff = to_nonperson = 0; pairs = collections.Counter(); wins = set(); ev_tot = ev_bad = 0
for r in rows:
    cand_ids = candidates(r, store)
    bad_names = set()
    for layer, keys in (("events", ("subject", "object")), ("facts", ("subject", "object"))):
        for x in r[layer]:
            for k in keys:
                nm = x.get(k)
                if not nm or (layer == "facts" and k == "object" and x.get("relation") == "other_verb"): continue
                f, s = first_match(nm, cand_ids), strict(nm, cand_ids)
                if f is None: continue
                tot += 1
                if f != s:
                    diff += 1; wins.add(r["id"]); bad_names.add(nm)
                    to_nonperson += bool(NONPERSON.search(names[f]))
                    pairs[(nm, names[f], names[s])] += 1
    for e in r["events"]:
        ev_tot += 1
        ev_bad += (e.get("subject") in bad_names) or (e.get("object") in bad_names)
print(f"{a.file.split('/')[-2]}/{a.file.split('/')[-1]} [{a.series}{' ' + a.only_split if a.only_split else ''}]: {len(rows)} windows")
print(f"  gold ends resolved to a candidate: {tot}; first-match differs from the strict choice: {diff} ({diff / max(tot, 1):.1%}); of those, mapped to a battle / chapter page: {to_nonperson}")
print(f"  windows with at least one such end: {len(wins)}/{len(rows)}; events touching one: {ev_bad}/{ev_tot} ({ev_bad / max(ev_tot, 1):.1%})")
for (nm, f, s), c in pairs.most_common(22):
    print(f"   {c:4d}  \"{nm}\" -> \"{f}\"   (strict: \"{s}\")")
