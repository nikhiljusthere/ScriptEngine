#!/usr/bin/env python3
"""Script-provable checks on the fact layer of the 2,150 training windows, written for this audit (it imports
nothing from the project's gate). Reads the latest gold record per window from gold_audit_v2.jsonl.

  M1  other_verb row whose verb is not a word of its own quote (catalog A88)
  M2  an end (event subject/object, fact subject) with no word in the window (outside name: A112/A130)
  M3  a quote that is not in the window word for word
  M4  a sentence no row and no tag touches
  M5  a quote that runs over a sentence boundary
  M6  the same fought/met pair written twice in a window

    python3 facts/fact_layer_checks.py > facts/fact_layer_checks.txt     (also writes facts/mech_candidates.json)
"""
import collections, json, re
G = "/home/goblin/ScriptEngine/series/universal/training/big/gold_v2/"
TRAIN = "/home/goblin/student_runs_local/jjk_side/s2data/train.jsonl"
bnum = {json.loads(l)["id"]: i for i, l in enumerate(open(G + "gold_in.jsonl"), 1)}
hist = {}
for l in open(G + "gold_audit_v2.jsonl"):
    l = l.strip("\x00\n ")
    if l:
        r = json.loads(l)
        if r.get("void"):
            if hist.get(r["id"]): hist[r["id"]].pop()
        else: hist.setdefault(r["id"], []).append(r)
train = [json.loads(l) for l in open(TRAIN)]
sents = {json.loads(l)["id"]: json.loads(l)["sentences"] for l in open("blind/train_all_input.jsonl")}
norm = lambda s: re.sub(r"\s+", " ", s or "").strip().lower()
C = collections.Counter(); out = collections.defaultdict(list)


def words(s):
    return [w for w in re.findall(r"[^\W\d_]+", s.lower()) if len(w) >= 3]


for r in train:
    i = r["id"]; b = bnum.get(i); g = hist.get(i, [None])[-1]
    if g is None: C["no gold record"] += 1; continue
    text = norm(r["passage"]); C["windows"] += 1
    ev, fa, tg = g["events"], g["facts"], g["tags"]
    C["events"] += len(ev); C["facts"] += len(fa); C["tags"] += len(tg)
    spans = []
    for kind, rows in (("event", ev), ("fact", fa), ("tag", tg)):
        for x in rows:
            q = norm(x.get("quote"))
            p = text.find(q) if q else -1
            if p < 0:
                C["M3"] += 1; out["M3"].append([b, i, kind, x]); continue
            spans.append((p, p + len(q), kind))
    # sentence spans
    ss = sents.get(i, {}); sspan = {}
    pos = 0
    for n, s in (ss.items() if isinstance(ss, dict) else enumerate(ss, 1)):
        p = text.find(norm(s), pos)
        if p < 0: p = text.find(norm(s))
        if p >= 0:
            sspan[n] = (p, p + len(norm(s))); pos = p + 1
    for n, (a_, z_) in sspan.items():
        s = ss[n] if isinstance(ss, dict) else ss[int(n) - 1]
        if len(s) < 12 or not re.search(r"[A-Za-z]{3}", s): continue
        C["sentences"] += 1
        if not any(p < z_ and q > a_ for p, q, _ in spans):
            C["M4"] += 1; out["M4"].append([b, i, n, s])
    for p, q, kind in spans:
        hit = [n for n, (a_, z_) in sspan.items() if p < z_ and q > a_ and (z_ - a_) >= 12]
        if len(hit) > 1 and kind != "tag":
            C["M5"] += 1; out["M5"].append([b, i, kind, text[p:q]])
    for f in fa:
        if f["relation"] == "other_verb":
            C["other_verb rows"] += 1
            v = norm(f.get("object")); q = norm(f.get("quote"))
            if v and not re.search(r"(?<!\w)" + re.escape(v) + r"(?!\w)", q):
                C["M1"] += 1; out["M1"].append([b, i, f["subject"], v, f.get("quote"), f.get("modality")])
    ends = [("event", e["subject"], e) for e in ev] + [("event", e.get("object"), e) for e in ev] + [("fact_subject", f["subject"], f) for f in fa]
    for kind, name, row in ends:
        if not name: continue
        C["ends"] += 1
        if norm(name) in text: continue
        w = words(name)
        if w and not any(re.search(r"(?<!\w)" + re.escape(x), text) for x in w):
            C["M2 no word in window"] += 1; out["M2"].append([b, i, kind, name, row.get("verb") or row.get("relation"), row.get("quote")])
        else:
            C["M2b only part of the name in window"] += 1
    seen = collections.Counter()
    for e in ev:
        if e["verb"] in ("fought", "met"):
            seen[(e["verb"], frozenset((norm(e["subject"]), norm(e.get("object")))))] += 1
    for k, n in seen.items():
        if n > 1: C["M6"] += 1; out["M6"].append([b, i, k[0], sorted(k[1])])
for k, v in sorted(C.items()): print(f"{k:40s} {v}")
json.dump(out, open("facts/mech_candidates.json", "w"), ensure_ascii=False, indent=0)
for k in ("M1", "M2", "M3", "M5", "M6"):
    print(f"\n## {k}: {len(out[k])}")
    for x in out[k][:400]: print("  ", json.dumps(x, ensure_ascii=False)[:330])
print(f"\n## M4: {len(out['M4'])} (first 60)")
for x in out["M4"][:60]: print("  ", json.dumps(x, ensure_ascii=False)[:330])
