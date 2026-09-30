#!/bin/bash
# switch_q8_oc.sh <old_oc_pid> <old_shell_pid|none> [--dry-run]
#
# Q8 twin of tools/master-work/switch_restart3_oc.sh (JJK handoff 2026-09-29):
# one detached shell switches opencode's model from the ninfer NVFP4 server
# (:18080) to the llama.cpp Q8_0 server (:8090) and relaunches THIS
# opencode's terminal window, so opencode continues the SAME session (pinned
# -s, not -c — 2026-09-21 incident) after the model reload.
#
# Parts:
#   1. guard sleep (the agent turn still streaming must finish first), then
#      ninfer-work/ninfer-stop.sh — instant unload of :18080 (Q6 holds ~24.9 GiB
#      and Q8 cannot load beside it — 2026-09-29 incident: Q6 was raw-restarted
#      at 23:26:59 and every Q8 load attempt OOMed)
#   2. serve_q8.sh (NP=6 CTX=65536, Q8_0 KV per owner; NGL ladder 999 -> 60 ->
#      52 -> 44 on OOM — the hybrid GDN rs cache ~3.6 GiB pins to the model
#      device, so even Q8 KV may need a few layers offloaded), bounded
#      :8090/health poll; log /tmp/jjk100/q8_server.log
#   3. internal LLM call (curl :8090) — proves the model live; bounded
#      /v1/models poll fallback
#   4. restart the Q8 watchdog (q6_watchdog.sh; relaunch line gets NGL=<n>
#      if the server needed partial offload)
#   5. UPDATE the session_v2 row's model to llamacpp-q8 (the session is
#      PERSISTED with the old model — opencode -s resumes the model stored on
#      the row, so a dead Q6 provider would be resumed otherwise), then
#      relaunch: new gnome-terminal window in the old cwd running
#      `opencode -s <pinned session>`, wait for the new pid, TERM ->
#      verify -> KILL -9 the old opencode + old window shell, then type the
#      switchpoint-resume prompt into the new TUI (xdotool, verified via a
#      new message=process line in opencode's log) so the work continues
#      instead of idling.
#
# Owner standard (oc-switch skill): the LLM readiness call is made INTERNALLY
# by this shell, never typed into any pane; the resume prompt is the one
# thing typed, into the NEW window only; the agent that launches this ends
# its turn immediately — the new opencode picks the session up on its own.
#
# Launch (the agent's last act):
#   setsid nohup bash /home/goblin/ScriptEngine/tools/train/ops/switch_q8_oc.sh \
#     <opencode pid> <shell pid|none> < /dev/null > /dev/null 2>&1 &
# Log: /tmp/jjk100/switch_q8_oc.log
set -u
OLD_OC=${1:?old opencode pid}
OLD_SHELL=${2:?old terminal shell pid, or "none"}
DRY=0
[ "${3:-}" = "--dry-run" ] && DRY=1
LOG=${LOG:-/tmp/jjk100/switch_q8_oc.log}
exec >>"$LOG" 2>&1
say() { echo "[$(date '+%F %T')] $*"; }
say "switch-q8-oc start: old_oc=$OLD_OC old_shell=$OLD_SHELL dry=$DRY"

# pinned to THIS session (the one being switched from), not the
# newest-in-directory — a sibling window can steal `-c` during the reload.
# 2026-09-30 ~06:5x: updated for the post-builder Q8 switch — the window
# moved to session "JJK sentence-grid window builder" (created 06:31 on
# ninfer-27b after the 06:1x Q8 unload); the old pin below is the dead
# 06:0x "Scratch windowing fix" Q8 session.
PINNED_SES=ses_f102b8651ffeUiOEPE6K6diaYv
OPS=/home/goblin/ScriptEngine/tools/train/ops

if [ "$DRY" -eq 1 ]; then
  say "DRY RUN — no process or GPU changes."
  echo "  would: guard sleep 45 s (launching turn finishes streaming)"
  echo "  would: part 1 ninfer-stop.sh (instant unload of :18080)"
  echo "  would: part 2 $OPS/serve_q8.sh NP=6 CTX=65536, Q8 KV (NGL ladder 999->60->52->44 on OOM) + bounded :8090/health poll"
  echo "  would: part 3 internal LLM call (curl :8090) -> readiness trigger"
  echo "  would: part 4 restart $OPS/q6_watchdog.sh (NGL=<n> on its relaunch line if needed)"
  echo "  would: part 5 UPDATE session_v2 model -> llamacpp-q8/qwen3.8-27b-q8 (row is persisted with the old model)"
  echo "  would: new window in old cwd: opencode -s $PINNED_SES (session_v2 db-lookup fallback)"
  echo "  would: TERM/KILL old oc $OLD_OC + shell ${OLD_SHELL}"
  echo "  would: type switchpoint-resume prompt into the new TUI (auto-continue)"
  exit 0
fi

mkdir -p /tmp/jjk100

# guard: the agent turn that launched this script is still streaming its
# final message on Q6 — do NOT kill :18080 until it has finished (45 s).
say "guard: sleeping 45 s for the launching turn to finish streaming"
sleep 45

# part 1: unload ninfer — opencode's current model dies at this moment
# (the relaunch in part 5 is why that is safe)
if ! /home/goblin/ninfer-work/ninfer-stop.sh; then say "ERROR: ninfer-stop failed"; exit 1; fi
say "part1: ninfer unloaded"

