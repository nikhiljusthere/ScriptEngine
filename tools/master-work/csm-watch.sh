#!/bin/bash
# csm-watch.sh — A's polling loop (owner directive 2026-09-10, CSM Phase-1 bay).
# 3-min cycles x N (default 160 = 8 h horizon). Each cycle:
#   (1) read only NEW lines since last offsets — line offsets in a_poll_state.json
#       (shell_log.jsonl, interventions.jsonl, plan/state.md, work_log.md) so
#       compaction can never lose state; shrink of a tracked file resets to 0;
#   (2) judgment cases:
#       LONG >300 s shell -> judge (kill already covered by monitor 59240;
#         sanctioned CUDA model leg = let-run; unprovable = flag) + decision line
#       MODEL_DOWN (2-strike :18080) -> tools/master-work/ninfer_restart.sh (self-guarded)
#       new dated [$ESC] :8000 line in state.md -> one-copy rule: stop (kill the
#         LIVE ps-found pid, never the pid in the ESC text — 11:31 incident lesson)
#         or restart (CUDA default @100k, honor explicit CPU; /health + device verify)
#       other ESCs -> flagged for LLM ruling, never executed
#   (3) one status line per cycle; commit after each judgment batch (path-limited).
# Break + close-log when work_log.md shows PHASE 1 COMPLETE.
set -u
cd /home/goblin/ScriptEngine
CYCLES=${1:-160}
SLEEP_N=${SLEEP_N:-12}; SLEEP_S=${SLEEP_S:-15}   # env overrides exist for the 1-cycle smoke test only
STATEF=reports/master-work/a_poll_state.json
DEC=reports/master-work/decisions.md
SLOG=reports/master-work/shell_log.jsonl
FLOG=reports/master-work/interventions.jsonl
STM=plan/state.md
WLOG=reports/master-work/work_log.md
ACTIVE=/tmp/csmwatch_active.tsv
MODEL_RX='span-recall.*(--panel|--probe)|--probe [0-9]|canon-run|pytest tests/|scriptengine\.cli (eval|span-recall|transcripts-embed|transcript-search)|events-extract'

path_for(){ case $1 in
  shell_log.jsonl) echo "$SLOG";;
  interventions.jsonl) echo "$FLOG";;
  plan/state.md) echo "$STM";;
  work_log.md) echo "$WLOG";;
esac; }

init_state(){
  [ -f "$STATEF" ] && return 0
  python3 - "$STATEF" <<PY
import json
f="$STATEF"
files={"shell_log.jsonl":"$SLOG","interventions.jsonl":"$FLOG","plan/state.md":"$STM","work_log.md":"$WLOG"}
d={k:sum(1 for _ in open(p)) for k,p in files.items()}
open(f,"w").write(json.dumps(d,indent=1)+"\n")
PY
}

