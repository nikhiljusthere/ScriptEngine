# COUNCIL_p21_post_sweep — the post-P2.1-sweep decision (2026-09-17)

Council #31, sequential one-agent-at-a-time (owner rule 2026-09-08): 5 advisors
→ 5 reviewers (blind to advisor labels) → chairman. Every agent a fresh
context; no shared transcript. Mapping: A=Executor, B=Contrarian,
C=Expansionist, D=First-Principles, E=Outsider.

**Inputs (all on disk):** `reports/csm/p21_sweep_2026-09-17/REPORT.md`
(qa 98.48 % / narrative 10.74 % / roster 0.77 % / auto 15.43 %, heldout
14.0 %; 89.1 % of line lookups routed to narrative; 237 both-misses; the 261
qa misses pre-binned), `reports/csm/GATE.md` (A17 floor policy, R-8 landing,
the R-8 "second misroute — recorded, not yet labelled" note),
`plan/CSM_2PHASE_PLAN.md` §P2.2–P2.5, `reports/master-work/PHASE2_JOB.md`.

## Questions put to the council

1. What is auto 15.43 % — a gate, a bar, or a description?
2. When and on which door is the P2.2 bar audit graded?
3. Is R-9 (the second misroute) pre-committed or evidence-gated?
4. What residual triage does `PHASE_B_COMPLETE` actually require — and is it
   reachable by construction?
5. Is the widened census bank (486) usable as-is for P2.3, or re-authored?

## Consensus (chairman)

1. **Auto 15.43 % is not a gate number on this panel.** The panel is verbatim
   line-lookup probes: clearing 97.5 % would require ~99.7 % of probes routed
   to qa (a constant-function router), and even a perfect router tops out at
   ~98.62 % (237 lines miss on both doors). 15.43 % (panel) / 14.0 % (heldout)
   is reported as the descriptive raw of the product path on a probe class it
   is not designed for. If a bar is ever set on the auto door it is set on the
   heldout (A24 out-of-sample), never on the panel. B: "you cannot gate on a
   number the question class cannot clear"; D: the ceiling arithmetic; A: it
   matches the pre-sweep A17 scope caveat (GATE.md, "Scope caveat").
2. **P2.2 is owed before `PHASE_B_COMPLETE`; grade it pre-fix, on the qa
   control arm.** The pre-registration's "panel 400-gate control arm" is JJK
   3b's in-process qa door (`tools/census_dimensions_csm_v2_grade.py` pattern);
   an auto-door pass is recorded alongside as the R-9-contingent supplement.
   The grade measures comprehension on the pre-fix tree; a post-fix delta is
   R-9's evidence, not the audit's verdict. B: auto-only grading would
   conflate the audit with the router defect; E: the 25/26 `a7_dimension_check`
   hit on qa is promising but is not the mechanical judge — the term-based
   judge needs the served bundle text, so it gets a grader, not a ledger
   lookup.
3. **R-9 is deferred, not pre-committed.** Pre-registered firing condition:
   the P2.4 writer leg + the P2.3 census verdict show writer-shaped questions
   misrouting (not just line lookups). Before any series-agnostic
   `router.py` change (which owes the four gates + the JJK regression debt),
   check the per-wiki route in `series/csm/overrides.yaml`: a CSM-only routing
   override is a smaller diff on the CSM side and keeps the JJK baseline
   untouched. A: cheapest route first; B: no pre-committed engine change on a
   probe class; C: keep the writer-shaped bar on the table as the alternative
   that retires R-9 entirely.
4. **The `PHASE_B_COMPLETE` residual scope is pre-registered now** — the
   construction blocker was that "a triage log for every residual" literally
   covers ~32.4k narrative/roster floor residuals, making the done-declaration
   unreachable by construction. Pre-registered scope: full class + reason for
   the qa 261 (237 both-misses first), the 24 auto-only, and the 26 bar-audit
   lines; narrative/roster floors closed by the complete histogram
   (`residuals_by_type.json`) + a first-5-per-cell sample with a
   deterministic class/reason (the floor's class is structural, not judged).
   D: the unscoped obligation was the blocker; E: histogram + sample is what
   JJK's own floor closure actually did.
5. **The widened census bank is writer-shaped as-is** — all 486 items carry
   `q`/`expect` (v1 60 + v2 50 verbatim; the 376 ability-pool items are
   writer questions, `build_census_widened.py` docstring). P2.3 is a pointer:
   a grader reusing the v2 grader's in-process pattern pointed at the widened
   bank. No re-authoring. C: the ability pool is the Q1/Q2 breadth; E: the
   v2 grader is the template.

## Pre-registrations (binding for the phase)

- **P-1** auto door: descriptive raw only, no panel bar; any future bar is set
  on the heldout (14.0 %).
- **P-2** P2.2: qa control-arm grade (pre-fix, in-process CUDA) + auto
  supplement; verdict R-9-contingent; grader `tools/csm/p23_grader.py`.
- **P-3** R-9: deferred; fires only on writer-shaped misroute evidence
  (P2.4 + P2.3); check `series/csm/overrides.yaml` before any `router.py`
  change.
- **P-4** residual scope per consensus 4; builder
  `tools/csm/p23_triage_inputs.py`, outputs under
  `p21_sweep_2026-09-17/triage/`.
- **P-5** P2.3 = the pointer grader over `census_widened_csm.json` (486),
  in-process CUDA on the whole card (Qwen down); fires in the model-unloaded
  handoff `reports/master-work/P23_HANDOFF.md` (the 26 bar-audit cases ride
  the same batch, both doors).

## Deferred (owner-return session, Qwen up)

P2.4 writer leg (one `script-gen` + `cli verify` on CSM) → the
R-9-vs-writer-bar evidence call (council or owner, per the trigger rules) →
residual triage sign-off (P-4) → `PHASE_B_COMPLETE`
(`plan/CSM_2PHASE_PLAN.md` §P2.5 checklist + P-4 scope).