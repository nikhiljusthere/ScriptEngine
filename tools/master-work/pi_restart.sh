#!/bin/bash
# pi_restart.sh — self-restart a pi session (detached helper, the agent never
# asks the owner). The new pi runs in a TMUX session: server-side send-keys
# is reliable, unlike xdotool's XSendEvent, which was silently dropped on
# 2026-09-09 01:49 (the typed `pi` never landed, the owner had to type it
# himself, and the helper log looked green because XSendEvent returns 0 even
# when the event is dropped).
#
# usage: pi_restart.sh <old_pi_pid> [tmux_session] [workdir] [msg_file] [exclude_pids...]
#   old_pi_pid  : exact pid to kill (verified, never a pattern)
#   tmux_session: default pi-csm
#   workdir     : default /home/goblin/ScriptEngine
#   msg_file    : file whose contents are typed as the resume line (one line)
#   exclude_pids: extra pids to ignore when finding the new pi (e.g. the
#                 A/B bay workers)
#
# Run it detached so it survives the tool call that launches it:
#   setsid nohup bash tools/master-work/pi_restart.sh $OLD_PID pi-csm /home/goblin/ScriptEngine /tmp/resume.txt < /dev/null > /dev/null 2>&1 &
#
# A visible window: open one attached to the session (the window closing
# never kills the session):
#   DISPLAY=:0 setsid gnome-terminal -- tmux attach -t pi-csm
#
# GRACE env: seconds before the kill (default 10 — owner rule 2026-09-09:
# restarts are immediate, max 10 s; let the dying session flush, no more
# stalling).
set -u
OLD=${1:?old pi pid}
SESS=${2:-pi-csm}
DIR=${3:-/home/goblin/ScriptEngine}
MSGFILE=${4:-}
shift $(( $# < 4 ? 0 : 4 ))
EXCL=("$OLD" "$@")
LOG=${LOG:-/tmp/pi_restart.log}
GRACE=${GRACE:-10}
exec >>"$LOG" 2>&1
say() { echo "[$(date '+%F %T')] $*"; }
say "start: old=$OLD sess=$SESS dir=$DIR msg=$MSGFILE grace=${GRACE}s"

sleep "$GRACE"
say "grace over"
if kill -0 "$OLD" 2>/dev/null; then
  kill "$OLD"
  say "TERM -> $OLD"
fi
for _ in $(seq 1 30); do
  kill -0 "$OLD" 2>/dev/null || break
  sleep 2
done
if kill -0 "$OLD" 2>/dev/null; then
  say "WARNING: $OLD still alive, KILL"
  kill -9 "$OLD"
fi
say "old pi gone"

# the new pi, in tmux (reliable)
tmux kill-session -t "$SESS" 2>/dev/null
tmux new-session -d -s "$SESS" -c "$DIR" "pi"
say "tmux session $SESS launched"
NEW=""
for _ in $(seq 1 30); do
  NEW=$(pgrep -x pi | grep -vxF -f <(printf '%s\n' "${EXCL[@]}") | head -1)
  [ -n "$NEW" ] && break
  sleep 2
done
if [ -z "$NEW" ]; then
  say "ERROR: no new pi process after 60s — check the tmux session"
  exit 1
fi
say "new pi pid=$NEW"

# give the TUI time to load the session, then type the resume line
sleep 12
if [ -n "$MSGFILE" ] && [ -f "$MSGFILE" ]; then
  MSG=$(head -1 "$MSGFILE")
  tmux send-keys -t "$SESS" "$MSG" Enter
  say "resume line sent to $NEW: ${MSG:0:80}..."
else
  say "no msg file — new pi starts bare"
fi
# verify what actually landed (the 01:49 lesson: never trust the send's rc)
sleep 8
say "--- capture-pane (last 6 lines):"
tmux capture-pane -t "$SESS" -p | tail -6 | sed 's/^/    | /'
say "done"