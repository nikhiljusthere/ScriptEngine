# COUNCIL — Phase 0: make `facts.db` rebuild-safe (0A/0B/0C/0D)

Date 2026-09-05. The phase from `plan/flow.md` §"Phase 0": 0A the three
pre-commit fixes to the `meaning` DDL; 0B the reset guard; 0C the durable key
(key `events`/`meaning` on `document.title` + section ordinal (+ sentence
ordinal + content hash) and remap on rebuild, instead of a wipe); 0D the gate.
The open question the phase answers: *does a rebuild preserve the derived
model layers, and if a build crashes mid-rebuild, is anything lost?*

Method: 5 advisors (independent) → anonymized defect list → the fixes → 5 peer
reviewers (independent, each weighted to a failure mode: line-level
correctness / edge cases / conventions / test sufficiency / operational
safety) → this synthesis. Protocol per the `llm-council` skill (parallel
batches of 5); every load-bearing claim re-verified against code +
`series/jjk/facts.db` + gate output before recording. The anonymized defect
claims are on disk at `PEER_REVIEW_PACK_phase0.md`; the gate output at
`/tmp/gate_phase0_demos.py` (run on copies of the live store, never the live
store).

## The step under review (0D gate output)

- **The diff** (`/tmp/phase0_final_diff.txt`, 1,436 lines over 7 files +
  `scriptengine/ingest/verbatim.py`, 41 lines, new): 0A in
  `stores/schema.sql` (the frozen `class` CHECK, the `is_event`-is-derived
  CHECK, the "unverified, not atemporal" comment); 0B in
  `stores/facts.py:require_rebuild` (+ `ResetRefusedError`) and
  `index/build.py` (refuses a non-forced rebuild while `events`/`meaning` are
  non-empty, `--force` passes); 0C in `remap_derived` (durable-key re-key) +
  `schema.sql` (durable columns) + `events.py`/`relations.py` (shared
  `verbatim.py` predicate: `fold`, `quoted_in`); 0D evidence below.
- **The guard**: `require_rebuild()` on a non-empty store raises
  `ResetRefusedError` naming the row counts; `cli index` catches it and says
  what `--force` would do.
- **The rebuild**: a forced rebuild with the base graph renumbered re-keys
  every surviving row onto its new ids; the report carries per-table
  `remapped / stale / orphaned / unverified` counts.

## Round 1 — the five advisors: four defects

**D1 — content-blind remap (the strongest position; the advisor recommended
HALT).** The first `remap_derived` re-keyed each row onto the *new*
section/node id its durable key resolved to, with no check that the resolved
section's text still *proves* the row. On a same-`revid` rebuild whose
content was re-parsed (a parser fix moves a section; an ordinal shift lands
the row on a different section), the row was silently resurrected on text
that may no longer say it — a forced rebuild could misattribute a 24,000-row
extraction. *Fix:* the remap now loads each target section's text and drops,
per table, an **`unverified`** branch: `events` rows fail `quoted_in(quote,
section_text)`; `meaning` rows fail membership of their stored
`content_hash` in the re-split section's `sentence_content_hash` set
(`index/chunker.py` gained that hash, sha256 of the stripped sentence).
Empty/NULL quotes and hashes drop as unverified. A section that never changed
passes both checks untouched.

**D2 — the crash window.** The first `reset()` took its row snapshot in memory
and handed it to `remap_derived`; a process death between the drop and the
remap left the derived tables gone and the rows unrecoverable — the next run
found the layers empty, passed the guard, and the crash's outcome was a full
wipe. *Fix:* `reset()` writes the snapshot (only when non-empty) to
`<facts.db>.reset-snapshot` **before** dropping the tables
(`_write_snapshot_file`); `remap_derived(snapshot=None)` reads that file
(`_read_snapshot_file`) and deletes it only after a successful remap
(`_drop_snapshot_file`). A re-run after a crash finds the layers empty,
passes the guard, and recovers from the file.

**D3 — the backfill NULL.** `ensure_events` (the one-time FK-migration
backfill) filled the new durable columns with bare scalar subqueries; a
missing section or document yields NULL and violates the NOT NULL columns, so
the backfill — and the guard that depends on a healthy store — could not run.
*Fix:* `COALESCE((SELECT …), '')` / `COALESCE((SELECT …), 0)`.