# part 2: start Q8. Measured-best FIRST (sweep_q8.sh 2026-09-30): NP=2 makes
# the GDN rs cache (74.8 MiB per GDN layer, scales with SLOT count) fit, so
# full offload works: 92.52 t/s vs 19.03 for the old NP=6/NGL=60 prod.
# NP=6 ladder is the fallback in case the card's fit changed.
NGLOK=""
setsid nohup "$OPS/serve_q8_best.sh" > /tmp/jjk100/q8_server.log 2>&1 < /dev/null &
PID=$!
ok=0
for i in $(seq 1 60); do
  curl -sf -m 3 http://127.0.0.1:8090/health >/dev/null 2>&1 && { ok=1; break; }
  kill -0 "$PID" 2>/dev/null || break   # server died (CUDA OOM) — stop waiting
  sleep 10
done
if [ "$ok" -eq 1 ]; then
  NGLOK="best"
  say "part2: :8090 healthy (serve_q8_best NP=2 NGL=999, server pid $PID)"
else
  say "part2: serve_q8_best did not come up healthy — NP=6 ladder fallback"
  if kill -0 "$PID" 2>/dev/null; then
    kill -9 "$PID" 2>/dev/null; sleep 5
    say "  killed stale attempt (pid $PID) before the next one"
  fi
  for NGLCAND in 999 60 52 44; do
    NGL=$NGLCAND NP=6 CTX=65536 setsid nohup "$OPS/serve_q8.sh" \
      > /tmp/jjk100/q8_server.log 2>&1 < /dev/null &
    PID=$!
    ok=0
    for i in $(seq 1 60); do
      curl -sf -m 3 http://127.0.0.1:8090/health >/dev/null 2>&1 && { ok=1; break; }
      kill -0 "$PID" 2>/dev/null || break
      sleep 10
    done
    if [ "$ok" -eq 1 ]; then
      NGLOK=$NGLCAND
      say "part2: :8090 healthy (NGL=$NGLCAND, server pid $PID)"
      break
    fi
    say "part2: NGL=$NGLCAND did not come up healthy — see /tmp/jjk100/q8_server.log"
    if kill -0 "$PID" 2>/dev/null; then
      kill -9 "$PID" 2>/dev/null; sleep 5
      say "  killed stale attempt (pid $PID) before the next one"
    fi
  done
fi
if [ -z "$NGLOK" ]; then
  say "ERROR: Q8 failed to load (best + NGL=999/60/52/44) — old opencode left ALIVE; owner must inspect /tmp/jjk100/q8_server.log"
  exit 1
fi

# part 3: internal LLM call — proves the model answers (bounded /v1/models
# poll fallback, as in the pi helper's skip-LLM variant)
if curl -s -m 90 http://127.0.0.1:8090/v1/chat/completions \
     -H 'Content-Type: application/json' \
     -d '{"model":"qwen3.8-27b-q8","messages":[{"role":"user","content":"switch-q8 ready check"}],"max_tokens":4}' \
     | grep -q '"choices"'; then
  say "part3: internal LLM call answered — Q8 live, triggering relaunch"
else
  say "WARN: LLM call silent — bounded /v1/models poll fallback"
  for i in $(seq 1 240); do
    curl -sf -m 2 http://127.0.0.1:8090/v1/models >/dev/null 2>&1 && { say "  :8090 answering (poll)"; break; }
    sleep 0.5
  done
fi

# part 4: restart the Q8 watchdog (the 5090 drives the display; a long
# kernel can trip the CUDA launch-timeout watchdog and kill the server —
# 2026-09-29). If partial offload was needed, the relaunch line carries it.
if [ "$NGLOK" != "999" ]; then
  grep -q "NGL=$NGLOK NP=6" "$OPS/q6_watchdog.sh" || \
    sed -i "s/^      NP=6 CTX=65536 setsid/      NGL=$NGLOK NP=6 CTX=65536 setsid/" "$OPS/q6_watchdog.sh"
  say "part4: watchdog relaunch line now NGL=$NGLOK NP=6 CTX=65536"
fi
WDPID=$(pgrep -f 'tools/train/ops/q6_watchdog.sh' | head -1)
if [ -n "$WDPID" ]; then
  kill "$WDPID" 2>/dev/null; sleep 2
  say "part4: stopped old watchdog (pid $WDPID)"
fi
setsid nohup "$OPS/q6_watchdog.sh" > /tmp/jjk100/watchdog.out 2>&1 < /dev/null &
say "part4: watchdog restarted"

# part 5: relaunch — open the NEW window first; wait for the new opencode
# pid; let it read the session db; THEN kill the old opencode + old shell.
# Same ordering as relaunch_term.sh / switch_restart3_oc.sh, and the same
# TERM-verify-KILL -9 escalation (interactive bash survives SIGTERM here).
# session persistence lives in `session_v2` (the v1 `session` table is legacy
# and empty for current sessions; `project` has no directory column — the v1
# query below would have silently degraded to -c, the 2026-09-21 incident).
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
# window would come up on the (now dead) Q6 provider and the session would
# error on its first turn. Single-column UPDATE; the old TUI is idle between
# turns, so a 5 s busy timeout is enough.
python3 - "$SES" <<'PY'
import sqlite3, sys
sid = sys.argv[1]
db = sqlite3.connect("/home/goblin/.local/share/opencode/opencode.db", timeout=5)
cur = db.execute(
    "UPDATE session_v2 SET model=? WHERE id=?",
    ('{"id":"qwen3.8-27b-q8","providerID":"llamacpp-q8"}', sid))
db.commit()
print(f"session_v2 model -> llamacpp-q8 (rows={cur.rowcount})")
PY
say "part5: session row rebound to llamacpp-q8"
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
say "switch-q8-oc done: new opencode $NEW (resume $RESUME, NGL=$NGLOK, auto-continue typed)"