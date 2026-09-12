# pi.md — the ScriptEngine agent kit (for pi sessions)

Read this at the start of a pi session (pointed to by `CLAUDE.md`). It
defines the standing rules the agent works under, the skill inventory, and
the **autonomous Qwen mode-switch protocol**. Details live in the referenced
docs; this file is the index plus the non-negotiables.

Companions: `docs/ops/QWEN_MODES.md` (the mode-switch method in full),
`plan/SWITCHPOINT.md` (the resume file), `.pi/skills/` (the skills).

---

## 1. Startup ritual (every session, in order)

1. `plan/drift_log.md` §4 — the live checkpoint (trunk/excursion position).
2. `reports/comprehension/GATE.md` + `COMPREHENSION_REMAINDER.md` — gate
   state and what remains to the comprehension goal.
3. `plan/SWITCHPOINT.md` — the last switchpoint (work in flight across
   sessions; if a fresh session was seeded from it, continue from there).
4. Mode check: `cat /home/goblin/ninfer-work/qwen_mode.txt` + `nvidia-smi`
   — which Qwen context mode is active, and where `:8000` should live.
5. If batch files were committed since: `reports/page-campaign/COVERAGE.md`
   (regenerate with `tools/coverage_report.py` when stale — never hand-edit).

**Status prose in docs can be stale; the checkpoint files above are
authoritative.** When they disagree, the checkpoint wins — and the stale
prose gets a one-line fix, committed.

## 2. Standing behavior rules (the "customizations")

### The three standing rules — `plan/STANDING_RULES.md` (verbatim authority,
repeated at the top of `flow.md`, `Plan_to_perfection.md`, `drift_log.md`)

1. **No user input. None, for the duration of the plan.** Every wall — a
   design fork, an ambiguous result, a blocked step, a judgement call, two
   defensible options — **run `llm-council` instead**: the council decides,
   the agent acts on its verdict and records it. No asking for approval,
   which option, or whether to proceed; no stopping to report progress and
   wait. The only stop is the halt path in `flow.md`, and it runs a council
   first. Council claims are **DB-verified before recording**; a council that
   cannot be verified against the store did not happen.
