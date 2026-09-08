# Peer Review 1 — CSM Unit-3 sweep fork (council 2026-09-09)

Reviewer weighting: **the chosen option burns wall-clock the campaign cannot afford.**
Fresh-context subagent; zero-GPU, read-only; all facts below re-verified on disk.

## Response-file mapping (caveat)

The task pointed at `adv_A.md`…`adv_E.md`; those files do not exist in
`reports/csm/receipts/council_unit3_sweep/`. The five advisor responses on disk carry
persona filenames. Letter mapping used here (deployment order by mtime, corroborated
by the executor's self-label):

| letter | file | deployed (mtime) |
|---|---|---|
| A | `adv_first-principles.md` | 03:48 |
| B | `adv_contrarian.md` | 03:50 |
| C | `adv_outsider.md` | 03:53 |
| D | `adv_executor.md` | 03:56 (its header self-labels “adv_D”) |
| E | `adv_expansionist.md` | 03:58 |

Persona names are cited throughout so the review is correct under any mapping.

## Verified on disk (re-checks of claims the responses lean on)

| Claim | Verdict | Evidence |
|---|---|---|
| Panel 17,181 sweep rows + 200 held-out, seed 42, hash `e3d73720…` | ✓ | `reports/csm/panel_csm.json` (`panel_size 17181`, `held_out_size 200`) |
| Pinned qa ledger 172 probed (165 HIT / 4 MISS_SPAN / 3 MISS_DOC), 17,009 remain | ✓ | `reports/span-recall/csm/sweep_qa_e3d73720.jsonl` (172 rows) |
| **The brief’s “168 probes ≈ CPU” is misattributed** | the 168-row re-probe was **CUDA** `:8000` (pid 103425, `device=cuda`); the 168 *CPU* rows were the “1200-s incident” sidecar (≈7.1 s/probe), dropped for provenance purity | `reports/csm/CSM3B_PRESTEP.md` §2–3 (the 168-probe datapoint is the *only* CUDA rate point; the CPU rate is the 1200-s incident, unverified today) |
| “0.9% hit rate” is completion-weighted (161/17,181), not per-probe | ✓ — per-probe miss ≈ 4% (7/168) | `CSM3B_PRESTEP.md` §3 |
| **Census is 39/60 (21 red), not 49/60** | raw file parses to 39 MECH_GREEN / 21 MECH_RED: arc-narrative 8 red, abilities 6 red, state-over-time 5 red, causality 1 red, appearance 1 red. The work_log “49/60” headline is a digit transposition — its own per-class greens sum to 39 | `reports/csm/census_dimensions_csm_results.jsonl` (mtime 09-09 03:39) vs `reports/master-work/work_log.md` 03:43 line |
| 150k state: Qwen pid 4348, 5,381 MiB free; `:8000` = CPU service (pid 4510) | ✓ (re-checked live: `/health` → `device: cpu`) | `work_log.md` 02:12 boot line; `GET /health` |
| In-process CUDA one-copy proven at 150k | census_dimensions 34 s + census_doors 18 s (= 52 s), Qwen alive, footprint unchanged 26,724 MiB; `:8000` stopped for the window, restarted CPU | `work_log.md` 03:43; `tools/census_dimensions.py` docstring (“in-process — the same path the :8000 /context endpoint uses”) |
| 150k plan rules: “no CPU shell command may exceed 15 s”; switching plan reserved for Phase 2 | ✓ | `plan/CSM_2PHASE_PLAN.md` lines 13, 19, 122; `plan/CSM_WAVE2_RESUME.md` §2 (job model loads in-process CUDA one-copy; server down for pytest/eval, up for HTTP gates), §4 (four gates after **every engine change**, one-copy ordering) |
| Job spec unit 3: batch sweep = “Wave-1 pinned panel + the 400-probe standing gate, on CUDA, one-copy ordering”; halt = miss-count regression or two no-reduction iterations → council | ✓ | `reports/master-work/CSM_WAVE2_JOB.md` unit 3 |
| **All five red-list entries are engine-class** (council trigger + four-gate re-run each) | ✓ — R-1 router count rule, R-2 qa-passage leg, R-3 roster token budget, R-4 chunker skip-set, R-5 relations router mode, all `scriptengine/` | `reports/csm/red_list_csm.md` line 88 |
| Sweep CLI is HTTP-only; no in-process 400-probe driver exists | `scriptengine/eval/span_recall.py` probes `http://127.0.0.1:8000` (urllib); `tools/probe_lines.py` is also HTTP; the census tools are the only in-process precedent (census shapes, not 400-probe) | verified in code |
| Held-out 200 rows have their own keyed ledger, 13 rows probed | ✓ (the outsider’s “never swept” is overstrong — it *is* swept, on its own ledger, 13/200) | `reports/span-recall/csm/sweep_qa_ec15e0d8.jsonl` (13 rows) |
| 5.4 extraction gate LIVE on structural-dimension reds | ✓ | `reports/csm/door_precheck_csm.md` (“if the census is red on a structural dimension, extraction proceeds”) |

## Per-response assessment

- **C — Outsider.** Sharpest factual catches (17,381 double-count; 39/60) and the only
  response that states the 150k device rule correctly: in-process CUDA one-copy is the
  plan-compliant, cheapest probe path (no switch, no LONG CPU run). Its “fold the full
  sweep into the orchestrator’s existing 100k switch — one switch, not two” is the
  wall-clock-optimal placement of the exhaustive panel. Weakness: its in-process 400-probe
  path is asserted, not verified (the CLI is HTTP-only; no driver exists yet), and its own
  first step defaults to the CLI route.
- **D — Executor (self-labeled adv_D).** Best execution quality: concrete 30-min/4-h/tomorrow
  timeline, parallelizes probe + miss-queue authoring, deepest on-disk spot-checks, and the
  only one that runs the 39/60 correction through the queue (“21 dimension-census reds”).
  Weakness for this weighting: anchors the probe on LONG-flagged CPU runs (35–48 min each,
  plan’s 15 s rule says probes go to GPU), and its “4 hours” for R-1..R-5 closure
  under-budgets 5 × four-gate re-runs + council triggers.
- **B — Contrarian.** Best halt-metric design: pin the halt denominator to a fixed 400-row
  grading subset re-probed after each fix (without it, deferring the full panel leaves the
  halt rule with no stable denominator). Correctly catches the 168-probe CUDA
  misattribution and the 0.9% completion-weighting. Weakness: its pinned-subset re-probe is
  a 35–40 min LONG run after *every* fix — the most expensive per-iteration grading
  mechanism of the five.
- **E — Expansionist.** Best strategy: promote the full panel to Phase B’s *first* act,
  pre-extraction, as the control arm (pre/post extraction pairing) + extraction spec,
  ledger carried across the dial via R-CSM3B-2 keying. Catches 39/60. Weakness: defers all
  probe cost to Phase B without quantifying it (5–10 h sweep + extraction + re-sweep
  competing for the same 100k session), and its change-of-mind (extraction de-scoped → A)
  would resurrect the plan-violating mid-phase switch.
- **A — First-principles.** Right reframe (“iteration 1 doesn’t need the 17,009-row
  sweep”), and the only documented-floor concept (structural reds are extraction-gated →
  declare a floor so the halt rule can’t false-fire). But its “verified facts” repeat the
  brief’s wrong 49/60 without re-deriving (its own cited reds — three classes summing to
  19 red — are inconsistent with 49/60’s 11 red), so its floor is scoped to three classes
  and the true 21-red census (incl. causality/appearance reds) is partly unowned in its plan.

## The three answers

1. **Strongest: C (Outsider).** Only response with the 150k device rule right (in-process
   CUDA one-copy, proven 52 s / Qwen alive), plus the two hard factual catches (17,381
   double-count; 39/60) and the minimal-switch placement of the exhaustive panel (one
   switch, not two–three). Caveat: its in-process 400-probe path is unverified.
2. **Biggest blind spot: A (First-principles).** Its spot-check parrots the brief’s wrong
   49/60 (raw census is 39/60, 21 red), so its documented floor (3 structural classes) +
   28-row queue leaves the causality/appearance reds unowned → false-halt risk under the
   two-no-reduction rule — exactly the wall-clock the campaign cannot afford.
3. **What all five missed:** (a) the **per-engine-change cost stack** that actually
   dominates Phase-1 wall-clock — all five red-list items are engine-class, so each fix =
   targeted re-sweep + four-gate re-run (one-copy ordering) + a council trigger if “big”;
   no one quantified that stack (gate re-runs + council overhead, not the 17,009-row
   sweep, is the burn). (b) No one verified the **in-process 400-probe driver** — the only
   probe mechanism that is both plan-compliant at 150k and cheap (~10 min vs 35–48 min
   LONG) — exists; it doesn’t (CLI is HTTP-only, census tools are the precedent). A ~50-line
   `tools/` driver (tooling, not engine — no council trigger) is iteration 1’s real first
   step.

## Recommended synthesis for the council

Execute **C (outsider’s variant)**, with four council rulings attached:

1. **Probe/gate mechanism at 150k = in-process CUDA one-copy** (`:8000` stopped, models
   loaded in-process per `CSM_WAVE2_RESUME.md` §2; proven by the 52 s census window). Rule
   it *before* iteration 1 starts so every 400-probe run and per-fix re-sweep takes ~10 min,
   no LONG flag, no plan violation. Precondition: build/extend the in-process 400-probe
   driver (~50 lines in `tools/`, reusing `eval.span_recall` verdict logic the way the
   census tools do) — no council trigger (tooling, not `scriptengine/`).
2. **Halt metric = B’s fixed 400-row subset, scoped to A’s documented floor** — and the
   floor is the *full 21-red census* (all five dimension classes, extraction-gated), not
   just the three structural classes; freeze the miss-queue inputs from the raw census file
   (21 reds), not the work_log summary.
3. **Exhaustive panel completion (17,181 pinned + 200 held-out on its own ledger) folds
   into the orchestrator’s existing `PHASE_A_COMPLETE` → 100k switch as Phase B’s
   first act, pre-extraction** (E’s control-arm argument; C/outsider’s single-switch
   placement). One switch total, plan-faithful.
4. **Budget the per-fix stack explicitly** (D’s “4 hours” is optimistic): 5 engine-class
   red-list items × [fix + targeted in-process re-sweep + four-gate re-run + council if
   big] ≈ 1.5–3 h of gate/council overhead alone, plus fix authoring. Sequence R-1..R-5 so
   the two no-reduction iterations are counted only over Phase-1-fixable classes (ruling 2),
   otherwise iteration 1 halts to council on extraction-gated reds it cannot close.

First executable step (under the synthesis): build the in-process 400-probe driver, run
the 400-probe gate + frozen 28-row queue + 21 census reds in one ~15-min one-copy window
(`:8000` CPU down/up around it), and write the pre-triaged miss queue — all at 150k, zero
switches.