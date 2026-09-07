# Council 13 — Step-4 gate semantics (the reached-but-uncited section)

Date 2026-09-07. 5 advisors → 5 reviewers → chairman. Records the decision
raised by `STEP4_DEMAND_PILOT.md` (finding F3): how the step-5 census gate
should treat a section that retrieval reaches correctly but the wiki does not
cite. This sets the census pass criterion and whether Phase 5's "closed on the
data" becomes **earned**.

## The decision

A retrieval-only pilot (66 of 545 pairs) found that for **minor** characters
the descriptive profile sections (Personality/Appearance/Trivia) carry **zero**
`{{Ref}}` chapter/episode markers in the source wikitext — the wiki simply does
not cite them — while the **main cast's** same sections *are* chapter-cited. So
the gate's literal test ("top beat … with a valid chapter/episode citation") is
**unmeetable** for most minor profile pairs. This is a wiki citation-coverage
property (the JJK analogue of the recorded Berserk 0%-sourcing / One Piece
per-instalment quirks), not a retrieval bug. How should the census treat a
section that is *reached* but *uncited*?

- **(A) reachability-only** — pass on "reached the right section"; "sourced" is a
  reported coverage metric, not a pass criterion.
- **(B) keep the citation requirement** — a reached-but-uncited section is a
  *gap*; closing it means adding citations to the wiki (out of scope for a
  retrieval-only pass), so it is recorded as a corpus limitation.
- **(C) dimension-aware** — claim-bearing dimensions (History) must be sourced;
  descriptive dimensions gate on reachability.

The tension the council had to weigh: **serving an uncited section does not make
it usable in a *sourced* script** — the contract requires a line to be traceable
to a chapter, and an uncited descriptive trait has no chapter. So *reachability*
(can retrieval surface the section) and *sourceability* (can the writer cite it)
are two different things, owned by different parties (the engine vs the wiki).

## Context (compact)

- The engine serves **cited, ordered** context; the writing contract (VOICE_RULES)
  requires every line traceable to a chapter/episode. No 27B, ever.
- Phase 5: the 5 prose dimensions are **kept as preserved prose**, served as
  cited beats, deliberately **not** extracted as structured fields (a field is a
  lossy, citation-severing derivative). Closed "on the data" (span-recall 100%),
  but "served" was *un-proven* → the 545 gate earns it.
- Pilot (nested-breadcrumb-corrected): reach 32/66, sourced 17/66, cross-page
  15/66. Personality 71% / Appearance 67% reach; History 30% (depressed by the
  fixable F2 cross-page gap); Trivia 0/4 + Overview 1/6 (under-sampled).
- Demand tiers: Personality HIGH, History HIGH, Appearance MOD, Overview
  MOD-LOW, Trivia LOW.

## Round 1 — five advisors

