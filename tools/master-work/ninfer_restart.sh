#!/usr/bin/env bash
# ninfer_restart.sh — scripted model-down recovery (plan/PLAN_master_work.md §6.5).
# Launched by the poller on MODEL-DOWN. Re-runs the serve profile matching the
# current qwen_mode.txt under setsid. Guards: never fight an owner-initiated
# qwen-switch, don't flap against a fresh recovery, don't double-launch.
set -u
NW=/home/goblin/ninfer-work; MW=/home/goblin/ScriptEngine/reports/master-work
cd "$NW" || exit 1

MODE=$(sed -n 's/^mode=\([^ ]*\).*/\1/p' qwen_mode.txt | head -1)
case "$MODE" in
  262k)  SERVE=./serve.sh ;;
  100k)  SERVE=./serve_100k.sh ;;
  [0-9]*) SERVE="./serve_ctx_${MODE}.sh" ;;   # custom ctx profiles (e.g. 135168)
  *) echo "ninfer_restart: unknown/missing mode in qwen_mode.txt ('${MODE:-<none>}') — not restarting" >&2; exit 1;;
esac
[ -f "$SERVE" ] || { echo "ninfer_restart: $SERVE missing — not restarting" >&2; exit 1; }

# guard 1: an owner-initiated switch is in flight — never fight it
pgrep -f 'qwen-switch\.sh' >/dev/null && { echo "ninfer_restart: qwen-switch.sh in flight — skipping"; exit 0; }

# guard 2: the model is healthy again (transient blip) — nothing to do
[ "$(curl -s -m 2 -o /dev/null -w '%{http_code}' http://127.0.0.1:18080/health)" = 200 ] && { echo "ninfer_restart: :18080 healthy now — nothing to do"; exit 0; }

# guard 3: 5-min cooldown after the last MODEL-UP (no flapping against a fresh recovery)
last_up=$(grep 'EVENT MODEL-UP' "$MW/a_wake_log.md" 2>/dev/null | tail -1 | grep -oP '^\[\K[^\]]+')
if [ -n "${last_up:-}" ]; then
  up_ts=$(date -d "$last_up" +%s 2>/dev/null || echo 0)
  [ $(( $(date +%s) - up_ts )) -lt 300 ] && { echo "ninfer_restart: MODEL-UP < 5 min ago — cooling down"; exit 0; }
fi

# guard 4: 5-min cooldown between our own attempts (a load takes 30–60+ s; the poller ticks every 60 s)
MARK=$NW/logs/ninfer_restart_last
[ -f "$MARK" ] && [ $(( $(date +%s) - $(stat -c %Y "$MARK") )) -lt 300 ] && { echo "ninfer_restart: attempted < 5 min ago — cooling down"; exit 0; }
touch "$MARK"

echo "ninfer_restart: launching $SERVE (mode=$MODE) under setsid → logs/ninfer_restart.log"
setsid nohup bash "$SERVE" > "$NW/logs/ninfer_restart.log" 2>&1 </dev/null &

# wait for health, then refresh qwen_pid/ts in qwen_mode.txt (the mode is unchanged)
for i in $(seq 1 60); do
  [ "$(curl -s -m 2 -o /dev/null -w '%{http_code}' http://127.0.0.1:18080/health)" = 200 ] && break
  sleep 5
done
newpid=$(pgrep -f 'qwen3_8_27b_nvfp4.ninfer' | head -1 || true)
if [ -n "${newpid:-}" ] && [ "$(curl -s -m 2 -o /dev/null -w '%{http_code}' http://127.0.0.1:18080/health)" = 200 ]; then
  sed -i "s/^qwen_pid=.*/qwen_pid=$newpid/; s/^ts=.*/ts=$(date -Is)/" qwen_mode.txt
  echo "ninfer_restart: healthy (pid=$newpid); qwen_mode.txt refreshed"
else
  echo "ninfer_restart: no healthy model after 5 min — check $NW/logs/ninfer_restart.log" >&2
  exit 1
fi