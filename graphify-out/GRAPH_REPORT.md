# Graph Report - E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine  (2026-08-23)

## Corpus Check
- rebuilt from merged AST + hand-authored doc-semantic extraction

## Summary
- 3378 nodes · 7107 edges · 167 communities (141 shown, 26 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 384 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2110e4ce`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Roster
- FactStore
- roster.py
- EpisodeIndex
- Member
- step5_retrieval.py
- step2_build_graph_v6.py
- cli.py
- facts.py
- Ontology
- collapse_variants
- content_words
- permission
- series_paths
- build_graph
- chronology.py
- build_roster
- drop_off_owner
- test_script_gen.py
- dependencies
- Annotated
- ingest/abilities.py
- NarrativeRetriever
- VectorStore
- test_question_bank.py
- WikiPage
- AnimeCrawler
- hybrid.py
- questions.py
- get_settings
- _semantic_reason
- WikiCrawler
- wikitext.py
- strip_markup
- Passage
- main.py
- templates.py
- test_llm_client.py
- test_relation_coverage.py
- load_overrides
- run
- TestKinds
- canon_run.py
- fandom_cleaner_fixed_v2.py
- build_graph
- context.py
- relations.py
- parse_constraints
- legacy/config.py
- build.py
- catalogue.py
- Locator
- test_ability_class.py
- norm
- Fact
- folded
- step3_chunk_and_embed.py
- page_is_discounted
- store_for
- Settings
- package.json
- build_graph
- split_sections
- test_ability_extraction.py
- Retrieval Pipeline (hybrid, narrative, roster, citations)
- scriptengine/config.py
- SeriesPaths
- Section
- test_wikitext.py
- drop_unnamed
- main.js
- LLMClient
- harness.py
- server.py
- _extract
- race_vocabulary
- test_model_residency.py
- collect_abilities
- render_prompt
- diagnose_misses.py
- TestLocators
- side_fighters
- export_obsidian
- ._opencode
- TestLocalBackend
- export.py
- chunk_page
- test_citations.py
- Counter
- TestItemMarkers
- subject_ranking
- canon_gold.py
- flatten_tables
- _agree
- TestPagesPerSection
- canon_report.py
- extract_links
- attribute
- TemplateCache
- script_writer.ps1
- test_context.py
- TestParsing
- test_stores.py
- declared_lists
- test_character_scoped.py
- test_gold_hygiene.py
- paths_for
- Page-driven accuracy campaign (page-run, ~100 Q per top page)
- _capped_beats
- rosters
- split_passage
- extract_series
- parametrize
- TestHeading
- TestOwnerSurvivesParsing
- App.js
- relation_coverage.py
- discover_infoboxes
- instalment_number
- TestGroundedness
- manifest.json
- split_params
- TestEpisodeIndex
- locator_from_title
- expected_type
- lexical.py
- TestOwnership
- TestAppearances
- TestCast
- TestScaffold
- TestThinkingIsDetectable
- TestFlatten
- FakeClient
- TestGraph
- TestLexicalSearch
- discounted_works
- TestBeats
- TestChains
- clean_all_files
- _item_name
- _tail_pattern
- model_health.py
- TestSubject
- TestEntityLinking
- Three doors: HTTP API :8000, Typer CLI, MCP stdio (wrap the same functions)
- owned_passages
- TestSpans
- TestStripFence
- TestNodes
- .__init__
- start_scriptengine.py
- TestSchema
- audit command (run before index; catches silent extractor defects)
- api/__init__.py
- eval/__init__.py
- index/__init__.py
- ingest/__init__.py
- scriptengine/__init__.py
- llm/__init__.py
- retrieve/__init__.py
- stores/__init__.py
- .test_a_fusion_is_not_a_form
- .test_a_subject_roster_does_not_make_its_person_unnameable
- preload.js
- Gate: canon-run --series opm (8/16 exact, 235/237 canon, 78.5% prec, 20/20 fact)
- Gate: pytest tests/ = 985 passed

## God Nodes (most connected - your core abstractions)
1. `FactStore` - 410 edges
2. `series_paths()` - 87 edges
3. `SeriesPaths` - 84 edges
4. `build_roster()` - 82 edges
5. `EpisodeIndex` - 66 edges
6. `get_settings()` - 64 edges
7. `load_overrides()` - 59 edges
8. `Settings` - 49 edges
9. `WikiPage` - 46 edges
10. `Roster` - 42 edges

## Surprising Connections (you probably didn't know these)
- `build_graph()` --calls--> `Counter`  [INFERRED]
  legacy/step2_build_graph_v2.py → tests/test_semantics.py
- `build_graph()` --calls--> `Counter`  [INFERRED]
  legacy/step2_build_graph_v3.py → tests/test_semantics.py
- `build_graph()` --calls--> `Counter`  [INFERRED]
  legacy/step2_build_graph_v6.py → tests/test_semantics.py
- `prune()` --calls--> `Counter`  [INFERRED]
  scriptengine/cli.py → tests/test_semantics.py
- `abilities()` --calls--> `link()`  [INFERRED]
  tests/test_roster_validation.py → scriptengine/cli.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **The three retrieval modes** — arch_hybrid_retrieval, arch_narrative_retrieval, arch_roster_retrieval [EXTRACTED 0.90]
- **The campaign gate triple** — arch_gate_eval, arch_gate_canon, arch_gate_pytest [EXTRACTED 0.90]
- **The three writer doors** — arch_fastapi_context, arch_typer_cli, arch_mcp_server [EXTRACTED 0.90]

## Communities (167 total, 26 thin omitted)

### Community 0 - "Roster"
Cohesion: 0.04
Nodes (68): apply_constraints(), canon_media(), Constraints, _declared_members(), _disagrees(), _distinct(), _game_only(), _grounded() (+60 more)

### Community 1 - "FactStore"
Cohesion: 0.03
Nodes (38): is_power_up_only(), True when the wiki calls this a power-up and never a transformation. Dark…, FactStore, Path, Row, Every category one page is filed under. Membership validation reads these: the…, Every resolved entity of one page type, e.g. every `technique`., Pages the wiki filed under one category. (+30 more)

### Community 2 - "roster.py"
Cohesion: 0.04
Nodes (64): ability_class(), ability_class_rules(), ability_kind_words(), ability_stopwords(), _asked_kinds(), battle_result(), _battles_table_rows(), _character_subject() (+56 more)

### Community 3 - "EpisodeIndex"
Cohesion: 0.05
Nodes (47): EpisodeIndex, Chapter number -> episode title, straight from the graph. Both relations are…, asks_for_battle_result(), asks_for_battles_in(), asks_one_on_one(), battle_result_fighter(), _battle_sides(), battles_in() (+39 more)

### Community 4 - "Member"
Cohesion: 0.05
Nodes (37): _debut(), _group_label(), _grouping_field(), looks_like_enumeration(), Member, _member_order(), _member_prose(), _names_a_character() (+29 more)

### Community 5 - "step5_retrieval.py"
Cohesion: 0.06
Nodes (36): CrossEncoder, build_context(), decompose_query(), is_multihop(), QwenModel, RAGPipeline, Step 4: Query decomposition for multi-hop questions + Qwen generation This…, Use Qwen to decompose a complex query into simpler sub-questions. (+28 more)

### Community 6 - "step2_build_graph_v6.py"
Cohesion: 0.11
Nodes (42): add_node(), add_relation(), best_kind(), build_graph(), BuildResult, chronology_key(), classify_title_part(), clean_text() (+34 more)

### Community 7 - "cli.py"
Cohesion: 0.06
Nodes (52): command, -m, scriptengine.mcp.server, .\\scriptengine\\.venv\\Scripts\\python.exe, abilities(), canon_run(), catalogue(), cite() (+44 more)

### Community 8 - "facts.py"
Cohesion: 0.06
Nodes (39): link(), Write the ownership a wiki states in prose rather than in a field. `owned_by`…, derive(), Any, Ownership a wiki states in a sentence rather than in a field. `owned_by` walks…, The character a technique page's lead says it belongs to, or ``""``., Write a `stated user` edge for every technique page naming its owner., stated_owner() (+31 more)

### Community 9 - "Ontology"
Cohesion: 0.07
Nodes (28): build_ontology(), build_ontology_from_transclusions(), _is_module(), item_section_names(), learn_field_labels(), _normalise_template(), Ontology, Any (+20 more)

### Community 10 - "collapse_variants"
Cohesion: 0.06
Nodes (24): collapse_variants(), _fragments(), normalise(), One ability under two names: the wiki's own title and the bare word inside it.…, The form two names are compared in: folded, collapsed, apostrophe-free. Not a…, `(prefixes, suffixes)` around every `: ` in an already-normalised name. Every…, Return (kept, dropped) where dropped records name + the variant that covers it.…, parametrize (+16 more)

### Community 11 - "content_words"
Cohesion: 0.07
Nodes (29): _asks_for_packaging(), _choose_set(), content_words(), _overlap(), rate_match(), Words that name the work itself, not a set inside it., True when the query itself named a volume, an episode, a film., The wiki's own name, as one lowercase run of letters. Read from the host in the… (+21 more)

### Community 12 - "permission"
Cohesion: 0.04
Nodes (46): Get-ChildItem*, git *, npm *, pytest *, python *, Remove-Item*, rm *, Test-Path* (+38 more)

### Community 13 - "series_paths"
Cohesion: 0.07
Nodes (25): Return the paths for ``name``, rejecting anything that could escape the root., series_paths(), Whether a topic is asking for order rather than membership. Checked before the…, wants_chronology(), parametrize, Tests for mode selection. Two bugs prompted this file. `qa`, the hybrid…, The enumeration test agreed with structure on all 154 real topics, so this is…, Who are the members of X" is "Every member of X" with a question mark. Every… (+17 more)

### Community 14 - "build_graph"
Cohesion: 0.11
Nodes (31): _add_node(), best_kind(), build_graph(), _classify_title_part(), _clean_battle_part(), clean_text(), entity_kind_from_ner(), extract_candidates() (+23 more)

### Community 15 - "chronology.py"
Cohesion: 0.07
Nodes (37): chronicle(), A character's story arc by arc, in the shape a life script is written. `The…, Appearance, appearances(), Arc, arc_pages(), Beat, beats() (+29 more)

### Community 16 - "build_roster"
Cohesion: 0.07
Nodes (29): battle_named(), battle_relations(), _battle_roster(), build_roster(), _combine(), is_one_on_one(), _is_packaging_set(), _narrowed_by_a_name() (+21 more)

### Community 17 - "drop_off_owner"
Cohesion: 0.07
Nodes (21): drop_general_pages(), drop_off_owner(), Remove abilities whose own page names users, none of them this character.…, Remove members whose own page is the class itself, not an instance of it.…, fixture, parametrize, Whose ability it is, settled on the ability's own page. `ingest/abilities.py`…, `Dismantle`, `Cleave` and `Hometown Domain` have no page anywhere on this wiki,… (+13 more)

### Community 18 - "test_script_gen.py"
Cohesion: 0.06
Nodes (11): bundle(), Tests for the script-writing loop: bundle -> draft -> verify -> repair -> save., TestApplyTitle, TestAutoBudget, TestCutSections, TestExpandScript, TestRepairScript, TestTitleOf (+3 more)

### Community 19 - "dependencies"
Cohesion: 0.05
Nodes (37): @emotion/react, @emotion/styled, @mui/icons-material, @mui/material, react, react-dom, react-router-dom, react-scripts (+29 more)

### Community 20 - "Annotated"
Cohesion: 0.11
Nodes (18): annotate(), Annotated, Block, _is_taggable(), Settings, Sourcing a script that already exists. The writing path gets its locators for…, Break a script into blocks without losing a character of it. Line-based rather…, Tag each block of `script` with the chapter and episode behind it. (+10 more)

### Community 21 - "ingest/abilities.py"
Cohesion: 0.09
Nodes (34): _answer_budget(), extract_character(), extract_from_passages(), extract_series(), Extraction, _fold(), _grounded_in(), _is_lead() (+26 more)

### Community 22 - "NarrativeRetriever"
Cohesion: 0.09
Nodes (21): Beat, _event_token_hits(), Narrative, NarrativeRetriever, Any, Settings, _query_content_tokens(), Content words in the query, minus stopwords and the subject's own name. (+13 more)

### Community 23 - "VectorStore"
Cohesion: 0.09
Nodes (17): _forget_reader(), Any, Path, QdrantClient, Vector storage, via Qdrant in local (embedded) mode. Same client API as the…, Store vectors keyed by chunk id. The chunk id from SQLite is reused as the…, Nearest chunks, optionally restricted to a level or a set of pages. Filtering…, Embedded vector storage for one series. (+9 more)

### Community 24 - "test_question_bank.py"
Cohesion: 0.06
Nodes (24): banks(), _campaign_batch_text(), fixture, Constraints on `questions/` itself, not on what the engine answers. The bank…, Two questions may not share a string, even across series. Question text is a…, `diagnose_misses.SUBJECT` must cover the bank, not a snapshot of it. It was a…, `diagnose_misses.py` does `for series, query, _ in GOLD`. That tuple shape is a…, Campaign batches sit under `_*.json` names that `load_all` skips. `load_file`… (+16 more)

### Community 25 - "WikiPage"
Cohesion: 0.10
Nodes (32): audit(), Report what the extractor understood, before you trust it., audit_series(), _citation_coverage(), compare_page(), _instalment(), Any, Auditing what extraction actually understood. A broken extractor is silent. The… (+24 more)

### Community 26 - "AnimeCrawler"
Cohesion: 0.10
Nodes (19): asyncio, CLI entry point for running the anime web crawler, AnimeCrawler, _fandom_api_base(), _is_fandom(), Any, BeautifulSoup, Fandom wiki crawler using MediaWiki API; bypasses Cloudflare entirely. (+11 more)

### Community 27 - "hybrid.py"
Cohesion: 0.09
Nodes (17): Embedder, Settings, Embedding, with the GPU treated as a shared resource. ComfyUI and a resident…, Release the model and its VRAM. Returns whether anything was freed., Free the GPU if nothing has used the model recently., Cross-encoder rerank, under the same load/unload discipline., Score each passage against the query. A cross-encoder reads the query and the…, Unload whichever shared model has gone idle. Returns whether any did. Called on… (+9 more)

### Community 28 - "questions.py"
Cohesion: 0.12
Nodes (29): Exception, AnswerItem, as_gold(), Bank, _blocked(), facts(), _item(), load_all() (+21 more)

### Community 29 - "get_settings"
Cohesion: 0.12
Nodes (32): get_settings(), Where a finished script goes, and under which video number. Reuses the existing…, script_destination(), Settings, _apply_title(), auto_budget(), _complete(), cut_sections() (+24 more)

### Community 30 - "_semantic_reason"
Cohesion: 0.10
Nodes (17): parse_response(), Read the model's JSON, tolerating the fences it was told not to use., Why an index-time classification disqualifies this from a race's forms. Read…, _semantic_reason(), fixture, parametrize, Tests for index-time semantic classification. Deterministic rules settle most…, Great Ape needs a full moon and Super Saiyan God a ritual of five Saiyans. The… (+9 more)

### Community 31 - "WikiCrawler"
Cohesion: 0.09
Nodes (19): api_base(), Any, Fetches a wiki into `series/<name>/wikitext/*.json`., One API call, with retries, backoff, and rate-limit compliance., See `list_all_pages`. Raises `EnumerationFailed` rather than returning an empty…, Real article titles in the main namespace. Redirects are excluded. `allpages`…, Pages in the `Template:` namespace, the wiki's own vocabulary., Fetch many pages in one request, shaped like `action=parse` output. Fandom… (+11 more)

### Community 32 - "wikitext.py"
Cohesion: 0.09
Nodes (26): Citation, A reference to a source work. Fandom wikis cite through templates such as…, A short human-readable form, e.g. ``Ref vol=5 page=26``., _citation_marker(), CitationGrammar, _flatten_links(), _has_locator(), Wikitext parsing. Wikitext cannot be parsed with regular expressions. Templates… (+18 more)

### Community 33 - "strip_markup"
Cohesion: 0.09
Nodes (9): Replace every ``<ref>`` with its locator, or with nothing. Nothing is the right…, Reduce wikitext to readable prose. Citations are flattened to a short locator,…, strip_markup(), _strip_ref_tags(), TestAlternateParamNames, TestCitationGrammar, TestMarkupStripping, TestPositionalCitations (+1 more)

### Community 34 - "Passage"
Cohesion: 0.11
Nodes (15): _deduplicate(), Passage, Any, Dense search, run both narrowed to graph-selected pages and wide open. Running…, Drop near-identical passages produced by chunk overlap. Consecutive chunks…, One retrieved passage, with everything needed to cite it., Combine rankings by reciprocal rank. RRF needs no score calibration between…, reciprocal_rank_fusion() (+7 more)

### Community 35 - "main.py"
Cohesion: 0.12
Nodes (26): BaseModel, get, on_event, post, abilities(), context(), ContextRequest, facts() (+18 more)

### Community 36 - "templates.py"
Cohesion: 0.10
Nodes (19): find_unresolved(), Resolve the wiki's curated list templates into the stored corpus. The crawler…, `(template_name, start, end)` for each declared top-level transclusion.…, Replace every declared transclusion with its expansion. Expansions key on…, splice(), find_templates(), infobox_candidates(), parse_template() (+11 more)

### Community 37 - "test_llm_client.py"
Cohesion: 0.11
Nodes (14): _event(), opencode_client(), parametrize, The model backend, spoken through opencode. The subprocess is mocked…, So a batch stops on the first one instead of recording every remaining page as…, This stopped a working batch on its first page, twice. Scanning the whole…, A run can exit 0 and have failed; the failure arrives as an event., Callers that only know about `LLMUnavailable` must still degrade. (+6 more)

### Community 38 - "test_relation_coverage.py"
Cohesion: 0.10
Nodes (17): _bank(), _prepare(), parametrize, Scoring the relations table, which the canon bank does not reach. The gap this…, Only partners held *solely* by narration are the declaration's doing., A store and a one-question bank, wired to where the scorer looks., `save_relations` replaces one character at a time, so group first., The wiki writes the relationship on whichever page it feels like. Geto's page… (+9 more)

### Community 39 - "load_overrides"
Cohesion: 0.12
Nodes (17): load_overrides(), Read `series/<name>/overrides.yaml`. The only place a wiki-specific rule may…, Extraction is opt-in per wiki, and costs nothing where unasked. This used to…, `--limit` must not mean "the first few alphabetically". Ordered by name,…, TestGating, facts_db(), _page(), fixture (+9 more)

### Community 40 - "run"
Cohesion: 0.12
Nodes (27): batch_path(), Any, Path, Settings, The triage sheet: every question with what it missed beside it., Where a campaign batch lives: `questions/_<series>_page_<slug>.json`., Score one batch against the live server and write a triage report. Returns…, report_markdown() (+19 more)

### Community 41 - "TestKinds"
Cohesion: 0.07
Nodes (13): Every ability of X" must not exclude what the wiki filed as a form. Which of…, Only the umbrella widens. "Every technique of X" is still techniques., `members:` is transcribed from the wiki, not read out of the index. Requiring a…, `keep_bare` is for hand-written lists only. A category read returning a name…, `subject:` is the exception to "a person beats a declared set". Without it…, Same set, two phrasings, and only one of them used to match. `\\b{phrase}s?\\b`…, Raising it looked right and measured worse. 25 canon items are dropped here,…, `NEVER_MEMBERS` applied to the set, not only to its members. `_disagrees`… (+5 more)

### Community 42 - "canon_run.py"
Cohesion: 0.14
Nodes (25): datetime, answers_markdown(), CanonRunError, check_fresh(), check_series(), git_sha(), health(), newest_source() (+17 more)

### Community 43 - "fandom_cleaner_fixed_v2.py"
Cohesion: 0.21
Nodes (26): build_citation_map(), clean_text(), compact_spaces(), convert_file(), detect_page_type(), extract_body_text(), extract_infobox(), extract_list_battles() (+18 more)

### Community 44 - "build_graph"
Cohesion: 0.19
Nodes (18): build_graph(), build_title_sets(), canonical_key(), extract_from_document(), extract_participants_from_battle_title(), find_arcs_in_text(), gather_titles(), GraphBuilder (+10 more)

### Community 45 - "context.py"
Cohesion: 0.14
Nodes (24): build_context(), estimate_tokens(), _narrative_context(), _one_line(), Any, Settings, _qa_context(), Assembling the context bundle a script-writing model consumes. This is the… (+16 more)

### Community 46 - "relations.py"
Cohesion: 0.11
Nodes (26): _guarded(), Run a job, returning the exception instead of raising it.…, _answer_budget(), _era_for(), extract_from_passages(), extract_series(), known_arcs(), known_names() (+18 more)

### Community 47 - "parse_constraints"
Cohesion: 0.09
Nodes (17): _media_of(), non_canon_works(), parse_constraints(), Enough of a stem to make `heroes` and `hero` the same word. Not a stemmer: this…, The words in a topic that narrow the set, and how wide to cast. "Every Saiyan…, How a question is likely to name a work, as well as its full title. Every…, Works this series keeps but does not count as its story., Which media a debut names. `Movie: ... Manga: ...` names two. (+9 more)

### Community 48 - "legacy/config.py"
Cohesion: 0.08
Nodes (23): AppConfig, ChunkerConfig, DatabaseConfig, ElasticsearchConfig, EmbeddingConfig, LangGraphConfig, Neo4jConfig, OllamaConfig (+15 more)

### Community 49 - "build.py"
Cohesion: 0.13
Nodes (24): Progress, index(), Build the fact store, graph, BM25 index and vectors., build_index(), _embed_chunks(), _harvest_link_aliases(), index_status(), _load_chunks() (+16 more)

### Community 50 - "catalogue.py"
Cohesion: 0.12
Nodes (15): _audit(), collect(), _manifest(), _pct(), Any, Settings, What is actually in the engine, generated from the engine. Every series brings…, Sourcing and typing, from the report `cli audit` already wrote. (+7 more)

### Community 51 - "Locator"
Cohesion: 0.14
Nodes (15): _distinct_works(), Locator, locators(), _numbers(), _range(), Turning wiki references into locators a script can say out loud. A script line…, Distinct locators, in the order they first cover something., Collapse locators into one readable range. ``Chapters 90-92, Episodes 35-36``,… (+7 more)

### Community 52 - "test_ability_class.py"
Cohesion: 0.08
Nodes (14): fixture, parametrize, Classing an ability by what the wiki says it *is*, not where it was filed.…, `Simple Domain` is `Anti-Domain Technique` *and* `Barrier Technique`., Empty means "no opinion", which must not read as "keep nothing"., So `cursed technique` can be narrower than `technique`., The wiki said nothing, so nothing has been shown about it., `Every ability of X` keeps Divergent Fist and Black Flash. Both really are… (+6 more)

### Community 53 - "norm"
Cohesion: 0.16
Nodes (23): norm(), _canon_of(), diagnose(), _heading_leaves(), is_lead_row(), _matched_keys(), _owned(), Row (+15 more)

### Community 54 - "Fact"
Cohesion: 0.14
Nodes (13): Chunking, driven by the section tree the API supplied. Three levels: * **0,…, A compact, readable summary of what the page is and states. Written as labelled…, Split into sentences, keeping abbreviations and citation markers intact., render_document_card(), split_sentences(), Fact, Link, The shapes that flow through ingestion. One rule governs this module:… (+5 more)

### Community 55 - "folded"
Cohesion: 0.12
Nodes (12): emphasised_names(), Every name the page puts in bold, in order, deduplicated. A wiki bolds what it…, folded(), parametrize, What a page names, as against what it mentions. `Every cursed technique of…, The case a page-existence rule would get wrong., The bank spells some entries as the target and some as the label., The whole reason this is narrower than `'''bold'''`. Sukuna's page bolds `Enma`… (+4 more)

### Community 56 - "step3_chunk_and_embed.py"
Cohesion: 0.14
Nodes (23): build_hierarchical_chunks(), chunk_section(), embed_chunks(), ingest_all(), is_section_header(), load_embedder(), load_entity_list(), parse_wiki_file() (+15 more)

### Community 57 - "page_is_discounted"
Cohesion: 0.17
Nodes (13): page_is_discounted(), Whether this whole page belongs only to a work the series discounts. Read from…, Edge, A typed relationship between two pages. ``confidence`` distinguishes how the…, page(), Dropping the works a series does not count, at index time. `non_canon_works:`…, A category means "appears in", not "belongs to". `Super Dragon Ball` is filed…, The game's own episodes and chapters say nothing about a debut, so the category… (+5 more)

### Community 58 - "store_for"
Cohesion: 0.13
Nodes (12): parametrize, They are `Devil Fruit / Gear 2`, not pages, and not `Former Pirates`., Killua and Kurapika both returned the identical 13 Greed Island cards., Frieza's four came back `declared` holding two of his eight forms., Bleach records one user edge for Ichigo across the whole wiki., Luffy's Gears are split across the two readings of one page. The headings on…, A model read them; the wiki did not file them., These are no longer filtered at query time; they are not indexed. `_game_only`… (+4 more)

### Community 59 - "Settings"
Cohesion: 0.11
Nodes (10): BaseSettings, Resolve ``auto`` to a concrete torch device without importing torch eagerly., Process-wide settings, overridable by env or `.env`., Settings, ask(), main(), Ask the running engine a sheet of questions and write down what it said. Every…, render() (+2 more)

### Community 60 - "package.json"
Cohesion: 0.09
Nodes (21): concurrently, electron, fs-extra, dependencies, axios, fs-extra, description, devDependencies (+13 more)

### Community 61 - "build_graph"
Cohesion: 0.13
Nodes (14): build_graph(), extract_entities(), GraphBuilder, is_section_header(), parse_wiki_file(), Step 1: Parse wiki text files → extract entities/relationships → build Neo4j…, Extract: - Named entities (characters, techniques, locations, arcs) -…, Run once; creates indexes for fast lookup. (+6 more)

### Community 62 - "split_sections"
Cohesion: 0.12
Nodes (11): collect_ref_definitions(), collect_ref_tag_definitions(), Section, Split a page into its lead and its sections. ``api_sections`` is the section…, Named ``<ref>`` bodies, keyed by name. Same convention as the template form:…, Named references that carry a locator, keyed by their name. MediaWiki cites a…, split_sections(), Splitting must move text, never lose it. The first version skipped the group… (+3 more)

### Community 63 - "test_ability_extraction.py"
Cohesion: 0.09
Nodes (11): Extracting the abilities a wiki only writes as prose. Half of what a character-…, A page's own opening paragraph is about the character by definition., `Holy Chain`, `Steal Chain` and `Emperor Time` are named in his lead and…, Techniques on the page a character owns, not on their own page. One Piece names…, A stored row has to say where it was read from, so these stay tellable from…, Off by default. Most wikis keep the techniques on the character, and reading…, `None` as the store proves it: undeclared must not reach a query., Killua's `Abilities & Powers` is 17,672 characters. Sending the first 4,000… (+3 more)

### Community 64 - "Retrieval Pipeline (hybrid, narrative, roster, citations)"
Cohesion: 0.10
Nodes (21): Anti-AI Voice Rules (docs/ANTI_AI_SCRIPTING.md), Battles-in roster path (reads the wiki's own battle infoboxes), Chapter/Episode citation traceability (numbers looked up, never inferred), G3: Nihongo keep-all (wikitext parser keeps english+kanji+romaji), G7: roster bundles carry hybrid passages for count queries, Hybrid / relevance retrieval, Indexing Pipeline (section chunking, embedding, build), Ingestion Pipeline (crawler, wikitext parser, ontology discovery, audit) (+13 more)

### Community 65 - "scriptengine/config.py"
Cohesion: 0.12
Nodes (16): Configuration for ScriptEngine. Every value here is either read by running code…, gold_names(), main(), Do this series' declarations contradict its own bank? `ability_stopwords` says…, Every gold item and alias in this series' set questions -> question ids., build(), headings(), main() (+8 more)

### Community 66 - "SeriesPaths"
Cohesion: 0.12
Nodes (12): Path, Filesystem layout for a single series. Each series is fully self-contained:…, Rendered HTML, as returned by ``action=parse``., Raw wikitext plus per-page API metadata, one JSON file per page., SQLite: documents, sections, nodes, edges, facts, and the FTS5 index., Qdrant local-mode storage directory., What was crawled, when, and from which wiki. Small enough to commit., Extraction audit reports. (+4 more)

### Community 67 - "Section"
Cohesion: 0.12
Nodes (15): keep_sections(), _names_a_work(), Section, Which works a series counts, applied at index time. `non_canon_works:` in…, The sections that are not a discounted work's corner of a kept page. Two…, Whether a string is one of these works, or something inside one. Whole string…, Whether one debut target belongs to a discounted work. The category hop is what…, _target_is_discounted() (+7 more)

### Community 68 - "test_wikitext.py"
Cohesion: 0.15
Nodes (9): extract_citations(), facts_from_infobox(), find_infobox(), Return the page's infobox as ``(template_name, raw_params)``.…, Turn infobox parameters into facts, keeping links and citations attached.…, Collect citation templates, recursing so nested ones are not missed.…, Tests for wikitext parsing. The cases here are drawn from real Jujutsu Kaisen…, TestCitations (+1 more)

### Community 69 - "drop_unnamed"
Cohesion: 0.13
Nodes (13): drop_unnamed(), _has_page(), Remove members the subject's page mentions but does not name. Asked for a…, fixture, Mentioned on a page is not the same as named by it. `Every cursed technique of…, The guarantee `apply_constraints` gives, for the same reason., `Dismantle` has no page anywhere on the wiki., The other half of the rule, and it covers a different blind spot. (+5 more)

### Community 70 - "main.js"
Cohesion: 0.20
Nodes (19): { app, BrowserWindow, ipcMain, dialog }, APP_PATHS, axios, checkDocker(), checkGit(), checkNode(), checkOllama(), checkPython() (+11 more)

### Community 71 - "LLMClient"
Cohesion: 0.16
Nodes (15): classify(), Classify the ability pages the wiki's own fields cannot settle. `Class =…, Classification, classify_page(), classify_series(), _context(), needs_classifying(), Any (+7 more)

### Community 72 - "harness.py"
Cohesion: 0.19
Nodes (19): _check_route(), evaluate(), _evaluate_narrative(), _evaluate_retrieval(), _evaluate_roster(), _evaluate_sourcing(), _hit_docs(), _hit_text() (+11 more)

### Community 73 - "server.py"
Cohesion: 0.14
Nodes (18): _load(), Any, Checking a finished script's chapter and episode tags against the crawl. The…, Check every tag in `text`. Returns the findings, worst first., Titles, cited instalments and adaptation pairings, straight from disk., verify_script(), _budget_for(), Any (+10 more)

### Community 74 - "_extract"
Cohesion: 0.14
Nodes (9): _Client, _extract(), The pass that reads chapter and episode pages instead of character pages.…, A narrative row has to stay tellable from an ability-list row., Everyone knows whose that is" must not get through., No declaration means no passages, not every page on the wiki., A model that returns one canned answer, so the guards can be measured., TestDeclaration (+1 more)

### Community 75 - "race_vocabulary"
Cohesion: 0.13
Nodes (13): Acquisition, classify(), _mentions(), _race_of(), race_vocabulary(), Prefix matching, so `saiyan` reaches `Saiyans` and `Saiyan beyond God`., How an ability is come by, derived rather than declared., Is this exclusive to `race`? Teachable and unknown never are. (+5 more)

### Community 76 - "test_model_residency.py"
Cohesion: 0.18
Nodes (14): _Counting, _FakeModel, Settings, Models stay loaded between requests, and still come back to ComfyUI. The GPU is…, An Embedder that records loads instead of reading 1.3 GB off disk., `release_models()` after every request is what made queries slow., The GPU still goes back, on a timer rather than per request. The clock is wound…, 0 disables the sweep rather than unloading constantly. (+6 more)

### Community 77 - "collect_abilities"
Cohesion: 0.17
Nodes (16): _chapter_number(), collect_abilities(), _load_page(), Any, Graph-driven ability lookup for a character. The knowledge graph already knows…, The stored crawl JSON for a page (sections carry Ref citations)., Chapter refs from the `Usage / <character>` section of an ability page., Every ability a character uses, with debut and per-character usage. Returns… (+8 more)

### Community 78 - "render_prompt"
Cohesion: 0.29
Nodes (4): Flatten a bundle into plain text, for callers that just want a string. Offered…, render_prompt(), bundle(), TestRenderPrompt

### Community 79 - "diagnose_misses.py"
Cohesion: 0.19
Nodes (16): _anywhere(), _canon_of(), diagnose(), _has_page(), _in_abilities(), _in_headings(), _in_own_prose(), _keys() (+8 more)

### Community 80 - "TestLocators"
Cohesion: 0.18
Nodes (7): True when these locators cover more chapters than a tag usefully can., _too_wide(), parse_locator(), parse_markers(), Read one inline marker back into its parts., Every inline locator in `text` as ``(start, end, Locator)``., TestLocators

### Community 81 - "side_fighters"
Cohesion: 0.16
Nodes (10): _character_titles(), Every page this wiki types as a character, longest first. Longest first because…, `(characters named on this side, whatever text is left over)`. Resolved…, side_fighters(), `Maki Zenin vs. The Hei` has `side2 = 'Hei Nobuaki Zenin'`. Matching `Nobuaki…, `Sukuna (16 Fingers)` says which Sukuna, not that two turned up., `Cursed Spirits` and `Jujutsu Sorcerers` are not named characters, so they fail…, `Finger Bearer` is one opponent, and not a named character. (+2 more)

### Community 82 - "export_obsidian"
Cohesion: 0.19
Nodes (8): export_obsidian(), Render `series/<name>/obsidian/` from the fact store. Read-only. Returns a…, _page(), fixture, Tests for the Obsidian vault export., A tiny indexed series: two documents, one location, two colliding links., series(), TestExport

### Community 83 - "._opencode"
Cohesion: 0.13
Nodes (12): _error_event(), _flatten(), _looks_throttled(), One turn, one answer, from whichever backend is configured., The answer, and the endpoint's `usage` block alongside it. Split out for…, An OpenAI-shaped endpoint: LM Studio on 1234, Ollama on 11434. Kept alongside…, `opencode run`, which exposes neither temperature nor max tokens., One line, because `opencode run` silently drops everything after the first.… (+4 more)

### Community 84 - "TestLocalBackend"
Cohesion: 0.21
Nodes (6): The OpenAI-shaped path: Ollama on 11434, LM Studio on 1234., Gemma 4 and Qwen3.5 both put their thinking in `reasoning_content` and leave…, `local` must not shell out, whatever opencode is doing., A cut-off answer looks like valid JSON until it is parsed. `parse_response`…, TestLocalBackend, TestTruncationIsNotSilent

### Community 85 - "export.py"
Cohesion: 0.23
Nodes (14): _collision_map(), _fact_properties(), _frontmatter(), _lead_links(), Any, Path, Export a series' graph to an Obsidian vault. Obsidian's graph view is built…, The page's own links, parsed from its wikitext before the first heading. The… (+6 more)

### Community 86 - "chunk_page"
Cohesion: 0.36
Nodes (6): chunk_page(), Produce every chunk for one page, in document order. `ordinal` is the position…, make_page(), Section, section(), TestChunkPage

### Community 87 - "test_citations.py"
Cohesion: 0.18
Nodes (9): coverage(), Rewrite ``(Chapter 79)`` as ``(Chapter 79, Episode 30)`` where known.…, How much of a passage can be sourced. Used by `cli audit`., upgrade_markers(), fixture, Tests for turning wiki references into locators a script can say., store(), TestCoverage (+1 more)

### Community 88 - "Counter"
Cohesion: 0.14
Nodes (8): Counter, How many statements a connection actually ran., Classification is asked the same question repeatedly inside one request.…, The guard against a memo outliving the data it was read from. `index` rewrites…, Two callers, two `overrides`, two answers, not whichever asked first., Keyed on what the overrides say, not on which dict object said it., `roster._profile` keeps its own memo in the same store's cache., TestMemoisation

### Community 89 - "TestItemMarkers"
Cohesion: 0.20
Nodes (6): Headings a wiki writes without writing a heading. `Goku/Power and Abilities`…, Otherwise every item's text is stored twice, once under its own heading and…, One Piece writes 7,491 of these markers, and its heaviest pages are `Chapter…, Bleach and One-Punch Man use `'''Bold'''` where Dragon Ball uses `;`., split_sections_for_bleach(), TestItemMarkers

### Community 90 - "subject_ranking"
Cohesion: 0.21
Nodes (7): ``(demoted_types, type_priority)`` for this wiki., subject_ranking(), Any, rank_subjects(), The stored classification for one page, or ``None``. Read on every roster…, Re-rank linked entities by how likely each is to be a script's subject.…, TestSubjectRanking

### Community 91 - "canon_gold.py"
Cohesion: 0.24
Nodes (13): ask(), haystack(), main(), _members(), present(), Score the online-canon question bank against a running server. The bank lives…, Everything in a bundle a caller could read an answer out of, folded. A fact…, Word-boundary containment, not `in`. Plain containment lets `Gon` match inside… (+5 more)

### Community 92 - "flatten_tables"
Cohesion: 0.18
Nodes (10): _flatten_one_table(), flatten_tables(), _is_media_only(), _is_namespaced(), True for links that are not a relationship to another article here., Turn wikitables into readable lines instead of deleting them. On a Fandom wiki…, True when a cell contains nothing but file or image links., Render a single table body as one line per row. (+2 more)

### Community 93 - "_agree"
Cohesion: 0.25
Nodes (6): _agree(), Any, The locator the retrieved passages agree on, or nothing. Agreement is counted…, FakePassage, Enough of `hybrid.Passage` to exercise agreement., TestAgreement

### Community 94 - "TestPagesPerSection"
Cohesion: 0.14
Nodes (4): parametrize, The old loop, run one heading at a time, is the oracle. Keeping it here means…, One query for one heading, and the same one query for two hundred. This is the…, TestPagesPerSection

### Community 95 - "canon_report.py"
Cohesion: 0.23
Nodes (12): append_index(), _delta(), _pct(), Path, Render a measurement run into something a person can act on. The scores say…, One row per run, so a number can be read as a trend rather than a fact., Every question the engine did not answer well, worst first. Ordered by what…, render() (+4 more)

### Community 96 - "extract_links"
Cohesion: 0.22
Nodes (5): extract_links(), normalise_title(), Collect every ``[[Target|Display]]`` in order of appearance. Category, File and…, Apply MediaWiki's own title rules so one page yields one node. MediaWiki…, TestLinks

### Community 97 - "attribute"
Cohesion: 0.22
Nodes (5): attribute(), The episode that adapted `chapter`, or "" when the anime has not., Fill in the episode when the graph knows it and the ref did not. A chapter of…, Assign every sentence the reference that covers it. The nearest ref *after* a…, TestAttribution

### Community 98 - "TemplateCache"
Cohesion: 0.26
Nodes (5): Path, The expanded wikitext for each template, keyed by template name., TemplateCache, A half-written cache must cost one re-fetch, never a failed run., TestTemplateCache

### Community 99 - "script_writer.ps1"
Cohesion: 0.22
Nodes (3): Fetch-And-Save(), Get-AutoBudget(), Save-Request()

### Community 100 - "test_context.py"
Cohesion: 0.24
Nodes (6): The writing contract, served with the context. Until now these three blocks…, The full contract, with the two choices the user makes folded in., writing_rules(), Tests for context bundle assembly and rendering., TestBudgeting, TestWritingRules

### Community 101 - "TestParsing"
Cohesion: 0.18
Nodes (4): parametrize, A passage naming nothing must not look like a failure., Wikis capitalise what they have named; the model does not., TestParsing

### Community 102 - "test_stores.py"
Cohesion: 0.22
Nodes (8): populated(), fixture, Tests for the fact store, graph traversal and lexical search., A small graph: Todo studies at Kyoto High and befriends Yuji., Five pages whose section headings repeat the way a wiki's do., sectioned(), store(), TestFacts

### Community 103 - "declared_lists"
Cohesion: 0.24
Nodes (7): declared_lists(), Any, Template names this wiki wants resolved, in declaration order., parametrize, Order is kept because a wiki declares its own preference., Off unless asked for: expanding every template would splice navboxes, infoboxes…, TestDeclaredLists

### Community 104 - "test_character_scoped.py"
Cohesion: 0.24
Nodes (6): _declared_name(), One declared member, as written, even when YAML disagreed. A member containing…, Questions about one character's abilities. Measured against online canon,…, YAML reads `Name: Value` inside an inline list as a mapping. `members:…, Every one was already being reported as a missing gold item., TestDeclaredNamesWithColons

### Community 105 - "test_gold_hygiene.py"
Cohesion: 0.31
Nodes (9): skipif, _cases(), Rules the gold sets themselves have to obey. `expect_any_text` was added for a…, A permissive assertion has to say why it is permissive., The alternatives must be names for the same thing. Two names for one marine is…, A case that expects nothing passes forever and measures nothing., test_any_of_lists_one_entity_not_several(), test_any_of_requires_a_justification() (+1 more)

### Community 106 - "paths_for"
Cohesion: 0.31
Nodes (4): paths_for(), Folding `previous` edges in beside `next` indiscriminately cut Dragon Ball from…, Filler and Super Dragon Ball Heroes are separate runs, not the story., TestOrder

### Community 107 - "Page-driven accuracy campaign (page-run, ~100 Q per top page)"
Cohesion: 0.22
Nodes (9): CitationGrammar (per-wiki citation vocabulary), Gate: eval --series jjk = 24/24, Rule: nothing about a series is hardcoded, Ontology / category discovery (derives the wiki's own taxonomy), Page-driven accuracy campaign (page-run, ~100 Q per top page), Per-wiki handling lives in series/<name>/overrides.yaml, Question batch JSON schema (questions[]/retired[]; id, kind, question, subject, tier, expect_mode, answer[], sources[], verified), Roster declaration format in series/<name>/overrides.yaml (+1 more)

### Community 108 - "_capped_beats"
Cohesion: 0.42
Nodes (3): _capped_beats(), Expand oversized beats into sourced, sentence-aligned parts., TestBeatSplitting

### Community 109 - "rosters"
Cohesion: 0.25
Nodes (7): The size a set's own name claims, if it claims one. `Seven Warlords of the…, The enumeration sets this series declares. Without this the registry is…, rosters(), _stated_count(), A set whose name counts itself is a free assertion to check. Most of what it…, `Extension Techniques` contains "ten" and states nothing., TestStatedCount

### Community 110 - "split_passage"
Cohesion: 0.36
Nodes (3): Split a section into overlapping passages at sentence boundaries. Overlap…, split_passage(), TestPassageSplitting

### Community 111 - "extract_series"
Cohesion: 0.22
Nodes (9): extract_series(), _guarded(), known_characters(), passages(), Settings, `folded name -> canonical`, built on the connection-owning thread., Read this series' declared narrative pages and store what they show., Return the exception instead of raising, so one page cannot stop a run. (+1 more)

### Community 112 - "parametrize"
Cohesion: 0.25
Nodes (5): parametrize, Bleach keeps its arcs only inside episode titles. Inventing an order would be…, TestDeclining, TestNoRegression, TestWantsChronology

### Community 113 - "TestHeading"
Cohesion: 0.22
Nodes (5): The arc section heading a script writes, from what the wiki wrote. `spans` is…, `Saitama Introduction Arc | MANGA CHAPTERS 1-4, EPISODE 1`. Asserted because…, An arc the anime has not reached must not be given an episode. The chapter half…, `50 chapters` says how many, not which, so it is not a locator. The re-crawl…, TestHeading

### Community 114 - "TestOwnerSurvivesParsing"
Cohesion: 0.22
Nodes (5): The regression: the field the pass keys on must reach the pass., `keep` is opt-in: the character-page pass must see the same rows., The pass tests `not owner`, so the key has to exist to be tested., The prompt asks for `owner` and the guard rejects a row without one. Asserted…, TestOwnerSurvivesParsing

### Community 115 - "App.js"
Cohesion: 0.31
Nodes (5): App(), theme, root, DashboardPage(), IngestionPage()

### Community 116 - "relation_coverage.py"
Cohesion: 0.39
Nodes (7): bank_path(), _descriptive(), load_bank(), main(), Path, Does the relations table hold the relationships the wiki documents? `canon-run`…, score()

### Community 117 - "discover_infoboxes"
Cohesion: 0.36
Nodes (4): discover_infoboxes(), Derive the vocabulary from the *shape* of each page's wikitext. This is what…, Type discovery from page shape, which is what makes this wiki-agnostic., TestStructuralDiscovery

### Community 118 - "instalment_number"
Cohesion: 0.39
Nodes (3): instalment_number(), Sort key for "Chapter 16" and friends, or None if it is not one. Returns…, TestInstalmentOrdering

### Community 119 - "TestGroundedness"
Cohesion: 0.25
Nodes (3): A name the passage never uses cannot be cited. Audited over 2,841 stored rows:…, `Equipment / Cannon Arm` names the thing its paragraph describes., TestGroundedness

### Community 120 - "manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 121 - "split_params"
Cohesion: 0.33
Nodes (4): Split a template body on ``|``, ignoring pipes inside nested constructs. A…, split_params(), Wikitext nests, so nothing here can be done with a flat regex., TestBalancedScanning

### Community 123 - "locator_from_title"
Cohesion: 0.38
Nodes (4): locator_from_title(), The locator a page carries by being that instalment. Not every wiki cites its…, parametrize, TestLocatorFromTitle

### Community 124 - "expected_type"
Cohesion: 0.38
Nodes (4): expected_type(), What this set is mostly made of, so the rest can be measured against it. Taken…, Better to return a mixed set than to guess which half is wrong., TestExpectedType

### Community 125 - "lexical.py"
Cohesion: 0.33
Nodes (6): build_match_query(), Any, BM25 search over the chunk text, via SQLite FTS5. Lexical retrieval is not a…, Turn free text into a safe FTS5 MATCH expression. Each term is quoted, and…, Rank chunks by BM25. FTS5's `bm25()` returns a negative number, more negative…, search()

### Community 126 - "TestOwnership"
Cohesion: 0.29
Nodes (4): Ownership is an edge, not a substring of the page's text., `Super Saiyan Rosé` belongs to Goku Black, and was Goku's., `owned_by` and `linked_from` are the same edges, read both ways., TestOwnership

### Community 127 - "TestAppearances"
Cohesion: 0.29
Nodes (3): A character's arcs, in story order: the spine of a life script. `The Entire…, A section is chunked at two levels, so the same prose arrives twice. Counted…, TestAppearances

### Community 128 - "TestCast"
Cohesion: 0.29
Nodes (3): Who is in an arc, read back off the character pages. The two wikis disagree…, `History` is a heading on places too, and a place is not a cast., TestCast

### Community 129 - "TestScaffold"
Cohesion: 0.29
Nodes (3): Two cuts of one section overlap without either containing the other. Garou's…, Garou is `ally` to Saitama only in the Ominous Future., TestScaffold

### Community 132 - "FakeClient"
Cohesion: 0.29
Nodes (5): fake_client(), FakeClient, fixture, Stand-in for LLMClient: returns canned answers, records the prompts., Patch the module's LLMClient so no test touches a model.

### Community 135 - "discounted_works"
Cohesion: 0.33
Nodes (4): discounted_works(), Any, The works this series does not count, lowercased., TestWorks

### Community 136 - "TestBeats"
Cohesion: 0.33
Nodes (3): Prose cut where its citations change: the shape a script is written in. The…, A beat's text is what gets read out; the ref is the tag on it., TestBeats

### Community 137 - "TestChains"
Cohesion: 0.33
Nodes (3): `Ash Crow --next--> Berserk (2016) Original Soundtrack` is a real edge.…, Berserk reported `Black Swordsman Arc` as its own chain and as part of the main…, TestChains

### Community 138 - "clean_all_files"
Cohesion: 0.50
Nodes (4): clean_all_files(), clean_text(), Clean and format text content, Clean all text files in directory

### Community 139 - "_item_name"
Cohesion: 0.40
Nodes (5): Match, _item_name(), The name a marker carries, or empty when it is not usable as one., Split one section body on its item markers. Returns the text before the first…, split_items()

### Community 140 - "_tail_pattern"
Cohesion: 0.40
Nodes (4): Pattern, SQLite's ``breadcrumb LIKE '%/ ' || leaf``, as a regex. Needed because `%` and…, How many pages carry each of these section headings. The wiki's own templates…, _tail_pattern()

### Community 141 - "model_health.py"
Cohesion: 0.50
Nodes (4): main(), probe(), Is the extraction model configured the way the run needs it? Two failures this…, `(healthy, why)` for the configured endpoint. Never raises.

### Community 142 - "TestSubject"
Cohesion: 0.40
Nodes (3): Which character the question is about., Otherwise "Every Saiyan transformation" is about the Saiyan article., TestSubject

### Community 144 - "Three doors: HTTP API :8000, Typer CLI, MCP stdio (wrap the same functions)"
Cohesion: 0.50
Nodes (4): FastAPI /context endpoint (the endpoint that matters), MCP stdio server (research / verify_script / script_path), Three doors: HTTP API :8000, Typer CLI, MCP stdio (wrap the same functions), Typer CLI (crawl/audit/index/query/eval/verify/script-gen/page-run)

### Community 145 - "owned_passages"
Cohesion: 0.50
Nodes (4): _matches(), owned_passages(), Whether a section path is one the series declared as holding abilities., Ability prose on the pages a character *owns*, not on their own page. One Piece…

## Knowledge Gaps
- **107 isolated node(s):** `$schema`, `model`, `npm`, `name`, `baseURL` (+102 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `FactStore` connect `FactStore` to `Roster`, `TestCast`, `roster.py`, `EpisodeIndex`, `Member`, `TestScaffold`, `TestGraph`, `cli.py`, `facts.py`, `TestBeats`, `TestChains`, `content_words`, `_tail_pattern`, `TestLexicalSearch`, `TestSubject`, `chronology.py`, `build_roster`, `owned_passages`, `drop_off_owner`, `TestSpans`, `Annotated`, `ingest/abilities.py`, `NarrativeRetriever`, `TestEntityLinking`, `TestNodes`, `TestSchema`, `hybrid.py`, `_semantic_reason`, `Passage`, `main.py`, `.test_a_fusion_is_not_a_form`, `test_relation_coverage.py`, `load_overrides`, `TestKinds`, `context.py`, `relations.py`, `parse_constraints`, `build.py`, `catalogue.py`, `Locator`, `test_ability_class.py`, `norm`, `store_for`, `test_ability_extraction.py`, `scriptengine/config.py`, `drop_unnamed`, `LLMClient`, `race_vocabulary`, `collect_abilities`, `diagnose_misses.py`, `TestLocators`, `side_fighters`, `export_obsidian`, `export.py`, `test_citations.py`, `Counter`, `subject_ranking`, `TestPagesPerSection`, `attribute`, `TestParsing`, `test_stores.py`, `test_character_scoped.py`, `paths_for`, `rosters`, `extract_series`, `parametrize`, `TestHeading`, `relation_coverage.py`, `TestGroundedness`, `TestEpisodeIndex`, `locator_from_title`, `expected_type`, `lexical.py`, `TestOwnership`, `TestAppearances`?**
  _High betweenness centrality (0.393) - this node is a cross-community bridge._
- **Why does `Counter` connect `Counter` to `FactStore`, `step2_build_graph_v6.py`, `cli.py`, `facts.py`, `race_vocabulary`, `build_graph`, `build_graph`, `diagnose_misses.py`, `norm`, `discover_infoboxes`, `WikiPage`, `_agree`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Why does `Settings` connect `Settings` to `roster.py`, `TestThinkingIsDetectable`, `series_paths`, `test_script_gen.py`, `Annotated`, `ingest/abilities.py`, `test_question_bank.py`, `WikiPage`, `hybrid.py`, `questions.py`, `get_settings`, `templates.py`, `test_llm_client.py`, `run`, `canon_run.py`, `context.py`, `relations.py`, `build.py`, `catalogue.py`, `scriptengine/config.py`, `LLMClient`, `harness.py`, `test_model_residency.py`, `TestLocalBackend`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Are the 118 inferred relationships involving `FactStore` (e.g. with `ContextRequest` and `SearchRequest`) actually correct?**
  _`FactStore` has 118 INFERRED edges - model-reasoned connections that need verification._
- **Are the 26 inferred relationships involving `EpisodeIndex` (e.g. with `FactStore` and `Route`) actually correct?**
  _`EpisodeIndex` has 26 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `model`, `npm` to the rest of the system?**
  _107 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Roster` be split into smaller, more focused modules?**
  _Cohesion score 0.03994845360824742 - nodes in this community are weakly interconnected._