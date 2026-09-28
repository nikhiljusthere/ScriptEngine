#!/bin/bash
# switch_restart3_oc.sh <mode> <old_oc_pid> <old_shell_pid|none> [--dry-run]
#
# The opencode twin of switch_restart3.sh (the pi flow): one detached shell
# switches the Qwen context mode and relaunches THIS opencode's terminal
# window, so opencode continues the SAME session in a new window after the
# model reload. The resume is PINNED to the exact session id the old
# opencode was in (opencode -s; bare -c resumes the NEWEST session in the
# directory, which another window can steal during the reload — 2026-09-21
# incident: the new window "did not continue"). After the relaunch the
# switcher types the switchpoint-resume prompt into the new TUI (xdotool,
# verified via a new model turn in opencode's log) so the work continues
# instead of idling on the composer. Owner standard (qwen-switch skill,
# 2026-09-10): the LLM readiness call is made INTERNALLY by this shell
# (HTTP to :18080), never typed into any pane; the resume prompt is the one
# thing typed, into the NEW window only; the agent that launches this ends
# its turn immediately — the new opencode picks up on its own.
#
# Launch (the agent's last act):
#   setsid nohup bash tools/master-work/switch_restart3_oc.sh 262k \
#     <opencode pid> <shell pid|none> < /dev/null > /dev/null 2>&1 &
# Log: /tmp/switch_restart3_oc.log
set -u
MODE=${1:?mode (262k|100k|<raw token count>)}
OLD_OC=${2:?old opencode pid}
OLD_SHELL=${3:?old terminal shell pid, or "none"}
DRY=0
[ "${4:-}" = "--dry-run" ] && DRY=1
LOG=${LOG:-/tmp/switch_restart3_oc.log}
exec >>"$LOG" 2>&1
say() { echo "[$(date '+%F %T')] $*"; }
say "switch3-oc start: mode=$MODE old_oc=$OLD_OC old_shell=$OLD_SHELL dry=$DRY"
cd /home/goblin/ninfer-work || { say "ERROR: no ninfer-work dir"; exit 1; }

if [ "$DRY" -eq 1 ]; then
  say "DRY RUN — no process or GPU changes."
  echo "  would: part 1 ninfer-stop.sh (instant unload)"
  echo "  would: part 2 qwen-switch.sh $MODE --api (json sync + :8000 placement)"
  echo "  would: part 3 internal LLM call (curl :18080) -> readiness trigger"
  echo "  would: new window in old cwd: opencode -s <pinned session> (fallback -c)"
  echo "  would: type switchpoint-resume prompt into the new TUI (auto-continue)"
  echo "  would: TERM/KILL old oc $OLD_OC + shell ${OLD_SHELL}"
  exit 0
fi

# part 1: unload — fires instantly (marks qwen_mode.txt mode=off)
if ! ./ninfer-stop.sh; then say "ERROR: unload failed"; exit 1; fi
say "part1: unloaded"

# part 2: load — syncs pi models.json + repo opencode.json + global
# opencode.jsonc, health-polls :18080, places :8000, writes qwen_mode.txt
# + a machine line to plan/SWITCHPOINT.md's switch log.
if ! ./qwen-switch.sh "$MODE" --api; then say "ERROR: load failed — model left as-is; inspect the ninfer logs"; exit 1; fi
say "part2: loaded (mode=$MODE)"

# part 3: internal LLM call — proves the model live from inside the shell;
# its return is the trigger (bounded /v1/models poll fallback, as in the
# pi helper's skip-LLM variant).
if curl -s -m 90 http://127.0.0.1:18080/v1/chat/completions \
     -H 'Content-Type: application/json' \
     -d '{"model":"qwen3.8-27b-ninfer","messages":[{"role":"user","content":"switch3-oc ready check"}],"max_tokens":4}' \
     | grep -q '"choices"'; then
  say "part3: internal LLM call answered — model live, triggering relaunch"
else
  say "WARN: LLM call silent — bounded /v1/models poll fallback"
  for i in $(seq 1 240); do
    curl -s -m 2 http://127.0.0.1:18080/v1/models >/dev/null 2>&1 && { say "  :18080 answering (poll)"; break; }
    sleep 0.5
  done
fi

# relaunch: open the NEW window first; wait for the new opencode pid; let
# it read the session db; THEN kill the old opencode + old shell. Same
# ordering as relaunch_term.sh, and the same TERM-verify-KILL -9
# escalation (this machine's interactive bash survives SIGTERM — proven
# 2026-09-10, proven again today on shell 24567).
#
# Pin the resume to the exact session the OLD opencode was in, not the
# newest-in-directory. `opencode -c` resumes the most recently updated
# session in the cwd; if a second window/session was created in the same
# dir during this run's reload, `-c` lands on the wrong one (2026-09-21:
# new window opened but "did not continue" because it resumed a sibling
# session, not the one being switched). The session id is the newest
# session row in the opencode db whose project dir == the old opencode's
# cwd. Fall back to `-c` if we can't resolve it.
CWD=$(readlink "/proc/$OLD_OC/cwd" 2>/dev/null)
[ -n "$CWD" ] || CWD=/home/goblin/ScriptEngine
SES=$(python3 - "$CWD" <<'PY' 2>/dev/null
import sqlite3, sys
c = sys.argv[1]
db = sqlite3.connect("file:/home/goblin/.local/share/opencode/opencode.db?mode=ro", uri=True)
row = db.execute(
    "SELECT s.id FROM session s JOIN project p ON p.id = s.project_id "
    "WHERE p.directory = ? ORDER BY s.time_updated DESC LIMIT 1", (c,)
).fetchone()
print(row[0] if row else "")
PY
)
if [ -n "$SES" ]; then RESUME="-s $SES"; else RESUME="-c"; fi
say "resume target: $RESUME (cwd $CWD)"
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
# type/key (never --window). Prove the prompt took effect via a new
# `message=process` line in opencode's log (opencode logs nothing while
# idle); one retry if the keys did not land.
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
say "switch3-oc done: new opencode $NEW (resume $RESUME, auto-continue typed)"