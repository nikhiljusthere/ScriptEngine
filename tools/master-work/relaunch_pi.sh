#!/bin/bash
# relaunch_pi.sh <old_pi_pid> <resume_msg_file>
#
# The "come back" half of the model-driven switch flow (owner 2026-09-10).
# The switch shell (switch_restart2.sh) already switched the model and sent
# the LLM call; the MODEL launches this script. We do: grace-kill the old pi
# -> tmux relaunch -> wait for TUI ready -> type the resume line ->
# capture-pane proof. (Same mechanics as switch_restart.sh, minus the
# switch step — extracted so both flows share one proven relaunch.)
set -u
OLD=${1:?old pi pid}
MSG=${2:?resume msg file (its first line is typed into the new pi)}
SESS=${SESS:-pi-csm}
DIR=${DIR:-/home/goblin/ScriptEngine}
GRACE=${GRACE:-5}
LOG=${LOG:-/tmp/switch_restart.log}
exec >>"$LOG" 2>&1
say() { echo "[$(date '+%F %T')] $*"; }
say "relaunch start: old_pid=$OLD msg=$MSG"

# grace, then kill the old pi
sleep "$GRACE"
if kill -0 "$OLD" 2>/dev/null; then kill "$OLD"; say "TERM -> $OLD"; fi
for _ in $(seq 1 20); do kill -0 "$OLD" 2>/dev/null || break; sleep 1; done
if kill -0 "$OLD" 2>/dev/null; then say "still alive — KILL -9 $OLD"; kill -9 "$OLD"; sleep 1; fi
say "old pi gone"

# come back to pi (tmux: server-side send-keys is the reliable path —
# the 2026-09-09 01:49 incident retired xdotool)
tmux kill-session -t "$SESS" 2>/dev/null
tmux new-session -d -s "$SESS" -c "$DIR" pi
say "tmux session $SESS launched"
NEW=""
for _ in $(seq 1 60); do
  # Wait until the pane's process is actually 'pi' (sh -c 'pi' execs in
  # place; a pgrep before spawn mislabels older pi's — 2026-09-10 00:58).
  PANE=$(tmux display-message -p -t "$SESS" '#{pane_pid}' 2>/dev/null || true)
  if [ -n "$PANE" ] && [ "$(ps -o comm= -p "$PANE" 2>/dev/null)" = "pi" ]; then
    NEW=$PANE; break
  fi
  sleep 1
done
[ -z "$NEW" ] && NEW=$(pgrep -x pi | grep -vxF "$OLD" | sort -n | tail -1)
[ -z "$NEW" ] && { say "ERROR: no new pi process after 60 s — check the tmux session"; exit 1; }
say "new pi pid=$NEW"
# any pi that survived the switch holds the pre-switch window in memory
# (pi snapshots contextWindow at startup — 2026-09-10 01:1x): warn.
STALE=$(pgrep -x pi | grep -vx "$NEW" | grep -vx "$OLD" | tr '\n' ' ')
[ -n "$STALE" ] && say "WARNING: other pi(s) alive: $STALE — any started pre-switch still holds the old window; exit each, then 'pi -c'"
# wait for the TUI to be ready before typing: the status line carries the
# model name (the old fixed 12 s sleep lost the race — 2026-09-10 01:0x).
for _ in $(seq 1 30); do
  tmux capture-pane -t "$SESS" -p 2>/dev/null | grep -q 'qwen3.8' && break
  sleep 2
done
if [ -f "$MSG" ]; then
  LINE=$(head -1 "$MSG")
  tmux send-keys -t "$SESS" "$LINE" Enter
  say "resume line sent to $NEW: ${LINE:0:80}..."
else
  say "no msg file — new pi starts bare"
fi
# verify what actually landed (01:49 lesson: never trust the send's rc)
sleep 8
say "--- capture-pane (last 6 lines):"
tmux capture-pane -t "$SESS" -p | tail -6 | sed 's/^/    | /'
say "relaunch done: new pi pid=$NEW (attach: DISPLAY=:0 setsid gnome-terminal -- tmux attach -t $SESS)"