# `series/<name>/overrides.yaml`: key reference

The declarative profile of one wiki: the only place wiki-specific rules may live (see `DECISION_one_engine.md`). The key → reader mapping is inventoried from the code (2026-09-28; engine files under `scriptengine/`, `.venv` excluded). **Re-inventory before relying on it:** run `franchise_kit/tools/survey_wiki.py` (the "Declared today" section) and grep the key in `scriptengine/`. A key that no code reads is dead, so retire it.

Status: **live** = read by the engine today · **tool** = read only by `tools/` · **dead** = read by nothing · **C4-T2** = mechanism landing in the Marvel C4 T2 work (`55c2cb9e` + follow-ups); confirm in code before relying on it.

## Crawl / typing / ontology

| key | reader | purpose | declared by (example) |
|---|---|---|---|
| `type_aliases` | ingest/ontology.py | map an infobox template name to the page type (Marvel `Marvel Database:Character Template` → `character`; fix MCU `infobox list` main articles) | marvel, mcu |
| `semantic_types` | retrieve/semantics.py | per-wiki fold of a `page_type` to a semantic type (`combat: technique`) | csm, opm |
| `skip_categories` | ingest/ontology.py | categories whose pages are skipped at crawl/index | marvel, mcu |
| `skip_patterns` | ingest/ontology.py | title patterns skipped (disambiguation handling hook) | marvel |
| `alias_fact_keys` | ingest/ontology.py | infobox keys harvested as aliases (`currentalias`) | marvel |
| `disambig_list_keys` | ingest/alias_align.py | disambiguation-page list fields → alias alignment (C3) | marvel |
| `identity_fields` | config.py | infobox keys used for identity questions (C1 page-gen) | csm, marvel, mcu |
| `prune_types` | cli.py | page types removed from the index | bleach, db, onepiece |
| `subject_aliases` | config.py | explicit subject alias table | csm |
| `subject_type_priority` | config.py | which types win subject resolution | opm |
| `subject_demote_types` | config.py | types a script is never "about" (series/volume/issue); **has an engine default, no series declares it** | — |

## Chunking / citations (traceability)

| key | reader | purpose | declared by |
|---|---|---|---|
| `content_sections` | index/chunker.py | promote sections the default chunker skips (Notes/References/Gallery prose) so chunk-containment reaches them | csm, jjk, marvel, mcu |
| `citation_params` | ingest/wikitext.py | `{{r|…}}`-style param → source kind (Marvel `r → comic`) | db, opm |
| `citation_positional` | ingest/wikitext.py | positional citation grammar | csm |
| `citation_ref_tags` | ingest/wikitext.py | ref tag shapes | berserk, bleach, db, hxh, onepiece |
| `citation_instalments` | ingest/wikitext.py | instalment naming | jjk |
| `citation_works` | ingest/wikitext.py, ingest/audit.py | the works a citation can name | jjk |
| `non_canon_works` | ingest/canon.py, retrieve/roster.py | works excluded from canon | db |
| `canon_media` | retrieve/roster.py | which media count as canon | hxh |

Rule: **never guess what a citation parameter means**. An unmapped parameter stays unmapped (OPM `cep`).

## Structure / relations (C2, C5)

| key | reader | purpose | declared by |
|---|---|---|---|
| `category_relations` | ingest/category_relations.py | category-name patterns → typed edges (`*/Members` → `member_of`) | marvel, mcu |
| `relation_sections` | ingest/relations.py | section names the relations pass reads (`Biography`, `Background`) | berserk, csm, db, hxh |
| `ability_sections`, `ability_headings`, `ability_kinds`, `ability_class`, `ability_owner_sections`, `ability_row_sections`, `ability_sections_umbrella`, `ability_stopwords` | ingest/abilities.py, retrieve/roster.py, ingest/ontology.py | the abilities pass + roster ability sets | many |
| `battle_relations`, `battle_aliases` | retrieve/roster.py, eval/page_gen.py | battle-page semantics | jjk |
| `template_lists` | ingest/templates.py | templates that expand to lists | jjk |
| `extra_facts` | index/build.py | interval facts re-landed on every index | jjk |

## Retrieval / roster

| key | reader | purpose | declared by |
|---|---|---|---|
| `rosters` | retrieve/roster.py, cli.py, eval/* | the roster registry: viewer words → the wiki's set | many |
| `roster_route_words` | eval/page_gen.py | words that route to the roster door (`[]` disables the JJK arc/saga guard) | marvel, mcu |
| `series_titles` | retrieve/roster.py | series title strings | opm |
| `floor_section_cap` | api/context.py | the per-subject floor's section cap | csm |

## Events / time axis / understanding (C4): `events:` block

| sub-key | status | purpose | example |
|---|---|---|---|
| `events.placement_types` | **live** (`27265f1c`) | the wiki's own names for event-container pages, added to the defaults `arc, saga, event, battle, story_arcs` | marvel `[story_arc]`, mcu `[conflict]` (+ `war` per survey) |
| `events.narrative_fact_keys` | C4-T2 | infobox fact values that carry prose (fnmatch globs); **every long prose key** under 100% | marvel `[history, "synopsis*", solicit, powers, abilities, overview, personality, professionalhistory, properties, plot]` |
| `events.furniture` | C4-T2 | extra section headings to exclude (every exclusion is counted per heading) | e.g. `[Interior Art, Cover Art]` |
| `events.axis.date_keys` | C4-T2 | fact keys holding an absolute date; parsed, no-year = counted residue | mcu `[date]` |
| `events.axis.chain_keys` | C4-T2 | previous/next linked-list keys, walked per partition | mcu `[previous, next]` |
| `events.axis.order_keys` | C4-T2 | keys citing a page whose rank is inherited (first/last issue, `part*`) | marvel `[first, last, "part*"]` |
| `events.axis.partition_key` | C4-T2 | one axis per value (multiverse) | marvel `reality` |
| `events.reality` (title pattern / fact key) | C4-T2, **review R8** | the partition naming convention for participant resolution; must live here, not in `events.py` | marvel `(Earth-616)` suffix |

## Coverage tooling only

| key | reader | purpose |
|---|---|---|
| `page_scope`, `remainder_note`, `unknown_pages` | tools/coverage_report.py | page-campaign coverage report |
| `archetypes` | **dead**: nothing reads it (declared by csm, jjk) | retire or wire up |
