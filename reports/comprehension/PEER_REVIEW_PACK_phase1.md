# PEER REVIEW PACK — Phase 1C gate (anonymized defect list)

The 1C gate (plan/flow.md) sits on two on-disk reports:
`reports/comprehension/PHASE1A_ORACLE.md` (18-item held-out oracle, 11/18 —
chair-corrected from a first-recorded 14/18, see "Chair corrections" below;
category split outcome 0/4, state 2/4, timeline 2/3, cross-page 1/1,
personality 4/4, equipment 1/1, quotes 1/1; Finding 3 = a new
subject-unaware fact-slice defect) and
`reports/comprehension/PHASE1B_VERB_COVERAGE.md` (100-sentence seeded sample
of the live JJK store's Summary sections; 39/100 covered by the closed
eight-verb set; 61% uncovered, of which 41 are description the set
deliberately refuses; the one recurring true eventive gap is
`met/encountered`). Five independent advisors produced the defect list below.
It is anonymized: no item names its source. The gate question: **does Phase 1
stand, and is 1C green for the chair to continue into Phase 2 without
pausing — and what scope/records enter the plan as a result?**

Standing context: Phase 0 committed as `94909d2` (branch
`character-scoped-questions`). The live store is `series/jjk/facts.db`
(read-only for reviewers). The :8000 API runs on CPU (Qwen owns the GPU).
The 24k `meaning` pass is at 1/4 preconditions green (retention only) and
must not run. `plan/ORACLE_v1.yaml` is frozen and never edited.

## Chair corrections (recorded at the 1C gate; COUNCIL_1.md carries the full ledger)

Figures in this pack were re-verified against the live store before being
recorded. Where the council record differs from a pack item, the record in
`COUNCIL_1.md` supersedes:

- **14/18 → 11/18** (pack heading, from R5 NR1): the 1A tally is 11 pass /
  7 fail, re-verified item-by-item against the raw console log; the
  per-category split above is unchanged.
- **P7**: the core point stands (1B is a slice, not the population; quote
  "61% of the Summary slice"). Placement-scope figures chair-verified: the
  extraction scope is 388 sections / 165,941 words and carries 714 of the
  2,748 placed events; chapter/episode docs carry 923; 32 are orphans.
- **P8**: 3/100 accepted (row 047 is the same event type). Chair
  corroboration: 112 extraction-family sections carry encounter wording
  (112 instances, lower bound); the pack's broader 3-word-set figure (163
  sections / 64 instances) is reviewer-measured and not re-verified.
- **P11**: "a `--refresh` under the current scope would drop them" corrected —
  verified: 0 of the 2,748 events sit outside `scope_plan('all')`, so a
  `--scope all` refresh drops nothing; under the default `placement` scope
  the 32 orphans (15 location / 12 organizations / 3 item / 2 technique)
  persist as dead weight, not dropped rows. Provenance is still to be
  determined before any refresh.
- **P15**: the fact-slice fix is P23, not P24 (cross-reference corrected in
  place above).
- **P26 / P27**: ruled in COUNCIL_1 — the 4C re-anchor is a pending owner
  decision (out of council authority, flow.md:78); the 1,748 pilot
  population is plan-side and must be recomputed when the `meaning` table is
  created (live store: 2,748 events, 2,594 with `arc_index NOT NULL`, 885
  in chapter/episode docs).

## Defects (P1–P27)

**P1. 1A report quote typo.** Finding 3 quotes `routed.why: "question about
'Suguru Gojo', a character"` for the Geto item; the raw bundle says
"Suguru Geto" (and for the Gojo item it is "Satoru Gojo"). Non-blocking;
correct the quote when the council record is written.

**P2. The R6 passage floor was inactive in this run.** Finding 3's design
statement "the qa path already anchors the subject's passages (the R6 recall
floor) — but not its facts" is true of the code (context.py:370-381 vs
385-393), but with `subject=None` the floor is off (`if subject else []`), so
B1's beat reached the bundle via the ranked beam, not via the floor. A reader
could misread the floor as having been active. Non-blocking; one-line
clarification in the record.

**P3. Runner audit-text bug.** The runner's `bundle_text` renders relation
edges as `source label target` using a nonexistent `label` key (qa relations
carry `relation`), so edge relation-names are dropped from the audited text.
No ground truth depends on a relation row; all 18 verdicts were re-scored
without effect. Fix the runner before any future oracle run reuses it.

**P4. A4 serves a similar-but-wrong outcome fact.** A4's bundle carries
`Sukuna vs. Jogo | Outcome = "Sukuna is victorious."` while the correct
battle's outcome is absent. The `contains` verdict is still correct (A4's
ground truth is absent), but a writer could quote the wrong battle's result.
Non-blocking for the gate; load-bearing for 2A's design: the outcome join
must bind the outcome to the *specific fight* (event level), not merely
surface battle infoboxes.

**P5. 1A plan-consequences are incomplete.** They remove ~42,500
(Personality) from the build list but not the full Phase-5 closure that
flow.md:236-243 authorises once E1–E4 pass (the phase "may not exist").
Record both: 42,500 per the 1C rule and Phase 5 closed in full per its own
gate.

