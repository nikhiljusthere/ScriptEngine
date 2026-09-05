# Phase 1A — held-out oracle run (ORACLE_v1)

- Date: 2026-09-05 (IST)
- Oracle: `plan/ORACLE_v1.yaml`, sha256 `a788fa29652a58152edf0f2ce16caea626db35d7e4463ec66176b5635a15935e` — verified at runner start, matches the plan's premise. The file was not edited.
- Engine state: commit `94909d2` (Phase 0). `:8000` API on CPU (Qwen holds the GPU), server start `2026-09-05T18:03:23Z` — after the commit, so the committed code served every item.
- Runner: `/tmp/oracle_run1a.py`; raw bundles dumped to `/tmp/oracle_1a_bundles/` (18 files); console log `/tmp/oracle_1a_results.txt`.

## Method

Each item's `question` was POSTed to `/context` with `mode: "auto"` and nothing else
(default token budget, default top-k, **no `subject` hint** — the oracle tests
natural phrasing alone). Scoring followed the oracle's own `meta.scoring`:

- `contains` — the served bundle's text must contain `ground_truth`.
- `value` — a fact in the bundle must carry `ground_truth` as the value for the
  named subject (`source_page`).
- `section` — the bundle must return content whose breadcrumb matches
  `source_section` on `source_page`.
- `distinguishes` — the bundle must place the beat in `ground_truth` and must not
  carry `must_not_confuse_with`.

Bundle text = everything a writer could quote from the bundle: beat/member/
passage `text` fields, facts (`field: value`), relation edges. Whitespace was
normalised and citation markers stripped using the engine's own marker grammar
(`retrieve/citations.py:42`), as the oracle's scoring specifies. The routed door
is `bundle["routed"]["mode"]`.

## Results — 11/18

> Chair-corrected at the 1C gate: the headline was first recorded as 14/18; the
> tally is 11 pass / 7 fail, re-verified item-by-item against the raw console
> log (`raw/oracle_1a/oracle_1a_results.txt`; `council1/r5_process_safety.md`
> NR1, `COUNCIL_1.md` ledger). No verdict changed — the per-category split
> below is what the 1C gate reads.

| ID | category | question | expect | result | door | what was served |
|----|----------|----------|--------|--------|------|-----------------|
| A1 | outcome | How did Nanami's fight against Mahito end? | fail | **FAIL** ✓ | qa | Nanami/Mahito plot beats; no outcome field ("Nanami withdraws." absent) |
| A2 | outcome | Who won the fight between Kashimo and Sukuna? | fail | **FAIL** ✓ | qa | fight beats; "Sukuna is victorious." absent |
| A3 | outcome | How did the confrontation between Hakari and Uraume end? | fail | **FAIL** ✓ | qa | "Uraume de…" beats; "Uraume commits suicide." absent |
| A4 | outcome | What was the result of the final battle against Sukuna? | fail | **FAIL** ✓ | qa | Gojo/Sukuna usage + synopsis; "The jujutsu sorcerers are victorious." absent |
| B1 | state | Where is Gojo during the Culling Game, and can he act? | fail | **PASS** ✗ | qa | Angel page beat, `Synopsis / Culling Game Arc`: "…she ought to be found so that she may help them unseal Satoru Gojo" |
| B2 | state | Was Geto a jujutsu sorcerer or a curse user, and did that change? | fail | **FAIL** ✓ | qa | no Geto facts served (serving defect, see Finding 3) |
| B3 | state | Is Nobara Kugisaki alive at the end of the story? | pass | **PASS** ✓ | qa | fact `Status: Alive` for Nobara Kugisaki |
| B4 | state | What grade of sorcerer is Gojo? | pass | **FAIL** ✗ | qa | Gojo's fact set truncated by the flat 30-fact slice; `class: Special Grade` dropped (see Finding 3) |
| C1 | timeline | When do Todo and Yuji first fight each other? | fail | **FAIL** ✓ | qa | Shibuya-era beats only; "Kyoto Goodwill Event Arc" absent, "Shibuya Incident" present (unrelated Yuji-vs-Choso battle fact) |
| C2 | timeline | In which arc does Todo fight Hanami with Playful Cloud? | pass | **PASS** ✓ | qa | `Kyoto Goodwill Event Arc` page, `Synopsis / Enemies Invade the Event` beat (8 of 8, Ch. 51 / Ep. 20): "Aoi cracks Hanami's hard shell with Playful Cloud" |
| C3 | timeline | What time does Todo arrive in Shibuya? | pass | **PASS** ✓ | qa | "Todo and Arata originally arrived in Shibuya around 11:09 P.M." |
| D1 | cross-page | Why do the sorcerers need to find the Angel? | pass | **PASS** ✓ | qa | Angel page beat carries the Gojo-unsealing sentence (same beat as B1) |
| E1 | personality | How does Nanami behave and speak? | pass | **PASS** ✓ | qa | Nanami `Personality` beat verbatim |
| E2 | personality | How does Gojo treat his students compared to the sorcerer executives? | pass | **PASS** ✓ | qa | Gojo `Personality` beat: "He is usually laidback and playful with his students…" |
| E3 | personality | Why does Toge Inumaki speak the way he does? | pass | **PASS** ✓ | qa | Toge `Personality` beat: "Toge chooses not to speak in a conventional manner…" |
| E4 | personality | What motivates Maki Zenin? | pass | **PASS** ✓ | qa | Maki `Personality` beat: "Maki is a very headstrong and straightforward person…" |
| F1 | equipment | What equipment does Aoi Todo use? | pass | **PASS** ✓ | qa | Todo `Equipment` section served (Playful Cloud entry) |
| F2 | quotes | What are some things Aoi Todo has said? | pass | **PASS** ✓ | qa | Todo `Quotes` section served |

