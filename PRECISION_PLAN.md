# Precision: getting enumeration answers from 33.5% to usable

## Context

`reports/2026-08-14-0822/REPORT.md` records 626/878 canon items (71.3% recall)
at **33.5% precision** over 85 closed-set questions. Recall is the number people
quote; precision is the one that decides whether the output is usable. "Every
technique of Garou" returns **70 members for 6 canon items** — all six are
there, buried in 64 wrong names. A script writer cannot use that, and no
improvement in recall will fix it: of the 46 questions already at 100% recall,
the 39 closed ones average **46.1% precision**.

Two decisions taken before planning:

- **Retrieval stays LLM-free.** Kind labels are computed at index time; no model
  in the query path. (The literature's strongest tool — a pointwise LLM verifier
  over each candidate — is therefore out of scope.)
- **Precision first**, accepting some recall loss. 5 right names in 6 beats 6
  right names in 70.

## What is actually wrong

Mapped in the code, not inferred. `build_roster` (`retrieve/roster.py:402`)
produces:

```
members = (owned_by edges ∩ asked_kinds, validated)      # roster.py:893-945
        ∪ (section headings on the character's page)     # roster.py:1182-1301
        ∪ (LLM-extracted prose rows, kind-folded)        # roster.py:1009-1110
```

Five compounding causes:

1. **Two of three sources are unvalidated by design.** `roster.py:1069-1080`
   states it: extracted rows skip `validate_member` because its decisive test
   asks whether a page's fields name this character as a user, and those rows
   exist precisely because no page does. `_section_roster` never calls it
   either. Their only filters are an exact-match `ability_stopwords` list, a
   `len(name.split()) <= 5` heuristic, and a template-frequency drop.
2. **Kind can never separate abilities.** `roster.py:2152-2153` returns "no
   disagreement" whenever both types are in `ABILITY_TYPES`
   (`technique, transformation, power_up, fusion`). A technique inside a set of
   *forms* is unrejectable. This is deliberate — `test_roster_validation.py:312`
   asserts it — because a page reading `technique` vs `transformation` depends
   on whether an editor filled a `Class` field.
3. **`confidence` describes the set's label, not its members**, and on the union
   path it is inherited from the ownership half alone (`roster.py:516-518`).
   That is why `exact` measures 29.8% precision across 19 questions while
   `declared` measures **87.3%** across 9.
4. **No per-member score exists.** `Member` (`roster.py:237`) has no score
   field. Ordering is alphabetical. The only limiter is the token budget walking
   the list in insertion order (`api/context.py:242-251`), and the eval passes
   `token_budget: 60000`, so it never binds.
5. **Nothing can detect over-inclusion.** `harness._evaluate_roster:237` checks
   `len(members) >= expect_min_members` — a floor, never a ceiling. There is no
   `expect_max_members` in the repo and exactly one upper-bound assertion
   anywhere (`test_character_scoped.py:147`, `len(names) < 80`).

**The junk is highly structured**, which is what makes this tractable. Sampled
from the run: off-kind entries (Zoro's swords answering a question about sword
*styles*, basis literally `"Roronoa Zoro's item, technique"`), generic traits
("Superhuman Physical Prowess", "Enhanced Senses", "Indomitable Will"),
non-canon game entries (Cell X, Vegecell, Perfect 16), section-header artifacts
("Current Swords", "Former Swords"), and other characters' techniques
("Tanktop Blow" under Garou).

**The decisive finding.** `abilities.section` records the breadcrumb each row
was read from, and it separates the classes almost perfectly:

```
Saitama — 43 extracted rows
  Abilities and Powers / Fighting Style      14 rows, all real named techniques
  Abilities and Powers / Physical Abilities  traits + 2 real
  Abilities and Powers / Miscellaneous       traits only
  Abilities and Powers / Supernatural        traits only
  Saitama            (bare = lead-level)     10 rows, all generic traits
```

`series/opm/overrides.yaml:30-31` declares `ability_sections: {technique:
[Abilities and Powers]}` — the parent — while its own comment on line 28 says
the techniques live under `Abilities and Powers / Fighting Style`. Garou is
identical: his six canon fists sit under `.../Human/Fighting Style` among 67
rows.

