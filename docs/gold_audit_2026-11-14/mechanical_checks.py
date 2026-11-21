#!/usr/bin/env python3
"""Mechanical checks on a v2 gold file: what a script can prove wrong without reading for meaning.

    python mechanical_checks.py --tools <repo>/tools GOLD.jsonl [GOLD2.jsonl ...] [--examples 4]
"""
import argparse, collections, json, re, sys

ap = argparse.ArgumentParser()
ap.add_argument("--tools", required=True); ap.add_argument("files", nargs="+"); ap.add_argument("--examples", type=int, default=3)
a = ap.parse_args()
sys.path.insert(0, a.tools); sys.path.insert(0, a.tools + "/train")
import eval_extraction as ee, score_layers_v2 as sl  # noqa: E402

VERBS = {"fought", "defeated", "killed", "captured", "escaped", "saved", "betrayed", "sealed", "met", "arrived", "departed", "awakened"}
RELS = {r for g in sl.GROUPS.values() for r in g}
TAGS = {"dialogue", "list_header", "production", "citation", "apposition", "attire", "capability", "deictic", "below_floor", "no_doer", "crowd_end", "no_relation"}
MODS = {"actual", "planned", "attempted", "ordered", "controlled", "claimed", "dreamed", "hypothetical"}
CERT = {"stated", "reported", "apparent", "denied"}
CANON = {"mcu", "comics", "alternate", "anime", "production", None}
EVENT_FORMS = re.compile(r"^(fought|fight(s|ing)?|defeat(s|ed|ing)?|kill(s|ed|ing)?|captur(e|es|ed|ing)|escap(e|es|ed|ing)|sav(e|es|ed|ing)|betray(s|ed|ing)?|seal(s|ed|ing)?|met|meet(s|ing)?|arriv(e|es|ed|ing)|depart(s|ed|ing)?|awaken(s|ed|ing)?)$", re.I)
PRON = {"he", "she", "they", "him", "her", "them", "it", "his", "hers", "their", "who", "himself", "herself", "themselves", "someone", "everyone", "others", "the others", "the group", "the two", "both"}
sents = lambda p: [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", p) if len(s.strip()) >= 20]

for path in a.files:
    rows = [json.loads(l) for l in open(path)]
    C = collections.Counter(); ex = collections.defaultdict(list)
    def hit(k, r, x):
        C[k] += 1
        if len(ex[k]) < a.examples: ex[k].append(f"[{r['page']}] {json.dumps({kk: x.get(kk) for kk in ('subject','verb','relation','object','tag','modality','asserted_by','quote') if kk in x}, ensure_ascii=False)[:230]}")
    n_ev = n_fa = n_tg = n_sent = n_cov = 0
    for r in rows:
        p = r["passage"]; low = (p + " " + r["page"]).lower()
        seen = set()
        for layer in ("events", "facts", "tags"):
            for x in r[layer]:
                q = (x.get("quote") or "")
                if q not in p: hit("quote not word for word in the passage", r, x)
                elif re.search(r"[.!?]\s+[A-Z\"]", q.strip()[:-1]) and layer != "tags": hit("quote runs across a sentence boundary", r, x)
                key = (layer, x.get("subject"), x.get("verb") or x.get("relation") or x.get("tag"), x.get("object"), x.get("modality"), q if layer == "tags" else None)
                if key in seen: hit("duplicate row", r, x)
                seen.add(key)
        for x in r["events"]:
            n_ev += 1
            if x.get("verb") not in VERBS: hit("event verb not in the list", r, x)
            if x.get("verb") == "awakened" and x.get("object"): hit("awakened with an object", r, x)
            if x.get("verb") != "awakened" and not x.get("object"): hit("event with no object", r, x)
            if x.get("object") and ee.same(x.get("subject"), x.get("object")): hit("event subject and object are the same name", r, x)
        for x in r["facts"]:
            n_fa += 1
            rel = x.get("relation")
            if rel not in RELS: hit("fact relation not in the list", r, x)
            if (x.get("modality") or "actual") not in MODS or (x.get("certainty") or "stated") not in CERT or x.get("canon") not in CANON: hit("illegal modality / certainty / canon", r, x)
            if rel == "other_verb":
                o = str(x.get("object") or "")
                if EVENT_FORMS.match(o): hit("other_verb used for an event verb", r, x)
                if o and o.lower() not in (x.get("quote") or "").lower(): hit("other_verb verb not in its quote", r, x)
            elif x.get("object") and ee.same(x.get("subject"), x.get("object")): hit("fact subject and object are the same name", r, x)
            if (x.get("modality") or "actual") == "actual" and x.get("asserted_by"): hit("actual modality with asserted_by set", r, x)
        for layer in ("events", "facts"):
            for x in r[layer]:
                for k in ("subject", "object"):
                    v = x.get(k)
                    if not v or (k == "object" and x.get("relation") == "other_verb"): continue
                    if v.strip().lower() in PRON: hit("an end is a pronoun or a group word", r, x)
                    elif not any(w.lower() in low for w in re.findall(r"[A-Za-z][A-Za-z'\-]{3,}", v)) and v.lower() not in low: hit("an end's name appears nowhere in the passage or page title", r, x)
        for x in r["tags"]:
            n_tg += 1
            if x.get("tag") not in TAGS: hit("tag not in the list", r, x)
            q = (x.get("quote") or "").strip()
            if q and any((y.get("quote") or "").strip() and ((y["quote"].strip() in q) or (q in y["quote"].strip())) for l2 in ("events", "facts") for y in r[l2]):
                hit("a tag and a row on the same text", r, x)
        qs = [(x.get("quote") or "").strip() for l2 in ("events", "facts", "tags") for x in r[l2]]
        for s in sents(p):
            n_sent += 1
            if any(q and (q in s or s in q) for q in qs): n_cov += 1
            else:
                C["sentence with no row and no tag"] += 1
                if len(ex["sentence with no row and no tag"]) < a.examples: ex["sentence with no row and no tag"].append(f"[{r['page']}] {s[:200]}")
    print(f"\n== {path.split('/')[-2]}/{path.split('/')[-1]}: {len(rows)} windows, {n_ev} events, {n_fa} facts, {n_tg} tags, {n_sent} sentences ({n_cov / max(n_sent,1):.1%} covered)")
    for k, v in C.most_common():
        print(f"  {v:4d}  {k}")
        for e in ex[k]: print(f"          {e}")
    if not C: print("  no mechanical defect found")
