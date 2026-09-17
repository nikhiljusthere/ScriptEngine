#!/usr/bin/env bash
# P2.3 + P2.2 grader handoff runner (council #31 P-2/P-5) — the model-unloaded
# batch. Pre-baked per PHASE2_JOB semantics: one launch line, halt codes,
# receipt, no mid-batch commits.
#
# The grader (tools/csm/p23_grader.py) is IN-PROCESS (the same
# build_context path the :8000 /context endpoint serves), so NO :8000 is
# needed — the batch only needs the GPU free for the retrieval stack
# (~5.3 GB). A CPU :8000 left running holds its models in RAM only: leave it.
#
# Launch (from the repo root, fully detached — the job survives the
# launching session, per the setsid rule):
#   setsid nohup bash tools/csm/p23_handoff.sh > /dev/null 2>&1 < /dev/null &
# Poll: reports/master-work/p23_grader_*_RECEIPT.md appearing = done.
#
# Halt codes:
#   10 Qwen still up after the stop attempt (mode file not off / :18080 busy)
#   11 GPU free < 6 GB after stopping Qwen (owner intervention)
#   12 venv / banks missing (pre-check)
#   14 smoke run failed (mechanics or model load broken)
#   15 wall-clock watchdog (45 min on the full run)
#   16 grader exit != 0 (its exit 3 = ERROR rate > 10% — do not ship)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
PY="$ROOT/scriptengine/.venv/bin/python"
MODE_FILE="$HOME/ninfer-work/qwen_mode.txt"
STOP="$HOME/ninfer-work/ninfer-stop.sh"
STAMP="$(date +%Y%m%d-%H%M%S)"
REC="reports/master-work/p23_grader_${STAMP}_RECEIPT.md"
LOG="reports/master-work/p23_grader_${STAMP}_run.log"
mkdir -p reports/master-work

pre() { echo "[p23] $*" | tee -a "$LOG"; }
fail() { pre "HALT ($2): $1"; echo "halt: $1" >> "$REC"; exit "$2"; }

[ -x "$PY" ] || fail "venv missing ($PY)" 12
[ -f reports/csm/census_widened_csm.json ] || fail "widened bank missing" 12
[ -f reports/csm/bar_audit_p14_preregistered.json ] || fail "bar-audit pre-registration missing" 12
[ -f "$STOP" ] || fail "ninfer-stop.sh missing ($STOP)" 12

# -- stop Qwen, free the whole card -------------------------------------------
if ! grep -q '^mode=off' "$MODE_FILE" 2>/dev/null; then
  pre "Qwen up ($(tr -d '\n' < "$MODE_FILE" 2>/dev/null || echo '?')) -> $STOP"
  "$STOP" || true
fi
grep -q '^mode=off' "$MODE_FILE" || fail "Qwen still up after stop attempt (mode file: $(cat "$MODE_FILE" 2>/dev/null))" 10
# :18080 must be free — a bare kill lets the restart poller resurrect Qwen
if "$PY" -c 'import socket,sys; s=socket.socket(); s.settimeout(1); sys.exit(0 if s.connect_ex(("127.0.0.1",18080)) else 1)'; then
  pre ":18080 free"
else
  fail ":18080 still busy (restart poller may be resurrecting Qwen)" 10
fi
FREE="$("$PY" - <<'EOF'
import subprocess
out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                      "--format=csv,noheader,nounits"],
                     capture_output=True, text=True).stdout.strip()
print(out.splitlines()[0] if out else "0")
EOF
)"
pre "GPU free after stop: ${FREE} MiB"
[ "$FREE" -ge 6000 ] || fail "GPU free ${FREE} MiB < 6000 MiB (a CUDA :8000 or another job holds the card?)" 11

# -- smoke: mechanics + model load on CUDA ------------------------------------
pre "smoke run (3 items/door)"
CENSUS_DEVICE=cuda timeout 600 "$PY" tools/csm/p23_grader.py --smoke >> "$LOG" 2>&1 \
  || fail "smoke run failed (see $LOG)" 14

# -- full run, 45-min watchdog --------------------------------------------------
pre "full run: widened 486 (qa) + bar-audit 26 x {qa,auto}"
RC=0
CENSUS_DEVICE=cuda timeout 2700 "$PY" tools/csm/p23_grader.py >> "$LOG" 2>&1 || RC=$?
[ "$RC" -eq 0 ] || fail "grader exit $RC (3 = ERROR rate > 10%; 124 = 45-min watchdog)" 16

# -- receipt --------------------------------------------------------------------
{
  echo "# p23 grader receipt $STAMP"
  echo
  echo "- tree: $(git rev-parse --short HEAD)"
  echo "- pre-checks: Qwen stopped (mode=off), :18080 free, GPU ${FREE} MiB free"
  echo "- banks: $(sha256sum reports/csm/census_widened_csm.json reports/csm/bar_audit_p14_preregistered.json | awk '{print $1"  "$2}' | tr '\n' ' ')"
  echo "- results: reports/csm/census_widened_csm_results.jsonl + reports/csm/bar_audit_p14_results.jsonl"
  echo
  echo "## grader tail"
  tail -n 40 "$LOG"
  echo
  echo "## After"
  echo "- Qwen is left DOWN. The owner restores the dial on return (P2.4 needs Qwen up)."
  echo "- Commit the results + this receipt (the batch writes files, it does not commit)."
} > "$REC"
pre "done: $REC"