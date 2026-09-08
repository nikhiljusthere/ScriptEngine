# Peer A — review of council responses A–E (CSM-1b/CSM-2 cadence)

## 1. Strongest response

**C.** Verified the canon arithmetic (146→148); the only mode-aware gate
read (262k → six VRAM-sensitive cases OOM on CUDA); the only catch of
uncommitted raw receipts (git-confirmed). Its per-door sanity floor
protects the 51-GPU-hour sweep from grading a dead qa door. Runner-up: B
(G-CSM-1 "verified in process" has no persisted receipt); D's 0752-vs-
REFUTED conflict is the sharpest one-off.

## 2. Biggest blind spot

**E.** (i) Misses the stale gate baseline (1242 predates CSM-2's 7 tests;
B/C/D flag it, git order confirms). (ii) Its (c) "no series name in
`coverage_report.py`" is wrong — line 224 `default="jjk"`, caught by A/B/C/D.
(iii) Its (d) (G-CSM-4 first; T0 into CSM-3(a)) contradicts the plan's item
order (fixes → item 7; T0 → 6(e)).

## 3. What all five missed

The re-baseline is mode-gated: Qwen's 262k switch is in progress, so
"re-baseline before CSM-3" needs an explicit order (finish switch →
checkpoint → 100k → CUDA gate → restore); nobody states it. The council's own record + plan bookkeeping (state/decisions)
are uncommitted — "if it is not on disk, it did not happen" is at risk
(C catches receipts only). A's "no blockers" vs B's "blocker" needs a
ruling.

---

Reviewer verification (peer-A, 2026-09-08): `series/csm/facts.db` (537 docs,
14 unknowns, 748 relations rows; `Blood Weaponization` 0 chunks; `pulling a
cord on his chest` 1; `Prime Minister Contract` 0 vs `Contract with the Prime
Minister` 11; TSD 1/4/5/6/7 = 1/31/18/3/12 chunks, 2/3 = 0); JJK
`COVERAGE.md` regeneration diff empty; `coverage_report opm` rc=3;
`default="jjk"` at `tools/coverage_report.py:224`; 0752 REPORT caveat (bank
changed) + extraction-gap prescription (`ingest/abilities.py`) confirmed;
REFUTED 2026-08-17 note in `series/csm/overrides.yaml` confirmed; live
`nvidia-smi` 30613/32607 MiB @ 100% + `:8000` health=cpu confirmed.