**D4 — untested destructive branches.** The original tests covered only the
happy-path remap; stale (`revid` changed), orphaned (section/node gone),
unverified (section no longer says it), no-quote, and crash-recovery had no
tests. *Fix:* 10 new tests in `tests/test_stores.py` (five per table; the
`meaning` ones in a new `TestMeaningRemap` class).

## Round 2 — the five peer reviewers

Verdicts: **SHIP-WITH-FIXES ×3** (correctness, edge cases, operational
safety), **SHIP ×2** (conventions, test sufficiency). All four advisor
defects judged **CLOSED 5/5**. Three new defects, two of them reproduced
against the code before being accepted:

**F1 — the clobber (reproduced, operational-safety reviewer).** With the
original *two-commit* remap (events committed, then meaning), a crash between
the two commits left a half-remapped store; the re-run's `reset()` then wrote
a non-empty in-memory snapshot `{events: N, meaning: 0}` and **overwrote the
crash file**, silently destroying the un-remapped `meaning` rows (the remap
report then lacked a `meaning` key). *Fix:* the remap is now **one commit,
all or nothing**, after both tables' `executemany`. Crash *before* the
commit: both tables rolled back, the file is intact, the store is empty,
`reset()`'s "an empty snapshot never overwrites the file" guard (facts.py:245-251)
leaves the recovery copy in place. Crash *after* the commit: the re-run's
snapshot is complete (the fully remapped rows), so the overwrite is safe and
the re-remap is idempotent. Demo 5 (below) covers the after-commit window
explicitly.

**F2 — the invisible drop (both the correctness and the operational-safety
reviewers).** `unverified` drops were computed in the remap report but
invisible at the surface: `cli.py` counted only stale+orphaned into its
`lost` line, fired its yellow print only on those, and `--force`'s help (and
`build.py`'s docstring) still said "only stale/orphaned rows are dropped" —
false since D1. *Fix:* the CLI now counts `unverified` in the drop total and
the print, the help and docstrings say "stale, orphaned or unverified rows
are dropped, each counted and reported", and `remap_derived` logs a
`logger.warning` naming the per-table counts when any row drops unverified.

**F3 — the duplicate-sentence collapse (reproduced, edge-cases reviewer).**
Two identical sentences in one section give two `meaning` rows the same
`content_hash`; the first re-key (`hashes.index(hash)`) sent both to the
first occurrence, and `INSERT OR REPLACE` on the `(section_id,
sentence_ordinal)` primary key then silently collapsed them into one row.
*Fix:* order-preserving occurrence matching — the k-th stored row (in old
ordinal order) for a given hash takes the k-th occurrence of that hash in the
re-split list; if the section holds fewer copies than stored rows, the extras
drop, counted as unverified. On an unchanged section this is exactly the old
ordinal, so unchanged builds are unaffected.

Non-blocking notes (conventions reviewer): the relations gate is now
punctuation-stricter than its old local `abilities._fold` (the shared
`verbatim.quoted_in` preserves punctuation; a quote that differs only in
punctuation now fails the gate — a known, intended tightening); the
`_MEANING_TABLE_DDL` in `facts.py` duplicates `schema.sql` (noted, not
merged); a `build.py` comment duplicated the remap docstring (trimmed).

The test-sufficiency reviewer additionally killed two mutations before the
round closed: reverting the D3 `COALESCE` turns
`test_a_legacy_table_backfills_a_dangling_section` red
(`IntegrityError: NOT NULL constraint failed: events.doc_title`), and
dropping the `revid is not None` guard turns
`test_a_null_revid_row_survives_a_rebuild` red. Two tests were added for
those branches; `facts.py` was verified byte-identical after the reviewer's
experiments.

## Re-gated evidence (post F1/F2/F3, this session)

- **pytest: 1,219 passed** (1,206 pre-Phase-0 baseline; +10 for D4, +2 for
  the reviewer's branches, +1 for F3's duplicate-sentence case).
