The device fork is the wrong frame. The 17,009-row panel isn't a one-shot measurement that will go stale — it's the campaign's **attribution instrument**, and the "staleness" *is* its value.

**Upside 1 — pre/post pairing.** Phase B runs the 100k switch (already planned) *and* the D6 extraction (meaning/events, 0 rows today). Run the full-panel sweep as Phase B's **first** act — after the switch, *before* the extraction — and it becomes the **control arm** of the experiment: same panel hash (`e3d73720`), pre- vs. post-extraction hit rate = proof the extraction added comprehension, not churn. The R-CSM3B-2 keyed ledger (`panel_hash`+`device`+`commit`) was *built* to survive a dial change; CSM-4's tier-1 just **resumes** it and diffs. Carried forward, not deferred-and-lost.

**Upside 2 — the sweep writes the extraction spec.** The 62 infobox keys outside engine vocabulary, the 8-verb gap (76% of 100 sentences not held by the 9-verb set), and the cross-page census (10,889/11,261 edges) are all *inputs* to the D6 build. The full-panel miss queue is where those clusters *surface* — the worklist that scopes Phase 2, not just a queue to close. Iteration 1's real deliverable: "produce the miss population that defines Phase 2's scope", not "close the misses".

**Verified on disk (corrects the prompt):** the census is **39/60 green / 21 red** (arc-nar 8, abilities 6, state-over-time 5, appearance 1, causality 1) — *not* the "49/60" the work_log states. The extraction gate is more live than documented.

So run **C now** (bounded CPU at 150k: 400-probe gate + 20 twenty_failures + 5 reds + targeted re-sweeps grading each fix, A LONG flag). **Addendum:** promote the full panel to Phase B's *first* act, pre-extraction, as baseline + spec; carry the keyed ledger across the dial.

OPTION: C-baseline (C now; full-panel promoted to Phase B opening act as pre-extraction baseline + extraction spec; ledger carried forward)
FIRST STEP: run the bounded 400-probe standing gate + the 20-row twenty_failures set on the CPU :8000; write the pre-triaged miss queue; record the 39/60 census correction.
CHANGE-OF-MIND IF: the D6 extraction gets de-scoped (dimension census stays green post-fix) — the pre/post pairing collapses, the panel's only value is a plain hit-rate number, and I'd take option A (switch now, run the full panel on CUDA once, switch back).