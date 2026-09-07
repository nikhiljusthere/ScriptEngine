# PEER REVIEW R2 — data quality (1C, round 2)

## Verdict

PROCEED-WITH-CHANGES — every data-quality defect I found is a "state the
reproducible figure" fix, not a structural blocker to Phase 2. The live store
(`series/jjk/facts.db`, read-only; probes via `file:/tmp/r2/store.db?mode=ro`)
confirms the substance of P4/P9/P10/P12/P13/P14/P18/P24 and the core of P7/P8/
P11/P27, but the pack's *supporting* figures on P7, P8 and P27 are not
reproducible and two of them are simply wrong (P7 "all 2,748 placed events",
P8 "135 occurrences"). Correct the figures before 2C, then proceed.

Method: every relied-upon number below is DB-verified against the live store
(appendix, SQL + result per check). Items that are process/code/plan (P2, P3,
P5, P6, P15, P16, P17, P19–P23, P25, P26) are out of the data-quality scope and
are left to the gate-logic reviewer (r3), which I have read and stayed
consistent with.

## Rulings on P1–P27 (data-quality lens)

| Item | Ruling | One-line data-quality reason |
|---|---|---|
| P1 | ACCEPT | Verified: `/tmp/oracle_1a_bundles/B2.json` `why: "Suguru Geto"`; the 1A report misquotes it "Suguru Gojo". Non-blocking quote typo. |
| P2 | UNVERIFIED | Code (`context.py:380` passage floor inactive with `subject=None`); not a data claim. Defer to r3 (ACCEPT). |
| P3 | UNVERIFIED | Code (runner's `bundle_text` drops relation `label`); not a data claim. Defer to r3 (ACCEPT). |
| P4 | ACCEPT | Verified: `A4.json` carries `('Sukuna vs. Jogo','Outcome','Sukuna is victorious.')` — a different battle's outcome, not the A4 ground truth; A1–A3 have no outcome rows. |
| P5 | UNVERIFIED | Plan (Phase-5 leave record); not a data claim. Defer to r3 (ACCEPT). |
| P6 | UNVERIFIED | Plan miscite (Phase 4 vs 5); not a data claim. Defer to r3 (ACCEPT). |
| P7 | MODIFY | Core slice point stands (verified below), but three supporting figures are wrong/non-reproducible: "all 2,748 placed events" → **714**; "character narrative sections (1,203)" not reproducible; "~171,716 words" not exact. See NR1–NR3. |
| P8 | MODIFY | 3/100 met/encountered gap is right (rows 008/018/047); the "163 sections / 64 instances" corroboration is not reproducible, and r3's replacement "135 phrase occurrences" is also wrong (live = 112). See NR4. |
| P9 | ACCEPT | Verified: the 100-row sample table has exactly 39 covered rows; 073 covered (`fought`), 085 uncovered (`fought (observation)`) — an uneven application of the same main-clause reading; the 38–40/100 band holds. |
| P10 | ACCEPT | Verified: 93 `awakened` and 4 `betrayed` rows are live (all under `qwen3.8-27b-ninfer`, 2026-09-05); 26 `sealed` rows mention prison/gojo. The 1B keep-justification cites the wrong verb (`sealed`), but the kept verbs do carry real rows. |
| P11 | MODIFY | Counts verified (2,748 live; 2,594 `temporal=1`; 32 orphans = location 15 + org 12 + item 3 + tech 2), but "a `--refresh` under the current scope would drop them" is a misread of the scope/refresh semantics. See NR6. |
| P12 | ACCEPT | Code-verified: the extractor windows prose with `_windows` (4,000-char windows, 300 overlap; `abilities.py:472`, called at `events.py:1002`) while the index chunks with `split_sentences` (`chunker.py:107`) — the two sides see different sentence boundaries. |
| P13 | ACCEPT | Verified: plan's section list (flow.md:233-234) sums to 100,926; live sums to **117,251** (Personality 42,533 / Appearance 14,180 / Overview 18,357 / Trivia 25,012 / History 17,169). "~106,000" is stale twice — record the live figure. |
| P14 | ACCEPT | Verified: ORACLE_v1 E1–E4 are all `category: personality`; the frozen sha256 `a788fa…` matches `plan/ORACLE_v1.yaml`. |
| P15 | UNVERIFIED | Process (2A/2C coupling); not a data claim. Defer to r3 (MODIFY, P24→P23 cross-ref). |
| P16 | UNVERIFIED | Process (2C reduction); not a data claim. Defer to r3 (ACCEPT). |
| P17 | UNVERIFIED | Process (EVENTIVE_VERBS re-freezes precondition 2 / PROMPT_VERSION `events-2026-09-05.2`); not a data claim. Defer to r3 (ACCEPT). |
| P18 | ACCEPT | Verified: `/tmp/oracle_run1a.py` (6,428 B), `/tmp/oracle_1a_results.txt` (18,378 B), `/tmp/oracle_1a_bundles/` (18 JSONs A1–F2) all exist; `/tmp` is ext4 (`/dev/nvme0n1p6`), not tmpfs — promote + sha256-pin before 2C. |
| P19 | UNVERIFIED | Process (`deviation_reasons.md` entries); not a data claim. Defer to r3 (ACCEPT). |
| P20 | UNVERIFIED | Process (restate 1/4 green at COUNCIL_1); not a data claim. Defer to r3 (ACCEPT). |
| P21 | UNVERIFIED | Process (commit list); not a data claim. Defer to r3 (ACCEPT). |
| P22 | UNVERIFIED | Process (stale-server trap, PID 94330 on CPU); not a data claim. Defer to r3 (ACCEPT). |
| P23 | UNVERIFIED | Process/code (2-prep fact-slice fix); not a data claim. Defer to r3 (ACCEPT). |
| P24 | ACCEPT | Verified: `aliases` over-maps — `sorcerer`→{Jujutsu Sorcerer, Hana Kurusu}, `gojo`→{Sorcerer Clan, Satoru Gojo}, `geto`→{Suguru Geto, Kenjaku}, `pseudo-geto`→{Kenjaku}; live collisions exist (`fight` ×9, `domain` ×8, `battle` ×8). Defer as a data-quality ticket; after P23 no oracle item depends on it. |
| P25 | UNVERIFIED | Code (`rank_subjects` type-priority vs `signals['subject']`); not a data claim. Defer to r3 (ACCEPT). |
| P26 | UNVERIFIED | Process (4C re-anchor is owner scope); not a data claim. Defer to r3 (MODIFY). |
| P27 | MODIFY | "1,748 chapter-anchored rows" point stands (nothing live equals 1,748; no `meaning` table), but the supporting "events in Chapter/Episode docs 885" is imprecise: total ch+ep events = **923**; 885 is the `arc_index`-NOT-NULL (chapter-anchored) subset. See NR5. |

Tally (data-quality lens): 9 ACCEPT / 4 MODIFY (P7, P8, P11, P27) / 14 UNVERIFIED
(process/code/plan, deferred to r3).

### Replacement texts (MODIFY items)

**P7** — keep the core: "1B's 61% uncovered figure covers only the Summary
slice: live, the 363 chapter/episode pages carry Summary 363 sections / 16,194
words vs Plot Details 363 sections / 241,855 words on the same pages." Replace
the three supporting figures with the reproducible ones:
- "and the 108-doc placement scope (**165,941 words / 388 sections** by the
  extraction rule — narrative heading + word-count floor, per `scope_plan`'s
  own docstring; 171,503 / 430 if all sections ≥20 words are counted)" — not
  "~171,716 words";
