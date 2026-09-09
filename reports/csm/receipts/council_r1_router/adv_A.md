# Council R-1 (router count rule) — advisor A: First Principles Thinker

First-principles read: the SHIP/AMEND/REJECT question hides the real problem. The router had
one query-shape model — "the set name is the wh-object; prepositional phrases are disposable
scope" — and the CSM bank proved it wrong for counting questions, where the set name lives
*inside* the prepositional phrase ("members are in the Four Horsemen"). The draft is exactly the
minimal model fix: the probe form is keyed on `counting` (`router.py:874–878`; only caller is the
`has_set` probe at line 552), it reuses the existing `_COUNT` regex (line 170, no new regex), and
crucially it re-uses the R1-d gate (line 885: a counting match is accepted only at exact/declared
confidence) as the tripwire. A scope the set does not cover therefore degrades to unverified
leftover → `partial` → qa (verified pre-fix on disk per the receipt: set-14 `partial`,
`rejected: [__unverified__'many']`). No new failure class opens, because the fix adds no new
decision surface — it changes which probe string reaches `build_roster`, and the R1-d gate,
which already existed, is what keeps "count the set's subset" on prose (jjk Geto pin, unchanged
in the 136-test router suite).

Checks I re-verified on disk:
- Diff: `git diff scriptengine/retrieve/router.py` = one hunk + docstring, +23/−1, no series
  name in the `.py` (the no-series-name rule holds; the rule fires only where a declared roster
  phrase matches, so a wiki with no rosters cannot trip it — pinned by
  `test_a_series_without_rosters_is_unaffected`).
- Every `how many` declared match phrase I spot-checked (csm:98/153, db:291–292, jjk:855/881/911,
  onepiece:107/115) has a shorter sibling, so keeping the phrase in the counting probe cannot
  orphan a declaration — the receipt's "9 across 5 series" audit is confirmed.
- 11-test file re-run by me: `pytest tests/test_csm_router_count_rule.py -q` = 11 passed in 3.29s
  (model-free, <15s).
- Queue: `reports/csm/miss_queue_csm_iter1.jsonl` rows csm-set-14, csm-set-15, red-R-1 all
  `status: open`, `fix_class: R-1`; red list R-1's "Not a per-wiki override" ruling holds — a
  csm-side override could not fix the phantom-`many` sub-bug, which only a router-side probe
  change can.

What SHIP actually commits to: the code is the small part. The real remaining risk is process —
the fix is only as good as (1) the four standing gates landing (pytest 1,265 = 1,254+11, eval
jjk 31/31, span-recall 48,572 + 400-probe, canon opm 236/236 79.0%, per the receipt's gate-time
commands), and (2) the R-1 class re-sweep turning green (R5: ≥1 own-new-row HIT or halt to
council). The db qa→roster flip is a behavior delta on a non-JJK series with no db gold count
row in the four gates — a documented residual, not a blocker.

VERDICT: SHIP / FIRST STEP AFTER VERDICT: B runs the four standing gates in one-copy order at 150k per the receipt's gate-time commands (pytest 1,265 → eval jjk 31/31 → span-recall 48,572 + 400-probe → canon-run opm 79.0%), then the R-1 class re-sweep (≥1 HIT on its own new rows) before committing and closing csm-set-14/15/red-R-1 / CHANGE-OF-MIND IF: pytest lands off 1,265 (an unexplained routing regression beyond the documented csm/db deltas), the R-1 re-sweep shows 0 own-new-row HITs (halt to council per R5), or eval/canon regresses below the 2026-09-08 re-baseline.