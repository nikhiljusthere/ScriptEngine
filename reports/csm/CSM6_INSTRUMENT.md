# CSM-6 instrument — master receipt (CSM Wave-2, sub-1)

Worker: CSM Wave-2 pair, sub-1 (fork-context worker). Run 2026-09-09,
zero-GPU (no model run, no `:8000`, no pytest/eval/span-recall/build_context;
every shell <15 s). JJK-100% invariant held: JJK baselines read-only, CSM
work in CSM-centric files only. No git, no subagents. Raw receipts inline.

## 1. Tool parameterization (`--series`) — done, JJK byte-identical

- `tools/census_dimensions.py`: `_census_paths(series)` — jjk keeps its
  legacy `reports/comprehension/census_3b_dimensions.json` /
  `census_3b_results.jsonl`; other series read/write `reports/<series>/
  census_dimensions_<series>.json` + `_results.jsonl`. `--series` flag
  (default jjk).
- `tools/placement_audit.py`: `--series` (default jjk) → per-series output
  `placement_audit_3d.json` (legacy) / `placement_audit_<series>.json`.
- `tools/census_doors.py`: `_set_paths(series)` (per-series frozen sets),
  `_set_meta` + `_write_set`/`_read_set` (JJK legacy files stay bare lists,
  byte-identical; non-legacy sets are `{meta, items}` with seed + revid
  stamp), `_degree_ranked` (graph-degree protagonists for corpora without
  the JJK campaign mains), roster shortfall fill + narrative grid guard
  (corpus property: freeze what the wiki declares, print the shortfall —
  JJK's exact-100 fills never fire the branches), `run()` per-series
  results path + dynamic total.
- **JJK-100% proof**: regenerating both JJK door sets to temp and hashing
  against the frozen files → **byte-identical (True/True)**; path
  resolution dry-checked for jjk + csm; the six JJK baseline files' shas
  are unchanged after all runs (`sha256sum -c` OK).
- **`placement_audit --series csm` run**: bar MET, vacuous — 0 event groups
  (CSM's `events` table is empty, Phase-2 territory); output
  `reports/csm/placement_audit_csm.json` (0.15 s, model-free SQL).

## 2. Dimension map — `reports/csm/dimension_map_csm.md`

Regenerated from CSM's own sections (222,761 words of character prose):
per-character arc narrative 112,628w/471, chapter/episode summaries
90,421w/243, Personality 22,322, Trivia 18,680, the ability vocabulary
23,205 (Abilities + Devil/Hybrid/Supernatural Powers + Skillset), History
5,417, Devil Contracts 2,555, Appearance 7,179, Physical Prowess 2,570,
Etymology 1,119, Overview 1,343, Human Form 907. Extracted today: events 0,
meaning 0 (Phase 2), abilities 376 rows/75 chars, rosters 11/20 declared.
Outcomes stays unmapped (CSM has 0 battle pages, no outcome-shaped fact
keys — verified). State-over-time: CSM mains carry 0-word saga-section
shells (the JJK interval-facts gap, on CSM); `series/csm/overrides.yaml`
declares no `extra_facts` yet. Three-must-cover rows (state/outcomes/
causality) carry CSM-specific consumers + failing-test acceptances.

## 3. Eight-verb sample — `reports/csm/eight_verb_sample_csm.md`

Seed 20260909, 100 sentences from the 243 chapter/episode `Summary`
sections (90,421w, 4,330 sentences ≥20 chars, engine splitter), read and
classified, no model. **24/100 covered; 76% of the slice cannot be held**
by the live set (fought 9, arrived 7, killed 5, departed 3; saved/met/
sealed/betrayed/awakened 0 — note the live set is 9 verbs: JJK COUNCIL_1
widened it with `met`). 69/76 uncovered are pure description (by design);
no recurring true eventive gap (JJK's `met/encountered` did not transfer:
0 first-contact events in this mid-series slice). Band 22–26/100.

## 4. Frozen census sets (seeded, stamped, fresh from CSM)

- **(a) 100+100 door sets** (`census_doors --regen` logic, run model-free —
  the *run* is the orchestrator's one-copy CUDA window; the freeze is
  structural): `reports/csm/census_roster_100_csm.json` = **11** (corpus
  property: CSM declares 11 member-rosters, shortfall frozen not padded;
  stamped meta: seed 42, `revids` 19 pinned pages, `documents_revid_max` 0)
  + `reports/csm/census_narrative_100_csm.json` = **100** (60 character +
  16 arc + 24 char-arc; the main tier is CSM's own degree-ranked
  protagonists — Denji, Devil, Makima, Pochita, Aki …).
- **(b) Dimension census**: `reports/csm/census_dimensions_csm.json` =
  **60 questions, 6 schedulable dimensions × 10** (arc-narrative,
  state-over-time, abilities, personality, appearance, causality — the
  JJK-shape item dict `{id,class,subject,q,expect[3],source}`), every one
  of the **180 expect terms verified verbatim in-store** (2 transcription
  typos caught + fixed on the verification pass).
- **(c) `d4_open50_csm.json`** (wave A): intact, 50 items, seed 20260909 —
  verified, not edited. `twenty_failures_csm.md` present (20 open rows).

## 5. T0 pilot — `reports/csm/t0_pilot_csm.json` + `T0_PILOT_CSM.md`

`cli page-sweep --series csm`: tier a **175/175 pages, 0 errors, 1,260
structured Qs**; tier b **0 pages** (CSM declares none of tier b's page
types — corpus property). **#1 emergence: 843 identity-field questions**
(status 171, gender 163, romaji 154, kanji 153, occupation 140, …) vs the
council's ~535 JJK-derived expectation — CSM is *richer* than expected.
**#2 survival: 843/843 (100%)** — every frozen answer item still sits
whole in the store. **Gap recorded, not patched:** 62 CSM infobox fact
keys are outside the engine's identity vocabulary, incl. the near-miss
spellings `anime_debut`/`manga_debut`/`japanese voice`/`english voice`;
full list in the frozen meta. Widening `IDENTITY_FIELDS` is an engine
change → council at the Phase-2 gate; the per-wiki key map is the
sanctioned Phase-1 alternative.

## 6. Cross-page fact census — `reports/csm/crosspage_census_csm.md`

SQL, <15 s: **10,889/11,261 edges (96.7%) cross documents** — `mentions`
8,586, the chapter/episode grid (next/previous/volume/chapters/arc),
infobox relations (affiliation, species, occupation, birthplace,
contracted devils/humans, …). `events` 0, `meaning` 0 (Phase-2 design).
**Verdict: green for Phase 1** (every cross-page fact the process serves
is present in the link/infobox layer); **no G-CSM-5 filed** — the empty
event/meaning layer is the scheduled Phase-2 target, and a numbered gap
only rides on a red dimension-census result (gate 5.4).

## Deferred to the orchestrator (by the unit's zero-GPU rule)

- The model-run of `census_dimensions --series csm` + `census_doors
  --series csm` (the green/red per-dimension + per-door results) —
  one-copy CUDA window (stop `:8000`, run, restart); the frozen inputs are
  all in place for it.
- 5.4 extraction decision + §9a closure loop (wave B, sub-2 + Unit 3).