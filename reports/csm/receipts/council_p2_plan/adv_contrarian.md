# Council P2-plan — Contrarian

**Verdict: AMEND (four).**

**A1 — P2.1's "51 GPU-h" is stale twice (Q2, Q6).** P2.1 prices 17,181×3×4 s = 57.3 h off the pre-pin 15,400 (panel verified: `panel_csm.json` = 17,181) — the figure CSM-3's council recorded as "58-GPU-h". And 4 s/probe is a JJK number COUNCIL_csm-3 ruled "fiction"; its mandated sanity-100 re-estimate is absent from P2.1, yet the cost section freezes it as "the one number no process change touches." The only CSM rate on disk: 8.5 s/probe CPU@150k (commit `f81a1af`) — at that rate ~122 GPU-h, 2.5× the budget. **Amend:** bounded sanity-100 at the 100k dial, measure CSM s/probe, re-estimate before committing.

**A2 — P2.3 is a moving target with a null branch (Q4).** Reds verified (MECH_RED 21: arc-narrative 8 / abilities 6 / state-over-time 5 / appearance 1 / causality 1); but scope is "whatever P1.4's re-adjudication leaves or adds," and a closed red de-scopes. If it closes all 21, the plan's sole comprehension step never fires and P2.5 closes D1–D10 on triage lines with no understanding layer — the goal unmet, "100 %" signed. A14 defers "de-contingent or numbered D6 item" to this council: rule now; the null branch must void P2.5, not pass it.

**A3 — P2.4 is n=1 (Q5).** One `script-gen` over 17,181 lines, no pre-registered pass bar (verify checks tag traceability, not comprehension). Pre-register the bar; make it a done-criterion, not a last step.

**A4 — cost hides the legs (Q6); Q1: no.** "P2.2–P2.5 ≈ 1 day" omits the 11-member sequential council, the four one-copy gate re-runs, and gpu-handoff fragmentation (30–60 s model-less per switch, unpriced for a 2-day batch). Phase 2 may not start on a regression halt: the marker encodes the floor, and a regressing queue invalidates the control arm the budget would buy.