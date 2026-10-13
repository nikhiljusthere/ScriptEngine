"""Re-gate the dropped rows of labels_v2 with today's gates (2026-10-13 fixes). --write: put the passing rows into
the base rows of windows past the review cursor (backup first); reviewed windows are listed for a hand pass."""
import json, sys, importlib.util, collections, shutil
W="/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags"; R="/home/goblin/ScriptEngine"; B=f"{R}/series/universal/training/big"
sys.path.insert(0, f"{W}/tools/train")
spec=importlib.util.spec_from_file_location("label_single", f"{W}/tools/train/label_single.py"); ls=importlib.util.module_from_spec(spec); spec.loader.exec_module(ls)
import fact_gate as fg, verify_row_wiki as vrw
sys.path.insert(0, f"{W}/tools/train"); import big_review_v2 as br2
wk={s: vrw.Wiki(f"{R}/series/{s}/facts.db") for s in ("marvel","mcu")}
P={}
for s in ("marvel","mcu"):
    for l in open(f"{R}/series/{s}/training/labels/big_in.jsonl"):
        d=json.loads(l); P[d["id"]]=d["messages"][1]["content"].split("Passage:\n",1)[1]
order=br2.order(); bnum={i:n+1 for n,i in enumerate(order)}
cursor=int(open(f"{B}/review_cursor_v2.txt").read().strip())
rows=[json.loads(l) for l in open(f"{B}/labels_v2.jsonl") if l.strip()]
AUD=br2.audit2()
stat=collections.Counter(); reviewed=[]
for r in rows:
    w=P.get(r["id"]); wiki=wk.get(r.get("series","marvel"), wk["marvel"])
    if not w: continue
    df=[{k:v for k,v in d.items() if k!="why"} for d in r.get("dropped_facts") or []]
    keep_f, moved_ev = fg.split_event_facts(df)
    fk,_=ls.fact_gate_keep(keep_f, w, wiki)
    ev=[{k:d.get(k) for k in ("quote","subject","verb","object")} for d in (r.get("dropped") or [])] + moved_ev
    ek=[]
    for e in ev:
        k,_=ls.gate([e], w, wiki); ek+=k
    tk,_=ls.tag_gate_keep([{k:v for k,v in d.items() if k!="why"} for d in r.get("dropped_tags") or []], w)
    have_t={(t.get("tag"),t.get("quote")) for t in r.get("tags") or []}; tk=[t for t in tk if (t.get("tag"),t.get("quote")) not in have_t]
    have_e={(e.get("subject"),e.get("verb"),e.get("object")) for e in r.get("events") or []}
    have_f={(f.get("subject"),f.get("relation"),f.get("object")) for f in r.get("facts") or []}
    ek=[e for e in ek if (e["subject"],e["verb"],e["object"]) not in have_e]
    fk=[f for f in fk if (f.get("subject"),f.get("relation"),f.get("object")) not in have_f]
    if not (ek or fk or tk): continue
    b=bnum.get(r["id"],0)
    side="unviewed" if b>cursor else "reviewed"
    stat[side+"_ev"]+=len(ek); stat[side+"_fa"]+=len(fk); stat[side+"_tg"]+=len(tk)
    if side=="unviewed" and "--write" in sys.argv:
        r["events"]=(r.get("events") or [])+ek; r["facts"]=(r.get("facts") or [])+fk; r["tags"]=(r.get("tags") or [])+tk
        old=r.get("recovered_2026_10_13") or {}
        r["recovered_2026_10_13"]={k:old.get(k,0)+n for k,n in (("events",len(ek)),("facts",len(fk)),("tags",len(tk)))}
    elif side=="reviewed":
        a=AUD.get(r["id"])
        if a:
            ae={(e.get("subject"),e.get("verb"),e.get("object")) for e in a.get("events") or []}
            af={(f.get("subject"),f.get("relation"),f.get("object")) for f in a.get("facts") or []}
            ek=[e for e in ek if (e["subject"],e["verb"],e["object"]) not in ae]
            fk=[f for f in fk if (f.get("subject"),f.get("relation"),f.get("object")) not in af]
        stat["reviewed_after_audit_ev"]+=len(ek); stat["reviewed_after_audit_fa"]+=len(fk)
        if ek or fk: reviewed.append({"id":r["id"],"b":b,"events":ek,"facts":fk,"tags":tk})
print(dict(stat), "cursor", cursor)
if "--write" in sys.argv:
    bak=f"{B}/labels_v2.jsonl.bak-pre-recovery-2026-10-13"
    import os
    k=2
    while os.path.exists(bak+(f".{k}" if k>1 else "")) and k<50: k+=1
    if os.path.exists(bak): bak+=f".{k}"
    shutil.copy(f"{B}/labels_v2.jsonl", bak); print("backup", bak)
    with open(f"{B}/labels_v2.jsonl","w") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False)+"\n")
    with open(f"{B}/recovered_reviewed_2026-10-13.jsonl","w") as f:
        for x in reviewed: f.write(json.dumps(x, ensure_ascii=False)+"\n")
    print("written; reviewed list:", len(reviewed))
