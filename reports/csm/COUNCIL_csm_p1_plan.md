# COUNCIL — CSM Phase-1 plan approval (2026-09-09)

## Question

Approve / amend / reject **Phase 1 of `plan/CSM_2PHASE_PLAN.md` (v2, 2026-09-09)** — the goal anchor, the process layer v2, and steps P1.1–P1.4. Goal: CSM at full D1–D6 comprehension; 100 % = the checkable D1–D10 done-set + a triage log for every residual, never "100 %" prose; CSM is the P6 successor to JJK's 09-07 done-declaration; halt before P6. Six scope questions: goal anchor, process layer v2 (7 rulings), P1.1 preconditions, P1.2 wave order/cost/meter, P1.3 halt-meter scoping, P1.4 close conditions (full text `reports/csm/receipts/council_p1_plan/QUESTION.md`).

## Members

11: 5 advisors + 5 peer reviewers + chairman. All zero-GPU, read-only (each member could write only its assigned receipt), fresh context, no member saw another's response.

| Letter | Role | File |
|---|---|---|
| A | The Executor | `adv_executor.md` |
| B | The Contrarian | `adv_contrarian.md` |
| C | The First Principles Thinker | `adv_first_principles.md` |
| D | The Outsider | `adv_outsider.md` |
| E | The Expansionist | `adv_expansionist.md` |
| R1–R5 | Peer reviewers (anonymized, weighted to failure modes) | `review_1.md` … `review_5.md` |
| Chair | Chairman (this record) | this file |

**Method note:** the 5 advisors ran **in parallel**, then the 5 peer reviewers **in parallel**, then the chairman — per the owner's 2026-09-09 23:2x instruction (phase-scoped councils; 5 advisors in parallel per phase), which **supersedes the sequential one-at-a-time convention for this council only**. Prior art: the superseded unified plan-council (`reports/csm/receipts/council_plan_v2/`) — A and B's executor/contrarian lenses were seeded from it per QUESTION.md.

## Verification notes

Every load-bearing claim in the verdict, re-verified against disk by the chairman before recording (zero-GPU, read-only):

| Claim | Verification | Result |
|---|---|---|
| Queue math 58 = 33 fixable + 22 floor + 3 stamped | `wc -l reports/csm/miss_queue_csm_iter1.jsonl` → 58; ruling/status counter: 3 closed(fixable, by R-1: csm-set-14/15, red-R-1) + 30 open(fixable) + 3 open(stamped) + 22 open(floor) | **Confirmed.** Fixable total = 33 (30 open + 3 closed); the plan's "~30 fixable / 22 floors" (L108) omits the 3 stamped and the 3 closed |
| `/tmp/csm_iter1_records` absent | `ls /tmp/csm_iter1_records` → `No such file or directory`; work_log 06:49:04 (item 1: commit_messages.txt) + 06:49:42 (item 2: r5_class_plan.md) prove it existed and held the C1/C2 messages + R-5 brief | **Confirmed lost** in the reboot; reconstructable model-free from work_log |
| qwen_mode.txt dial + free MiB | `cat /home/goblin/ninfer-work/qwen_mode.txt` → `mode=262k ctx=262144 … free_mib=1606 api=off` (ts 23:29:19); `nvidia-smi` → 30,498 MiB used / 1,605 MiB free | **Confirmed:** no CUDA `:8000` (~5–7 GB) possible as-is; the 262k→100k switch is a precondition, not the plan's step |
| 9-file uncommitted package | `git status --short` → 15 modified + 17 untracked = 32 entries; package files all uncommitted: `hybrid.py`, `roster.py`, `facts.py` (M), `series/csm/overrides.yaml` (M), `tests/test_retrieve.py`, `tests/test_csm_fixtures.py` (M), `tests/test_csm_roster_scoping.py` (??), `reports/csm/red_list_csm.md`, `reports/master-work/work_log.md` (M); contamination present: `E:\Personal\Plot Works/`, `sample scripts/`, stale `STOP`, untracked `reports/csm/receipts/*` dirs | **Confirmed** — one `git add .` away from an impure "atomic" commit |
| Council #21 R3 halt scoping | `reports/csm/COUNCIL_unit3_sweep.md` (R3 ruling): "The halt rule counts only Phase-1-fixable classes (plan Phase-1 done-criterion: 'the closure loop at a no-reduction halt or a documented floor', 2PHASE L92-98)" | **Confirmed** — the scoping exists in the record; the plan cites it (L112–113) but never states it in P1.3's prose |
| R-6 floor-inheritance note | `reports/csm/receipts/council_r2r3/chairman.md:43`: "8. **R-6 floor-inheritance question (R5)** — the `subject_aliases` hook design (aliases-table vs query-time override) must answer whether alias-resolved subjects inherit the new level-0 card via the floor. Recorded for R-6 drafting." | **Confirmed at line 43** — live design question hidden under R-6's "no-council" lever |
| pytest collect count vs plan's 1,303+2xp | `python -m pytest tests/ --collect-only -q` → **1,305 tests collected**; work_log gate-1 pin: "1,305 (1,303 passed + 2 xpassed)" | **Plan is right** (1,303+2xp = 1,305 collected); CLAUDE.md L355 "1,254" is stale |
| Plan blob (version-pin) | `git hash-object plan/CSM_2PHASE_PLAN.md` | **`840d413088d448abb7a1099aab81897443061455`** — this approval attaches to that artifact |
| Supporting checks | `reports/csm/GATE.md` absent; `reports/master-work/phase_status.txt` absent; `census_roster_100_csm.json` items n=**11** (D1 vacuity); `placement_audit_csm.json` stats groups=0 / arc_ranges {} (D5 met on zero events); `panel_csm.json` panel_size=17,181, held_out=200, min_words=6, seed=42; work_log item 4 (Part-A pre-build) has no DONE entry ("REMAINING: Part A … queued behind the gate-3 probe window"); CLAUDE.md L291/298 "150k Phase-1 mode" line present; plan L138 "reachability proxy until a bar audit proves transfer" + L144–145 "contingent per the council-#19 P4 ruling" present; COUNCIL_HISTORY.md row #24 = session audit, "#23 reserved for the R-2+R-3 council" | All **confirmed** |

