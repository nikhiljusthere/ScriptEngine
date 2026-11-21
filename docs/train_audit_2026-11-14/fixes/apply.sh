#!/bin/bash
# fixes/apply.sh dry|apply GNNN  -- dry-run a reviewed fix file on a scratch copy, or apply it to the gold audit
# file through the project's writer (big_review_v2.py fix) after a backup. Run from docs/train_audit_2026-11-14.
set -e
mode=$1; g=$2
D=$(cd "$(dirname "$0")/.." && pwd); G=/home/goblin/ScriptEngine/series/universal/training/big/gold_v2
W=/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags; PY=/home/goblin/ScriptEngine/scriptengine/.venv/bin/python
S=${SCRATCH:-/tmp/claude-1000/-home-goblin-ScriptEngine--claude-worktrees-9b-model-extraction-analysis-a7e9c9/dddcd92a-55f3-4b22-b0fb-cd3f7c69555a/scratchpad}
n=$(grep -c '^@' $D/fixes/$g.txt)
if [ "$mode" = dry ]; then
  (cd $W && BV2_SET=gold SCRIPTENGINE_ROOT=/home/goblin/ScriptEngine $PY $D/../gold_audit_2026-11-14/dry_run_fix.py tools/train $D/fixes/$g.txt $S/dry_$g.jsonl > $S/dry_$g.log 2>&1) || true
  echo "blocks $n; FIXED $(grep -c '^FIXED' $S/dry_$g.log)"; grep -v -E '^(FIXED|b[0-9]+ ev |---)' $S/dry_$g.log | head -30
  python3 $D/fixes/diff_records.py $S/dry_$g.jsonl $(grep -c '^FIXED' $S/dry_$g.log) -v | cut -c1-230
else
  before=$(wc -l < $G/gold_audit_v2.jsonl); cp -p $G/gold_audit_v2.jsonl $G/bak_train_audit/gold_audit_v2.pre-$g.jsonl; cp $D/fixes/$g.txt $G/fixes/$g.txt
  (cd $W && BV2_SET=gold SCRIPTENGINE_ROOT=/home/goblin/ScriptEngine $PY tools/train/big_review_v2.py fix $G/fixes/$g.txt 2>&1 | grep -v '^FIXED' | head -20)
  after=$(wc -l < $G/gold_audit_v2.jsonl); echo "blocks $n; audit lines $before -> $after"
  python3 $D/fixes/diff_records.py $G/gold_audit_v2.jsonl $((after-before))
  head -4216 $G/gold_audit_v2.jsonl | cmp - $G/gold_audit_v2.jsonl.bak-pre-train-audit-2026-11-14 && echo "old content untouched"
fi
