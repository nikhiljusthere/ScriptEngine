# Chairman Verdict — CSM Unit-3 Sweep Device Fork (council 2026-09-09)

**Chairman.** Fresh-context subagent; synthesized from the five advisor responses
(`adv_first-principles.md` … `adv_expansionist.md`) and the five peer reviews
(`review_1.md` … `review_5.md`), every load-bearing claim re-verified on disk by
the chairman (zero-GPU, read-only, all shells < 15 s; one live `GET /health`).

**Mapping caveat (all five reviews agree; the task's `adv_A.md`…`adv_E.md` do not
exist on disk):** A = first-principles · B = contrarian · C = outsider ·
D = executor (self-labeled `adv_D`) · E = expansionist (deployment order by mtime
03:48→03:58). Persona names are the safe reference.

**Chairman's own re-verification (all checked this session):**

| Claim | Verdict | Evidence |
|---|---|---|
| Panel 17,181 sweep + 200 held-out, seed 42, hash `e3d73720…` | ✓ | `reports/csm/panel_csm.json` (python: `panel` 17,181, `held_out` 200, `seed` 42, hash `e3d737205cd0…`) |
| qa ledger 172 rows = 165 HIT / 4 MISS_SPAN / 3 MISS_DOC; 17,009 remain | ✓ | `reports/span-recall/csm/sweep_qa_e3d73720.jsonl` (Counter) |
| Held-out ledger 13/200 | ✓ | `reports/span-recall/csm/sweep_qa_ec15e0d8.jsonl` |
| Census **39/60 green / 21 red** (not 49/60): abilities 6, arc-narrative 8, state-over-time 5, appearance 1, causality 1 | ✓ | `reports/csm/census_dimensions_csm_results.jsonl` (Counter over `verdict`); `work_log.md` 03:43 line says "49/60" but its own per-class greens (2+4+5+10+9+9) sum to 39 — a digit error |
| Doors: roster 11/11, narrative 97/100 (misses: Introduction, Bomb Girl, International Assassins) | ✓ | `reports/csm/census_doors_results_csm.jsonl` (Counter) |
| twenty-failures 20 rows = bank 8 / door 5 / d5 7 | ✓ | `reports/csm/twenty_failures_csm.md` (gate-column counts) |
| R-1..R-5 all engine-class (R-4: per-wiki override preferred first attempt) | ✓ | `reports/csm/red_list_csm.md` "Notes for the §9a executor" |
| 5.4 extraction gate LIVE (structural-dimension red ⇒ extraction proceeds) | ✓ | `reports/csm/door_precheck_csm.md` ("extraction proceeds **only if** the dimension census is red on a structural dimension"; "If the census is red on a structural dimension, extraction proceeds") |
| 168-probe datapoint = **CUDA** `:8000` (pid 103425, device=cuda), single bounded run "well under the 15-min cap"; the 168 CPU rows = dropped "1200-s incident" sidecar; "0.9%" = 161/17,181 completion-weighted | ✓ | `reports/csm/CSM3B_PRESTEP.md` §2–3 — the brief's fact #3 ("CPU ≈ 168 probes/bounded run") is misattributed |
| 150k rules: "no CPU shell command may exceed 15 s"; "the gpu-handoff switching plan … is NOT used in Phase 1"; "Phase 1 never uses the switching plan" | ✓ | `plan/CSM_2PHASE_PLAN.md` L12-13, L19-20, L122 |
| Phase-2 item order: CSM-4 exhaustive tier-1 × 3 doors (~51 GPU-h) **before** D6 extraction ("only on red census") | ✓ | `plan/CSM_2PHASE_PLAN.md` L102-108 |
| Phase-1 done-criterion: "the closure loop at a no-reduction halt or a documented floor" | ✓ | `plan/CSM_2PHASE_PLAN.md` L92-98 |
| Unit-3 spec: batch sweep (pinned panel + 400-probe gate, on CUDA, one-copy ordering) → pre-triaged miss queue → serial engine-fix closure; halt = miss-count regression or two no-reduction iterations → council | ✓ | `reports/master-work/CSM_WAVE2_JOB.md` unit 3 |
| Phase close: four gates → council → commit → coverage → `PHASE_A_COMPLETE` into `reports/master-work/phase_status.txt` (orchestrator polls it to start the 100k switch) | ✓ | `CSM_WAVE2_JOB.md` phase close; `reports/master-work/work_log.md` 02:12 line |
| JJK-100% invariant: four gates re-run after **every engine change**, "on CUDA, one-copy ordering"; at 150k: models load in-process CUDA one-copy, "server down for pytest/eval, up for HTTP gates" | ✓ | `plan/CSM_WAVE2_RESUME.md` §2 (L30), §4 (L75-78) |
| Sweep is HTTP-only: `BASE = "http://127.0.0.1:8000"` (urllib); no in-process 400-probe driver exists; census tools are the only in-process probe precedent | ✓ | `scriptengine/eval/span_recall.py` L44; `tools/census_dimensions.py` docstring ("in-process — the same path the :8000 /context endpoint uses") |
| Dead-door halt (exit 3) checks **merged** counts (prior ledger + this run) | ✓ | `scriptengine/cli.py` L2187-2193 (`if sanity and run["counts"]["HIT"] == 0`); `scriptengine/eval/span_recall.py` L477-493 (counts recomputed from the merged row set) |
| `--sanity N` probes the first N **unprobed** rows (one-way resume) | ✓ | `span_recall.py` L426-428; `cli.py` L2059-2063 |
| 150k state: qwen 150k pid 4348, 5,381 MiB free; `:8000` = CPU service (pid 4510 per log); census one-copy window proven (34 s + 18 s, Qwen alive, footprint unchanged 26,724 MiB); "5.4 extraction gate LIVE" | ✓ (pids per log; service re-checked live: `/health` → `device: cpu` this session) | `work_log.md` L51, L54-55 |
| `phase_status.txt` does not exist yet — PHASE_A_COMPLETE not written, 100k switch not started | ✓ | `ls` (absent) |
| No `recall_*.jsonl` under `reports/span-recall/csm/` — the legacy 400-probe gate has never run on CSM | ✓ | `ls` |
| 62 infobox keys outside engine vocabulary; pre-registered two-lever fork (per-wiki key map `series/csm/overrides.yaml` vs engine `IDENTITY_FIELDS`) | ✓ | `reports/csm/T0_PILOT_CSM.md` L48-50; `scriptengine/retrieve/roster.py:3317` (`_IDENTITY_FIELDS`) |
| Ledger files are git-tracked (recoverable) | ✓ | `git ls-files reports/span-recall/csm/` |

