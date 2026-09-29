#!/bin/bash
# sweep_q8.sh — find the fastest VRAM-feasible llama-server config for Qwen3.8-27B Q8_0
# on this 32 GB card (owner ask 2026-09-30). Runs the real server, measures it, picks a winner,
# and always restores a working server on :8090. Self-contained: safe to fire detached.
#
# ---- measured facts this sweep is built on (2026-09-30) -------------------------------
#  model: 65 blocks = 17 full-attn (3,7..63,64) + 48 GDN, every weight Q8_0, 27.04 GiB total
#    token_embd 1.258 GiB, output(lm_head) 1.258 GiB, 388 MiB avg per GDN layer
#    KV q8_0 = 36.1 KiB/token -> 2.258 GiB at ctx 65536
#    the GDN recurrent-state ("rs") cache is ~74.8 MiB PER GDN LAYER ON GPU (3591 MiB / 48
#    layers, from the Q6 OOM log: "failed to allocate buffer for rs cache") = 3.5 GiB, and
#    it is pinned to the model device. No llama-server flag moves it to host RAM.
#  => full offload (NGL=65) at 65k ctx needs ~33.6 GiB vs 31.84 available: OOM (observed).
#     Prod is NGL=60 (5 CPU layers, DRAM-bandwidth bound) = 22 t/s clean / 16.9 t/s real.
#     Q6_K_XL is 21.5 GiB so it fits fully offloaded and does 85 t/s — the prize is closing
#     the same gap for Q8 by freeing ~1.6 GiB. Three candidate levers, tried in order:
#       S1 NP=2                 if the rs cache is per-slot this frees up to 2/3 of 3.5 GiB
#       S2/S4 -ot token_embd=CPU frees 1.26 GiB, essentially free (one row lookup/token)
#       S3 V cache q4_0         halves the V half of the KV (only if the above fail)
#     plus a safe NGL rung-up and MTP depth (--spec-draft-n-max).
# --------------------------------------------------------------------------------------
set -u
LOG=/tmp/jjk100/sweep_q8.log
RES=/tmp/jjk100/sweep_q8_results.tsv
BIN=$HOME/llama.cpp/build/bin/llama-server
MODEL=/mnt/PROJECTS/models/qwen3.8-27b-q8/Qwen3.8-27B-Q8_0.gguf
TOTALV=32607
PRESLEEP=${PRESLEEP:-75}          # let the in-flight turn finish streaming before we pull the rug
TAG=sweep8099
PROD_WD=/home/goblin/ScriptEngine/tools/train/ops/q6_watchdog.sh

say(){ echo "[$(date +%T)] $*" | tee -a "$LOG"; }

COMMON=(--alias $TAG --host 127.0.0.1 --port 8099 --flash-attn on --jinja --kv-unified
        --spec-draft-type-k q8_0 --spec-draft-type-v q8_0 --cache-ram 16384
        --cache-prompt --cache-reuse 256 --spec-type draft-mtp --spec-draft-ngl all
        --fit off --no-context-shift --no-mmproj --reasoning on
        --threads 16 --threads-batch 16 -b 2048 -ub 512
        --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0.0
        --repeat-penalty 1.0 --presence-penalty 0.0 --metrics --perf)

KQ8="-ngl 999 -c 65536 --cache-type-k q8_0 --cache-type-v q8_0"
N60="-ngl 60 -c 65536 --cache-type-k q8_0 --cache-type-v q8_0"
N62="-ngl 62 -c 65536 --cache-type-k q8_0 --cache-type-v q8_0"
EMB="-ot token_embd.weight=CPU"
MTP3="--spec-draft-n-max 3 --spec-draft-p-min 0.5"
MTP5="--spec-draft-n-max 5 --spec-draft-p-min 0.5"

BEST_NAME=""; BEST_TG=0; BEST_ARGS=""; BOOTED=0
: > "$RES"
printf 'config\ttg_tps\tpp_tps\tspec_accept\tdrafts\n' > "$RES"

kill_sweep(){ pkill -f "$TAG" 2>/dev/null; sleep 1; pkill -9 -f "$TAG" 2>/dev/null; sleep 2; }

