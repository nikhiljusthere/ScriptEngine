#!/bin/sh
# Egress batch WATCHDOG (2026-09-26) — sole orchestrator of the F1+F3+F5 egress
# batch (replaces egress_batch_tail.sh, whose wait condition tracked the
# launcher's bash wrapper pid instead of the python pid).
#
# Campaign throttle protocol (plan §1a, owner ruling 2026-09-26):
#   * serial stages: marvel F1 backfill -> mcu F1 backfill -> F3 recrawl -> F5 top-up
#   * F1 backfill stages run with --workers 8 (2026-09-27 speedup: parallel API
#     batches; the tool's 429/error clean-stop is unchanged, so the rotation
#     protocol below still applies verbatim)
#   * every egress (re)connect is verified with api.ipify.org (egress logged)
#   * a stage that stops on 429/error is re-run ONLY after rotating to a fresh
#     egress IP from the EXHAUSTED-country pool (FI DE FR ES UK SG JP CA NL US CH —
#     all consumed on 2026-09-25, re-use pre-authorized; a NEW country would
#     need owner budget sign-off). Never blind-retry a stalled IP.
#   * if the VPN session drops while a stage is alive, the stage is stopped
#     cleanly (tools are idempotent/re-resumable), egress re-verified, resumed.
#   * all actions are receipted to the log below ("a claim that is not on disk
#     did not happen").
#
# Usage: setsid nohup sh tools/marvel/egress_watchdog.sh >/dev/null 2>&1 &
# State: /tmp/opencode/egress_watchdog_2026-09-26.state
set -u
REPO="$(cd "$(dirname "$0")/../../" && pwd)"
cd "$REPO"
PY="scriptengine/.venv/bin/python"
STATE=/tmp/opencode/egress_watchdog_2026-09-26.state
LOG="reports/marvel/receipts/egress_watchdog_2026-09-26.log"
POOL="FI DE FR ES UK SG JP CA NL US CH"
TICK=600          # 10 min
MAX_TICKS=432     # 72 h hard stop (owner review)

log() { echo "$(date '+%F %T') $*" >> "$LOG"; }

# ---------- state ----------
# Adopt whatever is already running (marvel backfill launched pre-watchdog).
if [ -f "$STATE" ] && grep -q '^STAGE=' "$STATE"; then
  . "$STATE"
fi
if [ -z "${STAGE:-}" ]; then
  STAGE=marvel; COUNTRY=FI; RUN=1; RUN_START=$(date +%s); LAST_IP=""
fi
save_state() {
  printf 'STAGE=%s\nCOUNTRY=%s\nRUN=%s\nRUN_START=%s\nLAST_IP=%s\nREEXEC_FOR=%s\n' \
    "$STAGE" "$COUNTRY" "$RUN" "$RUN_START" "$LAST_IP" "${REEXEC_FOR:-}" > "$STATE"
}

# ---------- stage helpers (anchored patterns skip the bash launcher wrapper) ----------
stage_pid() {
  case "$STAGE" in
    marvel) pgrep -f '^scriptengine/\.venv/bin/python tools/marvel/revid_backfill\.py --series marvel ' | head -1 ;;
    mcu)    pgrep -f '^scriptengine/\.venv/bin/python tools/marvel/revid_backfill\.py --series mcu ' | head -1 ;;
    f3)     pgrep -f '^scriptengine/\.venv/bin/python tools/marvel/fixlist_fetch\.py --series marvel --titles-file tools/marvel/f3_recrawl' | head -1 ;;
    f5)     pgrep -f '^scriptengine/\.venv/bin/python tools/marvel/fixlist_fetch\.py --series mcu --titles-file tools/marvel/mcu_topup_f5' | head -1 ;;
  esac
}

stage_log() {  # first run of a stage keeps the plain log name
  case "$STAGE" in
    marvel) L="revid_backfill_marvel_2026-09-26" ;;
    mcu)    L="revid_backfill_mcu_2026-09-26" ;;
    f3)     L="fixlist_f3_2026-09-26" ;;
    f5)     L="fixlist_f5_2026-09-26" ;;
  esac
  [ "$RUN" -gt 1 ] && L="$L_run$RUN"
  echo "reports/marvel/receipts/$L.log"
}

