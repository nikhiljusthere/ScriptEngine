# D6 CLOSE — A20 STAMP (2026-09-18)

D6 (the §9a closure loop: targeted extraction + rebuild + closure
instruments) is CLOSED. Two councils refused the stamp (WITHHOLD,
WITHHOLD ×2); the landing council (parallel advisors/reviews/chair,
`COUNCIL_csm_d7_landing.md`) ruled LAND-then-STAMP conditional on:
commit at pinned hash → re-gate from committed IDs → JJK-exact re-proof
→ register 46→green + 16-row docs. All five posted below, same commit.

## The close evidence (all against commit `9ef7082e`)

1. **Landing base** `9ef7082e`: `scriptengine/api/context.py` +64
   (subject-routing: generic arc/chapter/episode/volume title patterns
   with node/alias resolution + router-subject fallback in
   `_qa_context` when the caller passes no subject) + six new
   `tools/csm/` instruments. Sole tracked code delta (verified).
2. **Four gates, post-commit, whole card** (`tools/csm/d7_gates.sh`,
   state `/tmp/d7_gates/`, run dirs `reports/2026-09-18-0607/`):
   pytest **1,329 passed + 2 xpassed rc=0** (pin holds) / eval jjk
   **31/31** / span-recall jjk **48,572 offline rc=0 + 398/400 live
   (99.5%)** / canon-run opm **236/236 · 10/16 exact · 79.0% · 0
   confident-wrong**. JJK diff = gate-output artifacts only
   (`recall_verbatim.jsonl` +rows, `reports/index.md` +row); no JJK
   code/corpus/store moves.
3. **Official regrade, post-commit** (`census_widened_csm_results.jsonl`):
   **417 → 463/486 (+46 red→green, 0 green→red, 0 errors)**; flip list
   `receipts/d6_probe/CONFIRM_FLIPS.json` (reproduces the pre-commit
   measurement exactly, class for class); pre-spike snapshot
   `receipts/d6_window/census_widened_csm_results_pred7.jsonl`.
   OOS200 **168 → 190** (floor pre−2 holds by 24); green30 **0 flips**;
   bar-qa 11 → 13.
4. **Register**: the 46 flipped rows carry recovered_by "qa+subject
   (D7 spike, landed; official regrade 463/486)". The 7 amended
   holdouts stay in the D7 named limit (chap-01 numeric collision;
   org-03/05/06; vol-10 guidebook; pool-140/358 width). The 16 floor
   rows each carry triage + root_cause + owning_phase Phase-2 + closer
   "D6 extraction / 5.4 re-adjudication" + post-Phase-2 retest trigger
   (ROUTING×12 / CONTENT×2 / PARTIAL×2 — verified programmatically).
   134 setrel COMPLETE pre+post. 69-ledger: 46 green + 7 limit + 16
   floor + 0 unregistered. Void triggers (gate regression / flips /
   A-row closes-still-red): none fired.

## What "A20 closed" does and does not claim

D6's pass test is met on every clause: 46 reds ended green (measured
twice, second run from committed IDs); the rest sit in named-limit /
Phase-2 buckets with defect+leg; OOS floor; green sample; gates;
JJK-baseline. It does NOT claim CSM 100%: 23 reds stand (7 D7 width/
collision holdouts + 16 Phase-2 floor), and the Phase-2 extraction
campaign (interval facts, timeline consumers for the 333-row events
table no graded door reads yet) is untouched. Coverage: csm 473/537
(88.1%), 4,013 Qs, remainder 0.

## Known open items (recorded, deferred)

- Page-run blackout (134× connection-refused, zero access-log traces):
  root cause UNDETERMINED after full elimination (killers, proxy,
  port, stale, clock; dmesg unavailable — OOM excluded via
  graceful-shutdown SIGTERM logic); halt guards added to both window
  scripts (untested by fault injection); no contamination found in any
  instrument. RETEST owed if a future window shows the same signature.
- Served text not byte-stable run-to-run (trailing-beat drift,
  verdicts stable).
- 3 width holdouts need subsection recall beyond focus routing
  (pool-140/358, chap-01 depth).
