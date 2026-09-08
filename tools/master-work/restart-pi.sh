#!/bin/bash
# restart-pi.sh <session-id> [window-id]
# Kill the given pi pid (verified present) and relaunch pi with the same session.
# The 2026-09-08 bug this replaces: xdotool "type" into a window whose shell
# just died looks like success but lands nowhere — so the typed command must be
# PROVEN via a file side-channel before the window path is accepted.
set -u
SID=${1:?usage: restart-pi.sh <session-id> [window-id]}
WIN=${2:-50331658}
LOG=/tmp/restart_pi_$SID.log
log(){ echo "[$(date +%H:%M:%S)] $*" | tee -a $LOG; }
MYPID=$(pgrep -f "pi.*$SID" | head -1)
[ -z "$MYPID" ] && { log "no pi pid for session $SID (abort)"; exit 1; }
log "killing A pi pid=$MYPID"
kill "$MYPID" 2>/dev/null
sleep 4
rm -f /tmp/a_restart_verify
V=""
if xdotool windowactivate --sync "$WIN" 2>/dev/null; then
  xdotool type --delay 15 --window "$WIN" "touch /tmp/a_restart_verify && pi --session $SID" 2>/dev/null && xdotool key --window "$WIN" Return
  for i in $(seq 1 12); do sleep 2; [ -f /tmp/a_restart_verify ] && { V=ok; break; }; done
fi
if [ -n "$V" ]; then
  log "A restarted in window $WIN (verified via side-channel)"
else
  rm -f /tmp/a_restart_verify
  tmux kill-session -t a-supervisor 2>/dev/null
  tmux new-session -d -s a-supervisor -c /home/goblin/ScriptEngine "pi --session $SID"
  sleep 8
  log "window path unverified — A restarted in tmux a-supervisor (owner: tmux a -t a-supervisor)"
fi
log "=== restart complete"
