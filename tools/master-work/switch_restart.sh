#!/bin/bash
# switch_restart.sh <mode> <resume_msg_file> <old_pi_pid>
#
# The full "close pi → switch ninfer → come back to pi" flow in ONE detached
# helper (owner 2026-09-09/10: "this should all have happened with a
# terminal command or a script — you were doing this flawlessly yesterday" =
# pi_restart.sh's kill+relaunch half; this adds the switch, in the only safe
# order). Order matters — the 2026-09-10 00:3x incident: an INLINE switch
# from a running session whose context (~400k) exceeds the target dial (102k)
# strands that session (no model, so it can never launch the restart helper;
# the owner had to restore 262k by hand). So:
#   1) exit pi first (short grace for flush)
#   2) switch the model (30-60 s reload; pi is already out, so nothing is
#      stranded mid-reload)
#   3) come back: tmux + pi + typed resume line, verified by capture-pane
#
# Launch it detached so the calling session can die mid-tool-call:
#   setsid nohup bash tools/master-work/switch_restart.sh 100k /tmp/resume_msg.txt $(pgrep -x pi | head -1) < /dev/null > /dev/null 2>&1 &
# The helper survives that death (setsid) and finishes the whole flow.
# Attach to the new pi: DISPLAY=:0 setsid gnome-terminal -- tmux attach -t pi-csm
# Log: /tmp/switch_restart.log
set -u
MODE=${1:?mode (262k|100k|150k)}
MSG=${2:?resume msg file (its first line is typed into the new pi)}
OLD=${3:?old pi pid — verified from pgrep, never from memory}
SESS=${SESS:-pi-csm}
DIR=${DIR:-/home/goblin/ScriptEngine}
GRACE=${GRACE:-5}
LOG=${LOG:-/tmp/switch_restart.log}
exec >>"$LOG" 2>&1
say() { echo "[$(date '+%F %T')] $*"; }
say "start: mode=$MODE msg=$MSG old_pid=$OLD"

# 1) exit pi
sleep "$GRACE"
if kill -0 "$OLD" 2>/dev/null; then kill "$OLD"; say "TERM -> $OLD"; fi
for _ in $(seq 1 20); do kill -0 "$OLD" 2>/dev/null || break; sleep 1; done
if kill -0 "$OLD" 2>/dev/null; then say "still alive — KILL -9 $OLD"; kill -9 "$OLD"; sleep 1; fi
say "old pi gone"

# 2) switch the model. --force is deliberate here: the flow is always a
#    handoff (fresh pi resumes from plan/SWITCHPOINT.md), and the old session
#    may exceed the target dial (that is usually WHY we are switching).
#    :8000 placement is decided by qwen-switch's headroom rule (--api).
cd /home/goblin/ninfer-work || { say "ERROR: no ninfer-work dir"; exit 1; }
if ! ./qwen-switch.sh "$MODE" --api --force; then
  say "ERROR: switch failed — model left as-is; inspect the qwen logs, then re-run this helper"
  exit 1
fi
say "model switched to $MODE"

# 3) come back to pi (tmux: server-side send-keys is the reliable path —
#    the 2026-09-09 01:49 incident retired xdotool)
tmux kill-session -t "$SESS" 2>/dev/null
tmux new-session -d -s "$SESS" -c "$DIR" pi
say "tmux session $SESS launched"
NEW=""
for _ in $(seq 1 30); do
  NEW=$(pgrep -x pi | grep -vxF "$OLD" | head -1)
  [ -n "$NEW" ] && break
  sleep 2
done
if [ -z "$NEW" ]; then say "ERROR: no new pi process after 60 s — check the tmux session"; exit 1; fi
say "new pi pid=$NEW"
sleep 12   # let the TUI come up before typing
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
say "done: mode=$MODE new pi pid=$NEW (attach: DISPLAY=:0 setsid gnome-terminal -- tmux attach -t $SESS)"