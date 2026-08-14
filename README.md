# ScriptEngine

A universal knowledge engine over Fandom wikis. Point it at a wiki, and it
serves ordered, cited, structured knowledge over HTTP to whatever writes your
scripts.

ScriptEngine does **not** write scripts. It feeds the writer that does — the AI
assistant, hooked in directly through `STARTME.md` and `script_writer.ps1` —
with the one thing a script writer actually needs and a plain RAG cannot give
it: events in the right order, with the right participants, traceable to a
source.

**Status:** Eight wikis. See [docs/CATALOGUE.md](docs/CATALOGUE.md) for the
current numbers, which are generated from the stores rather than typed here:

```powershell
python -m scriptengine.cli catalogue
```

**8 series, 23,656 pages, 119 declared enumeration sets.**

| series | wiki | pages | typed | inline refs | instalment pages |
|---|---|---:|---:|---:|---:|
| `db` | Dragon Ball | 8,052 | 100% | 4% | 0 |
| `onepiece` | One Piece | 7,613 | 94% | 0% | 2,603 |
| `bleach` | Bleach | 2,126 | 95% | 34% | 0 |
| `hxh` | Hunterpedia | 2,014 | 96% | 50% | 455 |
| `opm` | One-Punch Man | 1,565 | 98% | 30% | 263 |
| `jjk` | Jujutsu Kaisen | 987 | 99% | 55% | 393 |
| `berserk` | Berserk | 762 | 90% | 0% | 451 |
| `csm` | Chainsaw Man | 537 | 97% | 42% | 268 |

A script line gets its chapter one of two ways, and a series needs only one of
them. **Inline refs** is the share of sentences the wiki footnotes itself.
**Instalment pages** is the other route: One Piece footnotes almost nothing but
writes 1,191 chapter pages and 1,172 episode pages, each with a full summary, so
a claim retrieved from the page titled "Chapter 1015" is sourced to Chapter 1015.

Berserk is the one to be careful with — it scores low on both, because its wiki
cites cover art and interviews and titles nothing by number.

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

# 2. Drop what no script will cite — video games, soundtracks, dub credits.
#    Driven by `prune_types` in the series' overrides; --dry-run lists first.
python -m scriptengine.cli prune --series jjk --dry-run

# 3. Check what the extractor actually understood before trusting it
python -m scriptengine.cli audit --series jjk

# 4. Build the fact store, the graph, and the indexes
python -m scriptengine.cli index --series jjk

# 5. Export the graph to an Obsidian vault and explore it in graph view
python -m scriptengine.cli export --series jjk

# 6. Ask it something
python -m scriptengine.cli query --series jjk "How did the Shibuya Incident unfold?"

# 7. Classify the ability pages the wiki's own fields cannot settle.
#    A local model, once, at index time — retrieval only ever reads the result.
python -m scriptengine.cli classify --series jjk --dry-run

# 8. Check the sets it can enumerate, and score them against the wiki
python -m scriptengine.cli rosters --series jjk
python -m scriptengine.cli eval --series jjk

# 9. Serve it to ComfyUI
python -m scriptengine.api.main

# 10. Measure it against the researched question bank and read the report.
#     Needs the server from step 9 already running.
python -m scriptengine.cli canon-run --dry-run     # validates the bank only
python -m scriptengine.cli canon-run --skip-eval   # writes reports/<run-id>/REPORT.md
```

`eval` and `canon-run` answer different questions. `eval` asks "did a change
break what worked" against the crawl as it exists on disk, and gates the build.
`canon-run` asks "is the engine right about the series" against answers
researched online, and is allowed to say no for a long time — it never exits
non-zero on a bad score.

The crawler asks for **50 pages per request** — MediaWiki's cap for anonymous
callers — which is the difference between 112 and ~2,500 pages a minute. One
Piece's 7,937 pages take three minutes. Concurrency is not the lever and raising
it does not help: Fandom limits per request, so more workers are served more
slowly. See [docs/CORPUS_REPORT.md](docs/CORPUS_REPORT.md).

Pruning changes the stored wikitext, so `audit` and `index` have to follow it;
until they do, the store still answers with the pages that were removed. Be
careful pruning the `unknown` type — it is everything no infobox could classify,
not a known category of junk, and on Dragon Ball it deleted the wiki's own
`Dragon Ball` article.

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

### Sourcing a script that already exists

The writing path gets its locators for free, because the research context
arrives with them. A script written before this existed, or written somewhere
else, needed sourcing by hand. `cite` runs the pipeline backwards:

```powershell
python -m scriptengine.cli cite "<path to the script>" --series jjk
# 96 blocks of prose, 74 tagged, 22 left alone
# All 39 distinct tags check out against the raw wiki pages.
```

Each block of prose becomes a query; the passages that come back carry the
wiki's own references, and the locators on those become the block's tag.

**It does not change a word.** `unannotate` reverses the operation, and `cite`
runs that check on every invocation before writing: if the cited text does not
reduce back to the input byte for byte, it refuses to write and says so. The
original is never opened for writing either — output goes to
`<name> (cited).md` beside it.

Two rules keep it honest rather than merely productive. A block is tagged only
when at least two retrieved passages name the same locator, so hits that
disagree leave the block alone. And a tag may not span more than eight chapters,
because reading references off a whole wiki section produces
`(Chapters 1-171, Episodes 1-58)`, which is true and useless.

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
own: a curated category, a union of several, the sections of a single page, a
discovered page type, or the distinct values of one infobox field — whichever
answers the topic best. Grouping is found through the wiki's label for a field,
so "Every Rank of Curse" reaches the parameter Jujutsu Kaisen keys as `class`
and labels "Grade" without a line of series-specific code.

The sections source exists because some sets are never a category: One Piece
gives no Marine rank its own article, so asking by category returns `Marine
Officers` — fourteen people rather than the twenty-two-rank ladder the wiki
writes as one page.

**A topic that named its series used to be answered by the series.** Both large
wikis name most of their categories after themselves, so "Every race in Dragon
Ball" handed two free words to `Dragon Ball Z episodes` and came back as 150
episode titles — while "Every race", the same question four words shorter,
returned `Races` correctly. The wiki's own name is now read from the manifest
host and removed from both sides of the comparison.

What survives that fix is a set that is wrong but not empty, so every roster now
reports **how well it matched**: `declared`, `exact`, `partial` or `weak`, with
the words the topic never asked for. "Every Straw Hat Pirate" still answers with
`Straw Hat Pirates' Creations` — the crew's weapons — but it comes back
`partial`, naming *creations* as the reason, and the bundle carries a `warning`
a caller can act on.

