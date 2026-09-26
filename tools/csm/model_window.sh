#!/bin/bash
# CSM model window (D33/D34): Qwen down, whole card, run the four standing
# gates + the council instruments + the 298-batch page-run sweep, then
# restore the steady state (Qwen @174080 up, :8000 on CPU).
#
# The campaign's opencode session sits idle while this runs (tier-2
# handoff pattern, docs/ops/PC_GPU_HANDOFF.md): every decision is a file
# under /tmp/csm_model_window/, and Qwen comes back up no matter what
# (the trap restores it on any failure — the session depends on it).
#
# Launch (detached):  setsid nohup bash tools/csm/model_window.sh </dev/null >/dev/null 2>&1 &
# Poll:               tail /tmp/csm_model_window.log ; cat /tmp/csm_model_window/state
set -u
cd /home/goblin/ScriptEngine
VENV=scriptengine/.venv/bin/python
NINFER=/home/goblin/ninfer-work
LOG=/tmp/csm_model_window.log
STATEDIR=/tmp/csm_model_window
STATE=$STATEDIR/state
mkdir -p "$STATEDIR"

say() { echo "$(date +%H:%M:%S) $*" | tee -a "$LOG"; }
phase() { echo "$1" > "$STATE"; say "PHASE $1"; }

# restore is idempotent (it checks before acting) and runs on BOTH the
# normal exit and any failure: the campaign session's model must come back.
restore() {
  trap - EXIT
  say "RESTORE: bringing the steady state back (Qwen up, :8000 CPU)"
  # The CUDA :8000 must leave the card BEFORE Qwen loads: the 2026-09-17
  # window restored Qwen first, Qwen found 7.7 of its 10 GB runtime reservation
  # and exited, and the mode file still claimed a restore (Qwen down 13:30-18:28).
  pkill -f 'scriptengine.api.main' 2>/dev/null
  for i in $(seq 1 30); do
    [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)" -lt 2048 ] && break
    sleep 2
  done
  if ! pgrep -f 'qwen3_8_27b_nvfp4.ninfer' >/dev/null; then
    nohup "$NINFER/serve_ctx_174080.sh" >> "$NINFER/logs/serve_170k_window.log" 2>&1 &
    say "RESTORE: serve_ctx_174080 launched"
    for i in $(seq 1 60); do
      curl -s -m 2 http://127.0.0.1:18080/health 2>/dev/null | grep -q ok && break
      sleep 10
    done
    QPID=$(pgrep -f 'qwen3_8_27b_nvfp4.ninfer' | head -1 || true)
    FREE=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
    printf 'mode=174080 ctx=174080 qwen_pid=%s ts=%s free_mib=%s api=off\n' \
      "${QPID:-0}" "$(date +%Y-%m-%dT%H:%M:%S%:z)" "$FREE" > "$NINFER/qwen_mode.txt"
    say "RESTORE: Qwen mode file written (pid ${QPID:-MISSING})"
    curl -s -m 2 http://127.0.0.1:18080/health 2>/dev/null | grep -q ok \
      || say "RESTORE: FAILED — Qwen :18080 not healthy (see $NINFER/logs/serve_170k_window.log)"
  fi
  # GPU-only (owner directive 2026-09-26): :8000 comes back on CUDA or stays off —
  # never CPU. The embedder + reranker need ~5.3 GiB beside Qwen.
  FREE_API=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
  if [ "${FREE_API:-0}" -ge 5632 ]; then
    SCRIPTENGINE_DEVICE=cuda nohup "$VENV" -m scriptengine.api.main > /tmp/scriptengine_api.log 2>&1 &
    for i in $(seq 1 30); do
      curl -s -m 2 http://127.0.0.1:8000/health 2>/dev/null | grep -q ok && break
      sleep 5
    done
    say "RESTORE: :8000 on CUDA; steady state restored"
  else
    say "RESTORE: :8000 left OFF — ${FREE_API:-?} MiB free < 5.5 GiB (GPU-only: never CPU; dial Qwen down to host it)"
  fi
  echo "done-restored" > "$STATE"
}
trap restore EXIT

# ── pre-checks ────────────────────────────────────────────────────────────
phase precheck
if pgrep -f 'events[-_]extract' >/dev/null; then
  say "ABORT: an events-extract batch is in flight — Qwen owns the card"; exit 1
fi
curl -s -m 3 http://127.0.0.1:18080/health | grep -q ok || { say "ABORT: Qwen :18080 not healthy"; exit 1; }
say "precheck ok (Qwen up, no extraction batch)"

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