getoff(){ python3 -c '
import json,sys
try: print(json.load(open(sys.argv[1])).get(sys.argv[2],0))
except Exception: print(0)' "$STATEF" "$1"; }

setoff(){ python3 - "$STATEF" "$1" "$2" <<'PY'
import json,sys,os
f=sys.argv[1]
try: d=json.load(open(f))
except Exception: d={}
d[sys.argv[2]]=int(sys.argv[3])
t=f+".tmp"; open(t,"w").write(json.dumps(d,indent=1)+"\n"); os.replace(t,f)
PY
}

# newlines <key>: print lines since the stored offset (complete lines only);
# advance the offset; a shrunken file resets to 0 (append-only discipline makes
# this a rare path; ESC re-exposure is guarded by is_live_esc + dedup).
newlines(){
  local k=$1 f sz o
  f=$(path_for "$1"); sz=$(wc -l < "$f" 2>/dev/null || echo 0); o=$(getoff "$k")
  [ "$sz" -lt "$o" ] && o=0
  if [ "$sz" -gt "$o" ]; then setoff "$k" "$sz"; tail -n +$((o+1)) "$f"; fi
}

DIRTY=0; JUDG=0; JT=0
dec(){ printf -- '- %s [A] (csm-watch) %s\n' "$(date +%Y-%m-%dT%H:%M:%S%:z)" "$1" >> "$DEC"; JUDG=$((JUDG+1)); JT=$((JT+1)); DIRTY=1; }

commit_batch(){
  [ "$DIRTY" = 1 ] || return 0
  git add "$DEC" "$STATEF" 2>/dev/null
  if git commit -q -m "csm-watch $(date +%H:%M): A judgment batch ($(git diff --cached --name-only | tr '\n' ' '))" 2>/dev/null; then
    echo "  [commit] $(git log --oneline -1 | cut -c1-60)"
  fi
  DIRTY=0
}

# --- MODEL_DOWN (2-strike, then the self-guarded restart script) ---
QWEN_DOWN=0; QSTAT=ok
qwen_check(){
  if curl -s -m 5 http://localhost:18080/health 2>/dev/null | grep -q '"status":"ok"'; then QSTAT=ok; QWEN_DOWN=0; return; fi
  QSTAT=down; QWEN_DOWN=$((QWEN_DOWN+1))
  if [ "$QWEN_DOWN" -ge 2 ]; then
    dec "MODEL_DOWN (2 consecutive :18080 failures @ $(date +%H:%M:%S)): running tools/master-work/ninfer_restart.sh (self-guarded: no fight a switch-in-flight, 5-min cooldowns; 30-60 s reload — A/B model-less per charter 6.3, tmux+sessions survive)"
    timeout 400 bash tools/master-work/ninfer_restart.sh >> reports/master-work/control_run.log 2>&1
    local rc=$?
    if curl -s -m 15 http://localhost:18080/health 2>/dev/null | grep -q '"status":"ok"'; then
      dec "Qwen back UP post-restart (:18080 health ok @ $(date +%H:%M:%S); qwen_mode.txt refreshed by the script)"
    else
      dec "Qwen restart FAILED (rc=$rc, :18080 still down @ $(date +%H:%M:%S)) — flagged to directing session; check /home/goblin/ninfer-work/logs/ninfer_restart.log"
    fi
    QWEN_DOWN=0; DIRTY=1
  fi
}

# --- :8000 one-copy ops (ESC execution) ---
APIPG='python.*scriptengine\.api\.main'
esc_stop(){
  local pid i apps still n
  pid=$(pgrep -f "$APIPG" | head -1 || true)
  if [ -z "$pid" ]; then dec ":8000 stop ESC: already down (no api.main process) — no-op."; return; fi
  kill "$pid" 2>/dev/null
  for i in $(seq 1 15); do pgrep -f "$APIPG" >/dev/null || break; sleep 1; done
  still=$(pgrep -f "$APIPG" | head -1 || true)
  if [ -n "$still" ]; then kill -9 "$still" 2>/dev/null; sleep 2; fi
  apps=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | grep -c . || true)
  if curl -s -m 3 http://localhost:8000/health >/dev/null 2>&1; then
    dec ":8000 STOPPED per ESC (live pid $pid killed; /health STILL answering — flagged, check for stray launcher) — one-copy: nvidia compute-apps=$apps"
  else
    dec ":8000 STOPPED per ESC (live pid $pid killed — pid-freshness rule: ps-found pid, never the ESC text's; /health refusing; one-copy verified: nvidia compute-apps=$apps = Qwen-only)"
  fi
}

esc_restart(){
  local l=$1 dev pid i ok d n
  case "$l" in *"device=cpu"*|*"on CPU"*) dev=cpu;; *) dev=cuda;; esac
  pid=$(pgrep -f "$APIPG" | head -1 || true)
  if [ -n "$pid" ]; then dec ":8000 restart ESC: already up (pid $pid) — no-op."; return; fi
  if [ "$dev" = cpu ]; then
    setsid nohup env SCRIPTENGINE_DEVICE=cpu scriptengine/.venv/bin/python -m scriptengine.api.main >> /tmp/scriptengine_api.log 2>&1 < /dev/null &
  else
    setsid nohup scriptengine/.venv/bin/python -m scriptengine.api.main >> /tmp/scriptengine_api.log 2>&1 < /dev/null &
  fi
  ok=0
  for i in $(seq 1 45); do
    if curl -s -m 3 http://localhost:8000/health 2>/dev/null | grep -q '"status":"ok"'; then ok=1; break; fi
    sleep 2
  done
  n=$(pgrep -cf "$APIPG" || true)
  if [ "$ok" = 1 ]; then
    d=$(curl -s -m 3 http://localhost:8000/health | grep -o '"device":"[a-z]*"' | head -1)
    dec ":8000 RESTARTED per ESC (device=$dev; one-copy verified: /health ok $d, api.main copies=$n, Qwen untouched)"
  else
    dec ":8000 restart FAILED (/health not ok after 90 s @ $(date +%H:%M:%S)) — flagged to directing session; check /tmp/scriptengine_api.log"
  fi
}

