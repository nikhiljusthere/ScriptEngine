#!/bin/bash
# csm-control.sh <b_pi_pid> <b_win>  — Terminal A's monitor (plan/CSM_CONTROL_PLAN.md)
#
# Watches every shell Terminal B's pi process runs (pi -> `bash -c` -> python),
# logs each with its duration (reports/csm/shell_log.jsonl), and enforces the
# Phase-1 GPU rule: model-heavy work that sits on CPU for >15 s gets killed
# with a typed re-run hint (focused XTEST — vte ignores `key --window`).
# LONG (>300 s) runs are flagged, not killed — A the LLM judges those.
# Interventions fire only while a shell is active in B (owner rule: "fire when
# qwen stops in B"). Detached: setsid nohup bash csm-control.sh <pid> <win>
set -u
BPID=${1:?usage: csm-control.sh <b_pi_pid> <b_win>}
BWIN=${2:?}
LOGDIR=/home/goblin/ScriptEngine/reports/csm
mkdir -p "$LOGDIR"
SLOG="$LOGDIR/shell_log.jsonl"
FLOG="$LOGDIR/interventions.jsonl"
MODEL_RX='span-recall.*(--panel|--probe)|--probe [0-9]|canon-run|pytest tests/|scriptengine\.cli (eval|span-recall)|events-extract'
declare -A START CMD LONGF
DOWN_S=""
NOW(){ date +%s; }
J(){ # J <target-file> k1=v1 k2=v2 ...
  local f=$1; shift; local kv="" k v
  for pair in "$@"; do k=${pair%%=*}; v=${pair#*=}; kv+="\"$k\":\"$v\","; done
  printf '{"ts":"%s",%s}\n' "$(date -Iseconds)" "${kv%,}" >> "$f"
}
hint(){ # pid reason hint
  xdotool windowactivate --sync "$BWIN" 2>/dev/null; sleep 0.5
  xdotool type --delay 8 "Control A killed your shell (pid $1: $2). Re-run on GPU: $3" 2>/dev/null
  xdotool key Return
  sleep 1
}
is_model(){ grep -qE "$MODEL_RX" <<< "$1" && return 0; grep -q 'SCRIPTENGINE_DEVICE' <<< "$1" && return 0; return 1; }
cpu_bound(){ # true only when THIS pid (a python interpreter) shows no CUDA context
  local p=$1
  ls -l "/proc/$p/fd" 2>/dev/null | grep -q 'nvidia' && return 1
  grep -q 'SCRIPTENGINE_DEVICE=cpu' "/proc/$p/environ" 2>/dev/null && return 0
  grep -q 'scriptengine' <<< "$(tr '\0' ' ' < "/proc/$p/cmdline" 2>/dev/null)" && return 0
  return 1
}
while :; do
  if [ ! -d "/proc/$BPID" ]; then
    J "$FLOG" event=B_PID_GONE b_pid="$BPID"; sleep 30; continue
  fi
  kids=""
  for c in $(pgrep -P "$BPID" 2>/dev/null); do kids+=" $c $(pgrep -P "$c" 2>/dev/null)"; done
  # starts
  for p in $kids; do
    [ -d "/proc/$p" ] || continue
    cmd=$(tr '\0' ' ' < "/proc/$p/cmdline" 2>/dev/null | head -c 220)
    case "$cmd" in *bash*|*python*|*scriptengine*|*pytest*) ;; *) continue ;; esac
    [ -n "${START[$p]:-}" ] && continue
    START[$p]=$(NOW); CMD[$p]="$cmd"; LONGF[$p]=0
    J "$SLOG" event=START pid="$p" cmd="${cmd//\"/\\\"}"
    # rule 1: explicit CPU device on a model command — kill at sight, never wait
    if grep -q 'SCRIPTENGINE_DEVICE=cpu' <<< "$cmd" && is_model "$cmd"; then
      kill "$p" 2>/dev/null
      J "$FLOG" event=KILLED pid="$p" reason="explicit CPU device on a model command"
      hint "$p" "CPU device" "drop the SCRIPTENGINE_DEVICE=cpu override (CUDA is free under 100k); one-copy rule: stop :8000 first for in-process jobs"
      unset "START[$p]" "CMD[$p]" "LONGF[$p]"
    fi
  done
  # aging / exits
  for p in "${!START[@]}"; do
    [ -d "/proc/$p" ] || { d=$(( $(NOW) - ${START[$p]} )); J "$SLOG" event=END pid="$p" dur_s="$d"; unset "START[$p]" "CMD[$p]" "LONGF[$p]"; continue; }
    age=$(( $(NOW) - ${START[$p]} )); cmd=${CMD[$p]}
    # rule 2: model-heavy python, CPU-bound, >15 s — kill + hint (the 1200-s incident, structurally)
    if [ "$age" -gt 15 ] && [[ "$cmd" == *python* ]] && is_model "$cmd" && cpu_bound "$p"; then
      s8000=$(pgrep -f 'scriptengine.api.main' | head -1); srvcpu=""
      if [ -n "$s8000" ] && grep -q 'SCRIPTENGINE_DEVICE=cpu' "/proc/$s8000/environ" 2>/dev/null; then
        srvcpu=" — :8000 is also on CPU: restart it on CUDA, then re-run"
      fi
      kill "$p" 2>/dev/null
      J "$FLOG" event=KILLED pid="$p" age_s="$age" reason="model work CPU-bound >15s" cmd="${cmd:0:150}"
      hint "$p" "CPU-bound ${age}s" "same command via the GPU path (no CPU override)$srvcpu"
      unset "START[$p]" "CMD[$p]" "LONGF[$p]"
    fi
    # rule 3: any shell >300 s — flag for A's judgment (no auto-kill)
    if [ "$age" -gt 300 ] && [ $(( age / 300 )) -gt "${LONGF[$p]}" ]; then
      J "$FLOG" event=LONG pid="$p" dur_s="$age" cmd="${cmd:0:150}"; LONGF[$p]=$(( age / 300 ))
    fi
  done
  # rule 4: model health backstop (the old poller's job, now A's)
  if ! curl -sf -m 2 http://127.0.0.1:18080/health >/dev/null 2>&1; then
    [ -z "$DOWN_S" ] && DOWN_S=$(NOW)
  else
    if [ -n "$DOWN_S" ]; then J "$FLOG" event=MODEL_RECOVERED down_s=$(( $(NOW) - DOWN_S )); DOWN_S=""; fi
  fi
  if [ -n "$DOWN_S" ] && [ $(( $(NOW) - DOWN_S )) -gt 60 ]; then
    J "$FLOG" event=MODEL_DOWN down_s=$(( $(NOW) - DOWN_S )); DOWN_S=""
  fi
  sleep 5
done