UNVERIFIED: (a) the exact CPU per-probe rate at the current 150k service — two
on-disk figures exist and disagree: ≈1–2 s/probe (`work_log.md` L26-27, 150k-era
CPU-service measurement, "1025 % util") vs 7.1 s/probe (1200/168, the dropped
"1200-s incident" sidecar, `CSM3B_PRESTEP.md` §2). The first gate run measures it;
the LONG flag applies at either figure (400 probes ≈ 7–48 min, both > 300 s).
(b) Live pids 4348/4510 — cited from `work_log.md` L51; this session confirmed
only the service's liveness + `device=cpu` via `/health`, not the pids.

---

## Where the Council Agrees

1. **The device fork is settled: option C, 5/5, independently.** Every advisor
   chose "stay at 150k, no mid-phase dial switch; run the 400-probe gate + the
   frozen miss inputs now; defer the exhaustive panel to Phase B (CSM-4 @ 100k)".
   Each for its own reason — A: the 17,009-row sweep "adds a denominator, not a
   fix class"; B: C "is the only option in the owner's intended order
   (sample → fix one class → targeted grade → exhaustive at Phase 2)"; C: the
   options table rests on assumptions that don't survive the on-disk files; D: "at
   150k it is the plan's own path" (the sweep is an HTTP client; CUDA is not
   reachable without the Phase-2-reserved switch); E: the full panel is Phase B's
   first act, "the staleness *is* its value".
