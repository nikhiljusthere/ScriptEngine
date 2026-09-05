# COUNCIL — Phase 1C gate: 1A held-out oracle + 1B verb coverage

Date 2026-09-05. The gate from `plan/flow.md:171-178`: emit both Phase-1
reports, run the council, and continue into Phase 2 on green. The two
reports: `PHASE1A_ORACLE.md` (the 18-item held-out oracle,
`plan/ORACLE_v1.yaml`, run against the committed Phase-0 engine) and
`PHASE1B_VERB_COVERAGE.md` (100-sentence seeded sample of the live store's
Summary sections, measured against the eight-verb closed set). The open
questions the gate answers: *does Phase 1 stand as recorded, which scope and
records enter the plan as a result, and is the chair cleared to continue
into Phase 2 without pausing?*

Method: 5 advisors (independent, parallel) → anonymized defect list
(`PEER_REVIEW_PACK_phase1.md`, P1–P27) → 5 peer reviewers (independent,
parallel, each weighted to a failure mode: `council1/r1_oracle_scoring.md`,
`r2_verb_coverage.md`, `r3_process_plan.md`, `r4_serving_defect.md`,
`r5_process_safety.md`) → this synthesis. Every load-bearing claim below was
re-verified against the live store (probed via a read-only copy at
`/tmp/chair_probe/facts.db`, never the live store) and against the as-run
evidence before recording; where a reviewer's figure failed verification it
is struck and the correction carried in the ledger.

## The step under review

**1A — the oracle (11/18; the heading was first recorded 14/18 and is
chair-corrected here, R5 NR1).** PASS: B1, B3, C2, C3, D1, E1–E4, F1, F2.
FAIL: A1–A4, B2, B4, C1. Categories: outcome 0/4, state 2/4, timeline 2/3,
cross-page 1/1, personality 4/4, equipment 1/1, quotes 1/1. The two
surprises against the recorded `expect`: B1 passed (the cross-page state
fact is reachable through the plain ranked beam — no cross-page machinery
needed) and B4 failed (the reviewer who authored the item expected the grade
to be served; the serving path drops it).

