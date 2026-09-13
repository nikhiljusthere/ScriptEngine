#!/usr/bin/env bash
# oc-watch.sh — keep an opencode TUI running autonomously.
#
# opencode only writes log lines while it is working, so a blocked prompt is
# visible in the log: the last line is an unresolved `message=asking` entry.
# This watcher polls the log and, per pending id:
#   per_* (permission dialog) -> auto-answers "always allow" by typing into the
#        opencode window (Right -> Enter -> Enter, default selection is "once")
#        unless OC_WATCH_NO_AUTO=1 (then it wakes pi instead).
#   que_* (MCQ question)      -> wakes pi (types a one-line prompt into the pi
#        window) so the pi agent reads the question from opencode.db and answers.
# Owner rule 2026-09-13: NO continue-messages otherwise. A finished task or a
# crashed session is NOT a stall - the watcher never types into opencode except
# for dialog keys. It only heartbeats; if a run dies, the user sees it in the
# terminal and starts the next task themselves.
#
# Start:  setsid nohup bash tools/master-work/oc-watch.sh >/tmp/oc_watch.out 2>&1 </dev/null &
# Stop:   kill $(cat /tmp/oc_watch.pid)
# Log:    /tmp/oc_watch.log (status lines only)
set -u
LOG="$HOME/.local/share/opencode/log/opencode.log"
PIDF=/tmp/oc_watch.pid
STATE=/tmp/oc_watch_state
HB=/tmp/oc_watch.log
INTERVAL="${OC_WATCH_INTERVAL:-10}"

echo $$ > "$PIDF"
oc_window() { # opencode window: title is set by opencode as "OC | <task>"
  local w
  w=$(xdotool search --name '^OC ' 2>/dev/null | head -1)
  if [ -n "$w" ]; then echo "$w"; return; fi
  # fallback: the gnome-terminal window that is neither pi's nor a bare "Terminal"
  for w in $(xdotool search --class Gnome-terminal 2>/dev/null); do
    local n; n=$(xdotool getwindowname "$w" 2>/dev/null)
    case "$n" in *'π - ScriptEngine'|Terminal) : ;; *) echo "$w"; return ;; esac
  done
}
pi_window() { xdotool search --name 'π - ScriptEngine' 2>/dev/null | head -1; }
wake_pi() { # $1 = one-line reason
  local w
  w=$(pi_window)
  if [ -z "$w" ]; then echo "$(date +%T) WARN: no pi window, cannot wake" >> "$HB"; return; fi
  xdotool windowactivate --sync "$w" 2>/dev/null; sleep 0.4
  xdotool type --clearmodifiers --delay 20 -- "oc-watch: $1. Handle per .pi/skills/opencode-watch."
  sleep 0.3
  xdotool key Return
}
answer_always() { # type "always allow" into the opencode window (default sel = "once")
  local w; w=$(oc_window)
  [ -n "$w" ] || return 1
  xdotool windowactivate --sync "$w" 2>/dev/null; sleep 0.4
  xdotool key Right; sleep 0.4
  xdotool key Return; sleep 0.4
  xdotool key Return
}
hb=0
while :; do
  OC=$(pgrep -x opencode | head -1)
  if [ -z "$OC" ]; then
    [ $((hb++ % 30)) -eq 0 ] && echo "$(date +%T) opencode not running - idle polling" >> "$HB"
    sleep "$INTERVAL"; continue
  fi
  # --- blocked prompt? last line of the log is an unresolved asking entry ---
  if tail -1 "$LOG" 2>/dev/null | grep -qa 'message=asking'; then
    AID=$(tail -1 "$LOG" | grep -oa 'id=[a-z_]*[a-z0-9_]*' | head -1 | cut -d= -f2)
    if [ -n "$AID" ] && ! grep -qsaF "$AID" "$STATE"; then
      echo "$AID" >> "$STATE"; tail -50 "$STATE" > "${STATE}.t" && mv "${STATE}.t" "$STATE"
      case "$AID" in
        per_*)
          if [ "${OC_WATCH_NO_AUTO:-0}" = 1 ]; then
            wake_pi "opencode blocked on permission $AID - answer always-allow"
          elif answer_always; then
            echo "$(date +%T) $AID auto-answered (always allow)" >> "$HB"
          else
            wake_pi "opencode blocked on permission $AID, no OC window found"
          fi
          ;;
        que_*)
          wake_pi "opencode blocked on question $AID (MCQ) - read it from opencode.db and answer"
          echo "$(date +%T) $AID MCQ - pi woken" >> "$HB"
          ;;
      esac
    fi
  fi
  [ $((hb++ % 6)) -eq 0 ] && echo "$(date +%T) ok oc=$OC last=$(tail -1 "$LOG" 2>/dev/null | cut -c1-100)" >> "$HB"
  sleep "$INTERVAL"
done