## Where the Council Agrees

- **P1.1 is not executable as written.** A (four missing preconditions), B (not executable: /tmp loss, unlisted rebuild + bay redeploy), D (four concrete defects: "seed-7"/"one-copy" undefined, queue math wrong, Part-A "pre-built" false). E alone said "executable (9-file package intact)" — E is right that the package is intact, wrong that the plan is executable: the verified 262k dial (free 1,606 MiB, api=off) makes the plan's first step (Seed-7 400-probe on the CUDA `:8000`) impossible until the unlisted 100k switch, and the /tmp loss kills the "pre-built rows + hash" premise. R2 and R5 both flag E's verdict as wrong. **(A, B, D; R2, R5)**
- **The model-free rebuild pass is owed before the switch.** /tmp/csm_iter1_records is gone; C1/C2 messages, the R-5 brief, and the Part-A panel (work_log item 4 never DONE) must be reconstructed from work_log 06:49:04/06:49:42 + the receipts. **(A, B; verified by chair)**
- **The 100k switch is the plan's SPOF and must be an ordered, named precondition** (SWITCHPOINT → qwen-switch.sh 100k → pi_restart → CUDA `:8000`, named redeployer, with an abort/rollback branch). **(A; R4)**
- **A C3 doc-hygiene commit is missing**: CLAUDE.md "JJK D6 active" lines + stale 150k-mode line + stale 1,254 suite count, WAVE2 §1 CSM-3 = `bc73795`→`f93d396`, v1 cadence un-retired; the untracked receipts dirs are outside C1/C2. Path-limited adds; ban `git add .`. **(A, B, D; R1, R2)**
- **The halt meter must be scoped in P1.3's prose**: the 22 never-reducing floors (+ 3 stamped) must be excluded, per #21 R3, or "two no-reduction iterations" trips on iteration 1. **(A, B, C, D; R5: "A's 'state it in one sentence' survives")**
- **The R-6 floor-inheritance question must be pre-registered** in the R-5 council brief so the "no-council" lever doesn't hide it. **(B, D, E; R1)**
- **P1.4 is incomplete**: campaign-todos sync (done-criterion only), the doc-hygiene commit, the `reports/csm/GATE.md` skeleton (absent; P2.1's receipts need it), and the bar-audit pull-in. **(A, B, C, E; R1, R5)**
- **D1 transfers vacuously** to CSM (roster census = 11 questions, not 100). **(C, D)**
- **The queue math must read 33 fixable + 22 floor + 3 stamped = 58.** **(A, D; verified by chair + R5)**
- **P1.1 step 0 = zero-GPU baseline re-verify** (pytest collect + span-recall offline) on the dirty tree, re-anchoring "baseline-exact" post-reboot. **(R3; chair re-ran the collect: 1,305)**
- **The approved artifact must be version-pinned** (the plan file itself is dirty in the 32-entry tree; receipts untracked). **(R2; done — blob recorded above)**

## Where the Council Clashes

1. **P1.1 executability — E vs A/B/D.** E: "executable (9-file package intact)"; A/B/D: not executable as written (switch not a step, /tmp records lost, Part-A panel never built, monitor-gap hazard live through P1.1 if a bay is used). **Resolution: A/B/D prevail.** The intact package is a fact, but executability requires preconditions the plan never lists. E's one surviving upside (cross-corpus census sweep, 34 s + 18 s) is not needed for Phase 1 and is deferred to the Phase-2 council.
2. **The P1.3 meter — E vs A/B/D.** E: "correctly scoped — the 22 floors don't count (plan L111–113 cites #21 R3)"; A/B/D: "the meter trips itself / underscoped — a literal reading halts iteration 1." **Resolution: both are half right, and the split is the amendment.** E is right that the plan *cites* #21 R3 (L112–113) and the record does scope the halt to Phase-1-fixable classes (verified). A/B/D are right that P1.3's own prose ("halt on … two no-reduction iterations" over the 58-row queue) never states the scoping, so a literal execution halts on iteration 1 into a council the shrunk trigger list doesn't authorize. Amendment A11 states the scoping in the prose; the citation stays.
3. **The goal-anchor noun — C vs D/E.** C: "the plan certifies the wrong noun" (D1–D10 is JJK's reachability done-set; the sole comprehension step P2.3 is contingent — the done-set can close on triage lines without understanding). D: table "self-contained — good"; E: "right Phase-1 boundary." **Resolution: C's Phase-1-relevant text amendments are accepted** (A13 D1-vacuity note; A14 contingency flag + bar-audit ordering via A12d). The plan itself already concedes "reachability proxy until a bar audit proves transfer" (L138, verified) — the missing pieces are the vacuity note, the explicit contingency flag, and pulling the model-free bar audit before the 51-GPU-h panel. The **full P2 debate** (de-contingent P2.3 / add a numbered D6 comprehension item) is **deferred to the Phase-2 council** per the owner's phase-scoped instruction.
4. **The P1.2 90-min draft — B/D vs A/E.** B: "bundles relations mode + builder + R-6 + R-7 off a lost brief, after two workers died at 60 min — the timeout incident class re-triggers here first"; D: "over-scoped"; A/E: "order and meter right." **Resolution: keep the order and the meter (≥ 1 own-new-row HIT or halt); split the draft.** The 90-min draft covers R-5 core only; R-6/R-7 land as separate short no-council passes under Process R-2 (A6).

## Blind Spots the Council Caught

(from the five peer reviews)

- **Gate baselines taken at face value (R1).** No advisor cross-checked the plan's inlined four-leg values against the latest receipts (`GATE_REBASELINE_2`, CSM-3b gates); if any is stale, P1.1's first gate leg fails for the wrong reason. Chair note: the plan's pytest value *was* re-verified (1,303+2xp = 1,305 collected, matches the work_log pin); the remaining legs are covered by the A2 step-0 re-verify.
- **The approved artifact is not version-pinned (R2).** `plan/CSM_2PHASE_PLAN.md` is itself a dirty (M) file in the 32-entry tree, and the council receipts (`reports/csm/receipts/*`) are untracked, outside C1/C2 scope → blob hash recorded (A: `840d413…` above) and the receipts fold into C3 (A4).
- **The dial and the suite count were never checked against owner rules (R3).** CLAUDE.md's "150k Phase-1 mode" (L291/298) contradicts the plan's 262k→100k, and its "1,254" suite count (L355) contradicts the plan's 1,303+2xp. Chair verified: qwen_mode.txt = 262k (the switch is right; the CLAUDE.md line is stale) and 1,305 collected (plan right; CLAUDE.md stale) → both lines added to the C3 hygiene list (A4).
- **The 100k switch is the plan's SPOF with no abort path (R4).** The SWITCHPOINT checkpoint sits uncommitted in the dirty tree, /tmp is already proved lost across one reboot, and no member defined what happens if qwen-switch or pi_restart fails (model down, no CUDA `:8000`, campaign stalled). A1 adds the named redeployer + abort/rollback branch. R4 also prices the council legs: P1.2's kept §3 trigger + a P1.3 halt trigger = up to two sequential 5+5+1 council cycles the 2–3-day estimate excludes.
- **The JJK-stays-100 % invariant was unchecked (R5).** No member verified the R-5 router-mode commit + R-6/R-7 overrides leave the JJK baseline green. It is covered by baseline-exact, but the R-5 meter re-sweep must carry the JJK/OPM invariant pins (the work_log R-5 brief already names them, "JJK/OPM invariant pins per the R-1 pattern") — stated in A9.
- **`git add .` is the contamination bug the dirty tree exposes (R1).** 15 M + 17 untracked incl. `E:\Personal\Plot Works/`, `sample scripts/`, stale `STOP` → path-limited adds by named paths, `git add .` banned (A4).

## The Amendments

Ordered; each PLAN-LINE-REF → exact change. Line refs are to `plan/CSM_2PHASE_PLAN.md` @ blob `840d413`.

**P1.1 preconditions (L84–97):**
1. **A1 — L84/L89: the 100k switch becomes an ordered precondition step.** Insert before the gate legs: `SWITCHPOINT checkpoint (plan/SWITCHPOINT.md — commit it in C3) → ninfer-work/qwen-switch.sh 100k → pi_restart.sh → bring up the CUDA :8000`, with a **named redeployer** (A flips the bay per the owner standing rule; P1.1 must name who brings up `:8000`) and an **abort branch** (switch/restart failure → abort before any gate leg; rollback = `qwen-switch.sh 262k`; no gate legs on a dead model). Rationale (verified): qwen_mode.txt = mode=262k, free_mib=1606, api=off.
2. **A2 — L89: zero-GPU baseline re-verify as P1.1 step 0.** Before the switch: pytest collect (pin 1,305 = 1,303+2xp) + `span-recall --series jjk` offline (48,572/48,572) + red-list recount, on the current dirty tree, re-anchoring "baseline-exact" post-reboot; the four gate legs run only after it.
3. **A3 — L90: model-free rebuild pass (~30 min, before the CUDA probe).** `/tmp/csm_iter1_records/` is gone (verified) → reconstruct from work_log 06:49:04/06:49:42 + the on-disk receipts: the C1/C2 commit messages, the R-5 brief (`r5_class_plan.md`), and the R-2 Part-A panel rows + hash + ledger target (work_log item 4 never DONE — L90's "pre-built rows + hash" is false as written).
4. **A4 — L93–96: add a C3 doc-hygiene commit to the selective package.** C3 = CLAUDE.md L14/341 ("JJK D6 active" → done, P6-successor framing) + CLAUDE.md L291/298 (retire the stale "150k Phase-1 mode" line; dial = 262k ↔ 100k per qwen_mode.txt) + CLAUDE.md L355 (suite count 1,254 → 1,303+2xp = 1,305 collected) + `CSM_WAVE2_RESUME.md` §1 (CSM-3 = `f93d396`, not `bc73795`) + v1 cadence un-retired + the untracked `reports/csm/receipts/` dirs (council_p1_plan, council_plan_v2, council_r2r3, council_p2_plan, iter1_*.md). **All commits use path-limited `git add` by named paths only; `git add .` is banned** (dirty tree = 15 modified + 17 untracked incl. `E:\Personal\Plot Works/`, `sample scripts/`, stale `STOP`).
5. **A5 — L96/L114: create the `reports/csm/GATE.md` skeleton** (verified absent; P2.1's per-door raw numbers land there — the plan's own P2.1 references it).

**P1.2 (L98–107):**
6. **A6 — L98–101: split the 90-min draft.** The 90-min-or-split draft covers **R-5 core only** (4th series-agnostic router mode `relations` + budgeted bundle builder + MODES/endpoint update). **R-6 (`subject_aliases`, 3 arc-display names) + R-7 (`identity_fields`, 61-key map) become separate short no-council passes** under Process R-2 — the 90-min bundle re-triggers the timeout-incident class (two workers died at 60 min) and the brief it was drafted from is lost.
7. **A7 — L102: pre-register the R-6 floor-inheritance question in the R-5 council brief.** Per `reports/csm/receipts/council_r2r3/chairman.md:43`: the `subject_aliases` hook design (aliases-table vs query-time override) must answer whether alias-resolved subjects inherit the new level-0 card via the floor — so the "no-council" lever does not hide an open design question.
8. **A8 — L98: optional add — cross-corpus R-5 spot-pins.** 2–3 relationship phrasings per other corpus, model-free, registered so P6 starts with 8-corpus router coverage (E's upside; optional, does not gate Phase 1).
9. **A9 — L103/L110: define "own-new-row HIT" in one line** (used in the plan, the council record, and work_log; defined nowhere — verified by grep): the class's own targeted re-sweep hits ≥ 1 of the class's own new/stamped rows (work_log R-3-leg usage: set-17/set-01/char-02 = 3/3 own-new-row HITs) or halt; the re-sweep carries the JJK/OPM invariant pins per the R-1 pattern.

**P1.3 (L108–113):**
10. **A10 — L108: correct the queue math.** "Miss-queue (58 rows: ~30 fixable / 22 floors)" → **"58 rows = 33 fixable (30 open + 3 closed by R-1) + 22 extraction-gated floor + 3 stamped"** (verified against `miss_queue_csm_iter1.jsonl`).
11. **A11 — L110–113: carry #21 R3's scoping into the prose.** After "halt on miss-count regression or two no-reduction iterations" add: "the halt meter counts **only the 33 fixable rows**; the 22 floor rows + 3 stamped rows are excluded (council #21 R3: 'the halt rule counts only Phase-1-fixable classes', `reports/csm/COUNCIL_unit3_sweep.md`)." Without this, a literal reading trips on iteration 1 into a council the shrunk trigger list doesn't authorize.

**P1.4 (L114–122):**
12. **A12 — L114–118 + L120–122: add the missing close conditions.** (a) the campaign-todos section sync moves from done-criterion to close condition; (b) the doc-hygiene commit (C3, A4) is landed; (c) the `reports/csm/GATE.md` skeleton (A5) exists; (d) **bar-audit pull-in**: P2.2's model-free 3–5 pre-registered CSM panel-line cases per D6 dimension run **before the `PHASE_A_COMPLETE <ts>` marker**, so the done-set is bar-adjudicated before 51 GPU-h of P2.1; (e) the **R-6 floor-inheritance verdict** (from the R-5 council, A7) is recorded in the `PHASE_A_COMPLETE` marker so Phase 2 cannot relitigate it.

**Goal anchor (L14–28, L138, L144–145):**
13. **A13 — L20 (D1 row): the vacuity note.** "D1 transfers vacuously to CSM: CSM's roster census is 11 questions (`census_roster_100_csm.json`, items n=11; doors 11/11) — D1 closes at 11/11, not 100."
14. **A14 — L144–145: the P2.3 contingency flag, Phase-1-relevant scope only.** Mark P2.3 ("contingent per the council-#19 P4 ruling") as the plan's **sole comprehension step**, and record: if it does not fire, the D1–D10 done-set closes on triage-log lines, not understanding (the plan's own L138 concession, verified). The bar-audit ordering fix is A12(d). **The full P2 debate** (de-contingent P2.3, or add a numbered D6 comprehension item) **is deferred to the Phase-2 council** per the owner's phase-scoped instruction.

**Count: 14 amendments** (P1.1: 5 · P1.2: 4 · P1.3: 2 · P1.4: 1 compound (5 conditions) · goal anchor: 2).

## The Verdict

**SHIP-AMENDED — 14 amendments.** The Phase-1 half of the plan (goal anchor, process layer v2, P1.1–P1.4) is approved **with** the amendments above; the execution order stands (fix-then-extract is the right decomposition — the ~33 fixable rows are near-free and shrink the 51-GPU-h extraction surface). No amendment widens scope or breaks a standing rule: baseline-exact, the one-copy GPU rule, and the shrunk council trigger are all preserved. The process layer v2 is sound (R-7 no-council is safe — 61 keys verified; R-6 no-council is amended, not broken, by A7). What is *not* approved: P1.1 as written (it lacks its own preconditions — A1–A5) and P1.3/P1.4 as written (A10–A12). The approval attaches to plan blob `840d413088d448abb7a1099aab81897443061455`; the amendments are applied to the plan file and the new blob is re-pinned at C3. The full Phase-2 goal-noun debate stays with the Phase-2 council.

## The One Thing to Do First

**Run the model-free P1.1 step-0 pass, then — and only then — the ordered 100k switch.** Concretely: (1) rebuild the lost `/tmp/csm_iter1_records/` artifacts model-free from work_log 06:49:04/06:49:42 + the on-disk receipts (C1/C2 commit messages, the R-5 brief, the Part-A panel rows + hash — A3); (2) zero-GPU baseline re-verify on the current dirty tree (pytest collect = 1,305 + span-recall offline 48,572/48,572 + red-list recount — A2); (3) then execute A1 in order: SWITCHPOINT checkpoint (committed in C3) → `qwen-switch.sh 100k` → `pi_restart.sh` → bring up the CUDA `:8000` with a named redeployer and the abort branch. Nothing else moves until step 3 is green.

## Ledger entry

Exact line for row #25 of `reports/comprehension/COUNCIL_HISTORY.md` (the orchestrator appends; this council did not touch the ledger; row #24 = the session-audit council, #23 remains reserved for the R-2+R-3 council in the staged package):

```
| 25 | `reports/csm/COUNCIL_csm_p1_plan.md` (CSM campaign; artifacts `reports/csm/receipts/council_p1_plan/` — 5 advisors A–E + 5 peer reviews + chairman) | csm-p1-plan (2026-09-09): 11-member council (5 advisors + 5 reviewers in parallel per owner 23:2x + chairman) — verdict: **SHIP-AMENDED (14 amendments)** on `plan/CSM_2PHASE_PLAN.md` v2 Phase-1 half (goal anchor + process layer v2 + P1.1–P1.4), version-pinned at blob `840d413`. P1.1 not executable as written: the 262k→100k switch is an unlisted precondition (qwen_mode.txt = 262k / free 1,606 MiB / api=off — no CUDA `:8000` as-is) → ordered step: SWITCHPOINT checkpoint → qwen-switch.sh 100k → pi_restart → CUDA `:8000` with named redeployer + abort branch; `/tmp/csm_iter1_records` lost in the reboot → model-free rebuild pass (C1/C2 messages, R-5 brief, Part-A rows+hash from work_log 06:49:04/06:49:42) + zero-GPU baseline re-verify (pytest collect 1,305 + span-recall offline) as P1.1 step 0; add C3 doc-hygiene commit (CLAUDE.md JJK-D6/150k-mode/1,254-suite lines, WAVE2 §1 f93d396, untracked receipts dirs) with path-limited git adds, `git add .` banned (dirty tree 15 M + 17 ?? incl. `E:\…`, `sample scripts/`, stale `STOP`); `reports/csm/GATE.md` skeleton. P1.2: split the 90-min draft (R-5 core only; R-6/R-7 separate short no-council passes) + pre-register the R-6 floor-inheritance question (council_r2r3/chairman.md:43) in the R-5 council brief + define own-new-row HIT + optional cross-corpus spot-pins. P1.3: queue math corrected to 58 = 33 fixable (30 open + 3 closed by R-1) + 22 floor + 3 stamped; #21 R3 halt scoping stated in prose (meter counts only the 33 fixable). P1.4: close conditions add campaign-todos sync, C3, GATE.md, the P2.2 model-free bar-audit pull-in (pre-PHASE_A_COMPLETE), and the R-6 verdict recorded. Goal anchor: D1 vacuity note (CSM roster census = 11, not 100) + P2.3 contingency flag (full P2 debate deferred to the Phase-2 council). Method: 5 advisors parallel + 5 reviewers parallel + chairman (owner 2026-09-09 23:2x, superseding the sequential convention for this council); all 11 zero-GPU/read-only/fresh-context. |
```