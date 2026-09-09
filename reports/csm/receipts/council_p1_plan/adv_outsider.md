# Advisor (outsider lens) — CSM Phase-1 plan approval

**Q1:** D1–D10 table is self-contained — good. But D1's "100 enumeration questions" transfers vacuously (CSM roster census = 11; the plan doesn't note it). The 22-floor honesty holds.

**Q2:** Baseline-exact inlines the gate values — good. But R-6/R-7 "no-council" hides an open design question (R-6 floor-inheritance, verified open in `council_r2r3/chairman.md:43` + work_log) the plan folds into a "no-council lever" without pointing at that record.

**Q3:** Not executable as written. "Seed-7" unexplained (span_recall.py's 400-sample default; no pointer). "One-copy" used 3×, defined nowhere. Queue math wrong: plan says 58 rows "~30 fixable / 22 floors"; on-disk (verified) = 33 fixable + 3 stamped + 22 floor. P1.1 assumes a "pre-built" R-2 Part-A panel — no such file exists (work_log item 4 never DONE); `/tmp/csm_iter1_records` gone (verified).

**Q4:** The "own-new-row HIT" halt condition is undefined in every document (grep: used in plan, council record, work_log; defined nowhere). 90 min for a 4th router mode + new bundle builder + 2 hooks + 61-key override is over-scoped.

**Q5:** As written, the meter trips itself: "halt on two no-reduction iterations" + 22 never-reducing floors in the same queue → a literal reading halts iteration 1. The plan relies on council #21 R3 scoping (fixable classes only) but never states it in P1.3.

**Q6:** "5.4" in "34 s 5.4 re-adjudication" is a section label (CSM_WAVE2_RESUME §5.4) the plan never points at. R-4 defers the monitor patch to Phase 2, but the stale-ESC hazard that voided the last gate-3 window stays live through P1.1.

**Cross-cutting:** council citations are ledger-numbers only ("#21 R3") with no paths, though records exist under `reports/csm/`. Dial contradiction: CLAUDE.md's "150k Phase-1 mode" vs the plan's "262k → 100k" — qwen_mode.txt = 262k now (verified), so the switch is right; but the stale 150k line and CLAUDE.md's "1,254" suite count vs the plan's 1,303+2xp are absent from the hygiene list.