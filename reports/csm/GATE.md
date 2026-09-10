# CSM gate — the four standing gates, live state

The CSM campaign (Phase 1, §9a closure loop) runs the **same four standing
gates** the JJK campaign uses, because every CSM engine change must not
regress the JJK baseline (JJK stays at 100%). Nothing here is graded — the
gates are mechanical (counts, string/foreign-key equality); they report, they
do not judge.

The four gates (re-run after every fix-class, before calling it done):

1. **gate-1 — `pytest tests/ -q`** (in-process, CUDA): the full suite green.
   Current pin **1,305** (1,303 baseline + 2 new R-2/R-3 tests, council #23).
2. **gate-2 — `eval --series jjk`**: **31/31 (100%)** gold.
3. **gate-3 — `span-recall --series jjk`**: **48,572/48,572 offline (rc=0)**
   + a 400-probe (seed-rotated; the live window must clear the 390/400 =
   97.5% bar).
4. **gate-4 — `canon-run --series opm --skip-eval`** (one-copy rule):
   **236/236 canon (100%)**, 79.0% closed-set precision, 0 confident-wrong.

## Live state

**GREEN at the R-6 subject_aliases pass** (P1.2, §9a iter-1 R-6 closure,
2026-09-10). All four gates green on CUDA (one-copy 100k dial): pytest
**1,318 collected** (1,315 R-5 pin + 3 new R-6 tests; the only failures are
the known env-mcp trio under a stopped :8000), eval jjk **31/31**, span-recall
**48,572 rc=0 + 398/400 (99.5%)**, canon opm **236/236, 10/16 exact, 79.0%**.
Queue `door-nar-None` ×3 closed (open 35 / closed 23 / total 58).
Raw receipts: `reports/csm/receipts/r6_subject_aliases_run.md` +
`reports/2026-09-10-0820/REPORT.md` (gate-4); commit hashes in
`reports/master-work/work_log.md` (2026-09-10 gate line).

**Machine-readable ledger-of-record v1:** `reports/csm/GATE_LEDGER.json` —
read it *first* after a reboot; if `HEAD == last_green.commit` the four gates
stand, do not re-run them.

## The halt rule

Phase 1 halts at the **extraction-gated floor**: the `D6-extraction` class
(21 rows, closed only by the Phase-2 extraction campaign) plus the invariant
floor rows (the roster floor `csmdoor-01` 31/88, and the D5 reachability
residuals that need a new chunking/coverage pass, not a retrieval fix). When
every non-floor, non-extraction fix-class is green and the queue's remaining
open rows are all extraction/floor, B writes
`reports/csm/PHASE_A_COMPLETE_AT_FLOOR.md` and stops.