#!/bin/bash
# D6 134 page-run re-run (post side-session): the side session's page-run
# phase hit 134x connection-refused at preflight (operational, zero requests
# reached :8000) while the server was up; this re-runs the frozen 134 slugs
# against the healthy server under the same conditions as the pre-baseline
# (Qwen 100k up, :8000 CUDA). Touches neither Qwen nor :8000 itself.
#
# Launch (detached): setsid nohup bash tools/csm/d6_pagererun.sh </dev/null >/dev/null 2>&1 &
# Poll: tail /tmp/d6_pagererun.log; wc -l /tmp/d6_pagererun.tsv
set -u
cd /home/goblin/ScriptEngine
VENV=scriptengine/.venv/bin/python
LOG=/tmp/d6_pagererun.log
TSV=/tmp/d6_pagererun.tsv
: > "$LOG"
: > "$TSV"
i=0
n=0
while read -r slug; do
  case "$slug" in \#*|"") continue;; esac
  n=$((n+1))
done < reports/csm/D6_PAGE134_SLUGS.txt
echo "$(date +%H:%M:%S) page-rerun start: $n frozen D6 slugs" >> "$LOG"
i=0
while read -r slug; do
  case "$slug" in \#*|"") continue;; esac
  i=$((i+1))
  "$VENV" -m scriptengine.cli page-run --series csm --batch "$slug" >> "$LOG" 2>&1
  rc=$?
  printf '%s\t%s\n' "$slug" "$rc" >> "$TSV"
  if [ $((i % 20)) -eq 0 ]; then echo "$(date +%H:%M:%S) page-rerun: $i/$n done" >> "$LOG"; fi
done < reports/csm/D6_PAGE134_SLUGS.txt
echo "$(date +%H:%M:%S) page-rerun: ALL $n done" >> "$LOG"
pass=$(awk -F"\t" '$2==0{c++} END{print c+0}' "$TSV")
echo "$(date +%H:%M:%S) page-rerun: $pass/$n scored rc=0" >> "$LOG"
# A 100% operational failure must halt loudly, never read as a result.
if [ "$n" -gt 0 ] && [ "$pass" -eq 0 ]; then
  echo "$(date +%H:%M:%S) page-rerun: HALT — 0/$n scored (all operational rc=1)" >> "$LOG"; exit 3
fi
