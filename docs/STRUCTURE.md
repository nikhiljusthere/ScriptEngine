# Structure

A full inventory of what's on disk and what each piece does. `ARCHITECTURE.md`
explains the design decisions and why the pipeline is shaped this way; this
document is the complementary map — every directory, every module, what it's
for. Start with `ARCHITECTURE.md` if you want the reasoning; come here when
you need to find where something lives.

## Top-level layout

```
ScriptEngine/
  scriptengine/       the engine itself (Python package, see below)
  ui/                 Electron + React desktop shell
  series/              one self-contained folder per series (gitignored)
  legacy/              the retired first-generation pipeline, kept for reference
  docs/                architecture and operational docs (this file included)
  questions/           the online-canon question bank, one JSON per series (tracked)
  reports/             one folder per measurement run, plus index.md (tracked)
  tests/               pytest suite, mirrors scriptengine/ module layout
  sample scripts/      published reference scripts defining the house style
  scripts output/      gitignored working dir: fetched context + finished scripts
  graphify-out/        generated knowledge-graph of this codebase
  out/                 gitignored legacy raw crawl dump (pre-rewrite corpus)
  STARTME.md           session entry point for the script-writing workflow
  README.md            project pitch, install, usage, live catalogue stats
  CLAUDE.md             agent working agreements
  script_writer.ps1     interactive/headless request builder + context fetcher
  start_scriptengine.py / .bat   venv-resolving API launcher
  requirements.txt, package.json, constants.json, .env (gitignored)
  ScriptEngine RAG Answer.json   ComfyUI workflow JSON (repo-root copy)
```

Languages: Python 3.12 (core engine), JavaScript/React + Electron (optional
desktop UI), PowerShell (`script_writer.ps1`, `start_scriptengine.bat`), SQL
(`stores/schema.sql`). Dependency tooling: `uv` + `requirements.txt` for
Python, `npm` for the root Electron shell and `ui/`. No Docker, no database
servers — SQLite and embedded Qdrant only.

## Entry points

| Command | What it does |
|---|---|
| `python -m scriptengine.cli <command>` | Typer CLI — `crawl`, `prune`, `audit`, `index`, `classify`, `export`, `query`, `timeline`, `rosters`, `eval`, `canon-run`, `catalogue`, `script-path`, `verify`, `cite` |
| `python -m scriptengine.cli canon-run` | Measures the engine against `questions/` and writes a run folder under `reports/`. Refuses to start against a down or stale server; never exits non-zero on a bad score |
| `python -m scriptengine.api.main` | FastAPI service on `:8000`; `POST /context` is the endpoint that matters |
| `start_scriptengine.py` / `.bat` | Resolves the venv Python and launches the API without an activation step |
| `script_writer.ps1` | Interactive or headless tool that calls `/context` and writes `scripts output/current_request.json` |
| `npm start` (root) | Launches the optional Electron desktop shell |

## `scriptengine/` — module by module

| Module | Role |
|---|---|
| `config.py` | Process-wide `Settings` (pydantic-settings) — every value has a caller |
| `cli.py` | Typer command surface |
| `export.py` | Renders a series' SQLite graph to an Obsidian markdown vault (read-only) |
| `ingest/crawler.py` | MediaWiki API crawler — TLS impersonation, `allpages` enumeration, 50-page batching, retry/backoff |
| `ingest/wikitext.py` | Hand-written wikitext parser: templates, infoboxes, `[[links]]` → edges, `{{Ref}}` → citations, section trees, table flattening |
| `ingest/ontology.py` | Structural (not name-based) page-type discovery from infobox templates |
| `ingest/abilities.py` | Index-time extraction of abilities that exist only as prose, not as pages or headings |
| `ingest/canon.py` | Applies `non_canon_works` filtering (games, spin-offs) at index time |
| `ingest/classify.py` | Local-LLM semantic classification for cases structural rules can't settle (index-time only, cached) |
| `ingest/audit.py` | Extraction-quality auditing — catches a silently broken extractor |
| `ingest/documents.py` | `WikiPage` document model |
| `stores/facts.py` | `FactStore` — one SQLite file per series: documents, sections, nodes, edges, facts, FTS5 (BM25) |
| `stores/vectors.py` | `VectorStore` — Qdrant in embedded/local mode, one directory per series |
| `stores/schema.sql` | SQLite schema |
| `index/build.py` | Orchestrates crawled pages into the stores (full rebuild, not incremental append) |
| `index/chunker.py` | Three-level section-driven chunking: document card / section / paragraph |
| `index/embedder.py` | Lazy-loaded `bge-large-en-v1.5` embedder + `bge-reranker-v2-m3` reranker, idle-unload, CPU fallback |
| `retrieve/hybrid.py` | Vector ∪ BM25 ∪ graph → RRF fusion (k=60) → cross-encoder rerank → parent-section expansion |
| `retrieve/narrative.py` | Chronological "beats" retrieval — walks chapter/episode/arc ordering |
| `retrieve/roster.py` | Enumeration retrieval: declared sets, category reads, membership validation against topic constraints |
| `retrieve/citations.py` | Turns sparse `{{Ref}}` citations into per-sentence `(Chapter N, Episode M)` locators |
| `retrieve/abilities.py` | Graph-driven backward walk (`user` edges) for "every ability of X" |
| `retrieve/annotate.py` | Back-annotates an already-written script against the index |
| `retrieve/router.py` | Picks `narrative` vs `roster` vs `qa` mode from the query shape |
| `retrieve/semantics.py` | Distinguishes what an entity *is* from what category it's filed under |
| `llm/client.py` | OpenAI-compatible HTTP client (Ollama / LM Studio / opencode) — index-time and eval only, never retrieval |
| `api/main.py` | FastAPI app, `:8000`, `POST /context` primary route |
| `api/context.py` | Assembles the token-budgeted context bundle — the actual product |
| `api/rules.py` | `VOICE_RULES` / `STYLE_RULES` / `ANNOTATION_RULES` — the script-writing contract shipped with every context bundle |
| `eval/` | Gold-question regression suite, catalogue generator, canon-recall scoring, script-tag verification |
| `eval/questions.py` | Loads and validates `questions/<series>.json`. Series are discovered from filenames, so no `.py` file names a series |
| `eval/canon_gold.py` | Scores the bank against the live server — recall and precision per set question, presence-in-bundle per fact question |
| `eval/diagnose_misses.py` | Buckets every missing canon item as retrieval gap / unlinked page / extraction gap / corpus gap / gold error |
| `eval/canon_report.py` | Renders `REPORT.md`: headline, the wrong-answers list, bucket shares, and a generated remediation section that names a real file path per bucket |
| `eval/canon_run.py` | Orchestrates a run into `reports/<run-id>/`. Owns the server up-check and the staleness guard |