What that cannot catch is a set whose name matches perfectly and whose category
the wiki barely fills: `Grand Line Islands` has four members and reports
`exact`. `docs/RETRIEVAL_SCENARIOS.md` records ten scored scenarios, twenty-one
adversarial probes, and what is still known to fail.

### A category is not an answer

"Every Saiyan transformation" returned Black Frieza, because the Dragon Ball
wiki files it under `Transformations` — correctly, it is one — and nothing
downstream ever asked the second half of the question. No embedding was
involved: a roster is a category read, not a search.

So candidates are now **validated against the topic** before they are returned.
Ownership and race come from fields the extractor already stored (`Users`,
`Inventor`, and one graph hop to the owner's own `Race`), medium from the
`Debut` field that already names it. Each rejection is reported with its reason:

```
Every Saiyan transformation   160 candidates → 75 kept
  - Black Frieza   not saiyan
  - Class-up       outside the story (Game: Dragon Ball Heroes)
  - Android 1617   outside the story (Dragon Ball Fusions)
```

Scope is **canon by default** — manga, anime, film — and game and spin-off
material is never deleted, only held back until a topic asks for it ("every
transformation ever"). A qualifier only constrains when the wiki has an article
about it, which is what stops "Every Cursed Technique of Sukuna" from filtering
on *cursed*, a word every technique on that wiki would fail. And if validation
would empty a set, it is skipped: a visibly broad list beats a blank one.

Full account, including the 28-point review that prompted it:
[docs/RAG_DESIGN_REVIEW.md](docs/RAG_DESIGN_REVIEW.md).

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
  eval/           gold question sets (jjk, db, onepiece), scoring, catalogue,
                  the questions/ loader, canon scoring, diagnosis and the
                  report renderer behind `canon-run`
questions/        the online-canon question bank, one JSON per series (tracked)
reports/          one folder per measurement run + index.md (tracked)
series/           one self-contained folder per series (gitignored)
legacy/           the previous pipeline, kept until Phase 5 proves the new one
ui/               Electron + React desktop shell
docs/             architecture, adding a series, API, audits, script style,
                  CATALOGUE (generated), CORPUS_REPORT, RETRIEVAL_SCENARIOS
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
| 11 | Dragon Ball and One Piece, cite mode, generated catalogue | **done** |
| 12 | Batched crawling (50 pages/request), type-level pruning | **done** |
| 13 | Enumeration scored against the wikis: series-name defect fixed, `sections_of:` and `categories:` sources, eval sets for both large wikis | **done** |
| 14 | A roster reports how well it matched, so a wrong set says so instead of looking certain | **done** |
| 15 | Membership validation: candidates checked against the topic's own constraints, canon by default, rejections reported | **done** |
| 16 | Ability ontology: race-exclusive vs teachable vs character-specific, derived from users and inventors so it self-corrects | **done** |
| 17 | Semantic types: a set admits only what it is made of, so an army stops containing planets | **done** |
| 18 | Index-time semantic classification for what structure cannot settle — properties, cached, never in the query path | **done** |
| 19 | Audited against canon sources: subpage folding, per-series canon media, declared members for sets no wiki files | **done** |
| 20 | Tell a current member from a former one — the Espada holds 18 pages for ten seats | |
| 21 | Detect an *incomplete* set — one whose name matches exactly but whose category the wiki barely fills | |

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
