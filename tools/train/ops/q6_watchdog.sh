#!/bin/bash
# Restart the Q6 server if it dies (2026-09-29: CUDA "launch timed out" killed it
# mid-run; the display-attached 5090 has a kernel watchdog). Checks every 30 s.
while true; do
  if ! curl -sf -m 10 http://127.0.0.1:8090/health >/dev/null; then
    sleep 20
    if ! curl -sf -m 10 http://127.0.0.1:8090/health >/dev/null && ! ss -ltn | grep -q ':8090 '; then
      echo "$(date +%T) server down, restarting" >> /tmp/jjk100/q6_watchdog.log
      # 2026-09-30: SERVE_SCRIPT lets the restart use the MEASURED-BEST config (written by
      # sweep_q8.sh) instead of hardcoding NGL=60. The older /tmp copy of this watchdog had
      # no NGL pin and OOM-looped on the NGL=999 default (q6_server_W2244/W2254.log).
      setsid nohup "${SERVE_SCRIPT:-/home/goblin/ScriptEngine/tools/train/ops/serve_q8.sh}" > /tmp/jjk100/q6_server_W$(date +%H%M).log 2>&1 < /dev/null &
      for i in $(seq 1 60); do curl -sf http://127.0.0.1:8090/health >/dev/null && break; sleep 10; done
      echo "$(date +%T) server up" >> /tmp/jjk100/q6_watchdog.log
    fi
  fi
  sleep 30
done
