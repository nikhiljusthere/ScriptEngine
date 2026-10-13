import json,re,sys
R="/home/goblin/ScriptEngine"
P={}
for s in ("marvel","mcu"):
    for l in open(f"{R}/series/{s}/training/labels/big_in.jsonl"):
        d=json.loads(l); P[d["id"]]=d["messages"][1]["content"].split("Passage:\n",1)[1]
rows=[json.loads(l) for l in open("/home/goblin/ScriptEngine/series/universal/training/big/audit_27b_2026-10-13/stage4_recovered_screen.jsonl")]
acc=[r for r in rows if r.get("verdict")=="ACCEPT"]
acc.sort(key=lambda r:r["b"])
a,b=int(sys.argv[1]),int(sys.argv[2])
for i,r in enumerate(acc[a:b],a):
    x=r["row"]; w=P[r["id"]]; q=x.get("quote") or ""
    k=w.find(q); s=w[max(0,w.rfind(". ",0,max(k,0))+2 if k>0 else 0):][:0]
    st=max(0,w.rfind(". ",0,k)+2) if k>0 else 0; en=w.find(". ",k+len(q)); en=len(w) if en<0 else en+1
    rel=x.get("verb") or x.get("relation"); mod=x.get("modality") or ""
    print(f"[{i}] b{r['b']} {r['kind'][0].upper()} {x.get('subject')}|{rel}|{x.get('object') or '-'}"+(f"|{mod}" if mod and mod!='actual' else "")+f"  q={q[:70]!r}")
    print("     S:", w[st:en][:260].replace("\n"," "))
print(len(acc))