- "which holds **714 placed events** (all `arc`/`saga`/`event`/`battle`/
  `story_arcs` docs), not all 2,748 — the other 2,034 sit on chapter/episode/
  character/character-synopsis/location/organization/item/technique pages via
  the corpus rule" — the code's `scope_plan` docstring already says "388
  sections (165,941 words) that hold all 714 placed events";
- drop "character narrative sections (1,203)" or replace with a reproducible
  figure (nearest: 1,303 sentences in 134 narrative sections across the 146
  `character` pages; 9,134 across the character-family).

**P8** — keep "The met/encountered gap is 3/100, not 2/100 (rows 008, 018, 047;
047 was bucketed 'fought (encounter + assessment)')". Replace the corroboration
with: "Live corroboration: **112 sections** in the placement ∪ character
families carry encounter/crosses-paths/first-contact wording (**112 phrase
hits**: 111 `encounter` + 1 `crosses paths` + 0 `first contact`; query:
`(lower(text) LIKE '%encounter%' OR LIKE '%crosses paths%' OR LIKE
'%first contact%')` over `page_type IN PLACEMENT_TYPES OR page_type LIKE
'%character%'`)". The original "163 sections / 64 instances" and r3's "135
phrase occurrences" are both not reproducible — use 112/112.

**P11** — keep "Live events = 2,748 rows (2,594 is the `temporal=1` subset,
all `arc_index` NOT NULL); 32 rows (1.2%) sit in location/organizations/item/
technique page types (15+12+3+2) in neither PLACEMENT_TYPES (`events.py:59`)
nor the character families (`events.py:834-840`)". Replace "A `--refresh` under
the current scope would drop them — a latent derived-row-loss exposure" with:
"Under the **default** `--scope placement`, `scope_plan` does not read those
pages and `save_events` (facts.py:1782) replaces per-arc only, so the 32 rows
**persist as dead weight** (not dropped, not re-proven). Under the documented
complete-coverage `--scope all` refresh, the 32 sections **are** in the corpus
scope (each names ≥2 character nodes, verified), so they are re-extracted and 0
of the 2,748 drop. The real exposure is (a) a **scope change** that newly
covers those pages, where per-arc replacement then drops any rows the new
extraction does not re-prove (condition 4, flow.md:72-73), or (b) a **rebuild**
that orphans their sections. Determine the 32 orphans' provenance (presumably
an earlier, broader scope) before such a run." Note: the corpus rule at
`events.py:834-840` filters the *referenced* character-family nodes, not the
section's own document, so it reaches into chapter/episode Plot Details (295
of 363 ch/ep "Plot Details" sections are in corpus scope) — the 32 are in scope
for that reason, not because their page is a character page.

