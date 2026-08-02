# ScriptEngine

A universal knowledge engine over Fandom wikis. It ingests a wiki, derives that
wiki's own entity taxonomy from the wiki itself, and serves ordered, cited,
structured context over HTTP to whatever writes the video scripts — an AI
assistant driving `POST /context` directly, or the legacy ComfyUI node.

**ScriptEngine does not write scripts.** It feeds the model that does, and it
serves the writing rules (`scriptengine/api/rules.py`) alongside the research so
the contract travels with the context.

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
python -m scriptengine.cli export --series jjk        # Obsidian vault in series/jjk/obsidian/
python -m scriptengine.cli eval   --series jjk        # regression suite
python -m scriptengine.cli script-path "Title" --create   # where a script goes
python -m scriptengine.cli verify "<script>" --series jjk # check its tags
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
- **Scripts must not sound AI-written.** `docs/ANTI_AI_SCRIPTING.md` distills
  Wikipedia:Signs of AI writing for spoken narration. Its rules live in
  `scriptengine/api/rules.py` (`VOICE_RULES`) and are appended to every context
  bundle; when reviewing or generating script output, apply the audit at the
  bottom of that doc.
- **Every line of a script must be traceable to a chapter.** The `sourced:`
  header on each beat is computed in `scriptengine/retrieve/citations.py` by
  reading each `{{Ref}}` as covering the sentences before it and resolving the
  chapter to its episode through the graph. Numbers are looked up, never
  inferred: a chapter the anime never adapted gets no episode. `cli audit`
  reports the coverage and fails when citations stop reaching the prose.
- **Run `eval` after touching chunking, fusion, retrieval or the parser.** It is
  a regression suite, not a scoreboard. If a gold question is wrong, fix the
  question and record why in `gold_jjk.json` — do not tune the retriever to make
  one ambiguous prompt go green.
- **Run `audit` before `index`.** A broken extractor is silent; that is the
  failure mode the audit exists to catch. On a new wiki, read `cited directly`
  and `sentences w/ chapter` first: they are how you find out that this wiki
  cites in a shape nothing here reads yet.
- **Never guess what a citation parameter means.** One-Punch Man's `cep` appears
  twice on the whole wiki and is deliberately left unmapped. A guessed mapping
  puts a number nobody verified into a finished script, which is worse than an
  untagged line.
- **Verify a finished script's tags** with `cli verify` before calling it done.
  It reads the raw crawl rather than the index.
- **Comments explain why, not what.** Where a line exists because of a specific
  bug, the comment says which bug. Keep that.
- **Do not add a dependency without a caller.** The previous `config.py`
  declared Postgres, Redis and Elasticsearch that nothing imported.

## Layout

```
scriptengine/
  config.py       settings; every value has a caller
  ingest/         crawler, wikitext parser, ontology discovery, audit
  stores/         SQLite facts+graph+FTS5+categories, Qdrant local vectors
  index/          section-driven chunking, embedding, build
  retrieve/       hybrid (relevance), narrative (chronological) and roster
                  (enumeration) retrieval, plus citations (chapter/episode)
  api/            FastAPI on :8000 — /context is the endpoint that matters,
                  rules.py is the script-writing contract it serves
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

Six wikis indexed, 8,113 pages: Jujutsu Kaisen, Bleach, Hunterpedia,
One-Punch Man, Berserk, Chainsaw Man. All six type above 90%; five of the six
source a third to a half of their prose to a chapter. Eval 24/24 on `jjk`.

Adding the five needed no series-specific Python. What each one *did* need was a
description of how it writes a citation, because no two of these wikis agree —
Chainsaw Man is positional, One-Punch Man numbers a webcomic and a manga apart,
and Bleach, Hunterpedia and Berserk put the locator in prose inside an HTML
`<ref>`. That vocabulary lives in `series/<name>/overrides.yaml`; the mechanism
is `wikitext.CitationGrammar`.

Berserk sources 0% and that is the wiki, not the pipeline: it cites cover art
and interviews rather than instalments, so a Berserk script cannot carry
chapter tags. `audit` says which of the two it is.

Open: Marvel is a legacy wiki using Lua modules and `Marvel Database:Character
Template`; structural discovery should reach it but has not been re-tested since
that landed.
