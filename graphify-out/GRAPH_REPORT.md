# Graph Report - E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine  (2026-08-01)

## Corpus Check
- 67 files · ~53,850 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1221 nodes · 2520 edges · 69 communities (56 shown, 13 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 141 edges (avg confidence: 0.68)
- Token cost: 433,769 input · 0 output

## Community Hubs (Navigation)
- Index Building & Alias Harvesting
- Ontology & Type Discovery
- Legacy Graph Builder v6
- CLI & Configuration
- Legacy Graph Builder v3
- Qdrant Vector Store
- React UI Dependencies
- Narrative Beats & Timeline
- Electron IPC Channels
- Legacy HTML Cleaner
- Legacy Graph Builder v2
- Settings & Device Resolution
- CLI Command Surface
- Wikitext Template Scanning
- Node Package Manifests
- Legacy MediaWiki Crawler
- Legacy Chunk & Embed
- Crawler Enumeration & Retry
- FastAPI Routes & Schemas
- FactStore SQLite Access
- Electron Main Process
- Entity Linking (word vs substring)
- Legacy Graph Builder v1
- Project Overview & Docs
- Legacy Fictional Config
- Legacy Qwen Generation
- Re-extraction from Wikitext
- Series Layout & Overrides
- Context Bundle & Token Budget
- Model Loading & VRAM Sharing
- Graph Traversal Queries
- FactStore Tests
- Series Filesystem Paths
- Wikilinks & Title Normalisation
- FTS5 Lexical Retrieval
- Passage Deduplication
- Gold Eval Harness
- Crawl Politeness & Audit Rationale
- Embedding Model Config
- Hybrid Retrieval Pipeline
- Cross-Encoder Reranking
- Markup Stripping
- Instalment Ordering
- Section Splitting
- Wikitable Flattening
- Legacy BM25 & Vector Search
- RRF Fusion
- Citation Extraction
- Legacy Neo4j Cypher Traversal
- LLM HTTP Client
- Graph Traversal Tests
- Retrieval Result Shapes
- Web App Manifest
- Balanced Template Scanning
- HybridRetriever Lifecycle
- Lexical Search Tests
- Clock Time Extraction
- FactStore Schema Lifecycle
- Legacy JJK Text Cleaner
- Page Type Detection
- api package
- eval package
- index package
- ingest package
- scriptengine package
- llm package
- retrieve package
- stores package
- Electron Preload Bridge

## God Nodes (most connected - your core abstractions)
1. `FactStore (SQLite documents, graph, facts, FTS)` - 74 edges
2. `SeriesPaths (per-series filesystem layout)` - 40 edges
3. `WikiPage (the serialised unit of ingestion)` - 37 edges
4. `VectorStore (embedded Qdrant per series)` - 37 edges
5. `Ontology (a wiki's own type vocabulary)` - 33 edges
6. `Settings (process-wide config)` - 32 edges
7. `get_settings()` - 28 edges
8. `Embedder (lazy BGE bi-encoder with idle unload)` - 26 edges
9. `chunk_page (three-level chunking)` - 25 edges
10. `build_index (corpus to queryable stores)` - 24 edges

## Surprising Connections (you probably didn't know these)
- `v6 chronology edges for chapter / episode / volume` --semantically_similar_to--> `mode: "narrative" — passages in narrative order, not similarity order`  [INFERRED] [semantically similar]
  legacy/step2_build_graph_v6.py → docs/API.md
- `v2 junk-page filters and hardcoded JJK arc aliases` --semantically_similar_to--> `Rejection list (LICENSES.chromium.txt, angular.txt, test.txt)`  [INFERRED] [semantically similar]
  legacy/step2_build_graph_v2.py → docs/EXTRACTION_AUDIT.md
- `clean_text (in-place JJK-specific capitalisation rewriter)` --superseded_by--> `Rule: if a fix mentions a series name and lives in a .py file, it is in the wrong place`  [EXTRACTED]
  legacy/clean_all_files.py → docs/ARCHITECTURE.md
- `RAGPipeline (simple vs multi-hop QA routing)` --superseded_by--> `POST /context (token-budgeted bundle for the script-writing model)`  [INFERRED]
  legacy/step4_generation.py → docs/API.md
- `Hardcoded 'E:\VS CODE\...' corpus path (does not exist)` --superseded_by--> `Self-contained series/<name>/ folder (raw, wikitext, facts.db, vectors, manifest)`  [INFERRED]
  legacy/step2_build_graph_v3.py → docs/ADDING_A_SERIES.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Four graph-builder iterations (~3,700 lines) rebuilding entities from prose** — legacy_step2_build_graph_graphbuilder, legacy_step2_build_graph_v2_junk_filters, legacy_step2_build_graph_v3_resolve_alias, legacy_step2_build_graph_v6_nodeevidence, legacy_step2_build_graph_v6_relationevidence [EXTRACTED 1.00]
- **vector u BM25 u graph -> RRF -> cross-encoder -> parent expansion (the shape that was kept)** — legacy_step5_retrieval_hybridretriever, legacy_step5_retrieval_bm25index, legacy_step5_retrieval_graphretriever, legacy_step5_retrieval_rrf, legacy_step5_retrieval_rerank, legacy_step5_retrieval_expand_to_parent, docs_architecture_retrieve_hybrid [EXTRACTED 1.00]
- **Section-detection failure cascade: bare 'appearance' vs '## Appearance' collapsed every doc, killing chunk hierarchy and parent expansion** — legacy_step2_build_graph_is_section_header, legacy_step3_chunk_and_embed_build_hierarchical_chunks, legacy_step5_retrieval_expand_to_parent, docs_extraction_audit_mean_sections, docs_architecture_prop_sections [INFERRED 0.88]
- **MediaWiki API to SQLite/Qdrant ingestion flow** — scriptengine_ingest_crawler_crawl, scriptengine_ingest_crawler_build_page, scriptengine_ingest_wikitext_split_sections, scriptengine_ingest_documents_wikipage, scriptengine_index_chunker_chunk_page, scriptengine_stores_facts_factstore, scriptengine_stores_vectors_vectorstore [EXTRACTED 1.00]
- **Series-agnostic type discovery (no code per wiki)** — scriptengine_ingest_ontology_ontology, scriptengine_ingest_ontology_discover_infoboxes, scriptengine_ingest_wikitext_infobox_candidates, scriptengine_ingest_ontology_type_for_templates, scriptengine_config_load_overrides, scriptengine_ingest_crawler_load_extracted [EXTRACTED 1.00]
- **SQLite rowid as vector point id — the shared identity contract** — scriptengine_stores_facts_factstore, scriptengine_stores_vectors_vectorstore, scriptengine_index_build_build_index, scriptengine_stores_vectors_rationale_rmtree_stale_rowid_collision, scriptengine_index_build_rationale_vector_count_mismatch [EXTRACTED 1.00]
- **Hybrid retrieval pipeline: link, expand, retrieve three ways, fuse, rerank, dedup, expand parents** — scriptengine_retrieve_hybrid_entity_linking_stage, scriptengine_retrieve_hybrid_graph_expansion_stage, scriptengine_retrieve_hybrid_lexical_leg, scriptengine_retrieve_hybrid_vector_search, scriptengine_retrieve_hybrid_graph_leg, scriptengine_retrieve_hybrid_reciprocal_rank_fusion, scriptengine_retrieve_hybrid_rerank_stage, scriptengine_retrieve_hybrid_deduplicate, scriptengine_retrieve_hybrid_parent_expansion_stage [EXTRACTED 1.00]
- **Context delivery path: HTTP request to ordered, cited, budgeted bundle** — scriptengine_api_main_route_context, scriptengine_api_main_contextrequest, scriptengine_api_context_build_context, scriptengine_api_context_qa_context, scriptengine_api_context_narrative_context, scriptengine_retrieve_hybrid_search_pipeline, scriptengine_retrieve_narrative_timeline, scriptengine_api_context_render_prompt [EXTRACTED 1.00]
- **Renderer to service contract: preload exposes, main handles, FastAPI serves** — ui_electron_preload_js_electron_bridge, ui_electron_main_js_setupipc, ipc_get_context, ipc_get_timeline, ipc_get_facts, ipc_search, ipc_list_series, ipc_health_check, scriptengine_api_main_app [EXTRACTED 1.00]

## Communities (69 total, 13 thin omitted)

### Community 0 - "Index Building & Alias Harvesting"
Cohesion: 0.05
Nodes (58): Progress, _harvest_link_aliases (aliases from link display text), _load_chunks (chunk rows, parents, chunk_nodes), _load_documents(), _load_graph (nodes, aliases, facts, edges), Insert nodes, aliases, facts and edges. Nodes are created for every page first,…, Learn the names people actually use, from how they write their links. A wiki's…, Insert chunks, wire parents, and link each chunk to the entities it names.… (+50 more)

### Community 1 - "Ontology & Type Discovery"
Cohesion: 0.05
Nodes (39): Rationale: every config value must have a caller, Rationale: series-specific rules live only in overrides.yaml, never in .py, Rationale: a broken extractor reports no error at all, build_ontology(), build_ontology_from_transclusions(), discover_infoboxes (shape-voted type discovery), _is_module(), learn_field_labels (Portable Infobox schema labels) (+31 more)

### Community 2 - "Legacy Graph Builder v6"
Cohesion: 0.11
Nodes (41): add_node(), add_relation(), best_kind(), build_graph(), BuildResult, classify_title_part(), clean_text(), doc_type_from_title() (+33 more)

### Community 3 - "CLI & Configuration"
Cohesion: 0.09
Nodes (42): CLI crawl command, index(), cli._load_overrides (duplicated overrides reader), Build the fact store, graph, BM25 index and vectors., load_overrides (series overrides.yaml reader), Configuration for ScriptEngine. Every value here is either read by running code…, Filesystem layout for a single series. Each series is fully self-contained:…, Create the directory tree for this series. (+34 more)

### Community 4 - "Legacy Graph Builder v3"
Cohesion: 0.11
Nodes (31): _add_node(), best_kind(), build_graph(), _classify_title_part(), _clean_battle_part(), clean_text(), entity_kind_from_ner(), extract_candidates() (+23 more)

### Community 5 - "Qdrant Vector Store"
Cohesion: 0.08
Nodes (19): Defect: stale Qdrant point ids resolve to whatever row holds that rowid now, Rationale: more points than chunks means a corrupt store, not untidiness, Rationale: a thin run must never overwrite a richer manifest, Any, Path, QdrantClient, Nearest chunks, optionally restricted to a level or a set of pages. Filtering…, Embedded vector storage for one series. (+11 more)

### Community 6 - "React UI Dependencies"
Cohesion: 0.05
Nodes (37): @emotion/react, @emotion/styled, @mui/icons-material, @mui/material, react, react-dom, react-router-dom, react-scripts (+29 more)

### Community 7 - "Narrative Beats & Timeline"
Cohesion: 0.09
Nodes (16): Flatten a bundle into plain text, for callers that just want a string. Offered…, render_prompt (flatten a bundle without dropping citations), Beat (one ordered step of a narrative), Narrative, Any, Return `subject` as ordered beats. Resolves the subject through the alias table…, A page's own sections, in the order the article presents them., One beat per linked page, in instalment order. (+8 more)

### Community 8 - "Electron IPC Channels"
Cohesion: 0.11
Nodes (30): Defect: UI called /api/v1/... endpoints that were never written, IPC channel 'check-series-exists' (filesystem scan of crawl dir), IPC event 'crawl-progress' (crawler stdout/stderr stream), IPC channel 'crawl-series' (spawns scriptengine.cli crawl), IPC channel 'get-context', IPC channel 'get-facts', IPC channel 'get-timeline', IPC channel 'health-check' (+22 more)

### Community 9 - "Legacy HTML Cleaner"
Cohesion: 0.16
Nodes (32): GET /facts/{entity} — exact infobox-derived lookup, not a search, Rationale: facts are stored as facts, never flattened into prose and re-extracted, ingest/wikitext.py (infobox to facts, [[links]] to edges, {{Ref}} to citations), build_citation_map(), clean_text(), compact_spaces(), convert_file(), detect_page_type() (+24 more)

### Community 10 - "Legacy Graph Builder v2"
Cohesion: 0.19
Nodes (18): build_graph(), build_title_sets(), canonical_key(), extract_from_document(), extract_participants_from_battle_title(), find_arcs_in_text(), gather_titles(), GraphBuilder (+10 more)

### Community 11 - "Settings & Device Resolution"
Cohesion: 0.11
Nodes (14): BaseSettings, main(), get_settings(), Process-wide settings, overridable by env or `.env`., Resolve ``auto`` to a concrete torch device without importing torch eagerly., Settings (process-wide config), Embedding, with the GPU treated as a shared resource. ComfyUI and a resident…, select_impersonation() (+6 more)

### Community 12 - "CLI Command Surface"
Cohesion: 0.12
Nodes (20): command, audit(), config(), crawl(), list_series(), _load_overrides(), query(), ScriptEngine command line. python -m scriptengine.cli --help Commands are added… (+12 more)

### Community 13 - "Wikitext Template Scanning"
Cohesion: 0.12
Nodes (22): find_templates(), _flatten_links(), _flatten_one_table(), infobox_candidates (structural infobox detection), _is_media_only(), _is_namespaced(), parse_template(), Wikitext parsing. Wikitext cannot be parsed with regular expressions. Templates… (+14 more)

### Community 14 - "Node Package Manifests"
Cohesion: 0.09
Nodes (21): concurrently, electron, fs-extra, dependencies, axios, fs-extra, description, devDependencies (+13 more)

### Community 15 - "Legacy MediaWiki Crawler"
Cohesion: 0.18
Nodes (9): AnimeCrawler (legacy MediaWiki crawler), _fandom_api_base(), _is_fandom(), Any, BeautifulSoup, Fandom wiki crawler using MediaWiki API — bypasses Cloudflare entirely., _root_domain(), _select_impersonation() (+1 more)

### Community 16 - "Legacy Chunk & Embed"
Cohesion: 0.15
Nodes (21): 3-level hierarchical chunker (doc / section / paragraph), chunk_section(), embed_chunks(), ingest_all(), is_section_header(), load_embedder(), load_entity_list(), parse_wiki_file() (+13 more)

### Community 17 - "Crawler Enumeration & Retry"
Cohesion: 0.12
Nodes (12): EnumerationFailed, RuntimeError, Fetches a wiki into `series/<name>/wikitext/*.json`., One API call, with retries, backoff, and rate-limit compliance., See `list_all_pages`. Raises `EnumerationFailed` rather than returning an empty…, Article titles in the main namespace., Pages in the `Template:` namespace — the wiki's own vocabulary., Other names this page answers to, for entity linking later. (+4 more)

### Community 18 - "FastAPI Routes & Schemas"
Cohesion: 0.19
Nodes (20): BaseModel, get, post, context(), ContextRequest (series, query, mode, token_budget, as_prompt), facts(), health(), list_series() (+12 more)

### Community 19 - "FactStore SQLite Access"
Cohesion: 0.10
Nodes (5): FactStore (SQLite documents, graph, facts, FTS), Any, Path, Create or update an entity. A node is often created as an unresolved link…, Read/write access to one series' `facts.db`.

### Community 20 - "Electron Main Process"
Cohesion: 0.20
Nodes (19): { app, BrowserWindow, ipcMain, dialog }, APP_PATHS, axios, checkDocker(), checkGit(), checkNode(), checkOllama(), checkPython() (+11 more)

### Community 21 - "Entity Linking (word vs substring)"
Cohesion: 0.16
Nodes (17): retrieve/hybrid.py (vector u BM25 u graph, RRF, cross-encoder, parent expansion), Word-boundary entity linking against the alias table, Find which known entities are mentioned in this chunk., tag_entities (substring entity tagging, every entity x every chunk), Import of python.step3_retrieval (module does not exist), expand_to_parent (level-2 chunk to level-1 section context), extract_query_entities (substring query entity linking), HybridRetriever (legacy hybrid retrieval orchestrator) (+9 more)

### Community 22 - "Legacy Graph Builder v1"
Cohesion: 0.15
Nodes (12): build_graph(), extract_entities (spaCy NER over rendered prose), GraphBuilder v1 (Neo4j writer), parse_wiki_file(), Step 1: Parse wiki text files → extract entities/relationships → build Neo4j…, Extract: - Named entities (characters, techniques, locations, arcs) -…, Run once — creates indexes for fast lookup., Create or update a Document node. (+4 more)

### Community 23 - "Project Overview & Docs"
Cohesion: 0.15
Nodes (19): ScriptEngine (universal knowledge engine over Fandom wikis), scriptengine/config.py — every value here has a caller, mode: "narrative" — passages in narrative order, not similarity order, POST /context (token-budgeted bundle for the script-writing model), api/main.py — FastAPI service on :8000, Rationale: BM25 is not optional — names are where dense retrieval is weakest, facts.db — one SQLite file per series (documents, sections, nodes, edges, facts), SQLite FTS5 on-disk BM25 index (+11 more)

### Community 24 - "Legacy Fictional Config"
Cohesion: 0.11
Nodes (15): ChunkerConfig, DatabaseConfig, LangGraphConfig, OllamaConfig, QdrantConfig, Anime Script AI - Configuration Module Centralized configuration for all…, PostgreSQL database configuration, Qdrant vector database configuration (+7 more)

### Community 25 - "Legacy Qwen Generation"
Cohesion: 0.18
Nodes (11): build_context(), decompose_query(), is_multihop(), In-process Qwen2.5-7B loader (transformers, device_map=cuda), RAGPipeline (simple vs multi-hop QA routing), Step 4: Query decomposition for multi-hop questions + Qwen generation This…, Use Qwen to decompose a complex query into simpler sub-questions., Build a clean context string for Qwen. Includes retrieved chunks and relevant… (+3 more)

### Community 26 - "Re-extraction from Wikitext"
Cohesion: 0.17
Nodes (12): Rationale: indexing is a rebuild, making the result a pure function of the corpus, WikiCrawler.build_page (API response to WikiPage), Turn one API response into a fully extracted `WikiPage`., Re-run extraction on a page's stored wikitext. Fetching a page is expensive;…, Rationale: fetching is expensive, parsing is not — keep the wikitext, Rationale: subpages inherit the parent type; an untyped parent yields 'subpage', reextract (re-parse stored wikitext), facts_from_infobox (parameters to Facts) (+4 more)

### Community 27 - "Series Layout & Overrides"
Cohesion: 0.15
Nodes (15): scriptengine.cli (crawl / audit / index / query / eval), constants.json path and module registry, series/<name>/overrides.yaml (skip_categories, type_aliases), Self-contained series/<name>/ folder (raw, wikitext, facts.db, vectors, manifest), index/build.py (section-driven chunking and embedding), Rule: if a fix mentions a series name and lives in a .py file, it is in the wrong place, Rationale: schemaless labels are data, not DDL — why SQLite beat Kuzu, scriptengine.cli audit --series <id> --sample 50 (+7 more)

### Community 28 - "Context Bundle & Token Budget"
Cohesion: 0.19
Nodes (12): Truncation happens at beat boundaries, never mid-beat, build_context (the shape of the whole product), estimate_tokens (deliberately pessimistic chars-per-token), _narrative_context (narrative-mode bundle), Ordering is preserved, not re-sorted by relevance, Any, _qa_context (qa-mode bundle), Assembling the context bundle a script-writing model consumes. This is the… (+4 more)

### Community 29 - "Model Loading & VRAM Sharing"
Cohesion: 0.15
Nodes (10): LLMClient (OpenAI-compatible HTTP client), Rationale: talk to an already-resident model instead of paying for the weights twice, Rationale: ComfyUI and resident models cannot share VRAM, Embedder (lazy BGE bi-encoder with idle unload), Lazily-loaded sentence-transformer with an idle timeout., Release the model and its VRAM. Returns whether anything was freed., Rationale: BGE query and passage prefixes encode an asymmetry one prefix collapses, Rationale: device='cuda' hardcoded in five places against a CPU-only torch build (+2 more)

### Community 30 - "Graph Traversal Queries"
Cohesion: 0.12
Nodes (6): Row, Find entities mentioned in `text`, matching on whole words only. The previous…, Entities reachable within `depth` hops, nearest first. Edges are traversed in…, Relationships touching these entities, strongest evidence first., Structured facts for one entity. A lookup, not a search., A document's sections in page order — the basis of narrative retrieval.

### Community 31 - "FactStore Tests"
Cohesion: 0.13
Nodes (8): populated(), fixture, Tests for the fact store, graph traversal and lexical search., A small graph: Todo studies at Kyoto High and befriends Yuji., store(), TestFacts, TestNodes, TestSchema

### Community 32 - "Series Filesystem Paths"
Cohesion: 0.13
Nodes (8): Path, Rendered HTML, as returned by ``action=parse``., Raw wikitext plus per-page API metadata, one JSON file per page., SQLite: documents, sections, nodes, edges, facts, and the FTS5 index., Qdrant local-mode storage directory., What was crawled, when, and from which wiki. Small enough to commit., Extraction audit reports., Optional per-series YAML. Series-specific handling lives here, never in code.

### Community 33 - "Wikilinks & Title Normalisation"
Cohesion: 0.17
Nodes (8): Rationale: wiki redirects miss the bare 'Todo' that prose links use constantly, extract_links (wikilink harvesting), normalise_title (MediaWiki title rules), Collect every ``[[Target|Display]]`` in order of appearance. Category, File and…, Apply MediaWiki's own title rules so one page yields one node. MediaWiki…, Rationale: dropping interwiki links lost the voice actor's name, Rationale: without title folding the graph grew both Grade and grade, TestLinks

### Community 34 - "FTS5 Lexical Retrieval"
Cohesion: 0.15
Nodes (15): Rationale: facts are stored exact in SQLite and rendered searchable in the card, Retriever leg: FTS5 lexical search, Rationale: substring matching tagged 'Ryu' inside 'Ryomen' and silently dropped chunks, build_match_query (safe FTS5 MATCH expression), Any, Turn free text into a safe FTS5 MATCH expression. Each term is quoted, and…, Rank chunks by BM25. FTS5's `bm25()` returns a negative number, more negative…, Rationale: names are exactly where dense vectors are weakest (+7 more)

### Community 35 - "Passage Deduplication"
Cohesion: 0.29
Nodes (8): Defect: overlapping chunks surface the same content two or three times, _deduplicate (opening-shingle overlap filter), Passage, Drop near-identical passages produced by chunk overlap. Consecutive chunks…, One retrieved passage, with everything needed to cite it., passage(), Tests for fusion, deduplication and narrative ordering., TestDeduplication (overlapping passages collapse, first wins)

### Community 36 - "Gold Eval Harness"
Cohesion: 0.27
Nodes (13): gold_jjk.json (fact / alias / semantic / lexical / multihop / narrative), evaluate (run every gold question, score by kind), _evaluate_narrative (enough beats, in order, with times), _evaluate_retrieval (doc hit + text hit), _hit_docs(), _hit_text(), Blunt, judge-free scoring keeps verdicts fast and stable, load_gold() (+5 more)

### Community 37 - "Crawl Politeness & Audit Rationale"
Cohesion: 0.17
Nodes (13): Crawl politeness: 10 workers, 0.2 s delay, honour HTTP 429 Retry-After, ingest/crawler.py (MediaWiki-API-first crawler), Rationale: no daemon — the Docker daemon was not installed on the target machine, action=parse&prop=sections (real heading tree from the API), Qdrant local (embedded) mode vector store, mean_sections — the single most important audit metric, Rationale: a broken extractor is silent — audits exist to catch it, curl_cffi browser TLS impersonation (+5 more)

### Community 38 - "Embedding Model Config"
Cohesion: 0.18
Nodes (9): CrossEncoder, model_idle_unload_seconds and device: auto degrading to CPU, EmbeddingConfig (bge-m3, device hardcoded to cuda), Embedding model configuration, embed_query(), Models singleton with device="cuda" hardcoded, SentenceTransformer, Embed query with BGE query prefix. (+1 more)

### Community 39 - "Hybrid Retrieval Pipeline"
Cohesion: 0.24
Nodes (8): Defect: substring entity matching ("Todo" inside "Todoroki", "Ryu" inside "Ryomen"), Stage 1: query entity linking via alias table, Stage 2: graph neighbour expansion (1-2 hops), Retriever leg: chunks reachable from graph nodes, Stage 7: expand survivors to their parent section, Hybrid search pipeline (search()), Retriever leg: dual dense search (_vector_search), TestEntityLinking (whole-word alias matching)

### Community 40 - "Cross-Encoder Reranking"
Cohesion: 0.20
Nodes (5): Cross-encoder rerank, under the same load/unload discipline., Score each passage against the query. A cross-encoder reads the query and the…, Free the GPU if nothing has used the model recently., Reranker (cross-encoder shortlist scorer), Stage 6: cross-encoder rerank of the shortlist

### Community 41 - "Markup Stripping"
Cohesion: 0.26
Nodes (6): Reduce wikitext to readable prose. Citations are removed rather than flattened.…, Rationale: inlined citations made vectors encode bibliography, Rationale: gallery bodies leaked image filenames into timeline prose, Rationale: longest-argument heuristic yields Japanese script and furigana, strip_markup (wikitext to prose), TestMarkupStripping

### Community 42 - "Instalment Ordering"
Cohesion: 0.27
Nodes (7): Across-page ordering: linked instalments as beats (arc ToC fallback), instalment_number (kind, number sort key), _ordered_related (numbered instalments in numeric order), _participants (characters from strong infobox edges), Sort key for "Chapter 16" and friends, or None if it is not one. Returns…, timeline() — subject resolved to ordered beats, TestInstalmentOrdering (numeric, not alphabetical)

### Community 43 - "Section Splitting"
Cohesion: 0.25
Nodes (7): Defect: heading detector never matched, so every page became one unnamed section, Section, Split a page into its lead and its sections. ``api_sections`` is the section…, Rationale: API supplies hierarchy, wikitext supplies content (offsets shift), split_sections (lead + section tree), Within-page ordering: a page's own sections in article order, TestSections (a page with headings never collapses to one section)

### Community 44 - "Wikitable Flattening"
Cohesion: 0.25
Nodes (6): flatten_tables (wikitables to readable rows), Turn wikitables into readable lines instead of deleting them. On a Fandom wiki…, Rationale: tables carry the most factual content, so never delete them, Tests for wikitext parsing. The cases here are drawn from real Jujutsu Kaisen…, Tables carry content on a Fandom wiki, not decoration., TestTables

### Community 45 - "Legacy BM25 & Vector Search"
Cohesion: 0.31
Nodes (5): BM25Index (rank_bm25 rebuilt in RAM from a full Qdrant scroll), QdrantClient, Search Qdrant by vector similarity. Optionally filter by entities mentioned in…, Pull all level-2 chunks from Qdrant and build BM25 index., vector_search()

### Community 46 - "RRF Fusion"
Cohesion: 0.31
Nodes (5): semantic-04: rephrase an ambiguous question rather than tune the retriever, Focused-vs-open dense search trade-off (Binding Vow blindfold), Combine rankings by reciprocal rank. RRF needs no score calibration between…, Stage 5: reciprocal rank fusion (RRF), TestFusion (agreement between retrievers is evidence)

### Community 47 - "Citation Extraction"
Cohesion: 0.22
Nodes (6): Citation (structured source reference), A reference to a source work. Fandom wikis cite through templates such as…, A short human-readable form, e.g. ``Ref vol=5 page=26``., extract_citations (recursive citation capture), Collect citation templates, recursing so nested ones are not missed., TestCitations

### Community 48 - "Legacy Neo4j Cypher Traversal"
Cohesion: 0.25
Nodes (5): Recursive-CTE graph traversal in SQLite, Cypher [r*1..$depth] parameterised variable-length bound, GraphRetriever (Neo4j Cypher traversal), Given entity names, traverse graph to find related entities. Returns list of…, Return document titles that mention any of these entities.

### Community 49 - "LLM HTTP Client"
Cohesion: 0.22
Nodes (5): LLMClient, LLMUnavailable, RuntimeError, No model endpoint answered. Callers should degrade, not crash., Whether an endpoint is reachable. Never raises.

### Community 51 - "Retrieval Result Shapes"
Cohesion: 0.25
Nodes (5): Facts and relations count as retrieved text, Any, Dense search, run both narrowed to graph-selected pages and wide open. Running…, The full result of a query, including how it was reached., Retrieved (query result: passages, entities, facts, relations)

### Community 52 - "Web App Manifest"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 53 - "Balanced Template Scanning"
Cohesion: 0.33
Nodes (4): Split a template body on ``|``, ignoring pipes inside nested constructs. A…, split_params(), Wikitext nests, so nothing here can be done with a flat regex., TestBalancedScanning

### Community 56 - "Clock Time Extraction"
Cohesion: 0.53
Nodes (3): extract_time (clock time out of a section heading), Pull a clock time out of a section heading, if it has one., TestTimeExtraction (meridiem normalised from headings)

### Community 58 - "Legacy JJK Text Cleaner"
Cohesion: 0.50
Nodes (4): clean_all_files(), clean_text (in-place JJK-specific capitalisation rewriter), Clean and format text content, Clean all text files in directory

### Community 59 - "Page Type Detection"
Cohesion: 0.50
Nodes (4): Rationale: a Fandom wiki already publishes its own structure, Per-wiki type vocabulary discovery from *Infobox* templates, ingest/ontology.py (page types discovered from infobox templates), _detect_page_type (URL-substring page typing)

## Ambiguous Edges - Review These
- `Neo4jConfig (bolt://localhost:7687, conflicting password)` → `GraphBuilder v1 (Neo4j writer)`  [AMBIGUOUS]
  legacy/README.md · relation: conceptually_related_to
- `ElasticsearchConfig (BM25 service that was never used)` → `BM25Index (rank_bm25 rebuilt in RAM from a full Qdrant scroll)`  [AMBIGUOUS]
  legacy/README.md · relation: conceptually_related_to
- `EmbeddingConfig (bge-m3, device hardcoded to cuda)` → `Models singleton with device="cuda" hardcoded`  [AMBIGUOUS]
  legacy/README.md · relation: conceptually_related_to
- `HybridRetriever (legacy hybrid retrieval orchestrator)` → `Import of python.step3_retrieval (module does not exist)`  [AMBIGUOUS]
  legacy/step4_generation.py · relation: references
- `Rationale: field labels are enrichment, so failures are silent by design` → `Rationale: a broken extractor reports no error at all`  [AMBIGUOUS]
  scriptengine/ingest/ontology.py · relation: conceptually_related_to
- `release_models (hand the GPU back to ComfyUI)` → `startAPIServer (spawns python -m scriptengine.api.main)`  [AMBIGUOUS]
  scriptengine/retrieve/hybrid.py · relation: conceptually_related_to
- `GET /health` → `Stale service panel (Postgres/Neo4j/Elasticsearch/Redis, result.services)`  [AMBIGUOUS]
  ui/src/pages/DashboardPage.js · relation: shares_data_with
- `Defect: UI called /api/v1/... endpoints that were never written` → `Stale service panel (Postgres/Neo4j/Elasticsearch/Redis, result.services)`  [AMBIGUOUS]
  ui/src/pages/DashboardPage.js · relation: conceptually_related_to

## Knowledge Gaps
- **80 isolated node(s):** `name`, `version`, `description`, `main`, `start` (+75 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Neo4jConfig (bolt://localhost:7687, conflicting password)` and `GraphBuilder v1 (Neo4j writer)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `ElasticsearchConfig (BM25 service that was never used)` and `BM25Index (rank_bm25 rebuilt in RAM from a full Qdrant scroll)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `EmbeddingConfig (bge-m3, device hardcoded to cuda)` and `Models singleton with device="cuda" hardcoded`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `HybridRetriever (legacy hybrid retrieval orchestrator)` and `Import of python.step3_retrieval (module does not exist)`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `Rationale: field labels are enrichment, so failures are silent by design` and `Rationale: a broken extractor reports no error at all`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `release_models (hand the GPU back to ComfyUI)` and `startAPIServer (spawns python -m scriptengine.api.main)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `GET /health` and `Stale service panel (Postgres/Neo4j/Elasticsearch/Redis, result.services)`?**
  _Edge tagged AMBIGUOUS (relation: shares_data_with) - confidence is low._