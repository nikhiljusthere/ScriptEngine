#!/bin/bash
# Restart the Qwen3.6-35B-A3B NInfer server if it dies (2026-09-30).
# Replaces the q6_watchdog.sh that guarded the llama.cpp Q8 server on :8090.
#
# The 5090 is display-attached and has a kernel watchdog that has killed CUDA
# processes mid-run before ("launch timed out"), so a supervisor is worth
# having. Checks every 30 s.
#
# Mode file, so ninfer-work/qwen-switch.sh and friends can see the state:
#   ~/ninfer-work/qwen_mode.txt
#
# NOTE ON STOPPING: to switch models away from the 35B, kill THIS watchdog
# first (it will otherwise restart the server and collide with the new load),
# then kill the server by exact PID. Do not use a broad pkill pattern: that
# killed the controlling shell once already.
while true; do
  if ! curl -sf -m 10 http://127.0.0.1:18081/health >/dev/null; then
    sleep 20
    if ! curl -sf -m 10 http://127.0.0.1:18081/health >/dev/null && ! ss -ltn | grep -q ':18081 '; then
      echo "$(date +%T) 35b server down, restarting" >> /tmp/jjk100/ninfer35_watchdog.log
      setsid nohup /home/goblin/ScriptEngine/tools/train/ops/serve_35b.sh \
        > /tmp/jjk100/ninfer_35b_$(date +%H%M).log 2>&1 < /dev/null &
      # 20.6 GiB of weights loaded at ~877 MiB/s => ~25 s, plus engine init.
      for i in $(seq 1 60); do curl -sf -m 5 http://127.0.0.1:18081/health >/dev/null && break; sleep 10; done
      PID=$(pgrep -f 'build35/apps/ninfer-serve' | head -1)
      printf 'mode=ninfer-35b ctx=262144 qwen_pid=%s ts=%s free_mib=%s api=off\n' \
        "${PID:--}" "$(date -Iseconds)" \
        "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" \
        > /home/goblin/ninfer-work/qwen_mode.txt
      echo "$(date +%T) 35b server up (pid $PID)" >> /tmp/jjk100/ninfer35_watchdog.log
    fi
  fi
  sleep 30
done
