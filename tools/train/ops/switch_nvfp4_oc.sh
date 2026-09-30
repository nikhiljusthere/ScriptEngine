#!/bin/bash
# switch_nvfp4_oc.sh <old_oc_pid> <old_shell_pid|none> [--dry-run]
#
# Reverse twin of switch_q8_oc.sh (2026-09-30): one detached shell switches
# opencode's model from the llama.cpp Q8_0 server (:8090) back to the ninfer
# NVFP4 27B "100k" profile (:18080, serve_100k.sh) and relaunches THIS
# opencode's terminal window, so opencode continues the SAME session (pinned
# -s, not -c — 2026-09-21 incident) after the model reload.
#
# Why: owner conditional 2026-09-30 ~07:xx — if the window-100 foundational
# code is complete, go to 35B A3B for the from-scratch window run; if not,
# back to NVFP4 to finish the code. Day 1 (builder) is committed in
# 1397ec34, but Day 2 (engine integration: _windows replacement, packed reads
# -> labeled grid windows, G1 at window level) and Day 3 (emit_windows.py,
# rekey_gold.py, pool regeneration) are NOT written. => NVFP4.
#
# Parts:
#   1. guard sleep (the agent turn still streaming must finish first — it is
#      streaming on Q8 :8090, which part 2 kills)
#   2. stop the Q8 watchdog (q6_watchdog.sh) FIRST — it restarts a dead :8090
#      within ~50 s — then the Q8 llama-server; wait for the card to clear
#      (< 2 GiB; Q8 holds ~31.5 GiB and the 27B NVFP4 cannot load beside it)
#   3. serve_100k.sh (ninfer NVFP4 27B, --max-context 102400, :18080), bounded
#      :18080/v1/models poll (same 150 s bound as qwen-switch.sh); log
#      /home/goblin/ninfer-work/logs/serve_100k.log
#   4. internal LLM call (curl :18080) — proves the model answers; bounded
#      /v1/models poll fallback
#   5. qwen_mode.txt -> mode=on ctx=102400 (so the master-work poller
#      ninfer_restart.sh sees the target state) + machine line in
#      plan/SWITCHPOINT.md (same convention qwen-switch.sh appends)
#   6. UPDATE the session_v2 row's model to ninfer-27b (the session is
#      PERSISTED with the old model — opencode -s resumes the model stored on
#      the row, so a dead llamacpp-q8 provider would be resumed otherwise),
#      then relaunch: new gnome-terminal window in the old cwd running
#      `opencode -s <pinned session>`, wait for the new pid, TERM ->
#      verify -> KILL -9 the old opencode + old window shell, then type the
#      switchpoint-resume prompt into the new TUI (xdotool, verified via a
#      new message=process line in opencode's log) so the work continues
#      instead of idling.
#
# NOT touched (deliberately): the :8000 ScriptEngine API (down at switch time;
# the 100k profile has room for it later — start it with qwen-switch.sh --api
# or the master-work tooling), the 35B watchdog (killed before the Q8 switch;
# 35B is the NEXT phase, not this one), opencode.json / opencode.jsonc
# context (ninfer-27b already at 102400 in both — verified 2026-09-30).
#
# Owner standard (oc-switch skill): the LLM readiness call is made INTERNALLY
# by this shell, never typed into any pane; the resume prompt is the one
# thing typed, into the NEW window only; the agent that launches this ends
# its turn immediately — the new opencode picks the session up on its own.
#
# Launch (the agent's last act):
#   setsid nohup bash /home/goblin/ScriptEngine/tools/train/ops/switch_nvfp4_oc.sh \
#     <opencode pid> <shell pid|none> < /dev/null > /dev/null 2>&1 &
# Log: /tmp/jjk100/switch_nvfp4_oc.log
set -u
OLD_OC=${1:?old opencode pid}
OLD_SHELL=${2:?old terminal shell pid, or "none"}
DRY=0
[ "${3:-}" = "--dry-run" ] && DRY=1
LOG=${LOG:-/tmp/jjk100/switch_nvfp4_oc.log}
exec >>"$LOG" 2>&1
say() { echo "[$(date '+%F %T')] $*"; }
say "switch-nvfp4-oc start: old_oc=$OLD_OC old_shell=$OLD_SHELL dry=$DRY"