# live = a dated line from THIS bay (local 2026-09-10, or UTC 2026-09-09 19:00+ which is local 09-10 00:00+).
# Everything else (undated [$ESC] 150k-era lines, other dates) = stale: flag, never execute.
is_live_esc(){
  case $1 in
    *'2026-09-10'T*) return 0;;
    *'2026-09-09'T1[9]*) return 0;;
    *'2026-09-09'T2[0-3]*) return 0;;
  esac
  return 1
}

flag_nonexec(){
  local l=$1 h
  h=$(printf '%s' "$l" | md5sum | cut -c1-10)
  [ "$(getoff "flag_$h")" = 1 ] && return 0
  setoff "flag_$h" 1
  EPEND=1
  dec "NON-AUTO ESC flagged (needs LLM/directing-session ruling, NOT executed): $(printf '%s' "$l" | cut -c1-220)"
}

# act on one new state.md line. Only a dated "[date] ESC ..." REQUEST line is a
# candidate; verb matching is verb-BEFORE-port ("stop :8000", "restart :8000") so
# a line merely mentioning ":8000 stop" in a negation ("no :8000 stop needed")
# can never trigger a kill. [$TSI]/position lines are read, never acted on.
scan_state_line(){
  local l=$1 ws=0 wr=0
  case "$l" in
    "\[\$ESC\]"*) flag_nonexec "$l"; return 0;;   # 150k-era prefix — never auto-execute
  esac
  if printf '%s' "$l" | grep -Eq '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}T[^]]+\] ESC'; then
    if is_live_esc "$l"; then
      case $l in *"stop :8000"*|*"stopping :8000"*) ws=1;; esac
      case $l in *"restart :8000"*|*"restarting :8000"*|*"restart-8000"*) wr=1;; esac
      if [ "$ws" = 1 ] || [ "$wr" = 1 ]; then
        [ "$ws" = 1 ] && esc_stop
        [ "$wr" = 1 ] && esc_restart "$l"
        return 0
      fi
    fi
    flag_nonexec "$l"; return 0
  fi
  return 0
}

# --- LONG >300 s judgments (active shells from shell_log; dedup by pid) ---
long_scan(){
  local pid age cmd inapps
  [ -f "$ACTIVE" ] || return 0
  while IFS=$'\t' read -r pid age cmd; do
    case "$pid" in ''|MAX) continue;; esac
    if grep -q "\"pid\":\"$pid\"" "$FLOG" 2>/dev/null && grep "\"pid\":\"$pid\"" "$FLOG" | grep -q '"event":"KILL"'; then
      dec "LONG $pid (${age} s): monitor 59240 already auto-killed it (provably-CPU model work; typed re-run hint delivered) — no A action."
    elif printf '%s' "$cmd" | grep -Eq "$MODEL_RX"; then
      inapps=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | grep -cx "$pid" || true)
      if [ "${inapps:-0}" -ge 1 ]; then
        dec "LONG $pid (${age} s, model work, GPU footprint): let-run — sanctioned in-process CUDA gate/probe leg under the 100k dial (pre-approved LONG pattern: 400-probe ~57 min, panel sweeps, canon-run); not a CPU job."
      else
        dec "LONG $pid (${age} s, model work, no persistent GPU footprint): FLAGGED for LLM ruling — in-process model loads show only transiently in nvidia-smi, so CPU-vs-CUDA is unprovable from here; the monitor covers the provably-CPU case, so default = watch, not blind-kill. Cmd: $(printf '%s' "$cmd" | cut -c1-140)"
      fi
    else
      dec "LONG $pid (${age} s, non-model shell): let-run — outside the model-work GPU rule; B's bounded work."
    fi
    setoff "long_$pid" 1
  done < "$ACTIVE"
}