**1B — verb coverage (39/100 of the Summary slice; contested band 38–40, P9).**
61% of the slice cannot be held by the eight verbs; 41 points are description
the set deliberately refuses; the only recurring true eventive gap outside
the set is `met/encountered` (3/100 after P8's re-bucketing of row 047).
Per the 1C rule, the verb set is widened before any further extraction.

**Findings carried into the plan** (full text in `PHASE1A_ORACLE.md`):
outcome is a real, in-store gap (A-group 0/4 — exactly 2A's measure); a new
subject-unaware fact-slice defect explains B4 (and B2's mechanism — Geto's
answer *is* in the store, unserved); E1–E4 pass, so Phase 5's own gate
closes it; F1/F2 pass, so 2B's premise is refuted by its own measure.

## Round 2 — the five peer reviewers

Verdicts: **PROCEED-WITH-CHANGES** (all five; the changes are the record
fixes and the scope rulings below, none of which re-interprets a fired
condition). Tally on P1–P27: r1 25 ACCEPT / 2 MODIFY / 2 new; r2 9 ACCEPT /
4 MODIFY / 14 unverified / 6 new; r3 22 ACCEPT / 5 MODIFY / 3 new; r4 2
ACCEPT / 1 MODIFY / 3 new; r5 26 ACCEPT / 1 MODIFY (P21, the commit list) /
3 new (NR1, NR2, NR3). Two of the new defects are blocking-record:
NR1 (the 14/18 headline is 11/18 — verified item-by-item against the raw
console log, `raw/oracle_1a/oracle_1a_results.txt`) and NR2 (the 1B
headline is contested and must carry the 38–40 band). Both are applied to
the reports in this commit.

## Verified-claims ledger (checked against code / the live store this run)

Oracle run and bundles (as-run evidence, sha256-pinned in "Evidence pins"
below; all 20 files verified against the R5 manifest):

- [x] **11/18** — the per-row table, the category table and the raw log agree
  (PASS B1, B3, C2, C3, D1, E1–E4, F1, F2; FAIL A1–A4, B2, B4, C1).
- [x] **B1 PASS**: GT "she ought to be found so that she may help them
  unseal Satoru Gojo" served at beat 8 of 8 on the `Angel` page,
  `Synopsis / Culling Game Arc` (score 0.1015). Zero 0.0-score floor rows in
  the bundle: the R6 passage floor was **inactive** (auto mode ran
  `build_context` with `subject=None`, `context.py:380`; the beat reached the
  bundle via the ranked beam, P2).
- [x] **B2 FAIL**: the bundle carries **zero** Geto facts; `routed.why` =
  "question about 'Suguru Geto', a character" (the report's first-recorded
  "Suguru Gojo" was a typo, P1 — corrected).
- [x] **B4 FAIL**: 30 served facts = `Grade` 5 + `Hana Kurusu` 12 +
  `Jujutsu Sorcerer` 8 + Gojo 5 (his first five in `f.id` order); the
  `class`/`Grade` = `Special Grade` row is Gojo's **15th of 20** facts
  (`facts.id` 8192; R4's "14th" is off by one) — ten rows past the flat
  `result.facts[:30]` cut (`context.py:392`), filled in participant link
  order.
- [x] **C2 PASS**: GT "Aoi cracks Hanami's hard shell with Playful Cloud"
  served at beat 8 of 8 on the `Kyoto Goodwill Event Arc` page,
  `Synopsis / Enemies Invade the Event` (score 0.5818, "Chapter 51,
  Episode 20") — the report's first-recorded "Todo page Usage beat" was
  wrong (NR1). The oracle's `source_page: Aoi Todo` is an authoring hint;
  the check is `contains`.
- [x] **A-group ground truths in-store**: 98 `outcome` rows live in
  `facts` (96 `Outcome` + 2 empty-label), and all four A ground truths are
  verbatim in `facts.value` ("Sukuna is victorious." ×7; "Nanami withdraws."
  ×1; "Uraume commits suicide." ×1; "The jujutsu sorcerers are
  victorious." ×1).
- [x] **Geto**: 19 facts; `occupation` = "Jujutsu Sorcerer (Former) Curse
  User" at position 13 — B2's answer exists in the store, unserved.

Live store (probed via copy; store read-only):

- [x] **`events`: 2,748 rows** (2,594 is the `temporal=1` =
  `arc_index NOT NULL` subset — P11's "2,594 events" headline was the
  subset, not the table; every row under `events-2026-09-05.2`).
- [x] **Placement split**: 714 events on placement docs (battle 387 /
  event 127 / story_arcs 200); 923 on chapter/episode docs (chapter 629 /
  episode 294), of which **885** have `arc_index NOT NULL` (P27's live
  figure checks out); **32 orphans** on page types in neither
  `PLACEMENT_TYPES` (`events.py:59`) nor the character families
  (`events.py:834-840`): location 15 / organizations 12 / item 3 /
  technique 2. **0 of the 2,748** sit outside `scope_plan('all')` — a
  `--scope all` refresh drops nothing; under the default `placement` scope
  the 32 persist as dead weight, not dropped rows (P11's "would drop them"
  corrected). Provenance of the 32 still to be determined before any
  refresh.
- [x] **Placement extraction scope** (`scope_plan(store, 'placement')`):
  **388 sections / 165,941 words**.
- [x] **The five section families** (`sections.word_count`, live):
  Personality 42,533 / Appearance 14,180 / Overview 18,357 / Trivia 25,012 /
  History 17,169 = **117,251**; the plan's own per-section list sums to
  **100,926** (42,533+14,180+16,731+15,887+11,595); flow.md:243's
  "~106,000" matches **neither** (P13). The record carries the live number.
- [x] **Live verb distribution** (2,748 rows): fought 1,200 / arrived 526 /
  killed 314 / saved 289 / departed 288 / **awakened 93 / sealed 34 /
  betrayed 4**. All 93 `awakened` + 4 `betrayed` rows were extracted by
  qwen3.8-27b-ninfer under `events-2026-09-05.2` on 2026-09-05 — the
  keep-justification for those two cells (P10's rewrite; the report's
  `sealed` example was a miscite).
- [x] **P8 corroboration (chair-measured)**: 112 extraction-family sections
  carry encounter wording (112 sentence-level instances; 111 "encounter" + 1
  "crosses paths", lower bound). The pack's broader 3-word-set figure (163
  sections / 64 instances) is reviewer-measured and not re-verified; both
  point the same way — the gap is corpus-real, not an artifact.
- [x] **Alias collisions**: 168 distinct colliding aliases overall; the
  single-token subset is 77 distinct (178 alias-node pairs); top-3 by node
  count: fight 9 / battle 8 / domain 8. (R2's "168 single-token" qualifier
  is wrong; 168 is the all-lengths count.)
- [x] **The `meaning` table is absent** from the live store; the 1,748
  chapter-anchored-row pilot population (P27) is plan-side and unverified —
  recompute when the table is created; it gates nothing on faith.
- [x] **`plan/ORACLE_v1.yaml` sha256**
  `a788fa29652a58152edf0f2ce16caea626db35d7e4463ec66176b5635a15935e` —
  matches the frozen premise; the file was not edited by this run.
- [x] **Server under test**: `:8000` PID 94330 on CPU
  (`SCRIPTENGINE_DEVICE=cpu`; Qwen PID 3664 owns the GPU, 24,670/32,607
  MiB), started 2026-09-05 23:33:22 +0530 = **18:03:22Z** — after commit
  `94909d2` (18:01:34Z), so the committed code served every item.
  (Report A's 18:03:23Z is process-start rounding, R5 NR3; this record
  cites 18:03:22Z.)

Struck or amended reviewer figures (the record supersedes): R1's "14/18
stands" (it is 11/18); R4's Gojo `class` position 14 (it is 15) and Geto
passage count 33 (it is 35); R2's "168 single-token aliases" (168 all, 77
single-token); P11's "a refresh would drop them" (0 dropped under `all`;
dead weight under `placement`); P8's 163/64 pair (chair-measured 112/112
adopted; the pair recorded as reviewer-measured).

## Amendments and rulings entering the plan

1. **2-prep (new sub-step, before 2A): the subject-anchored fact floor,
   capped.** (P23 + R4 NR1, both verified.) Two serving-side changes,
   `hybrid.py` untouched:
   (a) `main.py` auto mode: pass `request.subject or
   routed.signals.get("subject")` into `build_context` (qa scope for the
   first landing; the narrative no-hint floor gap is a follow-up);
   (b) in the qa builder, resolve the subject through a shared
   title→alias→node-name helper on `FactStore` (the current lookup is a
   plain `n.name` match with no alias resolution), **lead** the fact list
   with the subject's own facts (per-subject cap ~24), fill the remainder
   from `result.facts` excluding the subject's rows, total cap 30;
   (c) **a floor cap / beam-budget reservation**: the floor must not be
   allowed to consume the whole budget. Measured: the floor cost per beat
   is `estimate_tokens(passage.text) + 30` (`context.py:421`;
   `estimate_tokens` = `len(text)/3.6 + 1`, `context.py:63-64`); Gojo's
   floor is **42 level-2 passages (4,132 words) = 8,540 tokens** against
   the 6,000 default `token_budget` (`main.py:90`) — an uncapped floor
   would evict the ranked beam that carries B1's beat and regress B1
   green→red (R4 NR1's ~8.5k figure is confirmed to the token). Geto's
   floor (35 passages, 2,377 words) = 5,095. The cap (e.g. reserve ≥50%
   of the budget for the ranked beam) is part of the spec.
   Anchor: the router's `signals["subject"]` — never `rank_subjects()[0]`,
   which ranks "Hana Kurusu" first for both the Gojo and the Geto item
   (P25, verified live). Gate: the full 18-item oracle re-run (expect B4
   green, B2 green, B1/B3/C2/C3/D1/E/F held, A1–A4 still red pending 2A,
   C1 red as expected) plus the standing gates.
2. **2A — event-level outcome binding.** The 98 in-store `outcome` rows
   must be bound to the *specific fight* (event level), not surfaced from
   any battle infobox (P4: A4's bundle already carries a
   similar-but-wrong outcome, `Sukuna vs. Jogo`). Serving channel: the
   battle-page prepend path (`retrieve/hybrid.py:213-225`), which is
   immune to the subject-unaware slice — or 2-prep becomes a 2C
   precondition (P15). Either way the channel is stated in 2A's spec.
3. **Verb widening: `met` only.** `EVENTIVE_VERBS += {met}` in
   `events.py:43-54` (not `encountered`, not `defeated` — the latter is
   redundant with 2A's structured outcomes). The widening edits the events
   prompt's verb-rule list, so **prompt v1 is re-frozen post-widening**,
   against the widened set, with its own `PROMPT_VERSION` bump from
   `events-2026-09-05.2` (P17); the 2,748 cached rows stay untouched.
   `betrayed`/`awakened` stay on the live evidence (93/4 rows, above).
   Phase-2 order: widening first (its own commit, `events.py` has no diff
   on disk yet), then 2-prep, then 2A.
4. **2C reduced (P16).** With 2B refuted there is no F extraction: 2C =
   "A-group shows 2A's change; F-group unchanged (already passing at 1A)."
   Before the 2C gate: restart `:8000` on CPU and record server-start >
   commit in the 2C record, exactly as 1A did (P22 — the running server
   serves `94909d2` and would silently measure pre-change code).
5. **2B halts (recorded).** F1/F2 PASS at 1A refutes 2B's premise by its
   own measure; the 3,782 + 1,518 words leave the build list. Entry with
   raw evidence in `plan/deviation_reasons.md`.
6. **Phase 5 closes in full (recorded).** E1–E4 pass: Personality (42,533
   words) leaves the build list per the 1C rule; the other four families
   (74,718 live words) leave by the gating condition, not by
   section-specific evidence (P14); flow.md:243's "~106,000" is not
   recorded (plan list 100,926 / live 117,251, P13). Entry with raw
   evidence in `plan/deviation_reasons.md`.
7. **4C re-anchor: pending owner decision (P26).** After 1A + 2-prep,
   "B1 and B2 must move" (flow.md:226) is vacuous; the proposed re-anchor
   (B-group holds + the interval state table non-empty and cited by
   `/context`; time-indexed probes go to a council-approved ORACLE_v2 item)
   is out of council authority (flow.md:78 condition 7) and is recorded in
   `plan/deviation_reasons.md` as a pending decision, not an action.
8. **Deferred, not gate-blocking (P24).** The linker over-match (`Hana
   Kurusu ← "sorcerer"`, `Sorcerer Clan ← "gojo"`, `Kenjaku ← "geto"` /
   "pseudo-geto") is an ingest data-quality ticket: audit single-token
   generic aliases at harvest; report same-alias collisions in `audit`.
   After 2-prep no oracle item depends on it. The `Grade` concept recall
   is legitimate — left.
9. **P3 (runner audit-text bug) — post-hoc, separate file.** The promoted
   `oracle_run1a.py` is pinned as-run (sha256 below); the fixed runner goes
   to the repo as a separate file, noted here, so no ground truth is
   silently re-scored (none depended on relation rows).
10. **P11 follow-up.** Determine the 32 orphans' provenance before any
    `--refresh`.

## Evidence pins (P18 — the 1A gate evidence, promoted and pinned)

`reports/comprehension/raw/oracle_1a/` — 20 files (runner, console log, 18
bundles, ≈390K). Every file verified this run against the R5 manifest
(`council1/r5_process_safety.md:130-149`), `sha256sum -c`: 20/20 OK.

```
b42d1f4f584e88708fb6dfa3e8752c6f8efd3060ce27a5999072f88a2e5989fb  oracle_run1a.py
d273dc0124da799b82745ef07536bae029263ddb1f65548081219eb52fba9a4b  oracle_1a_results.txt
6e386eec6b283ac73309e6b258644b9f1d80984a680c00118350a9f0aff584cb  A1.json
ac114825bf5867e333c7f33f2587ea054b16e7573417c8192d84e03ac72887a1  A2.json
9a0c9281d531eb6b3d504e15b590cf543e9b2fffd1ed255ab97a8aef64f52250  A3.json
16dc0b506ab32ba6e360d42c3117368f060628dafc21359171a062e55ecc0661  A4.json
5a63041f97cac3fc838eb59c35cb5d0e17cd652db00e4962d99c817238ed7815  B1.json
d9aedff1c9920f9ef21c07ecbccfd0d745ddb87c64cbc256221581e3fbacf51c  B2.json
bb98a822d2017959e3a3316c702ef70ac9c9ccca4257308948081fe2ce006273  B3.json
1d66bccfecbe98ff93a35994413594e136d7623aa60e77ff9bf2873192b12310  B4.json
19c3ab7815917e4ddb9f0cc2d136be69322fc931eb2f3187ef3ab83ed51a79d7  C1.json
51cfa9fd2969c405de5167a83e6f5816f97aa9d3b7860c163fca7ea6143ee824  C2.json
25864505aad9cd6d7cac5dbbb307b33ecffe7253a77cd4b8158212e6b94cf18b  C3.json
40f3d9dfbe65a7778069547ee3b147480a16b333ccbd490e28c20b9caa53f46d  D1.json
cf41bf13cd84bfd0f2d45dd744474f1c876425084c08ec8db527df079a7c1501  E1.json
5a0a5cd1b1189b924b63e568002d4a5f2eeae101cbd4b7fe2f6c70d7f83ad6bf  E2.json
2ce66843c0256a9303d9f5f4ce3e95c57503778792821ca1f640a7d6c38da077  E3.json
7437cf8b1d2b4ce6bfad1ce7a08776e28fbb19c4f9012d3922d1b4c4fa30828b  E4.json
60bafa963b34f8c6d81591d0b31537fd08739add2725fbc4ea8754a6c94e9b7f  F1.json
5e05eab1bda323cabe7a06a627e8db4b06cd7a56f004facfffd09747fa0c72ef  F2.json
```

## The 24k `meaning` pass — precondition status (re-stated per P20)

1. **Retention — GREEN** (Phase 0C/0D, `94909d2`: 2,748/2,748 remapped,
   crash windows re-gated).
2. **Frozen class spec + prompt v1 + participant guard — NOT YET**, amended
   by ruling 3 above: prompt v1 is re-frozen *post*-widening against the
   widened set, with its own `PROMPT_VERSION` bump (P17).
3. **Pilot on the 1,748 chapter-anchored rows — NOT YET** (the population
   is plan-side, unverified; recompute when the `meaning` table exists,
   P27).
4. **Pilot accuracy at its floor — NOT YET** (no pilot).

**One of four green. The 24,000-sentence pass does not run.**

## Verdict (chairman)

**PROCEED-WITH-CHANGES: 1C is green; the chair continues into Phase 2
without pausing.** Phase 1 stands on the corrected record (11/18; 39/100
of the Summary slice, band 38–40). The changes: the record fixes applied in
this commit; the 2B halt and the Phase-5 closure logged in
`plan/deviation_reasons.md` with raw evidence; the Phase-2 scope as amended
above (2-prep with floor cap → `met` widening → 2A → reduced 2C). The
council repaired no halt and re-interpreted no fired condition (flow.md:56
— the 2B halt *fired* and was refused, which is the designed path).

## Commit (Phase 1 — stage these named paths only; no push)

Per R5 P21 (the pack's list, modified):

| path | status |
|------|--------|
| `reports/comprehension/PHASE1A_ORACLE.md` | new (with the 11/18 heading + record fixes) |
| `reports/comprehension/PHASE1B_VERB_COVERAGE.md` | new (with the 3/100 + 38–40 band, P10/P12/P7) |
| `reports/comprehension/PEER_REVIEW_PACK_phase1.md` | new (with the 11/18 header + chair-corrections block) |
| `reports/comprehension/COUNCIL_1.md` | new (this file) |
| `reports/comprehension/raw/oracle_1a/` (20 files) | new (P18; sha256s pinned above) |
| `reports/comprehension/COUNCIL_HISTORY.md` | modified (row #9 appended) |
| `plan/deviation_reasons.md` | modified (2B + Phase-5 entries + 4C pending-decision note) |

Excluded, with reasons: `reports/index.md` (tracked-modified on disk; its
diff adds five rows referencing untracked canon-run dirs — it belongs to a
later commit); `scriptengine/ingest/events.py` (no diff on disk — the verb
widening is Phase-2 work, its own commit); the ~700 other untracked paths
(canon-run dirs, `page-campaign/*`, `questions/*`, repo-root scratch).
Standing rule flow.md:279: named paths only — never `git add -A` — and no
push.

## Known, recorded (not blocking)

- The runner's relation-edge audit gap (P3) — fixed runner lands as a
  separate file; verdicts stand (no GT depends on a relation row).
- The 32 orphan events' provenance is undetermined (P11) — determine before
  any `--refresh`; 0 drop risk under `--scope all` is verified.
- The 4C re-anchor (P26) is a pending owner decision; the gate as written
  stands until the owner rules.
- The 1,748 pilot population (P27) is plan-side; it is recomputed, not
  trusted, when the `meaning` table is created.