- **Gate 0D, 5/5 demos** (`/tmp/gate_phase0_demos.py`, fresh copies of the
  live `jjk` store): (1) guard fired — `ResetRefusedError` at 2,748 rows;
  (2) forced rebuild, renumbered graph — `{remapped: 2748, unverified: 0}`;
  (3) unverified branch — a section's text replaced under its 32 rows drops
  exactly those 32; a text-*appended* section's 24 rows survive
  (`{remapped: 2716, unverified: 32}`), and the new `logger.warning` fired;
  (4) crash recovery — the build dies after `reset`, 2,748 rows on disk in
  the snapshot file, the re-run recovers all 2,748 and deletes the file;
  (5) the post-commit crash window (F1's probe) — stale file + fully
  remapped store, the re-run's complete snapshot overwrites safely,
  idempotent re-remap, nothing lost.
- **Live-store dry run:** all 2,748/2,748 event rows pass the verbatim
  predicate against their own section text (`failed=0`) — a content-validated
  remap loses zero live rows on an unchanged build.
- **Standing gates:** `eval --series jjk` 24/24; `canon-run --series opm`
  10/16 exact, 236/236 canon, 79.0%; `span-recall --series jjk` 48,572/48,572
  (100%). `eval`/`canon-run` ran on CPU (`SCRIPTENGINE_DEVICE=cpu`) while the
  27B Qwen model held the GPU; `:8000` ran on CPU for the canon-run's API
  dependency.

## Verified-claims ledger (checked against code / `series/jjk/facts.db` this run)

- [x] **events: 2,748 rows, every one `revid` NULL.** All 987 JJK documents
      carry `revid = 0` in the crawl; the `isdigit` guard in `save_events`
      maps that to NULL, so the `stale` branch is **structurally dead on
      JJK** and the `unverified` content check is the only live defence
      there. NULL-`revid` rows are deliberately *kept* (dropping them would
      wipe the whole live layer on the first forced rebuild).
- [x] **The live `jjk` store has no `meaning` table** (created by
      `ensure_meaning` on the next index); 987 documents, 7,601 sections.
      The `meaning` remap branch is therefore exercised synthetically (the
      `TestMeaningRemap` suite) and on live-store copies only.
- [x] **The eight-verb closed set** is `arrived / awakened / betrayed /
      departed / fought / killed / saved / sealed` (live `DISTINCT verb`
      query) — the set Phase 1B measures.
- [x] **`plan/ORACLE_v1.yaml` sha256** =
      `a788fa29652a58152edf0f2ce16caea626db35d7e4463ec66176b5635a15935e` —
      matches the Phase 1A premise (checked this run; the file is never
      edited).
- [x] **F1 reproduced before the fix**: simulated crash between the two
      commits → re-run `reset()` overwrote the crash file with
      `{events: N, meaning: 0}` → the un-remapped rows were gone and the
      report lacked a `meaning` key. Post-fix the intermediate state is
      unobservable (single commit) and demo 5 covers both adjacent windows.
- [x] **F3 reproduced before the fix**: two rows, same sentence, ordinals 0
      and 2; a rebuild prepending one sentence re-keyed both to ordinal 1 and
      `INSERT OR REPLACE` left one row. Post-fix both survive (ordinals 1 and
      3; `test_remap_keeps_two_rows_for_a_sentence_that_appears_twice`).

## The 24k `meaning` pass — precondition status (flow.md "Authorising the
large GPU pass without a human")

The pass proceeds **only when all four** are green, recorded here with
evidence:

1. **Retention solved — GREEN.** Phase 0C landed and 0D is green: a rebuild
   demonstrably remaps survivors (demo 2: 2,748/2,748), crash recovery
   holds (demo 4), and the post-commit window loses nothing (demo 5).
2. **Frozen class spec + prompt v1 + participant guard — NOT YET.** The
   class vocabulary is frozen by the DDL `CHECK`; prompt v1 tied to
   `PROMPT_VERSION` and the participant guard are written with the pass.
3. **Pilot on the 1,748 chapter-anchored rows, scored against
   `ORACLE_v1.yaml` — NOT YET** (Phase 1A runs the oracle first).
4. **Pilot accuracy at or above its stated floor — NOT YET** (no pilot yet).

**One of four green. The 24,000-sentence pass does not run.**

## Verdict (chairman)

**SHIP Phase 0.** The four advisor defects are closed 5/5; the three
peer-review defects (F1 clobber, F2 invisible drop, F3 duplicate collapse)
are fixed, re-gated, and regression-tested; every standing gate is green.
Commit the named paths (branch `character-scoped-questions`, no push). Per
0D, **continue into Phase 1 without pausing**: 1A run the held-out oracle
(hash verified above), 1B the eight-verb coverage measurement, 1C the gate.

Known, recorded (not blocking): the relations gate's punctuation tightening
(F2-adjacent behavior change); the live `stale` branch dead on JJK (the
crawl writes `revid = 0`; the `unverified` check is the live defence); the
`meaning` table absent from the live store until the next index.