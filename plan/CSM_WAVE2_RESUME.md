# CSM resume — Wave 2 + §9a closure loop (owner-directed 2026-09-09)

Continues `plan/CSM_2PHASE_PLAN.md` (Phase 1) from where the 2026-09-08
switchpoint left it (Wave-2 pre-step graded PASS, 19:45). Deployed via the
A/B bay (`ab-bay` skill + `terminal-pilot` + `tools/master-work/csm-control.sh`).
Two owner directives added 2026-09-09, both load-bearing below: the **council
trigger** (§3) and the **JJK-100% invariant** (§4).

## 1. Progress review (what is done, with receipts)

| Item | State | Receipt |
|---|---|---|
| CSM-3 — D5 measurement infrastructure | done, `f93d396` | four §2a traps closed; pinned hashed panel keyed (title, section, sentence) with held-out split; CLI resume; hit_rate over the full panel denominator; all three doors; `span-recall` → `chunk-containment` rename (alias kept) |
| Wave-1 gates + 39-question seed bank | done | `reports/csm/CSM3B_GATES.md` @ `78b5cf3`; four standing gates re-baselined 2026-09-08 15:22–15:26: pytest 1,254 / eval jjk 31/31 / span-recall 48,572 offline + 390/400 probe / canon opm 10/16 · 236/236 · 79.0% |
| CSM-3b (post-council fixes) | done, ratified — council ledger row #20 | `reports/csm/COUNCIL_csm-3b.md`, rulings R-CSM3B-1..7 |
| Wave-2 pre-step (F1 ledger fix + live roster probe) | graded PASS 2026-09-08 19:45 | live interleaved 2-panel survival (pinned 168→172, held-out 9→13, both keyed ledgers retain own rows); F1 closed; roster-door 31/88 members (0 pre-fix) |
| **Next** | **Wave 2 → §9a closure loop iteration 1** | this plan, §5 |

## 2. Deployment — the A/B bay (per `ab-bay` skill)

**Dial first (CSM_2PHASE_PLAN setup step 1).** The owner booted Qwen at 262k
(`ninfer-start`, 2026-09-09). Phase 1 runs at 150k:
1. Commit the checkpoint (done — this plan's commit).
2. `ninfer-work/qwen-switch.sh 150000 --force` (the fit guard refuses a clean
   dial because the resumed session file exceeds 150k tokens; --force after
   the checkpoint is the established pattern).
3. Verify the generated profile carries `--vision`; add it if missing.
4. `nvidia-smi` after the dial: 150k leaves ≈5.2 GB free (< 6 GiB) → `:8000`
   stays **CPU service** only; all *job* model loads run in-process on CUDA
   under the one-copy rule (server down for pytest/eval, up for HTTP gates).

**A — tmux session `control` (the GPU supervisor).** Eyes = the machine
monitor: `setsid nohup bash tools/master-work/csm-control.sh <b_pid> work
reports/master-work > /dev/null 2>&1 &` (5-s process-tree poll of B's pi tree;
every shell → `shell_log.jsonl` with duration; auto-kill of provably-CPU model
work >15 s; LONG >300 s flagged, not killed; MODEL_DOWN >60 s backstop →
`ninfer_restart.sh`). A (the LLM) judges only by reading
`reports/master-work/shell_log.jsonl` + `interventions.jsonl` every ~3 min;
typed hints go through the monitor (and are file-probed after typing — never
assume a type landed); commit after each intervention batch.

**B — tmux session `work` (the worker).** Executes
`reports/master-work/CSM_WAVE2_JOB.md` in order. Contract line typed at
bootstrap: *"Control A monitors every shell you run — GPU-only, no CPU shell
>15 s, >300 s runs get flagged for A's judgment — re-run per its hints (they
appear in your terminal or `reports/master-work/interventions.jsonl`)."*

**Wave rule (unchanged):** B deploys exactly 2 working subagents (native pi
subagents) per wave → wait for both results on disk → B (as orchestrator)
verifies both with raw receipts → deploys the next 2. Never queue, never 3+.
Councils are a separate cadence, one agent at a time, any mode.

Exact bootstrap type-lines: `reports/master-work/CSM_WAVE2_JOB.md` §Bootstrap.

## 3. Council trigger (owner rule 2026-09-09 — supersedes "every 2–3 todos" for CSM)

Run the LLM council (sequential, one agent at a time; 5 advisors → 5 peer
reviewers → chairman; every claim DB-verified before recording; written to
`reports/csm/COUNCIL_<subject>.md` + the `reports/comprehension/COUNCIL_HISTORY.md`
ledger, committed with the work it reviewed) to assess correctness:

