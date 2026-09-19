#!/bin/bash
# switch_restart3_oc.sh <mode> <old_oc_pid> <old_shell_pid|none> [--dry-run]
#
# The opencode twin of switch_restart3.sh (the pi flow): one detached shell
# switches the Qwen context mode and relaunches THIS opencode's terminal
# window, so opencode continues the SAME session (opencode -c) in a new
# window after the model reload. Owner standard (qwen-switch skill,
# 2026-09-10): the LLM readiness call is made INTERNALLY by this shell
# (HTTP to :18080), never typed into any pane; the agent that launches
# this ends its turn immediately — the new opencode resumes on its own.
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
  echo "  would: new window: cd /home/goblin/ScriptEngine && exec opencode -c"
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
PRE=" $(pgrep -x opencode | tr '\n' ' ')"
DISPLAY=:0 setsid gnome-terminal -- bash -lc "cd /home/goblin/ScriptEngine && exec /home/goblin/.opencode/bin/opencode -c" &
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
say "switch3-oc done: new opencode $NEW (session resumed via opencode -c)"