"""Build a battle coverage bank for any series that records fights.

Gold is transcribed from the wiki's own battle infobox -- who fought, and what
each side used -- read through the series' declared `battle_relations`. A
primary source, but nobody researched it independently, so it is filed under `_`
where `load_all` skips it: this measures whether retrieval reaches what
ingestion stored, and must not move the headline number."""
import json, sys, collections
sys.path.insert(0, r"E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from scriptengine.config import series_paths, load_overrides
from scriptengine.stores.facts import FactStore
from scriptengine.retrieve import semantics as ontology
from scriptengine.retrieve.roster import battle_relations

series = sys.argv[1]
root = r"E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine"
paths = series_paths(series); ov = load_overrides(paths)
pairs = battle_relations(ov)
st = FactStore(paths.facts_db)

existing = json.loads(open(f"{root}/questions/{series}.json", encoding="utf-8").read())
existing = existing["questions"] if isinstance(existing, dict) else existing
already = {q["question"].strip().lower() for q in existing}

battles = [r["title"] for r in st.connection.execute(
    "SELECT title FROM documents WHERE page_type LIKE '%battle%' COLLATE NOCASE")]
rec = {}
for b in battles:
    node = st.node_by_name(b)
    if not node: continue
    d = collections.defaultdict(list)
    for r in st.connection.execute(
        "SELECT e.relation, n.name FROM edges e JOIN nodes n ON n.id=e.target_id"
        " WHERE e.source_id=? AND e.relation != 'mentions'", (node["id"],)):
        d[(r["relation"] or "").lower()].append(r["name"])
    rec[b] = d

def is_char(n): return ontology.semantic_type(st, n, ov) == "character"

fights = collections.defaultdict(list)
for b, d in rec.items():
    for side, _ in pairs:
        for who in d.get(side, []):
            if is_char(who): fights[who].append(b)

qs, n = [], 0
def add(q, subject, answer, note):
    global n
    if q.strip().lower() in already or len(answer) < 2: return
    n += 1
    qs.append({"id": f"{series}-cov-{n:02}", "kind": "set", "question": q,
               "subject": subject, "scope": "closed", "expect_mode": "roster",
               "tier": "wiki", "verified": "2026-08-16", "sources": [], "note": note,
               "answer": [{"item": a, "aliases": []} for a in answer]})

for who, bs in sorted(fights.items(), key=lambda kv: -len(kv[1]))[:12]:
    add(f"Every battle of {who}", who, sorted(set(bs)),
        f"Transcribed from the side fields of {len(set(bs))} battle pages.")
for b, d in rec.items():
    for side, abil in pairs:
        who = [c for c in d.get(side, []) if is_char(c)]
        tech = d.get(abil, [])
        if len(who) == 1 and len(tech) >= 2:
            add(f"Which techniques did {who[0]} use in {b}?", who[0], list(dict.fromkeys(tech)),
                f"Transcribed from `{abil}` on the `{b}` page.")

out = f"{root}/questions/_{series}_battles.json"
json.dump({"series": series, "questions": qs}, open(out, "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print(f"[{series}] battle pages={len(rec)}  relations={pairs}")
print(f"  wrote {len(qs)} questions -> {out.split('/')[-1]}")
st.close()
