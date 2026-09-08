#!/usr/bin/env bash
# gpu-handoff.sh — cross-session GPU step handoff (council verdict 2026-09-08,
# reports/master-work/COUNCIL_gpu_handoff.md; protocol: docs/ops/PC_GPU_HANDOFF.md).
#
# Two tiers:
#   tier1 — NO mode flip. Deterministic Qwen-batch steps (events-extract, LLM
#           batches) run under 262k with Qwen owning the GPU and :8000 on CPU
#           (normal 262k behavior). A just detaches the batch + the typer:
#               tools/master-work/gpu-handoff.sh --tier1 <spec>
#   tier2 — the chain (CUDA embed/reindex, ≥2-parallel-subagent phases, or a
#           judgment step needing a fresh 100k session). A writes the spec +
#           SWITCHPOINT + git commit, then its FINAL action:
#               setsid nohup tools/master-work/gpu-handoff.sh --tier2 <spec> >/dev/null 2>&1 &
#           This script is plain shell (no LLM in the chain except C's task):
#             1. quiescence: A's session jsonl stable ~10 s + all session jsonls stable 5 s
#                (launch-side race guard: the switch must not overlap A's turn-end model call)
#             2. qwen-switch.sh 100k --force      (no --api: :8000 stays where it is = CPU)
#             3. open C's terminal (title GPU-C): wrapper = pi "<task>" ; wrapper writes the state file
#                (C is a FRESH pi session: models.json now says 100k -> C declares 100k, no overflow class)
#             4. wait: state file (done|failed) + :18080 liveness (ninfer_restart.sh on death, bounded x2)
#                + heartbeat deadline (no state update in eta_sec -> STALLED.flag)
#             5. qwen-switch.sh 262k --force  (PI_SESSION_FILE=C's transcript; --force backstop,
#                because deleting C's file first would poison the guard with A's transcript)
#                — this absorbs the "D terminal" (rejected by the council; still a plain shell
#                between turns, hard rule holds)
#             6. typer (plain shell, idempotent one-shot): gate =
#                state==done ∧ qwen_mode.txt==262k ∧ :18080 healthy ∧ report mtime stable ~30 s
#                ∧ window found by TITLE (never a cached window id — stale after reboot)
#                ∧ A's jsonl idle ~10 s ∧ typed-flag unset
#                -> windowactivate + type resume_line + Enter, ONCE.
#                state==failed  -> type a FAILURE line instead (A decides; never silent).
#                stale window    -> flag file; owner types the resume one-liner (it is on disk).
#
#   --test <spec> — dry-run: no real switch (echo), fake batch, a titled test
#           window whose shell records typed lines to a side-channel file.
#           Verifies the whole chain mechanics without touching the model.
#
# spec file = KEY=VALUE lines:
#   kind=tier1|tier2
#   batch=<resumable-from-disk shell command>            (tier1; tier2: C's task runs it)
#   report=<path C/A must leave the report at>
#   resume_line=<the fixed one-liner A reads on resume>
#   a_title=<A's terminal title (fallback lookup; shells/pi often rewrite it)>
#   a_win=<A's window id: A captures `xdotool getactivewindow` at handoff (primary, no vision)>
#   a_session=<A's pi session jsonl path>
#   eta_sec=<heartbeat deadline for the GPU task (default 3600)>
#   task=<C's pi prompt: what to do, where the report goes>   (tier2)

set -uo pipefail
NW=/home/goblin/ninfer-work
REPO=/home/goblin/ScriptEngine
MW=$REPO/reports/master-work
STATE_DIR=$MW/gpu_handoff_state
mkdir -p "$STATE_DIR"

usage() { grep '^#   ' "$0" | head -8; exit 1; }
MODE=""
case "${1:-}" in
  --tier1) MODE=tier1; shift ;;
  --tier2) MODE=tier2; shift ;;
  --test)  MODE=test;  shift ;;
  *) usage ;;