# newest receipt for this stage (backfill: file is overwritten per run;
# fixlist: fixed name, only accepted from the current run window)
latest_receipt() {
  case "$STAGE" in
    marvel|mcu)
      ls -t "reports/marvel/receipts/revid_backfill_${STAGE}_"*_2026-09-26.json 2>/dev/null | head -1 ;;
    f3) R="reports/marvel/receipts/fixlist_f3_recrawl_2026-09-26.json"
        if [ -f "$R" ] && [ "$(stat -c %Y "$R" 2>/dev/null || echo 0)" -gt "$RUN_START" ]; then echo "$R"; fi ;;
    f5) R="reports/marvel/receipts/fixlist_mcu_topup_f5_2026-09-26.json"
        if [ -f "$R" ] && [ "$(stat -c %Y "$R" 2>/dev/null || echo 0)" -gt "$RUN_START" ]; then echo "$R"; fi ;;
  esac
}

stage_ok() {  # receipt from this stage and fully successful
  [ -n "$1" ] || return 1
  case "$STAGE" in
    marvel|mcu)
      python3 - "$1" <<'EOF'
import json, sys
r = json.load(open(sys.argv[1]))
sys.exit(0 if r.get("stop_reason") == "complete" else 1)
EOF
      ;;
    f3|f5)
      python3 - "$1" <<'EOF'
import json, sys
r = json.load(open(sys.argv[1]))
sys.exit(0 if not any(str(x.get("status", "")).startswith("missing-or-failed")
                      for x in r.get("rows", [])) else 1)
EOF
      ;;
  esac
}

stop_summary() {
  case "$STAGE" in
    marvel|mcu)
      python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["stop_reason"])' "$1" 2>/dev/null ;;
    f3|f5)
      python3 -c 'import json,sys;r=json.load(open(sys.argv[1]));print("bad_rows="+str(sum(1 for x in r["rows"] if str(x.get("status","")).startswith("missing-or-failed"))))' "$1" 2>/dev/null ;;
  esac
}

