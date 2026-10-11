#!/bin/bash
# v2 labeller resume (events + facts + tags): every big_in id not yet in labels_v2.jsonl, input order.
R=/home/goblin/ScriptEngine
W=$R/.claude/worktrees/big-review-flags
T=${T:-/tmp/label_v2_ids}; mkdir -p $T
B=$R/series/universal/training/big
P=$R/scriptengine/.venv/bin/python
$P -I - "$B/labels_v2.jsonl" "$T/rest_ids.jsonl" $R/series/marvel/training/labels/big_in.jsonl $R/series/mcu/training/labels/big_in.jsonl <<'PY'
import json, sys
done = set()
for l in open(sys.argv[1]):
    l = l.strip("\x00\n ")
    if l:
        done.add(json.loads(l)["id"])
n = 0
with open(sys.argv[2], "w") as out:
    for p in sys.argv[3:]:
        for l in open(p):
            if l.strip():
                i = json.loads(l)["id"]
                if i not in done:
                    out.write(json.dumps({"id": i}) + "\n"); n += 1
print("remaining ids", n)
PY
cd $W
SCRIPTENGINE_ROOT=$R exec $P tools/train/label_single.py --schema v2 \
  --in $R/series/marvel/training/labels/big_in.jsonl --in $R/series/mcu/training/labels/big_in.jsonl \
  --out $B/labels_v2.jsonl --ids $T/rest_ids.jsonl --workers 8 --provenance v2-full
