# CSM 100% — full session audit (2026-09-09)

Reconstructed from every session transcript in
`~/.pi/agent/sessions/--home-goblin-ScriptEngine--/` (09-07 → 09-09), cross-checked
against the on-disk records (`reports/csm/`, `plan/`, git log, `COUNCIL_HISTORY.md`).
If a fact disagrees with a raw receipt, the receipt wins.

## 1. What the CSM 100% plan is

The Chainsaw Man corpus run to the same bar JJK reached (D6 comprehension): the
corpus *understands* everything about a character — every line/fact/prose/event
means something, is structured, is placed on the timeline, and is reachable
through all three doors (qa + roster + narrative). Defined by
`reports/csm/COUNCIL_csm-campaign.md` (2026-09-07, owner campaign council) and
executed per `plan/CSM_2PHASE_PLAN.md` (owner-directed 2026-09-08):

- **Campaign items** (`plan/SWITCHPOINT.md` "Campaign todos"): 0 Wave-0
  tier-0 reachability · 1 CSM-1 seed-bank inventory + revid stamps · 2 CSM-2
  page-type classification + scoreboard generalization · 3 CSM-3 D5 measurement
  infrastructure · 4 CSM-4 D5 exhaustive tier-1 × 3 doors · 5 CSM-5 remainder
  (fixtures / gold-sliced / red list / door pre-check / twenty-failures) ·
  6 CSM-6 instrument (census tools, dimension map, eight-verb sample, frozen
  sets, T0 pilot, cross-page census) · 7 §9a closure loop · 8 CSM-8
  done-declaration + pilot memo.
- **Phase 1 (fixing process)**: 150k Qwen dial; **2 parallel working
  subagents per wave** (deploy 2 → access both results on disk → next 2, never
  queue); **all model/GPU work on CUDA, no CPU shell >15 s**; the
  gpu-handoff switching plan is *not* used; councils one agent at a time.
- **Phase 2 (extraction & exhaustive)**: smaller dial (100k or less),
  gpu-handoff chain authorized, CSM-4 (~15,400 sentences × 3 doors ≈ 51 GPU-h),
  D6 extraction only if the dimension census goes red, CSM-8 done-declaration.
  Halt before P6.
- Standing invariants (owner 2026-09-09): **council trigger** — a sequential
  11-member council assesses correctness after every CSM phase, at every big
  decision, and at every big engine change (supersedes "every 2–3 todos");
  **JJK-100% invariant** — the four standing gates (pytest / eval jjk /
  span-recall jjk 48,572 + 400-probe / canon opm) re-run after every engine
  change, CSM work lands in CSM-centric files only, the JJK baseline is
  untouched.

## 2. How much is done (per campaign item)

