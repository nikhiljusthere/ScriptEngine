# CSM override package — iteration 1 (unit-3 serial-fix closure, 2026-09-09)

Scope: the no-council per-wiki override track. Input: the 13 d5 line-miss rows
(fix class `R-4/R-2`: `csmd5-01..07` + the six `gate400-*` rows of
`reports/csm/miss_queue_csm_iter1.jsonl`), the 3 `R-6` narrative-door rows
(`door-nar-Introduction` / `door-nar-Bomb Girl` / `door-nar-International
Assassins`), and the `R-7` infobox-key override-support check
(`reports/csm/T0_PILOT_CSM.md` L48-50). Zero-GPU, model-free, read-only except
the two report files below; every command < 15 s; no git add/commit; no JJK
files touched.

## Method

For each d5 row: (a) is the target section in `series/csm/facts.db`
`sections`? (b) does the `chunks` table cover it (level-1 section chunk +
level-2 passages, word counts)? (c) is the section excluded by the
chunker's effective skip policy — `scriptengine/index/chunker.py`
`BOILERPLATE_SECTIONS` (8 engine-default titles) minus the CSM override's
`content_sections: [Notes, References]` (the COUNCIL_d5-close mechanism:
`effective_boilerplate_sections` = global set − `content_sections`, i.e. the
override can only *promote* engine-boilerplate sections to content, never add
skips)? Verdict: OVERRIDABLE only if the section is skipped by that policy;
R-2 if chunked + chunk present but unretrieved; UNDETERMINED otherwise.