**P27** — replace "events in Chapter/Episode docs 885" with: "events in
chapter/episode docs **923** (629 chapter + 294 episode; `SELECT count(*)
FROM events e JOIN documents d ON d.title=e.doc_title WHERE d.page_type IN
('chapter','episode')` → 923). Note 885 is the `arc_index`-NOT-NULL
('chapter-anchored') subset (591 chapter + 294 episode) — if the item means
chapter-anchored rows, 885 is defensible; if it means all ch/ep events, it is
923; state which." Keep: no `meaning` table exists in the live store; nothing
on disk equals 1,748; state the provenance (or recompute when the table lands)
rather than gating on it.

## New data-quality defects (NR1..NR6)

**NR1 — P7 "all 2,748 placed events live there [in the placement scope]" is
wrong; the figure is 714** (blocking for the record). `SELECT count(*) FROM
events e JOIN documents d ON d.title=e.doc_title WHERE d.page_type IN
('arc','saga','event','battle','story_arcs')` → **714** (battle 387 + event
127 + story_arcs 200). The other 2,034 (chapter 629 + episode 294 + character
150 + character_synopsis 929 + location 15 + organizations 12 + item 3 +
technique 2) live outside PLACEMENT_TYPES and are covered by the corpus rule.
The code's own `scope_plan` docstring already says the 388 placement sections
"hold all **714** placed events", so the pack's 2,748 contradicts the code.
Disposition: corrected in the P7 replacement above.

**NR2 — P7 "character narrative sections (1,203)" is not reproducible**
(note). No stated extraction rule yields 1,203. Live: 1,303 sentences in 134
narrative-heading sections across the 146 `character` pages; 9,134 across the
character-family (`character` + `character_synopsis`). Disposition: drop the
figure or cite one of the reproducible ones (P7 replacement above).

**NR3 — P7 "~171,716 words" (placement scope) is not exactly reproducible**
(note). Live: extraction rule (narrative heading + word-count floor, per
`scope_plan` docstring) = **165,941 words / 388 sections**; all placement
sections ≥20 words = **171,503 / 430**. Neither is 171,716. Disposition: state
the rule and use 165,941/388 (P7 replacement above).

**NR4 — P8's "163 sections / 64 instances" and r3's "135 phrase occurrences"
are both not reproducible; live is 112/112** (note). Placement ∪
character-family, `encounter`/`crosses paths`/`first contact`: **112 sections /
112 phrase hits** (111 `encounter` + 1 `crosses paths` + 0 `first contact`).
Other families: all sections 186/216; `scope_plan('all')` 125/142; 2-pattern
(encount + first contact) 184/214. Disposition: use 112/112 (P8 replacement
above).

**NR5 — P27 "events in Chapter/Episode docs 885" is imprecise; total is 923**
(note). Total ch+ep events = **923** (629 chapter + 294 episode). 885 is the
`arc_index`-NOT-NULL (chapter-anchored) subset (591 + 294). The substantive P27
point (1,748 unverified, no `meaning` table) stands. Disposition: corrected in
the P27 replacement above.

