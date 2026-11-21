#!/usr/bin/env python3
"""Run big_review_v2's gated `fix` on a COPY of the gold audit file, so nothing real is written.

    BV2_SET=gold SCRIPTENGINE_ROOT=/home/goblin/ScriptEngine <main venv python> dry_run_fix.py <tools/train dir> FIXFILE OUT_COPY
Prints the tool's own FIXED / REFUSED / UNMATCHED lines, then the resulting rows of each window.
"""
import json, shutil, sys
tools, fixfile, out = sys.argv[1:4]
sys.path.insert(0, tools)
import big_review_v2 as bv
shutil.copyfile(bv.AUDIT2, out)
n0 = sum(1 for _ in open(out))
bv.AUDIT2 = type(bv.AUDIT2)(out)
bv.fix(fixfile)
new = [json.loads(l) for l in open(out)][n0:]
print(f"--- {len(new)} record(s) appended to the copy")
for r in new:
    print(f"b{r['b']} ev {[(e['subject'], e['verb'], e['object']) for e in r['events']]}")