## Totals by category (never an aggregate alone)

| category | passed | items |
|----------|--------|-------|
| outcome | 0/4 | A1–A4 all fail, all expected to fail |
| state | 2/4 | B1 pass (surprise), B2 fail, B3 pass, B4 fail (surprise) |
| timeline | 2/3 | C1 fail (as expected), C2–C3 pass (as expected) |
| cross-page | 1/1 | D1 pass, as expected |
| personality | 4/4 | E1–E4 all pass, as expected |
| equipment | 1/1 | F1 pass, as expected |
| quotes | 1/1 | F2 pass, as expected |

## Surprises against the recorded `expect` (both directions)

1. **B1: expected fail, got PASS.** The engine is better than believed. The
   cross-page state fact (Gojo sealed; the pinning sentence lives on Angel's
   page) is reachable through the plain ranked beam — no cross-page machinery
   needed for this case.
2. **B4: expected pass, got FAIL.** The reviewer was wrong that the grade is
   served. The data exists in the live store (`facts` for Satoru Gojo:
   `class`/label `Grade` = `Special Grade`) but the serving path drops it —
   see Finding 3.

## Findings

1. **Outcome is a real gap (A1–A4, 0/4, all as expected).** The bundle carries
   the fight's prose but never the wiki's structured outcome. This is exactly
   what Phase 2A (battle-outcome join) exists for; the oracle's A-group is its
   direct measure.
2. **E1–E4 pass (4/4).** Personality is a **retrieval** problem, not an
   extraction one: the `Personality` sections already reach the writer in plain
   phrasing. Two plan consequences record together (1C rule + the phase's own
   gate): ~42,533 words (Personality) leave the build list per the 1C rule, and
   the **Phase 5** extraction "may not exist" and closes in full per its own gate
   (flow.md:236-243) — the other four section families (Appearance 14,180 /
   Overview 18,357 / Trivia 25,012 / History 17,169 words, live) leave by the
   gating condition, not by section-specific evidence.
3. **New serving defect: the qa fact path is subject-unaware (B4, and B2's
   mechanism).** Two compounding caps (an entity slice in `retrieve/hybrid.py`,
   a flat fact slice in `api/context.py`):
   - `entities[:5]` (line 201) takes the first five of however many entities
     `link_entities` matched. B4's question matched five entities
     (`Grade`, `Hana Kurusu`, `Jujutsu Sorcerer`, `Satoru Gojo`,
     `Sorcerer Clan`) and B2's matched seven, with the actual subject
     (`Suguru Geto`) seventh — outside the cut.
- the qa builder then slices the concatenated fact list flat
      (`result.facts[:30]`, `api/context.py:392`). The slice fills in
      participant link order, so B4's 30 slots went to `Grade` (5 facts),
      `Hana Kurusu` (12) and `Jujutsu Sorcerer` (8), leaving Gojo — the fourth
      of the five participants — exactly his first five facts in `f.id` order
      (`name`, `Kanji`, `Rōmaji`, `Alias`, `Species`). The `class`/`Grade` row
      (Gojo's 15th of 20, `facts.id` 8192) sat 10 rows past the cut and never
      reached the bundle.
- The router *did* identify the subject correctly in both cases
      (`routed.why: "question about 'Suguru Geto', a character"` /
      `"…'Satoru Gojo'…"`) and the qa path already anchors the subject's
      **passages** (the R6 recall floor, `context.py:370-381`) — but not its
      **facts**. In this run the floor was **inactive**: auto mode did not
      forward `routed.signals["subject"]` into `build_context`, so it ran with
      `subject=None` (`context.py:380`), and B1's beat reached the bundle via
      the ranked beam, not the floor. Consequence:
     B2's failure is *not* (only) the oracle's stated reason ("nothing in the
     store models what was TRUE of a character"): Geto's
     `occupation = Jujutsu Sorcerer (Former) Curse User` is in the live store
     and would have answered the item had it been served.
   - Side observation: the linker over-matches on generic words — `Grade`
     (the concept page) and an unexplained `Hana Kurusu` appear in both B4's
     and B2's participant lists. Flagged, not chased: the verdicts stand on the
     fact-slice cut alone.
4. **Timeline repeat-encounter gap stands (C1, as expected).** The first-clash
   question is answered entirely from Shibuya-era content; "Kyoto Goodwill
   Event Arc" never reaches the bundle and "Shibuya Incident" does (via an
   unrelated battle's `Arc` fact). C2–C3 show single-arc placement works; it is
   the *distinguishing* that is missing.
5. **F1/F2 pass.** Phase 2B's premise is "oracle F1/F2 failed at 1A (i.e.
   retrieval does not already serve these)". It is **refuted**: Equipment and
   Quotes sections are already served in plain phrasing. Per 2B's own rule
   ("IF REFUTED: no extraction owed — halt and record"), the 3,782 + 1,518 word
   extraction is not owed.

## Plan consequences (for the 1C council)

- 2A (battle outcomes) proceeds — the A-group is its gate.
- 2B (Equipment/Quotes extraction) is refuted by its own premise → halt and
  record; those words leave the build list alongside the 42,533 personality
  words, and Phase 5 closes in full per its own gate (Finding 2,
  flow.md:236-243).
- The fact-slice defect (Finding 3) is new scope: a small retrieval fix
  (subject-anchored facts, mirroring the R6 passage floor) that would likely
  turn B4 green and change B2's diagnosis from "store gap" to "served".
  Candidate for Phase 2 (mechanical, no model).
- The state category's true size after the fix: B1 reachable, B3/B4 served-or-
  servable; only time-indexed state (state-at-a-moment during an arc) remains
  unmodelled.