# pinned to THIS session (the one being switched from), not the
# newest-in-directory — a sibling window can steal `-c` during the reload.
# Same session through both switches: created 06:31 on ninfer-27b, moved to
# Q8 at ~06:5x (switch_q8_oc.sh), moving back now.
PINNED_SES=ses_f102b8651ffeUiOEPE6K6diaYv
NINFER=/home/goblin/ninfer-work
SERVE_LOG=$NINFER/logs/serve_100k.log

if [ "$DRY" -eq 1 ]; then
  say "DRY RUN — no process or GPU changes."
  echo "  would: guard sleep 45 s (launching turn finishes streaming on Q8)"
  echo "  would: part 2 stop q6_watchdog.sh FIRST, then the Q8 llama-server (:8090); wait for card < 2 GiB"
  echo "  would: part 3 $NINFER/serve_100k.sh (NVFP4 27B, ctx 102400, :18080) + bounded :18080/v1/models poll (150 s)"
  echo "  would: part 4 internal LLM call (curl :18080) -> readiness trigger"
  echo "  would: part 5 qwen_mode.txt mode=on ctx=102400 + SWITCHPOINT.md machine line"
  echo "  would: part 6 UPDATE session_v2 model -> ninfer-27b/qwen3.8-27b-ninfer (row is persisted with the old model)"
  echo "  would: new window in old cwd: opencode -s $PINNED_SES (session_v2 db-lookup fallback)"
  echo "  would: TERM/KILL old oc $OLD_OC + shell ${OLD_SHELL}"
  echo "  would: type switchpoint-resume prompt into the new TUI (auto-continue)"
  exit 0
fi

mkdir -p /tmp/jjk100

# guard: the agent turn that launched this script is still streaming its
# final message on Q8 — do NOT kill :8090 until it has finished (45 s).
say "guard: sleeping 45 s for the launching turn to finish streaming"
sleep 45

# part 2: stop Q8 — watchdog FIRST (it restarts a dead :8090 within ~50 s),
# then the server. The agent has NO model from here until the health check
# passes (the relaunch in part 6 is why that is safe).
WDPID=$(pgrep -f 'tools/train/ops/q6_watchdog.sh' | head -1)
if [ -n "$WDPID" ]; then
  kill "$WDPID" 2>/dev/null
  for i in $(seq 1 10); do kill -0 "$WDPID" 2>/dev/null || break; sleep 1; done
  if kill -0 "$WDPID" 2>/dev/null; then kill -9 "$WDPID" 2>/dev/null; sleep 1; fi
  say "part2: Q8 watchdog stopped (pid $WDPID)"
else
  say "part2: no Q8 watchdog running"
fi
Q8PID=$(pgrep -f 'llama-server -m /mnt/PROJECTS/models/qwen3.8-27b-q8' | head -1)
if [ -n "$Q8PID" ]; then
  kill "$Q8PID" 2>/dev/null
  for i in $(seq 1 30); do kill -0 "$Q8PID" 2>/dev/null || break; sleep 0.5; done
  if kill -0 "$Q8PID" 2>/dev/null; then
    say "part2: Q8 server still up; SIGKILL"
    kill -9 "$Q8PID" 2>/dev/null
  fi
  say "part2: Q8 server stopped (pid $Q8PID)"
else
  say "part2: no Q8 server running"
fi
# wait for the card to clear (bounded, status every ~10 s)
for i in $(seq 1 36); do
  USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
  [ "$USED" -lt 2048 ] && { say "part2: card clear (${USED} MiB used)"; break; }
  [ $(( i % 10 )) -eq 0 ] && say "  waiting for GPU to clear… ${USED} MiB still used"
  sleep 10
done
USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
if [ "$USED" -ge 2048 ]; then
  say "ERROR: GPU still holds ${USED} MiB (another process? nvidia-smi) — old opencode left ALIVE; owner must inspect"
  exit 1
fi

# part 3: start the 27B NVFP4 100k profile (same serve script + log + poll
# bound qwen-switch.sh uses for 100k)
say "part3: loading Qwen NVFP4 ctx=102400 (model reload ~30-60 s)…"
setsid nohup "$NINFER/serve_100k.sh" > "$SERVE_LOG" 2>&1 < /dev/null &
PID=$!
ok=0
for i in $(seq 1 600); do
  if curl -s -m 2 http://127.0.0.1:18080/v1/models >/dev/null 2>&1; then ok=1; break; fi
  kill -0 "$PID" 2>/dev/null || break   # serve died (OOM?) — stop waiting
  [ $(( i % 40 )) -eq 0 ] && say "  … ${i}x0.25s: :18080 not answering yet"
  sleep 0.25
