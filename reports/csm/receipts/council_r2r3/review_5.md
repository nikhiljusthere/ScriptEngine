# Peer review 5 — council R-2/R-3 (weighted: inter-draft × queued-class interactions)

**1. Strongest: B.** Found the only live defect the other four took at face value: `recovered` is uncapped; when >top_k dropped passages cover the query, `deduplicated[:top_k−L]` (hybrid.py:365) is a negative slice — the internal list grows past top_k, the rerank tops are dropped, and dedup-order (not score) recovered passages win. Verified: `rrf_score` exists (hybrid.py:56), so the cap is 1 line + 1 test. Also caught: stale facts.py docstring (:1983 "level-2" vs SQL `level IN (0,2)`); `Roster.warning` misreports on the empty-intersection path ("14 of 14" while the full list was served unscoped).

**2. Biggest blind spot: E.** Only SHIP/SHIP; accepted "beam-bounded" without simulating that L>top_k regime; missed the red-list ID collision (C) and the receipt sweep omission (D); its R-6/R-7 "cheapener" point stops at pattern level and never asks whether R-6's alias design (aliases-table vs query-time override) rides on the R-2 floor.

**3. All five missed:**
- **R-2 × R-1:** the re-admission sits in `HybridRetriever.retrieve`, which also powers the roster count branch (context.py:290–293, top_k=8) — R-1's closed rows csm-set-14/15 and the G7 count-prose expectation sit inside R-2's blast radius; D's sweep list omits them.
- **R-3 × R-5:** when the relations mode (red R-5, CSM-7) lands, its scoping must be decided against `closed_members` — the red-list addendum's R-1×R-5 note defers exactly this to R-5 drafting; nobody carried it forward.
- **R-6:** the `subject_aliases` hook design (aliases-table vs override-read) decides whether alias-resolved subjects auto-inherit the new level-0 card via the floor.
- **Process:** the red-list R-3/R-4 ID collision (C) belongs in the amendment, not the notes.