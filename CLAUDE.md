# ScriptEngine

A universal knowledge engine over Fandom wikis. It ingests a wiki, derives that
wiki's own entity taxonomy from the wiki itself, and serves ordered, cited,
structured context over HTTP to whatever writes the video scripts: an AI
assistant driving `POST /context` directly, or the legacy ComfyUI node.

**ScriptEngine does not write scripts.** It feeds the model that does, and it
serves the writing rules (`scriptengine/api/rules.py`) alongside the research so
the contract travels with the context.

## Start here

1. **Active work: completing JJK D6 comprehension** (JJK only; this run stops
   before P6). "JJK 100%" here means full D6 comprehension — the corpus
   *understands* everything about a character (what each line/fact/prose/event
   means, whether it is an event, where it sits on the timeline, all
   structured dimensions), not just line retrieval (D5 is the separate
   reachability layer; `docs/ROADMAP.md` "current goal" states the exit
   condition). Live checkpoint: `plan/drift_log.md` §4 (current position) +
   `reports/comprehension/GATE.md` (gate state) + `reports/comprehension/
   COMPREHENSION_REMAINDER.md` (the remainder plan + the two-100%s + the
   checkable definition of 100% comprehension). The JJK prose pass is
   **complete** (100% on every in-scope narrative page type) — its single
   final record is `reports/page-campaign/PROSE_PASS_FINAL.md` (method, the
   crucial engine fixes, final state).
2. Read `docs/ARCHITECTURE.md`, the design and why it is this way.
3. Read `graphify-out/GRAPH_REPORT.md`, the knowledge graph of this codebase:
   god nodes, communities, and the legacy→current supersession map.
4. `python -m scriptengine.cli list`, what series exist on disk.

## The one idea everything follows from

A Fandom wiki already publishes its own structure through the MediaWiki API.
Infobox templates name the page types, categories label the pages, wikilinks are
pre-resolved edges with canonical targets, and the section tree arrives with
explicit levels. So **nothing about a series is hardcoded**, which is why the
same pipeline handles Jujutsu Kaisen, Chainsaw Man and Marvel.

Type discovery is *structural*, not name-based: an infobox is the template
transcluded before the first heading, with the most named parameters, appearing
once per page. Searching template names for the word "infobox" finds JJK's
twenty types and nothing on Chainsaw Man, whose infobox is called `Character`.

**The rule: if a fix mentions a series name and lives in a `.py` file, it is in
the wrong place.** Per-wiki handling goes in `series/<name>/overrides.yaml`.

## Commands

```bash
source scriptengine/.venv/bin/activate    # or call scriptengine/.venv/bin/python directly

python -m scriptengine.cli crawl  --series jjk --start-url <any wiki page>
python -m scriptengine.cli audit  --series jjk        # ALWAYS before indexing
python -m scriptengine.cli index  --series jjk        # add --no-embed to skip the GPU
python -m scriptengine.cli query  --series jjk "question"
python -m scriptengine.cli timeline --series jjk "Shibuya Incident"
python -m scriptengine.cli export --series jjk        # Obsidian vault in series/jjk/obsidian/
python -m scriptengine.cli eval   --series jjk        # regression suite
python -m scriptengine.cli page-run --series jjk --batch <slug>  # score one page's question batch
python -m scriptengine.cli canon-run --series opm    # cross-series gold regression
python -m scriptengine.cli span-recall --series jjk   # is EVERY line reachable? (offline, <1s)
python -m scriptengine.cli span-recall --series jjk --probe 400  # + live retrieval sample
python -m scriptengine.cli catalogue                  # regenerate docs/CATALOGUE.md
python -m scriptengine.cli script-path "Title" --create   # where a script goes
python -m scriptengine.cli verify "<script>" --series jjk # check its tags
python -m scriptengine.cli script-gen "Topic" --series jjk --words 6000  # write + verify a script
python -m scriptengine.api.main                       # serve on :8000
python -m scriptengine.mcp.server                     # MCP over stdio (research/verify_script/script_path)

python -m pytest tests/ -q
```

