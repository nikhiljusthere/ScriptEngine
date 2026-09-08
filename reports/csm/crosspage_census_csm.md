# CSM cross-page fact census (SQL, <15 s, no model)

Run 2026-09-09 (CSM-6 instrument unit). Source: `series/csm/facts.db`
(edges 11,261; nodes→documents join). The census question: does CSM carry
cross-page facts that Phase 1 must serve but cannot?

## Measurement

- **10,889 of 11,261 edges (96.7%) cross documents** (source_doc ≠
  target_doc via the nodes→document_id join).
- Cross-document edges by relation:

| relation | cross-doc | overall |
|---|---:|---:|
| mentions | 8,586 | 8,946 |
| next / previous | 300 / 299 | 300 / 299 |
| arc | 243 | 247 |
| volume | 232 | 232 |
| manga_debut | 215 | 215 |
| affiliation | 203 | 204 |
| species | 121 | 121 |
| episode | 78 | 78 |
| relatives | 76 | 76 |
| occupation | 74 | 74 |
| birthplace | 59 | 59 |
| anime_debut | 57 | 57 |
| adapted from | 45 | 45 |
| contracted humans / contracted devils | 42 / 38 | 42 / 38 |
| notable_members | 37 | 37 |
| (15 more, ≤36 each) | | |

- `events` table: **0 rows**. `meaning` table: **0 rows** (Phase-2
  extraction territory per `plan/CSM_2PHASE_PLAN.md`).

## Reading

- **The cross-page link/infobox layer is fully present and already
  consumed**: the 10.9k cross-document edges are pre-resolved wikilinks
  (`mentions`) plus the wiki's own structural grid (chapter/episode
  `next`/`previous`/`volume`/`chapters`, `arc`/`saga`) and infobox-derived
  relations (`affiliation`, `species`, `occupation`, `birthplace`,
  `contracted devils/humans`, `manga_debut`…). These are exactly what the
  router, roster door and narrative door read — nothing in this layer is
  unreachable.
- **The event/meaning layer is empty by design, not by defect**: CSM's
  extraction (Phase 2) has not run, so `events`/`meaning` are 0. The §12
  dimension census (the model-run, orchestrator's one-copy window) is what
  decides whether a CSM extraction is owed per dimension; the placement
  audit is vacuous on 0 events (see `placement_audit_csm.json` — bar MET
  with 0 groups).

## Verdict

**Green for Phase 1**: every cross-page fact the Phase-1 process serves is
present in the link/infobox layer. **No G-CSM-5 filed**: the empty
event/meaning layer is the scheduled Phase-2 target, not a Phase-1 miss — a
numbered gap would only ride on a red dimension-census result (extraction
gate 5.4), when a build is actually owed and deferred to P6.