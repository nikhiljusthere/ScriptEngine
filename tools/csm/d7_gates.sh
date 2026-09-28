#!/bin/bash
# D7 gate window: whole card for engine work (Qwen 65k down, :8000 CUDA up).
# Runs the 4 standing gates + the official p23 486 regrade WITH the D7
# subject-routing spike active (uncommitted tree), then restores the user
# steady state (Qwen 65k up, :8000 DOWN, mode file api=off).
#
# Qwen is stopped because Qwen65k (22 GB) + :8000 (5.3 GB) + one in-process
# worker (5.3 GB) peaks ~32.6 GB > 32 GB card. The session model is remote
# (Muse Spark), so stopping Qwen blinds nothing here; the EXIT trap brings
# the EXACT user argv back (no --vision; captured 2026-09-18) no matter what.
#
# Launch (detached):  setsid nohup bash tools/csm/d7_gates.sh </dev/null >/dev/null 2>&1 &
# Poll:               tail /tmp/d7_gates.log ; cat /tmp/d7_gates/state
set -u
cd /home/goblin/ScriptEngine
VENV=scriptengine/.venv/bin/python
NINFER=/home/goblin/ninfer-work
LOG=/tmp/d7_gates.log
STATEDIR=/tmp/d7_gates
STATE=$STATEDIR/state
mkdir -p "$STATEDIR"

say() { echo "$(date +%H:%M:%S) $*" | tee -a "$LOG"; }
phase() { echo "$1" > "$STATE"; say "PHASE $1"; }

restore() {
  trap - EXIT
  say "RESTORE: Qwen 65k up, :8000 down (user steady state)"
  pkill -f 'scriptengine.api.main' 2>/dev/null
  for i in $(seq 1 30); do
    [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)" -lt 2048 ] && break
    sleep 2
  done
  if ! pgrep -f 'qwen3_8_27b_nvfp4.ninfer' >/dev/null; then
    cd "$NINFER"
    nohup ./ninfer/build/apps/ninfer-serve /mnt/PROJECTS/ninfer-transfer/models/qwen3_8_27b_nvfp4.ninfer \
      --host 0.0.0.0 --port 18080 \
      --model-id qwen3.8-27b-ninfer \
      --max-context 65536 \
      --kv-capacity 65536 \
      --max-concurrency 3 \
      --pending-timeout-ms 120000 \
      --default-max-tokens 20480 \
      --prefill-chunk 4096 \
      --kv-dtype int8 \
      --spec mtp --draft-tokens 3 --lm-head-draft \
      --preserve-thinking \
      --cors \
      --log-stats-interval-ms 1000 \
      --request-log-jsonl /home/goblin/ninfer-work/logs/requests.jsonl \
      >> "$NINFER/logs/serve_65k_d7.log" 2>&1 &
    cd /home/goblin/ScriptEngine
    say "RESTORE: Qwen 65k relaunched with user argv (no vision)"
    for i in $(seq 1 60); do
      curl -s -m 2 http://127.0.0.1:18080/health 2>/dev/null | grep -q ok && break
      sleep 10
    done
    QPID=$(pgrep -f 'qwen3_8_27b_nvfp4.ninfer' | head -1 || true)
    FREE=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
    printf 'mode=65k ctx=65536 qwen_pid=%s ts=%s free_mib=%s api=off\n' \
      "${QPID:-0}" "$(date -Is)" "$FREE" > "$NINFER/qwen_mode.txt"
    say "RESTORE: mode file written (pid ${QPID:-MISSING})"
    curl -s -m 2 http://127.0.0.1:18080/health 2>/dev/null | grep -q ok \
      || say "RESTORE: FAILED — Qwen :18080 not healthy"
  fi
  pkill -f 'scriptengine.api.main' 2>/dev/null
  say "RESTORE: steady state restored (Qwen 65k up, :8000 down)"
  echo "done-restored" > "$STATE"
}
trap restore EXIT

# ── pre-checks ────────────────────────────────────────────────────────────
phase precheck
if pgrep -f 'events[-_]extract' >/dev/null; then
  say "ABORT: an events-extract batch is in flight — Qwen owns the card"; exit 1
