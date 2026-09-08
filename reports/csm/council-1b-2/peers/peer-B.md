# Peer review B (The Contrarian, peer id B) — CSM-1b + CSM-2 cadence council

Reviewer B's independent verification (store queries, git log, live re-runs of
`tools/coverage_report.py`): JJK `COVERAGE.md` regeneration diff empty (rc=0);
`csm` rc=0 (0/537, remainder 227); `opm` rc=3 (no `page_scope`); csm `facts.db`
= 537 docs / 13 types / 14 unknowns, `Weaponization` 0 chunk hits, TSD 2/3
absent and only TSD 4/5 have document pages; `questions/csm.json` 39/39 active
stamped; pytest 1249 collected; Qwen 262k on the card (30618/32607 MiB, 100%
util) while `:8000` already runs on CPU.

## 1. Strongest response

**B.** It verified the store claims itself (0-hit proofs; only TSD 4/5 have
pages → csm-set-14's "5" is a floor, not a wiki total), and its (d) carries the
only hard blocker: git-log ordering proves GATE_REBASELINE's pytest 1242
predates CSM-2's +7 tests (now 1249) — the "JJK baseline" is no longer
reproducible on the current tree. C's GPU-state point (262k Qwen blocks the
CUDA re-baseline; 6 `test_context` OOMs) is a close second but its 1243+6
claim is un-re-runnable right now.

## 2. Biggest blind spot

**E.** Its (d) is upside-only (fix G-CSM-4 first, fold T0 into CSM-3(a)) with
zero gate/baseline items — it misses the stale-baseline blocker entirely. And
(c) is factually wrong: it claims "no series name in `coverage_report.py`
(only via `paths.overrides`)", but the pre-existing `default="jjk"` CLI arg
is in that tool — A, B, C, and D all flagged it.

## 3. What all five missed

(i) The uncommitted +400-line append to `reports/span-recall/jjk/
recall_verbatim.jsonl` (GATE_REBASELINE's probe ran in append mode) is §2a
trap #2 in the wild — append-duped jsonl, `done` unwired. CSM-3(b) is the fix
for the probe path; re-running the probe before that appends another 400
lines. C lists the file only as "commit it".
(ii) The re-baseline B/C/D demand is not runnable on CUDA today (Qwen 262k,
100% util) — it needs a 100k-switch/CPU decision first (only C says so). And
CLAUDE.md's gates table is now stale a third time (1,239 → 1,242 → 1,249).