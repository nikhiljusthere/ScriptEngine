#!/usr/bin/env bash
# CSM P2.1 pre-baked sweep runner (PHASE2_JOB.md pre-bake leg; A17/A18/A26,
# council #29). Full 17,181-row panel x 4 doors (qa, narrative, roster, auto)
# + the 200-row held-out through auto, against a CUDA whole-card :8000 with
# Qwen DOWN. Nothing here needs an agent: pre-checks, halt conditions, the
# per-door watchdog and the receipt are all in this file (PHASE2_JOB.md 69-88:
# "a batch with no agent has no judgement, so the script must carry it").
#
# Launch (directing session, from the repo root):
#   setsid nohup bash tools/csm/p21_sweep.sh > /dev/null 2>&1 < /dev/null &
# then poll the newest reports/master-work/p21_sweep_*_run.log.
#
# Exit codes: 0 done. 4 :8000 health halt. 5 ERROR-rate halt. 10-12 pre-check
# failure (panel hash / service down / Qwen up). 20-23 door rc (2 ledger
# corrupt or tier-0 miss, 3 dead-door, 1 crash). 30 integrity (row count).

set -u -o pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO" || exit 99
VENV="$REPO/scriptengine/.venv/bin/python"
BASE="http://127.0.0.1:8000"          # mirrors span_recall.BASE
PANEL="reports/csm/panel_csm.json"
HELDOUT="reports/csm/panel_csm.json.heldout.json"
LEDGER_DIR="reports/span-recall/csm"
OUT="reports/master-work"
STAMP="$(date +%Y%m%d_%H%M%S)"
RUNLOG="$OUT/p21_sweep_${STAMP}_run.log"
RECEIPT="$OUT/p21_sweep_${STAMP}_RECEIPT.md"
PANEL_ROWS=17181
HELDOUT_ROWS=200
# A26 frozen control-arm inputs (reports/csm/GATE.md P2.1 step-0 table)
PANEL_SHA_EXPECT="cf72135fb03ef82cbe3cfeb4d943442d165b6fa8cf1f34058bbcda98c6ab25ec"
HELDOUT_SHA_EXPECT="604dc8ca14b177701511b73b27d64170de792f3b0d212846f66b2756264124e8"
# Declared halt bound (PHASE2_JOB.md 77-80): the 11:23 incident wrote 400
# straight ERROR rows against a dead service and nobody noticed for minutes.
ERROR_WINDOW=50
ERROR_BOUND=10
HEALTH_FAILS_MAX=2
SLEEP=30

mkdir -p "$OUT"
log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$RUNLOG"; }
receipt() { echo "$*" >> "$RECEIPT"; }

panel_sha() { sha256sum "$1" | cut -d' ' -f1; }

# --- pre-checks (zero GPU spend) ------------------------------------------
panel_sha_now="$(panel_sha "$PANEL")"
heldout_sha_now="$(panel_sha "$HELDOUT")"
# The pin file is a dict ({"panel": [...], "hash": ...}); the held-out side
# file is a bare row array (COUNCIL_csm-3 Ruling 7) -- both load (cli.py 2153).
panel_rows_now=$("$VENV" -c 'import json,sys; d=json.load(open(sys.argv[1])); print(len(d["panel"]))' "$PANEL")
heldout_rows_now=$("$VENV" -c 'import json,sys; print(len(json.load(open(sys.argv[1]))))' "$HELDOUT")

{
  echo "# CSM P2.1 sweep receipt — $(date -Is)"
  echo
  echo "- git: $(git rev-parse --short HEAD) | status: $(git status --porcelain | wc -l) dirty paths"
  echo "- panel sha256: ${panel_sha_now} (frozen ${PANEL_SHA_EXPECT})"
  echo "- heldout sha256: ${heldout_sha_now} (frozen ${HELDOUT_SHA_EXPECT})"
  echo "- panel rows: ${panel_rows_now} (expect ${PANEL_ROWS}) | heldout rows: ${heldout_rows_now} (expect ${HELDOUT_ROWS})"
  echo "- Qwen :18080: $(if ss -ltn 2>/dev/null | grep -q ':18080 '; then echo UP; else echo down; fi)"
  echo "- VRAM: $(nvidia-smi --query-gpu=memory.used,memory.free --format=csv,noheader 2>/dev/null | head -1)"
  echo
} > "$RECEIPT"

if [ "$panel_sha_now" != "$PANEL_SHA_EXPECT" ] || [ "$heldout_sha_now" != "$HELDOUT_SHA_EXPECT" ]; then
  log "HALT pre-check: panel/heldout sha256 differs from the A26 frozen inputs — exit 10"
  exit 10
