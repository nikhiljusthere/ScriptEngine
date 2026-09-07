# Step 5 — the 545 census

Generated 2026-09-07 from `tools/census_545.py` (pairs: `tools/census_545_pairs.json`, 545). Run on CUDA, in-process `route` + `build_context` — the same path the `:8000` `/context` endpoint uses. Re-run: `CENSUS_DEVICE=cuda python tools/census_545.py` (CPU default; `--device cuda` for the ~9-min fast path; resumable via `--out`).

**What a pair is.** One (character page × question dimension) asked as a natural question. A pair is *reached* when a beat on the target page whose breadcrumb carries the dimension as any component is in the served bundle. It is *sourced* when at least one such beat also carries a locator.

## Global counts

| class | n | % |
|---|---:|---:|
| reached | 258 | 47.3% |
| reached-uncited | 282 | 51.7% |
| not-reached | 5 | 0.9% |
| no-section | 0 | 0.0% |
| errors | 0 | 0.0% |
| **total** | **545** | |

**Reached at all: 540/545 (99.1%).** Retrieval-controlled misses: **5**. Figures reflect the post-a5e93c3 re-run (the Trivia-section fix): the two previously-not-reached cases (Kenjaku, Noritoshi Kamo) now resolve to reached-uncited, which is why not-reached fell 7 → 5 and reached-uncited rose 280 → 282.

## By tier

| tier | n | reached | reached-uncited | not-reached | sourceable % |
|---|---:|---:|---:|---:|---:|
| main-cast | 74 | 47 | 27 | 0 | 63.5% |
| minor | 471 | 211 | 255 | 5 | 44.8% |

## Per-dimension totals

| Dimension | n | reached | reached-uncited | not-reached | miss % | thin n | thin % |
|---|---|---|---|---|---|---|---|
| Appearance | 145 | 26 | 119 | 0 | 0.0 | 3 | 2.1 |
| History | 100 | 79 | 18 | 3 | 3.0 | 3 | 3.0 |
| Overview | 41 | 30 | 11 | 0 | 0.0 | 0 | 0.0 |
| Personality | 138 | 87 | 49 | 2 | 1.4 | 4 | 2.9 |
| Trivia | 121 | 36 | 85 | 0 | 0.0 | 13 | 10.7 |

## Not-reached pairs (5)

The retrieval-controlled misses — the target section exists but no beat reached it. `sub` distinguishes a wrong section on the right page from a bundle that landed on another page entirely.

| dimension | page | tier | sub | top doc | top section |
|---|---|---|---|---|---|
| History | Chiharu Miyaguni | minor | wrong-section | Chiharu Miyaguni | Chiharu Miyaguni |
| History | Mimiko Hasaba/Synopsis | minor | wrong-section | Mimiko Hasaba/Synopsis | Synopsis / Gojo's Past Arc |
| History | Nanako Hasaba/Synopsis | minor | cross-page | Nanako Hasaba | Nanako Hasaba |
| Personality | Phantom Cursed Spirit | minor | wrong-section | Phantom Cursed Spirit | Appearance |
| Personality | Sara Kozuki | minor | wrong-section | Sara Kozuki | Sara Kozuki |

By sub-class: `wrong-section` 3, `cross-page` 2.

## Follow-up (tracked)

**Two genuine retrieval faults**, both now **fixed** (the other five are thin
minor-profile pages that land on the page root or an adjacent section — a
depth/length limit, not a fixable miss). Both fixes are retrieval-only and gated.

1. **Trivia / Kenjaku** (was wrong-section). Root cause: in `_qa_context` the
   ranked beam is walked to budget exhaustion *before* the subject's floor, so a
   busy character's big Personality/Abilities sections fill the 6000-token
   budget and the target Trivia section (already ranked first in the floor by
   `_qrank`) is never reached. Fix: a **guarded floor-lead** — when the query
   points at exactly one of the subject's sections (its title strictly beats
   every other section on query-term overlap), that section's leading chunk is
   paid before the beam. The guard keeps the beam-first walk for neutral and
   cross-page questions, so B1's cross-page beats are protected.
2. **Trivia / Noritoshi Kamo (Ancestor)** (was cross-page). Root cause:
   `link_entities` strips parentheses from the query (`_WORD`), so the qualified
   alias `noritoshi kamo (ancestor)` never matches a generated candidate; the
   ancestor's `exact` flag stays 0 and the descendant (exact on `noritoshi
   kamo`) wins the `exact DESC` ordering. Fix: a `_QUALIFIED` regex mints a
   parenthetical-preserved candidate from "Name (Qualifier)" spans, so the
   qualified entity links exactly and its `exact` flag wins.

**Gates (all green after the fix):** `pytest tests/ -q` = 1,239 passed;
`eval --series jjk` = 31/31 (100%); main-cast census reprobe = 0 not-reached /
74 (unchanged from baseline). Both fault pairs now classify `reached-uncited`
(the section is reached; uncited because minor Trivia sections are not
chapter-cited — a corpus property). A full 545 re-run
(`CENSUS_DEVICE=cuda python tools/census_545.py`) refreshed the global
not-reached count 7 → 5.

