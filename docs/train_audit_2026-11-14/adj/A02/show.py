import json, sys
P="/home/goblin/ScriptEngine/.claude/worktrees/9b-model-extraction-analysis-a7e9c9/docs/train_audit_2026-11-14/adj/A02_adj_input.jsonl"
lo,hi=int(sys.argv[1]),int(sys.argv[2])
for i,l in enumerate(open(P)):
    if not (lo<=i<hi): continue
    d=json.loads(l)
    print("="*30, i, "b", d["b"], d["id"], d.get("series"), "|", d["page"], "/", d["section"])
    print("BEFORE:", d.get("page_text_before","")[-400:])
    for k,v in d["sentences"].items(): print(f"  [{k}] {v}")
    print("AFTER:", d.get("page_text_after","")[:300])
    print("GOLD EV:"); [print("   ",e) for e in d["gold_events"]]
    print("GOLD FACTS:"); [print("   ",e) for e in d["gold_facts"]]
    print("GOLD TAGS:"); [print("   ",e) for e in d["gold_tags"]]
    print("NOTES:", d.get("reviewer_notes"))
    print("SR:", d.get("second_reader"))
    for k in ("second_reader_only_events","gold_only_events","gold_people_second_reader_omits"):
        print(k, d.get(k))
    other=[k for k in d if k not in ("b","id","series","page","section","page_text_before","page_text_after","sentences","gold_events","gold_facts","gold_tags","reviewer_notes","second_reader","second_reader_only_events","gold_only_events","gold_people_second_reader_omits")]
    if other: print("OTHER KEYS", other)