2. **Option A (mid-phase 150k→100k switch) is dominated on two independent axes.**
   Plan fidelity: the switching plan "is NOT used in Phase 1"
   (`plan/CSM_2PHASE_PLAN.md` L19-20, L122) — a mid-phase 100k switch is a plan
   violation, not a workaround (B; C; D). Staleness: the 5.4 extraction gate is
   LIVE (`reports/csm/door_precheck_csm.md`), so a pre-extraction exhaustive panel
   measures a state the extraction will change, and CSM-4 re-sweeps the same doors
   at 100k anyway (the orchestrator's own `PHASE_A_COMPLETE` → 100k switch plan,
   `work_log.md` L51). A also buys 3 reload windows instead of 1 (switch down,
   switch back, then the planned switch at phase close) — D's count, which the
   chairman's verification of the spec update confirms.
3. **The census on record is wrong by 10 rows: it is 39/60 (21 red), not 49/60.**
   Four of five advisors (B, C, D, E) caught it independently; the raw receipt
   parses to 39 MECH_GREEN / 21 MECH_RED (chairman re-verified), and the
   `work_log.md` 03:43 line contradicts its own per-class list. The 5.4
   gate-LIVE verdict survives — it gets *worse* (the brief's reds list omitted the
   appearance + causality reds). A (first-principles) parroted the 49/60 without
   re-deriving (reviews 1 and 2 flag this as its biggest blind spot).
4. **The "17,381-row panel" is a conflation.** The sweep panel is 17,181 rows;
   the 200 held-out rows live in a separate keyed ledger (`sweep_qa_ec15e0d8`,
   13/200 today) (C caught it; D verified; chairman re-verified both files).
5. **Iteration 1's deliverable is a well-specified miss queue + graded re-sweeps —
   not a 17,009-row denominator** (the job spec's own shape,
   `CSM_WAVE2_JOB.md` unit 3). All five agree the frozen inputs
   (twenty-failures 20, red list 5, door-census reds, dimension-census reds)
   already name the fix classes; the full panel "adds breadth only after the
   known classes are closed — and CSM-4 is that closure" (D).

## Where the Council Clashes

1. **The 400-probe gate's mechanism at 150k — the only real fork inside C.**
   - *CPU `:8000`, bounded LONG-flagged run* (D, E, B, and the brief's own option
     B): zero new code, provenance-continuous ledger rows, plan-compliant via the
     documented LONG > 300 s flag-to-A mechanism (`work_log.md` L52). Cost: one
     LONG flag, ~7–48 min of CPU service load (UNVERIFIED rate, see above).
   - *In-process CUDA one-copy window* (C's first choice; review 1's ruling 1):
     literally satisfies the 150k rule "all model/GPU work on CUDA", no LONG flag,
     ~10–15 min, uses the proven 52 s census window pattern. But the driver
     **does not exist** — `span_recall.py` is HTTP-only (chairman-verified) — so
     C's path presupposes new code, and its ledger rows must be proven
     equivalent to the HTTP path before they sit beside the 168-row CUDA ledger
     and CSM-4's sweep. The reviews themselves clash on this: review 1 rules it a
     ~50-line `tools/` driver with **no** council trigger (tooling, not engine),
     while review 3 calls the in-process gate path "infeasible … making one =
     engine change (council + four gates)". The chairman resolves the
     classification below (R1): review 3 mislabels a `tools/` file as an engine
     change, but review 3's underlying point — the path is *asserted, not
     verified* — is the reason it loses iteration 1.
