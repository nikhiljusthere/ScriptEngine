# SWITCHPOINT — the resume file for Qwen mode switches

pi's model is the Qwen server: while the server is reloading the agent has no
model, and after reopening pi the *transcript* may be discarded (small
contexts compact fast). So everything needed to continue must live here, on
disk, **before** `qwen-switch.sh` runs. Fill the hand-written section before
every switch; `qwen-switch.sh` appends machine lines to the switch log — never
edit those.

## Current position (hand-written — fill BEFORE every switch)
- **2026-09-08 (owner re-architecture, active):** CSM two-phase plan (`plan/CSM_2PHASE_PLAN.md`) — Phase 1 (fixing) at the 150k dial with 2-subagent waves + GPU-only; Qwen is now 150k (pid 91197, free 5182 MiB); :8000 on CPU; fresh CSM session `01a080c1` (tmux `csm-phase1`) runs Phase 1; A-session restarted same-session per owner directive

- mode: **262k + `--vision` (this session started under it, 2026-09-08; the
  old stuck 100k CSM session 01a07cab is retired/trashed — everything it held
  is on disk)** → CSM campaign RESUMED. Items 1–2 are zero-GPU disk work,
  fine under 262k. Item 4 (D5 exhaustive sweep; GPU-h pending the measured
  s/probe — COUNCIL_csm-3: 4 s/probe is an unmeasured JJK number, the sanity
  runs measure CSM's rate and re-estimate before the batches) goes through the
  gpu-handoff chain (`docs/ops/PC_GPU_HANDOFF.md` + `tools/master-work/
gpu-handoff.sh`) in a 100k-mode side session — never block this session on
  the GPU, never `--api` on a chain switch.
- git: head `1f46f33` (csm: COUNCIL_csm-1b-2 record + rulings + receipt
  hygiene) on the campaign trail `… → 9e13815` (control: gates re-baselined)
  → `42aa296` (csm: CSM-2) → `1f46f33` → (this launch checkpoint). The
  master-work process committed `1eb85eb`/`42fb946` (docs rules) in parallel
  — separate area, no CSM-path overlap. Untracked (master-work, not CSM
  area):
  `plan/AB_DEPLOYMENT.md`,
  `reports/master-work/{GPU_LIVE1_REPORT.md,STOP,gpu_handoff_state/}`;
  modified by the master-work process (do not commit from the CSM session):
  `plan/decisions.md`, `plan/state.md`, `reports/master-work/a_wake_log.md`.
- trunk/excursion address (drift_log §4): **X2 CLOSED** (JJK D6 done, D11) ·
  trunk P6 not-started by owner directive (JJK-only halt). **Active: the CSM
  (Chainsaw Man) campaign** (owner-authorized 2026-09-07): the 8-item plan in
  `reports/csm/COUNCIL_csm-campaign.md` is the campaign plan; **CSM-1, CSM-1b,
  CSM-2 DONE; the COUNCIL_csm-1b-2 cadence council is complete with 5 rulings
  applied; the gate re-baseline LANDED (gpu-gate3: all 4 gates PASS on the
  1,249 tree, 2026-09-08 15:26); **CSM-3 starts.**
- work explanation (what's done, what's in flight, the exact next step):
  - **CSM-1 DONE (`064093e`)** — inventory + revid-stamp, zero new
    questions: `questions/csm.json` 39/39 active + `questions/
    _csm_relations.json` 11/11 stamped `source_revid` (18 distinct wiki
    source pages pinned, 0 unpinnable; the 1 retired entry has no `sources`
    key → null, documented; `csm-set-02`'s cbr.com source unpinnable);
    `reports/csm/CSM1_INVENTORY.md` committed (counts, revid table, the 20
    declared rosters, verification output, incident receipt). Raw receipts
    only. The tool's first run wiped the questions lists (tuple-unpack swap)
    — restored from git, fixed, recorded in the inventory's Incident section;
    same fix batch: Fandom-403 UA + CRLF/indent whole-file churn.
  - Standing four gates NOT re-run for CSM-1: no engine/store change (question
    files + a CSM-only tool in `tools/csm/`); JJK baseline untouched.
  - **CSM-1b DONE (`b526298`)** — stamped-bank validation: 4 in-place gold
    fixes (reasons in bank notes), 4 numbered engine gaps (G-CSM-1..4),
    relations bank measured 0/11 (runner `tools/csm/validate_relations.py`).
    Receipts: `reports/csm/CSM1B_BANK_VALIDATION.md` +
    `CSM1B_RELATIONS_BANK.md` + raw runs `reports/2026-09-08-{0746,0752}/`.
  - **CSM-2 DONE (`42aa296`)** — see the done-this-turn line below.
  - **COUNCIL_csm-1b-2 DONE (2026-09-08)** — 5 advisors + 5 peers (round 1's
    peer/chairman rounds were void: a harness text-capture bug made them
    review failure stubs; round 2 re-ran on the recovered advisor text; the
    run-log section in the record says so). Record:
    `reports/csm/COUNCIL_csm-1b-2.md` (+ `reports/csm/council-1b-2/peers/`).
    Rulings applied in the tree: (1) csm-set-14 accepted as corpus-compiled
    gold with the floor caveat in the bank note; (2) G-CSM-2 = retrieval-side
    (the 2026-08-17 REFUTED note wins; do NOT patch `ingest/abilities.py`);
    (3) G-CSM-4 ruled OUT of CSM-3's three doors — owner = CSM-7 fix phase;
    (4) CSM-3 done-criteria additions: per-door sanity floor, <6-word floor
    decided pre-pinning, tier-0 rename span-recall→chunk-containment, §7's
    four pilot cost numbers (addendum in `reports/csm/COUNCIL_csm-campaign.md`);
    (5) receipt hygiene: bank-changed caveat + G-CSM-1 raw receipt
    (`reports/csm/GCSM1_ROSTER_DOOR.md`) + `default="jjk"` recorded exception
    (comment in `tools/coverage_report.py` + scoreboard) + the untracked
    receipts committed.
  - **CSM-3 DONE (`f93d396`)** — D5 measurement infrastructure: the four
    §2a traps closed (pinned hashed panel + seeded held-out split, wired
    (title, sentence) resume with jsonl rewrite + ERROR re-probe,
    full-denominator hit_rate, three doors + the per-door sanity floor,
    tier-0 rename `chunk-containment` with the `span-recall` alias, the
    <6-word floor recorded as a declared boundary — CSM census 775 lines).
    The csm panel is pinned: `reports/csm/panel_csm.json`, hash
    e3d73720… (17,181 sweep + 200 held-out = 17,382 tier-0-eligible).
  - **Next: COUNCIL_csm-3** (cadence: 2 todos since COUNCIL_csm-1b-2 — the
    gate re-baseline + CSM-3; one agent at a time in any mode), **then
    CSM-4**: the D5 exhaustive tier-1 × 3 doors sweep on the pinned panel
    (17,181 × 3 doors; the ≈58-GPU-h figure assumes the unmeasured 4 s/probe —
    the sanity runs measure CSM s/probe first, JJK's warm 0.47 s/probe ≈ 8 h;
    the re-estimate lands in GATE.md before the batches, COUNCIL_csm-3 Ruling 4)
    runs in a 100k-mode side session via the tier-2
    chain — C runs the sweep, never the fixer (§9a: the agent never runs the
    sweep that grades a fix it made).
  - Council cadence: last fired after CSM-2 (`COUNCIL_csm-1b-2`); next fires
    after CSM-3 (2 completed todos).
- open questions / risks:
  - GPU at check time: Qwen 262k owns the card, `:8000` on CPU (headroom
    1,202 MiB after the gpu-gate3 262k switch-back, 15:29 → CPU is correct;
    do not co-locate). CSM-3 is code + panel work (zero-GPU up to the sweep);
    the D5 exhaustive sweep (GPU-h pending the measured s/probe, COUNCIL_csm-3)
    is CSM-4 (item 4) and goes through
    the tier-2 chain again in a 100k-mode side session.
  - The master-work A/B deploy is in flight on this box (the untracked /
    modified files above); CSM commits stay CSM-area paths only, and the
    master-work files are managed by that process.
- first action on resume: **CSM-3** (item 3 scope + the addendum in
  `reports/csm/COUNCIL_csm-campaign.md`) — the gpu-gate3 RESUME landed
  (15:30:08) and its steps are done (report read, `:8000` on CPU, baselines
  rewritten, CSM gate section opened, C transcript trashed).
- done this turn (2026-09-08, CSM-3): D5 measurement infrastructure, the
  four §2a traps closed (`f93d396`): `build_panel` (deterministic order,
  sha256 hash stamped, seeded held-out split written to a side file the
  executor never opens; csm panel pinned: hash e3d73720…, 17,181 sweep +
  200 held-out, tier-0 17,382/17,382 re-confirmed); pinned `recall()`
  (no corpus read under a running sweep, resume keyed (title, sentence),
  jsonl rewritten not append-duped, transient ERROR rows re-probed,
  hit_rate over the FULL panel, crash-tolerant sidecar); the `door` param
  forces the /context mode per door (qa / roster / narrative) with
  per-door `sweep_<door>.jsonl` + `--sanity N` dead-door halt (exit 3);
  tier-0 renamed `chunk-containment` (`span-recall` alias kept, both
  registered + tested); the <6-word floor decided pre-pinning per ruling
  4b = record the exclusion (CSM census: 775 sub-6-word lines, all in
  chunks, all chapter-list rows; recorded in `series/csm/overrides.yaml`).
  CLAUDE.md command line updated. pytest **1,253** green on CPU (1,249 +
  4 new; the 6 VRAM-sensitive cases pass on CPU, 127 s). Council cadence:
  COUNCIL_csm-3 fires next (2 todos since COUNCIL_csm-1b-2), then CSM-4.
- done this turn (2026-09-08, gpu-gate3 RESUME 15:30:08): read C's report —
  all 4 gates PASS on CUDA on the 1,249 tree (pytest 1,249/1,249 incl. the 6
  OOM cases, eval jjk 31/31, span-recall jjk 48,572/48,572 + 390/400 probe,
  canon opm 10/16 · 236/236 · 79.0%; receipts
  `reports/csm/GATE_REBASELINE_2.md` committed). `:8000` verified on CPU (the
  262k switch-back had already placed it — pid 80967, /health device=cpu;
  Qwen pid 80906 is the only GPU process). Chain state clean (state=done, no
  STALLED, one typed RESUME 15:30:08). C transcript trashed after reading the
  report. CLAUDE.md + gates-skill baselines re-baselined 1,242 → 1,249 with
  run timestamps; the 1,242 `GATE_REBASELINE.md` marked superseded; the CSM
  gate section opened in `reports/comprehension/GATE.md` as the live record.
  Committed. **Next: CSM-3** (D5 measurement infrastructure).
- done this turn (2026-09-08, gpu-gate3 launch — fresh CSM session 01a08064,
  inheriting from disk; the retired session 01a07ff0's window 51768426 is
  BadWindow, so the spec's A-side fields were retargeted): a_win=51286464
  (my terminal — the pts/1 `pi` pid 78300 start 09:41:24Z matches this
  session's 09:41:25Z; the other "π - ScriptEngine" window 50331658 is the
  live master-work session 01a07f33's terminal), a_session = this session's
  jsonl, a_title unchanged. Committed the spec + task + this switchpoint
  (launch checkpoint), then launched the tier-2 chain (setsid
  gpu-handoff.sh --tier2 plan/gpu_gate3.spec). Sitting idle at the prompt
  until the typed RESUME.
- done this turn (2026-09-08, COUNCIL_csm-1b-2 + rulings): cadence council
  completed (5 advisors + 5 peers; round 1's peer/chairman rounds void on a
  harness text-capture bug — round 2 re-ran on recovered advisor text, noted
  in the record's run-log). Record + peer files committed with the 5 rulings
  applied in the tree (bank note, CSM1B receipt, tool comment, scoreboard,
  campaign-plan addendum, G-CSM-1 raw receipt, untracked receipts committed).
  Hard blocker now: the gate re-baseline (suite 1,249 vs the record's 1,242)
  runs in the gpu-gate3 100k+CUDA side session; CSM-3 opens on its report.
- done this turn (2026-09-08, CSM-2): scoreboard generalized — `page_scope`
  + `unknown_pages` + `archetypes` + `remainder_note` in `series/csm/`
  overrides.yaml (13 types classified; the 14 unknowns each disposed; 4 in
  scope) and the same encoding in `series/jjk/overrides.yaml` (retired
  hardcoded behavior verbatim); `tools/coverage_report.py` reads the scope,
  exits 3 on unclassified; JJK output byte-identical (modulo Generated);
  csm denominator 537, in-scope remainder 227; 7 new tests (pytest 1249).
  Receipt: `reports/csm/CSM2_SCOREBOARD.md`. **Next: CSM-3** (D5
  measurement infrastructure). Council fires on the 2 completed todos
  (CSM-1b + CSM-2) → `reports/csm/COUNCIL_csm-1b-2.md`.
- done this turn (2026-09-08, gpu-live2 RESUME): read C's report (all 4 gates
  PASS on CUDA), `:8000` verified on CPU, chain state clean (no STALLED, one
  typed resume), C transcript trashed, CLAUDE.md + gates-skill baselines
  re-baselined with run timestamps + committed. **Next: CSM-2** (page-type
  classification + scoreboard generalization, council item 2 — grounding data
  in the CSM-1b todo note + `reports/csm/`).
- done this turn (2026-09-08, CSM-1, fresh 262k+vision session): CSM-1
  DONE + committed `064093e` (stamped bank + inventory artifact, CSM-area
  paths only). Tool fixes committed with it: Fandom-403 UA, tuple-swap
  data-loss (restored from git, then fixed), CRLF/indent churn. Coverage
  regenerated (JJK 893/987, in-scope remainder 0 — date-line only change).
  Standing gates not re-run: CSM-1 made no engine/store change. Next: CSM-2
  (page-type classification + scoreboard generalization, council item 2);
  council fires after CSM-2 (cadence: every 2–3 todos).
- done this turn (2026-09-07 23:3x, CSM Wave-0 + campaign start): CSM
  grounded (537 pages, 5,081 facts, 11 types, audit 5/5 PASS, span-recall
  rc=2 with 439 unreachable) → diagnosed (pre-G15 index + Notes/References
  divergence) → fixed (re-index + `content_sections`) → verified (0
  unreachable, 100.0000%; all standing gates green on CUDA, 1,242 pytest).
  Two new owner rules persisted in CLAUDE.md (GPU >15 min; 10–15 s polling
  + explicit timeout). CSM campaign todos created (#11–#15). Council on
  the CSM plan launched. Committed `281fe2e`.

## gpu-gate3 handoff (2026-09-08 — A=01a08064 (fresh CSM session; retargeted from the retired 01a07ff0) → chain → C on 100k → A resume)

**DONE 15:30 local — chain complete (state=done, no STALLED, typed RESUME
15:30:08; C transcript trashed after the report was read; `:8000` back on CPU
via the 262k switch-back, pid 80967, /health device=cpu).** All 4 gates PASS
on CUDA on the 1,249 tree (receipts `reports/csm/GATE_REBASELINE_2.md`):
pytest **1,249/1,249** (the 6 OOM cases pass on GPU) · eval jjk **31/31** ·
span-recall jjk **48,572/48,572** offline + **390/400 (97.5%)** probe · canon
opm **10/16 exact, 236/236, 79.0%**. CLAUDE.md + gates-skill baselines
re-baselined 1,242 → 1,249; the 1,242 `GATE_REBASELINE.md` record is
superseded; the CSM gate section is now open in
`reports/comprehension/GATE.md` as the live record.

**Gate re-baseline, round 2 (council blocker, COUNCIL_csm-1b-2).** The
GATE_REBASELINE record (1,242, git `9e13815`) predates CSM-2's +7 tests
(`42aa296` → suite 1,249): the "JJK baseline" is no longer reproducible and
CSM-3's gate re-verification would start broken. Same tier-2 chain as
gpu-live2: `gpu-handoff.sh --tier2 plan/gpu_gate3.spec` flips 262k→100k,
opens C (visible terminal, fresh 100k pi) which runs the four standing gates
**on CUDA on the 1,249 tree** per `plan/gpu_gate3_task.md` (pytest full —
the 6 VRAM-sensitive `test_context` cases must pass; eval jjk; span-recall
jjk offline + --probe 400 on a CUDA `:8000`; canon opm --skip-eval) →
`reports/csm/GATE_REBASELINE_2.md`, flips back 262k, typed RESUME into A's
window (51286464).

**On resume (the typed RESUME line is my next user message):**
1. Read `reports/csm/GATE_REBASELINE_2.md` (C's 1,249-tree re-baseline).
2. Restore `:8000` to CPU (C leaves it on CUDA; 262k co-location rule).
3. Check chain state: `reports/master-work/gpu_handoff_state/gpu_gate3.
{log,stalled,typed}` + `/tmp/gpu_gate3_chain.log`; a `STALLED` flag =
   inspect, then replay the same setsid line (gates are idempotent).
4. Trash C's transcript (`…/gpu_handoff_state/c_session`) — only AFTER
   reading the report.
5. Rewrite the CLAUDE.md + gates-skill baselines (1,242 → 1,249 + run
   timestamps; the record's 1,242 line is superseded), open the CSM gate
   section in `reports/comprehension/GATE.md` as the live record (council
   peer-C finding: the campaign's designated live gate record did not exist),
   commit — then start **CSM-3** (item 3 scope + the addendum in
   `reports/csm/COUNCIL_csm-campaign.md`).

## gpu-live2 handoff (2026-09-08 — A=01a07ff0 → chain → C on 100k → A resume)

**DONE 13:57 local — chain complete (state=done, no STALLED; C transcript
trashed after the report was read; `:8000` back on CPU, pid 62983).** All 4
gates PASS on CUDA (receipts `reports/csm/GATE_REBASELINE.md`):
pytest **1,242/1,242** (the 6 OOM cases pass on GPU) · eval jjk **31/31** ·
span-recall jjk **48,572/48,572** offline + **390/400 (97.5%)** probe ·
canon opm **10/16 exact, 236/236, 79.0%**. CLAUDE.md + the gates skill
baseline updated with these numbers + run timestamps (the 1,239-vs-1,242
stale pair is resolved: the suite is 1,242).

Second live run of the gpu-handoff chain (docs/ops/PC_GPU_HANDOFF.md):
`gpu-handoff.sh --tier2 plan/gpu_live2.spec` flips 262k→100k, opens C
(visible terminal `GPU-gpu_live2`, fresh 100k pi) which runs the
**standing-gates re-baseline** per `plan/gpu_live2_task.md` (pytest full on
CUDA incl. the 6 OOM cases, eval jjk, span-recall jjk offline + --probe 400
on a CUDA :8000, canon opm --skip-eval) → `reports/csm/GATE_REBASELINE.md`,
flips back 262k, and the gated typer types the resume line into A's window
(51768426). A sits idle at its prompt meanwhile (frozen context, zero cost).
Context: CSM-1b (owner directive 2026-09-08) is DONE + committed — bank
validation + 4 in-place gold fixes + relations runner + 4 numbered engine
gaps (G-CSM-1..4); the gate re-baseline moved to this side session (owner
correction: 262k holds the card → 100k+CUDA, never CPU fallback).

**On resume (the typed RESUME line is my next user message):**
1. Read `reports/csm/GATE_REBASELINE.md` (C's re-baseline).
2. Restore `:8000` to CPU (C left it on CUDA; 262k co-location rule —
   headroom 1,604 MiB < 6 GiB).
3. Check chain state: `reports/master-work/gpu_handoff_state/gpu_live2.{log,stalled,typed}`
   + `/tmp/gpu_live2_chain.log`. A `STALLED` flag = inspect, then replay:
   `setsid nohup bash tools/master-work/gpu-handoff.sh --tier2 plan/gpu_live2.spec >/dev/null 2>&1 &`
   (gates are idempotent).
4. Trash C's transcript (`reports/master-work/gpu_handoff_state/c_session`)
   — only AFTER reading the report (deleting it earlier poisons the
   switch-back fit guard).
5. Update CLAUDE.md's stale gate values with the re-baselined numbers + run
   timestamps (the 1,239 vs 1,242 self-contradiction), commit, then resume
   **CSM-2** (scoreboard/classification, council item 2 — its grounding data
   is in `plan/SWITCHPOINT.md`'s CSM-1b todo note / `reports/csm/`).

## gpu-live1 handoff (2026-09-08 — A=01a07f33 → chain → C on 100k → A resume)

First LIVE run of the gpu-handoff chain (docs/ops/PC_GPU_HANDOFF.md):
`gpu-handoff.sh --tier2 plan/gpu_live1.spec` flips 262k→100k, opens C
(visible terminal `GPU-gpu_live1`, fresh 100k pi) which runs the JJK gate
baseline per `plan/gpu_live1_task.md` (→ `reports/master-work/GPU_LIVE1_REPORT.md`),
flips back 262k, and a gated plain-shell typer types the resume line into A's
window (50331658). A sits idle at its prompt meanwhile (frozen context, zero
cost). Engine was untouched by today's MASTER_WORK deploy, so the baseline
should hold (eval 31/31, span-recall 100%); a deviation is a real signal.

**On resume (the typed RESUME line is my next user message):**
1. Read `reports/master-work/GPU_LIVE1_REPORT.md` (C's baseline).
2. Restore `:8000` to CPU (C left it on CUDA; 262k co-location rule —
   headroom 3.5 GiB < 6 GiB).
3. Check chain state: `reports/master-work/gpu_handoff_state/gpu_live1.{log,stalled,typed}`
   + `/tmp/gpu_live1_chain.log`. A `STALLED` flag = inspect, then replay:
   `setsid nohup bash tools/master-work/gpu-handoff.sh --tier2 plan/gpu_live1.spec >/dev/null 2>&1 &`
   (gates are idempotent).
4. Trash C's transcript (`reports/master-work/gpu_handoff_state/c_session`)
   — only AFTER reading the report (deleting it earlier poisons the
   switch-back fit guard).
5. CSM resume remains on hold (owner-paused; the stuck session 01a07cab
   resumption is a separate, later flip).

## Campaign todos (live list — every CSM session rebuilds its todo panel from this section and syncs it back after each status change; the panel is per-session volatile state, disk is the tiebreaker)

- [x] 0. Wave-0 tier-0 reachability — 439→0 unreachable, span-recall csm rc=0 (record only; 6-word floor note in the audit)
- [x] 1. Seed-bank inventory + revid-stamp (CSM-1 — `064093e`)
- [x] 2. Classify every CSM page type + generalize the scoreboard (CSM-2 — `42aa296`; 14 unknowns resolved, JJK output byte-identical)
- [x] Standing-gate re-baselining ×2 — gpu-live2 (`GATE_REBASELINE.md`, 1,242) + gpu-gate3 (`GATE_REBASELINE_2.md`, 1,249; CLAUDE.md + gates-skill baselines updated, `2c80867`)
- [x] 3. D5 measurement infrastructure (CSM-3 — `f93d396`: pinned hashed panel + held-out split, csm panel pinned hash e3d73720… (17,181 + 200); wired (title,sentence) resume, jsonl rewritten; full-denominator hit_rate; three doors + --sanity dead-door halt; tier-0 rename `chunk-containment` (alias kept); <6-word floor recorded (775-line census, exclusion stands); pytest 1,253)
- [ ] 4. D5 exhaustive tier-1 × 3 doors (**PHASE 2 — extraction**; GPU-h pending measured s/probe — sanity runs measure it first, COUNCIL_csm-3 Ruling 4; batched via the gpu-handoff chain in Qwen quiet windows, smaller dial if VRAM demands; standing 400-probe gate stays)
- [ ] 5. Phase-0 remainder (**PHASE 1 — Wave 2, sub 4**) — 5.3 pilot fixtures / 5.5 no-LLM-judge / 5.4 door-first (extraction only on red) / §13 awareness line / the twenty-failures set (named author)
- [ ] 6. D6 oracle + bounded instrument (**PHASE 1 — instrument half**: parameterize the two jjk-hardcoded tools, CSM dimension map, eight-verb sample, frozen census sets (seeded + revid-stamped, D4 authored by a fresh-context subagent), T0 pilot, cross-page fact census; **PHASE 2 — extraction half**, only on red census)
- [ ] 7. §9a closure loop (D1–D6; **PHASE 1 iteration 1**: one class per fix, never reword to pass, halt on regression / two no-reduction iterations)
- [ ] 8. Done-declaration + pilot memo (**PHASE 2**; pasted raw output + the four pilot numbers; JJK baseline diff-empty; halt before P6)
- Standing items (whole campaign): council every 2–3 todos — **one agent at a time** (owner rule 2026-09-08); raw receipts, never "100%" prose; `coverage_report` regenerated after every commit; the four standing gates before any pass is declared done; per-wiki handling in `series/csm/overrides.yaml` / `tools/csm/` only; JJK baseline untouched; **Phase 1 (owner rule 2026-09-08): all model/GPU work on CUDA at the 150k dial, no CPU shell command >15 s, 2-subagent waves; the gpu-handoff switching plan is Phase 2 only**.

## Switch log (machine-appended by qwen-switch.sh)

- (none yet)- 2026-09-07T22:05:09+05:30 qwen-switch: ctx=102400 (mode 100k), api=off, free=8988MiB
- 2026-09-07T22:17:58+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=8986MiB
- 2026-09-07T22:19:34+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=8986MiB
- 2026-09-07T22:53:45+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=3513MiB
- 2026-09-07T23:32:51+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=9002MiB
- 2026-09-08T10:14:37+05:30 qwen-switch: ctx=135168 (owner manual +--vision; profile = serve_ctx_135168.sh), api=cpu, free=5575MiB
- 2026-09-08T12:51:22+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=7072MiB
- 2026-09-08T12:56:08+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1604MiB
- 2026-09-08T13:47:15+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=6932MiB
- 2026-09-08T13:56:00+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1488MiB
- 2026-09-08T15:18:32+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=6699MiB
- 2026-09-08T15:29:18+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1202MiB
- 2026-09-08T16:50:27+05:30 qwen-switch: ctx=150000 (mode 150000), api=cpu, free=5182MiB