fi
if [ "$panel_rows_now" != "$PANEL_ROWS" ] || [ "$heldout_rows_now" != "$HELDOUT_ROWS" ]; then
  log "HALT pre-check: panel/heldout row count changed — exit 10"
  exit 10
fi
if curl -s -m 10 -o /dev/null "$BASE/health"; then
  log ":8000 /health ok"
else
  log "HALT pre-check: :8000 /health failed — start the CUDA service first, then re-run — exit 11"
  exit 11
fi
if ss -ltn 2>/dev/null | grep -q ':18080 '; then
  log "HALT pre-check: Qwen :18080 is UP — the sweep leg wants the whole card (PHASE2_JOB.md 93-103): stop Qwen, then re-run — exit 12"
  exit 12
fi
log "pre-checks passed (panel+heldout frozen, :8000 up, Qwen down)"

# A18 control arm: rows stamped with the current HEAD resume forward; any
# other stamp (e.g. the pre-R-8 f2a611d sanity rows) would attribute P1
# parser fixes to P2.3, so those ledgers start from zero. Wipe is per-ledger
# and only touches stale-stamp rows, so a halt + re-run on an unchanged tree
# resumes instead of restarting.
# (cli.py _sweep_stamps stamps with `git rev-parse --short HEAD`, 7 chars)
HEAD7="$(git rev-parse --short HEAD)"
wipe_count=0
resume_count=0
receipt "## A18 pre-wipe state"
receipt
for d in qa narrative roster auto; do
  L="$LEDGER_DIR/sweep_${d}_e3d73720.jsonl"
  if [ ! -f "$L" ] || [ ! -s "$L" ]; then
    receipt "- ${L##*/}: absent (fresh)"
    continue
  fi
  rows_l=$(wc -l < "$L")
  if grep -q "\"commit\": \"${HEAD7}\"" "$L"; then
    receipt "- ${L##*/}: ${rows_l} rows stamped ${HEAD7} — resume forward"
    resume_count=$((resume_count + 1))
  else
    receipt "- ${L##*/}: ${rows_l} rows, last stamp $(tail -1 "$L" | grep -o '"commit": "[a-f0-9]*"' | head -1) — wiped (stale stamp)"
    rm -f "$L"
    wipe_count=$((wipe_count + 1))
  fi
done
receipt
log "A18: ${wipe_count} ledger(s) wiped (stale stamp), ${resume_count} resumed (stamped ${HEAD7})"

# heldout ledger path (the CLI recomputes the same 8-char panel hash at load)
h8=$("$VENV" -c 'import json,sys; sys.path.insert(0,"."); from scriptengine.eval.span_recall import _panel_hash; print(_panel_hash([list(r) for r in json.load(open(sys.argv[1]))])[:8])' "$HELDOUT")
HLEDGER="$LEDGER_DIR/sweep_auto_${h8}.jsonl"

run_door() { # $1=door $2=panel-file $3=ledger $4=expected-rows
  local door="$1" panel="$2" ledger="$3" rows="$4"
  local doorlog="$OUT/p21_sweep_${STAMP}_door_${door}.log"
  DOORLOGS+=("$doorlog")
  local start end rc lines err pct
  log "door ${door}: start (${rows} rows, ledger ${ledger##*/})"
  start=$(date +%s)
  nohup "$VENV" -m scriptengine.cli span-recall --series csm --panel "$panel" --door "$door" > "$doorlog" 2>&1 &
  local pid=$!
  local health_fails=0 last_seen=0
  while kill -0 "$pid" 2>/dev/null; do
    sleep "$SLEEP"
    if curl -s -m 10 -o /dev/null "$BASE/health"; then
      health_fails=0
    else
      health_fails=$((health_fails + 1))
      log "door ${door}: :8000 health FAIL (${health_fails}/${HEALTH_FAILS_MAX})"
      if [ "$health_fails" -ge "$HEALTH_FAILS_MAX" ]; then
        kill "$pid" 2>/dev/null
        log "HALT: :8000 health failure x${HEALTH_FAILS_MAX} — sweep killed, resume after service recovery (exit 4)"
        exit 4
      fi
    fi
    if [ -f "$ledger" ]; then
      lines=$(wc -l < "$ledger")
      if [ "$lines" -gt "$last_seen" ]; then
        last_seen=$lines
        err=$(tail -n "$ERROR_WINDOW" "$ledger" | grep -c '"verdict": "ERROR"' || true)
        err=${err:-0}
        pct=$(( lines * 100 / rows ))
        log "door ${door}: ${lines}/${rows} (${pct}%), last-${ERROR_WINDOW} ERROR=${err}, $(($(date +%s) - start))s"
        if [ "$err" -gt "$ERROR_BOUND" ]; then
          kill "$pid" 2>/dev/null
          log "HALT: ERROR ${err}/${ERROR_WINDOW} > bound ${ERROR_BOUND} — sweep killed (ERROR rows re-probe on resume) (exit 5)"
          exit 5
        fi
      fi
    fi
  done
  wait "$pid"; rc=$?
  end=$(date +%s)
  if [ "$rc" -ne 0 ]; then
    log "door ${door}: CLI rc=${rc} (2=ledger corrupt/tier-0 miss, 3=dead-door, 1=crash) — log: ${doorlog##*/}"
    exit $((20 + rc))
  fi
  lines=$(wc -l < "$ledger")
  if [ "$lines" -ne "$rows" ]; then
    log "INTEGRITY: door ${door} ledger has ${lines}/${rows} rows — exit 30"
    exit 30
  fi
  local hit mdoc mspan trunc errs rate
  hit=$(grep -c '"verdict": "HIT"' "$ledger" || true)
  mdoc=$(grep -c '"verdict": "MISS_DOC"' "$ledger" || true)
  mspan=$(grep -c '"verdict": "MISS_SPAN"' "$ledger" || true)
  trunc=$(grep -c '"verdict": "TRUNCATED"' "$ledger" || true)
  errs=$(grep -c '"verdict": "ERROR"' "$ledger" || true)
  rate=$(awk -v h="$hit" -v r="$rows" 'BEGIN { printf "%.4f", (h / r) * 100 }')
  log "door ${door}: done — HIT ${hit} / MISS_DOC ${mdoc} / MISS_SPAN ${mspan} / TRUNCATED ${trunc} / ERROR ${errs}, hit_rate ${rate} %, $(( (end - start) / 60 ))m"
  receipt "| ${door} | ${ledger##*/} | ${lines} | ${hit} | ${mdoc} | ${mspan} | ${trunc} | ${errs} | ${rate} % | $(( (end - start) / 60 ))m |"
  return 0
}