fi
curl -s -m 3 http://127.0.0.1:18080/health | grep -q ok || { say "ABORT: Qwen :18080 not healthy"; exit 1; }
git diff --stat -- scriptengine/api/context.py | head -5 >> "$LOG" 2>&1
say "precheck ok (spike diff above; Qwen up, no extraction batch)"

# ── Qwen down, whole card ────────────────────────────────────────────────
phase qwen-down
"$NINFER/ninfer-stop.sh" >> "$LOG" 2>&1
for i in $(seq 1 30); do
  pgrep -f 'qwen3_8_27b_nvfp4.ninfer' >/dev/null || break
  sleep 5
done
sleep 5
FREE=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
say "Qwen down; free VRAM ${FREE} MiB"
if [ "$FREE" -lt 25000 ]; then say "ABORT: card not free (${FREE} MiB)"; exit 1; fi

# ── :8000 on CUDA (trio + canon need the live server) ───────────────────
phase api-cuda
pkill -f 'scriptengine.api.main' 2>/dev/null; sleep 3
SCRIPTENGINE_DEVICE=cuda nohup "$VENV" -m scriptengine.api.main > /tmp/d7_gates_api.log 2>&1 &
APIPID=$!
for i in $(seq 1 60); do
  curl -s -m 2 http://127.0.0.1:8000/health 2>/dev/null | grep -q ok && break
  kill -0 "$APIPID" 2>/dev/null || { say "ABORT: :8000 CUDA died"; tail -20 /tmp/d7_gates_api.log >> "$LOG"; exit 1; }
  sleep 5
done
say ":8000 up on CUDA (pid $APIPID)"

# ── gate 1: pytest ───────────────────────────────────────────────────────
phase pytest
SCRIPTENGINE_DEVICE=cuda "$VENV" -m pytest tests/ -q > "$STATEDIR/pytest.log" 2>&1
echo "pytest rc=$? $(tail -1 "$STATEDIR/pytest.log")" > "$STATE.pytest"
tail -1 "$STATEDIR/pytest.log" >> "$LOG"

# ── gate 2: eval jjk ────────────────────────────────────────────────────
phase eval-jjk
SCRIPTENGINE_DEVICE=cuda "$VENV" -m scriptengine.cli eval --series jjk > "$STATEDIR/eval_jjk.log" 2>&1
echo "eval rc=$?" > "$STATE.eval"
tail -5 "$STATEDIR/eval_jjk.log" >> "$LOG"

# ── gate 3: span-recall jjk ─────────────────────────────────────────────
phase span-recall
"$VENV" -m scriptengine.cli span-recall --series jjk > "$STATEDIR/span_recall.log" 2>&1
echo "span-recall-offline rc=$?" > "$STATE.span"
"$VENV" -m scriptengine.cli span-recall --series jjk --probe 400 >> "$STATEDIR/span_recall.log" 2>&1
echo "span-recall-probe rc=$?" >> "$STATE.span"
tail -5 "$STATEDIR/span_recall.log" >> "$LOG"

# ── gate 4: canon-run opm ───────────────────────────────────────────────
phase canon-opm
"$VENV" -m scriptengine.cli canon-run --series opm --skip-eval > "$STATEDIR/canon_opm.log" 2>&1
echo "canon-run rc=$?" > "$STATE.canon"
tail -5 "$STATEDIR/canon_opm.log" >> "$LOG"

# ── official regrade WITH the spike (pre-spike snapshot saved first) ────
phase banks
mkdir -p reports/csm/receipts/d6_window
# -n: never clobber the pre-spike snapshot on repeat runs; the worktree
# results file is the run's output and is overwritten every run by design.
cp -n reports/csm/census_widened_csm_results.jsonl reports/csm/receipts/d6_window/census_widened_csm_results_pred7.jsonl
cp -n reports/csm/bar_audit_p14_results.jsonl reports/csm/receipts/d6_window/bar_audit_p14_results_pred7.jsonl 2>/dev/null || true
say "banks: pre-spike snapshot present in reports/csm/receipts/d6_window/"
SCRIPTENGINE_DEVICE=cuda "$VENV" tools/csm/p23_grader.py > "$STATEDIR/p23_grader.log" 2>&1
echo "p23 rc=$?" > "$STATE.banks"
tail -8 "$STATEDIR/p23_grader.log" >> "$LOG"

phase done
say "D7 GATE WINDOW COMPLETE: state files under $STATEDIR"
