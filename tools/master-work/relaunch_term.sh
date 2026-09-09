#!/bin/bash
# relaunch_term.sh <session_file> <old_pi_pid> <old_shell_pid>
#
# The "come back" half of the 3-part switch (owner 2026-09-10): open a NEW
# window of the owner's own terminal app (gnome-terminal — the app the
# owner starts from the GNOME search; NOT tmux) running
# `cd <repo> && pi --session <file>` = the SAME session in the new window.
# Then kill the old pi and close the old terminal window (killing its
# shell closes the window). Launched detached by switch_restart3.sh, so it
# survives the old pi's death. Log: /tmp/switch_restart3.log
set -u
SESSION=${1:?session file the new pi resumes (full path)}
OLD_PI=${2:?old pi pid}
OLD_SHELL=${3:?old terminal shell pid}
DIR=${DIR:-/home/goblin/ScriptEngine}
LOG=${LOG:-/tmp/switch_restart3.log}
exec >>"$LOG" 2>&1
say() { echo "[$(date '+%F %T')] $*"; }
say "relaunch_term start: session=$(basename "$SESSION") old_pi=$OLD_PI old_shell=$OLD_SHELL"

# pi's that already exist — the NEW one is any pid that appears AFTER the
# window is opened (a pre-existing pi must never be mislabeled as the new
# one — 2026-09-10 00:58 lesson, same guard as relaunch_pi.sh)
PRE=" $(pgrep -x pi | tr '\n' ' ')"

# 1) open the new terminal window (setsid: survives this shell's death;
#    DISPLAY=:0 like the tmux attach line in the old flow)
DISPLAY=:0 setsid gnome-terminal -- bash -lc "cd $DIR && exec pi --session $SESSION" &
say "new terminal window launched (gnome-terminal)"

# 2) wait for the new pi process (one that was not in PRE)
NEW=""
for _ in $(seq 1 90); do
  for p in $(pgrep -x pi); do
    case "$PRE" in *" $p "*) ;; *) NEW=$p; break 2;; esac
  done
  sleep 1
done
[ -z "$NEW" ] && { say "ERROR: no new pi after 90 s — old pi left ALIVE; inspect the new window"; exit 1; }
say "new pi pid=$NEW"

# 3) let it read the session file BEFORE the old pi dies (same-session
#    continuity: the transcript must be complete when the new pi loads it)
sleep 5

# 4) kill the old pi (graceful, then hard)
if kill -0 "$OLD_PI" 2>/dev/null; then kill "$OLD_PI"; say "TERM -> old pi $OLD_PI"; fi
for _ in $(seq 1 20); do kill -0 "$OLD_PI" 2>/dev/null || break; sleep 1; done
if kill -0 "$OLD_PI" 2>/dev/null; then kill -9 "$OLD_PI"; say "KILL -9 $OLD_PI"; fi
say "old pi gone"

# 5) close the old terminal window. Two shapes:
#    a) OLD_SHELL = "none": the window was launched as
#       gnome-terminal -- bash -lc '... exec pi' — there is no separate
#       shell; the old pi IS the window's process, so the window closes
#       when the old pi died in step 4 (gnome-terminal closes the window
#       when its command exits).
#    b) separate shell (a user-launched window): kill the shell. TERM
#       first, then VERIFY death: this machine's interactive bash survives
#       SIGTERM (2026-09-10: it lost a TERM that landed while it was
#       reaping the old pi, and a second TERM at the bare prompt). Escape
#       to KILL -9 — safe at the prompt.
if [ "$OLD_SHELL" = "none" ]; then
  say "old window has no separate shell (exec chain) — it closes when the old pi died"
else
  kill "$OLD_SHELL" 2>/dev/null && say "TERM -> old shell $OLD_SHELL"
  for _ in $(seq 1 10); do kill -0 "$OLD_SHELL" 2>/dev/null || break; sleep 1; done
  if kill -0 "$OLD_SHELL" 2>/dev/null; then
    kill -9 "$OLD_SHELL" 2>/dev/null
    sleep 1
    say "KILL -9 -> old shell $OLD_SHELL (survived TERM)"
  fi
  if kill -0 "$OLD_SHELL" 2>/dev/null; then say "ERROR: old shell $OLD_SHELL still alive — window not closed"; exit 1; fi
  say "old shell gone (window closed)"
fi
say "relaunch_term done: new pi $NEW (session $(basename "$SESSION"))"