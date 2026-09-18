#!/usr/bin/env bash
# D7 GPU window: stop 135k -> grade legs singly -> 4 gates -> restore 135k.
# Every step after the kill is shell: no LLM survives by design.
#
# Verbatim chain (chairman.md) + exactly three disclosed deviations:
#   (a) bare `python` -> $PY  ($S/scriptengine/.venv/bin/python)
#   (b) bounded liveness guard after the Qwen kill: 6x5s SIGTERM window ->
#       one SIGKILL -> 3x5s -> else RECEIPT_KILLFAIL + exit 1
#   (c) unset both leg flags before the four standing gates (the leg loop
#       exports them; the gates must measure committed-tree behavior)
set -u
S=/home/goblin/ScriptEngine
W=$S/reports/csm/receipts/d7_window
PY=$S/scriptengine/.venv/bin/python

# 1. stop the 135k owner-manual Qwen (pid captured on disk in pre-stage)
QPID=$(cat /tmp/d7_qwen_pid.txt)
kill "$QPID"
# (b) bounded liveness guard: SIGTERM window (6x5s) -> one SIGKILL -> 3x5s
# -> else record KILLFAIL and stop; a wedged kill must not leave the window
# running with the model still up.
i=0
while kill -0 "$QPID" 2>/dev/null; do
  i=$((i+1))
  if [ "$i" -le 6 ]; then sleep 5; continue; fi
  if [ "$i" -eq 7 ]; then kill -9 "$QPID" 2>/dev/null; fi
  if [ "$i" -gt 9 ]; then
    echo KILLFAIL > "$W/RECEIPT_KILLFAIL"
    echo "[chain] KILLFAIL: qwen pid $QPID still alive after SIGTERM+SIGKILL" >&2
    exit 1
  fi
  sleep 5
done

# 2. poll for the whole card (bounded, status lines)
for i in $(seq 1 36); do
  f=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | tr -d ' ')
  echo "[chain] $(date +%T) gpu_free=${f}MiB"
  [ "$f" -ge 8000 ] && break
  sleep 10
done

# 3. legs, singly, in order — stop at the first red
for leg in A B C; do
  case $leg in
    A) export SCRIPTENGINE_TIERED_RECALL=1  SCRIPTENGINE_ABILWIDTH_RECALL=0 ;;
    B) export SCRIPTENGINE_TIERED_RECALL=0  SCRIPTENGINE_ABILWIDTH_RECALL=1 ;;
    C) export SCRIPTENGINE_TIERED_RECALL=1  SCRIPTENGINE_ABILWIDTH_RECALL=1 ;;
  esac
  CENSUS_DEVICE=cuda $PY $S/tools/csm/p23_grader.py      > $W/LEG${leg}_p23.log 2>&1 || { echo "$leg: p23 rc=$? (halt)"; break; }
  $PY $S/tools/csm/blind_score.py                        > $W/LEG${leg}_blind.log 2>&1
  $PY $S/tools/csm/d6_flip.py                            > $W/LEG${leg}_flip.log 2>&1
  $PY $S/tools/csm/check_targets.py $leg                 > $W/LEG${leg}_targets.log 2>&1
  grep -q '^RED' $W/LEG${leg}_targets.log $W/LEG${leg}_flip.log 2>/dev/null && { echo "$leg: RED (halt)"; break; }
done

# 4. four standing gates (default env = both flags OFF = committed-tree JJK no-op)
# (c) the leg loop exported the flags; clear them so the gates measure the
# committed tree (both flags OFF) regardless of which leg ran last.
unset SCRIPTENGINE_TIERED_RECALL SCRIPTENGINE_ABILWIDTH_RECALL
$PY -m pytest $S/tests/ -q > $W/gate_pytest.log 2>&1
CENSUS_DEVICE=cuda $PY -m scriptengine.cli eval --series jjk > $W/gate_eval.log 2>&1
$PY -m scriptengine.cli chunk-containment --series jjk > $W/gate_span.log 2>&1
setsid nohup $PY -m scriptengine.api.main > $W/gate_api.log 2>&1 < /dev/null &
for i in $(seq 1 60); do curl -sf http://127.0.0.1:8000/health >/dev/null && break; sleep 5; done
$PY -m scriptengine.cli chunk-containment --series jjk --probe 400 >> $W/gate_span.log 2>&1
pkill -f 'scriptengine\.api\.main'
CENSUS_DEVICE=cuda $PY -m scriptengine.cli canon-run --series opm --skip-eval > $W/gate_canon.log 2>&1

# 5. restore 135k from the captured argv (cwd + args verified in pre-stage)
( cd "$(cat /tmp/d7_qwen_cwd.txt)" && setsid nohup bash -c "$(cat /tmp/d7_qwen_argv.txt)" > /tmp/qwen135k_restore.log 2>&1 < /dev/null & )
for i in $(seq 1 60); do curl -sf http://127.0.0.1:18080/health >/dev/null && break; sleep 5; done
nvidia-smi > $W/gpu_after.txt
echo DONE > $W/RECEIPT_DONE