`crawl` resumes by default, so pages already on disk are skipped. `index` re-parses
from stored wikitext, so a parser fix reaches the whole corpus in seconds without
re-crawling.

## Working agreements

- **Verify against the live wiki, not just the tests.** Nearly every real defect
  in this project was found by running the pipeline against Fandom and reading
  the output, not by reading code. Tables being silently deleted, `{{Ruby}}`
  returning furigana, stale Qdrant vectors resolving to unrelated text: all
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
  question and record why in `gold_jjk.json`. Do not tune the retriever to make
  one ambiguous prompt go green.
- **Run `audit` before `index`.** A broken extractor is silent; that is the
  failure mode the audit exists to catch. On a new wiki, read `cited directly`
  and `sentences w/ chapter` first: they are how you find out that this wiki
  cites in a shape nothing here reads yet.
- **Run `span-recall` after `index`.** It proves every sentence in the corpus
  sits whole inside some chunk -- offline, exhaustive, under a second for a
  series. A re-index that silently drops content is otherwise invisible until
  someone happens to ask about the missing line: this is the check that caught
  the Trivia chunking gap on JJK, and found 1,039 unreachable lines on OPM and
  1,171 on Bleach. Exit 2 means content is unreachable; fix that before
  authoring anything against the index. See `reports/span-recall/README.md`.
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
- **Never let a server launch block the shell.** Start the `:8000` API fully
  detached: `setsid nohup python -m scriptengine.api.main > /tmp/scriptengine_api.log 2>&1 < /dev/null &`.
  A plain `nohup ... &` (no `setsid`) dies with the process group when the tool
  call is aborted, so the server silently stops. After launching, confirm with a
  *short, non-blocking* `ps` + `curl /health` (no `sleep`). What works and what
  does not (learned the hard way):
  - **`setsid ... &` does NOT make the bash tool return instantly.** The tool
    waits for the whole command up to its timeout (120s default) even with the
    job detached. So a "launch + poll" one-liner hits the 120s timeout. That is
    fine — `setsid` keeps the job alive after the timeout. Just launch it (let the
    tool time out if needed), then poll with separate *fast* commands. For long
    runs, pass a larger `timeout` (ms) to the bash call.
  - **Never a bare `sleep N`** — it reads as a hung shell and gets aborted. To
    wait, run a **bounded loop that prints a status line every ~15s** (short
    sleeps inside, status on every iteration), so the shell is visibly working.
  - **Long sequential background work:** `setsid nohup bash -c 'for s in …; do
    cmd "$s" >> /tmp/x.txt; done' > /tmp/x.txt 2>&1 < /dev/null &`, then poll the
    file with a bounded status-printing loop. The job survives the tool timeout.
- **GPU device selection for servers/APIs: CUDA first, CPU last.** Whenever
     you launch a server or API (`:8000` FastAPI, MCP, anything loading the
     embedder/reranker), decide the device in this order:
     1. **Check if the GPU is free** (`nvidia-smi`). If the card is free (or has
        room for the embedder + reranker, ~4–5 GB), **run on CUDA** (the default
        device — no `SCRIPTENGINE_DEVICE` override).
     2. **If it is not free, check if it can be freed** — stop a stale
        long-lived `:8000` server you are about to replace, stop a finished or
        interruptible GPU batch, etc. If you can free the card, **free it and
        run on CUDA**.
     3. **Only if the GPU cannot be freed, run on CPU** (`SCRIPTENGINE_DEVICE=cpu
        setsid nohup … < /dev/null &`). The standard case: ninfer's Qwen holds
        the card for extraction and the extraction model owns the GPU (hard rule
        below), so it cannot be freed — then CPU is the fallback. CPU page-runs
        are slow (cross-encoder ~14s/question): a 150-question batch takes ~35
        min, so kick it off detached and poll rather than blocking.
      4. **Borrow the headroom for a *short* `:8000` task, even with Qwen on the
         card.** Qwen's KV pool is *pre-reserved* (`--kv-capacity 155648`), so its
         ~24.6 GB is a fixed allocation and the ~7 GB "free" is genuinely spare
         headroom — Qwen only hits ~100% util *while decoding a prompt* and idles
         between bursts, when the 7 GB is free. For a **short, bounded** `:8000`
         run (e.g. a `span-recall` 400-probe, ~4 min) you *can* launch it on CUDA
         co-located with Qwen: the embedder+reranker load lazily per request
         (~5.3 GB), borrow the 7 GB, and Qwen survives (memory stays pinned, no
         OOM). Only do it when (a) Qwen is in a quiet window (low util, no
         extraction batch running), (b) the task is short, (c) you check Qwen's
         health right after (`nvidia-smi` / `kill -0`), and (d) you restore the
         safe steady-state (stop the CUDA `:8000`, bring up CPU `:8000`) when
         done. **Not** for `events-extract` / heavy LLM batches — those keep Qwen
         under continuous load and are what the hard rule below forbids co-locating.
