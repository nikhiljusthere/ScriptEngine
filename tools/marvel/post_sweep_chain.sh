#!/usr/bin/env bash
# GATE C — marvel post-sweep chain (zero egress; local only).
#
# Waits for the tier-a sweep to finish, then runs the marvel-side GATE C
# evidence in order, GPU steps serialized (one 32 GB card, ~5 GB free under
# the Qwen dial):
#   1. index --series marvel --no-embed   (store + BM25 with the
#      content_sections promotion; events/meaning empty so no --force)
#   2. chunk-containment --series marvel  (tier 0: 0 unreachable; CPU)
#   3. census_c6.py bank --series marvel  (refuses partial/error sweep)
#   4. census_c6.py oos-freeze --series marvel (deterministic, pre-model)
#   5. census_c6.py census --series marvel      (GPU, in-process)
#   6. census_c6.py oos-score --series marvel --out pre (GPU, in-process)
#   7. eval --series marvel / --series mcu (GPU; the D1 marvel-set gates)
#
# Exit 0 = every step green; the first failure stops the chain and is the
# line to fix. Log: /tmp/opencode/marvel_post_sweep_chain.log
set -uo pipefail
cd /home/goblin/ScriptEngine
PY=scriptengine/.venv/bin/python
LOG=/tmp/opencode/marvel_post_sweep_chain.log
SWEEP_PID=${1:?usage: post_sweep_chain.sh <sweep_pid>}

log() { echo "=== $(date '+%F %T') $*" | tee -a "$LOG"; }
step() { # step <name> <cmd...>
  local name=$1; shift
  log "STEP $name"
  if "$@" >>"$LOG" 2>&1; then
    log "STEP $name OK"
  else
    log "STEP $name FAILED (exit $?)"
    exit 1
  fi
}

# GPU contention guard: wait until the card has headroom (model ~5 GB; the
# MCU OOS re-score or any other job must be finished first).
wait_gpu() {
  while :; do
    # This driver rejects `memory_free`; derive it from the valid fields.
    used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
    total=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
    free=$((total - used))
    [ "$free" -gt 6000 ] && break
    log "GPU busy (free=${free} MiB); sleeping 60s"
    sleep 60
  done
}

log "post-sweep chain start; waiting for sweep pid $SWEEP_PID"
while kill -0 "$SWEEP_PID" 2>/dev/null; do sleep 60; done
log "sweep pid $SWEEP_PID finished"

# Sweep completeness is asserted by the bank itself (no --allow-partial):
# it refuses a report with any error page or a missing page.
step 1-index    "$PY" -m scriptengine.cli index --series marvel --no-embed
step 2-contain  "$PY" -m scriptengine.cli chunk-containment --series marvel
step 3-bank     "$PY" tools/marvel/census_c6.py bank --series marvel
step 4-freeze   "$PY" tools/marvel/census_c6.py oos-freeze --series marvel
wait_gpu
step 5-census   "$PY" tools/marvel/census_c6.py census --series marvel
step 6-oos-pre  "$PY" tools/marvel/census_c6.py oos-score --series marvel --out pre
step 7-eval-m   "$PY" -m scriptengine.cli eval --series marvel
step 8-eval-mcu "$PY" -m scriptengine.cli eval --series mcu

log "post-sweep chain complete: all steps green"