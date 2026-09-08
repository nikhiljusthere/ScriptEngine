**Verdict: close CSM-3b.** The four standing gates match the re-baseline exactly, both engine fixes (roster-door, panel-hash) are committed and green in the 1,254-test suite, and every open item (F1, G-CSM-1/2) has a documented owner and schedule. That is a close, not a dodge; reopening adds no signal.

A fresh-eyes read still flags three things:

1. **The receipt is not self-contained.** CSM3B_GATES.md says "COMPLETE" and "matches re-baseline" but assumes the reader knows what CSM-3b was and what the re-baseline numbers are. Phase 2 runs on receipts alone (side sessions, Qwen quiet windows); a reader who has not read COUNCIL_csm-3.md cannot reconstruct this wave. Add a five-line "what this wave delivered" header to the receipt or SWITCHPOINT. Cheap, high value.

2. **F1 is an efficiency trap Phase 2 will hit again.** Because hit_rate uses the full-panel denominator, the wiped 168 rows corrupted no number — they only cost re-probe time. So git recovery "worked" by luck, not by design. Phase 2 is 17,181 probes × 3 doors, ~2 GPU-days, unattended: any interleaved sanity run silently re-burns hours of GPU. The fix (key the ledger by panel hash) is a few lines — land it inside the CSM-4 wave, before the sweep starts. That is the one ruling I want recorded.

3. **Check G-CSM-1/G-CSM-2 before CSM-5.** If either is a zero-GPU cheap-signal fix (like the 5.4 door pre-check), pull it into Wave 2. Also keep the labels apart: 4/4 sanity is liveness, not health — the real state is 57.9% exact with two zero-recall questions.

F2: no ruling needed — intentional, already documented. F3: not a council item, but verify monitor rule-2 before any unattended Phase-2 window; a kill heuristic that already killed two CUDA jobs is a pre-flight check, not a formality.