DOORLOGS=()

{
  receipt "## Per-door results (panel ${PANEL_ROWS} rows; hit_rate over the FULL panel, §2a trap 3)"
  receipt
  receipt "| door | ledger | rows | HIT | MISS_DOC | MISS_SPAN | TRUNCATED | ERROR | hit_rate | wall |"
  receipt "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"
} >> "$RECEIPT"

log "sweep sequence: qa -> narrative -> roster -> auto (full panel), then auto heldout"
run_door qa "$PANEL" "$LEDGER_DIR/sweep_qa_e3d73720.jsonl" "$PANEL_ROWS"
run_door narrative "$PANEL" "$LEDGER_DIR/sweep_narrative_e3d73720.jsonl" "$PANEL_ROWS"
run_door roster "$PANEL" "$LEDGER_DIR/sweep_roster_e3d73720.jsonl" "$PANEL_ROWS"
run_door auto "$PANEL" "$LEDGER_DIR/sweep_auto_e3d73720.jsonl" "$PANEL_ROWS"

log "heldout: 200 rows through auto (out-of-sample, A24(a))"
run_door auto-heldout "$HELDOUT" "$HLEDGER" "$HELDOUT_ROWS"

{
  receipt
  receipt "## Door logs"
  receipt
  for dl in "${DOORLOGS[@]}"; do
    receipt "- ${dl##*/}"
  done
  receipt
  receipt "## Halt conditions (declared before the run)"
  receipt
  receipt "- :8000 /health: 2 consecutive failures -> kill + exit 4 (none fired)"
  receipt "- ERROR rate: > ${ERROR_BOUND} of last ${ERROR_WINDOW} rows -> kill + exit 5 (none fired; ERROR rows re-probe on resume)"
  receipt
  receipt "## A17 grading inputs (Claude, after this run)"
  receipt
  receipt "- auto full-panel rate vs the 97.5 % bar (the post-R-8 product number)"
  receipt "- qa: miss file (MISS_DOC + MISS_SPAN + ERROR) triaged row by row — \"miss file empty\" applies to qa alone"
  receipt "- narrative / roster: documented floors; every residual triaged with class + reason"
  receipt "- heldout auto rate: out-of-sample check (a memorised panel looks green)"
  receipt "- second R-8 misroute decision: post-measurement, per the A17 bar"
  receipt
  receipt "## Resuming after a halt"
  receipt
  receipt "Re-run the same launch line: pre-checks re-verify the frozen inputs, and ledgers"
  receipt "stamped with the current HEAD resume forward (only ERROR rows re-probe); a"
  receipt "ledger whose rows carry an older stamp is wiped and restarts (A18 — a"
  receipt "mid-run commit move invalidates the mixed-stamp ledger, full restart)."
} >> "$RECEIPT"

log "P2.1 sweep complete — receipt: ${RECEIPT##*/}"
exit 0