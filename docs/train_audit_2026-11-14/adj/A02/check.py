import json
D="/home/goblin/ScriptEngine/.claude/worktrees/9b-model-extraction-analysis-a7e9c9/docs/train_audit_2026-11-14/adj/"
W={json.loads(l)["b"]:json.loads(l) for l in open(D+"A02_adj_input.jsonl")}
b=None
for line in open(D+"A02_fix.txt"):
    line=line.rstrip("\n")
    if line.startswith("@"): b=int(line[1:].split()[0]); continue
    if line.startswith("+ "):
        p=line[2:].split("|"); q=p[3]
        ok=any(q in s for s in W[b]["sentences"].values()) and len(q)>=12
        print(b,"ADD",p[:3],"quote ok" if ok else "QUOTE BAD")
    elif line.startswith("f- "):
        p=line[3:].split("|")
        ok=any([f[0],f[1],f[2] or "-"]==p for f in W[b]["gold_facts"])
        print(b,"FDEL",p,"match" if ok else "NO MATCH")