- **A (Contrarian):** Rejects the trichotomy. (A) "launders" — re-closes an
  un-proven claim under a new label. (B) **conflates** corpus failure with
  retrieval failure (300+ permanent reds = noise; drowns the one real signal,
  History's fixable cross-page gap). (C) **misattributes** — uncited-ness is a
  *tier×corpus* property, not a *dimension* property (Gojo's Personality IS
  cited; a minor's is not). "Reached" is **undefined** for the cross-page
  /Synopsis case (exactly where History's 30% lives) — define it in writing
  before the 545 runs. n=4 Trivia / n=6 Overview is "a rumor with a label."
  Honest move: gate reachability (fail the cross-page misses, fix them),
  publish sourceability as a per-(dimension, tier) matrix that the writing
  contract consumes; uncited cells served as explicitly-uncited beats, never
  silently cited.
- **B (First Principles):** The gate spans **two owners** (reachability=engine,
  sourceability=wiki); grading a retrieval-only pass on the wiki's property is a
  noise generator. Pass = reachability only, with explicit reached /
  reached-uncited / no-section (no-section its own bucket). Sourceability is the
  **headline measured number** per dimension (reach% vs source%), a coverage
  metric not a footnote. Correct the Phase-5 claim to "served as beats; citation
  coverage is per-corpus/per-dimension, measured."
- **C (Expansionist):** Adopt (C) — but not as a compromise; it's the true model
  and the exercise is under-scoped. "Uncited" is a *signal* worth more than a
  pass rate → three deliverables: (1) the 545 reachability test proves the engine
  serves character profiles as an ordered, cited **service** (a product, not a
  check); (2) record "uncited" as a per-wiki `dimension_sourceability` class in
  `overrides.yaml` so gate outcomes are predictable *and* the writing contract
  can phrase "the profile describes X" instead of faking a chapter (improves
  script voice — F3 is a **voice rule**); (3) demand × sourceability = a routing
  map (premium cited lanes). File the census as that quadrant, "the artifact
  that's bigger than the gate."
- **D (Outsider):** The data has already decided; the options are postures toward
  the same fact. Three entangled things, only one is the gate's job: (1)
  retrieval (measurable, fixable), (2) citation coverage (corpus property;
  Berserk-0% precedent), (3) usability (downstream per-pair fact). (B) rigs the
  scoreboard red and buries History's 30% (a known, fixable cross-page bug) —
  that's "rephrase to dodge." So (A): pass=reached, 3-way signal, per-dimension
  sourceable-rate table as a **regenerated** live artifact. (C) is the trap:
  hand-drawing a claim-bearing-vs-descriptive line *before* the census — don't.
  Two conditions: fix the /Synopsis gap **before** the census; "no sourceable
  citation" must be a first-class state the writer layer acts on (safer than a
  model inventing a chapter).
- **E (Executor):** (C) as a **static two-row config**, not an auto-classifier.
  (B) is the trap (permanently red); (A) alone is too weak — **false green**: 15
  of 66 reach-but-can't-cite would EARNED when the writer still can't cite the
  line. Two rows: History = reached **AND** sourced (high demand, claim-bearing,
  gap is retrievable/fixable, main-cast history already cited);
  Personality/Appearance/Trivia/Overview = reach-only (sourced a reported
  metric). Don't fold battle/abilities; don't invent a claim-bearing detector.
  "Gate is green when each dimension meets its row; red means *we* missed, never
  the wiki."

## Round 2 — five reviewers (failure-mode lenses)

- **Logic:** (1) A uniform "History reached-AND-sourced" bar contradicts the
  tier axis — a **minor's** History is almost certainly uncited too, so it goes
  red *by the wiki's policy*, breaking "red means WE missed." The bar must be
  **tier-qualified**. (2) "Pass = reachability" has **no threshold** (all 545,
  or measured-and-reported?) — state the band or it's unfalsifiable. (3) The
  EARN target is silently downgraded: "explicitly-uncited beats" violate the
  "every line traceable" invariant *by design* — state the invariant is now
  "traceable OR explicitly-untagged," and define "reached" for cross-page
  History.
- **Devil's advocate:** (B) steelman — "reached" hands the writer a chapterless
  beat; a published table is a report, not a gate, so the EARNED claim is hollow
  for exactly the descriptives most often uncited. (C) steelman — History is the
  single most in-demand, claim-bearing dimension; "secondary bar" is
  underspecified, so the census can go green while History is served-but-uncited.
  **Cheaper recovery:** a **tier-scoped** gate — require sourceability where the
  wiki actually cites (main-cast, all dimensions), accept "reached, uncited,
  published" only for minor descriptives. Recovers (B)'s protection without
  conflating corpus with retrieval, and gives (C) a concrete primary bar.
- **Pragmatist:** v1 build order — (1) F1 matcher fix (last breadcrumb
  component) + regression test (hours); (2) F2: bridge the qa door to the
  character's /Synopsis subpage, **gated on a 20–30-question History probe +
  eval before the full census** (one day); (3) census harness: 545 question
  gen, the signals, per-dimension×tier sourceability table into COVERAGE.md via
  `coverage_report.py` (one day) — `citations.py`'s `Locator` already separates
  "no marker in wikitext" (empty) from "bare `(Chapter N)`, episode
  unresolvable", so reached-uncited is measurable **today, no new plumbing**;
  (4) full census detached CPU ~2h, poll. Critical path 2→4; 1∥3. **Cut from
  v1:** the `overrides.yaml` *expected-rates* config (drift; the measured table
  *is* the expectation), the quadrant routing map (presentation, v2), and a
  brand-new "History additionally earned" gate (reuse existing audit/span-recall
  coverage).
- **Edge-case:** (1) "Valid citation" checks the page/reference/chapter but not
  that the chapter's **subject** is this character — a Shibuya-chapter History
  beat is formally sourced but entity-mismatched → **add entity concordance**.
  (2) F2's /Synopsis bridge must be **conditional** (only when the main page
  lacks the section), else main-cast History gets double-served. (3) F1
  contaminates "no-section" — a nested section under a different breadcrumb tail
  misfires as absent; split "truly absent" vs "matcher miss" post-F1. (4) Thin
  cells (n<5): report the **count**, not a rate (CI on n=4 is ±50). (5) A
  section-mismatched beat can be *cited* and false-pass if you only check
  "has a citation" — "wrong section" is its own signal, independent of citation.
  (6) A 100%-uncited cell: rank risk = demand × (1 − sourceability); low-demand +
  zero-sourceable → **close via acceptance**, not repair.
- **Clarity:** "Reached" must be one precise, reproducible definition: bundle
  holds ≥1 beat with `doc_title == canonical page` (facts.db) **AND** the beat's
  breadcrumb's **last component ∈ the dimension's alias set** (alias sets in
  `overrides.yaml`); fixed template + top-k ⇒ the count is identical on two runs.
  "no-section" = the page's section tree lacks the alias. Writer-facing uncited
  beat renders `sourced: none — uncited (no wiki marker)`, never a number;
  VOICE_RULES: uncited beats never carry episode numbers. EARNED is one yes/no:
  every pair ∈ {reached, reached-uncited, no-section, not-reached} with zero
  unexplained errors, every uncited output beat carries the marker, 100% of
  wiki-cited History beats resolve through `citations.py`.

## Verified claims (re-checked against code + corpus before recording)

- **`citations.py` distinguishes the two uncited states today** (no new
  plumbing): a section with no inline marker resolves to an empty `Locator`
  (`attribute` :248 → `parse_markers` :219 finds nothing → `locators()` :292
  returns `[]`), while a bare `(Chapter N)` keeps a truthy `Locator(chapter=N)`
  even when the episode is unresolvable (`upgrade_markers` :229, "a marker the
  graph cannot complete is left exactly as the wiki wrote it"; `narrative.py:408`).
  So **reached-uncited** (no marker) is separable from **sourced-to-chapter**
  (bare marker, episode not adapted).
- **F2 / F3 verified in the pilot by reading source wikitext:** the 6 named
  characters (Kinji Hakari, Hanami, Jogo, Jiro Awasaka, Mahito, Yuki Tsukumo)
  have **no** History section on the main page — only the `/Synopsis` subpage;
  the "reached-but-unsourced" rows have `section_Ref = 0` (Wasuke Itadori,
  Dabura Karaba, Hanako of the Toilet, Hagane Daido), while main-cast sections
  passed sourced.
- **`overrides.yaml` is the home for per-wiki section alias sets** (the rule:
  per-wiki handling lives in `overrides.yaml`, not `.py`); `battle_aliases`
  already exists at the file's tail, so a `dimension_aliases` block is the
  natural fit. `citations.py` is series-agnostic (its docstring says so).

## VERDICT — tier-scoped gate

> **Earn reachability. Require sourcing where the wiki cites (the main cast).
> Publish — never fail, never silently cite, never fill by inference — where it
> doesn't (the minor tier).**

**(1) Reachability is the pass criterion** (the engine's job). Each existing
(dimension, character) pair is classified into exactly **one** of:
- `reached` — ∃ beat with `doc_title == canonical page` AND the beat's
  breadcrumb's **last component ∈ the dimension's alias set** (alias sets in
  `overrides.yaml`).
- `reached-uncited` — reached, but no beat for that section carries a non-empty
  locator (the source has no marker; the wiki's property).
- `not-reached` — the target section is present (or should be) but no top
  beat matches: sub-classify **cross-page** (top doc is another page),
  **wrong-section** (right page, different section on top), **lead-on-top**.
  This is the retrieval-controlled miss → the fix loop (class a/b).
- `no-section` — the page's section tree genuinely lacks the alias (the character
  has no such section); **excluded from the reach denominator**, not a failure.

The gate **PASSES** when `not-reached` is driven to ~0 (retrieval-controlled
misses fixed) and the count is **reproducible** (fixed question template +
fixed top-k ⇒ identical on two runs). A cited beat from the *wrong* section is
`not-reached` (caught by the section-identity check), **not** a pass — the
edge-case false-pass is closed.

**(2) Sourceability is tier-scoped** (the wiki's property).
- **Main-cast** characters: the gate **additionally requires** reached beats to
  be **sourced** (a non-empty locator) **with entity concordance** (the cited
  chapter is actually about *this* character, not just "some chapter exists" —
  spot-check the small main-cast History set against the character↔chapter graph
  edges). This is achievable (the wiki cites main-cast sections) and it is the
  contract-critical tier. This is the concrete primary bar that recovers option
  (C)'s protection.
- **Minor** characters: `reached-uncited` is the **accepted outcome**, not a
  failure. The wiki does not cite minor profile sections (a corpus property,
  same class as Berserk's 0%); it is **published** in COVERAGE.md as a
  per-dimension × per-tier sourceable-rate table (regenerated, not hand-stated;
  thin cells n<5 report the **count**, not a rate). Minor descriptives *and*
  minor History alike are published-not-failed — because **uncited-ness is a
  tier property, not a dimension property**.

**(3) History specifics.** Fix the **F2 /Synopsis cross-page gap before the
census** (the one real, fixable retrieval signal dragging History to 30%). The
bridge is **conditional** — extend the subject/anchored floor to the character's
`/Synopsis` subpage *only when the main page lacks the dimension section*, so a
main-cast character whose History sits on the main page is not double-served.
Reached, wiki-cited History beats must be sourced **with entity concordance**.

**(4) Uncited beats in the writer's output.** A `reached-uncited` beat renders
`sourced: none — uncited (no wiki marker)` and **never carries an episode
number** (VOICE_RULES). It stays **connective tissue, never a claim**. This is
the explicit invariant update: the contract's "every line traceable to a
chapter" becomes "**every *claiming* line traceable; *connective* lines may be
explicitly-uncited and are marked as such, never silently cited and never filled
by inference**." This is stated so the EARN target is not silently downgraded.

**EARNED for Phase 5 = one yes/no:**
1. Every existing pair is classified into exactly one of
   {reached, reached-uncited, no-section, not-reached}, with `not-reached` ≈ 0
   and the count reproducible across two runs.
2. 100% of **main-cast** reached beats are sourced (with entity concordance).
3. 100% of wiki-cited History beats resolve through `citations.py`.
4. Every `reached-uncited` beat in the output carries the explicit
   `sourced: none — uncited` marker (asserted by an output-shape test).

Unclosed cells (minor descriptives/History that are uncited) are recorded in
COVERAGE.md as **corpus limitations, not retrieval failures**.

## Cut from v1 (deferred, with reasons)

- **`overrides.yaml` expected-rates config** — deferred (drift risk; the
  *measured* table is the expectation). The **alias sets** (what title
  components count as each dimension) ARE load-bearing and go in
  `overrides.yaml` (per-wiki, per the repo rule).
- **Demand × sourceability quadrant routing map** — deferred to v2 (it's
  presentation + a voice-routing aid; the natural next artifact, but not part of
  the gate).
- **A new "History additionally earned" gate** — do not build; reuse existing
  audit/span-recall coverage + the main-cast sourced bar above.
- **Writing-contract consumption of the sourceability table** — v2; v1 just
  publishes it.

## Consequences for step 5 (the census)

1. **Bake F1 + F2 first.** F1 = the census tooling's section matcher uses the
   *last* breadcrumb component (nested "Abilities and Powers / Overview"). F2 =
   the conditional /Synopsis subject-floor bridge, **gated on a 20–30-question
   History probe (mixed tier) + `eval` before the full census** — all F2 tuning
   on the probe (each full re-run is ~2h CPU), full census only at the end.
2. **Census harness** emits the four signals + the per-dimension × per-tier
   sourceable-rate table into COVERAGE.md via `coverage_report.py` (no new
   plumbing — `citations.py` already separates the uncited states).
3. **Run** all 545, detached on CPU (~13s/query ⇒ ~2h), bounded polling.
4. **Pass** = `not-reached` ≈ 0 AND main-cast reached beats 100% sourced
   (entity-concordant) AND cited History beats 100% resolve. Minor uncited cells
   are **published, not failed** → Phase 5 is **earned with an explicit
   coverage note**, closed per-dimension.