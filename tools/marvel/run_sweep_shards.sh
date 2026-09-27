#!/usr/bin/env bash
# GATE C — concurrent tier-a sweep across the idle cores, then the merge.
#
# Each shard runs the unchanged single-process sweep logic over its own
# stable hash partition (--shard K --shards N), into its own report file
# seeded from the canonical report (so already-swept pages are skipped).
# Shard reports never touch each other; when every shard has exited, the
# shard files are merged back into the canonical report and removed.
#
# The post-sweep chain waits on THIS script's pid, so it starts only after
# the sweep is complete AND merged. Logs: /tmp/opencode (outside the repo).
#
# Usage: run_sweep_shards.sh <series> <tier> [shards]
set -uo pipefail
cd /home/goblin/ScriptEngine
PY=scriptengine/.venv/bin/python
SERIES=${1:?usage: run_sweep_shards.sh <series> <tier> [shards]}
TIER=${2:?usage: run_sweep_shards.sh <series> <tier> [shards]}
N=${3:-16}
BASE="questions/_${SERIES}_page_sweep_${TIER}.report.json"

[ -f "$BASE" ] || { echo "canonical report $BASE missing; nothing to seed from" >&2; exit 1; }

pids=()
for ((k=0; k<N; k++)); do
  f=$(printf "%02d" "$k")
  # Seed only on a first run: a crash-then-rerun keeps each shard's partial
  # report (its `done` set resumes from there) instead of re-sweeping it.
  # A stale seed from an older run is caught by the merge's superset check.
  [ -f "${BASE}.shard${f}" ] || cp "$BASE" "${BASE}.shard${f}"
  "$PY" -m scriptengine.cli page-sweep \
      --series "$SERIES" --tier "$TIER" \
      --shard "$k" --shards "$N" \
      --out "${BASE}.shard${f}" \
      >> "/tmp/opencode/sweep_${SERIES}_t${TIER}_shard${f}_of_${N}.log" 2>&1 &
  pids+=("$!")
done
rc=0
for p in "${pids[@]}"; do
  wait "$p" || rc=1
done
if [ "$rc" -ne 0 ]; then
  echo "one or more shards exited non-zero; NOT merging (fix and re-run; the shards are resumable)" >&2
  exit 1
fi
"$PY" tools/marvel/merge_sweep_shards.py --series "$SERIES" --tier "$TIER" --shards "$N"
echo "shard sweep complete + merged into $BASE"