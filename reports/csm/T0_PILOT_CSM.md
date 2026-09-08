# T0 pilot — CSM (page_gen sweep, model-free)

Run 2026-09-09 (CSM-6 instrument unit). `cli page-sweep --series csm`
(model-free: structural generation + in-page verification only — no model,
no `:8000`, no GPU). Frozen set: `reports/csm/t0_pilot_csm.json` (843 items,
stamped; generated fresh from `series/csm`, never copied from JJK).

## Sweep

- **Tier a (characters): 175/175 pages, 0 errors, 1,260 structured Qs**
  (per-page batches under `questions/_csm_page_*` + the sweep report
  `questions/_csm_page_sweep_a.report.json`).
- **Tier b: 0 pages** — CSM declares no `character_synopsis` / `battle` /
  `technique` / `story_arcs` / `event` page types (corpus property; CSM's
  narrative surface is per-character arc sections, not battle pages).

## Pilot #1 — emergence

**843 identity-field questions generated** (vs the council's ~535
JJK-derived expectation — CSM's 175 character pages carry more filled
identity cells than the JJK expectation assumed, so emergence is *above*
the expectation, not below). Field mix: status 171, gender 163, romaji 154,
kanji 153, occupation 140, age 31, birthday 14, height 16, japanese 1.

**Vocabulary gap (recorded, not patched):** 62 CSM infobox fact keys sit
outside the engine's `IDENTITY_FIELDS` + `UNCHECKED_KEYS` vocabulary — the
notable near-miss spellings are CSM's `anime_debut` / `manga_debut` /
`japanese voice` / `english voice` vs the engine's `anime debut` / `debut` /
`voice` / `eng voice` (underscore vs space + CSM's own naming). Full list in
`t0_pilot_csm.json` `meta.unmatched_csm_infobox_keys` (species, birthplace,
aliases, affiliation, contracted devils, contracted humans, …). Extending
the shared vocabulary is an engine change → a council decision at the Phase-2
gate, not a Phase-1 patch; per-wiki mapping (the §9a per-wiki-override
preference) is the sanctioned alternative.

## Pilot #2 — verification survival of the frozen set

**843/843 (100%)**: every answer item of every frozen identity question
still sits whole in `series/csm/facts.db` (`facts.value` ∪ `sections.text`).
No stale content; the frozen set is current against the corpus (crawl
predates revid pinning — `documents.revid` all 0; the corpus pin is
`questions/csm.json` `revids`, 19 pages, stamped 2026-09-09).

## Reading

The T0 pilot says the CSM character layer is *richer* than the JJK-derived
expectation (843 vs 535 emergence) and fully current (100% survival). The
one structural finding is the infobox vocabulary gap (62 keys, four near-
miss spellings): when Phase 2 schedules the extraction, the council chooses
between widening `IDENTITY_FIELDS` (engine) and a CSM per-wiki key map
(`series/csm/overrides.yaml`).