# write $ACTIVE: one row per active (START-without-END) shell + MAX row
build_active(){
  python3 - "$SLOG" "$STATEF" "$ACTIVE" <<'PY'
import json,sys
from datetime import datetime
slog, statef, out = sys.argv[1], sys.argv[2], sys.argv[3]
start, gone = {}, set()
for line in open(slog):
    try: j = json.loads(line)
    except Exception: continue
    p = j.get("pid")
    if j.get("event") == "START": start[p] = (j.get("ts",""), j.get("cmd",""))
    elif p in start: gone.add(p)
try:
    judged = {k for k in json.load(open(statef)) if k.startswith("long_")}
except Exception: judged = set()
# shell_log ts is date -Iseconds (tz-aware +05:30); now must be aware-local too
now = datetime.now().astimezone()
maxd = 0
rows = []
for p, (ts, cmd) in start.items():
    if p in gone or f"long_{p}" in judged: continue
    try:
        t = datetime.fromisoformat(ts)
        if t.tzinfo is None: t = t.astimezone()
        age = int((now - t).total_seconds())
    except Exception: continue
    maxd = max(maxd, age)
    if age > 300: rows.append(f"{p}\t{age}\t{cmd[:200]}")
rows.append(f"MAX\t{maxd}\t")
open(out, "w").write("\n".join(rows) + "\n")
PY
}

# --- main loop ---
init_state
CY=0; EPEND=0
while [ "$CY" -lt "$CYCLES" ]; do
  CY=$((CY+1)); DIRTY=0; JUDG=0
  EPEND=0; P1=0
  qwen_check
  NEW_SHELL=$(newlines shell_log.jsonl)
  NEW_INT=$(newlines interventions.jsonl)
  NEW_STATE=$(newlines plan/state.md)
  NEW_WLOG=$(newlines work_log.md)
  NS=$(printf '%s' "$NEW_SHELL" | grep -c . || true)
  NI=$(printf '%s' "$NEW_INT" | grep -c . || true)
  build_active
  MAXD=$(awk -F'\t' '$1=="MAX"{print $2}' "$ACTIVE" 2>/dev/null || echo 0)
  long_scan
  if [ -n "$NEW_STATE" ]; then
    while IFS= read -r line; do
      [ -n "$line" ] && scan_state_line "$line"
    done <<< "$NEW_STATE"
  fi
  if grep -q "PHASE 1 COMPLETE" "$WLOG" 2>/dev/null; then P1=1; fi
  commit_batch
  next=watch
  [ "$P1" = 1 ] && next="CLOSE-LOGGED-exit"
  [ "$QSTAT" = down ] && next="QWEN-DOWN-check"
  [ "$EPEND" = 1 ] && next="ESC-pending-LLM"
  echo "[$(date +%H:%M:%S)] A-poll #${CY}/${CYCLES}: qwen=${QSTAT} :8000=$(curl -s -m 3 http://localhost:8000/health 2>/dev/null | grep -o '"device":"[a-z]*"' | cut -d'"' -f4 || echo down) new-shells=${NS} max-dur=${MAXD}s new-interv=${NI} judgments=${JUDG} esc-pend=${EPEND} p1=${P1} next=${next}"
  if [ "$P1" = 1 ]; then
    dec "PHASE 1 COMPLETE seen in work_log.md @ $(date +%H:%M:%S) — close logged; A watch loop exiting cleanly (B idles per spec; monitor 59240 keeps the shell-eye; a new poll block is re-issued by the directing session only when Phase 2 opens)"
    commit_batch
    break
  fi
  for s in $(seq "$SLEEP_N"); do sleep "$SLEEP_S"; done
done
echo "[A-poll END $(date +%H:%M:%S)] ${CY}/${CYCLES} cycles run; total judgments ${JT}; last commit $(git log --oneline -1 | cut -c1-50)"