# run <name> <base args> <mtp args> -> BOOTED=1/0, RESULT row appended when it came up
run(){
  local name="$1" base="$2" mtp="$3"
  local log=/tmp/jjk100/sweep_${name}.log
  say "--- $name : $base $mtp"
  kill_sweep
  # shellcheck disable=SC2086
  setsid nohup "$BIN" -m "$MODEL" "${COMMON[@]}" $base $mtp > "$log" 2>&1 < /dev/null &
  BOOTED=0
  for _ in $(seq 1 54); do                     # ~4.5 min cap per config
    if curl -sf -m 3 http://127.0.0.1:8099/health >/dev/null 2>&1; then BOOTED=1; break; fi
    pgrep -f "$TAG" >/dev/null || break
    sleep 5
  done
  if [ "$BOOTED" = 1 ]; then
    sleep 4
    local vram out
    vram=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)
    out=$(python3 /tmp/jjk100/bench.py 8099 "$name" 128 4096 2>&1 | tail -1)
    say "$name UP  vram=${vram}/${TOTALV} MiB  |  $out"
    case "$out" in RESULT*) echo "$out" >> "$RES";; *) say "  bench failed: $out";; esac
  else
    say "$name DOWN"
    grep -hiE 'out of memory|failed to allocate|rs cache|error loading|compute buffer' "$log" \
      | tail -3 | sed 's/^/      /' | tee -a "$LOG"
  fi
  kill_sweep
  return 0
}

# consider <name> <base args> <mtp args>  — keep the fastest config measured so far
consider(){
  local name="$1" base="$2" mtp="$3" tg
  tg=$(awk -v n="$name" '$1==n{print $2}' "$RES" | tail -1)
  if [ -n "${tg:-}" ] && awk "BEGIN{exit !($tg > $BEST_TG)}"; then
    BEST_TG=$tg; BEST_NAME=$name; BEST_ARGS="$base $mtp"
    say "    -> new best: $name ($tg t/s)"
  fi
  return 0
}

run_sweep(){
  # --- control: the production config, measured in the same harness
  run prod_n60 "$N60 -np 6" "$MTP3"
  [ "$BOOTED" = 1 ] && consider prod_n60 "$N60 -np 6" "$MTP3"

  # --- S1: FULL offload, 2 slots. Tests whether the rs cache is per-slot. Cleanest prize.
  run full_np2 "$KQ8 -np 2" "$MTP3"
  if [ "$BOOTED" = 1 ]; then
    consider full_np2 "$KQ8 -np 2" "$MTP3"
    # --- S2: 4 slots if 2 worked — safer for parallel subagents, may still fit
    run full_np4 "$KQ8 -np 4" "$MTP3"
    [ "$BOOTED" = 1 ] && consider full_np4 "$KQ8 -np 4" "$MTP3"
  else
    # --- S3: safe rung-up, no compromise at all
    run n62 "$N62 -np 6" "$MTP3"
    [ "$BOOTED" = 1 ] && consider n62 "$N62 -np 6" "$MTP3"
    # --- S4: full offload with the embedding table on the CPU (frees 1.26 GiB)
    run full_embcpu "$KQ8 -np 6 $EMB" "$MTP3"
    if [ "$BOOTED" = 1 ]; then
      consider full_embcpu "$KQ8 -np 6 $EMB" "$MTP3"
    else
      # --- S5: last resort — full offload + Q4_0 V cache
      run full_embcpu_vq4 "-ngl 999 -c 65536 -np 6 $EMB --cache-type-k q8_0 --cache-type-v q4_0" "$MTP3"
      [ "$BOOTED" = 1 ] && consider full_embcpu_vq4 "-ngl 999 -c 65536 -np 6 $EMB --cache-type-k q8_0 --cache-type-v q4_0" "$MTP3"
    fi
  fi

  # --- S6: winner + deeper MTP drafting (speculative decode is exact: zero quality cost)
  if [ -n "$BEST_NAME" ]; then
    local b=${BEST_ARGS% $MTP3}
    run "${BEST_NAME}_mtp5" "$b" "$MTP5"
    [ "$BOOTED" = 1 ] && consider "${BEST_NAME}_mtp5" "$b" "$MTP5"
  fi
  return 0
}