**NR6 — P11 "a `--refresh` under the current scope would drop them" misreads
the scope/refresh semantics** (note). The 32 orphans are in the corpus scope
(verified), so under the documented `--scope all` refresh, 0 of the 2,748 drop;
under the default `--scope placement`, the 32 pages are not read and the rows
persist as dead weight (per-arc replacement, facts.py:1782). The drop risk
materializes only on a scope change that covers those pages, or a rebuild.
Also, `events.py:834-840` (the "character families" P11 cites) filters the
referenced character-family *nodes*, not the section's document, so the corpus
rule reaches chapter/episode Plot Details (295 of 363 ch/ep "Plot Details"
sections are in corpus scope) — the 32 are in scope via that path. Disposition:
corrected in the P11 replacement above.

## Verified-claims ledger (SQL → result)

- `SELECT count(*) FROM events` → **2,748**; `WHERE temporal=1` → **2,594**;
  `WHERE arc_index IS NOT NULL` → **2,594** (the temporal subset ==
  arc_index-NN). `revid IS NULL` on all 2,748.
- Verb distribution (live `events.verb`): fought 1200, arrived 526, killed 314,
  saved 289, departed 288, **awakened 93**, **sealed 34**, **betrayed 4**.
  All `awakened`/`betrayed` rows under `qwen3.8-27b-ninfer`, 2026-09-05.
- events by `doc_title`→`documents.page_type`: character_synopsis 929, chapter
  629, battle 387, episode 294, story_arcs 200, character 150, event 127,
  location 15, organizations 12, item 3, technique 2 (= 2,748).
- **714** events have doc in PLACEMENT_TYPES (battle 387 + event 127 +
  story_arcs 200) → NR1.
- ch+ep events = **923** (chapter 629 + episode 294); `arc_index IS NOT NULL`
  within ch+ep = **885** (591 + 294) → NR5.
- 32 orphans (location 15 + org 12 + item 3 + tech 2): **all 32** section_ids
  are in `scope_plan('corpus')` and `scope_plan('all')` (0 out of scope under
  `all`) → NR6.
- Section word totals by title (live): Plot Details 241,855 / 363, Summary
  16,194 / 363, Personality 42,533 / 138, Trivia 25,012 / 299, Overview 18,357
  / 49, History 17,169 / 129, Appearance 14,180 / 145. Five-section (Phase-5)
  sum = **117,251**; plan list = 100,926 (P13).
- Placement-scope word totals: extraction rule = **165,941 / 388 sections**;
  all sections ≥20 words = **171,503 / 430** (NR3).
- P8 phrase corroboration (placement ∪ char-family): **112 sections / 112 hits**
  (111 encounter + 1 crosses paths + 0 first contact) (NR4).
- P9: 100-row sample table = exactly **39** covered rows; 073 covered (`fought`),
  085 uncovered (`fought (observation)`).
- Report A re-confirmed: Satoru Gojo 20 facts (`class | Grade = Special
  Grade`); Suguru Geto 19 (`occupation = Jujutsu Sorcerer (Former) Curse
  User`); Hana Kurusu 12; 98 outcome rows; all 4 A ground truths verbatim,
  incl. "Sukuna vs. Jogo => Sukuna is victorious." (backs P4).
- ORACLE_v1 sha256 `a788fa29…` matches `plan/ORACLE_v1.yaml`; E1–E4 all
  `category: personality` (P14).
- P18 evidence on disk: `/tmp/oracle_run1a.py`, `/tmp/oracle_1a_results.txt`,
  `/tmp/oracle_1a_bundles/` (18 JSONs) — all present; `/tmp` ext4.

## Notes for the chairman

- My MODIFYs (P7, P8, P11, P27) all agree with r3's direction; they add the
  data-quality corrections r3's ACCEPT/MODIFY did not carry: P7's "2,748
  placed events" is 714 (NR1), P7's "1,203" and "~171,716" are not
  reproducible (NR2–NR3), P8's "135 occurrences" (r3's replacement) is 112
  (NR4), P27's 885 is the chapter-anchored subset of 923 (NR5), and P11's
  drop-exposure only materializes on a scope change / rebuild (NR6).
- All 14 UNVERIFIED items are process/code/plan and are correctly carried by
  r3; no data-quality objection to r3's rulings on them.
- Net: no blocker to Phase 2. Require the P7/P8/P27 figure corrections and the
  P11 scope-semantics note in the 1C record; the rest proceed as r3 ruled.