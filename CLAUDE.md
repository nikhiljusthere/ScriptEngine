# ScriptEngine

A universal knowledge engine over Fandom wikis. It ingests a wiki, derives that
wiki's own entity taxonomy from the wiki itself, and serves ordered, cited,
structured context over HTTP to whatever writes the video scripts: an AI
assistant driving `POST /context` directly, or the legacy ComfyUI node.

**ScriptEngine does not write scripts.** It feeds the model that does, and it
serves the writing rules (`scriptengine/api/rules.py`) alongside the research so
the contract travels with the context.

## Start here

1. **Active work: the CSM (Chainsaw Man) 100% campaign, Phase 1** (JJK D6 is
   DONE — D1–D10, 2026-09-07, `reports/page-campaign/PROSE_PASS_FINAL.md`;
   CSM is the P6 successor corpus, not the finisher of JJK's open work).
   Phase 1 = the §9a closure loop on the frozen miss queue (fix the
   pre-registered fix-classes; four standing gates after each; halt at the
   extraction-gated floor). Live checkpoint: `plan/drift_log.md` (current
   position, D19) + `reports/csm/GATE.md` (CSM gate state) +
   `reports/master-work/PHASE1_JOB.md` (the P1.1–P1.4 job spec, owner
   2026-09-09). JJK remains at 100% (its prose pass is complete on every
   in-scope narrative page type) and is the baseline-exact reference every
   CSM engine change must not regress.
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
python -m scriptengine.cli chunk-containment --series jjk   # tier 0: EVERY line whole in a chunk (offline, <1s; alias: span-recall)
python -m scriptengine.cli chunk-containment --series jjk --probe 400  # + tier 1 live retrieval sample
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
- **Scripts must not sound AI-written.** The voice contract is the
  `humanscope` skill (`.pi/skills/humanscope/` — the AI fingerprint is in the
  story's structure, not its words: Structure Sheet before drafting, 30-feature
  audit after). Its compact form lives in `scriptengine/api/rules.py`
  (`VOICE_RULES`) and is appended to every context bundle; when reviewing or
  generating script output, run the skill's Mode B audit on the draft.
- **A script's shape comes from the owner's essence, not from the research**
  (owner rule 2026-09-09): before drafting any script, ask the owner for the
  essence — the opening (what the video starts on and how heavy it is), the
  pacing (anime scripts pace slowly), the resolution (the thematic verdict the
  video lands on, a reading not a literal claim), and the bad things /
  tragedies it works through in between. The research supplies the facts; the
  owner supplies the shape. If the owner asks, offer some options per element
  and let them pick. The engine serves this contract as `ESSENCE_RULES` in
  `scriptengine/api/rules.py` (folded into `writing_rules`, so `script-gen`
  and `/context` carry it with every bundle).
- **Every line of a script must be traceable to a chapter.** The `sourced:`
  header on each beat is computed in `scriptengine/retrieve/citations.py` by
  reading each `{{Ref}}` as covering the sentences before it and resolving the
  chapter to its episode through the graph. Numbers are looked up, never
  inferred: a chapter the anime never adapted gets no episode. `cli audit`
  reports the coverage and fails when citations stop reaching the prose.
- **A script ships in three layers.** The contract is in `scriptengine/api/
  rules.py` (`ANNOTATION_RULES`): a chapter/episode tag per contiguous run;
  verbatim quotes marked with their transcript timestamp `[E<n> mm:ss]`;
  and a `[covers X-Y]` source-span line after every third passage naming the
  events/battles and ch/ep ranges those passages draw on. `script-gen`
  (`scriptengine/script/writer.py`) always writes a words-only companion,`
  `<title>-clean.md`, beside the tagged script, and a deterministic backstop
  rebuilds the `[covers]` lines from the tags if the model left them out.
  A tag cites the thing the line is about (a character's span in an arc, a
  fight's span), not the whole arc. Full spec: `docs/SCRIPT_STYLE.md` §6.
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
    wait, run a **bounded loop that prints a status line every 10–15s** (short
    sleeps inside, status on every iteration), so the shell is visibly working.
    Always pass an explicit `timeout` to the bash call (loop horizon plus
    headroom) — an un-timed call that outlives its work reads as a hang.
  - **Long sequential background work:** `setsid nohup bash -c 'for s in …; do
    cmd "$s" >> /tmp/x.txt; done' > /tmp/x.txt 2>&1 < /dev/null &`, then poll the
    file with a bounded status-printing loop. The job survives the tool timeout.
- **GPU device selection for servers/APIs and any job: CUDA first, CPU last.** Whenever
     you launch a server or API (`:8000` FastAPI, MCP, anything loading the
     embedder/reranker) or a job that loads them, decide the device in this order:
     1. **Check if the GPU is free** (`nvidia-smi`). If the card is free (or has
        room for the embedder + reranker, ~4–5 GB), **run on CUDA** (the default
        device — no `SCRIPTENGINE_DEVICE` override).
     2. **If it is not free, check if it can be freed** — stop a stale
        long-lived `:8000` server you are about to replace, stop a finished or
        interruptible GPU batch, etc. If you can free the card, **free it and
        run on CUDA**.
     3. **If the GPU cannot be freed, do NOT default a *job* to CPU** (2026-09-08
        owner correction — the old "CPU is the fallback" branch is retired; it
        caused the CSM pytest CPU misrun). The job's fallback is the 100k
        switch: `qwen-switch.sh 100k` frees ~7–8 GB so the embedder+reranker
        co-locate on CUDA (100k use case 1). For a campaign session that must
        not block on the GPU, that 100k job runs in a FRESH 100k side session
        via the gpu-handoff chain (`docs/ops/PC_GPU_HANDOFF.md`, tier 2) — the
        campaign session sits idle, the side session does the GPU work, the
        chain flips back and types the resume. CPU is reserved for: the
        `:8000` *service* (it just runs slower) and short (<15 min) jobs
        (point 5).
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
     5. **No CPU job longer than 15 minutes (2026-09-07 user directive).** Any
        job that would run >15 min on CPU — or that would simply be *faster*
        on the GPU — runs on CUDA. If the 262k Qwen profile is holding the
        card, switch it to 100k first (`ninfer-work/qwen-switch.sh 100k --api`;
        frees ~9 GB and the embedder+reranker co-locate on CUDA — this is 100k
        mode's use case 1). CPU is reserved for short (<15 min) jobs and for
        running the `:8000` *service* while Qwen owns the card for a long LLM
        batch (the hard rule below — that clause is about the service, never
        about a job's own models).
- **Coverage is a live artifact, not a sentence.** No document states what is
      next or what remains — docs point at `reports/page-campaign/COVERAGE.md`,
      which `tools/coverage_report.py` regenerates (never hand-edited). Run it
      after every batch commit.
- **Council reviews deploy one agent at a time (owner rule 2026-09-08; the old
  "5 in parallel" convention is retired).** 5 advisors sequentially, then 5 peer
  reviewers, then the chairman — one sub-agent at a time, waiting for each result
  before spawning the next, in any Qwen mode. **Council trigger for CSM work
  (owner rule 2026-09-09): after every CSM phase completes, at every big
  decision, and at every big engine change — to assess correctness (the old
  "every 2–3 todos" cadence is retired for CSM; full form:
  `plan/CSM_WAVE2_RESUME.md` §3, `plan/flow.md` CSM node).** Whatever CSM
  requires, JJK stays at 100% — the four standing gates re-run after every
  engine change, and CSM work lands in CSM-centric files only (JJK baseline
  untouched). Independence is preserved either
  way (every sub-agent starts with a fresh context and never sees the other
  responses); the cost is wall-clock time only. Why: at full 262k context all five
  children fight Qwen's shared KV pool (`--max-concurrency 3`) for answering — the
  2026-09-05 5-parallel attempt failed, and the 2026-09-07 CSM council expired 2 of
  5 advisors while waiting for admission. The `llm-council` skill's sequential
  default is now the project convention.

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
CUDA, can-free → free and CUDA, cannot-free → 100k switch for the job
(`:8000` service → CPU). The one sanctioned exception
is a **short, bounded `:8000` probe** in a Qwen quiet window (working-agreement
point 4 above): Qwen's KV pool is pre-reserved, so its ~7 GB of headroom is
genuinely free between prompt bursts and a lazily-loaded embedder+reranker (~5.3 GB)
can borrow it — verified 2026-09-05 (a span-recall probe ran to completion with Qwen alive
throughout). The rule still stands for `events-extract` and any long,
load-sustaining LLM batch.

**Qwen context modes (262k exploratory ↔ 100k Phase-1/service).** Qwen's `--kv-capacity`
pre-reserves its int8 KV pool, so context length is a VRAM dial: the 262k
profile leaves ~3.5 GiB headroom (`:8000` must run on CPU — the old "short
CUDA probe" exception above was measured at a smaller KV pool and does not
apply to the current 262k profile), while the 100k service profile frees
~7–8 GB so the embedder+reranker co-locate on CUDA and up to 2 subagents run
in parallel (llm-council runs one agent at a time in any mode — owner rule
2026-09-08). **Phase 1 runs at 100k** (the live CSM dial, switched from the
draft 150k at the P1.1 boundary, council #24/#25): the campaign's *fixing
process* runs at 100k with **up to 2 parallel working subagents per wave**
(deploy 2 → access results → deploy the next 2, never queued) and **all
model/GPU work on CUDA — no CPU shell command may exceed 15 s**. The 150k
profile is retained for a heavier single-pass context if a Phase-2 extraction
leg needs it. The gpu-handoff switching plan
is **reserved for Phase 2 (extraction)**; it is not used per-step in Phase 1.
Switching is
checkpoint (`plan/SWITCHPOINT.md`) → `ninfer-work/qwen-switch.sh` (one atomic
call — the pi agent may switch autonomously at phase boundaries, `pi.md` §4)
→ resume; the agent has no model during the ~30–60 s reload window, but the
pi process survives and the transcript is on disk. Full method + guardrails:
`docs/ops/QWEN_MODES.md`.

**The pi-session agent kit is `pi.md` (repo root).** Standing behavior rules
(checkpoint-first, drift/council/gate/GPU/commit discipline, the code rules),
the skill inventory (`.pi/skills/` — `qwen-switch`, `switchpoint`,
`scriptengine-gates`; `llm-council` via `.pi/settings.json` →
`~/.claude/skills`), and the **autonomous** Qwen mode-switch protocol (phase-
boundary switches as one atomic tool call, hard transcript fit-guard,
overflow handoff). A fresh pi session reads `pi.md` §1 (startup ritual) first.

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

**Now active: the CSM (Chainsaw Man) 100% campaign, Phase 1 (the §9a closure
loop).** JJK D6 is DONE (D1–D10, 2026-09-07) and is the baseline-exact
reference every CSM engine change must not regress. The goal: CSM reaches the
same checkable 100% bar over its own corpus — the §9a closure loop fixes the
pre-registered fix-classes (R-1…R-7), re-runs the four standing gates after
each, and halts at the extraction-gated floor (22 floor rows + the 21-red
extraction class, Phase 2). Live state: `reports/csm/GATE.md` (CSM gate state)
+ `plan/drift_log.md` (current position, D19) + `reports/csm/
miss_queue_csm_iter1.jsonl` (the frozen miss queue). P6 (cross-corpus,
`plan/Plan_to_perfection.md` §7) waits until Phase 1 closes.

**Gates (re-run before calling any pass done; re-baselined 2026-09-08 via the
gpu-gate3 100k+CUDA side session — raw receipts `reports/csm/GATE_REBASELINE_2.md`):**
`pytest tests/ -q` = **1,305** (the current gate-1 pin; the 1,303 baseline +
2 new R-2/R-3 tests, council #23). Per Ruling 5e a known +N test delta does
not re-run the gates — the full four-gate re-run happens at each fix-class's
closure. (Historical: 1,249 re-baselined 2026-09-08; 1,254 = 1,249 + 4 CSM-3
+ 1 CSM-3b roster-door test @ `f93d396`.) `eval --series jjk` = 31/31 (15:22–15:23); `span-recall
--series jjk` = 48,572/48,572 offline (rc=0) + 390/400 live probe (97.5%;
15:23–15:26, CUDA `:8000`); `canon-run --series opm` = 10/16 exact,
236/236 canon, 79.0% (15:26, `--skip-eval` one-copy rule).
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
