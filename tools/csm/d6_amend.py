"""D6-close council amendment (exit 1): re-file the 48 EXTRACTION-GATED
dim+abl rows as a D7 retrieval-ranking named limit. Surgical line-scoped
string replacement: only lines whose row id is in the 48-set are touched;
all other lines stay byte-identical. Verifies afterwards."""
import json

PATH = "/home/goblin/ScriptEngine/reports/csm/census_v1_floor_triage.jsonl"

REPS = [
    ('"triage": "EXTRACTION-GATED (fresh triage, p23 receipts)"',
     '"triage": "NAMED-LIMIT (D6-close council amendment 2026-09-18: qa-door retrieval ranking; extraction closer failed 0/48)"'),
    ('"root_cause": "extraction-gated (D6 set/relation/mechanism completeness)"',
     '"root_cause": "retrieval-ranking (D6-close finding): character-card dominance over arc Synopsis chunks in the qa door; events table invisible to qa bundles (0/69 served texts with event markers; events_order_enabled() OFF by default, narrative.py L77-85)"'),
    ('"owning_phase": "Phase-2 (D6)"',
     '"owning_phase": "D7 (ranking leg)"'),
    ('"closer": "D6 extraction campaign"',
     '"closer": "D7 ranking-leg fix (character-card vs arc-Synopsis ranking)"'),
    ('"lever": "D6 extraction track"',
     '"lever": "D7 ranking track"'),
    ('"retest_trigger": "re-run p23 census after D6"',
     '"retest_trigger": "re-grade on D7 ranking fix"'),
    ('"extraction_gated": true',
     '"extraction_gated": false'),
]

lines = open(PATH, encoding="utf-8").read().splitlines()
targets = set()
for line in lines:
    r = json.loads(line)
    if r.get("bucket") in ("dim", "abl") and r.get("triage") == "EXTRACTION-GATED (fresh triage, p23 receipts)":
        targets.add(r["id"])
assert len(targets) == 48, len(targets)

out = []
touched = 0
for line in lines:
    rid = json.loads(line)["id"]
    if rid in targets:
        for old, new in REPS:
            assert old in line, (rid, old)
            line = line.replace(old, new)
        touched += 1
    out.append(line)
open(PATH, "w", encoding="utf-8").write("\n".join(out) + "\n")

# verify
rows = [json.loads(l) for l in open(PATH, encoding="utf-8") if l.strip()]
assert len(rows) == 233
am = [r for r in rows if r["id"] in targets]
assert len(am) == 48
from collections import Counter
print("triage:", Counter(r["triage"] for r in am))
print("owning:", Counter(r["owning_phase"] for r in am))
print("closer:", Counter(r["closer"] for r in am))
print("lever:", Counter(r["lever"] for r in am))
print("gated:", Counter(r["extraction_gated"] for r in am))
rest = [r for r in rows if r["id"] not in targets]
assert not any(r.get("owning_phase") == "D7 (ranking leg)" for r in rest)
assert not any("NAMED-LIMIT (D6-close" in (r.get("triage") or "") for r in rest)
print("touched rows:", touched, "| total rows:", len(rows), "| amendment OK")
