#!/usr/bin/env python3
"""Supervisor's viewer: the latest gold record of windows by b number, with every reviewer note.
    python3 adj/show_gold.py 1046 1058
"""
import json, sys
G = "/home/goblin/ScriptEngine/series/universal/training/big/gold_v2/"
rows = [json.loads(l) for l in open(G + "gold_in.jsonl")]
hist = {}
for l in open(G + "gold_audit_v2.jsonl"):
    l = l.strip("\x00\n ")
    if l:
        r = json.loads(l)
        if r.get("void"):
            if hist.get(r["id"]): hist[r["id"]].pop()
        else: hist.setdefault(r["id"], []).append(r)
for b in map(int, sys.argv[1:]):
    w = rows[b - 1]; h = hist.get(w["id"], [])
    print(f"=== b{b} {w.get('series')} | {w.get('page')} | {w.get('section')} | id {w['id']}")
    print("  TEXT:", w.get("passage") or w.get("text") or w.get("window") or w.get("input"))
    if not h: print("  (no gold record)"); continue
    a = h[-1]
    for e in a["events"]: print(f"  E {e['subject']}|{e['verb']}|{e.get('object')}  «{e['quote']}»")
    for f in a["facts"]: print(f"  F {f['subject']}|{f['relation']}|{f.get('object')}|{f.get('modality') or 'actual'}|{f.get('certainty') or 'stated'}|{f.get('asserted_by') or ''}  «{f['quote']}»")
    for t in a["tags"]: print(f"  T {t['tag']}  «{t['quote']}»")
    for x in h: print("  NOTE:", x.get("why"))
    print()
