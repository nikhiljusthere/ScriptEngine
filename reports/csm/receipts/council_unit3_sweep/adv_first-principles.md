# First Principles — CSM unit 3 sweep device-path (2026-09-09)

Wrong question. "Which device do we run the 17,009-row sweep on" presupposes iteration 1
needs that sweep. It doesn't.

Iteration 1 must produce a well-specified miss queue for serial fixes and a graded
re-sweep. The actionable inputs are already frozen on disk: twenty-failures (20 rows),
red list (5 entries), 3 narrative-door misses (Introduction / Bomb Girl / International
Assassins), and the 3 structural-dimension red classes. ~30 rows, and they already name
fix classes (router count rule, qa-passage leg, roster shortfall, section intruder,
relations routing). A 17,009-row sweep adds a denominator, not a fix class.

And the denominator would be stale: the 5.4 extraction gate is LIVE (work_log.md 03:43;
events/meaning tables = 0 rows, extraction scheduled). A full-panel sweep now measures a
state the extraction will change. R-CSM3B-2's ledger keying is provenance, not a
deadline — the 172-row ledger is intact; the remaining rows accumulate in Phase B, where
CSM-4 tier-1 lands at 100k anyway (the orchestrator's own PHASE_A_COMPLETE → 100k
switch plan).

A dies twice: plan fidelity (CSM_2PHASE_PLAN: the switching plan is "reserved for
Phase 2 … NOT used in Phase 1") and staleness — 5–10 h of CUDA for an artifact we'll
invalidate. B is 26+ h for the same artifact.

Pick **C**, with one correction: stay at 150k on CPU :8000 (measured 5,381 MiB <
6 GiB: CUDA :8000 needs a switch, which Phase 1 forbids). (1) Baseline 400-probe
standing gate, bounded ~35–40 min (A LONG-flag). (2) Execute the frozen ~28-row miss
set as the pre-triaged queue. (3) Targeted ~50-row re-sweep per serial fix, each within
the 15-min cap. (4) Declare the 3 structural-dimension reds a **Phase-1 documented
floor** — they are extraction-gated (5.4 LIVE), so no Phase-1 serial fix closes them;
the plan's own Phase-1 done-criterion is "no-reduction halt or a documented floor".
(5) Exhaustive panel completion = Phase B, post-extraction, 100k.

Facts spot-checked: panel_csm.json (17,181+200, hash e3d73720…, seed 42);
sweep_qa_e3d73720.jsonl (172 rows); census_dimensions_csm_results.jsonl (49/60 green;
reds arc-narrative 2/10, state-over-time 5/10, abilities 4/10); census_doors
(roster 11/11, narrative 97/100, 3 named misses); door_precheck_csm.md (5.4 gate
condition); work_log.md (5,381 MiB headroom; :8000 CPU; census one-copy window;
"5.4 extraction gate LIVE").

OPTION: C (variant: C-deferred-panel — 400-probe gate + frozen 28-row miss set + per-fix re-sweeps in Phase 1 at 150k/CPU; structural reds declared a documented floor; exhaustive 17,009-row panel deferred to Phase B post-extraction at 100k)
FIRST STEP: Run the baseline 400-probe standing gate on CPU :8000 (bounded ~35–40 min, A LONG-flag), then execute the frozen 28-row miss set (twenty-failures 20 + red-list 5 + 3 narrative reds) to build iteration-1's pre-triaged queue
CHANGE-OF-MIND IF: (a) the 5.4 gate flips green on a census re-run — no extraction planned, so a pre-extraction full panel is no longer stale, and bounded CPU runs (B) become the plan-faithful path to completing the panel in Phase 1; or (b) the Phase-B 100k switch / CSM-4 is cancelled — the panel must then complete in Phase 1, and A (mid-phase 100k switch) becomes the cost-minimal choice