## Data flow

```
MediaWiki API → ingest/crawler.py → series/<name>/wikitext/*.json
   → ingest/ontology.py + ingest/wikitext.py → index/build.py
   → facts.db (SQLite) + vectors/ (Qdrant)
   → retrieve/hybrid.py + narrative.py → api/main.py (:8000)
   → external writer (AI assistant, or the legacy ComfyUI node)
```

Full rationale for each of these choices lives in `ARCHITECTURE.md`.

## `ui/`

Electron shell + React 18/MUI (Create React App). `ui/electron/main.js` and
`preload.js` bridge to the FastAPI backend and spawn CLI subprocesses.
`ui/src/pages/DashboardPage.js` and `IngestionPage.js` are the two views.

## `legacy/`

The retired first-generation pipeline: crawler, four iterations of a
spaCy/NER-based graph builder (`step2_build_graph.py` and `_v2`/`_v3`/`_v6`),
an HTML cleaner, and Neo4j-based retrieval. Deliberately retained — not
imported anywhere — until Phase 5 of the roadmap proves the replacement at
parity. See `legacy/README.md` for the file-by-file reasoning.

## `tests/`

23 `test_*.py` files mirroring the `scriptengine/` module layout (abilities,
canon, chronology, chunker, citations, classify, context, export, ontology,
retrieve, roster, router, semantics, stores, vectors, wikitext, and more).
Run with `python -m pytest tests/ -q`.

## `docs/`

| File | Covers |
|---|---|
| `ARCHITECTURE.md` | Design rationale — why the pipeline is shaped this way |
| `STRUCTURE.md` | This file — the directory/module inventory |
| `ROADMAP.md` | Where the project is headed |
| `CHANGELOG.md` | Dated log of changes, updated per work session |
| `ADDING_A_SERIES.md` | How to onboard a new wiki, including the citation grammar |
| `API.md` | `/context` and `/abilities` reference |
| `CATALOGUE.md` | Generated — current per-series stats, do not hand-edit |
| `CORPUS_REPORT.md` | Crawl throughput and corpus size notes |
| `EXTRACTION_AUDIT.md` | Extraction-quality audit findings |
| `RAG_DESIGN_REVIEW.md` | The 28-point review behind roster validation |
| `RETRIEVAL_SCENARIOS.md` | Scored scenarios and adversarial probes |
| `SCRIPT_STYLE.md` | The house script-writing style spec |
| `TRIAGE.md` | Corpus/ontology triage notes |
| `ANTI_AI_SCRIPTING.md` | Anti-AI-writing rules distilled into `VOICE_RULES` |

## Other top-level docs

- `README.md` — pitch, install, CLI walkthrough, live catalogue, roadmap table
- `CLAUDE.md` — agent working agreements (read first by an AI working in this repo)
- `STARTME.md` — session entry point for the direct script-writing workflow (distinct from dev/architecture docs)

## Series data (`series/<name>/`)

Each series is fully self-contained and gitignored: `raw/`, `wikitext/*.json`,
`facts.db` (SQLite), `vectors/` (Qdrant), `manifest.json`,
`overrides.yaml` (per-wiki quirks only — never Python), `audit/`. Delete the
folder and the series is gone; copy it and the series moves. Nothing is
shared between series but the code.
