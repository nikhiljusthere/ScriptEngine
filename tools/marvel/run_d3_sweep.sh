#!/usr/bin/env bash
# D3 3-door tier-1 sweep supervisor (marvel, D5 reachability exhaustiveness).
#
# Per door, CSM order qa -> narrative -> roster:
#   1. skip the door when its ledger is already complete (517,960 rows, 0
#      ERROR rows) -- relaunch-safe, the campaign step resumes across
#      windows;
#   2. otherwise the sanity-100 gate (CSM A15 timer): a zero-hit 100-probe
#      subset halts the door (exit 3, dead-door halt -- council addendum:
#      never burn the exhaustive sweep on a door that serves nothing);
#   3. then the full panel sweep: idempotent, resumes from the per-door
#      ledger (rewritten, never appended; (title, sentence)-keyed; ERROR
#      rows re-probed on the next window; hit_rate divides by the FULL
#      517,960 panel, §2a trap-3).
#
# Prereq: the :8000 serving stack up (CUDA-only -- GPU-only directive;
# never CPU). A server-down window ends a full run with a wall of ERROR
# rows (the probe loop never aborts on a failed probe); the supervisor
# stops the chain and the next window re-probes from the ledger.
#
# Launch (detached):
#   setsid nohup bash tools/marvel/run_d3_sweep.sh </dev/null >/dev/null 2>&1 &
# Poll:
#   tail /tmp/opencode/d3_sweep.log ; cat /tmp/opencode/d3_sweep_state
set -u
cd /home/goblin/ScriptEngine
VENV=scriptengine/.venv/bin/python
PANEL=reports/marvel/tier1_panel_2026-09-27.json
HASH8=a880bf25            # the panel hash (stamped in-file; ledger name key)
PANEL_SIZE=517960
DOORS=(qa narrative roster)
LOG=/tmp/opencode/d3_sweep.log
STATE=/tmp/opencode/d3_sweep_state
mkdir -p /tmp/opencode

say() { echo "$(date +%H:%M:%S) $*" | tee -a "$LOG"; }
ledger() { echo "reports/span-recall/marvel/sweep_${1}_${HASH8}.jsonl"; }
probed() {
  local f
  f=$(ledger "$1")
  if [ -f "$f" ]; then wc -l < "$f"; else echo 0; fi
}
errors() {
  local f n
  f=$(ledger "$1")
  if [ -f "$f" ]; then
    n=$(grep -c '"verdict": "ERROR"' "$f" || true)
    echo "${n:-0}"
  else
    echo 0
  fi
}

say "D3 supervisor start $(date '+%F %T'); :8000 health: $(curl -s -m 3 http://127.0.0.1:8000/health 2>/dev/null | head -c 160)"
if ! curl -s -m 3 http://127.0.0.1:8000/health 2>/dev/null | grep -q ok; then
  say "ABORT: :8000 not healthy -- start the serving stack (CUDA) and relaunch; the ledgers resume"
  exit 1
fi

for door in "${DOORS[@]}"; do
  p=$(probed "$door"); e=$(errors "$door")
  if [ "$p" -ge "$PANEL_SIZE" ] && [ "$e" -eq 0 ]; then
    say "$door: ledger COMPLETE ($p probed, 0 errors) -- skip"
    echo "door=$door status=complete probed=$p ts=$(date +%s)" >> "$STATE"
    continue
  fi
  unprobed=$((PANEL_SIZE - p))
  if [ "$unprobed" -gt 0 ]; then
    say "$door: sanity-100 gate ($p/$PANEL_SIZE probed, $e error rows to re-probe)"
    "$VENV" -m scriptengine.cli span-recall --series marvel --panel "$PANEL" \
      --door "$door" --sanity 100 >> "$LOG" 2>&1
    rc=$?
    if [ "$rc" -eq 3 ]; then
      say "$door: DEAD-DOOR HALT (zero hits on the sanity subset, exit 3) -- full sweep not run (council addendum)"
      echo "door=$door status=DEAD ts=$(date +%s)" >> "$STATE"
      continue
    fi
    if [ "$rc" -ne 0 ]; then
      say "$door: sanity rc=$rc (1 = panel/ledger tamper, 2 = tier-0 misses) -- aborting the chain"
      echo "door=$door status=sanity-failed rc=$rc ts=$(date +%s)" >> "$STATE"
      exit 1
    fi
    say "$door: sanity ok (live door; $(probed "$door")/$PANEL_SIZE probed)"
  fi
  say "$door: full sweep start ($p/$PANEL_SIZE probed; ~$((unprobed / 1000))k probes left this window)"
  t0=$(date +%s)
  "$VENV" -m scriptengine.cli span-recall --series marvel --panel "$PANEL" \
    --door "$door" > "/tmp/opencode/d3_full_${door}.log" 2>&1
  rc=$?
  t1=$(date +%s)
  p2=$(probed "$door"); e2=$(errors "$door")
  tail -14 "/tmp/opencode/d3_full_${door}.log" >> "$LOG"
  if [ "$rc" -ne 0 ]; then
    say "$door: full rc=$rc at $p2/$PANEL_SIZE -- window lost; relaunch resumes from the ledger"
    echo "door=$door status=interrupted rc=$rc probed=$p2 errors=$e2 ts=$t1" >> "$STATE"
    exit 1
  fi
  if [ "$p2" -ge "$PANEL_SIZE" ] && [ "$e2" -eq 0 ]; then
    say "$door: COMPLETE in $((t1 - t0))s -- $p2/$PANEL_SIZE, 0 errors (ledger $(ledger "$door"))"
    echo "door=$door status=complete probed=$p2 errors=0 ts=$t1" >> "$STATE"
  else
    say "$door: run ended rc=0 but $e2 error rows remain ($p2/$PANEL_SIZE) -- likely a server-down window; chain stops, next window re-probes"
    echo "door=$door status=needs-reprobe probed=$p2 errors=$e2 ts=$t1" >> "$STATE"
    exit 1
  fi
done

say "D3 3-door sweep COMPLETE -- per-door ledgers are the verdict evidence (plan §834: miss file to zero, or a documented floor with cause + retest)"
echo "all-doors=complete ts=$(date +%s)" >> "$STATE"