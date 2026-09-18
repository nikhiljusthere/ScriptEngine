# CSM 100% completion plan (2026-09-18, opencode; owner-ordered;
# AMENDED post plan-council — full 5+5+1, chair verdict APPROVED
# with amendments; transcript reports/csm/COUNCIL_csm_plan100.md)

Objective: CSM reaches the JJK bar — every in-scope question green,
content remainder 0, four gates green at each change. Start state: D6
CLOSED/A20 (`3c047604`), 486 bank at **463/486 (95.3%)**, coverage
473/537 remainder 0, JJK baseline exact.

Remainder ledger (23 reds, all filed):
- 7 D7 holdouts (named limit, D7 owner): chap-01 (numeric collision),
  org-03/05/06 (Prophecy / Tokyo Div 5 / Yakuza), vol-10 (guidebook),
  pool-140 (Body Control width), pool-358 (Biru Ken width).
- 16 floor rows (Phase-2-tracked, defect+owner+retest filed): 8
  arc-narrative, 4 state-over-time (interval facts), 3 abilities,
  1 causality.

Denominator annex (every exit below is read against these; a
checkpoint without numbers is not a checkpoint): closure target =
486 bank (463 green / 23 red); OOS200 locked floor 166, current 190
(a drop toward the floor is a WARNING, below 166 is FAIL); green30
must stay 30/30; coverage 473/537 remainder 0 (page instrument);
pytest pin 1,331; eval 31/31; span 48,572 offline + probe baseline
390 (current 398); canon 10/16 + 236/236 + 79.0%; JJK diff = gate
artifacts only, no code/corpus/store.

Standing guards (every regrade, no exceptions): 0 green→red
counter-flips (any counter-flip rolls back its mechanism alone);
green30 zero flips; OOS per annex; 4 gates green; blind-set accuracy
must not trail bank movement (a fix that moves only the bank fails).

GPU discipline: steady state Qwen 65k up + `:8000` down. Whole-card
windows (Qwen stopped, trap-restored to exact 65k argv) are REQUIRED
whenever `:8000` must be up (pytest trio, span live probe, canon,
page-run) or for extraction batches — triple residency peaks ~32.6
GB > 32 GB card. p23-only regrades may run co-located (`:8000` down,
Qwen up, one model holder ≈27 GB). Short bounded in-process probes
may co-locate in quiet windows with post-checks. No CPU job >15 min.
State survival: commit BEFORE gates (never gate an uncommitted tree
twice); reboot-rule updated on every land; predictions DB-verified.

Councils (parallel allowed per owner 2026-09-18): full 5+5+1 at every
**bold** checkpoint below. A step is DONE only when its council says so.

## Step 0 — blind fresh set (FIRST, before any D7b edit)

Author ~24 fresh questions (different subjects/pages than any 486
row, same classes: numeric-collision chapters/volumes, org
enumerations, guidebook volume, ability subsections, arc/state
rows), each with corpus-verified expect terms, frozen to
`reports/csm/blind_fresh_d7.jsonl`. Score against the frozen build
(`3c047604`) with the p23 judge path, archive results. Fixes that
move only the bank fail against this set. COUNCIL CHECKPOINT only
as part of D7a (baseline attached to findings).

## Step D7a — diagnose the 7 holdouts

Per holdout, from committed artifacts + chunk SQL, gold-error triage
first (expect terms verified in corpus — a wrong-gold row is retired
as gold error, not fixed as engine gap): served bundle vs gold-chunk
location vs expect terms → defect statement with DB-verified
locations + fix hypothesis + falsifiable flip prediction. Short
co-located live probes allowed where CPU evidence is ambiguous.
Exit: 7 defect sheets + blind baseline + P2-scope draft (runs
concurrent from here). COUNCIL CHECKPOINT (findings + fix designs).

## Step D7b — implement minimal fixes (uncommitted until gates)

Generic mechanisms only (no series names in `.py`; per-wiki scoping
via `series/csm/overrides.yaml` if needed). ONE mechanism at a time;
each ships with its falsifiable prediction, DB-verified location,
rollback trigger, and per-mechanism flip count (co-located p23-only
regrade, `:8000` down). Smoke is mechanical:
`tools/csm/d6_probe.py --row <id>` on target rows (direction only) —
attribution comes from the per-mechanism full-bank count, never from
smoke. Any mechanism with a counter-flip rolls back alone.

## Step D7c — gate + official regrade

Whole-card window: 4 gates + p23 486 + all guards (incl. blind-set
re-score). Exit: gates green + per-mechanism flips counted +
holdouts closed; non-flips re-open diagnosis (relabeling is not an
exit). COUNCIL CHECKPOINT (land? amend?).

## Step P2-scope — extraction leg design (runs concurrent with D7a)

16 floor rows: re-prove retrieval-vs-extraction per row FIRST (a
misdiagnosed retrieval failure must never buy GPU-days); residual
extraction scope only. Interval facts: extra_facts declarations per
JJK precedent costed against model extraction. GPU budget in hours,
abort/shrink rules, P2 fallback if over budget, retest triggers.
NOTHING extracts until this council locks scope. COUNCIL CHECKPOINT
(big decision + GPU-days).

## Step P2-execute — extract + rebuild + regrade + gates

Locked scope only, atomic resume, LLM owns the GPU, zero-regression
receipts (index shape, events remap, vector counts), span-recall +
coverage re-proof after the shape change, full gates + guards.
COUNCIL CHECKPOINT (results → verdict).

## Step CLOSE — 100% declaration

Only when: 486/486 green + coverage remainder 0 + final 4-gate
green run + declaration record (PHASE_CSM_100.md) + ledger key.
Remainder rows, if any, close by flip or by explicit void-set
criteria (cause + defect + retest pointer, council-decided — never
by phrasing). FINAL COUNCIL verdict. That council, not this plan,
declares 100%.
