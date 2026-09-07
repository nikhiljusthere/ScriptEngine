# Step 4 — demand-weighted relevance pilot (fast signal before the 545 census)

Date 2026-09-07. The next-move council's step 4: run the relevance gate on a
demand-weighted subset (heavy Personality/History, light Trivia) as the fast
signal before the full 545 (dimension, page) census (step 5). Retrieval-only,
no 27B — the same constraint as the whole sequence.

## Method

- **Population:** 218 character + character_synopsis pages → 545 existing
  (dimension, page) pairs (Personality 138, Appearance 145, Overview 41,
  Trivia 121, History 100) — the counts match the Phase 5 closure table exactly.
- **Sample:** 66 pairs, demand-weighted (seed 20260907): Personality 24,
  History 20, Appearance 12, Overview 6, Trivia 4.
- **Path:** the faithful in-process auto bundle (`route` → `build_context`, the
  same code the `:8000 /context` endpoint runs), CPU (Qwen owns the GPU).
- **Gate signals** per pair (top beat of the bundle):
  - **reach (S1):** top beat is the page's own section for the dimension.
  - **sourced (S3):** S1 and the top beat carries a chapter/episode citation.
  - **cross-page:** the top beat is a *different* page than the target.

Artifacts: `pairs_545.json` (full census pool), `demand_pilot_sample.json`,
`demand_pilot_results.json` (66 rows, top-beat detail), log
`/tmp/opencode/demand_pilot.log` (wall 874s).

## The fast signal (nested-breadcrumb-corrected)

The first pass reported 12/66, but that was **contaminated by a gate
methodology bug**: a dimension section nested under a parent ("Abilities and
Powers / Overview", "Synopsis / History") was not matched by an exact
`breadcrumb == dimension` test, so a correct top beat read as a miss. Corrected
(the section is the *last* component of the breadcrumb path):

| dimension | reach (top is own section) | sourced | cross-page |
|-----------|:--:|:--:|:--:|
| Personality | 17/24 (71%) | 10/24 | 0/24 |
| Appearance  | 8/12  (67%) | 2/12  | 2/12  |
| Overview    | 1/6   (17%) | 1/6   | 2/6   |
| Trivia      | 0/4   (0%)  | 0/4   | 0/4   |
| History     | 6/20  (30%) | 4/20  | 11/20 |
| **total**   | **32/66 (48%)** | **17/66** | **15/66** |

Reading: the core profile dimensions retrieve their own section on top for the
majority of sampled characters (Personality 71%, Appearance 67%). History's 30%
is **depressed by finding F2 below** (a known, fixable cross-page gap), and the
Trivia (0/4) / Overview (1/6) samples are too small to trust — the census (step
5) will give those real numbers.

## Three findings

**F1 — gate methodology: match the section by its *last* breadcrumb component.**
Top-level sections carry `breadcrumb == "Personality"`, but the same-nested
section carries `"Abilities and Powers / Overview"` / `"Synopsis / History"`.
The gate (and the census) must treat the target section as present when the
last path component equals the dimension. This is a fix to *our* gate, not the
retriever.

**F2 — cross-page gap: a character's History lives only on the `/Synopsis`
subpage, and the qa door does not bridge to it.** For Kinji Hakari, Hanami,
Jogo, Jiro Awasaka, Mahito, Yuki Tsukumo the main page has **no** History
section; only the `<Name>/Synopsis` subpage does. A "what is the history of
X?" query resolves the character to the **main** page (surfacing its lead /
Abilities-Overview / Personality section) and never reaches the subpage's
History. This is the dominant History failure (8 of the 11 cross-page rows) and
is a genuine **retrieval** gap (class (a) cross-page confusion): the
subject-anchored walk (the R6 authored floor) fetches the subject's page but
not its `/Synopsis` subpage. Fixable in retrieval (extend the subject floor to
the character's `/Synopsis` subpage for the dimensions that live there), not by
rephrasing.

**F3 — citation coverage is a wiki property, not a resolver bug.** Every
"reached but unsourced" row (15 pairs) is a section whose **source wikitext
carries zero `{{Ref}}` markers** (verified: Wasuke Itadori Personality 0,
Dabura Karaba Appearance 0, Hanako Appearance 0, Hagane Daido Appearance 0).
The main cast's profile sections *are* chapter-cited (Gojo/Nanami/Megumi/Mai/
Mei Mei passed sourced); **minor characters' descriptive profile sections
simply are not** — the wiki cites their battle/narrative sections, not their
Personality/Appearance/Trivia. So the council's literal gate ("top beat … with
a valid chapter/episode citation") is **unmeetable** for most minor-character
profile pairs. This is the JJK analogue of the recorded corpus quirks (Berserk
cites cover art not instalments; One Piece per-instalment pages): the wiki's
citation shape, not the pipeline's.

## Genuine retrieval failures for the fix loop (class (a)/(b))

Beyond F2/F3, the pilot surfaced true cross-entity / ranking misses (top beat
is the wrong page or the wrong section on the right page):

- **Wrong entity:** Naobito Zenin→"Sorcerer Clans/Zenin Clan/Members",
  Kokichi Muta (Overview)→"Yuji Itadori/Synopsis", Dura Val Bobbidi Mechika→
  "Modulo Chapter 9", Yuko Ozawa→"Epilogue/Character in Order of Appearances",
  Nobara Kugisaki/Synopsis→"Hanako of the Toilet/History", Charles Bernard→
  "Chapter 181/Plot Details". (class (a) cross-page, or (b) if the character
  page has no such section.)
- **Right page, wrong section on top (ranking):** Kinji Hakari (Personality)→
  "Abilities and Powers / Overview", Toji Fushiguro (Overview)→"Personality",
  plus lead-on-top rows (Tadashi Okazaki, Shigeru Sonoda, Toshihisa Negi,
  Jiro Awasaka, Sotomura, Hagane Daido, Iori Hazenoki, Kiyotaka Ijichi,
  Chiharu Miyaguni, Rin Amai, Takeru). (class (a) retrievable-but-not-served.)

## The open decision (to the council)

F3 is a **gate-semantics** decision, not a retrieval fix: the wiki does not
cite most minor-character profile sections, so "top beat … with a valid
citation" cannot hold for them. How should the step-5 census gate treat a
reached-but-uncited section?
- **(A) reachability-only** for uncited sections — the gate is "top beat is the
  page's own section"; "sourced" becomes a reported coverage metric, not a pass
  criterion. Phase 5 "served" = the section is retrievable; citation coverage is
  reported per dimension (main cast high, minor low).
- **(B) keep the citation requirement** — a reached-but-uncited section is a
  *gap*; but closing it means adding citations to the wiki (out of scope for a
  retrieval-only pass), so it is recorded as a known corpus limitation.
- **(C) dimension-aware** — the narrative/claim-bearing dimensions (History, and
  any cited battle/abilities content) must be sourced; the descriptive profile
  dimensions (Personality/Appearance/Trivia/Overview) gate on reachability.

This decides the census pass criterion and, with it, whether Phase 5's
"closed on the data" becomes "earned." Recorded for the council (see
`COUNCIL_step4-gate-semantics.md`).

## Next move

1. Bake **F1** (last-component section match) and **F2** (subject floor extends
   to the character's `/Synopsis` subpage for the dimensions that live there)
   into the census tool.
2. Resolve **F3** via the council (gate semantics for uncited sections).
3. Run the step-5 census (all 545, demand-weighted) with the corrected gate;
   classify the genuine failures per `STEP2_FAILURE_TAXONOMY.md` and fix
   retrieval (never 27B, never rephrase to dodge).