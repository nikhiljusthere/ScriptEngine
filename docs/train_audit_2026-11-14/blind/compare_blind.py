#!/usr/bin/env python3
"""Compare a blind second reading with the gold's per-line targets. Lines where the two readers differ are
the audit's work list; lines where they agree are confirmed by two independent readings.

    python compare_blind.py GOLD.jsonl BLIND.jsonl [--newer GOLD_CORRECTED.jsonl] [--worklist OUT.jsonl]

--newer: a corrected copy of the same gold. Then the script also reports, for the lines the correction changed,
how many the blind reading had already disagreed with (does blind reading find known errors) and how often it
agrees with the corrected line.
"""
import argparse, collections, json

ap = argparse.ArgumentParser()
ap.add_argument("gold"); ap.add_argument("blind"); ap.add_argument("--newer"); ap.add_argument("--worklist")
a = ap.parse_args()
load = lambda p: {json.loads(l)["id"]: json.loads(l) for l in open(p)}
gold, blind = load(a.gold), load(a.blind)
newer = load(a.newer) if a.newer else None
tri = lambda l: sorted([e[0], e[1], e[2] or 0] for e in l.get("events", []))
sym = lambda l: sorted((e[0], *sorted([e[1], e[2] or 0])) if e[0] in ("fought", "met") else (e[0], e[1], e[2] or 0) for e in l.get("events", []))
C = collections.Counter(); work = []
for i, b in blind.items():
    if i not in gold: continue
    g = {l["n"]: l for l in gold[i]["target"]["lines"]}
    nw = {l["n"]: l for l in newer[i]["target"]["lines"]} if newer and i in newer else {}
    for bl in b["lines"]:
        n = int(bl["n"]); gl = g.get(n)
        if gl is None: C["line number not in gold"] += 1; continue
        C["lines"] += 1
        same_c = bl["class"] == gl["class"]; same_p = sorted(bl.get("people", [])) == sorted(gl["people"]); same_e = sym(bl) == sym(gl)
        C["class agrees"] += same_c; C["people agree"] += same_p; C["events agree"] += same_e
        allsame = same_c and same_p and same_e
        C["line agrees on everything"] += allsame
        if gl["class"] == "event" and bl.get("real") is False: C["gold says event, blind says nothing in it happened"] += 1
        if not allsame:
            work.append({"id": i, "n": n, "class": [gl["class"], bl["class"]], "people": [gl["people"], sorted(bl.get("people", []))], "events": [tri(gl), tri(bl)], "real": bl.get("real")})
        if nw and n in nw and (nw[n]["class"], sorted(nw[n]["people"]), sym(nw[n])) != (gl["class"], sorted(gl["people"]), sym(gl)):
            C["lines the known correction changed"] += 1
            C["  of those: blind disagreed with the old gold (error found)"] += not allsame
            C["  of those: blind agrees fully with the corrected line"] += (bl["class"] == nw[n]["class"] and sorted(bl.get("people", [])) == sorted(nw[n]["people"]) and sym(bl) == sym(nw[n]))
            C["  of those: blind agrees with the corrected events"] += sym(bl) == sym(nw[n])
n = max(C["lines"], 1)
for k, v in C.items():
    print(f"{v:6d}  {k}" + (f"  ({v / n:.1%})" if k.endswith(("agrees", "agree", "everything")) else ""))
print(f"windows compared {sum(1 for i in blind if i in gold)}; lines needing a third look {len(work)} ({len(work) / n:.1%})")
if a.worklist:
    with open(a.worklist, "w") as f:
        for w in work: f.write(json.dumps(w) + "\n")