| Item | State | Receipt |
|---|---|---|
| 0 · Wave-0 tier-0 reachability | **done** | 439 → 0 unreachable, span-recall csm rc=0 (2026-09-07) |
| 1 · CSM-1 seed-bank inventory + revid | **done** | `064093e`; `reports/csm/CSM1_INVENTORY.md` (39 questions + 1 retired, 11 relation sets, 20 declared rosters) |
| 2 · CSM-2 page types + scoreboard | **done** | `42aa296`; `reports/csm/CSM2_SCOREBOARD.md` (13 store types: 5 in-scope, 7 excluded-in-writing; JJK output byte-identical) |
| Gates re-baseline ×2 | **done** | `GATE_REBASELINE.md` (1,242) + `GATE_REBASELINE_2.md` (pytest 1,249 / eval 31/31 / span-recall 48,572 + 390/400 / canon 79.0%, 09-08 15:22–15:26 CUDA) |
| 3 · CSM-3 D5 measurement infra | **done** | `f93d396`: pinned hashed panel (hash e3d73720, 17,181 + 200 held-out), (title, sentence) resume, full-denominator hit_rate, three doors + dead-door halt, tier-0 rename `chunk-containment` (alias kept), 1,253 tests |
| 3b · CSM-3b post-council | **done, ratified** | `bc73795` + `78b5cf3`; `COUNCIL_csm-3b` (ledger #20, 7 rulings); roster-door fix (served_text flattening, 0 → 31/88 live), F1 ledger trap fixed in the Wave-2 pre-step (`6537398`, graded PASS 09-08 19:45) |
| 5 · CSM-5 remainder | **done** (as Wave-2 unit 2) | commit `0e0e19e`; `reports/csm/CSM5_REMAINDER.md`: 5.3 fixtures (`test_csm_fixtures.py`, 3 pass + 2 xfail — G-CSM-1 debt states the xfail), 5.5 generator-sliced gold + held-out declaration + pre-registered red list (no LLM judge), 5.4 door pre-check → extraction gate **LIVE** (structural red), §13 awareness line, twenty-failures frozen set (named author, executed never edited) |
| 6 · CSM-6 instrument (half) | **done** (as Wave-2 unit 1) | commit `0e0e19e`; `reports/csm/CSM6_INSTRUMENT.md`: `census_dimensions.py` / `placement_audit.py` / `census_doors.py` parameterized `--series` (JJK byte-identical proof), CSM §12 dimension map, eight-verb 100-sentence sample (reading-only), frozen seeded+revid-stamped census sets (generated fresh from CSM), T0 pilot (843 questions via `page_gen.py`), cross-page fact census (SQL, <15 s). CUDA census window (one-copy, Qwen untouched): dimensions **49/60 mech-green** (council later corrected the record to **39/60 → 21 red**: arc-narrative 2/10, abilities 4/10, state-over-time 5/10) · doors roster 11/11, narrative 97/100 |
| 7 · §9a closure loop, iteration 1 | **in progress** | R-1 class **closed** (`b84445f` + `aef6707`, D18); R-2 (qa-passage leg) + R-3 (roster scoping) drafted by 2 workers, counseled (R-2 AMEND-3 / R-3 AMEND-4+records), amendments applied, gates 1–2 + gate-3 offline green — **gate-3 400-probe + gate-4 + class re-sweeps + selective commit still pending** (9-file package on disk, uncommitted); R-5 class plan drafted; R-6 (`subject_aliases`) + R-7 (`identity_fields`) recorded as engine hooks. Miss queue = the halt meter (55 rows: 33 fixable / 22 floor → 58 rows after R-1 stamps; 3 fixable rows closed by R-1) |
| 4 · CSM-4 exhaustive tier-1 × 3 doors | **not started** | Phase 2; council R4: the full 17,181-row panel lands in Phase B as first act, PRE-extraction (the control arm) |
| 8 · CSM-8 done-declaration + pilot memo | **not started** | Phase 2 |

**Score: campaign items 0, 1, 2, 3, 3b, 5, 6-instrument done (7 of 9);
item 7 ~40 % (1 of 5 fix classes closed, 2 of 5 gated-but-uncommitted, 1
planned); items 4 and 8 (Phase 2) untouched.**

## 3. Session-by-session timeline (all times local IST)

### 2026-09-07 — campaign kickoff (session `01a07cab`, JJK-closure day)
Main transcript was trashed by the owner; subagent runs + git log + council
records survive.
- JJK campaign closed (D11). CSM campaign council convened —
  `COUNCIL_csm-campaign.md` (5 advisors, 2 expired → n=3 + a recovered-advisors
  supplement): the question bank is not a D1–D6 component; 5.5 is *no* LLM
  judge; 5.6 must precede generation; all four §2a measurement traps live in
  `span_recall.py`; Wave-0's rc=0 closed tier-0 only (D5 is tier-1); 5.4 is
  door-first, extraction only on red; item 3 ≡ 5.1 (one artifact).
- CSM-1 (seed-bank inventory + revid stamps, `tools/csm/stamp_revids.py`) and
  CSM-2 (page-type classification + scoreboard generalization) executed;
  Wave-0 tier-0 sweep: 439 → 0 unreachable lines.

### 2026-09-08, 09:38–17:48 — session `01a07f33` (supervisor session)
- **PC-control build-out**: `--vision` added to the ninfer Qwen launch;
  tmux + xdotool + scrot vision-verified terminal control (open/close
  terminals, `/resume` session organization, typing into a fresh pi);
  `plan/PLAN_master_work.md` (A=Control + B=Work) reviewed by council
  `0204d37f` (11/11); `tools/master-work/gpu-handoff.sh` (tier-1/tier-2
  Qwen-switch chains) + `gpu-live1` first live run (100k+CUDA gate baseline
  report).
- **`COUNCIL_csm-1b-2`** (CSM-3 addendum): G-CSM-2 = the dead qa door;
  G-CSM-4 (relations door) ruled OUT of CSM-3's three doors (CSM-7's job);
  gate re-baseline must precede CSM-3.