2. **The halt meter.** B pins "miss-count regression / two no-reduction
   iterations" to a **fixed 400-row grading subset** re-probed after each fix
   (without a stable denominator, a deferred panel leaves the halt rule with
   nothing to count). A pins it to a **documented floor**: the structural reds are
   extraction-gated, so declare a floor and the halt rule cannot false-fire. C
   pins nothing in Phase 1 (the meter is the full sweep, folded into the 100k
   switch). Reasonable advisors disagree because the job spec's halt rule
   (CSM_WAVE2_JOB.md unit 3) was written assuming the full panel exists — once the
   panel is deferred, the meter has to be rebuilt, and the three rebuilds
   (fixed subset / floor / defer) are all defensible. Review 2 adds the sharpest
   constraint: a fix that closes its class on a targeted sweep can still
   "no-reduce" on a random 400-subset meter — the meter must connect to the
   per-fix class sweeps.
3. **Where the deferred panel lands in Phase B.** A schedules it *post-extraction*
   ("exhaustive panel completion = Phase B, post-extraction"); E, C, and review 5
   schedule it *pre-extraction* as the plan's own item order
   (`plan/CSM_2PHASE_PLAN.md` L102-108: CSM-4 sweep = item 2, D6 extraction =
   item 3, "only on red census"). E's extra argument: the pre-extraction baseline
   is the **control arm** of the extraction experiment (pre/post hit-rate delta
   = "proof the extraction added comprehension, not churn"), and the R-CSM3B-2
   keyed ledger was built to carry across the dial. This is a plan-reading clash
   with a right answer (the plan's own ordering), not a judgment call.
4. **Unit-3 wall-clock: D's "4 hours" for R-1..R-5 closure.** All five red-list
   items are engine-class (`red_list_csm.md` notes), so each fix = fix + targeted
   re-sweep + four-gate re-run (one-copy ordering) + a §3 council trigger.
   Reviews 1/2/3 independently flag that no response budgets that stack — it,
   not the sweep's 5–10 h, is the real Phase-1 wall-clock driver (chairman's
   estimate: ~40–60 min gate re-run × 5 + up to 5 council cycles ≈ 2.5–5 h
   overhead, before fix authoring). D's timeline is under-budget; D's *plan* is
   sound.

## Blind Spots the Council Caught

(things that emerged only in the peer-review round; all chairman-verified)

1. **The exit-3 dead-door halt is void on any warm ledger (review 4).** The
   sanity floor checks `run["counts"]["HIT"] == 0` over the **merged** row set
   (prior ledger + this run — `cli.py` L2187-2193 + `span_recall.py` L477-493,
   chairman re-verified). The qa ledger already holds 165 HITs, so any resumed qa
   sanity run can never halt: if a serial fix kills a door — the exact scenario
   C's per-fix re-sweeps create — a full 17k sweep against a dead door is
   possible. All five advisors missed it.
2. **B's fixed 400-row halt meter has no on-disk mechanism (review 4).** Resume is
   one-way (`to_run` skips every ledgered row; `span_recall.py` L426-428): a second
   `--sanity 400` probes rows 573–972, not the same 400. Re-probing the same
   subset needs ledger surgery (git-recoverable — the ledgers are tracked,
   chairman-verified) or a `--reprobe` engine flag (council + four gates). B's
   meter is unexecutable as written; the queue-based meter (R2) avoids the
   mechanism entirely.
3. **"The 400-probe standing gate" is ambiguous in the tooling and the options
   text (review 4).** Legacy `--probe 400` (router-mode, no `--door`, appends to
   `recall_verbatim.jsonl` without resume — and has **never run on CSM**: no
   `recall_*.jsonl` exists under `reports/span-recall/csm/`, chairman-verified)
   ≠ the qa-door 400 (`--panel --door qa --sanity 400`, keyed ledger). The job
   spec's "Wave-1 pinned panel + the 400-probe standing gate" pins which one
   iteration 1 delivers; none of the five responses did. The chairman pins it:
   the qa-door 400 on the pinned panel.