FINALIZED=0
finalize(){
  [ "$FINALIZED" = 1 ] && return 0
  FINALIZED=1
  kill_sweep
  pkill -f "port 8090" 2>/dev/null; sleep 2; pkill -9 -f "port 8090" 2>/dev/null; sleep 3
  # COMMON carries --port 8099/--alias sweep8099; rewrite them instead of passing a second
  # --port/--alias on the command line, so a first-wins arg parser can never leave :8090 dead.
  local C2=("${COMMON[@]}") i
  for i in "${!C2[@]}"; do
    case "${C2[$i]}" in
      --alias) C2[$((i+1))]=qwen3.8-27b-q8 ;;
      --port)  C2[$((i+1))]=8090 ;;
    esac
  done
  local args
  if [ -n "$BEST_ARGS" ]; then
    args="$BEST_ARGS"
  else
    say "!! no config passed; restoring known-good NGL=60"
    args="$N60 -np 6 $MTP3"
  fi
  say "RESTORE best=$BEST_NAME tg=$BEST_TG : $args"
  # shellcheck disable=SC2086
  setsid nohup "$BIN" -m "$MODEL" "${C2[@]}" $args > /tmp/jjk100/q8_server.log 2>&1 < /dev/null &
  local up=0
  for _ in $(seq 1 60); do
    curl -sf -m 3 http://127.0.0.1:8090/health >/dev/null 2>&1 && { up=1; break; }
    sleep 5
  done
  if [ "$up" = 1 ]; then
    say "RESTORED :8090 ($BEST_NAME, tg=$BEST_TG t/s) vram=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)/${TOTALV} MiB"
    # the watchdog must restart with the WINNING args, not a hardcoded NGL=60
    printf '#!/bin/bash\n# generated by sweep_q8.sh 2026-09-30 — the measured-best Q8 config\nexec %s -m %s %s %s\n' \
      "$BIN" "$MODEL" "${C2[*]}" "$args" > /tmp/jjk100/serve_q8_best.sh
    chmod +x /tmp/jjk100/serve_q8_best.sh
    SERVE_SCRIPT=/tmp/jjk100/serve_q8_best.sh setsid nohup bash "$PROD_WD" >> /tmp/jjk100/q6_watchdog.log 2>&1 < /dev/null &
    sleep 2
    pgrep -f "ops/q6_watchdog.sh" >/dev/null && say "watchdog relaunched (SERVE_SCRIPT=serve_q8_best.sh)" || say "WARN watchdog not running"
  else
    say "!! RESTORE FAILED — falling back to the known-good NGL=60 config"
    pkill -f "port 8090" 2>/dev/null; sleep 3
    # shellcheck disable=SC2086
    setsid nohup "$BIN" -m "$MODEL" "${C2[@]}" $N60 -np 6 $MTP3 > /tmp/jjk100/q8_server.log 2>&1 < /dev/null &
    for _ in $(seq 1 60); do curl -sf -m 3 http://127.0.0.1:8090/health >/dev/null 2>&1 && { say "FALLBACK OK"; break; }; sleep 5; done
  fi
  say "=== SWEEP DONE ==="
  cat "$RES" | tee -a "$LOG"
}
trap finalize EXIT

say "sweep armed (presleep ${PRESLEEP}s, then the prod server goes down)"
pkill -f "ops/q6_watchdog.sh" 2>/dev/null && say "watchdog stopped (it would otherwise race us for VRAM)" || say "watchdog was not running"
say "presleep ${PRESLEEP}s — my final message finishes streaming on :8090 before the rug is pulled"
sleep "$PRESLEEP"
kill_sweep
pkill -f "port 8090" 2>/dev/null; sleep 2; pkill -9 -f "port 8090" 2>/dev/null
say "prod :8090 down (its KV cache died with it — my next turn re-processes the prompt). VRAM now: $(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits) MiB"
run_sweep
finalize
