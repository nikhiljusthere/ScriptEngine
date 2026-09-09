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

**GREEN at `5c8237a`** (P1.1, §9a iter-1 R-2 + R-3 closure, 2026-09-09).
All four gates green on CUDA against the live 100k dial; the R-2 Part-A
panel mini-sweep (7/13 HIT, csmd5 own-new 2/7) and R-3 Part-B re-sweep
(15/15) cleared; 12 miss-queue rows stamped closed (open 55 → 43, closed 3 →
15). Raw receipts: `reports/2026-09-09-2051/` (gate-4),
`reports/span-recall/jjk/recall_verbatim.jsonl` (gate-3 ledger),
`reports/span-recall/csm/sweep_qa_a4b1d02d.jsonl` (Part-A mini-sweep).

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