done
if [ "$ok" -ne 1 ]; then
  say "ERROR: :18080 did not come up — old opencode left ALIVE; inspect $SERVE_LOG (tail below)"
  tail -20 "$SERVE_LOG" 2>/dev/null | sed 's/^/  | /'
  exit 1
fi
grep -E "model loaded|KV capacity|listening" "$SERVE_LOG" 2>/dev/null | head -5 | sed 's/^/  | /'
say "part3: :18080 healthy (serve_100k, serve pid $PID)"

# part 4: internal LLM call — proves the model answers (bounded /v1/models
# poll fallback, as in the pi helper's skip-LLM variant)
if curl -s -m 90 http://127.0.0.1:18080/v1/chat/completions \
     -H 'Content-Type: application/json' \
     -d '{"model":"qwen3.8-27b-ninfer","messages":[{"role":"user","content":"switch-nvfp4 ready check"}],"max_tokens":4}' \
     | grep -q '"choices"'; then
  say "part4: internal LLM call answered — NVFP4 live, triggering relaunch"
else
  say "WARN: LLM call silent — bounded /v1/models poll fallback"
  for i in $(seq 1 240); do
    curl -sf -m 2 http://127.0.0.1:18080/v1/models >/dev/null 2>&1 && { say "  :18080 answering (poll)"; break; }
    sleep 0.5
  done
fi

# part 5: state file + switch log (same convention qwen-switch.sh writes)
NEWQPID=$(pgrep -f 'qwen3_8_27b_nvfp4.ninfer' | head -1)
FREE=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
printf 'mode=on ctx=102400 qwen_pid=%s ts=%s free_mib=%s api=off\n' \
  "${NEWQPID:-?}" "$(date -Is)" "$FREE" > "$NINFER/qwen_mode.txt"
SP=/home/goblin/ScriptEngine/plan/SWITCHPOINT.md
if [ -f "$SP" ]; then
  echo "- $(date -Is) switch-nvfp4-oc: ctx=102400 (mode on), api=off, free=${FREE}MiB, qwen_pid=${NEWQPID:-?}" >> "$SP"
fi
say "part5: qwen_mode.txt mode=on ctx=102400 (pid ${NEWQPID:-?}, free=${FREE}MiB)"

# part 6: relaunch — open the NEW window first; wait for the new opencode
# pid; let it read the session db; THEN kill the old opencode + old shell.
# Same ordering as switch_q8_oc.sh, and the same TERM-verify-KILL -9
# escalation (interactive bash survives SIGTERM here).
CWD=$(readlink "/proc/$OLD_OC/cwd" 2>/dev/null)
[ -n "$CWD" ] || CWD=/home/goblin/ScriptEngine
SES=$PINNED_SES
if ! python3 - "$CWD" "$SES" <<'PY' 2>/dev/null | grep -q ok
import sqlite3, sys
c, sid = sys.argv[1], sys.argv[2]
db = sqlite3.connect("file:/home/goblin/.local/share/opencode/opencode.db?mode=ro", uri=True)
row = db.execute(
    "SELECT 1 FROM session_v2 WHERE id = ? AND directory = ?", (sid, c)
).fetchone()
print("ok" if row else "")
PY
then
  say "pinned session not in db for $CWD — falling back to newest-in-directory"
  SES=$(python3 - "$CWD" <<'PY' 2>/dev/null
import sqlite3, sys
c = sys.argv[1]
db = sqlite3.connect("file:/home/goblin/.local/share/opencode/opencode.db?mode=ro", uri=True)
row = db.execute(
    "SELECT id FROM session_v2 WHERE directory = ? AND time_archived IS NULL "
    "ORDER BY time_updated DESC LIMIT 1", (c,)
).fetchone()
print(row[0] if row else "")
PY
  )
fi
if [ -n "$SES" ]; then RESUME="-s $SES"; else RESUME="-c"; fi
say "resume target: $RESUME (cwd $CWD)"

