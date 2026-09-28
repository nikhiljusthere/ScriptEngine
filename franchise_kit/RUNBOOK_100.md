# Runbook: taking a new franchise to 100%

Distilled from JJK (the first 100%), CSM, and the Marvel/MCU campaign (2026-09-25..28). Every ordering rule below exists because doing it the other way cost hours or days on a real wiki.

## 0. What "100%" means (owner's definition; it governs everything)

> "Every single line of the corpus should be **understood, recallable and traceable** by our RAG. Nothing should be left anywhere."

| layer | meaning | the checkable number | tool |
|---|---|---|---|
| **Recallable** (D5) | `/context` actually serves the line | tier-1 sweep over the pinned panel: HIT per door ÷ full panel | `span-recall --panel … --door {qa,narrative,roster}` |
| **Understood** (D6) | the line was read by the extractor and carries a row: an event with participants + a placement, or a named standing/atemporal class | every panel sentence inside a read passage + `comprehension-gate` coverage split; D4 = 0 violations | `events-extract` dry-run coverage, `comprehension-gate` |
| **Traceable** | the line resolves to its source (chapter / issue / episode / film) | `audit` citation coverage; gaps named by cause | `audit --series` |

Rules that follow:
- **Coverage is never a budget variable.** A council may rule on order, speed and sequencing, never on leaving lines unread.
- **No triage model may drop work** (JEV was removed from extraction for exactly this).
- **Tier 0 (chunk containment) is a precondition, not coverage.** It is true by construction.
- **Name the door.** A forced-door D5 number and an auto-routed one are different claims.

## 1. Roles

