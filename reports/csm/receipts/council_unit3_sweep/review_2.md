# Peer Review 2 — CSM Unit-3 sweep fork (council 2026-09-09)

Reviewer weighting: **the council is measuring the wrong thing / the miss queue is under-specified.**
Fresh-context subagent; zero-GPU, read-only; every shell < 15 s.

**Response-file mapping (caveat).** The task pointed at `adv_A.md`…`adv_E.md`; those do not
exist in `reports/csm/receipts/council_unit3_sweep/`. The five responses carry persona
filenames. Mapping used (deployment order by mtime + the executor's self-label "adv_D",
same as review_1): A=`adv_first-principles` · B=`adv_contrarian` · C=`adv_outsider` ·
D=`adv_executor` · E=`adv_expansionist`.

**Verified on disk (claims the responses lean on).**
- `reports/csm/census_dimensions_csm_results.jsonl` (raw receipt, mtime 09-09 03:39):
  **39/60 MECH_GREEN / 21 MECH_RED** — per-class reds: arc-narrative 8, abilities 6,
  state-over-time 5, causality 1, appearance 1. `work_log.md` L55's "49/60" headline is
  a digit error (its own per-class greens sum to 39); the brief's fact 2 and A repeated
  it. (census tool was fixed mid-window per work_log L55; the raw file is the on-disk receipt.)
- `reports/csm/panel_csm.json`: 17,181 sweep + 200 held-out, seed 42 — option C's
  "17,381-row panel" double-counts the held-out (C caught this).
- `reports/span-recall/csm/sweep_qa_e3d73720.jsonl`: 172 rows (165 HIT / 4 MISS_SPAN /
  3 MISS_DOC); 17,009 remain.
- `reports/csm/CSM3B_PRESTEP.md` §3: the 168-probe datapoint ran on **CUDA** `:8000`
  (pid 103425, device=cuda), one bounded run; the 168 *CPU* rows were the dropped
  "1200-s incident" sidecar (~7.1 s/probe) — so the brief's fact 3 "CPU ~= 168 probes
  per bounded run" is misattributed (B caught it; D's CPU estimate uses the 1200-s rate).
  §3's "0.9%" = 161/17,181 completion-weighted, not per-probe (per-probe miss ≈ 7/168 ≈ 4%).
- `reports/csm/red_list_csm.md` L88: R-1..R-5 all **engine-class** (R-4 prefers a
  per-wiki override first attempt; all trigger §3 council + four-gate re-run).
- `reports/master-work/CSM_WAVE2_JOB.md` unit 3: queue = "(MISS_DOC / MISS_SPAN / gate
  violation / twenty-failures hit)"; halt = "miss-count regression or two no-reduction
  iterations → council".
- `scriptengine/eval/span_recall.py`: HTTP-only (urllib → 127.0.0.1:8000); no in-process
  400-probe driver exists (also flagged in review_1).
- `plan/CSM_2PHASE_PLAN.md` L8–14: at 150k "no CPU shell command may exceed 15 s —
  anything that would (…probe…) runs on GPU"; the switching plan is "NOT used in Phase 1".

## Answers

1. **Strongest: B (contrarian).** Only response fixing the meter: it pins the halt
   metric to a fixed 400-row grading subset (without which the halt rule has no
   denominator), and the only one to re-derive rates from disk — the 168-probe point
   is CUDA not CPU; "0.9%" is completion-weighted, not per-probe.

2. **Biggest blind spot: A (first-principles).** It claims spot-checks but parrots the
   brief's wrong 49/60 — the raw census is 39/60 with 21 reds (arc 8, abilities 6,
   state 5, causality 1, appearance 1). Its floor + 28-row queue leaves causality/appearance
   reds unowned — false-halt risk.

3. **What all five missed:** (a) Two unconnected meters: the halt's "miss count"
   is undefined once the panel is deferred, and B's 400-subset is a 2.3% sample
   (~2 rows per 100-row class): a fix that closes its class on a targeted sweep can
   still "no-reduce" on the subset meter — halt on the wrong meter. (b) No triage
   schema: the queue taxonomy (MISS_DOC/MISS_SPAN/gate/twenty-failures) is miss
   *type*, not fix *class*; no row→class mapping (R-1..R-5 or new R-6+) is
   pre-registered for the ~16 new gate misses, nor a per-class ruling (floor vs
   Phase-1-fixable) for the 21 census reds.

## Note to the chairman

The per-fix cost stack (5 engine-class red-list items × [four-gate re-run + council if
big]) — not the 17k-row sweep — is the real Phase-1 wall-clock driver (also flagged in
review_1); no response budgets it. Any synthesis keeping B's 400-row halt pin must add:
the row→class triage schema, a per-class floor/fixable ruling over all 21 census reds,
and a rule connecting the halt meter to the per-fix class sweeps (a class is "closed"
only when its own targeted sweep turns green; the halt count is judged over that union,
not the random 400-subset alone).