- **Coverage is a live artifact, not a sentence.** No document states what is
      next or what remains — docs point at `reports/page-campaign/COVERAGE.md`,
      which `tools/coverage_report.py` regenerates (never hand-edited). Run it
      after every batch commit.
- **Council reviews run 5 advisors (then 5 peer reviewers) in parallel.** A single
  message spawns all five sub-agents at once and it works well: independence is
  preserved because every sub-agent starts with a fresh context and never sees the
  other responses. This is council-only — it does NOT extend the parallelism to
  other sequential work (e.g. a closure loop), which still runs one sub-agent at a
  time. (Recorded in the `llm-council` skill; the passes that use it live in
  `reports/comprehension/`.)

## Layout

```
scriptengine/
  config.py       settings; every value has a caller
  cli.py          Typer CLI: crawl, audit, index, catalogue, eval, verify,
                  script-gen, and the rest of the pipeline as commands
  ingest/         crawler, wikitext parser, ontology discovery, audit
  stores/         SQLite facts+graph+FTS5+categories, Qdrant local vectors
  index/          section-driven chunking, embedding, build
  retrieve/       hybrid (relevance), narrative (chronological) and roster
                  (enumeration, incl. the battles-in path) retrieval, plus
                  citations (chapter/episode)
  script/         writing loop: bundle → prompt → prose → verified file, with
                  tag repair and length-band enforcement
  api/            FastAPI on :8000; /context is the endpoint that matters,
                  rules.py is the script-writing contract it serves
  mcp/            MCP server over stdio (research, verify_script, script_path)
  eval/           gold question set and scoring harness, tag verification,
                  catalogue
series/<name>/    self-contained corpus + stores (gitignored)
legacy/           the retired pipeline, kept for reference
graphify-out/     knowledge graph of this repo
plan/             campaign governance: flow.md (trunk structure), drift_log.md
                  (append-only history + §4 current position), standing rules
reports/          dated run dirs + page-campaign/ (question batches, wave
                  records, COVERAGE.md) + comprehension/ (GATE.md, council
                  records + COUNCIL_HISTORY.md ledger)
tools/            offline harnesses: census_545.py, coverage_report.py, …
```

## Infrastructure

**No Docker. No database servers.** SQLite holds the facts, graph and BM25
index; Qdrant runs embedded. Nothing to start before working.

GPU: torch must be a CUDA build (`--index-url https://download.pytorch.org/whl/cu130`
for the RTX 5090). Everything works on CPU, slowly. The embedder and reranker
load on first use and unload when idle, because ComfyUI and a resident model
cannot share VRAM.

