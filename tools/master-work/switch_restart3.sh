#!/bin/bash
# switch_restart3.sh <mode> <session_file> <old_pi_pid> <old_shell_pid>
#
# The 3-part model-driven switch (owner 2026-09-10: "first the unload
# command which fires up instantly, then the load command (5 sec wait),
# then an internal llm-call to qwen to trigger a script"):
#   part 1  ninfer-stop.sh               — unload (fires instantly; marks
#                                          qwen_mode.txt mode=off so no
#                                          poller resurrects the old profile)
#   part 2  qwen-switch.sh <mode> --api  — load: from mode=off this is the
#                                          load half only — syncs pi
#                                          models.json ctx, starts the serve
#                                          profile, health-polls :18080 (the
#                                          wait), places :8000, writes
#                                          qwen_mode.txt + SWITCHPOINT
#   part 3  internal LLM call to qwen — an HTTP chat completion into :18080
#           itself (NOT typed into any pi pane; that was the D20 flaw). The
#           call answers only once the model is live; its return is the
#           trigger: relaunch_term.sh opens a new window of the owner's
#           terminal running `pi --session <same session>`, then kills the
#           old pi + old terminal.
#
# The skip-LLM-call variant (owner: "you can do this yourself as well to
# skip the llm call") is the /v1/models poll fallback below — same trigger
# point, no model call.
#
# Launch detached so the calling session can die mid-flow:
#   setsid nohup bash tools/master-work/switch_restart3.sh 262k \
#     <session file> <old pi pid> <old shell pid> < /dev/null > /dev/null 2>&1 &
# Log: /tmp/switch_restart3.log
set -u
MODE=${1:?mode (262k|100k|...)}
SESSION=${2:?session file the new pi resumes}
OLD_PI=${3:?old pi pid}
OLD_SHELL=${4:?old terminal shell pid}
LOG=${LOG:-/tmp/switch_restart3.log}
exec >>"$LOG" 2>&1
say() { echo "[$(date '+%F %T')] $*"; }
say "switch3 start: mode=$MODE session=$(basename "$SESSION") old_pi=$OLD_PI old_shell=$OLD_SHELL"
cd /home/goblin/ninfer-work || { say "ERROR: no ninfer-work dir"; exit 1; }

# part 1: unload — fires instantly
if ! ./ninfer-stop.sh; then say "ERROR: unload failed"; exit 1; fi
say "part1: unloaded"

# part 2: load. The fit guard (transcript bytes/4 vs target ctx) is
# deliberately conservative (~2.7x overstatement) — FORCE=1 passes --force
# for the deliberate D20-style case (real token count fits; the session
# auto-compacts if it doesn't).
if ! ./qwen-switch.sh "$MODE" --api ${FORCE:+--force}; then say "ERROR: load failed — model left as-is; inspect the qwen logs, then re-run this helper"; exit 1; fi
say "part2: loaded (mode=$MODE)"

# part 3: the trigger. Default: internal LLM call to qwen itself — its return
# is the trigger. SKIP_LLM=1 = the skip-LLM variant (owner 2026-09-10):
# go straight to the /v1/models readiness poll, no model call.
if [ "${SKIP_LLM:-0}" = "1" ]; then
  say "part3: SKIP_LLM=1 — no LLM call, polling /v1/models for readiness"
  for i in $(seq 1 240); do
    curl -s -m 2 http://127.0.0.1:18080/v1/models >/dev/null 2>&1 && { say "  :18080 answering (poll)"; break; }
    sleep 0.5
  done
elif curl -s -m 90 http://127.0.0.1:18080/v1/chat/completions \
     -H 'Content-Type: application/json' \
     -d '{"model":"qwen3.8-27b-ninfer","messages":[{"role":"user","content":"switch3 ready check"}],"max_tokens":4}' \
     | grep -q '"choices"'; then
  say "part3: internal LLM call answered — model live, triggering relaunch"
else
  say "WARN: LLM call did not answer — bounded /v1/models poll fallback (skip-LLM variant)"
  for i in $(seq 1 240); do
    curl -s -m 2 http://127.0.0.1:18080/v1/models >/dev/null 2>&1 && { say "  :18080 answering (poll)"; break; }
    sleep 0.5
  done
fi
setsid nohup bash /home/goblin/ScriptEngine/tools/master-work/relaunch_term.sh \
  "$SESSION" "$OLD_PI" "$OLD_SHELL" < /dev/null > /dev/null 2>&1 &
say "relaunch_term triggered (pid $!)"
say "switch3 end: mode=$MODE"