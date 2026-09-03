# HANDOFF — OPM Top-25 Page Campaign (start here in a fresh session)

Drop this file into a new session and work top to bottom. It is the complete handoff: what the
project is, how to drive it, the tool surface (CLI / MCP / HTTP), the graphify knowledge-graph
workflow, and the timeout/encoding rules that cost real time last session. The campaign plan itself
lives at `C:\Users\Nikhil\.local\share\opencode\plans\opm-top25-page-campaign.md` — read it for the
per-cluster queue and the six-class checklist; this file is the *how*, that one is the *what*.

> **Round 1 is complete (2026-08-21, all 15 OPM clusters at a clean sweep).** For round 2 —
> the global fix pass over every wrong answer, the remaining clusters 16-20, and the 200
> fresh questions — start from **`HANDOFF_ROUND2.md`** instead (it links the
> **`WRONG_ANSWERS.md`** inventory and the fix plan G1-G8). This file stays as the
> environment/commands reference for both rounds.

---

## 0. What you are doing

Drive every top One Punch Man wiki page to **100% accuracy**, cluster by cluster, keeping gates
green. For each top page (by corpus size) exactly **100 sourced questions** scoped to that page's
cluster live in `questions/_opm_page_<slug>.json` and are scored live with
`cli page-run --series opm --batch <slug>`. A cluster is done at **100/100** (every set exact, every
fact present in the returned bundle) **and** a human six-class review finds no malformed/circular/
incomplete item.

OPM-specific facts that differ from JJK:
- OPM is already crawled + indexed (`series/opm/facts.db` ~45 MB, `vectors/` present). No crawl/index
  step unless you change the parser.
- `_opm_battles.json` **already exists** (per-character battle sets) — reuse its titles; don't rebuild.
- OPM's citation grammar numbers **webcomic (`wch`) and manga (`ch`) apart**. This is the #1 trap for
  any "which chapter / first appearance" fact.
- Some content (God, late S-Class) is webcomic-only — scope those questions or retire the clause.
- **There is no OPM eval bank** (`scriptengine/eval/gold_opm.json` is absent, so `eval --series opm`
  cannot run). The operational baseline is `canon-run --series opm` — recorded 2026-08-20-2312:
  exact **8/16**, canon **235/237 (99.2%)**, precision **78.5%**, fact **18/20**. Keep it from
  regressing; treat any drop as a regression.

---

## 1. Environment & commands

Repo: `E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine` (git). Windows PowerShell 5.1.

- **No `&&`.** Use `cmd1; if ($?) { cmd2 }`.
- Python: call the venv interpreter directly and set the path first:
  ```powershell
  $py = "E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine\scriptengine\.venv\Scripts\python.exe"
  $env:PYTHONPATH = "E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine"
  $env:PYTHONIOENCODING = "utf-8"   # ALWAYS, before any page-run / eval / graphify print
  ```
