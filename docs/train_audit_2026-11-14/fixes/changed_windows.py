#!/usr/bin/env python3
"""Every training window this audit changed: the gold audit records appended after the pre-audit backup
(4,216 lines), compared with the record each window had before. Writes fixes/changed_windows.json and prints
totals.   python3 fixes/changed_windows.py
"""
import collections, json, re, glob
G = "/home/goblin/ScriptEngine/series/universal/training/big/gold_v2/"
BASE = 4216
bnum = {json.loads(l)["id"]: i for i, l in enumerate(open(G + "gold_in.jsonl"), 1)}
lines = [json.loads(l.strip("\x00\n ")) for l in open(G + "gold_audit_v2.jsonl") if l.strip("\x00\n ")]
train = {json.loads(l)["id"]: json.loads(l) for l in open("/home/goblin/student_runs_local/jjk_side/s2data/train.jsonl")}
old = {}
for r in lines[:BASE]:
    if r.get("void"): old.pop(r["id"], None)
    else: old[r["id"]] = r
new = dict(old)
for r in lines[BASE:]: new[r["id"]] = r
fixfile = collections.defaultdict(list)
for p in sorted(glob.glob("fixes/G1*.txt")) + [G + "fixes/G133.txt"]:
    m = re.search(r"(G\d+)\.txt$", p)
    if not m: continue
    g = m.group(1)
    for m in re.finditer(r"^@(\d+)", open(p).read(), re.M): fixfile[int(m.group(1))].append(g)
key = {"events": lambda e: (e["subject"], e["verb"], e.get("object")),
       "facts": lambda f: (f["subject"], f["relation"], f.get("object"), f.get("modality") or "actual", f["quote"]),
       "tags": lambda t: (t["tag"], t["quote"])}
out = []; T = collections.Counter()
for i in {r["id"] for r in lines[BASE:]}:
    o, n = old[i], new[i]; d = {}
    for k in key:
        a = {key[k](x) for x in o[k]}; b = {key[k](x) for x in n[k]}
        d[k] = [len(b - a), len(a - b)]; T[k + " added"] += len(b - a); T[k + " removed"] += len(a - b)
    # an event whose quote moved (same subject, verb, object) changes which sentence the per-line target pins it to
    oq = {key["events"](e): e["quote"] for e in o["events"]}; nq = {key["events"](e): e["quote"] for e in n["events"]}
    requoted = sum(1 for k in nq if k in oq and oq[k] != nq[k]); T["events re-quoted"] += requoted
    if not any(sum(v) for v in d.values()) and not requoted: continue
    b = bnum[i]
    out.append({"b": b, "id": i, "series": train[i]["series"] if i in train else None, "page": o.get("page") or (train[i]["page"] if i in train else None),
                "in_train_2150": i in train, "fix_files": sorted(set(fixfile.get(b, []))),
                "events_added": d["events"][0], "events_removed": d["events"][1], "facts_added": d["facts"][0], "facts_removed": d["facts"][1],
                "tags_added": d["tags"][0], "tags_removed": d["tags"][1], "events_requoted": requoted})
out.sort(key=lambda r: r["b"])
json.dump(out, open("fixes/changed_windows.json", "w"), ensure_ascii=False, indent=0)
print(len(out), "windows changed;", sum(r["in_train_2150"] for r in out), "of them in the 2,150;", dict(T))
print("by series:", dict(collections.Counter(r["series"] for r in out)))
print("windows whose events changed:", sum(1 for r in out if r["events_added"] or r["events_removed"]))