# ── :8000 on CUDA (the live-server gates + the batch sweep) ─────────────
phase api-cuda
pkill -f 'scriptengine.api.main' 2>/dev/null; sleep 3
SCRIPTENGINE_DEVICE=cuda nohup "$VENV" -m scriptengine.api.main > /tmp/csm_window_api.log 2>&1 &
APIPID=$!
for i in $(seq 1 60); do
  curl -s -m 2 http://127.0.0.1:8000/health 2>/dev/null | grep -q ok && break
  kill -0 "$APIPID" 2>/dev/null || { say "ABORT: :8000 CUDA died"; tail -20 /tmp/csm_window_api.log >> "$LOG"; exit 1; }
  sleep 5
done
say ":8000 up on CUDA (pid $APIPID)"

# ── gate 1: pytest (the trio needs :8000 up, so it runs before the bank) ─
phase pytest
SCRIPTENGINE_DEVICE=cuda "$VENV" -m pytest tests/ -q > "$STATEDIR/pytest.log" 2>&1
echo "pytest rc=$? $(tail -1 "$STATEDIR/pytest.log")" >> "$STATE.pytest"
tail -1 "$STATEDIR/pytest.log" >> "$LOG"

# ── gate 2: eval jjk (in-process CUDA, co-located with the CUDA :8000) ──
phase eval-jjk
SCRIPTENGINE_DEVICE=cuda "$VENV" -m scriptengine.cli eval --series jjk > "$STATEDIR/eval_jjk.log" 2>&1
echo "eval rc=$?" >> "$STATE.eval"
tail -5 "$STATEDIR/eval_jjk.log" >> "$LOG"

# ── gate 3: span-recall jjk (offline tier 0 + live 400-probe) ───────────
phase span-recall
"$VENV" -m scriptengine.cli span-recall --series jjk > "$STATEDIR/span_recall.log" 2>&1
echo "span-recall-offline rc=$?" >> "$STATE.span"
"$VENV" -m scriptengine.cli span-recall --series jjk --probe 400 >> "$STATEDIR/span_recall.log" 2>&1
echo "span-recall-probe rc=$?" >> "$STATE.span"
tail -5 "$STATEDIR/span_recall.log" >> "$LOG"

# ── gate 4: canon-run opm (server, one-copy rule) ───────────────────────
phase canon-opm
"$VENV" -m scriptengine.cli canon-run --series opm --skip-eval > "$STATEDIR/canon_opm.log" 2>&1
echo "canon-run rc=$?" >> "$STATE.canon"
tail -5 "$STATEDIR/canon_opm.log" >> "$LOG"

# ── council instruments: the 486 widened bank + 26 bar (in-process CUDA) ─
phase banks
SCRIPTENGINE_DEVICE=cuda "$VENV" tools/csm/p23_grader.py > "$STATEDIR/p23_grader.log" 2>&1
echo "p23 rc=$?" >> "$STATE.banks"
tail -8 "$STATEDIR/p23_grader.log" >> "$LOG"

# ── the D2 leg's own instrument: every CSM page batch, 60k/top-50/hint ──
phase page-run
# batch files are questions/_csm_page_<slug>.json; the .coverage./.verify.
# twins are score artifacts, not batches
SLUGS=$(ls questions/_csm_page_*.json 2>/dev/null | grep -v '\.coverage\.json$' | grep -v '\.verify\.json$' | grep -v '\.report\.json$' | sed 's|questions/_csm_page_||; s|\.json$||')
N=$(echo "$SLUGS" | grep -c . || true)
say "page-run: $N batches"
: > "$STATEDIR/page_run.tsv"
i=0
for slug in $SLUGS; do
  i=$((i+1))
  "$VENV" -m scriptengine.cli page-run --series csm --batch "$slug" >> "$STATEDIR/page_runs.log" 2>&1
  rc=$?
  echo -e "$slug\t$rc" >> "$STATEDIR/page_run.tsv"
  if [ $((i % 50)) -eq 0 ]; then say "page-run: $i/$N batches done"; fi
done
say "page-run: all $N batches done"

# ── coverage regen (after the batch results land) ────────────────────────
phase coverage
"$VENV" tools/coverage_report.py > "$STATEDIR/coverage.log" 2>&1
echo "coverage rc=$?" >> "$STATE.coverage"
tail -3 "$STATEDIR/coverage.log" >> "$LOG"

phase done
say "WINDOW COMPLETE: state files under $STATEDIR (pytest.log eval_jjk.log span_recall.log canon_opm.log p23_grader.log page_run.tsv coverage.log)"