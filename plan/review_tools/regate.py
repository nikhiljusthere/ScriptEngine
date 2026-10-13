"""Re-gate stage-1 still-refused rows whose refusal reason contains argv[1], with the CURRENT gates; print passes."""
import json, sys, importlib.util
W="/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags"; R="/home/goblin/ScriptEngine"
sys.path.insert(0, f"{W}/tools/train")
spec=importlib.util.spec_from_file_location("label_single", f"{W}/tools/train/label_single.py")
ls=importlib.util.module_from_spec(spec); spec.loader.exec_module(ls)
import verify_row_wiki as vrw
P={}
for s in ("marvel","mcu"):
    for l in open(f"{R}/series/{s}/training/labels/big_in.jsonl"):
        d=json.loads(l); P[d["id"]]=d["messages"][1]["content"].split("Passage:\n",1)[1]
WK={}
n=p=0
for l in open(sys.argv[2] if len(sys.argv)>2 else "/home/goblin/ScriptEngine/series/universal/training/big/audit_27b_2026-10-13/stage1_still_refused.jsonl"):
    x=json.loads(l)
    if sys.argv[1] not in x["why"]: continue
    n+=1; w=P[x["id"]]; s=x.get("series") or "marvel"
    wk=WK.setdefault(s, vrw.Wiki(f"{R}/series/{s}/facts.db")); d=x["row"]
    if x["kind"]=="dropped": k,dr=ls.gate([{a:d.get(a) for a in ("quote","subject","verb","object")}],w,wk)
    elif x["kind"]=="dropped_facts": k,dr=ls.fact_gate_keep([d],w,wk)
    else: k,dr=ls.tag_gate_keep([d],w)
    ok=bool(k) and not dr; p+=ok
    print("PASS" if ok else "STILL", "|", k[0] if ok else (dr[0].get("why") if dr else "?")[:70], "|", d.get("subject"), d.get("relation") or d.get("verb"), d.get("object"), "|", (d.get("quote") or "")[:60])
print(f"{p}/{n} pass now")
