#!/bin/sh
# Egress batch tail (2026-09-26): F1-MCU + F3 + F5, serialised behind the
# F1-MARVEL backfill (pid $1). Campaign throttle protocol (plan §1a): every
# step stops clean on a 429 (revid_backfill exit 2 / fixlist rc!=0); on a
# stop, ROTATE the egress (nordvpn, exhausted-country pool — owner ruling
# 2026-09-26) and re-run the failed step. Never blind-retry a stalled IP.
#
# Usage: setsid nohup sh tools/marvel/egress_batch_tail.sh <marvel-pid> &
set -u
REPO="$(cd "$(dirname "$0")/../../" && pwd)"
cd "$REPO"
MARVEL_PID="${1:-}"
LOG="reports/marvel/receipts/egress_batch_tail_2026-09-26.log"
NOTE="FI 187.40.62.58 (nordvpn fi214, exhausted pool 2026-09-26)"
PY="$REPO/scriptengine/.venv/bin/python"

if [ -n "$MARVEL_PID" ]; then
  n=0
  while kill -0 "$MARVEL_PID" 2>/dev/null; do
    n=$((n+1)); [ "$n" -gt 1440 ] && { echo "gave up waiting for marvel pid" >> "$LOG"; exit 3; }
    sleep 60
  done
fi

# The backfill writes a receipt named revid_backfill_<series>_<stop_reason>_2026-09-26.json
REC="$(ls reports/marvel/receipts/revid_backfill_marvel_*_2026-09-26.json 2>/dev/null | tail -1)"
if [ -z "$REC" ]; then
  echo "no marvel backfill receipt — investigate, then re-run" >> "$LOG"
  exit 3
fi
STOP="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["stop_reason"])' "$REC" 2>/dev/null || echo unreadable)"
if [ "$STOP" != "complete" ]; then
  echo "marvel backfill stop_reason=$STOP ($REC) — halting tail; rotate egress + re-run" >> "$LOG"
  exit 2
fi
echo "marvel backfill complete ($REC); starting MCU backfill" >> "$LOG"

env PYTHONPATH="$REPO" "$PY" tools/marvel/revid_backfill.py \
  --series mcu --egress-note "$NOTE" >> "$LOG" 2>&1
MCU_RC=$?
if [ "$MCU_RC" -ne 0 ]; then
  echo "mcu backfill rc=$MCU_RC — halting; rotate egress + re-run" >> "$LOG"
  exit 2
fi
echo "mcu backfill complete; starting F3 recrawl" >> "$LOG"

env PYTHONPATH="$REPO" "$PY" tools/marvel/fixlist_fetch.py \
  --series marvel --titles-file tools/marvel/f3_recrawl_2026-09-26.jsonl \
  --disambiguate --shard-id f3_recrawl_2026-09-26 \
  --egress-note "$NOTE" >> "$LOG" 2>&1
F3_RC=$?
if [ "$F3_RC" -ne 0 ]; then
  echo "f3 rc=$F3_RC — halting; rotate egress + re-run" >> "$LOG"
  exit 2
fi
echo "f3 complete; starting F5 top-up" >> "$LOG"

env PYTHONPATH="$REPO" "$PY" tools/marvel/fixlist_fetch.py \
  --series mcu --titles-file tools/marvel/mcu_topup_f5_2026-09-26.jsonl \
  --shard-id mcu_topup_f5_2026-09-26 \
  --egress-note "$NOTE" >> "$LOG" 2>&1
F5_RC=$?
echo "egress batch tail done (mcu_rc=$MCU_RC f3_rc=$F3_RC f5_rc=$F5_RC)" >> "$LOG"
exit "$F5_RC"