**P6. 1A miscite.** "the Phase 4 personality extraction 'may not exist'
(flow.md:236)" — flow.md:236 is Phase 5's "may not exist"; personality
extraction is Phase 5 scope, not Phase 4's. Correct the citation.

**P7. The 1B corpus is a slice, not the population.** 363 Summary sections →
949 sentences is the densest plot slice but excludes `Plot Details` on the
same pages (~13,115 more sentences), character narrative sections (1,203),
and the 108-document placement scope (~171,716 words, where all 2,748 placed
events live). 61% is neither an upper nor a lower bound for the full scope.
Quote it as "61% of the Summary slice."

**P8. The met/encountered gap is 3/100, not 2/100.** Row 047 ("Nobara and
Akari encounter Haruta Shigemo on the way") is the same event type as 008
("make first contact") and 018 ("crosses paths with") but was bucketed
"fight-adjacent, closest: fought." Live corroboration: 163 sections in the
extraction families carry encounter/crosses-paths/first-contact wording
(64 sentence-level instances, lower bound). Correct the record to 3/100.

**P9. The classification rule is applied unevenly.** 073 ("the battle that
ensues proves to Jogo…") is covered=fought while 085 ("his allies watching
the fight know this situation…") is uncovered, though both contain a
stated conflict and both have epistemic main clauses. Under a
main-clause-governs reading both are uncovered (38/100); under the rule as
written 085 is covered (40/100). Record the 38–40/100 band and tighten the
rule wording ("the main clause's eventive content governs").

**P10. The keep-betrayed/awakened justification is miscited.** The report
justifies keeping both by citing "Gojo's Prison Realm is `sealed`" — a
`sealed` use is no evidence for `betrayed`/`awakened`. The actual evidence:
the live `events` table under `events-2026-09-05.2` has 93 `awakened` rows
and 4 `betrayed` rows. Rewrite the justification.

**P11. "2,594 events" is stale; 32 orphan rows sit outside both scope rules.**
Live `events` = 2,748 rows (2,594 is the `temporal=1` subset). 32 rows
(1.2%) sit in location/organizations/item/technique page types that are in
neither `PLACEMENT_TYPES` (events.py:59) nor the character families
(events.py:834-840), i.e. outside the current `scope_plan`. A `--refresh`
under the current scope would drop them — a latent derived-row-loss exposure.
Quote 2,748 in the record; determine the 32 orphans' provenance before any
`--refresh`.

**P12. "the same split the extractor sees" is an overclaim.** The extractor
reads section text in windows (`_windows`, events.py:1002), not per
sentence; `split_sentences` (chunker.py) is the *index*'s splitter. The
≥20-char unit is still the right one for the question asked; reword to "the
engine's own sentence splitter."

**P13. flow.md:243's "~106,000 words" is wrong twice over.** The plan's own
per-section list (42,533+14,180+16,731+15,887+11,595) sums to 100,926; the
live `sections.word_count` sums are Personality 42,533 / Appearance 14,180 /
Overview 18,357 / Trivia 25,012 / History 17,169 = 117,251 (the plan's
Overview/Trivia/History figures are stale). The record should carry the
live-verified number or note the staleness; do not record "~106,000."

**P14. E1–E4 evidence is Personality-only.** All four items are
`category: personality`; Appearance/Overview/Trivia/History have no oracle
items. The 1C rule justifies dropping Personality (~42,533); the other four
leave the build list by the gating condition (Phase 5 never opens), not by
section-specific evidence — the record must say so, and a future phase
needing one must bring its own oracle evidence.

**P15. 2A and the fact-slice defect are coupled; 2C is confounded.** 2A's
joined outcome lands as `facts` rows (98 `outcome` rows already exist; all
four A ground truths are in-store verbatim). If served via the
character-entity fact list, the subject-unaware slice (P-item, below) drops
them and 2C's A-group re-run fails for the wrong reason; the battle-page
prepend path (hybrid.py:213-225) is immune. Either 2A's spec states the
serving channel or the fact-slice fix (P23) becomes a 2C precondition.
Blocking for 2C, not for 1C.

**P16. 2C's F-group re-run is vacuous.** With 2B refuted (F1/F2 pass) there
is no F extraction, so the "F-group re-run" measures nothing. Reduce 2C to
"A-group shows 2A's change; F-group unchanged (already passing at 1A)."

**P17. The verb widening amends 24k-precondition 2.** Precondition 2 is
"frozen class spec + prompt v1 coupled to PROMPT_VERSION." The widening
edits the events prompt's verb rule list, so prompt v1 must be re-frozen
*post*-widening, against the widened set, with its own PROMPT_VERSION bump;
the cached 2,748 rows under `events-2026-09-05.2` stay untouched. The 24k
pass remains not-runnable (1/4 green).

**P18. 1A gate evidence lives only in /tmp.** Runner, console log and the 18
raw bundles (≈390K total) sit in `/tmp/oracle_run1a.py`,
`/tmp/oracle_1a_results.txt`, `/tmp/oracle_1a_bundles/`. /tmp on this
machine is not tmpfs (it survives reboots) but systemd-tmpfiles reaps it at
30 days, and the "never edited" oracle evidence is unenforceable outside
VCS. The repo already tracks raw gate output (`reports/comprehension/raw/`).
Promote runner + log + all 18 bundles to `reports/comprehension/raw/oracle_1a/`
and pin sha256s in the record. Blocking for the record, not for the gate.

**P19. The 2B halt is not logged where the plan requires.** The step
contract: "IF REFUTED: HALT. Log to `deviation_reasons.md` with the raw
output." F1/F2 PASS at 1A refutes 2B's premise, but
`plan/deviation_reasons.md` carries no 2B entry (and none for the Phase-5
premise refutation either). Per the standing rule, a halt that is not on
disk in the designated file "did not happen." Blocking for the record.

**P20. COUNCIL_1 must re-state the 24k precondition status.** COUNCIL_0's
ledger says 1/4 green (retention). Nothing in Phase 1 touched preconditions
2–4; the next record must re-state "1/4 green, pass does not run" to stay
self-contained (flow.md:96-97: "Record which of the four were green, with
evidence, in the phase's council report").

**P21. The commit list must be exact.** Phase-1 commit = PHASE1A_ORACLE.md,
PHASE1B_VERB_COVERAGE.md, COUNCIL_1.md, COUNCIL_HISTORY.md (append),
plan/deviation_reasons.md (P19 entries), and the promoted evidence (P18).
`reports/index.md` is tracked-modified but references untracked canon-run
dirs — exclude it (note it in COUNCIL_1). Never `git add -A`; no push.

**P22. 2C stale-server trap.** After Phase-2 code lands, the running :8000
(PID 94330, serving `94909d2` since 18:03:23Z) keeps serving pre-change
code; a 2C oracle re-run against it would silently measure the old code.
Before the 2C gate: restart :8000 on CPU, and record server-start > commit
in the 2C record (exactly as 1A did).

**P23. The fact-slice fix shape (new 2-prep sub-step, before 2A).** Two
serving-side changes, `hybrid.py` untouched: (1) `main.py` auto mode:
`subject = request.subject or routed.signals.get("subject")` passed into
`build_context` (qa scope for the first landing; the narrative no-hint floor
gap is a follow-up); (2) in the qa builder, resolve the subject via a shared
title→alias→node-name helper (the current fact lookup is a plain
`n.name` match with no alias resolution), lead the fact list with the
subject's own facts (per-subject cap ~24), fill the remainder from
`result.facts` excluding the subject's rows, total cap 30. Alternatives
rejected: larger caps (ad hoc; B2's subject sits 7th and can sit further),
per-entity round-robin (still misses Gojo's 15th fact), anchoring on
`rank_subjects()[0]` (P26). Gate = full 18-item oracle re-run (expect B4
green, B2 green, B1/B3/C2/C3/D1/E/F held, A1–A4 still red pending 2A, C1
red as expected) plus the standing gates.

**P24. The linker over-match is ingest data quality, not retrieval.** The
alias table carries `Hana Kurusu ← "sorcerer"`, `Sorcerer Clan ← "gojo"`,
and `Kenjaku ← "geto"`/`"pseudo-geto"` (Pseudo-Geto collides with the Geto
alias and tie-breaks ahead of Suguru Geto). After P23's fix no oracle item
depends on it. Defer as a data ticket: audit single-token generic aliases at
harvest; report same-alias collisions in `audit`. The `Grade` concept page
matching "grade" is legitimate recall — leave it.

**P25. Implementation hazard: `rank_subjects()[0]` is the wrong anchor.**
For both the Gojo and the Geto item, `rank_subjects` ranks "Hana Kurusu"
first (character page-type priority, then raw link order). An implementer
who anchors the fact floor on `rank_subjects` top-1 would serve Hana
Kurusu's 12 facts and "fix" nothing. The correct anchor is the router's
`signals["subject"]` inference (returned the right entity in both items).
State this in the 2-prep task spec.

**P26. The 4C gate premise goes stale.** 4C says "B1 and B2 must move."
After 1A, B1 is already green; after 2-prep, B2 is green too — so 4C's
"must move" gate would be vacuous and the B-group would no longer size the
state-over-time gap (it measures reachability of *static* state facts, not a
time index). Re-anchor 4C to: B-group holds (no regression) + the interval
state table is non-empty and cited by /context. Any true time-indexed-state
probe is a new oracle item (ORACLE_v2, council-approved) — ORACLE_v1 is
frozen and never edited. Apply at 4C, record at 1C.

**P27. The "1,748 chapter-anchored rows" pilot population is unverified.**
It is a plan-side figure; nothing in the live store equals it (no `meaning`
table yet; live: events 2,748, `arc_index` NOT NULL 2,594, events in
Chapter/Episode docs 885). The record should state its provenance and flag
recomputation when the `meaning` table is created; do not let it gate
anything on faith.