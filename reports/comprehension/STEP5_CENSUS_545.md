# Step 5 — the 545 census

Generated 2026-09-07 from `tools/census_545.py` (pairs: `tools/census_545_pairs.json`, 545). Run on CUDA, in-process `route` + `build_context` — the same path the `:8000` `/context` endpoint uses. Re-run: `CENSUS_DEVICE=cuda python tools/census_545.py` (CPU default; `--device cuda` for the ~9-min fast path; resumable via `--out`).

**What a pair is.** One (character page × question dimension) asked as a natural question. A pair is *reached* when a beat on the target page whose breadcrumb carries the dimension as any component is in the served bundle. It is *sourced* when at least one such beat also carries a locator.

## Global counts

| class | n | % |
|---|---:|---:|
| reached | 258 | 47.3% |
| reached-uncited | 280 | 51.4% |
| not-reached | 7 | 1.3% |
| no-section | 0 | 0.0% |
| errors | 0 | 0.0% |
| **total** | **545** | |

**Reached at all: 538/545 (98.7%).** Retrieval-controlled misses: **7**.

## By tier

| tier | n | reached | reached-uncited | not-reached | sourceable % |
|---|---:|---:|---:|---:|---:|
| main-cast | 74 | 47 | 27 | 0 | 63.5% |
| minor | 471 | 211 | 253 | 7 | 44.8% |

## Sourceable % by dimension × tier

Sourceable % = reached-and-sourced ÷ total for that cell.

| dimension | tier | n | sourced | sourceable % | reached-uncited | not-reached |
|---|---|---:|---:|---:|---:|---:|
| Personality | main-cast | 15 | 14 | **93.3%** | 1 | 0 |
| Personality | minor | 123 | 73 | **59.3%** | 48 | 2 |
| Appearance | main-cast | 15 | 6 | **40.0%** | 9 | 0 |
| Appearance | minor | 130 | 20 | **15.4%** | 110 | 0 |
| Overview | main-cast | 14 | 10 | **71.4%** | 4 | 0 |
| Overview | minor | 27 | 20 | **74.1%** | 7 | 0 |
| Trivia | main-cast | 15 | 5 | **33.3%** | 10 | 0 |
| Trivia | minor | 106 | 31 | **29.2%** | 73 | 2 |
| History | main-cast | 15 | 12 | **80.0%** | 3 | 0 |
| History | minor | 85 | 67 | **78.8%** | 15 | 3 |

## Not-reached pairs (7)

The retrieval-controlled misses — the target section exists but no beat reached it. `sub` distinguishes a wrong section on the right page from a bundle that landed on another page entirely.

| dimension | page | tier | sub | top doc | top section |
|---|---|---|---|---|---|
| History | Chiharu Miyaguni | minor | wrong-section | Chiharu Miyaguni | Chiharu Miyaguni |
| History | Mimiko Hasaba/Synopsis | minor | wrong-section | Mimiko Hasaba/Synopsis | Synopsis / Gojo's Past Arc |
| History | Nanako Hasaba/Synopsis | minor | cross-page | Nanako Hasaba | Nanako Hasaba |
| Personality | Phantom Cursed Spirit | minor | wrong-section | Phantom Cursed Spirit | Appearance |
| Personality | Sara Kozuki | minor | wrong-section | Sara Kozuki | Sara Kozuki |
| Trivia | Kenjaku | minor | wrong-section | Kenjaku | Personality |
| Trivia | Noritoshi Kamo (Ancestor) | minor | cross-page | Noritoshi Kamo | Appearance |

By sub-class: `wrong-section` 5, `cross-page` 2.

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
(`CENSUS_DEVICE=cuda python tools/census_545.py`) refreshes the global
not-reached count 7 → 5.

