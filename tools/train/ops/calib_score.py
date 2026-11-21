import json, sys
sys.path.insert(0,"tools"); from eval_extraction import score
cal=json.load(open("/mnt/PROJECTS/backups/jjk_100_20260929/opencode_calibration_ids.json"))
gold={}
for l in open("series/jjk/training/gold/gold_pilot_all.jsonl"):
    r=json.loads(l); ev=json.loads(r["messages"][2]["content"])["events"]
    gold[r["id"]]={"core":[[e["subject"],e["verb"],None if e["verb"]=="awakened" else e["object"]] for e in ev],"optional":[]}
for m,ids in cal.items():
    out={}
    for l in open(f"series/jjk/training/opencode/{m}_out.jsonl"):
        r=json.loads(l)
        if r["id"] in ids: out[r["id"]]=[e for e in r["events"] if str(e.get("verdict","")).lower()=="yes"]
    g={i:gold[i] for i in out}
    print(m, f"calibration windows done {len(out)}/15", score(g,out)[0] if out else "")