- **gpu-gate3 chain**: 262k→100k, side session C on CUDA runs the four
  standing gates → `GATE_REBASELINE_2.md` (15:22–15:26), baselines
  re-anchored 1,242 → 1,249.
- **CSM-3 landed** (`f93d396`) + **CSM-3b** (`bc73795`, `COUNCIL_csm-3` 7
  rulings + `COUNCIL_csm-3b` ratification).
- **16:47 owner directive — the two-phase split**: Phase 1 = the fixing
  process at 150k with 2-parallel subagent waves, GPU-only, no CPU shell
  >15 s; Phase 2 = extraction/exhaustive at an even smaller dial with the
  switching plan authorized → `plan/CSM_2PHASE_PLAN.md` (`42eb017`), docs
  updated, `csm_gate4_correction.md` deleted.
- **llm-council rule**: deploy one agent at a time (262k KV-pool contention);
  CPU-fallback clause retired (jobs never default to CPU).
- **17:37 `CSM_CONTROL_PLAN.md` + `csm-control.sh`** (commit `1523030`; the 17:55 `4d576d1` was the campaign-todos sync):
  Terminal A checks *every* shell Terminal B runs (5-s process-tree poll,
  `shell_log.jsonl` with durations, auto-kill of provably-CPU model work
  >15 s, LONG >300 s flagged, MODEL_DOWN backstop). Root-caused the 1200-s
  "stuck" incident: an exhaustive 17k-row panel sweep against a CPU :8000.
- Phase-1 setup: 150k dial, :8000 on CPU, fresh CSM session in tmux
  (`41c91f4`).

### 2026-09-08, 16:53 → 21:49 — sessions `01a080c1` / `01a080ef` / `01a080ec`
- `01a080c1` (fresh 150k Phase-1 executor): CSM-3b exit-code recheck; killed
  when the tmux run died (state on disk).
- `01a080ec` = **Control Terminal A** (fresh 100k): launched B + the machine
  monitor; killed two old-rule false positives (pytest on CPU, 16 s/20 s);
  worker-2 stall (frozen fork 25+ min) → typed nudge → B self-recovered with a
  fresh single run; **all four standing gates green** (pytest 1,254 /
  eval 31/31 / span-recall 48,572 + 390/400 / canon rc=0, `fd8bdd0`); power
  blip ~19:28 → 20-second checkpoint; `terminal-pilot` skill saved (commit +
  TOJI post-mortem fixes); Qwen restored to 262k.
