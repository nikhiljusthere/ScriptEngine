#!/bin/bash
# switch_restart2.sh <mode> <old_pi_pid>
#
# The MODEL-DRIVEN switch flow (owner 2026-09-10: "when you switch to some
# other context and see the model loaded, you send a call to the llm through
# that shell; that call will tell the model to terminate this shell and
# restart the pi agent"). Unlike switch_restart.sh (kill pi FIRST, then
# switch, then relaunch — for sessions that DON'T fit the target dial), this
# flow keeps the pi agent alive through the whole switch:
#   1) this shell (detached) switches the Qwen model and waits until the
#      model is loaded (the agent survives — its session must FIT the
#      target context, else use switch_restart.sh)
#   2) this shell types an LLM call into the directing pane (tmux
#      send-keys): "terminate this shell + restart the pi agent"
#   3) the MODEL receives that call as a normal turn and executes it with
#      its own tools: pkill this shell, launch relaunch_pi.sh (grace-kill
#      self, tmux relaunch, typed resume line), verify, end turn
#   4) this shell waits (bounded) for the model to terminate it
# The model does the restart with its judgment (TUI-readiness, adaptation),
# not a blind bash grep loop — that is the point of the flow.
# Log: /tmp/switch_restart.log
set -u
MODE=${1:?mode (262k|100k|150k)}
OLD=${2:?old pi pid — verified live (pane pid), never from memory}
SESS=${SESS:-pi-csm}
WAIT=${WAIT:-600}
LOG=${LOG:-/tmp/switch_restart.log}
exec >>"$LOG" 2>&1
say() { echo "[$(date '+%F %T')] $*"; }
say "switch2 start: mode=$MODE old_pid=$OLD"

# 1) switch the model, wait until it is loaded. --force: the flow is a
#    handoff (fresh pi resumes from plan/SWITCHPOINT.md), same as flow 1.
cd /home/goblin/ninfer-work || { say "ERROR: no ninfer-work dir"; exit 1; }
if ! ./qwen-switch.sh "$MODE" --api --force; then
  say "ERROR: switch failed — model left as-is; inspect the qwen logs, then re-run this helper"
  exit 1
fi
CTX=$(sed -n 's/.*ctx=\([0-9]*\).*/\1/p' qwen_mode.txt)
QPID=$(sed -n 's/.*qwen_pid=\([0-9]*\).*/\1/p' qwen_mode.txt)
say "model loaded: mode=$MODE ctx=$CTX qwen_pid=$QPID"

# 2) the LLM call, typed into the directing pane — this is the shell
#    "sending a call to the llm": it lands as a user turn the model must
#    execute (the model has bash tools; this shell does not restart pi).
CALL="LLM CALL from the switch shell (switch_restart2.sh): the model is loaded — mode=$MODE ctx=$CTX qwen_pid=$QPID. Do this NOW in one bash tool call: (1) terminate this switch shell: pkill -f switch_restart2.sh; (2) restart the pi agent: setsid nohup bash tools/master-work/relaunch_pi.sh $OLD /tmp/resume_msg.txt < /dev/null > /dev/null 2>&1 & (it grace-kills you after 5 s, relaunches pi in tmux pi-csm, types the resume line); (3) verify the relaunch helper is alive (kill -0 on its pid) and END YOUR TURN — you die at the grace; the new pi verifies /262k and reports to the owner."
tmux send-keys -t "$SESS" "$CALL" Enter
say "LLM call sent to $SESS (directing pi $OLD): ${CALL:0:80}..."

# 3) bounded wait for the model to terminate this shell
t0=$(date +%s)
while kill -0 $$ 2>/dev/null && [ $(( $(date +%s) - t0 )) -lt "$WAIT" ]; do sleep 5; done
if kill -0 $$ 2>/dev/null; then
  say "WARN: model did not terminate this shell within ${WAIT}s — self-exiting (check whether relaunch_pi ran)"
fi
say "switch2 end: mode=$MODE"