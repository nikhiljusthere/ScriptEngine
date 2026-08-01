# ScriptEngine

A universal knowledge engine over Fandom wikis. It ingests a wiki, derives that
wiki's own entity taxonomy from the wiki itself, and serves ordered, cited,
structured context over HTTP to a local Qwen/Gemma running in ComfyUI, which is
what actually writes the video scripts.

**ScriptEngine does not write scripts.** It feeds the model that does.

## Start here

1. Read `docs/ARCHITECTURE.md` — the design and why it is this way.
2. Read `graphify-out/GRAPH_REPORT.md` — the knowledge graph of this codebase:
   god nodes, communities, and the legacy→current supersession map.
3. `python -m scriptengine.cli list` — what series exist on disk.

## The one idea everything follows from

A Fandom wiki already publishes its own structure through the MediaWiki API.
Infobox templates name the page types, categories label the pages, wikilinks are
pre-resolved edges with canonical targets, and the section tree arrives with
explicit levels. So **nothing about a series is hardcoded** — which is why the
same pipeline handles Jujutsu Kaisen, Chainsaw Man and Marvel.

Type discovery is *structural*, not name-based: an infobox is the template
transcluded before the first heading, with the most named parameters, appearing
once per page. Searching template names for the word "infobox" finds JJK's
twenty types and nothing on Chainsaw Man, whose infobox is called `Character`.

**The rule: if a fix mentions a series name and lives in a `.py` file, it is in
the wrong place.** Per-wiki handling goes in `series/<name>/overrides.yaml`.

## Commands

```powershell
.\scriptengine\.venv\Scripts\Activate.ps1

python -m scriptengine.cli crawl  --series jjk --start-url <any wiki page>
python -m scriptengine.cli audit  --series jjk        # ALWAYS before indexing
python -m scriptengine.cli index  --series jjk        # add --no-embed to skip the GPU
python -m scriptengine.cli query  --series jjk "question"
python -m scriptengine.cli timeline --series jjk "Shibuya Incident"
python -m scriptengine.cli eval   --series jjk        # regression suite
python -m scriptengine.api.main                       # serve on :8000

python -m pytest tests/ -q
```

`crawl` resumes by default — pages already on disk are skipped. `index` re-parses
from stored wikitext, so a parser fix reaches the whole corpus in seconds without
re-crawling.

## Working agreements

- **Verify against the live wiki, not just the tests.** Nearly every real defect
  in this project was found by running the pipeline against Fandom and reading
  the output, not by reading code. Tables being silently deleted, `{{Ruby}}`
  returning furigana, stale Qdrant vectors resolving to unrelated text — all
  found by looking at results.
- **Run `eval` after touching chunking, fusion, retrieval or the parser.** It is
  a regression suite, not a scoreboard. If a gold question is wrong, fix the
  question and record why in `gold_jjk.json` — do not tune the retriever to make
  one ambiguous prompt go green.
- **Run `audit` before `index`.** A broken extractor is silent; that is the
  failure mode the audit exists to catch.
- **Comments explain why, not what.** Where a line exists because of a specific
  bug, the comment says which bug. Keep that.
- **Do not add a dependency without a caller.** The previous `config.py`
  declared Postgres, Redis and Elasticsearch that nothing imported.

## Layout

```
scriptengine/
  config.py       settings; every value has a caller
  ingest/         crawler, wikitext parser, ontology discovery, audit
  stores/         SQLite facts+graph+FTS5, Qdrant local vectors
  index/          section-driven chunking, embedding, build
  retrieve/       hybrid (relevance) and narrative (chronological) retrieval
  api/            FastAPI on :8000 — /context is the endpoint that matters
  eval/           gold question set and scoring harness
series/<name>/    self-contained corpus + stores (gitignored)
legacy/           the retired pipeline, kept for reference
graphify-out/     knowledge graph of this repo
```

## Infrastructure

**No Docker. No database servers.** SQLite holds the facts, graph and BM25
index; Qdrant runs embedded. Nothing to start before working.

GPU: torch must be a CUDA build (`--index-url https://download.pytorch.org/whl/cu130`
for the RTX 5090). Everything works on CPU, slowly. The embedder and reranker
load on first use and unload when idle, because ComfyUI and a resident model
cannot share VRAM.

## Status

Phases 0–6 complete. On the Jujutsu Kaisen wiki: 984 pages, 98.9% typed,
9,804 facts, 34,417 edges at 95.4% resolved, eval 21/21. Chainsaw Man reaches
90.9% typed with no CSM-specific code.

Open: Marvel is a legacy wiki using Lua modules and `Marvel Database:Character
Template`; structural discovery should reach it but has not been re-tested since
that landed.
