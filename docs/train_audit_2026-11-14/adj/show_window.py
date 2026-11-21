#!/usr/bin/env python3
"""Supervisor's viewer: print third-look windows compactly so a verdict can be checked by eye.
    python3 adj/show_window.py adj/A01_adj_input.jsonl [adj/A01_verdicts.jsonl] [--verdict gold_ok] [--b 6,29]
"""
import json, sys
args = [a for a in sys.argv[1:] if not a.startswith("--")]
opt = dict(zip(sys.argv[1:], sys.argv[2:]))
rows = [json.loads(l) for l in open(args[0])]
ver = {}
if len(args) > 1:
    ver = {json.loads(l)["b"]: json.loads(l) for l in open(args[1])}
want_v = opt.get("--verdict"); want_b = {int(x) for x in opt["--b"].split(",")} if "--b" in opt else None
for r in rows:
    v = ver.get(r["b"], {})
    if want_v and v.get("verdict") != want_v: continue
    if want_b and r["b"] not in want_b: continue
    print(f"=== b{r['b']}  {r.get('series','')} | {r.get('page','')} | {r.get('section','')}  [{v.get('verdict','')}]")
    S = r["sentences"]
    items = S.items() if isinstance(S, dict) else enumerate(S, 1)
    for i, s in items:
        print(f"  {i}. {s}")
    print("  GOLD ev:", "; ".join(f"{e[0]}|{e[1]}|{e[2]}" for e in r["gold_events"]) or "-")
    print("  blind-only:", r.get("second_reader_only_events") or "-")
    print("  gold-only:", r.get("gold_only_events") or "-")
    if r.get("gold_people_second_reader_omits"): print("  gold people blind omits:", r["gold_people_second_reader_omits"])
    if r.get("reviewer_notes"): print("  note:", str(r["reviewer_notes"])[:400])
    if v: print("  VERDICT:", v.get("reason"))
    print()
