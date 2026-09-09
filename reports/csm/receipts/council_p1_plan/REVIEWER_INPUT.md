# Peer-review input (anonymized) — Phase-1 plan council

## The question

## The decision

Approve / amend / reject **Phase 1 of `plan/CSM_2PHASE_PLAN.md` (v2,
2026-09-09)** — i.e. the goal anchor, the process layer v2, and steps
P1.1–P1.4. Remember the goal: CSM at full D1–D6 comprehension; 100 % = the
checkable D1–D10 done-set + a triage log for every residual, never "100 %"
prose; CSM is the P6 successor to JJK's 09-07 done-declaration; halt before
P6.

## Scope questions (answer all)

1. **Goal anchor:** is the D1–D10 done-set (as tabulated in the plan) the
   right and complete definition of 100 % — and does Phase 1 honestly state
   what it certifies vs what only Phase 2 can (the 22 extraction-gated
   floors; the missing comprehension layer)?
2. **Process layer v2 (7 rulings):** does any ruling break the
   baseline-exact invariant (four gates after every engine change), the
   one-copy GPU rule, or an owner standing rule? Is the shrunk council
   trigger (R-5 class / phase close / P6; pre-registered items no-council)
   right — or does R-6/R-7 "no-council" hide an open design question
   (the R-6 floor-inheritance note in the R-2+R-3 council record)?
3. **P1.1:** the 262k → 100k switch precondition + the four gate legs +
   the selective 2-commit (C1/C2) + ledger-of-record v1. Executable as
   written? (The `/tmp/csm_iter1_records` staging was lost in the reboot;
   the 9-file package is uncommitted on disk; `git status` shows a dirty
   tree one `git add .` away from an "atomic" commit.)
4. **P1.2:** the R-5 relations-mode wave (90-min-or-split draft → B grades
   → §3 council → four gates → R5-meter re-sweep → auto-commit) with
   R-6/R-7 folded in. Right order, right cost, right meter (≥ 1
   own-new-row HIT or halt)?
5. **P1.3:** the halt meter — correctly scoped so the 22 never-reducing
   floor rows do NOT trip "two no-reduction iterations" (council #21 R3:
   the halt rule counts only Phase-1-fixable classes)?
6. **P1.4:** the unit-4 close conditions (one-copy four gates + 34 s 5.4
   re-adjudication + pre-registered extraction-pass test shape +
   `coverage_report.py` + `PHASE_A_COMPLETE <ts>`) — complete, or missing
   a condition (e.g. the campaign-todos sync, the doc-hygiene fixes, the
   A/B monitor gap patches)?

## Grounding (verify before you record)

## The three review questions (answer all, max 200 words total)

1. Which response (A-E) is the strongest, and why?
2. What is the single biggest blind spot the five responses SHARE?
3. What did all five miss that you would have added?

## Response A



Executed P1.1–P1.4 on paper against the machine state.
Executed P1.1–P1.4 on paper against the machine state.


**P1.1 not executable as written — four missing preconditions.** (1) The
**P1.1 not executable as written — four missing preconditions.** (1) The
switch is not a step: qwen_mode.txt reads mode=262k, free_mib=1606, api=off —
switch is not a step: qwen_mode.txt reads mode=262k, free_mib=1606, api=off —
a CUDA `:8000` (~7 GB) is impossible as-is. Order: SWITCHPOINT checkpoint
a CUDA `:8000` (~7 GB) is impossible as-is. Order: SWITCHPOINT checkpoint
(exists) → `qwen-switch.sh 100k --force` → `pi_restart.sh` → bring up the
(exists) → `qwen-switch.sh 100k --force` → `pi_restart.sh` → bring up the
CUDA `:8000` (no bay exists post-reboot; P1.1 names no one to do it).
CUDA `:8000` (no bay exists post-reboot; P1.1 names no one to do it).
(2) `/tmp/csm_iter1_records/` gone (verified): C1/C2 messages + R-5 brief
(2) `/tmp/csm_iter1_records/` gone (verified): C1/C2 messages + R-5 brief
lost, but reconstructable model-free from work_log 06:49:04/06:49:42 — an
lost, but reconstructable model-free from work_log 06:49:04/06:49:42 — an
unlisted ~30-min rebuild pass. (3) R-2 Part-A panel: owner item 4 never
unlisted ~30-min rebuild pass. (3) R-2 Part-A panel: owner item 4 never
marked DONE and /tmp died — P1.1's "pre-built rows + hash" is false;
marked DONE and /tmp died — P1.1's "pre-built rows + hash" is false;
rebuild before the CUDA probe. (4) Monitor-gap patches deferred "before
rebuild before the CUDA probe. (4) Monitor-gap patches deferred "before
Phase 2" — the stale-ESC hazard that voided the last gate-3 window stays
Phase 2" — the stale-ESC hazard that voided the last gate-3 window stays
live through P1.1 if a bay is used; no bay, gap moot.
live through P1.1 if a bay is used; no bay, gap moot.


