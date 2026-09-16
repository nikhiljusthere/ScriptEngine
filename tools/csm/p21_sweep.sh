#!/usr/bin/env bash
# CSM P2.1 pre-baked sweep runner (PHASE2_JOB.md pre-bake leg; A17/A18/A26,
# council #29). Full 17,181-row panel x 4 doors (qa, narrative, roster, auto)
# + the 200-row held-out through auto, against a CUDA whole-card :8000 with
# Qwen DOWN. Nothing here needs an agent: pre-checks, halt conditions, the
# per-door watchdog and the receipt are all in this file (PHASE2_JOB.md 69-88:
# "a batch with no agent has no judgement, so the script must carry it").
#
# Preconditions (discharge BEFORE launching — the gate window is not part of
# this run and the pre-checks cannot see it): the R-8 four standing gates +
# eval --series jjk 31/31 green at the current pin, then Qwen :18080 DOWN
# and :8000 up on CUDA with the whole card. Pre-checks 11/12 enforce the
# service state (up + CUDA device) only.
#
# Launch (directing session, from the repo root):
#   setsid nohup bash tools/csm/p21_sweep.sh > /dev/null 2>&1 < /dev/null &
# Poll: halt + watchdog lines -> p21_sweep_<stamp>_run.log; per-door progress
# (every 100 rows, the CLI's on_progress) -> p21_sweep_<stamp>_door_<label>.log.
#
# Exit codes: 0 done. 4 :8000 health halt. 5 ERROR-rate halt. 10-12 pre-check
# failure (panel hash / service down or non-CUDA device / Qwen up). 20-23 door
# or sanity pre-pass rc (2 ledger corrupt or tier-0 miss, 3 dead-door,
# 1 crash). 30 integrity (row count).

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

# :8000 device (/health, main.py): a CPU service passes every other pre-check
# and would turn the A17 floors and the wall estimate into CPU numbers, so a
# non-CUDA device halts like a down service.
health_body="$(curl -s -m 10 "$BASE/health" || true)"
device="$(printf '%s' "$health_body" | "$VENV" -c 'import json,sys; print(json.load(sys.stdin).get("device","?"))' 2>/dev/null || echo down)"