4. **The per-fix cost stack was unpriced by every response (reviews 1/2/3).**
   5 engine-class red-list items × [four-gate re-run + council if big] ≈ 2.5–5 h
   of overhead — the dominant unit-3 cost (see Clash 4).
5. **The brief's rate facts are misattributed (B caught; reviews 1/2/3 re-verified;
   chairman re-verified).** The "168 probes ≈ one bounded run" datapoint is
   **CUDA** `:8000` (`CSM3B_PRESTEP.md` §3: pid 103425, `device=cuda`); the only
   CPU rate points are the ≈1–2 s/probe service measurement (`work_log.md`
   L26-27) and the dropped 1200-s incident sidecar (7.1 s/row). And "0.9%" is the
   completion-weighted 161/17,181 — the per-probe miss rate is ≈ 4% (7/168),
   which is what a 400-row gate should yield (~16 new misses).
6. **Phase-B upside the deferral would silently discard (review 5).** (a)
   *Reuse:* the commit-stamped (R-CSM3B-2) Phase-1 rows are a resumable prefix of
   CSM-4's sweep — the Phase-B probe budget shrinks by whatever Phase 1 graded.
   (b) *Gate interplay:* no one scheduled the 34 s one-copy census re-adjudication
   of 5.4 at phase close (reds closed by Phase-1 fixes ⇒ extraction de-scoped,
   per the plan's "only on red census"), nor a pre-registered extraction pass
   test (same 400-gate + red dimension classes green post-extraction; the
   200-row held-out as the out-of-sample leg). (c) *The infobox lever:* the
   62-key gap (`T0_PILOT_CSM.md` L48-50) has a pre-registered **no-council**
   lever (per-wiki key map in `series/csm/overrides.yaml`; engine
   `IDENTITY_FIELDS` widening is the council + four-gates alternative) that
   closes census reds and MISS_DOC rows; even E treats it as Phase-2-only.
7. **The JJK-100% invariant's "gates on CUDA" leg at 150k (review 3).** The
   span-recall 400-probe leg of the four gates is HTTP-only → at 150k it can
   only run on the CPU service (the plan's sole relief: "up for HTTP gates",
   `CSM_WAVE2_RESUME.md` §2 L30). Cited by no advisor; the chairman prices it
   into the gate re-runs (R7 side effects).

## The Recommendation

**Option: C — stay at 150k for all of section-9a iteration 1; no mid-phase dial
switch. Variant: C-deferred-panel — the 400-probe gate + the frozen miss queue now
on the CPU `:8000` service; the exhaustive panel folded into the *planned*
`PHASE_A_COMPLETE` → 100k switch as Phase B's first act, pre-extraction; the halt
meter pinned to the frozen miss queue with a documented floor over the
extraction-gated reds.**

**Why C (the chairman's synthesis of the unanimous core):** plan fidelity — the
switching plan "is NOT used in Phase 1" (`plan/CSM_2PHASE_PLAN.md` L19-20, L122),
so option A is a plan violation, not a workaround; staleness — the 5.4 gate is
LIVE (21 structural-dimension reds, `reports/csm/census_dimensions_csm_results.jsonl`
+ `door_precheck_csm.md`), so a pre-extraction 17k sweep measures a state the
extraction changes, and CSM-4 re-sweeps the same doors at 100k anyway
(`CSM_WAVE2_JOB.md` phase close: the orchestrator's `PHASE_A_COMPLETE` poll
"starts the 100k switch into Phase B" — `work_log.md` L51); switch count — A buys
3 reload windows, C buys exactly 1 (the planned one); and B is strictly worse —
17,009 rows at the on-disk CPU rates (≈1–2 s/probe `work_log.md` L26-27; 7.1
s/row 1200-s incident `CSM3B_PRESTEP.md` §2) ≈ 7.6–33.7 h of service load behind
~100–135 A-flagged bounded runs, for the same stale artifact.

**Rulings attached to C (what makes iteration 1 executable and halt-capable):**

- **R1 — the 400-probe gate mechanism at 150k = one bounded CPU `:8000` run,
  LONG-flagged to A.** Not a 100k switch (Phase-1-forbidden). Not the in-process
  one-copy 400-probe driver: it does not exist (`span_recall.py` L44 is
  HTTP-only — chairman-verified; the census tools are the only in-process
  precedent and a different question shape), and a new probe path must prove
  equivalence to the HTTP `/context` path before its ledger rows sit beside the
  168-row `e3d73720` ledger and CSM-4's sweep. The CPU service is the
  provenance-continuous, zero-new-code path; the 150k plan's own relief for long
  probe runs is the LONG > 300 s flag-to-A (`work_log.md` L52; the 400-gate is
  > 300 s at either on-disk CPU rate). The in-process driver is **pre-registered
  as the upgrade path**: a ~50-line `tools/` file (tooling, *not*
  `scriptengine/` — no council trigger; the chairman rejects review 3's
  "engine change" label), scheduled only if A flags the CPU path as
  unacceptably slow — and gated on a one-line equivalence note (the driver calls
  the same fusion entrypoint the `/context` endpoint uses, so rows are
  comparable by construction; record the binding diff in the receipt).
- **R2 — the halt meter = the fixed, frozen, pre-triaged miss queue, not the
  moving panel and not a re-probed 400-subset** (the 400-subset is
  inexpressible in the current CLI — one-way resume, review 4; the queue is
  expressible: class-targeted **subset-panel files**, each with its own
  recomputed hash + keyed ledger — the R-CSM3B-2 keying and the
  "interleaved runs coexist" design (`CSM3B_PRESTEP.md` §5) exist exactly for
  this; no ledger surgery, no engine flag). The queue = twenty-failures 20
  (`bank 8 / door 5 / d5 7`) + red-list 5 (R-1..R-5) + census reds 21 (frozen
  from the **raw** 39/60 file — not the work_log's 49/60) + narrative-door misses
  3 (Introduction, Bomb Girl, International Assassins) + the baseline 400-gate's
  own new misses (~16 at the per-probe 4%). Every row is pre-registered with a
  fix class (R-1..R-5 or a new R-6+) and a floor/fixable ruling (review 2's
  "row→class triage schema"). A class is "closed" only when its own class-targeted
  re-sweep turns green; "two no-reduction iterations" is counted over the
  queue's miss count between iterations; the 400-gate's per-window new-miss rate
  is a trend check only, never a halt trigger.
- **R3 — documented floor over the extraction-gated reds (A's concept, full
  21-red scope per reviews 1/2).** The 21 census reds sit on the extraction
  track: `reports/csm/dimension_map_csm.md` L51-52 — "red is the CSM trigger for
  the interval-facts / extraction build" — and the 5.4 gate is LIVE. They are
  triaged and attempted in the queue (what R-1..R-5 + the infobox lever close
  gets closed), but their *structural* closure is Phase 2's extraction build.
  Declare them a **Phase-1 documented floor** — the plan's own Phase-1
  done-criterion is "the closure loop at a no-reduction halt or a documented
  floor" (`plan/CSM_2PHASE_PLAN.md` L92-98). The halt rule counts only
  Phase-1-fixable classes; otherwise iteration 1 false-halts to council on reds
  it structurally cannot close (the wall-clock the campaign cannot afford).
- **R4 — the exhaustive panel lands in Phase B as the *first act, pre-extraction*
  (E + C + review 5; A's post-extraction placement inverts the plan).** Plan item
  order: CSM-4 "D5 exhaustive tier-1 × 3 doors" (item 2) precedes "D6
  extraction (only on red census)" (item 3) — `plan/CSM_2PHASE_PLAN.md`
  L102-108. The pre-extraction full-panel baseline (17,181 pinned qa, 17,009
  remaining; the 200-row held-out ledger at 13/200; roster + narrative
  exhaustive doors within CSM-4's × 3 doors, ~51 GPU-h) is the **control arm**
  of the extraction experiment, and the commit-stamped Phase-1 rows resume
  forward — CSM-4's probe budget shrinks by what Phase 1 graded (review 5).
  One switch total: the planned `PHASE_A_COMPLETE` → 100k switch
  (`phase_status.txt` does not exist yet — chairman-verified).
- **R5 — dead-door halt ruling (review 4).** Because exit 3 checks merged
  counts, the per-door sanity floor is dead on the warm qa ledger (165 HITs).
  Ruling: **any post-fix class re-sweep must show ≥ 1 HIT in its own new rows or
  halt to council** — the sanity floor's intent (a dead door must not burn a
  sweep) applied to the class sweeps. The one-line engine fix (check
  this-run counts, not merged) is deferred: it is an engine change (council +
  four gates) and the ruling gives equivalent protection without code.
- **R6 — phase close: re-adjudicate 5.4 + pre-register the extraction pass test
  (review 5).** A 34 s one-copy census re-run (the proven window, `work_log.md`
  L55) re-adjudicates the 5.4 gate class-by-class: a red class closed by a
  Phase-1 fix de-scopes the extraction per the plan's "only on red census".
  Pre-register the extraction's acceptance: the same 400-gate + the red
  dimension classes turn green post-extraction; the 200-row held-out is the
  out-of-sample leg.
- **R7 — the infobox-key lever is a Phase-1 candidate, not the device path
  (review 5).** The 62-key gap's per-wiki key map (`series/csm/overrides.yaml`)
  is the pre-registered **no-council** lever (`T0_PILOT_CSM.md` L48-50; engine
  `IDENTITY_FIELDS` widening *is* council + four gates). It closes census reds
  and MISS_DOC rows and shrinks D6's input surface. Schedule it as a Phase-1 fix
  candidate **after a small override-support check** (verify
  `series/csm/overrides.yaml` actually carries a key-map field — review 5's
  caveat: the two-lever fork is a pre-registration, not yet a built hook). The
  8-verb set-scope decision (`reports/csm/dimension_map_csm.md` L13-14: 76% of
  the Summary slice not held by the 9-verb set) is the sibling ruling for the
  same breath.

**Exact first executable step (B, the orchestrator — it "runs the sweep that
grades a fix", `CSM_WAVE2_JOB.md` unit 3):**

1. **A approval:** the LONG flag for the baseline gate run (the `work_log.md`
   L52 mechanism; > 300 s at either on-disk CPU rate).
2. **Launch the baseline 400-probe standing gate** (qa-door 400 on the pinned
   panel — R1/R2 disambiguation), one bounded run against the live CPU `:8000`
   service (no ESC stop; service stays up):

   ```
   scriptengine/.venv/bin/python -m scriptengine.cli span-recall \
     --series csm --panel reports/csm/panel_csm.json --door qa --sanity 400
   ```

   Probes the first 400 *unprobed* panel rows (rows 173–572 — `--sanity N` is
   "first N unprobed", `cli.py` L2059-2063; D's stated `--sanity 472` step would
   have probed 472 rows, not its stated 300 — review 4's correction), resumes
   the 172-row `e3d73720` ledger, ≈16 new misses expected, and records the
   first on-disk CPU rate measurement at the 150k service (resolving the
   UNVERIFIED rate above).
3. **In the same window (model-free, zero GPU): write the pre-triaged
   miss-queue file** (e.g. `reports/csm/miss_queue_csm_iter1.jsonl`) from the
   five frozen sources — `twenty_failures_csm.md` (20 rows, never edited per its
   freeze note), `red_list_csm.md` (R-1..R-5, each with fix class + file),
   `census_dimensions_csm_results.jsonl` (the 21 reds, **frozen from the raw
   39/60 file**), `census_doors_results_csm.jsonl` (3 narrative misses), the
   gate's new misses folded in at completion — every row stamped with fix class
   + floor/fixable ruling (R2/R3).

**Switch / escalation side effects (ESC lines, switchpoint, A approvals):**

- **ESC:** only the one-copy census windows (ESC stop `:8000` →
  `census_dimensions` 34 s + `census_doors` 18 s → ESC restart `:8000` CPU,
  30–60 s; the proven pattern `work_log.md` L54-55, 03:38–03:43, Qwen alive,
  footprint unchanged) — for the 21-red floor baseline and each post-fix
  re-adjudication. **No** `:8000` stop for the 400-gate or the class re-sweeps
  (they probe the live CPU service).
- **Switchpoint:** none in iteration 1 (the gpu-handoff switchpoint artifact is
  reserved for Phase 2, `plan/CSM_2PHASE_PLAN.md` L19-20). The single dial switch
  of the campaign remains the planned phase-close 150k→100k, triggered by the
  orchestrator's `PHASE_A_COMPLETE` poll (`work_log.md` L51); `phase_status.txt`
  does not exist yet (chairman-verified), so nothing has started.
- **A approvals / council triggers:** one LONG flag (the gate run). Per engine
  fix: the §3 council trigger + the JJK-100% four-gate re-run
  (`plan/CSM_WAVE2_RESUME.md` §4 — "after **every engine change** re-run all
  four (on CUDA, one-copy ordering)"). At 150k the gate re-run = pytest 1,254 +
  eval jjk 31/31 + canon opm 236/236 loaded in-process CUDA one-copy (server
  down for pytest/eval, up for HTTP gates — RESUME §2 L30) + span-recall 48,572
  offline (model-free) + the 400-probe leg on the CPU service (HTTP-only — the
  sole 150k relief, review 3) ≈ 40–60 min per re-run. × 5 fixes + up to 5
  council cycles ≈ 2.5–5 h of overhead before fix authoring — this, not the
  sweep, is unit 3's wall-clock driver (reviews 1/2/3; D's "4 hours" is
  under-budget). R-4's per-wiki-override attempt (`red_list_csm.md` notes) may
  close without a council; if the override cannot scope it, the engine fallback
  triggers.
- **JJK-100% invariant:** CSM work lands in CSM-centric files only; the four
  gates re-baselined 2026-09-08 15:22 stand as the bar
  (`plan/CSM_WAVE2_RESUME.md` L75-84).

**Condition under which the chairman changes his mind:** if the baseline
400-gate + frozen queue comes back **thin/empty** (twenty-failures all HIT, no
new miss class among the gate's misses, every red floor), iteration 1 collapses
to the plan's own **documented-floor close** ("the closure loop at a no-reduction
halt or a documented floor", `plan/CSM_2PHASE_PLAN.md` L92-98): no Phase-1 fix
classes, the 400-gate stands as the gate, and the full panel + roster/narrative
doors ride the planned 100k switch as Phase B's first act (pre-extraction
control arm + CSM-4). The *device path* does not change in that case — 150k
until phase close, no mid-phase switch (it remains plan-forbidden; the only
100k window is the planned one); what changes is what Phase 1 *does* (queue
closure vs. floor declaration). Secondary scope condition: if the phase-close
5.4 re-adjudication (R6) turns all 21 reds green, the extraction de-scopes per
the plan's "only on red census" and Phase B = sweep + done-declaration only —
the pre/post pairing collapses and the panel's value is a plain hit rate; still
one switch, still pre-extraction.

## The One Thing to Do First

**Launch the baseline 400-probe standing gate** —
`span-recall --series csm --panel reports/csm/panel_csm.json --door qa --sanity 400`
— as one bounded CPU `:8000` run behind a single A LONG-flag (R1), and in the
same model-free window **write the pre-triaged miss-queue file** from the five
frozen sources (twenty-failures 20 + red-list 5 + census reds 21 frozen from the
raw 39/60 file — *not* the work_log's 49/60 — + 3 narrative misses + the gate's
new misses), every row stamped with fix class + floor/fixable ruling (R2/R3).
No switch, no new code, no council trigger — one A LONG-approval, at 150k.