# rebind the resumed session to the NEW provider: opencode resumes the model
# STORED ON THE SESSION ROW, not the config default. Without this the new
# window would come up on the (now dead) llamacpp-q8 provider and the
# session would error on its first turn. Single-column UPDATE; the old TUI is
# idle between turns, so a 5 s busy timeout is enough.
python3 - "$SES" <<'PY'
import sqlite3, sys
sid = sys.argv[1]
db = sqlite3.connect("/home/goblin/.local/share/opencode/opencode.db", timeout=5)
cur = db.execute(
    "UPDATE session_v2 SET model=? WHERE id=?",
    ('{"id":"qwen3.8-27b-ninfer","providerID":"ninfer-27b"}', sid))
db.commit()
print(f"session_v2 model -> ninfer-27b (rows={cur.rowcount})")
PY
say "part6: session row rebound to ninfer-27b"
PRE=" $(pgrep -x opencode | tr '\n' ' ')"
DISPLAY=:0 setsid gnome-terminal -- bash -lc "cd '$CWD' && exec /home/goblin/.opencode/bin/opencode $RESUME" &
say "new opencode window launched"
NEW=""
for _ in $(seq 1 90); do
  for p in $(pgrep -x opencode); do
    case "$PRE" in *" $p "*) ;; *) NEW=$p; break 2;; esac
  done
  sleep 1
done
[ -z "$NEW" ] && { say "ERROR: no new opencode after 90 s — old opencode left ALIVE; inspect the new window"; exit 1; }
say "new opencode pid=$NEW"
sleep 5   # the new process must have the session db loaded before the old one dies

if kill -0 "$OLD_OC" 2>/dev/null; then kill "$OLD_OC"; say "TERM -> old oc $OLD_OC"; fi
for _ in $(seq 1 20); do kill -0 "$OLD_OC" 2>/dev/null || break; sleep 1; done
if kill -0 "$OLD_OC" 2>/dev/null; then kill -9 "$OLD_OC"; say "KILL -9 $OLD_OC"; fi
say "old oc gone"

if [ "$OLD_SHELL" != "none" ]; then
  kill "$OLD_SHELL" 2>/dev/null && say "TERM -> old shell $OLD_SHELL"
  for _ in $(seq 1 10); do kill -0 "$OLD_SHELL" 2>/dev/null || break; sleep 1; done
  if kill -0 "$OLD_SHELL" 2>/dev/null; then kill -9 "$OLD_SHELL" 2>/dev/null; sleep 1; say "KILL -9 -> old shell $OLD_SHELL (survived TERM)"; fi
  if kill -0 "$OLD_SHELL" 2>/dev/null; then say "ERROR: old shell $OLD_SHELL still alive — window not closed"; exit 1; fi
  say "old shell gone (window closed)"
else
  say "old window has no separate shell (exec chain) — it closes when the old opencode died"
fi

# auto-continue: type the switchpoint-resume prompt into the new TUI so the
# work continues instead of idling on the composer (owner rule 2026-09-21).
# vte key discipline from opencode-watch: windowactivate --sync, then plain
# type/key. Prove the prompt took effect via a new `message=process` line in
# opencode's log (opencode logs nothing while idle); one retry if the keys
# did not land.
sleep 3
W=""
for _ in $(seq 1 30); do
  W=$(DISPLAY=:0 xdotool search --name '^OC ' 2>/dev/null | tail -1)
  [ -n "$W" ] && break
  sleep 1
done
OCLOG="$HOME/.local/share/opencode/log/opencode.log"
PROMPT='Resume: read plan/SWITCHPOINT.md (if present) and execute its "first action on resume"; otherwise continue the current task. Do not idle.'
if [ -n "$W" ] && [ -f "$OCLOG" ]; then
  for attempt in 1 2; do
    MARK=$(grep -c 'message=process' "$OCLOG" || true)
    DISPLAY=:0 xdotool windowactivate --sync "$W"
    DISPLAY=:0 xdotool type --clearmodifiers "$PROMPT"
    DISPLAY=:0 xdotool key Return
    say "auto-continue: prompt typed into window $W (attempt $attempt)"
    ok=0
    for _ in $(seq 1 30); do
      [ "$(grep -c 'message=process' "$OCLOG" || true)" -gt "$MARK" ] && { ok=1; break; }
      sleep 1
    done
    [ "$ok" -eq 1 ] && { say "auto-continue: verified — new model turn started"; break; }
    say "WARN: no new model turn after attempt $attempt — keys may not have landed; owner may need to type the prompt"
  done
else
  say "WARN: OC window or opencode log not found — type the resume prompt into the new window manually"
fi
say "switch-nvfp4-oc done: new opencode $NEW (resume $RESUME, auto-continue typed)"
