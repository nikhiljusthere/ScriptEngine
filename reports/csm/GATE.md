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

**GREEN at the P1.4 four-gate copy** (P1.4 close, 2026-09-12, @`407c016`;
copy stamp commit `af382ee`). All four gates re-run green on CUDA (one-copy
100k dial): pytest **1,321** (1,316 passed + 3 known env-mcp trio failures
under a stopped :8000, 2 xpassed), eval jjk **31/31**, span-recall **48,572
rc=0 + 398/400 (99.5%)**, canon opm **236/236, 10/16 exact, 79.0%** (run dir
`reports/2026-09-11-2218/`). The env-mcp trio was live-proven 2/3 against a
running :8000 (the 1 failure is a **REAL pre-existing finding**: bare
character name "Maki Zenin" routes `qa` via `router.py:809-812`, mismatching
the test's narrative intent; the mismatch predates the test by a month —
deferred to P1.5, not a campaign regression; the gate-1 pin stays 1,321).
**5.4 re-adjudication (council R6):** 34 s one-copy census re-run (CUDA,
co-located with Qwen, 33 s, RC=0, Qwen alive) — 21/21 reds identical to the
09-09 run, **0 closed, 0 new regressions** => no de-scope; the 22-row
extraction-gated floor stands in full (21 `csm-dim-*` + `csm-char-04`), the
5.4 gate stays LIVE, P2.3 stays in scope. Raw receipts:
`reports/csm/receipts/census_5_4_readjudication_p14.md` (this run overwrote
`census_dimensions_csm_results.jsonl` in place; the 09-09 version is in git
at `af382ee`) + `reports/2026-09-11-2218/` (gate-4) +
`reports/span-recall/jjk/recall_verbatim.jsonl` (gate-3 live) +
`GATE_LEDGER.json` `p14_close_copy` + drift D24. **Bar-audit pre-registration
(close condition d):** `reports/csm/bar_audit_p14_preregistered.json` — 26
panel-line cases over the 6 D6 classes (3–5 each), 78/78 expect terms
verbatim-verified vs `series/csm/facts.db` (model-free, authoring subagent,
receipt `reports/csm/receipts/bar_audit_p14_author.md`).

Previous live state (R-7 @`81df799`, queue 35 open / 23 closed) stands in
`GATE_LEDGER.json` + drift D22; its receipts are unchanged.

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