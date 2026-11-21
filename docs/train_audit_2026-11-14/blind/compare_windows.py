#!/usr/bin/env python3
"""Window-level comparison of a blind second reading with the gold's per-line targets.

    python compare_windows.py GOLD.jsonl BLIND.jsonl [--worklist OUT.jsonl] [--answer CORRECTED_GOLD.jsonl]

Per window: events as (verb, pair) sets (fought and met unordered). blind-only = candidate missing events,
gold-only = candidate wrong events, gold people the blind reader lists nowhere = candidate wrong person.
--answer: a corrected gold for the same windows; reports how many of its changes the blind reading finds.
"""
import argparse, collections, json

ap = argparse.ArgumentParser()
ap.add_argument("gold"); ap.add_argument("blind"); ap.add_argument("--worklist"); ap.add_argument("--answer")
a = ap.parse_args()
load = lambda p: {json.loads(l)["id"]: json.loads(l) for l in open(p) if l.strip()}
gold, blind = load(a.gold), load(a.blind)
ans = load(a.answer) if a.answer else {}


def evset(lines):
    s = set()
    for l in lines:
        for e in l.get("events", []):
            v, x, y = e[0], e[1], e[2] or 0
            s.add((v,) + tuple(sorted((x, y))) if v in ("fought", "met") else (v, x, y))
    return s


ppl = lambda lines: {p for l in lines for p in l.get("people", [])}
T = collections.Counter(); work = []; bad = 0
V = {"fought", "defeated", "killed", "captured", "escaped", "saved", "betrayed", "sealed", "met", "arrived", "departed", "awakened"}
for i, b in blind.items():
    g = gold.get(i)
    if g is None: T["window not in gold"] += 1; continue
    c = g["candidates"]; nm = lambda k: c[k - 1] if k else None
    gl = g["target"]["lines"]
    if sorted(int(l["n"]) for l in b["lines"]) != sorted(l["n"] for l in gl): bad += 1
    for l in b["lines"]:
        if any(not (1 <= p <= len(c)) for p in l.get("people", [])) or any(e[0] not in V for e in l.get("events", [])): bad += 1
    G, B = evset(gl), evset(b["lines"])
    Pg, Pb = ppl(gl), ppl(b["lines"])
    cls = sum(x["class"] == y["class"] for x, y in zip(sorted(gl, key=lambda l: l["n"]), sorted(b["lines"], key=lambda l: int(l["n"]))))
    T["windows"] += 1; T["lines"] += len(gl); T["class agrees"] += cls
    T["gold events"] += len(G); T["blind events"] += len(B); T["events in both"] += len(G & B)
    T["blind-only events"] += len(B - G); T["gold-only events"] += len(G - B)
    T["gold people"] += len(Pg); T["gold people the blind reader does not list"] += len(Pg - Pb)
    if (B - G) or (G - B) or (Pg - Pb):
        work.append({"id": i, "series": g["series"], "page": g["page"],
                     "blind_only": [[e[0], nm(e[1]), nm(e[2])] for e in sorted(B - G)],
                     "gold_only": [[e[0], nm(e[1]), nm(e[2])] for e in sorted(G - B)],
                     "gold_people_unlisted": [nm(p) for p in sorted(Pg - Pb)]})
    if i in ans:
        N = evset(ans[i]["target"]["lines"])
        T["answer key: events added"] += len(N - G); T["  found by blind"] += len((N - G) & B)
        T["answer key: events removed"] += len(G - N); T["  absent from blind too"] += len((G - N) - B)
for k, v in T.items(): print(f"{v:6d}  {k}")
print(f"format problems {bad}; windows with something to look at {len(work)}/{T['windows']}")
if a.worklist:
    with open(a.worklist, "w") as f:
        for w in work: f.write(json.dumps(w, ensure_ascii=False) + "\n")
