#!/bin/bash
# gold v2 backfill (2026-10-14): the 3,822 unique gold windows get facts + tags from the 35B; the gold
# events are FIXED (--add-only). Resumable: label_single skips ids already in the output.
R=/home/goblin/ScriptEngine
W=$R/.claude/worktrees/big-review-flags
G=$R/series/universal/training/big/gold_v2
P=$R/scriptengine/.venv/bin/python
cd $W
SCRIPTENGINE_ROOT=$R exec $P tools/train/label_single.py --schema v2 \
  --in $G/gold_in.jsonl --add-only $G/gold_events.jsonl \
  --out $G/gold_labels_v2.jsonl --workers 8 --provenance gold-events+v2-facts
