# Executor (adv_D) — CSM unit 3 sweep fork, 2026-09-09

C — and not as a compromise: at 150k it is the plan's own path. The sweep CLI is an
HTTP client against `:8000` (`reports/csm/CSM3B_PRESTEP.md` §6), and at 150k `:8000`
must stay CPU (headroom 5,381 MiB < 6,144 co-locate threshold, `work_log.md` boot
line). So "panel sweep on CUDA" is simply not doable at 150k without a switch — that
is the fork. But A's headline deliverable is structurally wasted: the 5.4 extraction
gate is LIVE (dimension census red — 21 red rows verified on disk; the "49/60
mech-green" in `work_log.md` and the question is a digit transposition, it is
39/60), so the Phase-2 extraction changes the corpus and CSM-4 re-sweeps the whole
panel at 100k anyway. A buys 5–10 h of *unmeasured* CUDA time producing stale
numbers, 3 switches instead of 1 (the orchestrator's `PHASE_A_COMPLETE` poll starts
the 100k switch right after phase close regardless), and a deviation from the plan's
switch reservation. B is worse: 17,009 rows at the CPU 168-probes/1200-s rate (the
"1200-s incident", `CSM3B_PRESTEP.md` §2) ≈ 33 h plus ~100 A-LONG flags, same stale
output.

What B does under C — 30 min: one bounded CPU `:8000` sweep segment (panel rows
173–472, ~35 min at the 168/1200-s rate, one A-LONG flag) while B writes the
pre-triaged miss-queue file from the frozen inputs (twenty-failures 20 rows [bank 8 /
door 5 / d5 7, verified], red list 5, 21 dimension-census reds, 3 narrative-door
misses, the sweep's own 7 MISS rows). 4 hours: the 400-probe gate (35–40 min CPU,
LONG flag) + serial fix closure over R-1..R-5 (per-wiki override first; engine
changes take the council trigger + four gates), each fix graded by a targeted
re-sweep of its class, not the full panel. Tomorrow: halt check, phase close (four
gates in-process CUDA one-copy at 150k — proven pattern, `work_log.md` census
window), `PHASE_A_COMPLETE` → the already-planned 100k switch → CSM-4 completes the
panel at 100k on the post-extraction corpus, where the numbers will actually be
true. C's miss queue is well-specified without the 17,009 rows: every frozen input is
a named class with a fix locus (the red list even says which file). The full panel
adds breadth only after the known classes are closed — and CSM-4 is that closure.

OPTION: C / FIRST STEP: launch the bounded CPU sweep `span-recall --series csm --panel reports/csm/panel_csm.json --door qa --sanity 472` (rows 173–472, ~35 min, one A-LONG flag) and, in the same window, write the pre-triaged miss-queue file from the five frozen sources / CHANGE-OF-MIND IF: the gate + frozen-input miss queue comes back thin/empty (twenty-failures all HIT, gate green, no red class left to close) — then the sweep itself is the work and A (switch now, capture the pre-extraction full-panel baseline so CSM-4 can measure the extraction delta) wins; also if A refuses the bounded CPU gate run or CPU `:8000` is unhealthy.

## Verified on disk (spot-checks)

- `reports/csm/panel_csm.json`: 17,181 sweep rows + 200 held-out, seed 42 (python count).
- `reports/span-recall/csm/sweep_qa_e3d73720.jsonl`: 172 rows (165 HIT / 4 MISS_SPAN / 3 MISS_DOC), hash `e3d73720…`, 17,009 remain; no roster/narrative door ledgers exist yet.
- `census_dimensions_csm_results.jsonl`: **39/60** MECH_GREEN, 21 red (arcn 2/10, abl 4/10, state 5/10, appr 1/10 red, caus 1/10 red) — the "49/60" in `work_log.md` L55 is a typo (its own per-class greens sum to 39).
- `census_doors_results_csm.jsonl`: roster 11/11, narrative 97/100 (3 arc misses).
- `twenty_failures_csm.md`: 20 rows = bank 8 / door 5 / d5 7 (3 MISS_DOC + 4 MISS_SPAN).
- `red_list_csm.md`: 5 mechanical entries R-1..R-5, each with fix class + file.
- `work_log.md`: 150k free 5,381 MiB → `:8000` CPU service; census one-copy CUDA window 34 s + 18 s, Qwen alive.