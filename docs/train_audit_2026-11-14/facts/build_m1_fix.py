#!/usr/bin/env python3
"""Left out on purpose: b1538 Reggie told (a second "Reggie tells" row cannot exist beside the first: the
writer keeps one fact per subject, relation, object and modality) and b3110 Genus states ("According to
Genus": the sentence has no verb of his; needs a ruling).

Fix file for the A88 rows (other_verb whose verb is not a word of its quote). The literal form of each row
was chosen by reading the quote (table below, keyed by window number, subject, old verb); the script only
carries the row's other fields over and reports a clash with an existing row of the same subject and verb.

    python3 facts/build_m1_fix.py > fixes/G135.txt
"""
import collections, json, re, sys
G = "/home/goblin/ScriptEngine/series/universal/training/big/gold_v2/"
bid = {i: json.loads(l)["id"] for i, l in enumerate(open(G + "gold_in.jsonl"), 1)}
hist = {}
for l in open(G + "gold_audit_v2.jsonl"):
    l = l.strip("\x00\n ")
    if l:
        r = json.loads(l)
        if r.get("void"):
            if hist.get(r["id"]): hist[r["id"]].pop()
        else: hist.setdefault(r["id"], []).append(r)
NEW = {  # (b, subject, old verb) -> new verb | ("quote", new verb, new quote) | "DROP"
 (1023, "Beerus", "tries"): "try", (1295, "Dagon", "disappear"): "disappears", (1551, "Choso", "asked"): "ask",
 (1694, "Hakari", "told"): "tells", (1085, "Ogi Zenin", "said"): "saying", (1481, "Nanami", "surprised"): "catching",
 (2981, "Kaidou", "want"): "wants", (2981, "Kaidou", "asked"): "asks",
 (1376, "Nanami", "agrees"): ("quote", "agree", "Nanami will agree with him, which Nanami actually does"),
 (647, "Power", "states"): "DROP",
 (3261, "Royal Ripper", "threaten"): "threatening", (2900, "Trebol", "saw"): "see", (1454, "Satoru", "told"): "tell",
 (1454, "Megumi Fushiguro", "said"): "says", (1579, "Mei Mei", "told"): "tells", (1118, "Mai", "hid"): "hides",
 (1734, "Maki", "told"): "tells", (3066, "Erika", "told"): "tell", (1593, "Yuji", "held"): "holding",
 (1593, "Yuji", "asked"): "asking", (1111, "Gojo", "said"): "saying", (1111, "Gojo", "told"): "telling",
 (1724, "Maki", "send"): "sends", (1724, "Yuji", "restrain"): "restrains", (1724, "Sukuna", "tell"): "tells",
 (1724, "Maki", "kick"): "kicks", (1724, "Maki", "express"): "expresses", (2846, "Vegapunk", "made"): "making",
 (1104, "Usami", "offer"): "offered", (9, "Casca", "sees"): "see", (520, "Asa", "turn"): "turning",
 (1665, "Hazenoki", "deny"): "denied", (2821, "Shimotsuki Yasuie", "encourage"): "encouraged",
 (1224, "Kashimo", "hits"): "hit", (1547, "Mei Mei", "told"): "tells",
 (1276, "Hanami", "attack"): ("quote", "attack", "attack with his technique, but Jogo tells him not to do it"),
 (1442, "Mei Mei", "asked"): "asks", (1695, "Yorozu", "told"): "telling", (1385, "Sukuna", "say"): "says",
 (1385, "Sukuna", "blitz"): "blitzes", (1523, "Kiyotaka Ijichi", "told"): "telling", (1414, "Rika", "eat"): "eaten",
 (3264, "Zombieman", "told"): "tells", (1543, "Megumi", "told"): "tells", (1550, "Ogami", "spoke"): "speaking",
 (1621, "Sukuna", "asks"): "asked", (1621, "Yorozu", "asks"): "asked", (1494, "Maki", "use"): "used",
 (304, "Karin", "tell"): "tells", (2826, "Miss Valentine", "boast"): "boasting",
 (1181, "Ijichi", "involve"): "involved", (1718, "Maki", "threw"): "throws", (1100, "Geto", "tell"): "tells",
 (2882, "Luffy", "ate"): "eating", (2882, "Chopper", "ate"): "eating", (1634, "Masamichi Yaga", "punish"): "punishes",
 (3055, "Bartolomeo", "drank"): "drinking", (3173, "Void", "notes"): "noting", (643, "Fami", "reveals"): "DROP",
 (1710, "Naoya", "asks"): "asking",
}
norm = lambda s: re.sub(r"\s+", " ", s or "").strip().lower()
byb = collections.defaultdict(list)
for k, v in NEW.items(): byb[k[0]].append((k, v))
problems = []
for b in sorted(byb):
    g = hist[bid[b]][-1]; lines = []
    have = {(f["subject"], norm(f.get("object")), f.get("modality") or "actual") for f in g["facts"] if f["relation"] == "other_verb"}
    for (bb, subj, old), new in byb[b]:
        rows = [f for f in g["facts"] if f["relation"] == "other_verb" and f["subject"] == subj and norm(f.get("object")) == old
                and not re.search(r"(?<!\w)" + re.escape(old) + r"(?!\w)", norm(f["quote"]))]
        if len(rows) != 1: problems.append(f"b{b} {subj} {old}: {len(rows)} matching rows"); continue
        f = rows[0]; mod = f.get("modality") or "actual"
        lines.append(f"f- {subj}|other_verb|{f['object']}")
        # `f-` removes every row with this subject, relation and object whatever its modality: put the others back
        for o in g["facts"]:
            if o is not f and o["relation"] == "other_verb" and o["subject"] == subj and o.get("object") == f["object"]:
                t = f"|{o.get('modality') or 'actual'}|{o.get('certainty') or 'stated'}|{o.get('asserted_by') or ''}".rstrip("|")
                lines.append(f"f+ {subj}|other_verb|{o['object']}|{o['quote']}{t}")
        if new == "DROP": continue
        verb, quote = (new[1], new[2]) if isinstance(new, tuple) else (new, f["quote"])
        if not re.search(r"(?<!\w)" + re.escape(verb) + r"(?!\w)", norm(quote)): problems.append(f"b{b} {subj}: '{verb}' not in quote")
        if verb != old and (subj, verb, mod) in have: problems.append(f"b{b} {subj} {old}->{verb} ({mod}): CLASH with an existing row")
        have.add((subj, verb, mod))
        tail = f"|{mod}|{f.get('certainty') or 'stated'}|{f.get('asserted_by') or ''}".rstrip("|")
        lines.append(f"f+ {subj}|other_verb|{verb}|{quote}{tail}")
    print(f"@{b} gold: 2026-11-14 audit, A88 / B.3 -- the other_verb verb is the word in its quote\nkeep")
    print("\n".join(lines)); print()
for p in problems: print("PROBLEM", p, file=sys.stderr)
print(f"{len(byb)} windows, {len(NEW)} rows, {len(problems)} problems", file=sys.stderr)
