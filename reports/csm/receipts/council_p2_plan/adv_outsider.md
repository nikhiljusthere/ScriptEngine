# Outsider — CSM Phase-2 plan

**Q1 (boundary).** Phase 2's preconditions are a five-word header (100k dial; gpu-handoff authorized) + P1.4 close conditions; the real gate is a one-line marker (`PHASE_A_COMPLETE`, `phase_status.txt`) with no machine check; the plan never says "no marker, no Phase 2", so a P1.3 regression halt could still read as Phase-2-able.

**Q2 (P2.1).** The numbers collide: panel = 17,181 rows (`panel_csm.json`), but the cost line computes from "≈15,400 sentences" — the 1,781-row gap lives only in council #24. 51 GPU-h rests on 4 s/probe, an "unmeasured JJK number" per council #3 (JJK measured ≈0.47 s; records re-estimate 8–17 h, a 58-h variant also on record); COUNCIL_csm-3(d)(2) already ordered the sanity re-estimate, but P2.1 has none. "Gpu-handoff chain" / "quiet windows" are undefined in the plan; the chain's doc is a 262k→100k handoff, yet both phases run 100k — the plan never says why the chain is needed.

**Q3 (P2.2).** Double-scheduled: P1.4(d) already runs the same 3–5-case bar audit pre-marker; P2.2 re-lists it — which is real? "Per D6 dimension" is undefined (CSM census has 6 classes; JJK's 14); no grader named.

**Q4 (P2.3).** Red counts verified against the raw jsonl: 8/6/5/1/1 = 21, matching. A14 is a correct admission: this is Phase 2's only comprehension step — de-contingent it or number it.

**Q5 (P2.4).** The plan concedes the done-set is a "reachability proxy," then demotes the writer's test to one final step with no pass bar — make it a done-criterion.

**Q6 (P2.5 + cost).** "The four pilot numbers" are undefined (council #24 §8; #1/#2 already on disk in `T0_PILOT_CSM.md`); "JJK baseline diff-empty" never says which baseline (council's 1,242 or the re-baseline's 1,303+2xp, `GATE_REBASELINE_2.md`) — neither cited. "P2.2–P2.5 ≈ 1 day" has no breakdown; until the missing measurement exists, the honest range is ≈8 h, not 2 GPU-days.