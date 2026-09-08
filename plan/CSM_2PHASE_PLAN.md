# CSM 100% — two-phase execution plan (owner-directed 2026-09-08, supersedes the per-step gpu-handoff usage)

## The two phases

**Phase 1 — the fixing process (this plan's main body).** Exploration, audit,
indexing, measurement infrastructure, engine fixes, gate re-baselining —
i.e. campaign items 3, 5, 6 (instrument half) + the §9a closure loop.
Runs at a **150k Qwen dial** (one `qwen-switch.sh 150000`, then steady — NOT
the switching plan). **2 parallel working subagents per wave**: deploy 2 →
the orchestrator accesses both results → deploy the next 2. **No queueing**
(the orchestrator never has >2 children in flight; subagent waves are
sequential pairs). **All model/GPU work on CUDA** (co-located under the 150k
dial, one-copy-of-embedder rule); **no CPU shell command may exceed 15 s** —
anything that would (full pytest, eval, probe, canon) runs on GPU.

**Phase 2 — GPU / reranker / extraction.** D5 exhaustive tier-1 × 3 doors
(~51 GPU-h, 2 GPU-days) + D6 extraction (only if the dimension census goes
red) + the done-declaration. **Even smaller context if VRAM demands**
(e.g. 64k/100k dial). **The gpu-handoff switching plan is authorized here**
(batched side sessions in Qwen quiet windows); it is NOT used in Phase 1.

Standing rules unchanged: council **one agent at a time** (any mode) —
councils are a separate cadence, not part of the 2-subagent waves; raw
receipts; per-wiki overrides only; JJK baseline untouched; coverage_report
after every commit; the four standing gates before a pass is declared done.

## Setup (supervisor does this once, before Phase 1 starts)

1. Dial Qwen **262k → 150k** (`ninfer-work/qwen-switch.sh 150000`; one atomic
   call, ~30–60 s model-less window; pi processes survive). Verify the
   generated profile carries `--vision` (owner depends on VLM confirmation);
   add it if the generated profile lacks it.
2. `nvidia-smi` AFTER the dial (vision's fixed allocation eats headroom):
   - free ≥ 6 GiB → move `:8000` to **CUDA** (co-located; one-copy rule with
     in-process CLI jobs: server down during pytest+eval, up for HTTP gates).
   - free < 6 GiB → `:8000` stays CPU **only for its service role**; all
     *job* model loads still run in-process on CUDA (one copy at a time,
     stop `:8000` first). If even in-process CUDA OOMs, dial down to 100k
     (the owner's "even smaller context" clause) and re-measure.
3. Retire the 262k-declared CSM session (262k-in-memory > 150k-live = the
   overflow class). Launch a **fresh CSM session** (starts after the dial →
   declares 150k, clean). Bootstrap = this plan + the campaign todos
   (SWITCHPOINT "Campaign todos" section, which the session rebuilds its
   panel from and syncs).
4. Commit everything (checkpoint before the dial).

## Phase 1 — subagent waves (the orchestrator = the CSM session; fleet =
`delegate`/`worker`/`oracle`/`reviewer`/`scout`/`researcher` on local Qwen)

Wave pattern (hard rule): **deploy exactly 2 → wait for both results →
orchestrator accesses/verifies both on disk (raw receipts) → deploy the next
2. Never queue, never 3+.** Each subagent's work is on disk (reports/csm/),
so "access" = reading their artifacts, not their transcripts.

- **Wave 1**
  - Sub 1 (worker): **CSM-3 — D5 measurement infrastructure**: close the four
    §2a traps (pinned hashed panel keyed (title, section, sentence) with a
    held-out split; wire CLI resume keyed (title, sentence); hit_rate over
    the full panel denominator; all three doors (qa + roster + narrative);
    rename tier-0 `span-recall` → `chunk-containment` (alias kept)).
    pytest green; two consecutive sweeps reproduce the identical panel.
  - Sub 2 (worker): **gate + bank on GPU**: re-run the standing gates
    (pytest model tests / eval jjk / span-recall probe 400 / canon opm) on
    CUDA (one-copy ordering, server down for in-process, up for HTTP); run
    the 39-question CSM seed bank against the current index; record stale
    expectations + fix with reasons (raw receipts to reports/csm/).
- **Wave 2**
  - Sub 3 (worker): **CSM-6 instrument (no extraction)**: parameterize
    `census_dimensions.py` + `placement_audit.py` with `--series`; regenerate
    the §12 dimension map from CSM's own sections; the eight-verb
    100-sentence sample (no model — reading); frozen census sets (seeded +
    revid-stamped, generated fresh from CSM, never copied from JJK); T0
    pilot via series-agnostic `page_gen.py` (freeze to JSON, seed + revid,
    record emergence + survival = pilot numbers #1/#2); cross-page fact
    census (SQL over the graph — <15 s).
  - Sub 4 (worker): **CSM-5 remainder**: 5.3 pilot fixtures (only on the code
    CSM's fixes actually exercise); 5.5 generator-sliced gold + held-out set
    + pre-registered red list (NO LLM judge); 5.4 door pre-check (zero GPU —
    narrative door against existing cheap signals; extraction only if the
    Wave-2 dimension census goes red); the twenty-failures set (named author
    = a fresh-context subagent, executed never edited).
- **Between waves:** council (one agent at a time) reviewing the fixes just
  made (standing cadence: every 2–3 todos) → `reports/csm/COUNCIL_*.md`.
- **Then: the §9a closure loop, iteration 1**: batch sweep (Wave-1 pinned
  panel, 400-probe standing gate on CUDA) → pre-triaged miss queue
  (MISS_DOC / MISS_SPAN / gate violation / twenty-failures hit) → serial
  engine-fix closure (one class per fix; per-wiki override preferred; never
  reword to pass). The orchestrator (never the fixing subagent) runs the
  sweep that grades a fix. Halt: miss-count regression or two no-reduction
  iterations → council.

**Phase 1 done-criterion:** CSM-3/5/6-instrument complete (each item's
done-criterion, raw receipts); gates green **on GPU**; D5 panel pinned and
reproducible; the red list + twenty-failures frozen on disk; the closure
loop at a no-reduction halt or a documented floor; the campaign todos
section synced.

## Phase 2 — extraction & exhaustive (switching plan authorized here)

1. Dial to an even smaller context if the sweep's VRAM needs it (measure,
   don't guess).
2. **CSM-4: D5 exhaustive tier-1 × 3 doors** (~15,400 sentences × 3 doors
   ≈ 51 GPU-h) — batched, checkpointed, resumed in Qwen quiet windows via
   the gpu-handoff chain (`docs/ops/PC_GPU_HANDOFF.md` — now reserved for
   exactly this); miss file empty or every residual miss triaged with a
   documented floor; per-door raw numbers into `reports/csm/GATE.md`.
3. **D6 extraction** (only on red census): events + meaning layer per the
   JJK precedent (contingent extraction — the red set decides).
4. **CSM-8: done-declaration + pilot memo** (pasted raw output + the four
   pilot numbers; JJK baseline diff-empty; halt before P6).

## Doc changes made with this plan (owner: "update and delete all md")

- NEW: this file.
- UPDATED: `CLAUDE.md` (150k Phase-1 mode + ≤2 parallel working subagents +
  GPU-only/>15 s rule; switching plan = Phase 2), `pi.md` §5 (subagent
  policy 150k line; gpu-handoff subsection = Phase 2 only),
  `docs/ops/PC_GPU_HANDOFF.md` (header: reserved for Phase 2 / extraction),
  `docs/ops/QWEN_MODES.md` (150k mode line), `plan/SWITCHPOINT.md`
  (position = 2-phase plan; campaign todos tagged by phase).
- DELETED: `plan/csm_gate4_correction.md` (the gate-4 CPU→CUDA chain was
  superseded by this plan — Phase 1 never uses the switching plan).
- KEPT (records, not rules): all `reports/` council records, the
  gpu-live1/live2/gate3 specs + receipts, `plan/gpu_live2_directive.md`
  (historical directive with its supersession note).