- **Server** (must be up for `page-run`/eval; it is down at the start of a fresh session):
  ```powershell
  Start-Process -FilePath $py -ArgumentList "-m","scriptengine.api.main" -WindowStyle Hidden
  # poll until: Invoke-RestMethod http://localhost:8000/health  -> "device":"cuda", series incl. opm
  ```
  **Restart it after ANY engine or `series/opm/overrides.yaml` edit** — the store is re-read on start,
  and a stale server makes `canon-run`/measurement untrustworthy (there is a staleness guard that
  compares the server's start time against code mtimes). If port 8000 is busy:
  `Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force`.

- **Core loop:**
  ```powershell
  & $py -m scriptengine.cli page-run --series opm --batch <slug>   # exit 0 = 100%, 2 = failures remain
  ```
  Loads `questions/_opm_page_<slug>.json`, scores against the live server, writes
  `reports/page-campaign/<run>/REPORT.md`.

- **Gates (after any engine/overrides change):**
  ```powershell
  & $py -m scriptengine.cli canon-run --series opm  # must hold the 2026-08-20-2312 baseline (8/16, 235/237, 78.5%, 18/20)
  & $py -m pytest tests/ -q                          # repo-wide baseline: 985 passed (2026-08-21)
  ```
  (`eval --series opm` cannot run — no `gold_opm.json` on disk.)
  Pre-existing LSP type errors in `roster.py` (~898/~3261/~3631) and `test_roster.py:143` are NOT
  regressions — ignore them.

---

## 2. Timeout-loop rules (learned the hard way last session — do not re-learn)

These cost real time. Follow them from the first command.

1. **The bash tool's default timeout is 120 s.** Anything that walks or hashes a large tree exceeds
   it and gets killed mid-run, losing all output. Pass an explicit `timeout` (ms):
   - graphify `detect_incremental` over this repo: ~18–30 s normally, but **use 300000** to be safe.
   - AST extraction (`graphify.extract`) over ~100+ files: **300000**.
   - clustering + report generation on a ~4k-node graph: **300000**.
   - `page-run` / `eval` against the live server: usually fine at default, but give **120000–180000**
     for big batches.
2. **"Is this taking too long?" — know which steps are slow vs fast.** Slow (minutes): LLM semantic
   subagents, AST over many files, first-time embedding/index. Fast (seconds): detect, merge, cluster,
   report, `page-run` on a warm server. If a *fast* step hangs, it is stuck (usually the spawn crash
   below), not working — kill and fix rather than wait.
3. **Windows multiprocessing "spawn" crash.** Any script that calls `graphify.extract()` (or anything
   spawning a process pool) MUST wrap its work in `if __name__ == '__main__':`. Without it, the spawned
   children re-import the module and re-run `extract()`, recursing until
   `RuntimeError: An attempt has been made to start a new process before the current process has
   finished its bootstrapping phase` — and you get a **bogus 0-node result** that looks like success.
   Symptom: a wall of "worker failed … terminated abruptly" warnings, then `AST: 0 nodes`. Fix = add
   the guard, re-run.
4. **PowerShell mangles inline Python.** `python -c "…"` with nested double-quotes, backticks, or
   f-strings containing quotes gets corrupted by PowerShell (drops inner `"`, breaks `\`), producing
   `SyntaxError: unterminated string literal`. Two safe patterns:
   - Write a throwaway `.py` file and run it (`& $py .\temp_script.py`). **Preferred** for anything
     non-trivial.
   - Or pipe a here-string to stdin: `$code = @' … '@; $code | & $py -`.
5. **cp1252 stdout crashes on unicode.** The Windows console is cp1252 and throws `UnicodeEncodeError`
   on macrons (ū) or arrows (→) mid-run, discarding all output after that line. Always set
   `$env:PYTHONIOENCODING="utf-8"` first. When *writing* JSON/text from Python, pass
   `encoding='utf-8'` to `write_text()` — the default is cp1252 and will choke on a `→` in a label.

---

## 3. Tool surface (three doors over the same functions)

The engine serves the writer/researcher through three equivalent doors. For this campaign you mostly
use the **CLI** (`page-run`, `eval`) and read **wikitext directly**; use MCP/HTTP when a script or an
agent host needs it.

- **CLI (Typer)** — what the campaign drives:
  - `page-run --series opm --batch <slug>` — score one page batch live.
  - `eval --series opm` — regression suite over the official bank (`questions/opm.json`).
  - `query "question"`, `timeline "<subject>"`, `canon-run --series opm`, `audit --series opm`,
    `verify "<script>" --series opm`, `catalogue`.
- **MCP (stdio)** — `python -m scriptengine.mcp.server` exposes three tools for an agent host:
  - `research(subject, series="jjk", mode="auto", words=6000)` — the `/context` bundle + rendered
    prompt with house rules. Use to pull OPM context into a writing session.
  - `verify_script(text, series="jjk")` — check every chapter/episode tag against the raw crawl;
    returns `{tags, distinct, findings, passed}`. A script is not done until `passed: true`.
  - `script_path(title)` — where a finished script is saved (`scripts output/Video N - <Title>/…`).
- **HTTP (FastAPI :8000)** — `POST /context` is the endpoint that matters; `/health` for liveness.

**Scoring model (why answers must be exact substrings):** sets pass when returned members == gold
exactly. Facts pass when every gold item is present in the normalized bundle haystack — `norm()` =
NFKD-strip diacritics, lowercase, `&`→and, non-alnum→space, plural-fold; match = **word-boundary
containment** (so "December 24th, 2018" ≠ "December 24, 2018"). Fact items support `aliases`;
`accept:"all"` (default) requires every item, `accept:"any"` one. `expect_mode` in a batch is
metadata only — never used for scoring.

**Router rules that shape how you phrase questions** (`retrieve/router.py`, order matters):
1. chronology → roster · 2. **`how many` anywhere → roster** (misroute #1: prose numbers can't be
   found in a roster bundle) · 3. wh-interrogative, not plural-ask, subject ∉ {event, media} → qa ·
4. `looks_like_enumeration` → roster · 5. **`who|what|which are|were` → roster** (misroute #2) ·
6. interrogative + story verb, or subject_type ∈ {event, media} → narrative · 7. bare name ≤4 words →
qa; default → narrative.
Consequences: phrase counts as attribute lookups ("What number of X…"); ask parent/relative questions
in the singular; anchor event-subject facts to a character to pull them back to qa.

**Batch schema** (`questions/_opm_page_<slug>.json`): top-level `{series, wiki, updated, note,
questions[]}`; each question has `id (opm-pg-<slug>-NNN), kind(set|fact), question, subject, tier:
wiki, expect_mode, scope(closed|core|open), answer[{item, aliases?}], sources[], verified, note?`.
The `_` prefix keeps batches out of the official bank.

---

## 4. The graphify knowledge graph (this repo is graphified)

`graphify-out/` holds a persistent knowledge graph of this codebase: `GRAPH_REPORT.md` (human audit —
god nodes, communities), `graph.json`, `graph.html` (open in any browser). Use it to orient fast
instead of re-reading the tree. Current state after the 2026-08-20 update: **3819 nodes / 8562 edges
/ 225 communities**; top god nodes are `FactStore`, `Settings`, `SeriesPaths`, `build_roster()`.

- **Query it** (read-only, no rebuild): `/graphify query "<question>"` (BFS), `--dfs` for a specific
  path, `--budget N` to cap tokens; `/graphify path "A" "B"` for shortest path; `/graphify explain
  "Node"`. Example: `/graphify query "how does roster routing decide battles-in"`.
- **Keep it current** after code/doc changes: `/graphify . --update` (incremental — re-extracts only
  changed files). It reads `.graphifyignore` at the repo root, which scopes the graph to source +
  design docs and excludes `series/*`, `reports/`, `questions/`, `sample scripts/`. **Do not delete or
  weaken `.graphifyignore`** — without it a scan pulls in ~26k wikitext JSONs. A `.graphifyignore`
  *replaces* the `.gitignore` fallback (it does not add to it), so every exclusion is spelled out in
  that file already.
- **When to re-run:** after you finish a cluster and touch `roster.py`/`router.py`/new modules, or
  after adding design docs. It is cheap for code-only changes (AST only, no LLM). Docs/papers trigger
  the LLM semantic subagents (the slow part — see §2 timeout rules).

---

## 5. The campaign loop (per cluster) + triage rule

1. **Read** the cluster's source pages in `series/opm/wikitext/*.json` (field `wikitext`). Note what
   is chunked vs unchunked: infobox, `{{Nihongo}}`/romaji, scrollbox tables, and OPM's
   `{{Ref|chap=N}}` / `{{Ref|wch=N}}` frequently hold the *only* copy of a number.
2. **Draft exactly 100 questions** in `questions/_opm_page_<slug>.json`: a handful of **set**
   questions (battles — reuse `_opm_battles.json` titles, aliases, named moves, arc membership) and
   ~90+ **fact** questions (`accept: all`, multi-part where natural), phrased to route qa. Verify every
   answer phrase verbatim in the stored wikitext before scoring; mirror NFKD folding and `-th` date
   forms exactly.
3. **Declare rosters** in `series/opm/overrides.yaml` for any set discovery can't read (battles
   category, one-field alias, named-move lists). **Quote comma-containing YAML list items.** Restart the
   server after editing overrides.yaml.
4. **Run** `page-run --series opm --batch <slug>`; triage every miss; repeat to 100/100.
5. **Six-class review pass** over the whole batch (see plan); fix in place.
6. **Gates:** `canon-run --series opm` holds the 2026-08-20-2312 baseline + `pytest tests/ -q` 985 passed.
7. **Record** a row in `reports/page-campaign/STATUS.md` (first-run score, rosters declared, retires
   with reasons, gold fixes).

**Triage rule (the whole game):** every failure is read against the stored wikitext before touching
gold. Gold error (answer not on the wiki in that form) → fix the batch. Engine gap → rephrase to a
natural question inside the routing contract, or declare a roster in `series/opm/overrides.yaml`.
**Never tune the retriever for one prompt.** A "how many" whose number lives only in an unchunked
region (`{{Ref|chap=N}}`/infobox/scrollbox) cannot be golded to that number — retire the clause, keep
the retrievable part.

---

## 6. Queue & state

Cluster queue (by corpus size; story/character content leads): **1 Saitama → 2 Garou → 3 Genos →
4 Monster Association Arc → 5 Tatsumaki → 6 Chapters & Volumes → 7 Story Arcs** → then the
S-Class tail (Empty Void, Blast, Orochi, Beaut, Bang, God, Flashy Flash, Deep Sea King, Boros,
Superalloy Darkshine, Phoenix Man, Fuhrer Ugly). Full table + per-cluster notes in the plan file.

- **Clusters 1-15 are DONE (all 2026-08-21).** Every one of `questions/_opm_page_<slug>.json`
  for Saitama, Garou, Genos, Monster Association Arc, Tatsumaki, Chapters & Volumes, Story Arcs,
  Empty Void, Blast, Orochi, Beaut, Bang, God, Flashy Flash and Deep Sea King is at a clean
  sweep (12 at 100/100; Story Arcs 97/97, Flashy Flash 91/91, Deep Sea King 84/84 after
  retires-with-reasons), with rows 10-24 in `STATUS.md`. The agreed campaign scope was these
  15 clusters; it is complete.
- Final gate after the last cluster (2026-08-21-1904): `canon-run --series opm` at
  8/16 exact, 235/237 canon (99.2%), 78.5% precision, 18/20 fact -- identical to the
  2026-08-20-2312 baseline (no regression); `pytest tests/ -q` 985 passed.
- **If the campaign continues**, start at cluster 16 (Boros), then 17 Superalloy Darkshine,
  18 Phoenix Man, 19 Fuhrer Ugly, 20 Mysterious Beings (umbrella). The server is down at the
  start of a fresh session — start it (§1) and confirm `/health` first.
- Two structural findings are recorded in STATUS.md ("OPM campaign status"): the chronology
  path intercepts "every/all" enumeration phrasing (saga-membership and "every battle of X"
  sets are unanswerable for OPM), and `canon_gold.norm`'s one-s plural fold means chunked
  inflected verbs (`smashe`) never match gold (`smashed`) -- re-gold to a retrievable
  sub-phrase instead of tuning the scorer.
- JJK remains fully green in parallel (9/25 clusters done, eval 24/24) — do not regress it while
  working OPM; the gates are repo-wide.

## 7. Definition of done (per cluster)

- `page-run` reports **100/100** for the batch.
- Human re-read: no malformed / circular / incomplete item (six-class checklist clean).
- `canon-run --series opm` at its 2026-08-20-2312 baseline; `pytest tests/ -q` 985 passed.
- STATUS.md has the cluster's row with rosters declared + retires-with-reasons.

## 8. Out of scope / deferred

- No `.py` changes and no mid-campaign router fixes — OPM inherits JJK's already-shipped router work.
  If a page reveals a genuine routing gap that neither rephrasing nor a roster declaration solves,
  **stop and confirm** before touching `router.py`.
- Typo/spelling forgiveness stays deferred (no spelling-correction layer exists).