{
  echo "# CSM P2.1 sweep receipt — $(date -Is)"
  echo
  echo "- git: $(git rev-parse --short HEAD) | status: $(git status --porcelain | wc -l) dirty paths"
  echo "- panel sha256: ${panel_sha_now} (frozen ${PANEL_SHA_EXPECT})"
  echo "- heldout sha256: ${heldout_sha_now} (frozen ${HELDOUT_SHA_EXPECT})"
  echo "- panel rows: ${panel_rows_now} (expect ${PANEL_ROWS}) | heldout rows: ${heldout_rows_now} (expect ${HELDOUT_ROWS})"
  echo "- :8000 /health: device ${device}"
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
if [ "$device" = "down" ]; then
  log "HALT pre-check: :8000 /health failed or unparsable — start the CUDA service first, then re-run — exit 11"
  exit 11
fi
if [ "$device" != "cuda" ]; then
  log "HALT pre-check: :8000 device=${device} (expect cuda — a CPU service makes the floors/estimates CPU numbers) — exit 11"
  exit 11
fi
if ss -ltn 2>/dev/null | grep -q ':18080 '; then
  log "HALT pre-check: Qwen :18080 is UP — the sweep leg wants the whole card (PHASE2_JOB.md 93-103): stop Qwen, then re-run — exit 12"
  exit 12
fi
log "pre-checks passed (panel+heldout frozen, :8000 up on ${device}, Qwen down)"

# heldout ledger path (the CLI recomputes the same 8-char panel hash at load)
h8=$("$VENV" -c 'import json,sys; sys.path.insert(0,"."); from scriptengine.eval.span_recall import _panel_hash; print(_panel_hash([list(r) for r in json.load(open(sys.argv[1]))])[:8])' "$HELDOUT")
HLEDGER="$LEDGER_DIR/sweep_auto_${h8}.jsonl"

# A18 control arm: a ledger resumes forward only when EVERY row (main file +
# .new sidecar) is stamped with the current HEAD. Any older stamp (e.g. the
# pre-R-8 f2a611d/2f67222 sanity rows) would attribute P1 parser fixes to
# P2.3, so those ledgers start from zero — and the .new sidecar counts: the
# CLI writes live rows there until the clean-exit merge (span_recall.py), so
# a stale-stamp sidecar is residue a re-merge would pull into the fresh door,
# while a current-stamp sidecar is resume state and is kept. A mid-run commit
# move leaves a mixed-stamp ledger: full restart.
# (cli.py _sweep_stamps stamps with `git rev-parse --short HEAD`, 7 chars)
HEAD7="$(git rev-parse --short HEAD)"
wipe_count=0
resume_count=0
count_stale() { # $1=ledger or sidecar -> rows NOT stamped HEAD7 (0 if absent)
  grep -v "\"commit\": \"${HEAD7}\"" "$1" 2>/dev/null | wc -l
}
manage_ledger() { # $1=main ledger path — A18 verdict over main + .new sidecar
  local L="$1" side="${1}.new" rows_l stale_l
  if [ ! -f "$L" ] && [ ! -f "$side" ]; then
    receipt "- ${L##*/}: absent (fresh)"
    return 0
  fi
  rows_l=$(( $(wc -l 2>/dev/null < "$L" || echo 0) + $(wc -l 2>/dev/null < "$side" || echo 0) ))
  stale_l=$(( $(count_stale "$L") + $(count_stale "$side") ))
  if [ "$rows_l" -gt 0 ] && [ "$stale_l" -eq 0 ]; then
    receipt "- ${L##*/}: ${rows_l} rows stamped ${HEAD7} — resume forward"
    resume_count=$((resume_count + 1))
  else
    receipt "- ${L##*/}: ${rows_l} rows, ${stale_l} stale — wiped (main + sidecar, stale stamp)"
    rm -f "$L" "$side"
    wipe_count=$((wipe_count + 1))
  fi
}
receipt "## A18 pre-wipe state"
receipt
for d in qa narrative roster auto; do
  manage_ledger "$LEDGER_DIR/sweep_${d}_e3d73720.jsonl"
done
manage_ledger "$HLEDGER"
receipt
log "A18: ${wipe_count} ledger(s) wiped (stale stamp), ${resume_count} resumed (stamped ${HEAD7})"

# PHASE2_JOB.md 66-67: the first-run-only sanity-100 per door, zero panel
# spend. A ledger wiped/fresh after the A18 pass (0 rows) gets the pre-pass;
# a resumed ledger already carries its sanity rows, so the pre-pass is
# skipped — the CLI's --sanity limit applies to UNPROBED rows, so capping a
# resumed run at 100 would leave 17,081 rows and trip the exit-30 check.
sanity_prepass() { # $1=label $2=api-door $3=panel-file $4=ledger
  local label="$1" door="$2" panel="$3" ledger="$4"
  local side="${ledger}.new" n rc
  n=$(( $(wc -l 2>/dev/null < "$ledger" || echo 0) + $(wc -l 2>/dev/null < "$side" || echo 0) ))
  if [ "$n" -gt 0 ]; then
    log "sanity: ${label} resumes from ${n} rows — pre-pass skipped (first-run only)"
    return 0
  fi
  local slog="$OUT/p21_sweep_${STAMP}_sanity_${label}.log"
  log "sanity: ${label} pre-pass (100 probes, zero panel spend)"
  "$VENV" -m scriptengine.cli span-recall --series csm --panel "$panel" --door "$door" --sanity 100 > "$slog" 2>&1
  rc=$?
  if [ "$rc" -ne 0 ]; then
    log "HALT: sanity pre-pass ${label} rc=${rc} (2=tamper/tier-0 miss, 3=dead-door, 1=crash) — log: ${slog##*/} — exit $((20 + rc))"
    exit $((20 + rc))
  fi
  log "sanity: ${label} pre-pass ok (100 rows into ${ledger##*/}; log: ${slog##*/})"
}

run_door() { # $1=label $2=api-door $3=panel-file $4=ledger $5=expected-rows
  # label names the receipt row / door log (e.g. "auto-heldout"); api-door is
  # what the CLI POSTs as the request mode (api/main.py:79 only accepts
  # qa/narrative/roster/relations/auto — a free-form label would 422), so the
  # heldout leg runs api-door "auto" under label "auto-heldout" and the
  # heldout panel's distinct 8-char hash keeps its ledger apart.
  local label="$1" door="$2" panel="$3" ledger="$4" rows="$5"
  local side="${ledger}.new"
  local doorlog="$OUT/p21_sweep_${STAMP}_door_${label}.log"
  DOORLOGS+=("$doorlog")
  local start end rc lines err pct main_l side_l total base_main base_side main_new side_new
  log "door ${label}: start (${rows} rows, ledger ${ledger##*/}, api door ${door})"
  # A18 resume: rows already in the ledger/sidecar (e.g. a pre-halt .new burst)
  # are not this run's rows — the ERROR window counts only rows written after
  # the baseline, or a stale ERROR burst from a prior halted run trips exit 5
  # on resume (span_recall.py keeps the sidecar until the clean-exit merge).
  base_main=$([ -f "$ledger" ] && wc -l < "$ledger" || echo 0)
  base_side=$([ -f "$side" ] && wc -l < "$side" || echo 0)
  start=$(date +%s)
  nohup "$VENV" -m scriptengine.cli span-recall --series csm --panel "$panel" --door "$door" > "$doorlog" 2>&1 &
  pid=$!
  # pid is script-global: the EXIT trap (set below, per door) must see it after
  # run_door returns.
  # If this shell dies (reboot, OOM kill of the runner), the nohup'ed CLI keeps
  # sweeping into the same sidecar — the EXIT trap kills it so a re-run of the
  # launch line is the only resume path.
  trap 'kill "$pid" 2>/dev/null' EXIT
  local health_fails=0 last_seen=0
  while kill -0 "$pid" 2>/dev/null; do
    sleep "$SLEEP"
    if curl -s -m 10 -o /dev/null "$BASE/health"; then
      health_fails=0
    else
      health_fails=$((health_fails + 1))
      log "door ${label}: :8000 health FAIL (${health_fails}/${HEALTH_FAILS_MAX})"
      if [ "$health_fails" -ge "$HEALTH_FAILS_MAX" ]; then
        kill "$pid" 2>/dev/null
        log "HALT: :8000 health failure x${HEALTH_FAILS_MAX} — sweep killed, resume after service recovery (exit 4)"
        exit 4
      fi
    fi
    # Live rows land in the .new sidecar until the CLI's clean-exit merge
    # (span_recall.py), so the watchdog counts main + sidecar and the ERROR
    # window tails the sidecar (the newest rows) last.
    main_l=$([ -f "$ledger" ] && wc -l < "$ledger" || echo 0)
    side_l=$([ -f "$side" ] && wc -l < "$side" || echo 0)
    total=$((main_l + side_l))
    if [ "$total" -gt "$last_seen" ]; then
      last_seen=$total
      main_new=$((main_l - base_main))
      side_new=$((side_l - base_side))
      err=$({ [ "$main_new" -gt 0 ] && tail -n +$((base_main + 1)) "$ledger" | tail -n "$ERROR_WINDOW"; [ "$side_new" -gt 0 ] && tail -n +$((base_side + 1)) "$side" | tail -n "$ERROR_WINDOW"; } | tail -n "$ERROR_WINDOW" | grep -c '"verdict": "ERROR"' || true)
      err=${err:-0}
      pct=$(( total * 100 / rows ))
      log "door ${label}: ${total}/${rows} (${pct}%) [main ${main_l} + live ${side_l}], last-${ERROR_WINDOW} ERROR=${err}, $(($(date +%s) - start))s"
      if [ "$err" -gt "$ERROR_BOUND" ]; then
        kill "$pid" 2>/dev/null
        log "HALT: ERROR ${err}/${ERROR_WINDOW} > bound ${ERROR_BOUND} — sweep killed (the .new sidecar survives the kill; ERROR rows re-probe on resume) (exit 5)"
        exit 5
      fi
    fi
  done
  wait "$pid"; rc=$?
  end=$(date +%s)
  if [ "$rc" -ne 0 ]; then
    log "door ${label}: CLI rc=${rc} (2=ledger corrupt/tier-0 miss, 3=dead-door, 1=crash) — log: ${doorlog##*/}"
    exit $((20 + rc))
  fi
  lines=$(wc -l 2>/dev/null < "$ledger" || echo 0)
  if [ "$lines" -ne "$rows" ]; then
    log "INTEGRITY: door ${label} ledger has ${lines}/${rows} rows — exit 30"
    exit 30
  fi
  local hit mdoc mspan trunc errs rate
  hit=$(grep -c '"verdict": "HIT"' "$ledger" || true)
  mdoc=$(grep -c '"verdict": "MISS_DOC"' "$ledger" || true)
  mspan=$(grep -c '"verdict": "MISS_SPAN"' "$ledger" || true)
  trunc=$(grep -c '"verdict": "TRUNCATED"' "$ledger" || true)
  errs=$(grep -c '"verdict": "ERROR"' "$ledger" || true)
  rate=$(awk -v h="$hit" -v r="$rows" 'BEGIN { printf "%.4f", (h / r) * 100 }')
  log "door ${label}: done — HIT ${hit} / MISS_DOC ${mdoc} / MISS_SPAN ${mspan} / TRUNCATED ${trunc} / ERROR ${errs}, hit_rate ${rate} %, $(( (end - start) / 60 ))m"
  receipt "| ${label} | ${ledger##*/} | ${lines} | ${hit} | ${mdoc} | ${mspan} | ${trunc} | ${errs} | ${rate} % | $(( (end - start) / 60 ))m |"
  return 0
}

DOORLOGS=()

{
  receipt "## Per-door results (panel ${PANEL_ROWS} rows; hit_rate over the FULL panel, §2a trap 3)"
  receipt
  receipt "| door | ledger | rows | HIT | MISS_DOC | MISS_SPAN | TRUNCATED | ERROR | hit_rate | wall |"
  receipt "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"
  receipt
  receipt "## Halt conditions (declared before the run, so a halted receipt carries them)"
  receipt
  receipt "- :8000 /health: ${HEALTH_FAILS_MAX} consecutive failures -> kill + exit 4 (resume after service recovery)"
  receipt "- ERROR rate: > ${ERROR_BOUND} of the last ${ERROR_WINDOW} rows THIS RUN WROTE (main + .new sidecar, past the door's baseline) -> kill + exit 5 (a stale .new burst from a prior halted run is excluded; ERROR rows re-probe on resume)"
  receipt
  receipt "## Resuming after a halt"
  receipt
  receipt "Re-run the same launch line: pre-checks re-verify the frozen inputs, and a ledger"
  receipt "whose rows are all stamped with the current HEAD resumes forward (only ERROR rows"
  receipt "re-probe; live rows sit in the .new sidecar, merged on clean exit). A ledger with"
  receipt "any older-stamp row is wiped, sidecar included, and restarts (A18 — a mid-run"
  receipt "commit move invalidates the mixed-stamp ledger, full restart)."
} >> "$RECEIPT"

# first-run-only sanity pre-pass per wiped panel door (PHASE2_JOB.md 66-67);
# the heldout leg is the 200-row out-of-sample run itself — no pre-pass
sanity_prepass qa qa "$PANEL" "$LEDGER_DIR/sweep_qa_e3d73720.jsonl"
sanity_prepass narrative narrative "$PANEL" "$LEDGER_DIR/sweep_narrative_e3d73720.jsonl"
sanity_prepass roster roster "$PANEL" "$LEDGER_DIR/sweep_roster_e3d73720.jsonl"
sanity_prepass auto auto "$PANEL" "$LEDGER_DIR/sweep_auto_e3d73720.jsonl"

log "sweep sequence: qa -> narrative -> roster -> auto (full panel), then auto heldout"
run_door qa qa "$PANEL" "$LEDGER_DIR/sweep_qa_e3d73720.jsonl" "$PANEL_ROWS"
run_door narrative narrative "$PANEL" "$LEDGER_DIR/sweep_narrative_e3d73720.jsonl" "$PANEL_ROWS"
run_door roster roster "$PANEL" "$LEDGER_DIR/sweep_roster_e3d73720.jsonl" "$PANEL_ROWS"
run_door auto auto "$PANEL" "$LEDGER_DIR/sweep_auto_e3d73720.jsonl" "$PANEL_ROWS"

# label "auto-heldout", api door "auto" (the heldout panel's distinct 8-char
# hash keeps sweep_auto_<h8>.jsonl separate from the full-panel auto ledger)
log "heldout: 200 rows through auto (out-of-sample, A24(a))"
run_door auto-heldout auto "$HELDOUT" "$HLEDGER" "$HELDOUT_ROWS"

{
  receipt
  receipt "## Door logs"
  receipt
  for dl in "${DOORLOGS[@]}"; do
    receipt "- ${dl##*/}"
  done
  receipt
  receipt "## A17 grading inputs (Claude, after this run)"
  receipt
  receipt "- auto full-panel rate vs the 97.5 % bar (the post-R-8 product number)"
  receipt "- qa: miss file (MISS_DOC + MISS_SPAN + ERROR) triaged row by row — \"miss file empty\" applies to qa alone"
  receipt "- narrative / roster: documented floors; every residual triaged with class + reason"
  receipt "- heldout auto rate: out-of-sample check (a memorised panel looks green)"
  receipt "- second R-8 misroute decision: post-measurement, per the A17 bar"
} >> "$RECEIPT"

log "P2.1 sweep complete — receipt: ${RECEIPT##*/}"
exit 0