The 9-file package is intact (git status). The dirty tree (15 modified + 15
The 9-file package is intact (git status). The dirty tree (15 modified + 15
untracked, incl. `E:\Personal\Plot Works/`, `sample scripts/`, stale `STOP`)
untracked, incl. `E:\Personal\Plot Works/`, `sample scripts/`, stale `STOP`)
is one `git add .` from contamination, and C1/C2 cover neither the
is one `git add .` from contamination, and C1/C2 cover neither the
plan/SWITCHPOINT/decisions/index/a_wake_log files nor the R-7 doc-hygiene
plan/SWITCHPOINT/decisions/index/a_wake_log files nor the R-7 doc-hygiene
targets (CLAUDE.md, CSM_WAVE2_RESUME — unmodified on disk): add a C3.
targets (CLAUDE.md, CSM_WAVE2_RESUME — unmodified on disk): add a C3.


**P1.2** executable; its brief (lost `r5_class_plan.md`) survives verbatim in
**P1.2** executable; its brief (lost `r5_class_plan.md`) survives verbatim in
work_log. Add the R-6 floor-inheritance question to the R-5 council brief so
work_log. Add the R-6 floor-inheritance question to the R-5 council brief so
"no-council" doesn't hide it. **P1.3:** the meter as written counts the
"no-council" doesn't hide it. **P1.3:** the meter as written counts the
whole 58-row queue (verified 33 fixable / 22 floor / 3 stamped); the 22
whole 58-row queue (verified 33 fixable / 22 floor / 3 stamped); the 22
floors never reduce, so a global meter halts on iteration 1 — carry #21 R3's
floors never reduce, so a global meter halts on iteration 1 — carry #21 R3's
scoping in one sentence: count only the 33 fixable. **P1.4** missing:
scoping in one sentence: count only the 33 fixable. **P1.4** missing:
campaign-todos sync (done-criterion only), the doc-hygiene commit, a
campaign-todos sync (done-criterion only), the doc-hygiene commit, a
`reports/csm/GATE.md` skeleton (does not exist; P2.1's receipts need it),
`reports/csm/GATE.md` skeleton (does not exist; P2.1's receipts need it),
ledger row #23 (reserved, unwritten — `reports/comprehension/
ledger row #23 (reserved, unwritten — `reports/comprehension/
COUNCIL_HISTORY.md`).
COUNCIL_HISTORY.md`).


**Single first move:** model-free rebuild pass (C1/C2 lists, R-5 brief,
**Single first move:** model-free rebuild pass (C1/C2 lists, R-5 brief,
Part-A rows+hash) → checkpoint → 100k switch → CUDA `:8000` → gate legs.
Part-A rows+hash) → checkpoint → 100k switch → CUDA `:8000` → gate legs.
**Phase-1 done, machine-level:** CSM paths git-clean (C1+C2+C3+ledger-of-
**Phase-1 done, machine-level:** CSM paths git-clean (C1+C2+C3+ledger-of-
record v1); `PHASE_A_COMPLETE <ts>` in `reports/master-work/phase_status.txt`
record v1); `PHASE_A_COMPLETE <ts>` in `reports/master-work/phase_status.txt`
(does not exist yet); miss queue = 33 fixable green + 22 floor + 3 stamped
(does not exist yet); miss queue = 33 fixable green + 22 floor + 3 stamped
documented; red list synced; qwen_mode.txt mode=100k, `:8000` down/CPU.
documented; red list synced; qwen_mode.txt mode=100k, `:8000` down/CPU.
## Response B



**Q1:** D1–D10 is a reachability proxy the plan admits only partly: D5 is met *vacuously* (`placement_audit_csm.json`: 0 events, "bar MET" on zero data; events exist only post-P2.3). P2.2 concedes the done-set "is a reachability proxy until a bar audit proves it transfers," but the P1.4 marker mentions only the 22-floor gap.
**Q1:** D1–D10 is a reachability proxy the plan admits only partly: D5 is met *vacuously* (`placement_audit_csm.json`: 0 events, "bar MET" on zero data; events exist only post-P2.3). P2.2 concedes the done-set "is a reachability proxy until a bar audit proves it transfers," but the P1.4 marker mentions only the 22-floor gap.


**Q2:** R-7 no-council safe (61 keys, verified); R-6 no-council hides a live design question (`council_r2r3/chairman.md:43`: "floor-inheritance question … recorded for R-6 drafting"). P1.3's halt-council is also absent from the shrunk trigger list (R-5 / close / P6 only).
**Q2:** R-7 no-council safe (61 keys, verified); R-6 no-council hides a live design question (`council_r2r3/chairman.md:43`: "floor-inheritance question … recorded for R-6 drafting"). P1.3's halt-council is also absent from the shrunk trigger list (R-5 / close / P6 only).


**Q3:** Not executable as written: `/tmp/csm_iter1_records` is gone (verified) — C1/C2 messages, R-5 brief, Part-A panel lost; work_log shows DONE only for items 1–2, so the "pre-built" Part-A panel P1.1 assumes is not on disk. The tree is 32 entries (`E:\Personal\Plot Works/`, `sample scripts/`, stale `STOP`) — one `git add .` from polluting the "atomic" commit. Unlisted preconditions: staging rebuild, bay redeploy. Ledger v1 lands *with* C1, so P1.1 still runs on the fragile /tmp mechanism it retires.
**Q3:** Not executable as written: `/tmp/csm_iter1_records` is gone (verified) — C1/C2 messages, R-5 brief, Part-A panel lost; work_log shows DONE only for items 1–2, so the "pre-built" Part-A panel P1.1 assumes is not on disk. The tree is 32 entries (`E:\Personal\Plot Works/`, `sample scripts/`, stale `STOP`) — one `git add .` from polluting the "atomic" commit. Unlisted preconditions: staging rebuild, bay redeploy. Ledger v1 lands *with* C1, so P1.1 still runs on the fragile /tmp mechanism it retires.


**Q4:** Order and meter (≥1 own-new-row) right; but the 90-min draft bundles relations mode + builder + R-6 + R-7 off a lost brief, after two workers died at 60 min — the timeout incident class re-triggers here first.
**Q4:** Order and meter (≥1 own-new-row) right; but the 90-min draft bundles relations mode + builder + R-6 + R-7 off a lost brief, after two workers died at 60 min — the timeout incident class re-triggers here first.


**Q5:** Meter underscoped: #21 R3 (verified, `COUNCIL_unit3_sweep.md:42`) scopes the halt to Phase-1-fixable classes; P1.3 omits that — "two no-reduction iterations" over the full 58-row queue trips on the 22 never-reducing floors, halting mid-phase into a council the trigger list doesn't authorize.
**Q5:** Meter underscoped: #21 R3 (verified, `COUNCIL_unit3_sweep.md:42`) scopes the halt to Phase-1-fixable classes; P1.3 omits that — "two no-reduction iterations" over the full 58-row queue trips on the 22 never-reducing floors, halting mid-phase into a council the trigger list doesn't authorize.


**Q6:** Missing: the doc hygiene (CLAUDE.md unmodified, still "JJK D6 active"; `CSM_WAVE2_RESUME.md` §1 CSM-3 = `bc73795`, git log proves `f93d396`) is in neither C1/C2 nor P1.4; the monitor gap patch (stale-ESC hazard) is deferred to "before Phase 2," staying live through all of Phase 1. Campaign-todos sync is covered by the done-criterion.
**Q6:** Missing: the doc hygiene (CLAUDE.md unmodified, still "JJK D6 active"; `CSM_WAVE2_RESUME.md` §1 CSM-3 = `bc73795`, git log proves `f93d396`) is in neither C1/C2 nor P1.4; the monitor gap patch (stale-ESC hazard) is deferred to "before Phase 2," staying live through all of Phase 1. Campaign-todos sync is covered by the done-criterion.
## Response C



**The plan certifies the wrong noun.** The owner's question is CSM *comprehension* (D1–D6); the D1–D10 set is JJK's *reachability* done-set, copied verbatim into the goal anchor. It is mis-shaped for CSM in two verified ways: (a) D1's "100 frozen enumeration questions" transfers vacuously — CSM's roster census is 11 questions (`census_roster_100_csm.json`, verified on disk); (b) D3/D9 are JJK gate counts, not CSM measures. The plan concedes: "the done-set is a reachability proxy until a bar audit proves it transfers" (plan line 138).
**The plan certifies the wrong noun.** The owner's question is CSM *comprehension* (D1–D6); the D1–D10 set is JJK's *reachability* done-set, copied verbatim into the goal anchor. It is mis-shaped for CSM in two verified ways: (a) D1's "100 frozen enumeration questions" transfers vacuously — CSM's roster census is 11 questions (`census_roster_100_csm.json`, verified on disk); (b) D3/D9 are JJK gate counts, not CSM measures. The plan concedes: "the done-set is a reachability proxy until a bar audit proves it transfers" (plan line 138).


**Q1:** Phase 1 certifies reachability of what the wiki already says, not comprehension. The hole: the sole comprehension step, P2.3 extraction (events + meaning layer), is "contingent per the council-#19 P4 ruling" (line 145) — if it doesn't fire, the done-set closes and the owner's question is answered by triage-log lines, not understanding. Fix: make P2.3 non-contingent, or add a numbered comprehension item to D6.
**Q1:** Phase 1 certifies reachability of what the wiki already says, not comprehension. The hole: the sole comprehension step, P2.3 extraction (events + meaning layer), is "contingent per the council-#19 P4 ruling" (line 145) — if it doesn't fire, the done-set closes and the owner's question is answered by triage-log lines, not understanding. Fix: make P2.3 non-contingent, or add a numbered comprehension item to D6.


**Fix-then-extract is the right decomposition (Q4):** extraction ≈ 51 GPU-h; the ~30 fixable rows are near-free; fixing first shrinks the extraction surface.
**Fix-then-extract is the right decomposition (Q4):** extraction ≈ 51 GPU-h; the ~30 fixable rows are near-free; fixing first shrinks the extraction surface.


**The one misplacement:** P2.2's bar audit — the only step testing whether the D-set is the right bar for CSM's 17,181 short panel lines (17,181 rows, min_words 6, verified; ≈ 35 % of JJK's 48,572) — sits *after* P2.1's 51-GPU-h panel. It is cheap and model-free (3–5 pre-registered cases per D6 dimension). Move it into P1.4's close or gate P2.1 on it.
**The one misplacement:** P2.2's bar audit — the only step testing whether the D-set is the right bar for CSM's 17,181 short panel lines (17,181 rows, min_words 6, verified; ≈ 35 % of JJK's 48,572) — sits *after* P2.1's 51-GPU-h panel. It is cheap and model-free (3–5 pre-registered cases per D6 dimension). Move it into P1.4's close or gate P2.1 on it.


**Q2/Q3/Q5/Q6:** no process-layer break (council shrink, auto-commit, baseline-exact all preserve the invariants). Two text amendments: carry council-#21 R3 scoping into P1.3's prose (the halt rule counts only Phase-1-fixable classes, or the 22 never-reducing floors halt iteration one), and add the bar-audit verdict to P1.4's close conditions.
**Q2/Q3/Q5/Q6:** no process-layer break (council shrink, auto-commit, baseline-exact all preserve the invariants). Two text amendments: carry council-#21 R3 scoping into P1.3's prose (the halt rule counts only Phase-1-fixable classes, or the 22 never-reducing floors halt iteration one), and add the bar-audit verdict to P1.4's close conditions.


**Verdict: AMEND.** The execution order is right; the goal anchor's noun and one sequence item are wrong.
**Verdict: AMEND.** The execution order is right; the goal anchor's noun and one sequence item are wrong.
## Response D



**Q1:** D1–D10 table is self-contained — good. But D1's "100 enumeration questions" transfers vacuously (CSM roster census = 11; the plan doesn't note it). The 22-floor honesty holds.
**Q1:** D1–D10 table is self-contained — good. But D1's "100 enumeration questions" transfers vacuously (CSM roster census = 11; the plan doesn't note it). The 22-floor honesty holds.


**Q2:** Baseline-exact inlines the gate values — good. But R-6/R-7 "no-council" hides an open design question (R-6 floor-inheritance, verified open in `council_r2r3/chairman.md:43` + work_log) the plan folds into a "no-council lever" without pointing at that record.
**Q2:** Baseline-exact inlines the gate values — good. But R-6/R-7 "no-council" hides an open design question (R-6 floor-inheritance, verified open in `council_r2r3/chairman.md:43` + work_log) the plan folds into a "no-council lever" without pointing at that record.


**Q3:** Not executable as written. "Seed-7" unexplained (span_recall.py's 400-sample default; no pointer). "One-copy" used 3×, defined nowhere. Queue math wrong: plan says 58 rows "~30 fixable / 22 floors"; on-disk (verified) = 33 fixable + 3 stamped + 22 floor. P1.1 assumes a "pre-built" R-2 Part-A panel — no such file exists (work_log item 4 never DONE); `/tmp/csm_iter1_records` gone (verified).
**Q3:** Not executable as written. "Seed-7" unexplained (span_recall.py's 400-sample default; no pointer). "One-copy" used 3×, defined nowhere. Queue math wrong: plan says 58 rows "~30 fixable / 22 floors"; on-disk (verified) = 33 fixable + 3 stamped + 22 floor. P1.1 assumes a "pre-built" R-2 Part-A panel — no such file exists (work_log item 4 never DONE); `/tmp/csm_iter1_records` gone (verified).


**Q4:** The "own-new-row HIT" halt condition is undefined in every document (grep: used in plan, council record, work_log; defined nowhere). 90 min for a 4th router mode + new bundle builder + 2 hooks + 61-key override is over-scoped.
**Q4:** The "own-new-row HIT" halt condition is undefined in every document (grep: used in plan, council record, work_log; defined nowhere). 90 min for a 4th router mode + new bundle builder + 2 hooks + 61-key override is over-scoped.


**Q5:** As written, the meter trips itself: "halt on two no-reduction iterations" + 22 never-reducing floors in the same queue → a literal reading halts iteration 1. The plan relies on council #21 R3 scoping (fixable classes only) but never states it in P1.3.
**Q5:** As written, the meter trips itself: "halt on two no-reduction iterations" + 22 never-reducing floors in the same queue → a literal reading halts iteration 1. The plan relies on council #21 R3 scoping (fixable classes only) but never states it in P1.3.


**Q6:** "5.4" in "34 s 5.4 re-adjudication" is a section label (CSM_WAVE2_RESUME §5.4) the plan never points at. R-4 defers the monitor patch to Phase 2, but the stale-ESC hazard that voided the last gate-3 window stays live through P1.1.
**Q6:** "5.4" in "34 s 5.4 re-adjudication" is a section label (CSM_WAVE2_RESUME §5.4) the plan never points at. R-4 defers the monitor patch to Phase 2, but the stale-ESC hazard that voided the last gate-3 window stays live through P1.1.


**Cross-cutting:** council citations are ledger-numbers only ("#21 R3") with no paths, though records exist under `reports/csm/`. Dial contradiction: CLAUDE.md's "150k Phase-1 mode" vs the plan's "262k → 100k" — qwen_mode.txt = 262k now (verified), so the switch is right; but the stale 150k line and CLAUDE.md's "1,254" suite count vs the plan's 1,303+2xp are absent from the hygiene list.
**Cross-cutting:** council citations are ledger-numbers only ("#21 R3") with no paths, though records exist under `reports/csm/`. Dial contradiction: CLAUDE.md's "150k Phase-1 mode" vs the plan's "262k → 100k" — qwen_mode.txt = 262k now (verified), so the switch is right; but the stale 150k line and CLAUDE.md's "1,254" suite count vs the plan's 1,303+2xp are absent from the hygiene list.
## Response E



**Q1 Goal anchor:** D1–D10 is the right Phase-1 boundary, but D4 is undervalued:
**Q1 Goal anchor:** D1–D10 is the right Phase-1 boundary, but D4 is undervalued:
its frozen sets + pilot numbers seed the P6 runbook; the plan leaves the
its frozen sets + pilot numbers seed the P6 runbook; the plan leaves the
seven-sibling freeze on the table.
seven-sibling freeze on the table.


**Q2 Process v2:** shrunk triggers are upside, not risk: no-council checklists
**Q2 Process v2:** shrunk triggers are upside, not risk: no-council checklists
keep waves fast to pull P2.2/P2.4 forward (Q6). Flag: R-6 hides the
keep waves fast to pull P2.2/P2.4 forward (Q6). Flag: R-6 hides the
floor-inheritance design question — pre-register it.
floor-inheritance design question — pre-register it.


**Q3 P1.1:** executable (9-file package intact). Bigger: census tools are
**Q3 P1.1:** executable (9-file package intact). Bigger: census tools are
already series-parameterized (`--series` default jjk, byte-identical legacy
already series-parameterized (`--series` default jjk, byte-identical legacy
path — `tools/census_dimensions.py:137`, `census_doors.py:334`) and all eight
path — `tools/census_dimensions.py:137`, `census_doors.py:334`) and all eight
corpora have facts.db. Add a C2 addendum: one-copy census sweep over the other
corpora have facts.db. Add a C2 addendum: one-copy census sweep over the other
seven corpora (CSM's: 34 s + 18 s) — P6 becomes dial + sweep, not discovery.
seven corpora (CSM's: 34 s + 18 s) — P6 becomes dial + sweep, not discovery.


**Q4 P1.2:** order/cost/meter (≥ 1 own-new-row HIT or halt) right. Bigger: R-5
**Q4 P1.2:** order/cost/meter (≥ 1 own-new-row HIT or halt) right. Bigger: R-5
is a series-agnostic 4th router mode (`router.py:55` holds 3 today) but the
is a series-agnostic 4th router mode (`router.py:55` holds 3 today) but the
plan only re-sweeps CSM. The dead-door shape (relations capped at 20 rows as
plan only re-sweeps CSM. The dead-door shape (relations capped at 20 rows as
a qa side channel, `api/context.py:579`; 11,261 cross-doc CSM edges) exists on
a qa side channel, `api/context.py:579`; 11,261 cross-doc CSM edges) exists on
every wiki with a relations table. Register cross-corpus spot-pins (2–3
every wiki with a relations table. Register cross-corpus spot-pins (2–3
phrasings per corpus, model-free) so P6 starts with 8-corpus
phrasings per corpus, model-free) so P6 starts with 8-corpus
router coverage proven.
router coverage proven.


**Q5 P1.3:** correctly scoped: the 22 floors don't count (council #21 R3, plan
**Q5 P1.3:** correctly scoped: the 22 floors don't count (council #21 R3, plan
+ work_log verified). Upside: that list is P2.3's pre-triaged extraction
+ work_log verified). Upside: that list is P2.3's pre-triaged extraction
manifest; stamp it.
manifest; stamp it.


**Q6 P1.4:** incomplete: the done-set is a reachability proxy until a bar audit
**Q6 P1.4:** incomplete: the done-set is a reachability proxy until a bar audit
proves transfer (plan:138). Pull P2.4's writer-leg probe (script-gen +
proves transfer (plan:138). Pull P2.4's writer-leg probe (script-gen +
verify on CSM) and P2.2's 3–5 pre-registered bar-audit cases into P1.4 — 51
verify on CSM) and P2.2's 3–5 pre-registered bar-audit cases into P1.4 — 51
GPU-h of P2 should not invalidate the Phase-1 done-set; PHASE_A_COMPLETE
GPU-h of P2 should not invalidate the Phase-1 done-set; PHASE_A_COMPLETE
carries the writer-leg result.
carries the writer-leg result.


**Done-declaration as template:** `DONE_DECLARATION.md` (verified) is the P2.5
**Done-declaration as template:** `DONE_DECLARATION.md` (verified) is the P2.5
template — instantiate its D1–D10 checklist for all eight corpora now (census
template — instantiate its D1–D10 checklist for all eight corpora now (census
red-class floors filled where sweeps ran) so future runs are fill-ins, not
red-class floors filled where sweeps ran) so future runs are fill-ins, not
authoring.
authoring.