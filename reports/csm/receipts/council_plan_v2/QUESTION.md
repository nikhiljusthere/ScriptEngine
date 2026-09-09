# Council question — plan-approval for CSM 100% two-phase plan v2 (2026-09-09)

**Framed by the owner:** "Make the plan for both phases again, run an LLM
council on that plan, then finalize it. Remember what our goal is and what
100 % means for us."

## The decision

Approve / amend / reject `plan/CSM_2PHASE_PLAN.md` (v2, 2026-09-09) — the
regenerated two-phase execution plan for the CSM 100 % campaign. Answer, in
order:

1. **Is the goal anchor right?** The plan opens with: goal = CSM at full
   D1–D6 comprehension (the P6 successor to JJK's 09-07 done-declaration,
   halt before P6); 100 % = the checkable D1–D10 done-set (D1 roster census
   ≥ 99 % · D2 narrative census ≥ 99 % · D3 reachability tiers · D4
   preconditions recorded · D5 placement-gate audit · D6 all non-ideal
   results triaged · D7 no door-less table · D8 contingent builds · D9
   standing gates green · D10 halt) + a triage log for every residual,
   never "100 %" prose. Is that the right and complete definition for CSM
   (does anything from the JJK done-declaration not transfer, or transfer
   wrongly)?
2. **Is the decomposition right?** Phase 1 (rest of §9a iteration 1: P1.1
   gate legs + commit → P1.2 R-5 relations-mode wave with R-6/R-7 folded
   no-council → P1.3 halt-meter convergence → P1.4 unit-4 close) at the
   100k dial with a single 262k→100k switch; Phase 2 (P2.1 CSM-4 exhaustive
   tier-1 × 3 doors pre-extraction control arm ≈ 51 GPU-h → P2.2 bar audit →
   P2.3 D6 extraction only on the red class → P2.4 writer-facing acceptance
   leg → P2.5 CSM-8 done-declaration, halt before P6). Is the phase
   boundary, step order, halt meter, and each done-criterion right?
3. **Are the process-layer changes right?** (council #24 rulings now in
   the plan: councils only at R-5 / phase-close / P6, pre-registered items
   no-council; 90-min-or-split worker timeout; gate-green ⇒ auto-commit +
   one machine-readable ledger-of-record; A/B bay kept + 2 gap patches;
   2-parallel drafting + shared verification; the invariant renamed
   "baseline-exact" with the four pinned gate numbers; doc-hygiene fixes
   in this commit.) Any that would break the JJK-100 % invariant, the
   one-copy rule, or the owner's standing rules?
4. **Costs & schedule:** P1 ≈ 2–3 days, Phase 2 ≈ 2 GPU-days, total
   ≈ 1.5–2 weeks; "100 %" unreachable in Phase 1 (22 extraction-gated
   floors). Right, or is a step missing/over-costed?

## Grounding (verify before you record)

- The plan itself: `plan/CSM_2PHASE_PLAN.md` (v2 — read it in full first)
- JJK done-declaration (the 100 % template): `reports/comprehension/DONE_DECLARATION.md`
  (D1–D10 item-by-item + triage log) + `reports/comprehension/GATE.md`
  (~line 697: "done-set D1–D10 all hold — the terminal state is done")
- The campaign's live state + receipts: `reports/csm/SESSIONS_REVIEW_2026-09-09.md`
  + `reports/master-work/work_log.md` (tail) + `reports/csm/miss_queue_csm_iter1.jsonl`
  (58 rows) + `reports/csm/red_list_csm.md`
- The process rulings being inherited: `reports/csm/COUNCIL_csm_session_audit.md`
  (ledger #24) + `reports/csm/COUNCIL_unit3_sweep.md` (ledger #21: the
  C-deferred-panel + halt-meter + pre-extraction-control-arm rulings) +
  `plan/CSM_WAVE2_RESUME.md` (invariants + the §3 trigger the v2 shrinks)
- Gate baselines: the R-2+R-3 gate run lines in `reports/master-work/work_log.md`
  (pytest 1,303+2xp / eval 31/31 / 48,572 / 236/236 @ 79.0 %)
- git: `git log --oneline -10` (the R-1 commits b84445f/aef6707; the
  uncommitted 9-file R-2/R-3 package = `git status --short`)

## Rules for every member

Zero-GPU, read-only (you may write ONLY your assigned output file), every
load-bearing claim verified against disk before you record it (if you cannot
verify it, say so — never assume). One agent at a time (owner rule
2026-09-08).