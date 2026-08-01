# ScriptEngine

A universal knowledge engine over Fandom wikis. Point it at a wiki, and it
serves ordered, cited, structured knowledge over HTTP to whatever writes your
scripts.

ScriptEngine does **not** write scripts. It feeds the model that does — a local
Qwen or Gemma running in ComfyUI — with the one thing a script writer actually
needs and a plain RAG cannot give it: events in the right order, with the right
participants, traceable to a source.

**Status:** Phase 0 of 6 complete (rename and restructure). Ingestion is being
rebuilt. See [Roadmap](#roadmap).

---

## The idea

Most wiki RAG pipelines throw away the thing that makes a wiki valuable. They
render the page to prose, chunk the prose, embed the chunks, and then try to
recover entities and relationships from that prose with NER and regex — usually
with a hand-written table of character names per series.

That work is unnecessary. **A Fandom wiki already publishes its own structure**,
and the MediaWiki API hands it over directly:

| What you want | Where it already exists |
|---|---|
| The page's type | The infobox template it transcludes. JJK defines 20: `Character`, `Battle`, `Episode`, `Technique`, `Story Arcs`, `Location`, … |
| Its attributes | Wikitext infobox parameters, literally `\|age = 18` |
| Its relationships | Wikilinks, already resolved to canonical pages: `\|affiliation = [[Kyoto Metropolitan Curse Technical College\|Kyoto Jujutsu High]]` |
| Its structure | `prop=sections` — the real heading tree, with levels |
| Its labels | `prop=categories` — `Characters`, `Jujutsu_Sorcerers`, `Students` |
| Its sources | `{{Ref\|vol=5\|page=26}}` — citations as structured parameters |

So the entity taxonomy is **discovered per-wiki** rather than written per-series.
That is the whole design, and it is why the same pipeline handles Jujutsu Kaisen,
Chainsaw Man, and Marvel without a line of series-specific Python.

---

## Requirements

- **Python 3.12**
- **Node 18+** (only for the optional desktop UI)
- **An OpenAI-compatible LLM endpoint** — Ollama or LM Studio. Optional; used for
  summarisation and eval scoring, not for retrieval.
- A GPU is optional. Embedding and reranking fall back to CPU.

**No Docker. No database servers.** The graph, the facts, and the BM25 index all
live in one SQLite file per series; vectors live in Qdrant's embedded local mode.
There is nothing to start before you can work.

---

## Install

```powershell
# Python environment
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv python install 3.12
uv venv --python 3.12
.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt

# Desktop UI (optional)
npm install
cd ui; npm install; cd ..
```

---

## Use

```powershell
# 1. Crawl a wiki. Types are discovered; nothing is configured per series.
python -m scriptengine.cli crawl --series jjk --start-url https://jujutsu-kaisen.fandom.com/wiki/Jujutsu_Kaisen_Wiki

# 2. Check what the extractor actually understood before trusting it
python -m scriptengine.cli audit --series jjk

# 3. Build the fact store, the graph, and the indexes
python -m scriptengine.cli index --series jjk

# 4. Ask it something
python -m scriptengine.cli query --series jjk "How did the Shibuya Incident unfold?"

# 5. Serve it to ComfyUI
python -m scriptengine.api.main
```

Adding a second series is the same commands with a different `--series` and
`--start-url`. See [docs/ADDING_A_SERIES.md](docs/ADDING_A_SERIES.md).

### Feeding ComfyUI

The script-writing model calls `POST /context`, which returns a token-budgeted
bundle: passages **in narrative order**, the structured facts behind them, and a
citation for each claim, so the finished script can be traced back to the wiki.
Full reference in [docs/API.md](docs/API.md).

---

## Layout

```
scriptengine/
  config.py       settings; every value here has a caller
  ingest/         crawler, wikitext parser, ontology discovery
  stores/         SQLite facts + graph + FTS5, Qdrant vectors
  index/          section-driven chunking, embedding
  retrieve/       hybrid search, narrative ordering, reranking
  llm/            OpenAI-compatible client (Ollama / LM Studio)
  api/            FastAPI service on :8000
  eval/           gold question set and scoring harness
series/           one self-contained folder per series (gitignored)
legacy/           the previous pipeline, kept until Phase 5 proves the new one
ui/               Electron + React desktop shell
docs/             architecture, adding a series, API, audits
```

Each series is fully self-contained: delete the folder and the series is gone,
copy it and the series moves. Nothing is shared but the code.

---

## Roadmap

| Phase | Work | Status |
|---|---|---|
| 0 | Rename, restructure, drop Docker, retire the dead stack | **done** |
| 1 | Wikitext-first ingestion: ontology discovery, infobox and wikilink extraction | **done** |
| 2 | SQLite fact/graph/FTS5 store, Qdrant local vectors, section-driven chunking | **done** |
| 3 | Hybrid retrieval, narrative ordering, gold eval set | **done** |
| 4 | FastAPI service, Electron UI wired to it | **done** |
| 5 | Fresh crawl, extraction audit, iterate until coverage plateaus | in progress |
| 6 | Prove universality on Chainsaw Man and Marvel with no new code | |

### Where it stands on the Jujutsu Kaisen wiki

984 pages indexed out of 1,179 articles (the rest are galleries and maintenance
pages, skipped deliberately).

| | |
|---|---|
| Pages typed | 96.5% — into 19 types discovered from the wiki |
| Sections per page | 7.67 |
| Facts per page | 9.82 |
| Wikilink edges resolved | 95.1% of 34,431 |
| Citations captured | 8,539 |
| Chunks / vectors | 9,978 / 6,294 |
| Retrieval eval | 21/21 |

For comparison, the previous pipeline extracted **zero** facts and collapsed
every page into a single unnamed section.

The eval covers fact lookup, aliases, lexical and semantic search, multi-hop
questions and narrative ordering. It is a regression suite, not a scoreboard:
its value is that a change to chunking, fusion or reranking now moves a number
you can argue about. Run it with `python -m scriptengine.cli eval --series jjk`.

### What changed from the previous version

The earlier pipeline crawled and cleaned successfully — 850 pages of the JJK wiki
— but nothing downstream ever ran, and parts of it could not. Rebuilt because:

- **Section detection never fired.** It matched a bare `appearance`; the corpus
  emitted `## Appearance`. Every document collapsed into a single section, so the
  chunk hierarchy, the parent pointers, and the section metadata were all inert.
- **Citations were never stripped.** The regex removed `[1]`, but the cleaner had
  already expanded citations to full text — 40 to 130 per page — straight into
  the embeddings and the BM25 index.
- **Four graph builders**, ~3,700 lines, rebuilt entities from prose with spaCy
  and per-series alias tables. The wikitext already contained the answer.
- **The generation step could not import its own retriever**, and referenced an
  undefined constant.
- **The graph query used `[r*1..$depth]`**, which Neo4j rejects.
- **`config.py` described infrastructure nothing used** — Postgres, Redis,
  Elasticsearch — while each stage hardcoded its own conflicting values.
- **The UI called a FastAPI server that did not exist.**

The good parts were kept: the MediaWiki API crawler with its concurrency and
retry handling, the hybrid retrieval architecture, and the model choices. The old
code is in `legacy/` until Phase 5 confirms the replacement.