- **after every CSM phase completes** (assess the phase's work),
- **at every big decision** (a design fork, a triage call, a halt-path),
- **at every big engine change** (any fix that lands in `scriptengine/`,
  not a per-wiki override in `series/csm/overrides.yaml`).

The old "every 2–3 todos" cadence (Standing Rules 3a) is retired for CSM
work; the triggers above cover the same territory at decision boundaries.
If it is not on disk, it did not happen.

## 4. JJK-100% invariant (owner 2026-09-09)

Whatever CSM requires, **JJK stays at 100%**:

- The four standing gates stay at the 2026-09-08 15:22 re-baseline (pytest
  1,254 / eval jjk 31/31 / span-recall 48,572 offline + 400-probe live /
  canon-run opm 236/236 · 79.0%). After **every engine change** re-run all
  four (on CUDA, one-copy ordering). A regression = halt + fix under §3,
  never "record and move on."
- CSM work lands in **CSM-centric files only**: `tools/csm/*`,
  `series/csm/overrides.yaml`, `reports/csm/*` (and `gold_csm.json` only if
  R-CSM3B-5's condition ever authorizes it). **Never** the JJK baseline:
  `gold_jjk.json` (the official bank), `series/jjk/*`, the JJK overrides, or
  any JJK gate baseline.
- Per-wiki handling goes in `series/csm/overrides.yaml`, never in engine code
  naming a series (the standing rule). New CSM-specific engine files are
  allowed where the census/instrument work needs them — they are CSM-centric
  by construction (series-parameterized, `--series csm`), never JJK-patched.

## 5. B's units (full spec + bootstrap lines: `reports/master-work/CSM_WAVE2_JOB.md`)

1. **CSM-6 instrument (no extraction)** [worker sub 1 of the pair]:
   parameterize `census_dimensions.py` + `placement_audit.py` with `--series`;
   regenerate the §12 dimension map from CSM's own sections; the eight-verb
   100-sentence sample (reading, no model); frozen census sets (seeded +
   revid-stamped, generated fresh from CSM, never copied from JJK); T0 pilot
   via series-agnostic `page_gen.py` (freeze to JSON, seed + revid; record
   emergence + survival = pilot numbers #1/#2); cross-page fact census
   (SQL over the graph, <15 s).
2. **CSM-5 remainder** [worker sub 2 of the pair]: 5.3 pilot fixtures (only
   on the code CSM's fixes actually exercise); 5.5 generator-sliced gold +
   held-out set + pre-registered red list (NO LLM judge); 5.4 door pre-check
   (zero GPU — extraction only if the Wave-2 dimension census goes red); the
   twenty-failures set (named author = a fresh-context subagent, executed
   never edited).
3. **§9a closure loop, iteration 1**: batch sweep (Wave-1 pinned panel + the
   400-probe standing gate, on CUDA) → pre-triaged miss queue (MISS_DOC /
   MISS_SPAN / gate violation / twenty-failures hit) → serial engine-fix
   closure (one class per fix; per-wiki override preferred; never reword to
   pass). The orchestrator (B — never the fixing subagent) runs the sweep
   that grades a fix. Halt: miss-count regression or two no-reduction
   iterations → council (trigger §3b).
4. **Phase close (after items 1–3):** the four standing gates on CUDA (JJK-100%
   invariant) + council (trigger §3a, phase-completion assessment) + commit +
   `tools/coverage_report.py` → then Phase 2 (CSM-4 exhaustive tier-1) per
   `CSM_2PHASE_PLAN.md`, the gpu-handoff switching plan authorized there.

## 6. Doc changes made with this plan

- NEW: this file; `reports/master-work/CSM_WAVE2_JOB.md` (job spec + bootstrap lines).
- UPDATED: `plan/flow.md` (CSM 100% node: council trigger + JJK-100% invariant +
  A/B bay), `CLAUDE.md` (working agreements: council trigger line),
  `plan/drift_log.md` (D17), `plan/SWITCHPOINT.md` (position = restart → dial →
  bay → Wave 2).

## 7. Machine state at handoff (2026-09-09 ~01:50)

- Post-reboot (the owner powered the machine off at the end of the previous
  session and booted it back up).
- Qwen 262k via the owner's `ninfer-start` (pid 3550, `--vision
  --max-context 262144 --kv-capacity 262144`, 30.3 GB on the card, 1470 MiB
  free).
- `:8000` down (died with the power-off; the post-restart session brings it
  up per §2 — CPU service at 150k).
- No tmux sessions. The current pi session (pid 3702, window 54525962)
  restarts first per the owner ("i started ninfer with ninfer-start" — the
  fresh pi process reconnects to the freshly started server); the restart is
  the self-restart convention (detached helper, the agent never asks the
  owner).
- If the owner instead wants Wave 2 at 262k (no dial): the wave rule degrades
  to one working subagent at a time (262k headroom); say so at the restart —
  the default here is the 150k dial per the 2-phase plan.