2. **The GPU is available. Do not default to CPU.** Check `nvidia-smi` free
   memory first and size the job against it. Short retrieval jobs co-locate
   with Qwen safely; a sustained 27B extraction batch wants the card to
   itself (one OOM-crashed at 508/524 beside the reranker). When the card
   cannot be freed, the job's fallback is the 100k switch — a campaign
   session runs it in a 100k side session via the gpu-handoff chain
   (`docs/ops/PC_GPU_HANDOFF.md`); CPU is reserved for the `:8000` service
   and short (<15 min) jobs (2026-09-08 owner correction: the old "CPU is
   the fallback" branch is retired).
3. **Council cadence — three mandatory points.** (a) Every 2–3 completed
   todos: a council reviewing *the fixes just made*. (b) At the end of every
   sub-list, **before the return pointer fires**: a council assessing whether
   the sub-list actually completed. (c) At every phase gate: the gate council
   specified in `flow.md`. Each is written to
   `reports/comprehension/COUNCIL_<subject>.md` and committed with the work
   it reviewed. **If it is not on disk, it did not happen.**

### Kit rules — the working agreements of `CLAUDE.md`, restated as the
agent's own defaults:

1. **Checkpoint-first.** Never start real work without knowing the live
   position (drift §4). End significant work with the `switchpoint` skill
   (commit + SWITCHPOINT), not with a transcript.
2. **Drift discipline.** Trunk steps are `P<phase>.<step>`, excursions
   `X<n>.<step>` (never a phase number). Append-only `drift_log.md` §5
   format. Every excursion gets its return pointer **when it opens**.
3. **Council, not user input, at forks** (standing rule 1, operationalized).
   Big decisions / big builds go through `llm-council` (**5 advisors one at a
   time → 5 peer reviewers one at a time → chairman verdict** — owner rule
   2026-09-08: sequential in any mode; the 5-parallel convention is retired —
   at 262k the children fight Qwen's shared KV pool for answering), recorded in
   `reports/comprehension/COUNCIL_<subject>.md` with claims DB-verified
   before recording. Cadence per standing rule 3. If it is not on disk, it
   did not happen.
4. **Gates discipline.** `audit` before `index`, `span-recall` after
   `index`, the four standing gates after any build (see the
   `scriptengine-gates` skill). A pass is done only when its gate re-ran
   green on the current store.
5. **GPU discipline.** CUDA-first, CPU-last. The extraction model (Qwen)
   owns the card for LLM batches — stop `:8000` (or run it on CPU) first.
   Servers launch detached (`setsid nohup … < /dev/null &`); poll with
   bounded status-printing loops, never a bare `sleep`.
6. **Commit discipline.** Branch `character-scoped-questions`, named paths
   only, area-prefixed messages, no push. `series/` gitignored; dated
   `reports/` dirs untracked.
7. **Code rules.** If a fix names a series and lives in a `.py` file, it is
   in the wrong place (`series/<name>/overrides.yaml` is the only per-wiki
   surface). Never guess a citation parameter's meaning. No dependency
   without a caller. Comments name the bug. "No third corpse": every new
   table ships with the door that reads it. Verify against live wiki output,
   not just tests. Script output follows the `humanscope` skill
   (`.pi/skills/humanscope/`); its compact form is served as `VOICE_RULES`.
8. **Docs as live artifacts.** Nothing states "what is next" in prose —
   docs point at regenerated files (`COVERAGE.md`, `qwen_mode.txt`,
   switchpoint). Fix stale status lines when you find them; commit the fix.

## 3. Skill inventory

Skills live in `.pi/skills/` (project, versioned) plus `~/.claude/skills`
(exposed via `.pi/settings.json` — that's where `llm-council` comes from).
They appear in pi's startup header; force-load with `/skill:<name>`.

| skill | when |
|---|---|
| `qwen-switch` | before/after any GPU phase; the autonomous mode switch |
| `switchpoint` | before a switch, at council cadence, on "checkpoint" |
| `opencode-watch` | keep an opencode TUI running autonomously: watcher auto-answers permission prompts (always-allow), wakes pi on MCQ / dead runs |
| `scriptengine-gates` | after any build / before calling a pass done |
| `humanscope` | every script: the voice contract — Structure Sheet before drafting, 30-feature audit on the finished draft (served in compact form as `VOICE_RULES`) |
| `llm-council` | every fork, big build, phase gate — **5 advisors one at a time, then 5 peers one at a time** (owner rule 2026-09-08; sequential in any mode — 5-parallel retired, 262k KV contention); record + commit |

### Packages (version-pinned in `.pi/settings.json`; installs live in the
gitignored `.pi/npm/`)

| package | gives the session | when |
|---|---|---|
| `npm:pi-subagents@0.66.0` | `subagent` / `bg_wait` / `subagent_supervisor` tools — child pi sessions with their own fresh context (builtin agents: `scout` / `researcher` / `worker` / `reviewer` / `oracle` / `delegate`; parallel fan-out via `workflowScript` + `runs.all([...])`, background children via detached runner) | the council convention is now one parallel `subagent` call instead of hand-spawned `pi -p` processes; parallel reviews; background work. Sessions started **before** the install do not have the tool; every new session does. Subagent-policy limits (262k → linear; 100k → ≤2; councils one agent at a time in any mode — owner rule 2026-09-08) still apply — Qwen's `--max-concurrency 3` is the hard ceiling. |
| `npm:@juicesharp/rpiv-todo@2.9.0` | `todo` tool + `/todos` command + a live todo panel **above the editor** (rebuilt from the conversation, so it survives `/reload` and compaction; `ctrl+shift+t` collapses it; per-session state, no disk writes) | long campaign runs: keeps the plan on screen. Note: pi 0.85's TUI has **no right-side panel surface** (widgets: above/below editor; overlays: floating, 9 anchors) — the registry has no right-panel plugin; this is the closest thing. |

## 4. Installed capabilities (tools on this machine)

Installed 2026-09-07 (git log for provenance). All additive — they extend
reach, they do not change the standing rules.

| tool | where | what / when |
|---|---|---|
| **`workflow` tool** (pi-dynamic-workflows, user pi-package) | auto-loads every pi session | Claude-Code-style fan-out: the model writes a small JS script; the tool runs it across isolated subagents and synthesizes. Use for codebase audits, multi-perspective review, fan-out research — including running the council's 5+5 as one workflow. **GPU interaction: keep fan-out inside the active mode's subagent policy** (≤ 2 in 100k; 5 is the council exception) — each subagent is a live Qwen context. |
| **ponytail** (pi-extension, user pi-package) | auto-loads; `/ponytail [lite\|full\|ultra\|off]` | "Lazy senior dev" code discipline: minimal, working code (benchmarked ~54% less LOC, safety tier held). Reinforces "no dependency without a caller" + minimal diff. On for code work. |
| **`headroom`** | `~/.local/bin/headroom` (venv `~/.venvs/headroom`) | Compresses big tool outputs / JSON / RAG chunks *before* they reach the model — **68% measured on a 191 KB JSON payload** (51k→16k tokens). Library: `~/.venvs/headroom/bin/python` + `from headroom import compress(messages, model='qwen3.8-27b', model_limit=<ctx>)` (user messages are protected; tool payloads compress). Use when a big output must be re-fed (crawl dumps, query banks) — slows transcript growth, keeps the 100k fit guard green longer. **Proxy/wrap modes (full-agent integration) change pi's provider path — enable only with the user's sign-off.** |
| **`agent-reach`** | `~/.local/bin/agent-reach` (venv `~/.venvs/agent-reach`) | Web reach: `agent-reach get rss.feed <q>`, `agent-reach get youtube.<cmd> <q>` (channels rss + youtube ready, no auth; `agent-reach doctor` to check). Skill: `~/.pi/agent/skills/agent-reach/SKILL.md`. For research outside the wikis. |
| pi-subagents, rpiv-todo (project pi-packages) | `.pi/npm/` | Already load: the subagent + todo tools this kit uses. |

## 5. Autonomous Qwen mode switching

The model serving pi is the local Qwen 27B (`ninfer-serve` :18080). Its
`--kv-capacity` pre-reserves the int8 KV pool, so **context length is a VRAM
dial**: 262k leaves ~3.5 GiB headroom (no CUDA co-location); 100k frees
~7–8 GiB (the `:8000` embedder+reranker co-locates on CUDA, ≤2 parallel
subagents). Full method: `docs/ops/QWEN_MODES.md`. Protocol:

1. **Decide at phase boundaries.** Switch **down** when the next phase needs
   the CUDA reranker *alongside* me, or 2 parallel subagents. Switch **back
   up** when the GPU phase ends. One switch per phase — no thrashing.
   A heavy Qwen LLM batch is the *opposite* rule (stop `:8000`, no switch).
2. **Pre-flight (model alive):** `switchpoint` checkpoint (commit +
   SWITCHPOINT); fit check `wc -c $PI_SESSION_FILE / 4` — the estimate is
   conservative (~2.7x overstated): estimate > target ctx but the real count
   fits → `FORCE=1`; real doesn't fit → fresh-session handoff (step 5).
   Confirm no `events-extract` in flight.
3. **The switch is ONE detached 3-part shell** (the agent's last act; the
   helper survives the agent's death — full spec in the `qwen-switch` skill):
   ```bash
   setsid nohup bash tools/master-work/switch_restart3.sh <mode> <session_file> <my_pi_pid> <old_shell|none> < /dev/null > /dev/null 2>&1 &
   ```
   part 1 unloads (`ninfer-stop.sh`); part 2 loads + places `:8000` + syncs
   `models.json` (`qwen-switch.sh <mode> --api [--force]`); part 3 is an
   INTERNAL LLM call (HTTP :18080 — never typed into any pane, owner
   correction 2026-09-10) which triggers `relaunch_term.sh`: a new
   gnome-terminal window running `pi --session <session_file>`, then the old
   pi + old window are closed (TERM → verify → KILL -9 — this machine's
   interactive bash survives a bare TERM).
4. **Post-flight (the new pi, same session):** verify the status line (new
   window), `qwen_mode.txt`, the tail of `/tmp/switch_restart3.log`, and
   `pgrep -P 3439`; report the state (mode/ctx/free/api) + flow-OK to the
   owner in ONE line; then stop. First turn is a cold prefill (~1–2 min).
5. **Overflow handoff:** if the REAL transcript doesn't fit the target
   context, do not FORCE — do a full checkpoint and hand the user the
   fresh-session one-liner (*"Read plan/SWITCHPOINT.md and continue from
   there"*). A fresh session's tiny transcript always fits.

**Subagent policy:** 262k → linear, no parallel subagents. 100k → ≤2
parallel. 150k (CSM Phase 1, 2026-09-08) → up to 2 parallel *working*
subagents per wave (deploy 2 → access results → deploy the next 2, never
queued) — `plan/CSM_2PHASE_PLAN.md`. `llm-council` runs **one agent at a
time in any mode** (owner rule 2026-09-08 — at full 262k context the five
children fight the shared KV pool for answering; the standing exception is
retired).

### GPU handoff (cross-session, council-verified 2026-09-08; **reserved for
Phase 2 / extraction — owner rule 2026-09-08**)

Phase 1 (the CSM fixing process) runs at the 150k dial with co-located CUDA
and 2-subagent waves (`plan/CSM_2PHASE_PLAN.md`) — no per-step switching.
When the plan hits a Phase-2 GPU step I cannot run inline (extraction,
exhaustive sweeps; smaller context if VRAM demands): full protocol in
`docs/ops/PC_GPU_HANDOFF.md`, executable chain
`tools/master-work/gpu-handoff.sh`. Gist:

- **Tier 1 (no mode flip):** deterministic Qwen batches (`events-extract`)
  run under 262k — Qwen owns the GPU, `:8000` stays CPU. Just detach batch +
  gated typer. No new session.
- **Tier 2 (the chain):** I write spec + SWITCHPOINT + commit, then my final
  action launches `gpu-handoff.sh --tier2` (plain shell B) → `100k --force`
  → fresh 100k pi session C (new terminal, runs the GPU task, writes the
  report) → script does the `262k` switch-back (absorbs "D") → a plain-shell
  gated typer types my fixed resume line into my window (no vision). I sit
  idle at my prompt meanwhile and continue from the report. C's transcript
  is trashed by me after I read the report; B/D have none.
- Fit-guard note: both switches take `--force` (deliberate handoff); never
  `--api` (the batch needs `:8000` on CPU); never delete C's transcript
  before the switch-back (poisons the 262k guard).

## 6. Reference map

| question | file |
|---|---|
| where is the trunk / what happened | `plan/drift_log.md` (§4 position, §3 ledger) |
| what remains to comprehension | `reports/comprehension/COMPREHENSION_REMAINDER.md` |
| gate state | `reports/comprehension/GATE.md` |
| council decisions | `reports/comprehension/COUNCIL_*.md` + `COUNCIL_HISTORY.md` |
| Qwen modes + switch method | `docs/ops/QWEN_MODES.md` |
| resume across sessions | `plan/SWITCHPOINT.md` |
| live mode record | `ninfer-work/qwen_mode.txt` |
| coverage | `reports/page-campaign/COVERAGE.md` (regenerated) |
| writing rules | `scriptengine/api/rules.py` + the `humanscope` skill (`.pi/skills/humanscope/`) |
| the three standing rules (plan-level, verbatim) | `plan/STANDING_RULES.md` (copies in `flow.md`, `Plan_to_perfection.md`, `drift_log.md`) |
| dimension map (R1–R5 retired) | `plan/Plan_to_perfection.md` §12 (+ §13 durable-key precondition) |
| council methodology | `llm-council` skill (`~/.claude/skills/llm-council/SKILL.md`, exposed to pi via `.pi/settings.json`) |
| installed tools / capabilities | §4 above + `pi list` |