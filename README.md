# ScriptEngine

A universal knowledge engine over Fandom wikis. Point it at a wiki, and it
serves ordered, cited, structured knowledge over HTTP to whatever writes your
scripts.

ScriptEngine does **not** write scripts. It feeds the writer that does — the AI
assistant, hooked in directly through `STARTME.md` and `script_writer.ps1` —
with the one thing a script writer actually needs and a plain RAG cannot give
it: events in the right order, with the right participants, traceable to a
source.

**Status:** Six wikis indexed, 8,113 pages. See [Roadmap](#roadmap).

| series | wiki | pages | typed | prose sourced to a chapter |
|---|---|---|---|---|
| `jjk` | Jujutsu Kaisen | 987 | 98.9% | 55% |
| `bleach` | Bleach | 2,248 | 95.4% | 34% |
| `hxh` | Hunterpedia | 2,014 | 96.0% | 50% |
| `opm` | One-Punch Man | 1,565 | 98.0% | 31% |
| `berserk` | Berserk | 762 | 90.4% | 0% |
| `csm` | Chainsaw Man | 537 | 97.4% | 42% |

Five of the six were added without a line of series-specific Python. What each
one *did* need was a description of how it writes a citation, because no two of
these wikis agree — see [the citation grammar](docs/ADDING_A_SERIES.md#the-citation-grammar).

Berserk's 0% is the wiki, not the pipeline: it cites cover art and interviews
rather than instalments, so its prose carries no chapter numbers and a Berserk
script cannot be tagged. `audit` says so explicitly rather than reporting a
number that looks like a bug.

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
| Its sources | `{{Ref\|vol=5\|page=26}}` — citations as structured parameters, and inlined into prose as short locators (`(Chapter 143, Episode 30)`) so the script writer can cite every line |

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

# 4. Export the graph to an Obsidian vault and explore it in graph view
python -m scriptengine.cli export --series jjk

# 5. Ask it something
python -m scriptengine.cli query --series jjk "How did the Shibuya Incident unfold?"

# 6. Serve it to ComfyUI
python -m scriptengine.api.main
```

Or start the API by double-clicking `start_scriptengine.bat` (or
`python start_scriptengine.py`) — both resolve the `.venv` interpreter
themselves, so no activation step is needed.

Adding a second series is the same commands with a different `--series` and
`--start-url`. See [docs/ADDING_A_SERIES.md](docs/ADDING_A_SERIES.md).

### Writing scripts — the direct path

The AI assistant writes the scripts, not ComfyUI. The whole loop lives in the
repo:

| File | What it is |
|---|---|
| `STARTME.md` | Session entry point — read this first. The workflow, the questions to ask (topic, series, intro, length), and how to fetch context. |
| `docs/SCRIPT_STYLE.md` | The house style spec: format, intro toggle, voice + annotation rules, with the samples as reference. |
| `scriptengine/api/rules.py` | The rule blocks themselves, appended to every rendered prompt so the writer gets them with the research. |
| `script_writer.ps1` | Interactive menu (and headless mode) that builds a request and fetches the research context from `/context`. |
| `scripts output/` | Finished scripts (`<Title>.md`) and `current_request.json` (the fetched context a script is written from). |
| `sample scripts/` | The published reference scripts that define the style. |

One run:

```powershell
# interactive: press numbers to set topic / series / question / words / intro / budget / mode
powershell -ExecutionPolicy Bypass -File script_writer.ps1

# headless (the assistant drives this)
powershell -ExecutionPolicy Bypass -File script_writer.ps1 -Headless `
  -Topic "Shibuya Incident" -Series jjk -Words 3000 -Intro true
```

The fetch hits the same `POST /context` endpoint described below and writes the
rendered, token-budgeted research context to `scripts output/current_request.json`
(the previous one is kept as `current_request.prev.json`). The script is then
written from that context per `docs/SCRIPT_STYLE.md`. Because the writer is a
full-context AI rather than the node's ~2k-token generation window, scripts run
to 18,000+ characters (~3,000 words).

Finished scripts are filed into the production tree rather than the repo, one
numbered folder per video, beside that video's audio, images and storyboard:

```powershell
python -m scriptengine.cli script-path "Every Fight Mahoraga Has Ever Been In" --create
# <SCRIPTENGINE_SCRIPTS_ROOT>\Video 1 - Every Fight Mahoraga Has Ever Been In\Script\...
```

An existing folder with the same title is reused, so a rewrite lands back where
it started; a new title takes the next free number. Set the root with
`SCRIPTENGINE_SCRIPTS_ROOT` in `.env`, which is gitignored because the path is
personal to the machine.

Then check the script before calling it done:

```powershell
python -m scriptengine.cli verify "<path to the script>" --series jjk
```

`verify` reads every `(Chapter N, Episode M)` in the finished script and checks
it against the raw crawl: the instalment page exists, some reference actually
cites it, and the chapter/episode pairing matches the wiki's own adaptation
data. It reads `series/<name>/wikitext/`, not the index, so a bug in indexing
cannot make a bad tag look fine. The engine offers locators; the writer chooses
which to put on a line, and this is what catches the confident wrong number.

### The shape of a topic decides the mode

Four of the five published samples are enumerations — "Every Apostle in
Berserk", "Every Rank of Curse", "Every Level of the Abyss" — and one is an
account. Relevance ranking answers neither: it returns the eight passages
nearest the query, which is a sample of a set and not the set.

| Mode | Topic | What comes back |
|---|---|---|
| `narrative` | "Shibuya Incident" | beats in story order, across the event's page and the battle pages it links |
| `roster` | "Every Rank of Curse" | every member of the set the wiki declares, grouped by the wiki's own tier field |
| `qa` | a question | passages nearest the query |

`mode="auto"` reads the topic and picks. The set behind a roster is the wiki's
own: a curated category, a discovered page type, or the distinct values of one
infobox field — whichever answers the topic best. Grouping is found through the
wiki's label for a field, so "Every Rank of Curse" reaches the parameter Jujutsu
Kaisen keys as `class` and labels "Grade" without a line of series-specific code.

### Every line can be sourced

A script tags each block with the chapter and episode it came from. The wiki
supplies that, but not in the shape a script needs, and two gaps sat in between:

- **References are sparse in prose.** MediaWiki puts one `{{Ref}}` at the end of
  the passage it supports. In a fetched Shibuya Incident bundle that was 12.8%
  of sentences and 68 of 128 beats. Reading each reference as covering the
  sentences before it — which is what placing it there means — takes that page
  to 99.6%, and the span goes on the beat's `sourced:` header.
- **Half the references name a chapter and no episode.** 7,548 carry `chap`,
  3,815 carry `ep`. The rest resolve through the graph's own adaptation edges
  (`Chapter N -anime episode-> Episode M`), and a chapter the anime never
  adapted stays `(Chapter N)` rather than acquiring an invented one.

`python -m scriptengine.cli audit` reports both numbers, so a regression that
drops citations from the prose fails a check instead of quietly producing
untaggable scripts.

The ComfyUI workflow still exists for the audio/TTS side of the pipeline and is
documented below.

### The legacy ComfyUI path

The ComfyUI model calls `POST /context`, which returns a token-budgeted
bundle: passages **in narrative order**, the structured facts behind them, and a
citation for each claim, so the finished script can be traced back to the wiki.
Full reference in [docs/API.md](docs/API.md).

Two things make the ComfyUI integration work:

- **`top_k` on `/context`** — the endpoint now accepts an optional `top_k`
  (default: the engine's tuned 8). Raise it for questions that need recall
  over precision; the token budget still caps what the model receives.
- **`GET /abilities/{series}/{entity}`** — graph-driven ability lookup. It
  walks the `user` edges *backwards* from a character to every ability page
  that lists them, then returns each ability with its debut chapter (`debut`
  edge), its `Usage / <character>` section, and the `{{Ref|chap=N}}`
  citations inside that section — the chapters where the character was
  **shown** using it, not just talked about.

The abilities endpoint exists because prose retrieval cannot answer "every
ability of X" reliably: a multi-entity question ranks battle pages above the
ability pages. The graph does not care — `Black Flash -user-> Yuji Itadori` is
an edge, so his kit is found even when the character page is outranked. (This
is also why a character whose main page is missing or unresolved — JJK's
"Yuji Itadori" main page was skipped by an over-broad crawl filter until
Phase 5 — still answers "what are their abilities" without any page.)

### The ComfyUI workflow

The workflow lives at `custom_nodes/ScriptEngineRAG/` in the ComfyUI install
(a copy of the workflow JSON sits at the repo root as
`ScriptEngine RAG Answer.json`):

```
[Load LLM (krea2 CLIPLoader — you pick the .safetensors)]
        │
        ▼
[ScriptEngine RAG Answer] ◄── [Question / Arc (text)]
        │                        series: jjk | db | csm  (dropdown)
        ▼
answer ──────────► [Preview: Answer]
context ─────────► [Preview: RAG Context]
prompt ───────────► [Preview: LLM Prompt]
```

Two nodes, both read-only HTTP against ScriptEngine:

| Node | What it does |
|---|---|
| `ScriptEngineContext` | Fetches the rendered `/context` bundle (`as_prompt=true`); returns context + raw beats + facts JSON for inspection. |
| `ScriptEngineAnswer` | Fetches `/context`, then runs it through the loaded CLIP (LLM) via `tokenize`/`generate`/`decode`. Returns `answer`, `context`, `prompt`. |

`ScriptEngineAnswer` behaviors:

- **Anime selector** — `series` is a dropdown over the series on disk
  (`jjk`, `db`, `csm`); anything can still be typed in.
- **Entity expansion** (qa mode, on by default) — every proper noun in the
  question is resolved through `/abilities`, and the structured ability
  blocks are merged **ahead of** the prose passages so they are never
  truncated away. "Yuji Itadori and Choso" therefore retrieves both complete
  kits, each with debut chapters and per-character usage chapters.
- **No `[n]` citation markers** — ScriptEngine's section order markers
  (`[1]`, `[12]`) are stripped from the context before the LLM sees it
  (real citations like `(Chapter 101, Episode 37)` are kept, since that is
  content), and the prompt forbids bare retriever markers in the answer.
- **Per-line chapter/episode annotations (hardcoded format)** — every script
  line must end with its source, e.g. `(Chapter 101, Episode 37)`. Consecutive
  lines in the same episode/chapter share one tag at the end of the block
  ("if 3 lines are in the same episode, mention it once"). Numbers are never
  invented: citations are inlined into the retrieved prose itself
  (`(Chapter 143)` markers), so chapters/episodes stated in the context —
  plus debuts, usage chapters, anime debuts — are the only ones that may be
  used; unsourced facts get a plain line.
- **Anti-AI voice rules** — every generation gets a `VOICE_RULES` block
  (distilled from Wikipedia:Signs of AI writing, full learning in
  `docs/ANTI_AI_SCRIPTING.md`): no significance inflation, no "it's not X
  it's Y" reframes, no rule-of-three packing, no AI vocabulary, plain verbs,
  varied sentence length, no em dashes, no weasel wording.
- **House script format + intro toggle** — every narrative script ships in
  the sample-script format (`sample scripts/`): a bold title line, then
  `* **Heading**` sections with the narration as plain spoken paragraphs, and
  any closing recap never titled "Final Thoughts". `intro` (on by default) adds a fan-style hook paragraph
  between the title and the first section; off starts straight at the first
  heading. Enforced by a `STYLE_RULES` block in the prompt, injected the same
  way `VOICE_RULES` is.
- **ScriptEngine must be running** — the node fails with a readable message
  and the start command if the API is down, instead of feeding the LLM an
  empty context.

---

## Layout

```
scriptengine/
  config.py       settings; every value here has a caller
  ingest/         crawler, wikitext parser, ontology discovery
  stores/         SQLite facts + graph + FTS5 + categories, Qdrant vectors
  index/          section-driven chunking, embedding
  retrieve/       hybrid search, narrative ordering, reranking,
                  abilities (graph-driven character → ability lookup),
                  roster (enumeration), citations (chapter/episode locators)
  llm/            OpenAI-compatible client (Ollama / LM Studio)
  api/            FastAPI service on :8000, plus the script writing rules
  eval/           gold question set and scoring harness
series/           one self-contained folder per series (gitignored)
legacy/           the previous pipeline, kept until Phase 5 proves the new one
ui/               Electron + React desktop shell
docs/             architecture, adding a series, API, audits, script style
STARTME.md        session entry point for the direct script-writing path
script_writer.ps1 interactive request builder + context fetcher
scripts output/   finished scripts + current request context
sample scripts/   the published scripts that define the house style
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
| 7 | Graph-driven abilities endpoint (`/abilities`), ComfyUI answer workflow | **done** |
| 8 | Direct AI script-writing path: `STARTME.md`, `script_writer.ps1`, house style guide (`docs/SCRIPT_STYLE.md`) | **done** |
| 9 | Subject resolution, roster mode, per-sentence sourcing, rules served with the context | **done** |
| 10 | Five more wikis, and the per-wiki citation grammar they each needed | **done** |

### Where it stands on the Jujutsu Kaisen wiki

987 pages indexed out of 1,089 articles (the rest are image galleries and
maintenance pages, skipped deliberately).

| | |
|---|---|
| Pages typed | 98.9% — into 22 types discovered from the wiki |
| Sections per page | 7.69 |
| Facts per page | 10.2 |
| Wikilink edges resolved | 96.4% of 34,112 |
| Citations captured | 8,830 — kept structured *and* inlined in prose |
| Chunks / vectors | 10,127 / 6,404 |
| Retrieval eval | 21/21 |

Phase 5 has already fixed three data-integrity bugs found by auditing that
crawl:

- **Citations were captured but never rendered.** `{{Ref|chap=143}}` became a
  `Citation` object and then vanished from every downstream text — the vault,
  the fact store, and the LLM context. Prose now carries a compact
  `(Chapter 143, Episode 30)` locator (infobox fact values stay clean).
- **The three main character pages were skipped.** Yuji Itadori, Satoru Gojo
  and Sukuna carry "Articles needing cleanup", which an over-broad skip
  pattern treated as junk — so "the origin of Yuji" resolved to a battle page
  instead of the character. Maintenance banners no longer skip pages.
- **845 junk `:Category:` edges.** `[[:Category:X]]` links render as text on
  the page, but they still point at Category pages; a leading colon defeated
  the namespace check and created stub nodes for every one of them.

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
