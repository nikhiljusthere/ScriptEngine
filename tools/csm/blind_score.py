"""Blind fresh-set scorer (Step 0): grades reports/csm/blind_fresh_d7.jsonl
through the EXACT p23 path (in-process context_endpoint, mode qa,
subject None) and writes blind_fresh_d7_results.jsonl beside it.
Measurement only. Exit 0 always on clean run; exit 3 on harness error."""
import json
import os
import sys
import time

os.environ.setdefault("CENSUS_DEVICE", "cuda")
os.environ.setdefault("SCRIPTENGINE_DEVICE", os.environ["CENSUS_DEVICE"])
sys.path.insert(0, "/home/goblin/ScriptEngine")
from tools.csm.p23_grader import grade_item  # noqa: E402 same instrument

ROOT = "/home/goblin/ScriptEngine/reports/csm/"
items = [json.loads(l) for l in open(ROOT + "blind_fresh_d7.jsonl") if l.strip()]
t0 = time.time()
rows = [grade_item(it, "qa") for it in items]
errs = sum(1 for r in rows if r.get("verdict") == "ERROR")
greens = sum(1 for r in rows if r.get("verdict") == "MECH_GREEN")
open(ROOT + "blind_fresh_d7_results.jsonl", "w").write(
    "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
print(json.dumps({"blind": f"{greens}/{len(rows)}", "errors": errs,
                  "seconds": round(time.time() - t0, 1)}))
for r in rows:
    if r.get("verdict") != "MECH_GREEN":
        print("RED:", r["id"], "| missing:", r.get("missing"))