esac
[ $# -eq 1 ] || usage
SPEC="$1"; [ -f "$SPEC" ] || { echo "spec not found: $SPEC" >&2; exit 1; }

# ---- parse spec -------------------------------------------------------------
get() { sed -n "s/^$1=//p" "$SPEC" | head -1; }
BATCH=$(get batch); REPORT=$(get report); RESUME=$(get resume_line)
A_TITLE=$(get a_title); A_SESS=$(get a_session); ETA=$(get eta_sec); TASK=$(get task); A_WIN=$(get a_win)
[ -n "$A_TITLE" ] && [ -n "$RESUME" ] && [ -n "$REPORT" ] || { echo "spec needs a_title, resume_line, report" >&2; exit 1; }
ETA=${ETA:-3600}
SPECNAME=$(basename "$SPEC" .yaml); [ "${SPECNAME%.spec}" != "$SPECNAME" ] && SPECNAME=${SPECNAME%.spec}
STATE=$STATE_DIR/$SPECNAME.state
STALLED=$STATE_DIR/$SPECNAME.stalled
LOG=$STATE_DIR/$SPECNAME.log
: > "$LOG"
say() { echo "[$(date +%T)] $*" | tee -a "$LOG" >&2; }

health()  { [ "$(curl -s -m 3 -o /dev/null -w '%{http_code}' http://127.0.0.1:18080/health)" = 200 ]; }
mode_now(){ sed -n 's/^mode=\([^ ]*\).*/\1/p' "$NW/qwen_mode.txt" 2>/dev/null | head -1; }

# stable_mtime <path> <secs> — true if mtime unchanged for <secs> (single-sample loop)
stable_mtime() { local m1=$(stat -c %Y "$1" 2>/dev/null || echo 0) i; for i in $(seq 1 $(( $2 / 5 + 1 ))); do sleep 5; [ "$(stat -c %Y "$1" 2>/dev/null || echo 0)" = "$m1" ] || return 1; done; return 0; }

# quiescence: A's jsonl quiet ~10 s (launch-side race), all session jsonls quiet 5 s
quiesce() {
  say "quiescence: waiting for A ($A_SESS) quiet ~10 s + all sessions 5 s"
  if [ -n "${A_SESS:-}" ] && [ -f "$A_SESS" ]; then
    for i in $(seq 1 24); do stable_mtime "$A_SESS" 10 && break; sleep 5; [ $i -eq 24 ] && { say "STALLED: A not quiescent in 2 min"; return 1; }; done
  fi
  [ "$MODE" = test ] && return 0   # dry-run: skip the machine-wide check (poller noise would false-fail it)
  for i in $(seq 1 12); do
    grow=0
    for f in $(ls -t /home/goblin/.pi/agent/sessions/*/*.jsonl 2>/dev/null | head -6); do
      m1=$(stat -c %Y "$f"); sleep 5; [ "$(stat -c %Y "$f")" != "$m1" ] && grow=1
    done
    [ $grow -eq 0 ] && { say "quiescence ok"; return 0; }
  done
  say "STALLED: sessions never quiescent (12 x 5 s)"; return 1
}

# ---- tier 1: no flip --------------------------------------------------------
if [ "$MODE" = tier1 ]; then
  [ -n "$BATCH" ] || { say "tier1 needs batch="; exit 1; }
  say "tier1: detaching batch under $(mode_now) (no mode flip)"
  setsid nohup bash -c "
    $BATCH
    if [ \$? -eq 0 ]; then echo \"state=done\" > '$STATE'; else echo \"state=failed\" > '$STATE'; fi
    date -Is >> '$STATE'
  " > "$STATE_DIR/$SPECNAME.batch.log" 2>&1 </dev/null &
  # fall through to wait + typer (identical to tier2 minus the flip)
fi

# ---- tier 2: the chain ------------------------------------------------------
RESTARTS=0
if [ "$MODE" = tier2 ] || [ "$MODE" = test ]; then
  [ "$MODE" = tier2 ] && { [ -n "$TASK" ] || { say "tier2 needs task="; exit 1; }; }
  quiesce || { echo "state=stalled" > "$STALLED"; exit 1; }
  if [ "$MODE" = test ]; then
    say "TEST: skipping real 100k switch"
  else
    say "switch 262k -> 100k (--force, no --api: :8000 untouched)"
    ( cd "$NW" && ./qwen-switch.sh 100k --force ) >> "$LOG" 2>&1 || { echo "state=stalled-switch-down" > "$STALLED"; exit 1; }
  fi
  # open C: visible terminal, shell wrapper around pi (wrapper owns the state file)
  if [ "$MODE" = test ]; then
    # LLM-free test: C is a plain shell doing a fake task; state file still written by the wrapper
    say "opening C terminal (title GPU-$SPECNAME) — TEST: plain shell, no pi"
    setsid nohup gnome-terminal --title "GPU-$SPECNAME" -- bash -c "
      echo 'state=running' > '$STATE'
      sleep 5
      echo 'test report for $SPECNAME' > '$REPORT'
      echo 'state=done' > '$STATE'
      date -Is >> '$STATE'
    " >/dev/null 2>&1 &
  else
    say "opening C terminal (title GPU-$SPECNAME) with task + wrapper"
    setsid nohup gnome-terminal --title "GPU-$SPECNAME" -- bash -c "
      CID=\"c-$(basename "$SPECNAME")-\$(date +%s)\"
      pi -p --session-id \"\$CID\" \"\$0\" >/dev/null 2>&1
      rc=\$?
      ls -t /home/goblin/.pi/agent/sessions/*/*\"\$CID\".jsonl 2>/dev/null | head -1 > '$STATE_DIR/c_session'
      [ \$rc -eq 0 ] && echo \"state=done\" > '$STATE' || echo \"state=failed\" > '$STATE'
      date -Is >> '$STATE'
    " "$TASK" >/dev/null 2>&1 &
  fi
fi

# ---- wait loop: state + liveness + heartbeat --------------------------------
say "waiting for state ($STATE), heartbeat ${ETA}s, liveness :18080"
t0=$(date +%s)
while [ ! -f "$STATE" ]; do
  sleep 20
  now=$(date +%s)
  if [ $(( now - t0 )) -gt "$ETA" ]; then
    say "STALLED: no state file after ${ETA}s heartbeat"; echo "state=stalled-hb ts=$(date -Is)" > "$STALLED"; break
  fi
  if ! health; then
    if [ $RESTARTS -lt 2 ]; then
      RESTARTS=$(( RESTARTS + 1 ))
      say "MODEL-DOWN in chain: ninfer_restart.sh (attempt $RESTARTS/2)"
      ( "$REPO/tools/master-work/ninfer_restart.sh" ) >> "$LOG" 2>&1
    else
      say "STALLED: model dead after 2 restart attempts"; echo "state=stalled-model ts=$(date -Is)" > "$STALLED"; break
    fi
  fi
done
STATEV=$(sed -n 's/^state=\([^ ]*\).*/\1/p' "$STATE" 2>/dev/null | head -1)

# ---- switch-back (absorbs D) ------------------------------------------------
if { [ "$MODE" = tier2 ] || [ "$MODE" = test ]; } && [ -n "${STATEV:-}" ]; then
  if [ "$MODE" = test ]; then
    say "TEST: skipping real 262k switch-back"
    echo "mode=262k" > /tmp/gpu_handoff_test_mode   # typer gate reads this in test mode
  else
    say "switch-back 100k -> 262k (PI_SESSION_FILE=C transcript, --force backstop)"
    # C's transcript: the wrapper recorded it under a deterministic session id
    # (newest-file fallback is wrong here — the MASTER_WORK poller spawns a-*
    # one-shots in the same window and would win the "newest" race)
    CSESS=$(cat "$STATE_DIR/c_session" 2>/dev/null)
    [ -n "$CSESS" ] || { CSESS=$(ls -t /home/goblin/.pi/agent/sessions/*/*.jsonl 2>/dev/null | head -1); say "c_session missing — newest-file fallback"; }
    say "switch-back reference: $CSESS"
    ( cd "$NW" && PI_SESSION_FILE="$CSESS" ./qwen-switch.sh 262k --force ) >> "$LOG" 2>&1 \
      || { echo "state=stalled-switch-back" > "$STALLED"; exit 1; }
  fi
fi

# ---- typer: gated, one-shot, no-vision ---------------------------------------
TYPE_W=""
type_gate_pass() {
  [ "${STATEV:-}" = done ] || return 1
  if [ "$MODE" = test ]; then grep -q 'mode=262k' /tmp/gpu_handoff_test_mode || return 1
  else [ "$(mode_now)" = 262k ] || return 1; fi
  health || return 1
  [ -f "$REPORT" ] || return 1
  stable_mtime "$REPORT" 30 || return 1          # report not still being written
  local w
  if [ -n "${A_WIN:-}" ]; then w=$A_WIN   # primary: id captured by A at handoff
  else w=$(xdotool search --name "$A_TITLE" 2>/dev/null | head -1); fi   # --name only: the --class combo misses gnome-terminal windows (verified 2026-09-08)
  [ -n "$w" ] || return 1
  xdotool getwindowgeometry "$w" >/dev/null 2>&1 || return 1
  [ -n "${A_SESS:-}" ] && [ -f "$A_SESS" ] && { stable_mtime "$A_SESS" 10 || return 1; }  # A idle
  [ -f "$STATE_DIR/$SPECNAME.typed" ] && return 1
  TYPE_W=$w
  return 0
}

say "typer: gated type into window '$A_TITLE'"
typed=0
for i in $(seq 1 36); do
  if type_gate_pass; then
    xdotool windowactivate --sync "$TYPE_W" 2>/dev/null
    if [ "${STATEV:-}" = done ]; then
      say "typing resume line (once)"; xdotool type --delay 40 "$RESUME" && xdotool key Return
    else
      say "typing FAILURE line (state=$STATEV)"; xdotool type --delay 40 "GPU handoff $SPECNAME FAILED (state=$STATEV; see $LOG + $STALLED). Inspect and re-launch or abort." && xdotool key Return
    fi
    touch "$STATE_DIR/$SPECNAME.typed"; typed=1; break
  fi
  sleep 15
done
[ "$typed" = 1 ] || { say "typer: gate never passed (window '$A_TITLE' absent or gate open) — owner types: $RESUME"; echo "state=untyped resume=$RESUME" >> "${STALLED:-$STATE_DIR/$SPECNAME.flag}"; }
say "chain complete (state=${STATEV:-unknown})"