| who | does | never does |
|---|---|---|
| **Owner** | defines 100%; rules on scope (e.g. licensed/3rd-party titles), egress/VPN/ToS; authors the D2 blind question set (the executing side must not); schedules GPU windows; pastes or approves worker prompts | per-line judgement calls the plan can make mechanically |
| **Claude, architect/verifier** (full-GPU or side session) | writes the plan and worker prompts; runs the structure survey; decides overrides; reviews every worker design and commit **against the database, not the report**; runs speed engineering, identity proofs and the D3 sweep; monitors and steers the worker | long unattended extraction batches (the worker's Qwen is free and local) |
| **opencode on Qwen, worker** (`:18080`) | implements approved engine mechanisms with tests; runs extraction batches; writes receipts; runs gates; commits by named paths; runs councils when the plan requires one (`llm-council`, **one agent at a time**) | redesigning the plan; starting a second `events-extract` on the same series; running `:8000` while an extraction batch owns the card |

### How the architect drives the worker (proven 2026-09-28)
- **Shared state lives on disk:** `plan/SWITCHPOINT.md` (a dated entry per milestone at the top of "Current position"), `reports/<name>/REVIEW_*.md` (architect verdicts), commits, receipts.
- **Worker status comes from opencode's own records, never screenshots.** Read `~/.local/share/opencode/opencode.db` read-only: `session_message` rows of type `user` / `assistant` / `idle`. A newest `idle` row means the turn ended. Tool calls are in `~/.local/share/opencode/log/opencode.log`. Never read the account/credential tables.
- **Typing a reply into the TUI.** Needs the owner's `xdotool` permission.
  1. Use `xdotool windowactivate --sync <win>`, confirm `getactivewindow` equals `<win>`, then `xdotool type --clearmodifiers --file msg` and `xdotool key Return`.
  2. **Never use `--window`**: gnome-terminal ignores the synthetic events it sends, and three messages were silently lost that way.
  3. **Type only when the session is idle.** Mid-turn input is not queued reliably.
  4. **Verify delivery** by finding the text as a `type='user'` row.
- **Watcher:** a poll loop that emits only actionable lines: commits, new receipts, new `events-extract` processes (with their `SCRIPTENGINE_ANSWER_TOKENS`), "worker STOPPED" plus its last message, Qwen health, the `:8000` rule, and a 15-minute heartbeat.

## 2. Resource modes (the GPU is one 32 GB card)

| mode | who owns the card | runs | never alongside |
|---|---|---|---|
| **Q, Qwen-owned** | Qwen 27B (~24 GB) | extraction batches (`--workers 2`, leaving 1 slot for the worker), opencode | `:8000`; any in-process model job during a batch |
| **R, retrieval-owned** | `:8000` ×6 uvicorn workers on CUDA (~4 GB each) + a model-free `:8002` | D3 sweep, gates, bundle-identity proofs | Qwen |
| **Free CPU** (either mode) | none | survey, dry-runs, SQL verification, audits, unit tests, the D3 panel build | nothing heavy >15 min on CPU for model work (GPU-only rule) |

**Check utilization (`uptime` load vs cores, `nvidia-smi` util) whenever a long step runs: a single-threaded CPU step (a re-index) should always have GPU work overlapping it on another series' store.** A mode switch costs about a minute (unload Qwen / start `:8000`, or the reverse). **Batch the work by mode.** Do all Q-mode work together and all R-mode work together, and fill the other side's waiting time with CPU work.

Key measured numbers:
- **Extraction:** ~2.7–5 sections/min on 2 slots with thinking on. Answer budget 8,192 tokens; failed pages retry at `SCRIPTENGINE_ANSWER_TOKENS=20480` (Qwen's `--default-max-tokens`).
- **D3 sweep after the query-plan fixes:** qa ≈ 0.22 s/probe with 6 CUDA workers, narrative ≈ 0.02 s, roster ≈ 0.4–1 s. 517,960 probes: qa ~31 h, narrative ~3 h, roster ~1–3 days.

## 3. The phases, in order (what to do when)

Legend: **[C]** Claude/architect, **[W]** worker/opencode, **[O]** owner. GPU mode in brackets.

### Phase A: acquire the corpus (network-bound, [W] runs, [C] verifies; any GPU mode)
1. [C] Create the series id, write `plan/<NAME>_100_PLAN.md` from `PLAN_TEMPLATE.md`, and record the denominators to re-measure.
2. [W] `crawl --series <name> --start-url …`. Settings: resumable, stall watchdog (`CrawlStalled` → exit 42), browser UA, concurrency 2–3 on big wikis. Rotate egress on a throttle; never blind-retry the same IP. Stamp revids at crawl time.
3. [C] **Accounting must close exactly:** enumerated = on-disk ∪ skipped ∪ failed, every title with a cause. Delta-only re-enumeration afterwards (`recentchanges`); no full re-enumeration unless the owner asks.
4. [W] `audit --series <name>` **before** indexing.

### Phase S: survey and declare (model-free, **[C]** does this; fastest high-value step)
5. [W/C] `index --series <name> --no-embed` (a first pass for the survey).
6. **[C] `scriptengine/.venv/bin/python franchise_kit/tools/survey_wiki.py --series <name>`** (seconds). It reports:
   - S1: types + junk types + big `list`-typed articles;
   - S2: where the narrative lives (sections vs leads vs long fact values);
   - S3: headings outside the narrative test;
   - S4: placement candidates;
   - S5: time-axis signals;
   - S6: partition/reality;
   - S7: disambiguation hazards;
   - S8: speed indexes.
7. **[C] Declare** in `series/<name>/overrides.yaml` (reference: `OVERRIDES_REFERENCE.md`; template: `overrides.template.yaml`):
   - `type_aliases`;
   - `events.placement_types`;
   - `events.narrative_fact_keys` (**every** long prose key);
   - `events.axis` (date / chain / order / partition keys);
   - `events.reality` pattern;
   - `events.furniture`;
   - `content_sections`;
   - the citation grammar keys;
   - the roster registry.

   **Everything the extractor and the time axis need is declared BEFORE any extraction runs.** Marvel extracted first and then had to re-resolve 48% of its rows and re-derive every timeline position.
8. [C] If a shape cannot be declared: design note → review → [W] implements a generic mechanism + key (default inert) with tests → four gates.
9. [W] Full `index` (re-extract from stored wikitext; seconds to minutes). [C] re-runs the survey: types clean, `unknown` < 5%, no junk types, NOCASE indexes present.
10. [W] `chunk-containment --series <name>` = **0 unreachable** (tier 0). Fix misses via `content_sections` (Notes/References/Gallery prose), never by trimming the oracle.

### Phase C: understanding (GPU mode **Q**; [W] runs; [C] verifies each step against the DB)
11. [W] C1 structured facts (free, from infoboxes). C2 `category-relations`. C3 `alias-align` (disambiguation lists → aliases).
12. [W] **Events dry-run, full scope:** `events-extract --scope all --dry-run`. It must report:
    - per-class counts: sections by heading class, leads, fact passages per key, furniture excluded per heading, below-floor passages;
    - **the D6 coverage number: panel sentences inside a read passage ÷ all**. The target is 100% with every exception named.

    The prose test is *"contains ≥1 panel-eligible sentence"* (`span_recall.sentences(min_words=6)`, the same denominator as D3). It is never a word floor.
13. [W] **Pilot**, about 50 passages across every class (fact keys, narrative sections, list-shaped sections, leads). Record: s/passage, rows/passage, rejections per reason (verb / unknown participant / unquoted), and participant resolution (rows on hub/disambiguation/wrong-partition nodes must be ≈ 0). [C] verifies in SQL.
14. [W] Council on **throughput only** (batching short passages, slots, order: event-dense classes first so D4 rows land early).
15. [W] **Full run**, one `events-extract` per series (check `pgrep -af events-extract`), `--workers 2`. Re-run failed pages at `SCRIPTENGINE_ANSWER_TOKENS=20480` until `failed: 0`, or name each remaining page. Receipts per series, with **every zero-row passage accounted by reason**.
16. [W] **Time axis:** re-derive `temporal` / `arc_index` on stored rows from the declared signals (no re-extraction). [C] verifies temporal coverage: every eventive row placed, or counted residue (no-year dates and the like; never guessed). Where the wiki gives two orders (in-universe date vs publication), the **council** picks. Marvel issues carry both `releasedate` (on-sale) and cover `month/year`.
17. [W] `relations` / `abilities` passes. Plan C5 schedules each only with a named consumer query + a failing test, but under 100% none is left out; sequencing is the council's call.
18. [W] Four standing gates after every engine change (§4). [W] Re-index if derived layers changed.

### Phase D: verification and declaration
19. [O] **D2 blind set:** the owner authors ~24 corpus-blind questions per the named-limit classes. [W] `blind_panel.py validate` → freeze → score.
20. **[C] D3 tier-1 sweep, GPU mode R** (Qwen unloaded). Sequence:
    - pin the panel (`span-recall --make-panel`) and never re-pin mid-sweep;
    - `:8000` ×6 CUDA workers for qa, a model-free `:8002` for narrative → roster;
    - `span-recall --workers 16`;
    - the browser monitor `tools/marvel/d3_monitor.py` (to be generalized, see `CAMPAIGN_TOOLS.md`).

    **Only on the final build.** Any later index or extraction change forces a per-door ledger re-probe diff (first 100 rows: 0 verdict flips = rows stay valid, else clean-restart that door).
21. [W] D4 consistency: `comprehension-gate` + cross-page agreement → 0 violations.
22. [W] Miss files per door → root-cause each class → fix → re-gate → re-probe the affected rows.
23. [W] **D5 declaration council** (records only; the council, not the plan, declares 100%).

## 4. Gates (after every engine change, no exceptions)

The four standing gates, on CUDA:
- `pytest`: the pin; known env failures listed. Unset `FORCE_COLOR` or `test_page_gen` fails on ANSI codes.
- `eval --series jjk` = 31/31.
- `span-recall --series jjk` = 48,572 rc=0 plus the live probe ≈ 398/400.
- `canon-run --series opm` = 10/16 · 236/236 · 79.0%.

Plus the new series' own set: `chunk-containment`, `audit`, the census/OOS floor. **Commit before gating.** `canon-run` refuses a `:8000` that is older than the source; restart it.

**Speed-ups must be proven result-identical:**
1. Capture full `/context` bundles for a seeded sample per door **before** the change.
2. Re-capture after the change.
3. Require byte identity.
4. For a running sweep, re-probe its first 100 ledger rows: 0 verdict flips.

## 5. Time and resource savers (each cost real hours once)

- **Survey before anything.** Marvel lost roughly a day to a sections-only extractor, manga-shaped time-axis signals, a missing placement type, and an unaware participant resolver. The survey finds all of them in 10 seconds.
- **Declare → extract → sweep, in that order.** A D3 sweep on a build that C4 will change is wasted (Marvel paused a 30-hour sweep for this).
- **Profile before scaling.** Marvel's "GPU-bound" 8.9 s/probe was ~100% SQLite. The fixes were query plans, NOCASE indexes and store memos: 36–42× faster, byte-identical.
- **Run model-free work in the other mode's shadow:** surveys, dry-runs, SQL verification, tests, panel builds.
- **One writer per series** for extraction and for ledgers. Parallelism goes across doors or series, never inside one ledger.
- **Never trust a report number unchecked.** Architect verification against the DB caught:
  - 48% of events on the wrong entities;
  - 21,010 real sentences hidden by a 20-word floor;
  - 90% of MCU prose outside the heading list;
  - a duplicate extraction run.
- **Keep the worker's context lean** (it shares Qwen's KV pool with the extraction). Have it commit checkpoints often, since a long uncommitted turn can end mid-reasoning.
- **Logs go to `/tmp/opencode/`,** never the repo. Commit by named paths. Never touch the owner's dirty files.
