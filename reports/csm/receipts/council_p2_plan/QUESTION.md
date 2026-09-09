# Council question — Phase-2 plan approval (2026-09-09)

**Owner instruction (23:2x):** phase-scoped councils, 5 advisors run IN
PARALLEL per phase; the Phase-1 council already fixed the Phase-1 half of
the plan. This council approves / amends / rejects **Phase 2 of
`plan/CSM_2PHASE_PLAN.md` (v2)** — steps P2.1–P2.5, the cost & schedule
section, and the phase boundary (what must be true before Phase 2 may
start). Remember the goal: CSM at full D1–D6 comprehension; 100 % = the
checkable D1–D10 done-set + a triage log for every residual, never "100 %"
prose; halt before P6.

## The decision

Approve / amend / reject **Phase 2 of the plan**: P2.1 CSM-4 exhaustive
tier-1 × 3 doors (pre-extraction 17,181-row control arm, ~51 GPU-h) →
P2.2 bar audit → P2.3 D6 extraction (only on the red class) → P2.4
writer-facing acceptance leg → P2.5 CSM-8 done-declaration + pilot memo,
halt before P6.

## Scope questions (answer all)

1. **Phase boundary:** is the precondition set right (PHASE_A_COMPLETE
   marker, miss queue at documented floor, ledger-of-record committed,
   100k dial, gpu-handoff reserved)? May Phase 2 start if Phase 1 halts on
   a regression instead of a floor?
2. **P2.1:** the pre-extraction control arm + ~51 GPU-h estimate. Is 51
   GPU-h a measured number or an assumption (the 4 s/probe figure's
   provenance — `reports/csm/COUNCIL_csm-campaign.md`, the csm-3 record)?
   Does the plan need a sanity-measurement step (a bounded sample first,
   re-estimate, then the full run) before committing 2 GPU-days?
3. **P2.2 ordering:** the bar audit is scheduled AFTER the 51 GPU-h
   control arm — but it judges the instrument the control arm spends 51
   GPU-h on. Should the near-free bar audit run FIRST (the first-principles
   prior-art response in `reports/csm/receipts/council_plan_v2/` makes
   this case)? What does the bar audit pre-register (3–5 cases per D6
   dimension + owner-accepted residual cap) and who grades it?
4. **P2.3:** the red-class scope — verify the per-dimension red counts
   against `reports/csm/census_dimensions_csm_results.jsonl` (the plan now
   says arc-narrative 8 / abilities 6 / state-over-time 5 / appearance 1 /
   causality 1 = 21; re-check). Is "only on the red class" faithful to the
   JJK precedent (council #19 P4 contingent extraction)? What re-opens a
   closed red (the P1.4 re-adjudication)?
5. **P2.4:** the writer-facing acceptance leg (one `script-gen` +
   `cli verify` against CSM) — is ONE script enough, or does the
   done-set need the acceptance leg as a done-criterion rather than a
   final step (the JJK §5 definition ends with "a writer can ask, of any
   line, what it means and where it sits")? What is the pass bar for
   verify?
6. **P2.5 + cost:** the CSM-8 done-declaration (D1–D10 item-by-item on
   CSM + the four pilot numbers + triage log + JJK baseline diff-empty +
   halt-before-P6) — complete as the definition of "100 % done"? Is the
   total cost section (≈ 2 GPU-days Phase 2, ≈ 1.5–2 weeks total) honest
   given the unmeasured 51 GPU-h and the two extra steps (bar audit,
   acceptance leg)?

## Grounding (verify before you record)

- `plan/CSM_2PHASE_PLAN.md` (read in full — Phase 2 + cost section)
- `reports/comprehension/DONE_DECLARATION.md` (the JJK D1–D10 template +
  triage log) + `reports/comprehension/GATE.md` (~line 697)
- `reports/comprehension/COMPREHENSION_REMAINDER.md` (what "understanding"
  was defined to mean; the D-layer plan P0–P5 + halt before P6)
- `reports/csm/COUNCIL_csm-campaign.md` (the 51-GPU-h computation + the
  "unmeasured assumption" flags) + `reports/csm/COUNCIL_csm-3b.md`
  (switchpoint / one-switch-total)
- `plan/CSM_WAVE2_RESUME.md` § Phase-2 preconditions +
  `docs/ops/PC_GPU_HANDOFF.md` (the reserved switching plan)
- `reports/csm/receipts/council_plan_v2/` (prior art: the 5 advisor
  responses of the superseded unified council — especially
  `adv_first_principles.md` + `adv_executor.md` + `adv_contrarian.md`)
- `reports/csm/receipts/council_p1_plan/` (the Phase-1 council verdict the
  plan was just fixed with — the phase boundary it set)

## Rules for every member

Zero-GPU, read-only (you may write ONLY your assigned output file), every
load-bearing claim verified against disk before you record it (if you
cannot verify it, say so — never assume). This council's 5 advisors run in
parallel (owner instruction 23:2x); each starts fresh, sees no other
member's response. 150–300 words each, no preamble, no hedging.