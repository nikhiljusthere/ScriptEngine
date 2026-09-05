# Phase 0 peer-review pack

You are one of five independent peer reviewers for the **Plan to Perfection,
Phase 0** council. Phase 0 makes `facts.db` rebuild-safe: a guard
(`require_rebuild`) refuses a non-forced rebuild while the derived model layers
(`events`, `meaning`) are non-empty; a forced rebuild snapshots those rows,
drops and repopulates the base tables, and re-keys the rows onto the new graph
(`remap_derived`) instead of wiping them.

A prior 5-advisor council (anonymized below as A–D) found **four defects**.
All four are now claimed fixed. Your job: **independently verify each defect
is actually closed by the code**, and look for defects the advisors missed.
Do not take the fix author's word for anything: read the code.

## The four advisor defect claims

**D1 — content-blind remap (advisor: HALT, the strongest).**
`remap_derived` re-keyed each derived row onto the *new* section/node ids
resolved from its durable key (doc_title, section_ordinal / participant
names). On a same-`revid` rebuild whose content was re-parsed (a parser fix
moves a section, or an ordinal shift lands the row on a different section),
the row was silently resurrected on whatever section it now resolves to, with
no check that the section's text still proves the row. The advisor: a
content-validated remap is the real fix; without it a forced rebuild can
misattribute a 24,000-row extraction.

**D2 — the crash window.**
`reset()` took its row snapshot *in memory* and handed it to `remap_derived`.
A process death between the drop and the remap left the derived tables gone
and the rows unrecoverable; the next run found the layers empty, passed the
guard, and a full wipe was the outcome of the crash. The advisor: the snapshot
must survive the crash, i.e. be persisted to disk.

**D3 — the backfill NULL.**
`ensure_events` (the one-time FK-migration backfill) filled the new durable
columns with bare scalar subqueries (`SELECT d.title ...`, `SELECT s.ordinal
...`). When a section or its document was missing, the subquery yields NULL
and the INSERT violates the NOT NULL columns, so the backfill — and with it
the guard that depends on a healthy store — could not run. The advisor:
COALESCE the subqueries.

**D4 — untested destructive branches.**
The original tests covered only the happy-path remap. The destructive branches
— stale (`revid` changed), orphaned (section/node gone), and the crash
recovery — had no tests at all. The advisor: a guard whose refusal and
recovery paths are untested is not a guard.

## Where the fixes live (all uncommitted, branch `character-scoped-questions`)

Full diff: `/tmp/phase0_final_diff.txt` (1,436 lines).
New file: `scriptengine/ingest/verbatim.py` (in `/tmp/phase0_new_files.txt`):
`fold()` (NFKD + lowercase) and `quoted_in(quote, passage)` (>=12-char
quotes, whitespace-collapsed, diacritic-folded containment).

- **D1** → `scriptengine/stores/facts.py:334` `remap_derived`: now loads each
  section's text and drops, per table, an `unverified` branch — `events` rows
  fail `quoted_in(row["quote"], section_text)`; `meaning` rows fail a
  `content_hash` membership check against the re-split section
  (`scriptengine/index/chunker.py` gained `sentence_content_hash`, sha256 of
  the stripped sentence). Rows with an empty/NULL quote or hash are dropped
  as unverified. Remap reports add an `unverified` count.
- **D2** → `scriptengine/stores/facts.py:202` `reset()` now returns the
  snapshot **and** (only when non-empty) writes it to
  `<facts.db>.reset-snapshot` **before** dropping the tables
  (`_write_snapshot_file`, facts.py:279). `remap_derived(snapshot=None)`
  (facts.py:334) falls back to reading that file
  (`_read_snapshot_file`, facts.py:284) and deletes it only after a
  successful remap (`_drop_snapshot_file`, facts.py:298). A re-run after a
  crash finds the layers empty, passes the guard, and recovers from the file.
- **D3** → `scriptengine/stores/facts.py:1379` `ensure_events` backfill now
  uses `COALESCE((SELECT ...), '')` / `COALESCE((SELECT ...), 0)`.
- **D4** → `tests/test_stores.py`: 10 new tests — events:
  `test_remap_drops_a_row_its_document_revid_changed` (:520),
  `test_remap_drops_a_row_whose_section_vanished` (:541),
  `test_remap_drops_a_row_its_section_no_longer_says_it` (:568),
  `test_remap_drops_a_row_with_no_quote` (:593),
  `test_a_crashed_rebuild_recovers_the_rows_from_the_snapshot_file` (:612);
  meaning (new `TestMeaningRemap` class): `test_a_forced_rebuild_remaps_a_meaning_row`
  (:679), `test_remap_drops_a_meaning_row_its_document_revid_changed` (:702),
  `test_remap_drops_a_meaning_row_whose_section_vanished` (:717),
  `test_remap_drops_a_meaning_row_its_sentence_moved` (:734),
  `test_remap_rekeys_a_meaning_rows_sentence_ordinal` (:752).
- Supporting: `scriptengine/ingest/events.py` and `relations.py` now import
  the shared `quoted_in`/`fold` from `verbatim.py` (duplicate local copies
  removed); `schema.sql` comments document the three drop branches + crash
  file; `index/build.py` passes the `reset()` snapshot into `remap_derived`;
  `cli.py` exposes `--force` and catches `ResetRefusedError`.

## Evidence the fix author has

- Full suite: **1,216 passed** (baseline before Phase 0: 1,206).
- Live-store dry run: all **2,748/2,748** event rows pass the verbatim
  predicate against their own section text (`total=2748 failed=0`) — a
  content-validated remap loses zero live rows on an unchanged build.
- Gate 0D re-run on copies of the live store (`/tmp/gate_phase0_demos.py`):
  1. guard fired (`ResetRefusedError`, 2,748 rows);
  2. forced rebuild: `{before: 2748, remapped: 2748, stale: 0, orphaned: 0,
     unverified: 0}`;
  3. unverified branch: a section's text replaced under its 32 rows → exactly
     those 32 dropped as `unverified`; 24 rows in a text-*appended* section
     (quote intact) survived — `{remapped: 2716, unverified: 32}`;
  4. crash recovery: build died after `reset`, 2,748 rows written to the
     snapshot file; re-run recovered all 2,748 from the file and deleted it.
- `span-recall --series jjk`: 48,572/48,572 sentences reachable (100%).

## Known, documented limitation (verify it is really true)

Every JJK document has `revid = 0` in the source crawl; the `isdigit` guard
in `save_events` maps that to NULL, so **all 2,748 event rows carry a NULL
`revid`** — the `stale` branch is structurally dead on JJK, and the
`unverified` content check is the only live defence there. NULL-`revid` rows
are deliberately kept (dropping them would wipe the whole live layer on the
first forced rebuild). The `meaning` table is not yet populated (0 rows), so
its branch is tested synthetically only.

## Your task

1. For each of D1–D4: **CLOSED / PARTIAL / OPEN**, with file:line evidence.
2. New defects the advisors missed (if any), same standard: only real,
   reachable problems count — cite the code path.
3. Final verdict: **SHIP / SHIP-WITH-FIXES / HOLD**.

Be strict but fair: this is a guard around a 24,000-row extraction pass, and
the bar is "no silent loss of rows", not perfection.