"""Torture / mind-control candidates (owner rulings 2026-11-04). Writes rulings_2026-11-04/tc_<set>.json."""
import json, os, re, sys
sys.path.insert(0, "/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags/tools/train")
import big_review_v2 as bv
SET = os.environ.get("BV2_SET", "big")
SPLIT = re.compile(r"(?<=[.!?])[\"')\]]*\s+(?=[A-Z\"'(\[])|\n+")
TORT = re.compile(r"\b(tortur\w*|torment\w*|dissect\w*|vivisect\w*|brutali[sz]\w*|interrogat\w*|"
                  r"experiment\w* on|beat(?:s|en|ing)? (?:\w+ )?(?:while|as) (?:he|she|they) (?:was|were) (?:chained|tied|bound|held))\b", re.I)
CAPTIVE = re.compile(r"\b(captive|prisoner|chained|shackled|tied (?:up|down)|bound|imprisoned|held)\b", re.I)
CTRL = re.compile(r"\b(mind[- ]control\w*|under (?:\w+'s |the |his |her |their )?(?:mental )?control|controlled by|"
                  r"possessed by|possessing (?:him|her|them|[A-Z]\w+)|possession of (?:his|her|their|[A-Z]\w+'s) (?:body|mind)|took possession|brainwash\w*|hypnoti[sz]\w*|enthrall\w*|mesmeri[sz]\w*|thrall|"
                  r"puppet\w*|programmed to|mind[- ]wiped|trigger words|under (?:the )?influence|took control of|"
                  r"takes? control of|taken over|bewitched|entranced)\b", re.I)
def sents(t): return [s for s in SPLIT.split(t) if s.strip()]
def sent_of(ss, q):
    for i, s in enumerate(ss):
        if q[:40] in s: return i
    return None
ids, a2, pas = bv.order(), bv.audit2(), bv.br.passages()
out = {}
for b, wid in enumerate(ids, 1):
    rec = a2.get(wid)
    if not rec: continue
    text = pas[wid]; ss = sents(text); hits = []
    for e in rec["events"]:
        if e["verb"] not in ("fought", "defeated", "killed", "captured", "sealed", "wounded"): continue
        i = sent_of(ss, e["quote"])
        win = " ".join(ss[max(0, (i or 0) - 1):(i or 0) + 2]) if i is not None else e["quote"]
        own = ss[i] if i is not None else e["quote"]
        if e["verb"] in ("fought", "defeated") and TORT.search(own):
            hits.append(f"TORT: {e['subject']}|{e['verb']}|{e['object']}")
        elif e["verb"] in ("fought", "defeated") and CAPTIVE.search(own) and re.search(r"\b(beat|hit|punch|whip|cut|burn|shock)\w*", own, re.I):
            hits.append(f"TORT?: {e['subject']}|{e['verb']}|{e['object']}")
        if CTRL.search(win):
            hits.append(f"CTRL: {e['subject']}|{e['verb']}|{e['object']}")
    if hits: out[b] = hits
D = "/home/goblin/ScriptEngine/series/universal/training/big/rulings_2026-11-04/"
json.dump(out, open(D + f"tc_{SET}.json", "w"), indent=0)
from collections import Counter
c = Counter(h.split(":")[0] for v in out.values() for h in v)
print(SET, "windows", len(out), dict(c))