**Hard rule — the extraction model owns the GPU.** The 27B Qwen model
(`ninfer-serve` on `:18080`) holds ~24.6 GB of the 32 GB card, leaving ~7 GB for
its KV cache. When the `:8000` API's reranker also sits on the GPU it takes a
further ~4 GB, and the Qwen model OOM-crashes under load. That is exactly what
took down the first full-corpus extraction: **508/524 pages failed with
`[Errno 111] Connection refused`** because the model died mid-run. So when you
run `events-extract` (or any heavy LLM batch) on GPU, **dedicate the GPU to the
Qwen model**: stop the `:8000` API (or run it on CPU with
`SCRIPTENGINE_DEVICE=cpu`) first, then confirm `nvidia-smi` shows only the model
process and ~7 GB free before launching. Never run the extraction's LLM on CPU
as a workaround — the GPU is the path; just keep the card free for it. For
launching the `:8000` API itself, the decision order is the working-agreement
**"GPU device selection for servers/APIs: CUDA first, CPU last"** — free →
CUDA, can-free → free and CUDA, cannot-free → CPU. The one sanctioned exception
is a **short, bounded `:8000` probe** in a Qwen quiet window (working-agreement
point 4 above): Qwen's KV pool is pre-reserved, so its ~7 GB of headroom is
genuinely free between prompt bursts and a lazily-loaded embedder+reranker (~5.3 GB)
can borrow it — verified 2026-09-05 (a span-recall probe ran to completion with Qwen alive
throughout). The rule still stands for `events-extract` and any long,
load-sustaining LLM batch.

## Status

Eight Fandom wikis are indexed: Jujutsu Kaisen (the development + active-campaign
wiki), Bleach, Hunterpedia, One-Punch Man, Berserk, Chainsaw Man, Dragon Ball and
One Piece. The engine serves the writer through three doors that wrap the same
functions: the HTTP API on :8000, the Typer CLI, and an MCP server over stdio.

**The JJK prose pass is complete (2026-09-07): 100% on every in-scope narrative
page type** (characters, episodes, battles, techniques, chapters, synopses,
story arcs, events; in-scope content remainder 0). Final record — method,
crucial engine fixes, final state: `reports/page-campaign/PROSE_PASS_FINAL.md`.
The structured layer: ~1,355 declared roster entries in
`series/jjk/overrides.yaml` (verified against `facts.db`). Interval facts — a
character's state *during* an arc, which the infobox's current-state read cannot
express (the P4 4A S-group) — are declared per-wiki under `extra_facts` in the
same file and re-landed on every `index` by `scriptengine/index/build.py`
(P4.A). The method (user mandate): author natural questions; when one fails,
**diagnose the root cause and fix the gap** (fix gold / retire cross-page / fix
router or chunker) — never rephrase the question to dodge it. Coverage is a
regenerated list, not a number stated here — see
`reports/page-campaign/COVERAGE.md` (`tools/coverage_report.py`).

**Now active: JJK D6-comprehension completion (JJK only; stops before P6).**
The goal: the corpus *understands* everything about a character — what each
line/fact/prose/event means, whether it is an event, where it sits on the
anime's timeline, all structured dimensions (facts, history, fights); new
tables/modules (`relations`, `abilities`, a meaning layer, …) are in scope
where prose cannot do the job. Live remainder + the checkable definition of
"100% comprehension": `reports/comprehension/COMPREHENSION_REMAINDER.md`;
gate state: `reports/comprehension/GATE.md`; current position:
`plan/drift_log.md` §4. P6 (cross-corpus, `plan/Plan_to_perfection.md` §7)
waits until this run closes.

**Gates (re-run before calling any pass done):** `eval --series jjk` = 31/31;
`canon-run --series opm` = 10/16 exact, 236/236 canon, 79.0%; `pytest tests/ -q` = 1,239.
Batch files are `_`-prefixed so they stay out of the official gold bank. The
historical accuracy-campaign records (rounds 1/2, OPM + JJK waves) are in
`reports/page-campaign/STATUS.md` (the OPM handoffs `HANDOFF_OPM.md` /
`HANDOFF_ROUND2.md` were deleted 2026-09-07 — git-recoverable @ `faf6ce6`).

Two corpus quirks are the wiki's, not the pipeline's: Berserk cites cover art and
interviews (not instalments) so it sources 0%, and One Piece writes one page per
instalment (sourceable by route two); `audit` tells which a series is. Each wiki also
writes citations differently — that per-wiki vocabulary lives in
`series/<name>/overrides.yaml` (`wikitext.CitationGrammar`). Open: Marvel (legacy
Lua + `Marvel Database:Character Template`) is not re-tested since structural
discovery landed.