Effective CSM skip set (computed from `chunker.py` + `series/csm/
overrides.yaml`):
`{navigation, external links, see also, site navigation, gallery, image
gallery}` (engine's 8 defaults minus `notes`, `references`).

## 1. R-4/R-2 d5 line-miss rows — verdicts

**All 13 rows: target section is chunked, the chunk is present, the target
line sits whole inside a level-2 passage chunk, and the section is NOT in
the effective skip set. 0 of 13 are OVERRIDABLE; all 13 are R-2 (retrieval
leg, engine class, no override).** No `content_sections` /
`effective_boilerplate_sections` entry is warranted: none of the target
section titles is in the effective skip set, and `content_sections` can only
subtract from it (the JJK `References` precedent, COUNCIL_d5-close §Close
D5).

| row | page (page_type) / target section | section in `sections` | chunks (L1 / L2, words) | line in L2 chunk? | in effective skip set? | verdict |
|---|---|---|---|---|---|---|
| csmd5-01 (MISS_DOC) | `Academy Saga` (saga_box) / `Plot Summary` | id 11, 107w | 1 / 1 (107) | yes | no | **R-2** doc-retrieval leg |
| csmd5-02 (MISS_DOC) | `Academy Saga` / `Plot Summary` | id 11, 107w | 1 / 1 (107) | yes | no | **R-2** doc-retrieval leg |
| csmd5-03 (MISS_SPAN) | `Academy Saga` / `Story Arcs` | id 12, 277w | 1 / 6 (277) | yes (`The Death Devil has finally descended to Earth`, from `src_page` — the row's `q` field is truncated to `"`) | no | **R-2** passage leg |
| csmd5-04 (MISS_SPAN) | `Aging Devil` (character) / `Abilities / Devil Powers` | id 46, 657w | 1 / 9 (657) | yes (`sliced repeatedly by Pochita`) | no | **R-2** passage leg |
| csmd5-05 (MISS_SPAN) | `Aging Devil` / `Abilities / Devil Powers` | id 46, 657w | 1 / 9 (657) | yes (`no means of attack that could kill a Primal Fear`) | no | **R-2** passage leg |
| csmd5-06 (MISS_DOC) | `Aging Devil` / `Abilities / Devil Powers` | id 46, 657w | 1 / 9 (657) | yes (`never undergo reincarnation`) | no | **R-2** doc-retrieval leg |
| csmd5-07 (MISS_SPAN) | `Aging Devil` / `Plot / Aging Devil arc` | id 44, 986w | 1 / 9 (986) | yes (`nobody can age or die`) | no | **R-2** passage leg |
| gate400-188 (MISS_SPAN) | `Aging Devil arc` (story_arcs_box) / `Plot points introduced` | id 26, 812w | 1 / 23 (812) | yes (`vomit out the Ear Devil's head`) | no | **R-2** passage leg |
| gate400-189 (MISS_SPAN) | `Aging Devil arc` / `Plot points introduced` | id 26, 812w | 1 / 23 (812) | yes (`Denji refuses to believe that she is gone`) | no | **R-2** passage leg |
| gate400-211 (MISS_DOC) | `Aging Devil arc` / `Synopsis` | id 24, 1417w | 1 / 16 (1417) | yes (`Yoru abruptly kisses him again`) | no | **R-2** doc-retrieval leg |
| gate400-320 (MISS_SPAN) | `Akane Sawatari` (character) / `Abilities / Devil Contract` | id 66, 229w | 1 / 6 (229) | yes (`Swallow it whole`) | no | **R-2** passage leg |
| gate400-490 (MISS_DOC) | `Aki Hayakawa/History` (character_history) / `Synopsis / Bomb Girl arc` | id 108, 853w | 1 / 10 (853) | yes (`decapitated heads of Nomo`) | no | **R-2** doc-retrieval leg |
| gate400-542 (MISS_SPAN) | `Aki Hayakawa/History` / `Synopsis / Eternity Devil arc` | id 106, 657w | 1 / 6 (657) | yes (`retrieve the piece of the Gun Devil from the Eternity Devil`) | no | **R-2** passage leg |

L2 word counts sum exactly to the section's `word_count` in every case, so
the level-2 passages partition the section text — the line cannot be a
chunking loss. The miss is on the retrieval side: MISS_DOC rows never reach
the retrieved document set (document ranking/budget); MISS_SPAN rows retrieve
the document but the passage bundle (budget/ranking — the G-CSM-2 shape,
`red_list_csm.md` R-2: "the debt is the bundle leg (budget/ranking)") omits
the target passage. Both are engine classes; a per-wiki override has no
surface on either.

## 2. R-6 narrative arc-display aliases — ENGINE HOOK PENDING

The three `door-nar-*` rows miss because the narrative door resolves the
arc by *name*: `NarrativeRetriever.timeline` (`scriptengine/retrieve/
narrative.py`) runs `store.link_entities(subject)`, which does exact
phrase lookups of the query's word n-grams in the `aliases` table
(`scriptengine/stores/facts.py:815`). The wiki's arc display names are not
aliases of the arc pages:

| display name (question) | canonical page (verified in `documents`/`nodes`) | page_type | alias table |
|---|---|---|---|
| `Introduction` | `Introduction arc` (node resolved) | story_arcs_box | only `introduction arc`; bare `introduction` absent |
| `Bomb Girl` | `Bomb Girl arc` (node resolved) | story_arcs_box | only `bomb girl arc`; bare `bomb girl` absent |
| `International Assassins` | `International Assassins arc` (node resolved) | story_arcs_box | only `international assassins arc`; bare name absent |

**Hook check: NO per-wiki alias-map field exists.** `series/csm/
overrides.yaml` has no alias field (top-level keys: `ability_kinds`,
`ability_sections`, `ability_stopwords`, `archetypes`, `citation_positional`,
`content_sections`, `page_scope`, `relation_sections`, `remainder_note`,
`rosters`, `unknown_pages`); the override reader (`scriptengine/config.py`
`load_overrides`) is a generic dict loader, but the only overrides fields the
retrieval/subject-resolution path consults are `subject_demote_types` /
`subject_type_priority` (`config.subject_ranking`) and the roster/ability
fields in `retrieve/roster.py` — none feeds subject resolution with names.
The `aliases` table is populated at index time purely from wiki-side data
(`index/build.py`: page title, infobox alias cells, harvested link display
names, edge targets), not from overrides.

Recorded (per task: do NOT build the hook — engine change = council):
- **Missing field:** `subject_aliases:` in `series/csm/overrides.yaml` — a
  display-name → canonical-node-name map (`introduction: Introduction arc`,
  `bomb girl: Bomb Girl arc`, `international assassins: International
  Assassins arc`).
- **Consulting file:** `scriptengine/retrieve/narrative.py` —
  `NarrativeRetriever.timeline` (the `rank_subjects(self.store
  .link_entities(subject), self.demote, self.priority)` step); the existing
  overrides→retrieval seam is `config.subject_ranking()`
  (`scriptengine/config.py`), already called from
  `NarrativeRetriever.__init__`. (Router-side subject resolution in
  `scriptengine/retrieve/router.py` would need the same map if narrative
  routing is to see the display names for mode decisions.)
- No alias entries were added to `overrides.yaml` (an unread field is
  scaffolding).

## 3. R-7 infobox-key override-support check — ENGINE HOOK PENDING

The T0 pilot's 62-key gap (`T0_PILOT_CSM.md` L48-50; frozen list in
`reports/csm/t0_pilot_csm.json` `meta.unmatched_csm_infobox_keys` — the
frozen JSON holds **61** keys; the report text says 62, the JSON is the
authoritative artifact): the page-sweep identity builder matches fact keys
against the engine's module-level `IDENTITY_FIELDS` dict
(`scriptengine/eval/page_gen.py:49`, 16 entries) + `UNCHECKED_KEYS` (:71).
`_identity_builder` receives `overrides` but consults it only via
`_declared_list` (roster splits); the `key in IDENTITY_FIELDS` test is
engine-only. No file in the tree reads a per-wiki key-map override field
(grepped `identity_fields` / `key_map` / `infobox_map` / `fact_keys`
across `scriptengine/` + `series/`: no consumer).

Recorded (no engine code from this package):
- **Missing field:** `identity_fields:` in `series/csm/overrides.yaml` — a
  CSM-key → question-template map, consulted in `scriptengine/eval/
  page_gen.py` `_identity_builder` ahead of the engine `IDENTITY_FIELDS`
  (the builder already takes `overrides`, so the hook is a one-line engine
  merge — still an engine change → council + four gates).
- **Near-miss seed (the four the T0 pilot names):**
  ```yaml
  identity_fields:
    anime_debut: "In which anime episode is {name} first depicted?"
    manga_debut: "In which manga chapter does {name} first appear?"
    japanese voice: "Who is {name}'s Japanese voice actor?"
    english voice: "Who is {name}'s English voice actor?"
  ```
  The remaining ~57 keys are mostly release/organisation-page keys (composer,
  op/ed number, air date, volume, …) on out-of-scope archetypes; the full map
  is drafted when the hook is approved. Not applied (no hook to apply it
  through).

## 4. Applied + reindex flag

- **Applied to `series/csm/overrides.yaml`: nothing.** No row was
  OVERRIDABLE (all 13 d5 rows R-2), no R-6 hook exists, no R-7 hook exists.
  The file is untouched (git status clean for it; YAML still parses —
  11 top-level keys).
- **Reindex flag: NOT SET.** No override changed, so chunking is unchanged
  and `index --series csm` is not required by this package. (For the record:
  when the R-6/R-7 hooks land, an override-read-at-query-time design needs no
  reindex; an aliases-table design for R-6 would need one reindex to
  materialize the alias rows.)
- **Expected queue rows closed by this package: 0.** The 13 d5 rows stay
  open as R-2 (engine retrieval leg); the 3 R-6 rows stay open pending the
  `subject_aliases` hook; the R-7 lever stays pending the `identity_fields`
  hook (Phase-1 fix candidate once the hook is approved — the no-council
  lever the council pre-registered only in the sense that *data* stays in
  `overrides.yaml`; the reader half is engine and was not present).