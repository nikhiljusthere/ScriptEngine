# D6 OOS/green freeze register (pre-model-call)

Frozen before the D6 GPU window's first model call. Re-grade set = 69 p23 reds
(whole-bank re-grade) + the 30 green rows below + the 200 OOS rows below.

## Rule
- Seed: 20260918 (one `random.Random` instance; per-class green draws in sorted
  class order first, then the OOS draw over the remaining pool, all over
  id-sorted candidates)
- Population: 486 widened-result rows (`reports/csm/census_widened_csm_results.jsonl`)
- Draws are over the WHOLE population (chair lock): no leak exclusion. The 72-page
  window plan (`reports/csm/D6_DRYRUN_PLAN_WINDOW.txt`, alnum-normalized compare)
  does not shrink the pool; window-page rows are flagged `"in_window"` so the
  post analysis can slice window vs non-window. Rationale: the closure test is a
  score floor (post >= pre - 2, a drop of 3+ voids), so a window row that the
  extraction improves can only rise, never trip the floor; and a green row on a
  window page is the stricter check (the fix must not regress it).
- green30: 5 MECH_GREEN rows per dim class, classes = the six with
  >=5 greens in the population: ability-pool, appearance, causality, organization, personality, state-over-time
- oos200: 200 rows drawn from (population - green30), mixed verdicts
- Disjointness: green30 ∩ oos200 = ∅ (asserted at build)

## Counts
- green30: 30 -- per class: {"ability-pool": 5, "appearance": 5, "causality": 5, "organization": 5, "personality": 5, "state-over-time": 5}; in_window: 5
- oos200: 200 -- verdict mix: {"MECH_GREEN": 168, "MECH_RED": 32}; in_window: 69
- oos200 pool size after green30 removal: 456

## Deviations
- none (every dim class had >=5 greens)

## Pre-scoring method (recorded for the pre-baseline)
POST http://127.0.0.1:8000/context {series: "csm", query: <q>, mode: "qa"}
(P2.3 shape: no subject, endpoint-default budget/top_k) with `:8000` up;
verdict = `tools/census_dimensions.judge` over `scriptengine.eval.span_recall.served_text`
of the returned bundle -- identical to `tools/csm/p23_grader.py`'s in-process
grade minus the in-process model load, so `:8000` stays the single model holder.

## Green30 ids
- csm-abl-pool-026
- csm-abl-pool-079
- csm-abl-pool-160
- csm-abl-pool-316
- csm-abl-pool-322
- csm-dim-appr-03
- csm-dim-appr-07
- csm-dim-appr-08
- csm-dim-appr-09
- csm-dim-appr-10
- csm-dim-caus-01
- csm-dim-caus-04
- csm-dim-caus-07
- csm-dim-caus-08
- csm-dim-caus-09
- csm-dim-org-01
- csm-dim-org-02
- csm-dim-org-07
- csm-dim-org-09
- csm-dim-org-10
- csm-dim-pers-01
- csm-dim-pers-02
- csm-dim-pers-04
- csm-dim-pers-06
- csm-dim-pers-07
- csm-dim-state-04
- csm-dim-state-05
- csm-dim-state-06
- csm-dim-state-07
- csm-dim-state-10