Two signals were tested and **rejected**, which is why the obvious fixes are not
in this plan: cross-character frequency fails (real shared techniques like
`Cero` (9 holders), `Sonído` (8), `Resurrección` (6) look identical to traits
like `Enhanced Strength` (16)), and page-existence fails in both directions
(junk *with* pages: "Indomitable Will", "Regeneration", "Master Swordsman";
real techniques *without*: "Serious Punch", "Shunpo", "Bankai", "Two Sword
Style").

## Phase 0 — Make the measurement trustworthy first (blocking)

Optimising against a wrong target is worse than not optimising. Some measured
"junk" is correct:

- **Cell**: returns "Imperfect Form", "Semi-Perfect Form", "Perfect Form"; the
  bank says "Imperfect Cell", "Semi-Perfect Cell". Same entities, wiki naming —
  an **alias gap in `questions/db.json`**, scored as an engine error.
- **Saitama**: "Serious Squirt Gun", "Serious Headbutt", "Serious Spin",
  "Serious Whack-a-Mole" are genuine techniques the 7-item answer omits.

1. Audit every closed-set question whose precision is below 50%, comparing
   returned-but-unmatched names against the cited wiki page. Add missing
   aliases; add genuinely-canon omissions; retire nothing without a reason.
   **Delegate to `opencode`** (`opencode/deepseek-v4-flash-free`, `--auto`, one
   background run per series-pair) — it is high-volume wiki reading, the same
   shape as the work it already did well. Verify with the existing gate:
   re-fetch each cited page and confirm every item is in the raw wikitext
   (`tests/test_question_bank.py` + the citation check).
2. Re-run `canon-run` to get a corrected precision baseline. **Every number
   below is measured against that baseline, not against 33.5%.**
3. **Diagnose intruders, not just misses.** `diagnose_misses.py` buckets every
   missing item; there is no equivalent for the 882 returned-but-wrong ones, so
   precision work currently has no remediation table to aim at. Add the mirror:
   for each intruder, record which source vouched for it (ownership edge /
   heading / prose row / category), the section it came from, and whether it has
   a page. That table is what tells us, per fix, how many intruders it removes —
   and it is the difference between tuning blind and measuring.

   Note the arithmetic this has to respect: `precision = matched_gold_keys /
   len(members)` (`canon_gold.py:156`), where the denominator is **every**
   member returned. Garou's ceiling is 6/70 = 8.6% no matter what else changes.
   Precision moves only by returning fewer members.

## Phase 1 — Declare the right sections (data, not code; cheapest win)

3. For each series, find the leaf section that actually holds named abilities
   and declare it in `series/<name>/overrides.yaml → ability_sections`, replacing
   the parent. OPM becomes `technique: [Abilities and Powers / Fighting Style]`.
   Audit all 8 series the same way — **delegate the per-series section survey to
   `opencode`**, since it is mechanical reading of `abilities.section` values
   against each wiki's page layout.
4. Support **ranked** section preference, not a single leaf: canon item
   "Serious Punch" sits under `Physical Abilities`, so a strict Fighting-Style
   filter would drop it. Take the most specific declared section that yields
   members; fall back outward only when it yields none.
5. **Drop lead-level rows.** A row whose `section` is the bare page name (no
   `/`) came from the lead, not a heading, and in the sample is 100% generic
   traits. Series-agnostic, so this one belongs in code
   (`_extracted_roster`, `roster.py:1009`).
6. **Widen `ability_stopwords`.** It is consumed at both extraction time
   (`abilities.py:252`) and query time (`roster.py:1063`), so additions take
   effect on the next run with **no re-extraction**. Dragon Ball declares 5
   entries; One-Punch Man declares none — which is exactly why Saitama and Garou
   are the worst two offenders. The intruder table from step 3 supplies the
   candidates.
7. **Widen declared rosters.** `rosters: … members:` (`roster.py:174`) is the
   path measuring **87.3% precision** across 9 questions, and only Dragon Ball
   (Kais, Gods of Destruction) and HxH (Royal Guards) use it. Every question
   where the wiki keeps a clean, short list is a candidate. This is the single
   highest-precision mechanism already in the codebase.

## Phase 2 — REFUTED BY MEASUREMENT, 2026-08-15. Read this before building it.

The premise below — "a member backed by an ownership edge *and* a heading *and*
prose is near-certain; a single-source prose row is where the junk lives" — is
not true. Measured over all 1,568 members returned on closed sets in
`reports/2026-08-15-0935`:

| paths backing a member | canon | junk | precision |
|---:|---:|---:|---:|
| 0 | 41 | 12 | **77.4%** |
| 1 | 737 | 423 | 63.5% |
| 2 | 177 | 112 | 61.2% |
| 3 | 33 | 33 | **50.0%** |

**Corroboration correlates with being wrong**, and the reason is visible once
seen: a name recorded three ways is a prominent generic — `Bankai`, `Shikai`,
`Physical Abilities`, filed as a heading *and* an edge *and* prose because it is
structural. A specific named technique appears once, in prose. Building a score
on source count would have ranked the junk above the answers.

Nor does source *type* discriminate much: category 68.4%, prose 62.4%, ownership
edge 56.2%, heading 51.8%. Ownership is the path `validate_member` trusts, and
it is the second *worst*.

Three other candidate signals were tested and are flat:

- whether the member's page names the character back — 63.3% against 62.5%;
- name length — 63.3% (2–4 words) against 63.1% (one word);
- a leading grading word (`Enhanced`, `Immense`, `Master`) — 54.1% against 63.4%,
  the only one with any signal, over 61 members.

**What does discriminate is the section, which was the plan's original finding.**
Per `abilities.section` leaf: `Devil Powers` 100%, `Fighting Style` 92.7% over
124 members, `Cursed Technique` 79.2% — against `Powers & Abilities` 51.0%,
`Former Powers & Abilities` 37.0%, `Abilities` 32.1%. Named leaves are good,
generic containers are bad.

**But filtering on it is still not worth doing**, which is the part that decides
this phase. Dropping every prose row whose section leaf is a pure container:

    all characters      -147 junk, -131 canon   precision 63.0% -> 66.4%
    only where the character has a specific section available
                         -81 junk,  -82 canon   precision 63.0% -> 64.5%

Half of what it removes is the answer. The container sections genuinely hold
half the canon — Rukia's abilities, Ichigo's techniques, Byakuya's, Kenpachi's
are all filed under `Powers & Abilities` and nowhere better — so a filter that
empties them buys a percentage point by deleting real answers.

**Conclusion.** Do not build a per-member score on corroboration, and do not
filter prose rows by section globally. The remaining precision is not recoverable
by re-ranking what is already retrieved; it needs a different kind of evidence
than any path currently produces. The honest next lever is the one Phase 4
names — declaring the sets the wiki actually keeps, which measured 45.7% to
77.7% precision per shape on the questions where it was applied.

## Phase 2 (original, retained for the record) — Give every member a score

This phase is the roadmap's own stated destination. `docs/ROADMAP.md:80-83`
notes that phases 14, 15, 20 and 21 "are all variations on the same question —
'how much should a caller trust this set?' — and could eventually collapse into
one confidence model instead of four separate checks." A per-member score is
that model.

8. Add a `score` and a `sources` field to `Member` (`roster.py:237`). Each
   candidate records which of the three paths vouched for it. Corroboration is
   the signal the union currently throws away by deduplicating on lowercased
   name alone (`roster.py:1165-1171`): a member backed by an ownership edge
   *and* a heading *and* prose is near-certain; a single-source prose row is
   where the junk lives. Use `edges.confidence` (0.95 infobox vs 0.4 prose
   `mentions`) and `edges.provenance`, both already stored and unused for this.
9. **Recompute `confidence` from the members, not the set label.** Stop
   inheriting the ownership half's confidence onto a three-way union
   (`roster.py:516-518`). A set whose members are mostly single-source is
   `partial` regardless of how the set was found. This alone fixes the
   `exact` = 29.8% precision lie.
10. Emit the score per member in the API bundle so `canon-run` can measure a
    precision/recall curve against a threshold, rather than guessing one. Choose
    the threshold from that curve, and record it in the report. Two constraints
    to preserve: `apply_constraints` deliberately never empties a non-empty set
    (`roster.py:2222-2228`, asserted at `test_roster_validation.py:429`), so a
    threshold must degrade to "best N" rather than to nothing; and the API's
    per-member budget loop (`api/context.py:242-251`) currently truncates in
    insertion order — once members are scored it should truncate by score, which
    makes the default `token_budget=6000` behave sanely instead of keeping an
    arbitrary prefix.

## Phase 3 — Use the kind label that already exists

11. `semantics.semantic_type` is written at index time by `ingest/classify.py`
    and **retrieval never reads it** — `ontology.semantic_type()`
    (`semantics.py:169`) computes from `page_type` + infobox `Class` only; the
    stored label is consulted solely inside `validate_member`'s race branch
    (`roster.py:1869-1900`), and only ever to reject. Read it as an additional
    kind source. Free lever alongside it: the `semantic_types:` override key
    (page_type → semantic) is already read at `semantics.py:143` and **declared
    by no series**, so per-wiki kind mapping needs no code at all.
12. Then relax `roster.py:2152-2153` **only** where the stored label is present
    and confident — leaving the fallback intact so the behaviour
    `test_roster_validation.py:312` asserts still holds when there is no label.
    This is what lets a technique be rejected from a set of forms without
    reintroducing the failure that rule was written to prevent.
13. Extend `classify.py` coverage to ability rows that have no page of their
    own, since `needs_classifying()` (`classify.py:124`) currently only visits
    ambiguous ability *pages* — and much of the junk has no page.
14. **Cost note before touching extraction.** `PROMPT_VERSION`
    (`abilities.py:56`) is a per-row cache key, so bumping it invalidates every
    stored extraction across **all eight series at once** — "minutes of local
    inference per wiki", and it needs LM Studio or Ollama up. Do the
    27%-of-misses extraction-gap fix as one deliberate pass, not incrementally.

## Phase 4 — Group membership (recovers 5 questions returning nothing)

15. Five questions return `basis='-'`, `n=0`, 44 canon items: Band of the Falcon
    (14), Tokyo Special Division 4 (14), reborn Band (10), Four Kings (4),
    beherit types. The engine resolves characters, not groups; the member list
    sits on the group's own page. `unlinked page` is 80 items (32%) and 40 of
    them are exactly this. Declaring each in `overrides.yaml → rosters` (with
    `members:` or `category:`) is the cheap route and reuses the 87.3% path.
16. The same work fixes a precision disaster: "Every Weapon Devil" resolved to
    `basis='Devils'` — the whole category — returning **88 members for 7 canon**.
17. **Fix the report's advice while here.** The generated remediation tells the
    reader to "declare the link" in `series/<name>/overrides.yaml` for every
    `unlinked page` item — but **no such key exists**. The schema has no
    `exclude:`, no page→subject link, and no current/former key; the only
    exclusion levers are `non_canon_works:`, `ability_stopwords:` and
    `prune_types:`. Either add the key or change the advice, because 80 items
    (32% of all misses) currently point at a fix that cannot be carried out.

## Phase 5 — Make precision un-rottable

18. Add `expect_max_members` to the roster gold schema and assert it in
    `harness._evaluate_roster` (`harness.py:219`), whose current `enough` check
    (`len(members) >= expect_min_members`) is a floor with no matching ceiling.
    Without one the regression suite cannot see this defect class at all, which
    is how it survived. Note CLAUDE.md:76-79 — `eval` is a regression suite, not
    a scoreboard: set the ceiling from what the wiki actually says, and never
    tune the retriever to make one question go green.
19. Add a precision floor to `canon-run`'s report and a test asserting the
    padded-roster list does not grow.

## Sequencing

Phase 0 is blocking — everything else is measured against its corrected
baseline, and its intruder table is what tells each later phase how many wrong
names it actually removed.

Phase 1 is data-only, needs no re-extraction and no restart, and targets the two
worst offenders directly; take it next and measure before writing any code.
Phases 2 and 3 are the durable engineering and depend on each other (the score
needs the kind label to be worth much). Phase 4 is independent and can run in
parallel — it is mostly `overrides.yaml` authoring. Phase 5 should land with
Phase 2, not after, or the next regression is invisible again.

Stop after any phase and the work still stands: each one is measurable on its
own against the corrected baseline.

## Division of labour

| | Claude | opencode + DeepSeek | Subagents |
|---|---|---|---|
| Root-cause tracing, scorer/confidence/kind-label code, group path | owns it | — | — |
| Bank alias/coverage audit (Phase 0), per-series section survey (Phase 1) | reviews | does it | — |
| Independent verification of each batch | owns it | — | — |
| Parallel code exploration when a phase opens a new area | — | — | `Explore` |

Nothing from `opencode` is accepted without the citation gate that already
caught two fabricated citations in the question bank.

## Verification

```powershell
python -m pytest tests/ -q                                  # 612 baseline, must not drop
python -m pytest tests/test_character_scoped.py tests/test_roster_validation.py -q
python -m scriptengine.cli canon-run --dry-run
python start_scriptengine.py                                # MUST restart: staleness guard
python -m scriptengine.cli canon-run --skip-eval
python -m scriptengine.cli eval --series jjk                # must stay 24/24 — proves no leak
```

**What good looks like.** Precision on closed sets moves from the Phase 0
corrected baseline toward 80%+, with recall not falling more than a few points;
`Every technique of Garou` returns something near 6 rather than 70; the five
`basis='-'` questions return members; no question reports `exact` while
returning three times its canon count; and `reports/index.md` shows the move
across two runs. A recall drop is acceptable and expected — it must be *stated*
in the report, not absorbed silently.

**Restart discipline.** Every phase here edits code under `scriptengine/`. The
API holds its code in memory; `canon-run` will refuse to run against a stale
server (verified — it fired correctly during this session's diagnosis fix).

---

## Measured corrections (2026-08-14, during Phase 0 execution)

Four things above are wrong, found by building the intruder table the plan asks
for and then measuring against it. The plan is otherwise unchanged; these are
corrections to its arithmetic, not a change of direction.

**1. "Drop lead-level rows" is worth 45 intruders, not 259.** The plan's rule —
a row whose `section` is the bare page name — is right. Reading it as "the
breadcrumb has no `/`" is not: breadcrumb depth is a property of the wiki, not
of the lead. Dragon Ball files ability prose under a single-segment `Abilities`,
so the depth test called all 26 of Cell's rows lead-level when none are. Against
the page title, the run has **45 lead rows (5% of intruders)**, not 259 (29%).
Guarded by `test_diagnose_intruders.py`.

**2. Phase 1 is not data-only.** `ability_sections` is read in exactly one place
under `retrieve/` — `roster.py:1208`, inside `_section_roster` — so it selects
*headings*. `_extracted_roster` never consults it, and **prose rows are 56% of
all intruders**. Its other reader is `ingest/abilities.py`, which uses it to
choose what to extract, so narrowing it there shrinks the *next* extraction
rather than filtering what is already stored. Acting on sections at query time
means a section filter inside `_extracted_roster`: code, and a server restart —
though still no re-extraction, since `abilities.section` is already stored.

**3. The section lever is worth 36.5% → 43.2%, not 80%.** Measured over the
closed sets where any canon item was found, keeping only the sections that hold
canon, at **unchanged recall**. The gain is real but concentrated: Garou
9%→25%, Killua 18%→45%, Gon 50%→100%, Kurapika 62%→100%, Ulquiorra 20%→50%.
**Dragon Ball gains nothing at all** — its breadcrumbs are single-segment, so
canon and junk share `Abilities`, and its junk is non-canon game forms (Cell X,
Vegecell, Perfect 16) that want `non_canon_works:`/`prune_types:` instead. Note
this was measured against the *uncorrected* bank and is therefore a floor:
several sections counted as holding junk are holding canon the bank omitted.

**4. Phase 0 is larger than "some measured junk is correct".** On
`Every Saitama technique`, 8 of the 9 intruders under
`Abilities and Powers / Fighting Style` are genuine `Killer Move: Serious
Series` moves, and a ninth (`Serious Sneeze`) sits under `Physical Abilities`.
One is a pure alias gap — the bank stores only the Viz name
`Serious Sideways Jumps`, so the wiki's own `Serious Side Hops` scores as an
error. Real precision on that question is ~35%, not the measured 14%.

Two things the plan does not say, worth knowing before Phase 1:

* **Dropping lead rows is not free.** Some canon items *are* in the lead —
  Guts, Griffith, Denji and Byakuya each have canon in a bare-page-name
  section. A blanket lead filter costs recall on berserk, csm and bleach.
* **31 of the 42 audited questions are `baseline: true`.** Correcting them
  changes the canon count of the only subset comparable with pre-migration
  runs. Accepted deliberately: leaving 31 of the 42 worst questions wrong to
  protect one historical percentage would defeat the audit. The alternative
  considered and rejected was reclassifying them `scope: core`, which preserves
  the comparison but pulls the worst questions out of the precision denominator
  — collapsing the signal the whole plan exists to measure. The report must
  state that the comparable subset moved.


---

# Outcome, 2026-08-16

The plan's target was 33.5% precision. Where it finished, and what actually
moved it — recorded because the causes were not the ones this document predicted.

| | 2026-08-14 | 2026-08-16 |
|---|---|---|
| canon recovered | 626/878 (71.3%) | **1242/1362 (91.2%)** |
| precision, closed sets | 33.5% | **60.0%** |
| questions at recall 0 | — | 2/160 |
| confident and wrong | — | 2 |

The bank grew from 85 closed-set questions to 160, so the two rows are not the
same measurement; the recall percentage is comparable and the absolute counts
are not.

## What moved it

Almost none of it was scoring or ranking. In order of size:

1. **A missing kind.** `ability` and `technique` are the same word to
   `_KIND_WORDS`, so "Every ability of Gojo" and "Every cursed technique of
   Yuta" asked for the same thing and the wiki's graded stat lines answered
   both. Adding `trait`, admitted by `widen_umbrella` on the umbrella words
   only, raised **recall and precision together** — +11 canon and +2.7pp — after
   this document had recorded that trade as unavoidable. It was not
   unavoidable; it was a distinction that did not exist yet.

2. **Three classification faults**, each making real pages unreachable:
   `fighting_style_box` folded to `event` (63 pages), `combat` folded to `event`
   on One Punch Man (48 pages), and `parent_tab` folded to `unknown` (271 pages,
   including Saitama and Garou). `event` is in `NEVER_MEMBERS`, so all of them
   were barred from membership entirely.

3. **Declarations that contradicted the bank.** Eight names sat in
   `ability_stopwords` while the gold called them canon. `Every ability of
   Roronoa Zoro` went 7/10 → 10/10 on their removal.

4. **A re-extraction** under a prompt that keeps the wiki's graded stat lines.
   The extraction-gap bucket had been stuck at 62–75 misses in *every* run.

5. **Scoping a question to what it names.** A question naming a battle was
   answered with the character's whole kit: 36.9% recall at 5.6% precision over
   41 such questions, 100%/100% once the battle page was read.

## What the ceiling is

Of 120 remaining misses, **20 are not on the wiki at all**. No model, extractor
or retriever returns what the corpus does not contain, so recall is capped at
**98.5%** without new sources. Several more "misses" are gold errors — items
taken from game pages, or a count transcribed from a single page rather than
from the series.

## Refuted here, do not rebuild

Alongside the Phase 2 refutations above:

- **Alias-aware scoring.** Accepting a member returned under any name the wiki's
  alias table calls the same page. Written, measured, reverted: `divine dog`
  maps to both `Divine Dogs` and `Divine Dog: Totality`, so it merged two
  distinct shikigami. A scorer that reports a better number by being wrong is
  worse than no change.
- **Raising `_TEMPLATE_HEADING_PAGES` from 10 to 70** — measured worse, already
  recorded above.
- **Trimming the level-0 infobox card** from extraction passages: it looks like
  waste and produces a third of berserk's and hxh's ability rows.

Added 2026-08-16, from tuning the extraction endpoint:

- **`--parallel` above 4 — *only while the GPU is power-capped*.** Measured on 48
  identical real windows at a 570 W cap: 4 slots gave 27.5 windows/min, 6 gave
  **26.4**. Re-measured after raising the limit to the card's 600 W maximum, the
  result **reversed**: 4 gave 32.6, 6 gave 34.1, 8 gave 35.2, and the real run
  went 33.8 → 52.0 rows/min. Recorded here as a refutation of the *general* rule,
  not of the number: check `clocks_throttle_reasons` before concluding a card is
  saturated, because a power cap looks exactly like compute saturation.
- **Disabling thinking from the request.** All four methods measured and all four
  ignored — a Jinja `enable_thinking` directive in the system message,
  `/no_think`, `chat_template_kwargs`, and the plain control were within 12
  reasoning tokens of each other. `enableThinking` is resolved when the model
  loads, so it can only be set by the per-model default config.
- **Lowering context to fix `Context size has been exceeded`.** The context is a
  pool shared by all slots and the error reports one slot's usage, so the logged
  number always looks too small to be the cause. The fix is more total context.
- **`lms load --estimate-only` for VRAM planning.** It reported 16.52 GiB for
  both 20,480 and 28,672 context; the real difference was 24,435 vs 25,913 MiB.
  It ignores KV growth — measure with `nvidia-smi` instead.

## Where the process is written down

`NEW_SERIES_PLAYBOOK.md` — the ordered checklist for a new wiki, with every trap
and its measured cost.