# ---------- egress ----------
vpn_ok() { timeout 20 nordvpn status 2>/dev/null | head -1 | grep -q 'Status: Connected'; }
egress_ip() { timeout 20 curl -s -m 15 https://api.ipify.org 2>/dev/null; }

verify_egress() {  # no reconnect: just confirm VPN + egress IP (log it)
  if vpn_ok; then
    IP="$(egress_ip)"
    if [ -n "$IP" ]; then
      LAST_IP=$IP
      log "egress verified (unchanged): $IP (country $COUNTRY)"
      return 0
    fi
    log "WARN: VPN connected but ipify unreachable — proceeding (stage will self-stop if truly dead)"
    return 0
  fi
  log "egress NOT verified (VPN down) — rotating"
  return 1
}

# $1 = "same"  (VPN session drop: current country first)
#      "other" (429/stalled IP: a DIFFERENT country first — never blind-retry)
rotate_egress() {
  if [ "$1" = "other" ]; then
    ORDER=""
    for c in $POOL; do [ "$c" = "$COUNTRY" ] || ORDER="$ORDER $c"; done
    ORDER="$ORDER $COUNTRY"
  else
    ORDER="$COUNTRY"
    for c in $POOL; do [ "$c" = "$COUNTRY" ] || ORDER="$ORDER $c"; done
  fi
  for c in $ORDER; do
    if vpn_ok; then
      timeout 30 nordvpn disconnect >> "$LOG" 2>&1 || true
      sleep 3
    fi
    log "  nordvpn connect $c ..."
    timeout 90 nordvpn connect "$c" >> "$LOG" 2>&1
    sleep 8
    IP="$(egress_ip)"
    if vpn_ok && [ -n "$IP" ]; then
      if [ "$1" = "other" ] && [ "$IP" = "$LAST_IP" ]; then
        log "  $c returned the SAME stalled IP $IP — trying next country"
        continue
      fi
      COUNTRY=$c; LAST_IP=$IP
      log "  egress verified: $IP (country $c)"
      return 0
    fi
    log "  $c failed (ip='${IP:-none}')"
  done
  log "ALL POOL COUNTRIES FAILED — no verified egress; retrying next tick. If this persists at the morning gate, owner budget sign-off is needed for a new country."
  return 1
}

stop_stage() {  # clean stop of a running stage (resumable: tools re-scan unstamped)
  P="$(stage_pid)"
  [ -n "$P" ] || return 0
  log "  stopping stage pid $P (SIGTERM)"
  kill -TERM "$P" 2>/dev/null
  n=0
  while [ $n -lt 10 ] && [ -d "/proc/$P" ]; do sleep 1; n=$((n+1)); done
  if [ -d "/proc/$P" ]; then log "  still alive — SIGKILL"; kill -KILL "$P" 2>/dev/null; fi
}

launch() {  # (re)start the current stage with a fresh egress note; VERIFY the spawn
  # (2026-09-27 hardening: run-2's first launch() silently failed — the setsid job
  # never started, its error went to the watchdog's /dev/null stderr, and the
  # "launched" line was a lie (found when the marvel log stayed empty). Now: 3
  # in-place attempts on the SAME egress (no rotation), each verified via
  # stage_pid after 5 s; success is logged with the real pid. If all 3 fail the
  # failure is logged here (visible in $LOG) and the next tick's dead-run path
  # rotates egress and launches again.)
  NOTE="$COUNTRY ${LAST_IP} (nordvpn, exhausted pool 2026-09-26, watchdog run $RUN)"
  case "$STAGE" in
    marvel|mcu) : ;;
    f3|f5)      : ;;
    *) log "LAUNCH: unknown stage $STAGE — refusing"; return 1 ;;
  esac
  attempt=1
  while [ $attempt -le 3 ]; do
    case "$STAGE" in
      marvel) setsid nohup env PYTHONPATH="$REPO" "$PY" tools/marvel/revid_backfill.py \
                --series marvel --workers 8 --egress-note "$NOTE" >> "$(stage_log)" 2>&1 < /dev/null & ;;
      mcu)    setsid nohup env PYTHONPATH="$REPO" "$PY" tools/marvel/revid_backfill.py \
                --series mcu --workers 8 --egress-note "$NOTE" >> "$(stage_log)" 2>&1 < /dev/null & ;;
      f3)     setsid nohup env PYTHONPATH="$REPO" "$PY" tools/marvel/fixlist_fetch.py \
                --series marvel --titles-file tools/marvel/f3_recrawl_2026-09-26.jsonl \
                --disambiguate --shard-id f3_recrawl_2026-09-26 \
                --egress-note "$NOTE" >> "$(stage_log)" 2>&1 < /dev/null & ;;
      f5)     setsid nohup env PYTHONPATH="$REPO" "$PY" tools/marvel/fixlist_fetch.py \
                --series mcu --titles-file tools/marvel/mcu_topup_f5_2026-09-26.jsonl \
                --shard-id mcu_topup_f5_2026-09-26 \
                --egress-note "$NOTE" >> "$(stage_log)" 2>&1 < /dev/null & ;;
    esac
    sleep 5
    P="$(stage_pid)"
    if [ -n "$P" ]; then
      log "launched stage=$STAGE run=$RUN (pid $P, attempt $attempt, note: $NOTE) -> $(stage_log)"
      return 0
    fi
    log "LAUNCH attempt $attempt/3 FAILED stage=$STAGE run=$RUN (no stage process after 5 s) — retrying on same egress $LAST_IP"
    attempt=$((attempt+1))
  done
  log "LAUNCH FAILED stage=$STAGE run=$RUN (3 attempts, no stage process) — re-execing watchdog in a FRESH process context (2026-09-27: long-lived watchdogs lost the ability to spawn stage jobs silently after nordvpn connect; re-exec adopts the state file, one re-exec per RUN to avoid burning pool countries in a failure loop)"
  if [ "${REEXEC_FOR:-}" != "$RUN" ]; then
    REEXEC_FOR=$RUN
    save_state
    exec sh "$0"
  fi
  log "LAUNCH FAILED (re-exec already used for run $RUN) — next tick will rotate egress and launch again"
  return 1
}

