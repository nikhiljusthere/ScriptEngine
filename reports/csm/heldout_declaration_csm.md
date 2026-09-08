# CSM held-out probe sets — formal declaration (plan §5.5.2)

**Declared: 2026-09-09.** Plan §5.5: the executing agent must never grade its own
authoring. The strongest fix is *generator-sliced gold* (§5.5.1, landed as
`tools/csm/slice_gold.py` → `reports/csm/gold_sliced_csm.json`); the next is a
**held-out probe set authored by a party that is NOT the executing agent, which
that agent runs but may never edit. A failure there is a finding, never an
authoring defect.** This file declares those sets.

The no-edit rule is git-blame checkable: a §9a executor consumes these sets and
flips a row's status in *its own* triage file, never here. If `git blame` on a
set file shows the executor (or any non-author) touched the question text, the
set is compromised and the run is void.

---

## H-1 · D4 open-50 set

- **File.** `reports/csm/d4_open50_csm.json` (50 items, ids `Q01`–`Q50`).
- **Named author.** `fresh-context subagent "d4-open50-author" (worker, CSM
  Wave-2 wave A, 2026-09-09); frozen by the orchestrator's unit-1 commit; the
  executor runs it, never edits it` — recorded in the file's `meta.author`.
- **Provenance (verified on disk, 2026-09-09).** Valid JSON; `meta.seed = 20260909`;
  `meta.revid_fetched = 2026-09-09`; `meta.source_pages` = 54; 50 items, ids
  `Q01`–`Q50`; zero duplication of the 39-question seed bank (scan 2026-09-09).
  Grounded in CSM's own sections/rosters (JJK `census_3c_open_50.json` consulted
  for file shape only — no JJK question copied).
- **How the executor runs it.** The §9a closure-loop sweep probes each `Q` against
  the current index (the qa door for the open story-questions). The sweep is run
  by the orchestrator, **never by the authoring agent**. A miss is a finding.
- **Gold mode.** All 50 are open-ended (no structured answer) → `gold_mode = prose`
  in `reports/csm/gold_sliced_csm.json` (no verbatim span fabricated).

## H-2 · Twenty-failures frozen acceptance set

- **File.** `reports/csm/twenty_failures_csm.md` (20 rows, all `status = open`).
- **Named author.** `fresh-context subagent "twenty-failures-author" (worker, CSM
  Wave-2 wave A, 2026-09-09); the executor runs it, never edits it
  (git-blame checkable)` — recorded in the file's header.
- **Provenance (verified on disk, 2026-09-09).** 20 data rows; gate breakdown
  bank = 8 (`csm-set-14/15`, `csm-fact-06`, `csm-char-04`, `csm-set-17`,
  `csm-char-03`, `csm-set-02`, `csm-set-01`), door = 5 (`csm-rel-05/08/09/02`,
  `csmdoor-01`), d5 = 7 (`csmd5-01..07`); no `d6` rows (no CSM
  comprehension-layer receipt exists yet — the events build is JJK-only; recorded
  as a receipt gap, not a shortfall — the set is exactly twenty, nothing padded).
  Every row cites an on-disk receipt from the 2026-09-08 cycle and the store
  facts were re-verified read-only on 2026-09-09.
- **How the executor runs it.** The §9a miss queue *pre-triages* "twenty-failures
  hits": a row that fires in the sweep is consumed by the serial engine-fix
  closure (one class per fix). A hit **flips the row's status in the executor's
  triage file, not here** — this file is frozen. The `fix / reason` column carries
  the correct output; the executor never rewords a row to pass.

---

### The no-edit rule (both sets)

1. The authoring party is a **fresh-context subagent** (no shared context with the
   executor) — the held-out sets were never visible to the agent that will run them.
2. The executor (the §9a closure loop) **runs** these sets and **never edits** them.
3. A hit is recorded in the executor's triage file; the frozen set's status column
   is touched only by its named author (or the orchestrator's commit of that author's
   output). `git blame` is the check.
4. A compromised set (non-author edit) voids the run and is a council item (§3).