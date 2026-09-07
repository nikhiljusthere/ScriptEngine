# COUNCIL HISTORY

The ledger of every council run in this repo. Standing rule: **councils are
evidence, not conversation — if a council is not on disk, it did not
happen.** Each row points at the on-disk record (the full transcript of the
council's positions, the verified-claims ledger, and the verdict); this file
carries only the index + the verdict line. Newest first.

Protocol for every entry: 5 advisors (independent, parallel) → anonymized →
5 peer reviewers (independent, parallel, each weighted to a failure mode) →
chairman synthesis; every load-bearing claim re-verified against code +
`series/jjk/facts.db` before recording. (The parallel batches are the
council-only parallelism; sequential work elsewhere still runs one at a time.)

| # | Record | Step | Verdict (one line) |
|---|--------|------|--------------------|
| 12 | `COUNCIL_2c-gate.md` | 2C gate (beam-first) result + the A4 root-cause and fix | **2C beam-first 16/18 (A4 outcome + C1 timeline, a documented expected-fail); A4's root cause pinned to the live-qa fusion guard, *not* routing or the resolver (the resolved fight sits at position 6 — linked but not paid for, so the old `not in entities` guard skipped the prepend and the wrong top-5 fight was served). Fix `6af92ca` (dedup + prepend the resolved battle block): oracle 17/18 in-process (only C1 open), pytest 1239, eval 24/24, span-recall 100%.** |
| 11 | `COUNCIL_phase5-next-move.md` | next move after Phase 5 closure — the 5-step retrieval-only sequence | **Fix-first, then measure: (1) fix A4 [done `6af92ca`], (2) 3-way miss taxonomy (retrievable-but-not-served / absent-cross-page / gold-wrong — never rephrase a question to dodge), (3) fold demand-audit items into the gold bank, (4) demand-weighted pilot, (5) full 545 census. Retrieval-only, never 27B. Deferred: TF-IDF trait index + cross-series gate.** |
| 10 | `COUNCIL_phase5-closure.md` | Phase 5 closure — does not extracting the 5 prose dimensions (Personality/Appearance/Overview/Trivia/History) lose data? | **"No data loss" is TRUE (prose preserved + 100% span-recall; 218 pages, 545 pairs, ~106k words; a field is a lossy, citation-severing derivative).** But "closed" is not yet *earned*: the claim is backed only by E1–E4 (4/545, personality-only). Keep Phase 5 closed on the data (no 27B owed, reversible deferral); clear it with 4 retrieval-only gates BEFORE resuming from `2ea235e`: (1) demand audit, (2) 545-question relevance gate on used dimensions, (3) explicit "no section found" signal, (4) optional TF-IDF trait index for cross-character facets (never a reason to reopen extraction). |
| 9 | `COUNCIL_1.md` | Phase 1C gate — 1A held-out oracle + 1B verb coverage | **PROCEED-WITH-CHANGES (1C green; continue into Phase 2).** 1A: 11/18 (chair-corrected from a first-recorded 14/18; categories 0/4, 2/4, 2/3, 1/1, 4/4, 1/1, 1/1). 2A (event-level outcome binding) confirmed as the real gap — A-group 0/4, 98 `outcome` rows already in `facts`, all four A ground truths verbatim in-store. 2B refuted and halted (F1/F2 PASS at 1A; deviation_reasons.md). Phase 5 closed in full per its own gate (117,251 live words; plan list 100,926; flow.md:243's ~106,000 matches neither). New 2-prep: subject-anchored fact floor with a floor cap/beam reservation (Gojo's floor is 8,540 tokens > the 6,000 default budget) + `met` verb widening with prompt-v1 re-freeze. 4C re-anchor recorded as a pending owner decision. 24k pass: 1/4 preconditions green — it does not run. |
| 8 | `COUNCIL_0.md` | Phase 0 — rebuild-safe `facts.db` (0A/0B/0C/0D) | **SHIP.** Advisor defects D1 (content-blind remap), D2 (crash window), D3 (backfill NULL), D4 (untested destructive branches) closed 5/5; peer-review defects F1 (clobber), F2 (invisible drop), F3 (duplicate collapse) fixed and re-gated (pytest 1,219; gate 0D 5/5; eval 24/24; canon 10/16·236/236·79.0%; span-recall 100%). 24k-pass preconditions: 1/4 green — the pass does not run. |
| 7 | `COUNCIL_3b-commit.md` | 3b commit — corpus-scope work (524-page extraction) | **Set-size gain, not comprehension gain:** events 714 → 2,748, `temporal=1` still exactly 714, all 2,034 new rows `temporal=0`; invariant `COUNT(arc_index IS NULL) = COUNT(temporal=0) = 2,034` holds. |
| 6 | `COUNCIL_continuity-check.md` | D6-consumer scaffold design | **Build a gap *detector*, not a rejector** (`gap = claimed_arc − actual_arc`); seed the gold set from the **triaged** 107 (31 interaction-verb, gap≥2), not the raw 107; scaffold-only, model-free, `ingest/continuity.py`. |
| 5 | `COUNCIL_placement-signal.md` | placement-signal fix (D6-completeness) | **Code fix in the axis, not a data-UPDATE:** section signal (995 arc-named-heading rows) + chapter/episode `arc`/`chapters` signal; per-(page, section) placement; NULL `arc_index` 2,034 → 154, 2,748 intact. |
| 4 | `COUNCIL_d5-close.md` | D5-close (Ch.239 → References index miss) | **Close with a per-wiki chunker override** (`series/jjk/overrides.yaml: content_sections: [references]` + `effective_boilerplate_sections`), JJK-local; span-recall 48,572/48,572 + eval 24/24 after re-index. |
| 3 | `COUNCIL_last-bucket-scoping.md` | the last bucket's scope | **Mis-scoped as written** — re-scoped into units: 1 D5-close ∥ 2 placement-signal (code) → 3 continuity-check; cross-corpus is a separate bucket. |
| 2 | `COUNCIL_b5-premise.md` | the B5 premise (arc-named majority, round 2) | **B5 is diagnostic, not corrective:** do not build a demotion gate (no correct loser in 60/107 groups); surface repeat-encounter/boundary groups to a human and refine the key with a chapter/temporal component; the `(verb,s,o)` key's coarseness itself produces the "disagreement." |
| 1 | `COUNCIL_r1-per-line-meaning.md` | R1 per-line/per-beat meaning index (design, pre-build) | **Proceed with classifier+locator, bounded to the unverified complement** (not the 48k); the meaning-gloss question is an open values call; `arc_index` structurally NULL for unplaced lines; the door is a pure offline read. |

## Open values calls recorded by the councils (not acted on)

- The **meaning-gloss call** (classifier+locator vs a stored free-text
  gloss) — project-owner decision (`COUNCIL_r1-per-line-meaning.md`).
- **Door input identity** for `meaning`: wiki-line `(section_id, ordinal)`
  lookup vs writer-typed-line FTS5 match (`COUNCIL_r1-per-line-meaning.md`).
- **Authoritative source** for double-written event fields (pointer vs
  duplicate between `events` and `meaning`) (`COUNCIL_r1-per-line-meaning.md`).
- The **11% → 27.4% disagreement-rate rise**: genuine regression vs
  visibility artifact vs wiki drift — the spot-check records which
  (`COUNCIL_b5-premise.md`).
- `time_rank` is the wiki's *authoring* order, not chronology — the honest
  writer guarantee is "wiki-filed order with declared provenance"
  (`COUNCIL_b5-premise.md`).
- The cross-corpus pass: align the span-recall **oracle's** per-wiki
  content-policy with the chunker's per-wiki skip-policy across the other 7
  wikis (`COUNCIL_d5-close.md`).

## What is NOT in this ledger

- The per-batch `page-run` scoring campaigns and the comprehension-gate runs
  are *executions*, not councils — they live in `reports/page-campaign/` and
  `reports/comprehension/GATE.md`.
- A council that only happened in conversation has no row here and no
  standing: it is not evidence.