#!/bin/bash
# supervise.sh NN [NN ...] -> score finished chunks against the gold, write their worklists, log one line each to STATE.md
cd "$(dirname "$0")"; G=/home/goblin/student_runs_local/jjk_side/s2data/train.jsonl
for n in "$@"; do
  f=chunks/chunk_${n}_blind.jsonl; [ -f "$f" ] || { echo "chunk $n: no output file"; continue; }
  want=$(wc -l < chunks/chunk_${n}_input.jsonl); got=$(wc -l < "$f")
  line=$(python3 compare_windows.py $G "$f" --worklist chunks/chunk_${n}_work.jsonl | python3 -c "
import sys,re
t=sys.stdin.read(); g=lambda k:int(re.search(r'(\d+)\s+'+re.escape(k),t).group(1))
print(f\"class {g('class agrees')}/{g('lines')}={g('class agrees')/g('lines'):.0%}; events gold {g('gold events')} blind {g('blind events')} both {g('events in both')} blind-only {g('blind-only events')} gold-only {g('gold-only events')}; gold people unlisted {g('gold people the blind reader does not list')}/{g('gold people')}; \" + re.search(r'format problems.*', t).group(0))")
  msg="- $(date +%H:%M) chunk $n scored: windows $got/$want; $line"
  echo "$msg"; echo "$msg" >> ../STATE.md
done
echo "done chunks: $(ls chunks/*_blind.jsonl 2>/dev/null | wc -l)/32"
