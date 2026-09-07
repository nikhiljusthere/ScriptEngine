# PEER REVIEW R1 — oracle scoring (1C, round 2)

Reviewer weighting: **oracle scoring validity** (does the 1A 18-item oracle run
score what it claims to score, and does the 14/18 stand?). Every claim I rule
on below was re-checked against the raw bundles (`/tmp/oracle_1a_bundles/`), the
live store (`series/jjk/facts.db`, read-only), the code, or the oracle itself.

## Verdict

PROCEED — the 1A oracle scoring is valid and the 14/18 stands: all 18 verdicts
reproduce independently (runner-text and full-text), both surprises (B1 PASS,
B4 FAIL) are real and mechanistically explained, and no verdict depends on the
runner's known omissions; the defects found are record-level or plan-level and
enter the Phase-1 commit / plan as scope-and-record items, none of which
pauses the gate.

## Rulings on P1–P27

| Item | Ruling | One-line reason |
|---|---|---|
| P1 | ACCEPT | `B2.json routed.why` = `"question about 'Suguru Geto', a character"` (and `B4.json` = `"Satoru Gojo"`); the 1A report's "Suguru Gojo" is a quote typo; correct when the record is written. |
| P2 | ACCEPT | With `subject=None` the R6 floor is off (`context.py:380` `passages_for_subject(subject) if subject else []`); `B1.json` has 8 beats, all non-zero beam scores (0.1015–0.5397), zero score-0.0 floor rows, and its GT sits in beat 8 (`Angel / Synopsis / Culling Game Arc`, score 0.1015) — the beat reached the bundle via the ranked beam. One-line clarification in the record. |
| P3 | ACCEPT | `oracle_run1a.py` renders relations via `edge.get('label')`, a key qa relation rows do not carry (they carry `relation`, `quote`, `era`), so relation names/quotes were dropped from the audited text; I re-scored all 18 items on full text (beats + facts + relation `relation`/`quote`/`era`) and every verdict is identical to the runner-text scoring — no verdict affected; fix the runner before any future oracle run reuses it. |
| P4 | ACCEPT | `A4.json` carries `{'entity': 'Sukuna vs. Jogo', 'field': 'Outcome', 'value': 'Sukuna is victorious.'}` while the correct battle's outcome ("The jujutsu sorcerers are victorious.") is absent from the bundle; the `contains` FAIL verdict is still correct (GT absent), but a writer could quote the wrong fight's result; load-bearing for 2A's design (bind outcome to the specific fight). |
| P5 | ACCEPT | `flow.md:231-243` is Phase 5 ("The subjective set", all five sections at :233-234); "**This phase may not exist.** It opens only if oracle E1–E4 failed at 1A" (:236-237) and "IF REFUTED: close the phase" (:243) — with E1–E4 green the whole phase closes, so the record must carry both the ~42,500 (Personality) leave and the full Phase-5 closure, not just the former. |
| P6 | ACCEPT | `flow.md:236` is Phase 5's "may not exist"; personality extraction is Phase-5 scope (:233), Phase 4 is state-over-time — the 1A report's "Phase 4 personality extraction (flow.md:236)" is a miscite; correct to Phase 5. |
| P7 | MODIFY | The slice framing and its two verified figures are right (363 Summary sections → 949 sentences ≥20 chars reproduced exactly via `chunker.split_sentences`; 363 Plot Details sections → 13,115 such sentences; 108 PLACEMENT_TYPES docs → 171,716 words, all exact live counts) but the parenthetical "where all 2,748 placed events live" is wrong: only 714 of the 2,748 events sit on placement-type docs; see replacement. |
| P8 | ACCEPT | Sample row 047 ("Nobara and Akari encounter Haruta Shigemo on the way…") is literally the met/encountered event type (same as 008 "make first contact", 018 "crosses paths with") yet was bucketed "fought (encounter + assessment)" — "encounter" is not in the rule's conflict-wording list and "surprisingly powerful" is assessment, not conflict — so the gap is 3/100, not 2/100; the 163-section/64-instance corroboration is not re-derived (I count 186 sections across all titles carrying the wording, directionally consistent) — state it as a lower bound, which the item already does. |
| P9 | ACCEPT | 073 ("the battle that ensues proves to Jogo…") is covered=fought while 085 ("his allies watching the fight know…") is uncovered, though both contain a stated conflict and both carry epistemic main clauses; main-clause-governs → both uncovered (38/100), rule-as-written → 085 covered (40/100); the report's 39/100 is internally inconsistent; record the 38–40 band and tighten the rule wording. |
| P10 | ACCEPT | Live `events` under `prompt_version='events-2026-09-05.2'` (the only version present) has exactly 93 `awakened` and 4 `betrayed` rows; the "Gojo's Prison Realm is `sealed`" justification is a different verb and is no evidence for these two; rewrite the justification on the 93/4 rows. |
| P11 | ACCEPT (counts verified; refresh-mechanism claim unverified) | Live `events` = 2,748 rows; `temporal=1` = 2,594; 32 rows (15 location + 12 organizations + 3 item + 2 technique, 1.2%) sit in page types in neither `PLACEMENT_TYPES` (`events.py:59` = arc/saga/event/battle/story_arcs) nor the character families (`events.py:834-840`, types containing "character"); quote 2,748 and determine the orphans' provenance before any `--refresh`; whether a refresh actually drops them I did not verify. |
| P12 | ACCEPT | The extractor reads section text in windows (`events.py:34` imports `_windows` from `ingest/abilities`, called at `events.py:1002`), while `chunker.split_sentences` (`chunker.py:107`) is the index's splitter — "the same split the extractor sees" is an overclaim; reword to "the engine's own sentence splitter". |
| P13 | ACCEPT | The plan's own list (42,533+14,180+16,731+15,887+11,595) sums to 100,926, not ~106,000; live `sections.word_count` sums are Personality 42,533 / Appearance 14,180 / Overview 18,357 / Trivia 25,012 / History 17,169 = 117,251 (Overview/Trivia/History stale in the plan); record the live-verified 117,251 or note the staleness. |
| P14 | ACCEPT | All four E items in `plan/ORACLE_v1.yaml` are `category: personality`; Appearance/Overview/Trivia/History have no oracle items, so they leave the build list by the gating condition (Phase 5 never opens), not by section-specific evidence — say so in the record, and any future phase needing one brings its own oracle evidence. |
| P15 | MODIFY | The coupling is real and verified — 98 `facts WHERE key='outcome'` rows, all four A ground truths in-store verbatim, and the battle-page prepend (`hybrid.py:213-225`, `battle_facts` prepended ahead of the `facts[:30]` slice) is immune to the subject-unaware slice — but the item's cross-reference "the fact-slice fix (P24)" points at the alias data-quality item; the fact-slice fix is P23; see replacement. |
| P16 | ACCEPT | With 2B's premise refuted (F1/F2 pass at 1A) there is no F extraction, so 2C's "F-group re-run" measures nothing; reduce 2C to "A-group shows 2A's change; F-group unchanged (already passing at 1A)". |
| P17 | ACCEPT | Precondition 2 is "frozen class spec + prompt v1 coupled to PROMPT_VERSION" (`flow.md:89-91`); the live events table is a single version `events-2026-09-05.2`; widening `EVENTIVE_VERBS` (`events.py:43-54`) edits the prompt's verb rule list, so prompt v1 must be re-frozen post-widening with its own PROMPT_VERSION bump and the cached 2,748 rows stay untouched; the 24k pass remains 1/4 green and not-runnable. |
| P18 | ACCEPT | Runner + console log + 18 raw bundles live only in `/tmp` (`/tmp/oracle_run1a.py`, `/tmp/oracle_1a_results.txt`, `/tmp/oracle_1a_bundles/`, 18 files); the repo already tracks raw gate output in `reports/comprehension/raw/` (directory exists); promote to `reports/comprehension/raw/oracle_1a/` and pin sha256s in the record — blocking for the record. |
| P19 | ACCEPT | `plan/deviation_reasons.md` carries only the pre-run and 0A entries; F1/F2 PASS at 1A refutes 2B's premise and E1–E4 pass refutes Phase 5's "E1–E4 failed" premise, yet no 2B entry and no Phase-5 entry exist; per the standing rule a halt not on disk in the designated file "did not happen"; add both entries (with raw output) before the Phase-1 commit — blocking for the record. |
| P20 | ACCEPT | `COUNCIL_0.md:205` reads "One of four green. The 24,000-sentence pass does not run."; nothing in Phase 1 touched preconditions 2–4; per `flow.md:96-97` COUNCIL_1 must re-state "1/4 green (retention only), pass does not run" to stay self-contained. |
| P21 | ACCEPT | Phase-1 commit = PHASE1A_ORACLE.md, PHASE1B_VERB_COVERAGE.md, COUNCIL_1.md, COUNCIL_HISTORY.md (append), plan/deviation_reasons.md (P19 entries), promoted evidence (P18); `git status` shows `reports/index.md` is the only tracked modification (references untracked canon-run dirs) — exclude it and note it in COUNCIL_1; never `git add -A`; no push. |
| P22 | ACCEPT (one-second timestamp nit, no code consequence) | PID 94330 = `./scriptengine/.venv/bin/python -m scriptengine.api.main`, started Sat Sep 5 23:33:22 +0530 = 18:03:22Z (pack says 18:03:23Z — `ps` shows 18:03:22Z); commit `94909d2` landed 23:31:34 +0530 = 18:01:34Z, and the only tracked change since is `reports/index.md` (markdown, not loaded by the server) — so the server is serving `94909d2` code; a 2C re-run against it after Phase-2 code lands would silently measure the old code: restart :8000 on CPU before 2C and record server-start > commit, as 1A did. |
| P23 | ACCEPT | Mechanisms verified: with `subject=None` the floor is off (`context.py:380`); `facts_for` (`facts.py:1077-1085`) is a plain `n.name = ? COLLATE NOCASE` lookup with no alias join; the subject-lead fix (subject's own facts first, per-subject cap ~24, fill from `result.facts` minus the subject's rows, total cap 30) resolves both failures — Geto has 19 facts (GT occupation included) and Gojo 20 (GT `class`/Grade = 15th, included); the rejected alternatives are correctly rejected: a bigger cap is ad hoc (Geto sits 7th), round-robin gives 6/entity at cap 30 (still misses Gojo's 15th), and `rank_subjects()[0]` is the wrong anchor (P25, verified below). Gate = full 18-item re-run. |
| P24 | ACCEPT | Alias rows verified live: `Hana Kurusu ← "sorcerer"`, `Sorcerer Clan ← "gojo"`, `Kenjaku ← "geto"` and `Kenjaku ← "pseudo-geto"` (the collisions are real: "sorcerer" also hits `Jujutsu Sorcerer`, "gojo" also `Satoru Gojo`, "geto" also `Suguru Geto`; in B2's link order Kenjaku (6th) does tie-break ahead of Suguru Geto (7th)); after P23 no oracle item depends on it; defer as a data ticket (audit single-token generic aliases at harvest; report same-alias collisions in `audit`); `Grade` matching "grade" is legitimate recall. |
| P25 | ACCEPT (verified by execution) | I ran `rank_subjects(store.link_entities(q), demote, priority)` on both queries with the live JJK overrides: for "Was Geto a jujutsu sorcerer or a curse user…?" the order is [Hana Kurusu, Kenjaku, Suguru Geto, …] and for "What grade of sorcerer is Gojo?" [Hana Kurusu, Satoru Gojo, …] — top-1 is "Hana Kurusu" in both (character page-type priority, then raw link order), so anchoring the fact floor on `rank_subjects()[0]` would serve Hana Kurusu's facts and fix nothing; the router's `signals["subject"]` returned the right entity in both items (bundle `routed.signals.subject` = "Suguru Geto" / "Satoru Gojo"); state the correct anchor in the 2-prep task spec. |
| P26 | ACCEPT | 4C's "B1 and B2 must move" is already stale: B1 is green at 1A (surprise pass) and B2 goes green after 2-prep (subject-lead fix), so the gate would be vacuous and the B-group would stop sizing the state-over-time gap; re-anchor 4C to "B-group holds (no regression) + interval state table non-empty and cited by /context", with any time-indexed-state probe as a new ORACLE_v2 item (ORACLE_v1 frozen); apply at 4C, record at 1C. |
| P27 | ACCEPT | "1,748 chapter-anchored rows" is a plan-side figure (`flow.md:89`, 24k precondition 3); nothing in the live store equals it: no `meaning` table exists, live `events` = 2,748, `arc_index NOT NULL` = 2,594, events in Chapter/Episode docs = 885 (591 `doc_title LIKE 'Chapter%'` + 294 `'Episode%'`); the record should state its provenance and recompute when the `meaning` table is created; do not gate on faith. |

Tally: 25 ACCEPT (two with caveats: P11 refresh-mechanism unverified, P22
timestamp nit), 2 MODIFY (P7, P15), 0 REJECT.

### Replacement text — P7 (MODIFY)

The item's closing clause should read:

> …and the 108-document placement scope (~171,716 words, of which 714 of the
> 2,748 placed events live on placement-type docs; the remaining 2,034 live on
> chapter/episode/character-family/orphan docs). 61% is neither an upper nor a
> lower bound for the full scope. Quote it as "61% of the Summary slice."

Evidence: `SELECT COUNT(*) FROM documents WHERE page_type IN
('arc','saga','event','battle','story_arcs')` → 108; `SELECT
COALESCE(SUM(s.word_count),0) FROM sections s JOIN documents d ON d.id=s.document_id
WHERE d.page_type IN (…)same…` → 171,716; `SELECT COUNT(*) FROM events e JOIN
documents d ON d.title=e.doc_title WHERE d.page_type IN (…)same…` → 714 (story_arcs
200 + battle 387 + event 127); `SELECT COUNT(DISTINCT doc_title) FROM events` → 508.
The other P7 figures verified as stated: 363 Summary sections → 949 sentences
≥20 chars (reproduced via `chunker.split_sentences`); 363 Plot Details sections
→ 13,115. The "1,203 character narrative sections" figure is not re-derived
(character-family sections total 1,947; "narrative" is undefined in the item)
— see Unverified.

### Replacement text — P15 (MODIFY)

The last sentence should read:

> Either 2A's spec states the serving channel or the fact-slice fix (P23)
> becomes a 2C precondition.

Evidence: P24 is "The linker over-match is ingest data quality" (the alias
ticket); the subject-unaware fact-slice defect and its fix shape are P23. The
item's earlier placeholder "(P-item, below)" likewise points at P23. Nothing
in the coupling logic changes: verified live — `SELECT COUNT(*) FROM facts
WHERE key='outcome'` → 98; all four A ground truths ("Nanami withdraws.",
"Sukuna is victorious.", "Uraume commits suicide.", "The jujutsu sorcerers are
victorious.") present verbatim as outcome rows on the four battle pages; the
prepend path `hybrid.py:213-225` (`battle_facts` prepended, so its rows survive
the `result.facts[:30]` slice at `context.py:392`) is immune, while a
character-entity fact-list serving would drop them.

## New defects (NR1–NR2)

**NR1. The 1A report misattributes the beat that serves C2's ground truth.**
`reports/comprehension/PHASE1A_ORACLE.md:41` — the C2 row's "what was served"
column reads: `Todo page Usage beat: "Aoi cracks Hanami's hard shell with
Playful Cloud"`. In `/tmp/oracle_1a_bundles/C2.json` the ground truth appears
in exactly one beat: beat 8 of 8, `Kyoto Goodwill Event Arc / Synopsis /
Enemies Invade the Event` (an arc page, not the Aoi Todo page); beats 1–3 are
the Usage/Equipment beats (Playful Cloud Usage, Aoi Todo Equipment, etc.) and
none contains the ground-truth string. The PASS verdict itself is unaffected
(the `contains` check runs over the whole bundle text), but the record points a
reader at the wrong page for the served fact. Disposition: **blocking-record**
(correct the C2 row in COUNCIL_1: "Kyoto Goodwill Event Arc page, Synopsis /
Enemies Invade the Event beat (beat 8 of 8)").

**NR2. The B4 "5 of 20" mechanism in the record is imprecise about *which* 5.**
The pack/report shorthand "Gojo's facts stop at Species (5 of 20)" is right in
count but the record should state the mechanism exactly, or a future reader
will mis-locate the cut: the bundle's fact list is the per-participant
concatenation in `link_entities` order (Grade 5 + Hana Kurusu 12 + Jujutsu
Sorcerer 8 = 25, then Gojo fills 26–30), truncated at 30 (`context.py:392`),
so Gojo — the 4th of 5 participants — receives only his first 5 facts in
`f.id` order (name, kanji, romaji, alias, race/"Species"), and the ground
truth `class`/"Grade = Special Grade" is Gojo's 15th fact (`facts.id 8192`),
10 places past the cut. B2 is the same mechanism: Jujutsu Sorcerer 8 + Curse
User 7 + Jujutsu 7 + Hana Kurusu 8 = 30, so Cursed Spirit/Kenjaku/Suguru Geto
(participants 5–7) receive zero facts — `served_values: []` in
`/tmp/oracle_1a_results.txt:26`. Disposition: **blocking-record** (state the
participant-position + 30-cap mechanism, not just "5 of 20", in the 1A
record's Finding 3 and in the 2-prep task spec).

## Unverified claims

- **P7 "character narrative sections (1,203)"** — no definition of
  "narrative" is given; character-family sections total 1,947 live, so 1,203
  is directionally plausible but I did not re-derive the subset.
- **P8 "163 sections in the extraction families (64 sentence-level instances,
  lower bound)"** — the "extraction families" set is unspecified; my
  all-titles count of sections carrying encounter/crosses-paths/first-contact
  wording is 186, directionally consistent with a 163-family-subset and the
  64-instance lower bound, but neither figure is re-derived.
- **P11 "a `--refresh` under the current scope would drop them"** — the 32
  orphan rows and their scope-exclusion (not in `PLACEMENT_TYPES`, not in the
  character families) are verified; the refresh drop-behaviour itself I did
  not exercise.
- **P22 "since 18:03:23Z"** — `ps` shows the start as 23:33:22 +0530 =
  18:03:22Z (one second off); no code consequence (the serving-code claim
  holds either way: no tracked code change post-dates the start).
- **P5/P16/P23/P26 plan-logic projections** (2A serving-channel choice, 2C
  reduction, 2-prep gate outcome "B2 green, B4 green, A-group still red", 4C
  re-anchor) — accepted as design; their load-bearing mechanism claims
  (`context.py:380` floor-off, `facts.py:1077` plain-name lookup,
  `hybrid.py:213-225` prepend, `rank_subjects` top-1 = Hana Kurusu) are
  verified, but the projected outcomes land when the phases do.
- **P27 "1,748"** — by construction unverifiable until the `meaning` table
  exists (the live store has no `meaning` table); flagged for recomputation,
  as the item itself requires.

## Notes for the chairman (max 5 lines)

1. **Oracle scoring stands.** All 18 verdicts reproduce independently under
   two text variants (runner-text; full text with relation names/quotes/era);
   the 14/18 and the category split (outcome 0/4, state 2/4, timeline 2/3,
   cross-page 1/1, personality 4/4, equipment 1/1, quotes 1/1) are exact; the
   oracle sha256 matches the published `a788fa29…`.
2. **Both surprises are real and mechanistically explained:** B1 PASS — its GT
   ("…unseal Satoru Gojo") lives on the Angel page and the qa beam served that
   beat (score 0.1015, beat 8 of 8, no floor rows); B4 FAIL — the 30-fact cap
   over the per-participant concatenation gives Gojo (4th participant) only
   5 of 20 facts, cutting `class`/Grade (his 15th); B2 FAIL — Geto is 7th and
   gets zero facts. P23's subject-lead fix resolves both; P25's anchor warning
   is confirmed by execution (`rank_subjects` top-1 = "Hana Kurusu" on both
   queries).
3. **No verdict depends on the runner's relation omissions (P3)** — fix the
   runner before reuse; 1A's verdicts stand as scored.
4. **Blocking-record items for the Phase-1 commit:** P18 (promote the /tmp
   evidence + pin sha256s), P19 (2B and Phase-5 `deviation_reasons.md`
   entries), P21 (exact commit list; exclude `reports/index.md`), plus the
   text corrections P1/P6/NR1 and the 1B record fixes P8 (3/100), P9
   (38–40 band), P10 (93/4), P11 (2,748), P13 (117,251).
5. **Plan-side entries:** P5 (record the full Phase-5 closure), P7 as amended
   (714 of 2,748, not "all"; 61% is the Summary slice), P15 as amended
   (cross-ref P23), P17 (re-freeze prompt v1 post-widening), P24 (alias data
   ticket), P26 (re-anchor 4C), P27 (1,748 unverified — recompute at `meaning`
   creation).