advance() {
  case "$STAGE" in
    marvel) STAGE=mcu ;;
    mcu)    STAGE=f3 ;;
    f3)     STAGE=f5 ;;
    f5)
      log "EGRESS BATCH COMPLETE (marvel+mcu F1 backfill, F3 recrawl, F5 top-up). Next: delta re-gate (plan phase C entry)."
      save_state
      log "watchdog exiting (all stages done)"
      exit 0
      ;;
  esac
  RUN=1; RUN_START=$(date +%s)
  log "advancing to stage=$STAGE"
  # No stop happened here — a working egress IP is fine; only rotate if it
  # is actually down.
  if ! verify_egress; then
    if ! rotate_egress "same"; then save_state; return; fi
  fi
  launch
}

# ---------- tick ----------
tick() {
  PID="$(stage_pid)"
  if [ -n "$PID" ]; then
    if ! vpn_ok; then
      log "tick: stage=$STAGE run=$RUN ALIVE (pid $PID) but VPN DOWN — stop -> rotate -> resume"
      stop_stage
      if rotate_egress "same"; then RUN=$((RUN+1)); RUN_START=$(date +%s); launch; fi
      save_state
      return
    fi
    IPNOW="$(egress_ip)"
    if [ -n "$IPNOW" ]; then
      LAST_IP="$IPNOW"
    else
      log "tick: WARN ipify unreachable but VPN connected — trusting the stage's own request path (it self-stops with an error receipt if truly dead)"
    fi
    STAGNANT=$(( $(date +%s) - $(stat -c %Y "$(stage_log)" 2>/dev/null || echo $(date +%s)) ))
    if [ "$STAGNANT" -gt 900 ]; then
      log "tick: stage=$STAGE alive (pid $PID) but log stagnant ${STAGNANT}s — stop -> rotate -> resume"
      stop_stage
      if rotate_egress "same"; then RUN=$((RUN+1)); RUN_START=$(date +%s); launch; fi
      save_state
      return
    fi
    log "tick: stage=$STAGE run=$RUN alive (pid $PID) egress=${LAST_IP:-unverified} progress: $(tail -1 "$(stage_log)" 2>/dev/null)"
    save_state
    return
  fi

  # stage dead: classify
  REC="$(latest_receipt)"
  if [ -n "$REC" ] && stage_ok "$REC"; then
    log "stage=$STAGE run=$RUN complete ($(stop_summary "$REC"); echo; basename "$REC")"
    advance
    save_state
    return
  fi
  if [ -n "$REC" ]; then
    log "stage=$STAGE run=$RUN stopped: $(stop_summary "$REC") — rotating to a FRESH IP (no blind retry)"
    if rotate_egress "other"; then RUN=$((RUN+1)); RUN_START=$(date +%s); launch; fi
    save_state
    return
  fi
  log "stage=$STAGE run=$RUN dead with NO receipt (crash or hard kill) — rotating and re-running (idempotent)"
  if rotate_egress "other"; then RUN=$((RUN+1)); RUN_START=$(date +%s); launch; fi
  save_state
}

# ---------- main loop ----------
log "watchdog start (adopting stage=$STAGE run=$RUN; stage pid $(stage_pid))"
save_state
i=0
while :; do
  i=$((i+1))
  tick
  [ $i -ge "$MAX_TICKS" ] && { log "HARD STOP: ${MAX_TICKS} ticks elapsed — owner review"; break; }
  sleep "$TICK"
done
log "watchdog exit (stage=$STAGE run=$RUN)"
save_state