- `01a080ef` = **Terminal B** (worker): closed CSM-3b (`CSM3B_GATES.md` @
  `78b5cf3`); council `COUNCIL_csm-3b` ratified close (ledger #20); **Wave-2
  pre-step graded PASS 19:45** (`6537398`): F1 ledger trap fixed (sweep
  ledgers re-keyed by panel hash + device/commit stamps + exit-2 tamper
  refusal; 168 CPU-provenance rows dropped and re-probed on CUDA, 161 HIT /
  168) + roster-door live probe (31/88 members, 16,231 chars vs 0 pre-fix);
  Wave 2 deployed as workflow `2ceef179` (two zero-GPU workers:
  csm6-instrument + csm5-remainder).

### 2026-09-08 21:41 → 09-09 12:15 — session `01a081ca` (the "TOJI" session)
Owner-directed intermission, then the CSM resume:
- **Out-of-campaign**: installed the `humanscope` skill (replaced the old
  voice skill, made default); wrote the **Toji Fushiguro script** (D14,
  ~45-min/6,037 words, 104 tags, verify-clean, transcript-sourced citations
  incl. 21 `[E n mm:ss]` timestamps + JJK0 movie check); **JJK anime
  transcript import** (D12/D13): yakuaru closed captions →
  `scriptengine/transcripts.py` + `series/jjk/transcripts.db`, **16,226
  Qdrant points** embedded (15,411 lines + 815 signs, bge-large, CUDA,
  one-copy window under A/B supervision — the bay's first live job), idempotent
  re-run, smoke-verified; **Toji/Gojo script conventions made permanent**
  (D15: `ANNOTATION_RULES` — timestamps, `[covers X-Y]` every 3 passages,
  words-only clean companion, cite-the-thing-not-the-arc; `writer.py`
  `ensure_covers_blocks` backstop; 6 new tests) and (D16) the **essence
  contract** (`ESSENCE_RULES` in `rules.py`: opening / pacing / resolution /
  bad things — owner supplies the shape, the engine serves the facts).
- Built the **`ab-bay` + `terminal-pilot` skills** (`~/.pi/agent/skills/`,
  `pilot.sh`) and generalized `csm-control.sh` (tmux-aware hints, logdir arg).
- **01:45 IST owner CSM-resume directive** → **D17**: `plan/CSM_WAVE2_RESUME.md`
  (progress review with receipts + deployment spec) +
  `reports/master-work/CSM_WAVE2_JOB.md` (units + bootstrap type-lines); the
  **council trigger** and the **JJK-100% invariant** written into
  `plan/flow.md` + `CLAUDE.md`; session restarted; 150k dial; A/B bay booted
  02:02 IST (A = `01a082b6`, B = `01a082b7`).

### 2026-09-09, 02:02 → ~12:19 — sessions `01a082b6` (A) + `01a082b7` (B), the A/B bay
**Units 1+2 — the Wave-2 pair (commit `0e0e19e`, 03:43 IST):** see item 5/6
rows above. Plus: D4 open-50 + twenty-failures frozen sets (named authors);
coverage regenerated (jjk 893/987, remainder 0); the census window run
one-copy CUDA with Qwen 150k untouched (26,724 MiB footprint invariant).

**Unit 3 — the §9a closure loop, iteration 1:**
1. **Device-path fork → council** `COUNCIL_unit3_sweep` (11 sequential,
   ledger #21): **C-deferred-panel** — stay 150k; the 400-probe gate runs on
   the live CPU :8000 (bounded, LONG-flagged); the exhaustive 17,181-row
   panel defers to Phase B (pre-extraction control arm); the 21 census reds
   are the Phase-1 documented floor; halt meter = the frozen pre-triaged miss
   queue. Forced record corrections: census 39/60 (not 49/60), the 168-probe
   datapoint is CUDA (not CPU), panel = 17,181 + 200.
2. **400-gate ran** (`f81a1af`): ledger `sweep_qa_e3d73720.jsonl` 172 → 572
   rows (559 HIT / 5 MISS_DOC / 8 MISS_SPAN), ~8.5 s/probe CPU@150k, ~57 min
   (→ ~39 h for the full panel — re-confirming the deferral).
3. **Miss queue frozen** (`miss_queue_csm_iter1.jsonl`, 55 rows: 33 fixable /
   22 floor, every row stamped fix-class + floor/fixable) = the halt meter.
4. **Wave-1 serial fix**: R-1 router count-rule draft (`router.py` +22/−1,
   11-test CSM pin file) + the no-council override package (closed 0 rows —
   all 13 d5 line-misses verified retrieval-side R-2; R-6/R-7 engine hooks
   recorded, overrides.yaml untouched).
5. **Council R-1** (ledger #22): **AMEND** — ship the hunk exactly as
   drafted; 3 blast-radius test pins (csm-Tokyo / opm-Blizzard opm-set-16 /
   onepiece-Marines, 11 → 14 tests); gate-1 expectation 1,283; class boundary
   = `\bhow many\b` only; gate-4 pre-registration (opm-set-16-confined canon
   drop = documented delta, else revert); 3 queue stamp rows (55 → 58);
   red-list addendum.
6. **Four gates green** (one-copy 150k ordering: :8000 stop → pytest CUDA →
   eval → :8000 CPU → span-recall + 400-probe → canon opm): pytest 1,281+2xp
   = 1,283 · eval jjk 31/31 · span-recall 48,572/48,572 + 390/400 (97.5 %,
   exact baseline) · canon opm 236/236 / 79.0 % (exact baseline; opm-set-16
   absorbed via the "members" alias — pre-registered latent branch, tripwires
   stay live). **R-1 class re-sweep green** (set-14 5/5, set-15 4/4, stamped
   rows pinned, zero new misses) → **csm-set-14 / set-15 / red-R-1 CLOSED**
   (33 fixable → 30). Committed `b84445f` + `aef6707` (**D18**).
7. **Wave 2 (run `d9da8d8e`, 2 workers, disjoint writes)**:
   - **R-2 qa-passage leg** (G-CSM-2): `hybrid.py` rerank-veto re-admission
     (`_query_covered` 0.8 coverage guard, tail-fill, beam-bounded) +
     `facts.py` subject-floor level IN (0,2) lead card + 6 new tests.
   - **R-3 roster scoping** (G-CSM-3): `roster.py` +127/−9 three per-wiki
     opt-in knobs (`closed_members` / `ability_sections_umbrella` /
     `ability_row_sections`) + `series/csm/overrides.yaml` +29 + 13 tests.
   Both workers finished code + tests, then hit the 60-min timeout in their
   final verification loops (r2 receipt lost; B authored the work record
   `receipts/iter1_r2_passageleg.md`, graded not edited). B independently
   re-ran everything: R-3 pre/post table exact (set-17 14→7, set-08 14
   invariant, set-01 7→5, char-02 18→16, char-04 7 invariant); R-2 batteries
   74+2xp / 159 green.
8. **Combined section-3 council R-2+R-3** (run `fa01e720`, 11 sequential,
   zero-GPU, ~2 h): R-2 = **AMEND (3)**, R-3 = **AMEND (4 + records
   package)**. Amendments applied model-free: the hybrid splice uncapped
   splice (L > top_k negative-slice no-op, L == top_k full-swap eviction —
   capped at top_k−1, order-preserving, no rrf re-sort), a dangling
   docstring, a CR-only hunk restored to HEAD byte state, two roster
   empty-intersection gates, the red-list ID collision (queue R-3 ≡ red-list
   R-4 ≡ G-CSM-3), sweep-scope corrections (csmdoor-01 + csm-set-14/15
   invariants). Pre-gate pin: 1,305 collect (1,303 + 2 xpassed).
9. **Shared four-gate re-run**: GATE 1 GREEN (1,303+2xp, 192.7 s CUDA,
   exactly the chairman's pin), GATE 2 GREEN (31/31), GATE 3 offline GREEN
   (48,572/48,572) + 400-probe launched (CPU service, LONG-flagged, ~57–77
   min); GATE 4 (canon opm + opm-set-16 pre-registration) queued behind it.
10. **Gate-3 incident + recovery**: B's ESC carried a stale :8000 pid; A
    executed the stop, killing the service the probe depended on → ledger
    block 3,655–4,054 all-ERROR (connection-refused), declared **void as a
    gate number** (window-stamp-keyed; audit artifact only). A restarted
    :8000 (CPU pid 159542) and relaunched the probe (pid 159612, same
    deterministic seed-7 400 rows) → valid window = rows 4,055–4,454.
11. **R-3 class re-sweep Part B GREEN** (model-free, run while the probe
    flowed): 15/15 rows + invariants, csmdoor-01's 31/88 floor HELD at the
    serving layer, R-5 meter 3/3 own-new-row HITs satisfied, zero new misses
    on stamped rows.
12. **Owner override (12:3x IST) — the GPU standing rule**: every model shell
    must run on GPU; any provably-CPU model work terminated immediately
    (no 15-s grace). A flipped :8000 to the **CUDA service** (verified:
    embedder+reranker ~3.2 GB fits the 150k headroom, Qwen alive before/after).
    The in-flight probe was voided at ledger 4,315 (window incomplete). B
    worked the model-free queue in the owner's order:
    (1) the **R-2/R-3 selective-commit package staged** (2-commit pattern, 13
    named files + records + council package + COUNCIL_HISTORY #23 + D19,
    commit messages drafted — *not committed until the CUDA gate legs are
    green*), (2) the **R-5 class plan draft** (root cause: relationship
    phrasing routes to the roster door while the relations channel — 11,261
    `facts.db` edges — is only a qa-bundle side channel; fix shape: a 4th
    router mode `relations`, series-agnostic, checked before the enumeration
    branch + a dedicated budgeted bundle builder); items (3) unit-4
    phase-close prep and (4) the R-2 Part-A qa-leg panel (rows + hash +
    ledger, one-CLI-call run once the CUDA :8000 is up) were
    **in-progress / queued when the bay ended, not completed** (B's last
    turn: "Item 2 done. Re-reading the Unit 4 spec for the phase-close
    prep").
13. The owner closed B (it looked like a shell loop) and rebooted the machine
    (owner's `ninfer-start`, 262k). A was told to relaunch A+B at 100k; the
    bay ended there (06:49Z = 12:19 IST).

## 4. In what ways we worked (the mechanisms)

1. **The A/B terminal bay** — A = GPU supervisor whose *eyes* are the machine
   monitor (`tools/master-work/csm-control.sh`: 5-s process-tree poll of B's
   pi tree; every shell → `shell_log.jsonl` with duration; auto-kill of
   provably-CPU model work >15 s; LONG >300 s flagged, not killed;
   MODEL_DOWN backstop → `ninfer_restart.sh`). A's LLM half judges only from
   the jsonl files every ~3 min and commits after each intervention batch;
   typed hints are probed via a file side-channel (never assumed landed).
   B = the worker, executes the job spec in units, checkpoints every unit to
   `work_log.md`, escalates through `state.md`. Coordinated on disk
   (`decisions.md`, `interventions.jsonl`), never on memory.
2. **2-parallel subagent waves** — deploy exactly 2 → wait for both results
   on disk → orchestrator verifies raw receipts → deploy the next 2. Never
   queue, never 3+. Wave cap enforced against the 150k KV pool (2 consumers =
   the ceiling).
3. **Councils at decision boundaries** — sequential 11 members (5 advisors →
   5 anonymized peer reviewers → chairman), zero-GPU, fresh context, every
   load-bearing claim re-verified against code/facts.db before recording;
   written to `reports/csm/COUNCIL_*.md` + the `COUNCIL_HISTORY.md` ledger
   and committed with the work they reviewed. **7 CSM councils run**:
   csm-campaign (09-07), csm-1b-2, csm-3, csm-3b (#20), unit3_sweep (#21),
   R-1 router (#22), R-2+R-3 combined (#23 pending commit).
4. **JJK-100% invariant** — after every engine change the four standing gates
   re-run in the one-copy 150k ordering; every run was **baseline-exact**
   (pytest 1,283 → 1,303+2xp; eval 31/31; span-recall 48,572 + 390/400;
   canon 236/236 · 79.0 %) — zero JJK regression across the whole campaign.
   CSM work touched only CSM-centric files (engine hunks are
   series-parameterized / series-agnostic by construction; per-wiki knobs
   live in `series/csm/overrides.yaml`).
5. **GPU discipline** — 150k Phase-1 dial (5.4 GB headroom); one-copy rule
   (in-process embedder+reranker and the :8000 service never co-load;
   :8000 stopped for in-process pytest/eval, restarted after, device
   health-checked before any probe); Qwen's 26,724 MiB footprint verified
   invariant after every window. Owner's 12:3x rule escalated this to
   *all* model work on GPU (CPU shell >15 s = auto-kill, no grace).
6. **Disk is the tiebreaker** — raw receipts only (never "100 %" prose):
   gate receipts, council packages (`reports/csm/receipts/`),
   `work_log.md` / `state.md` / `SWITCHPOINT.md` / `drift_log.md` (D12–D18 +
   pending D19) checkpoints, git commit per unit, `coverage_report.py`
   regenerated after commits.
7. **Qwen mode switches at phase boundaries** (262k ↔ 150k ↔ 100k) as one
   atomic `qwen-switch.sh` call, checkpoint-first; the switching plan stays
   reserved for Phase 2.

## 5. Where it stands now (2026-09-09, ~22:15 IST)

- **Machine**: Qwen 262k (`pid 3584`, 30.5 GB, 1.6 GB free), `:8000` off, no
  tmux sessions. `/tmp/csm_iter1_records/` (staged commit package, R-5 plan,
  Part-A panel) was lost in the reboot — but every file the package names
  except the 9-file R-2/R-3 working set is committed; the 9 files remain on
  disk, uncommitted (git status confirms `hybrid.py`, `roster.py`,
  `facts.py`, `series/csm/overrides.yaml`, 3 test files, 2 work records,
  council_r2r3/ package, red_list addendum all present).
- **CSM position**: Phase 1, unit 3 (§9a iteration 1), between the R-2+R-3
  gate legs and the selective commit. To resume: relaunch the bay (owner:
  100k), grade/re-run the gate-3 400-row window on the CUDA :8000 (the
  4,055–4,454 window was voided; the seed-7 sample makes a re-run
  deterministic), gate 4 (canon opm + opm-set-16 pre-registration), R-2
  Part-A + R-3 Part-B re-sweeps (Part B already green), then the staged
  2-commit selective package + COUNCIL_HISTORY #23 + D19.
- **Then**: R-5 (relations router mode) fix → council → gates → re-sweep →
  commit; R-6/R-7 hooks if approved; halt meter (two no-reduction
  iterations → council) or class closure → unit 4 phase close (four gates +
  council 3a + coverage + `PHASE_A_COMPLETE` marker) → **Phase 2**
  (100k-or-smaller dial, gpu-handoff chain, CSM-4 exhaustive tier-1 ≈ 51
  GPU-h with the 17,181-row pre-extraction control arm, D6 extraction only
  if the 21-red census stays red, CSM-8 done-declaration, halt before P6).

## 6. Session inventory (CSM-relevant transcripts)

| Session (UTC start) | Role | CSM content |
|---|---|---|
| 09-07 `01a07cab` | JJK-closure day | CSM campaign council + CSM-1/2 + Wave-0 (main transcript trashed; subagent runs kept) |
| 09-08 `01a07f33` (04:08Z) | supervisor | PC-control/A-B bay build-out, csm-1b-2, gate3 re-baseline, CSM-3/3b, two-phase plan, control plan + monitor |
| 09-08 `01a080c1` (11:23Z) | Phase-1 executor (150k) | CSM-3b exit-code recheck (killed mid-run) |
| 09-08 `01a080ef` (12:12Z) | Terminal B worker | CSM-3b close, council csm-3b, Wave-2 pre-step PASS, Wave 2 deploy |
| 09-08 `01a080ec` (12:10Z) | Control Terminal A | monitor ops, gate cycle green, stall nudge, terminal-pilot skill |
| 09-08 `01a081ca` (16:11Z) | TOJI session | humanscope, Toji/Gojo scripts, JJK transcripts, D14–D16, ab-bay skill, **D17 CSM resume** |
| 09-08 `01a082b6` (20:30Z) | A (bay) | machine-monitor judging, gate-3 incident + recovery, CUDA-service flip, ESC/override execution |
| 09-08 `01a082b7` (20:30Z) | B (bay worker) | units 1–3: CSM-6 + CSM-5, §9a iter 1 (400-gate, miss queue, R-1..R-3, councils, gates, owner queue) |
| 09-09 `01a08531`, `01a085a4` | unrelated | final-year project paper (no CSM) |

Small side sessions (`01a080c1`'s siblings, `01a081b3`, `01a081bb`,
`01a081bc`, `01a081c4`, `01a08201-*`, `01a08211-*`): skill install,
terminal-pilot fixes, transcript-job A/B pair (D13), Toji prompt launches —
all recorded above where CSM-relevant.