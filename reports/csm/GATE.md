# CSM gate — the four standing gates, live state

The CSM campaign (Phase 1, §9a closure loop) runs the **same four standing
gates** the JJK campaign uses, because every CSM engine change must not
regress the JJK baseline (JJK stays at 100%). Nothing here is graded — the
gates are mechanical (counts, string/foreign-key equality); they report, they
do not judge.

The four gates (re-run after every fix-class, before calling it done):

1. **gate-1 — `pytest tests/ -q`** (in-process, CUDA): the full suite green.
   Current pin **1,321** (1,318 R-6 pin + 3 new R-7 tests; the only failures
   are the known env-mcp trio under a stopped :8000, 2 xpassed).
2. **gate-2 — `eval --series jjk`**: **31/31 (100%)** gold.
3. **gate-3 — `span-recall --series jjk`**: **48,572/48,572 offline (rc=0)**
   + a 400-probe (seed-rotated; the live window must clear the 390/400 =
   97.5% bar).
4. **gate-4 — `canon-run --series opm --skip-eval`** (one-copy rule):
   **236/236 canon (100%)**, 79.0% closed-set precision, 0 confident-wrong.

## Live state

**GREEN at the R-7 identity_fields pass** (P1.2, §9a iter-1 R-7 closure,
2026-09-12, @`81df799`). All four gates green on CUDA (one-copy 100k dial):
pytest **1,321** (1,318 R-6 pin + 3 new R-7 tests; the only failures are the
known env-mcp trio under a stopped :8000, 2 xpassed), eval jjk **31/31**,
span-recall **48,572 rc=0 + 398/400 (99.5%)**, canon opm **236/236, 10/16
exact, 79.0%**. R-7 class close re-sweep (council SHIP-AMENDED, A1–A7):
`csm-char-04` confirmed as the **22nd extraction-gated floor row** (stays
open; Phase-2 extraction track / 5.4 re-adjudication); `r1blast-tokyo`
live re-probed (qa→roster, 5/5 divisions, 0 new misses);
`r1blast-blizzard`/`r1blast-marines` held by gate-4 baseline-identity (direct
re-probes skipped by council — no onepiece standing gate; the R-7 hunk is
CSM-scoped). Queue unchanged: open 35 / closed 23 / total 58
(rows_closed_this_unit 0, by design). Raw receipts:
`reports/csm/receipts/r7_gate_window.md` + `r7_class_resweep.md` +
`r7_council/{advisors,chairman}.md` + `reports/2026-09-11-2135/REPORT.md`
(gate-4); commit hashes in `reports/master-work/work_log.md` (2026-09-12 gate
line).

**Machine-readable ledger-of-record v1:** `reports/csm/GATE_LEDGER.json` —
read it *first* after a reboot; if `HEAD == last_green.commit` the four gates
stand, do not re-run them.

## The halt rule

Phase 1 halts at the **extraction-gated floor**: the `D6-extraction` class
(21 rows, closed only by the Phase-2 extraction campaign) **plus
`csm-char-04`** — the 8th Makima-ability row, confirmed 22nd floor row by the
R-7 close re-sweep (its close lever is the Phase-2 extraction track / 5.4
re-adjudication) — and the invariant floor rows: the roster floor
`csmdoor-01` 31/88, the D5 reachability residuals
(`csmd5-01/02/03/05/06`, `gate400-320`, `red-R-4`) and the closed-class
curation residuals (`csm-char-03`, `csm-set-02`) — the ten stamped by-design
open, governing stamps in the red-list R-2/R-3 close notes. When every
non-floor, non-extraction fix-class is green and the queue's remaining open
rows are all extraction/floor (halt residual 35 = 22 floor + 10 residual +
3 `r1blast-*` stamps), B writes
`reports/csm/PHASE_A_COMPLETE_AT_FLOOR.md` and stops.