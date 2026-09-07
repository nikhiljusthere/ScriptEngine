# COUNCIL — 2C gate (beam-first) result + the A4 root-cause and fix

Date 2026-09-07. Records the 2C oracle gate as run at beam-first
(`2ea235e`), the A4 outcome miss it surfaced, the root cause pinned by
tracing the live qa door, and the fix that closed it. This is the evidence
record behind the next-move council (`COUNCIL_phase5-next-move.md`, history
#11).

## The 2C gate as run

`plan/ORACLE_v1.yaml` (18 items, sha256 re-verified at the 2C start),
served through the live qa door (`route()` → `build_context(mode="qa")`),
device CPU (Qwen owns the GPU). Two configurations were compared:

| configuration | score | open items |
|---------------|-------|-----------|
| floor-first (RED baseline) | 11/18 | — |
| **beam-first (`2ea235e`)** | **16/18** | **A4** (outcome), **C1** (timeline, documented expected-fail) |

So beam-first recovered 5 items over the floor-first baseline and left two:
A4 (an outcome question) and C1 (a timeline question recorded in the plan as
an expected-fail, not a regression).

## A4 — the outcome miss, root cause

**Item A4:** "What was the result of the final battle against Sukuna?" —
ground truth `The jujutsu sorcerers are victorious.` (the `Outcome` cell of
the battle page **Jujutsu Sorcerers vs. Sukuna**, ch. 244–268).

**What was *not* the cause** (ruled out by tracing):
- **Routing was correct.** `route()` sends A4 to `qa` with subject `Sukuna`.
- **The resolver was correct.** `battle_outcome` (roster.py:694) resolves the
  fighter-named phrasing to the one battle page whose sides name the fighters
  and returns that page's infobox — verified in isolation to return the
  correct page (`Jujutsu Sorcerers vs. Sukuna`, outcome at block index 7).

**The actual cause — the fusion guard in the live qa path
(`retrieve/hybrid.py`, `HybridRetriever.search` step 3b/3c):**

In the live `search()`, the top-5 entities are
`[Sukuna, Sukuna vs. Jogo, Sukuna vs. Yorozu, Sukuna vs. Mahoraga, Satoru Gojo
vs. Sukuna]`. `Jujutsu Sorcerers vs. Sukuna` sits at **position 6** — inside
`result.entities` (so the page is *linked*), but **outside the top-5 that
step 3 pays facts for** (`hybrid.py:201`). The 3b/3c guard was
`if entity not in result.entities: prepend`, which skipped the prepend
because the page *was* linked — the guard tested **linkage**, not **whether
that page's facts had actually been paid for**. Net: the correct fight's
`Outcome` was never added, and the wrong fight inside the top-5
(`Sukuna vs. Jogo`, position 2, ch. 114–116) was the one whose facts were
served.

**The fix (commit `6af92ca`):** compute `battle = battle_facts(...) or
battle_outcome(...)`, then **dedup + prepend** the resolved block so the
fight's infobox leads `result.facts` regardless of rank:

```python
entity = battle[0]["entity"]
result.facts = battle + [f for f in result.facts if f["entity"] != entity]
if entity not in result.entities:
    result.entities.insert(0, entity)
```

The mandate (from the next-move council) was to fix the **door**, not the
resolver — the resolver was right; the drop was in the fusion layer.

## Verification

- **Regression test** (`tests/test_context.py::TestBattleFactsReachTheQaBundle::
  test_a_low_ranked_named_fight_outcome_still_leads_the_facts`) drives the live
  qa path (`route` → `build_context`). **Red on the old guard** (the bundle
  showed `Sukuna vs. Jogo` ch. 114–116, no outcome), **green on the fix**.
- **Full 18-item oracle, in-process live qa path:** 17/18 — A1–A4 all pass,
  B/C/D/E/F all pass; only **C1** (the documented expected-fail timeline item)
  remains open. No regressions.
- **Standing gates:** `pytest tests/ -q` = **1239** (1238 + the new test);
  `eval --series jjk` = **24/24**; `span-recall --series jjk` = **100.0000%**
  (0 unreachable). All on CPU.

## Verified-claims ledger (checked this run)

- [x] A4 routes to `qa`, subject `Sukuna` — `retrieve/router.py` `route()`.
- [x] `battle_outcome` returns the correct page in isolation — `roster.py:694`,
  confirmed against `series/jjk/facts.db` (page `Jujutsu Sorcerers vs. Sukuna`,
  `outcome` = `The jujutsu sorcerers are victorious.`, `chapters` ch. 244–268).
- [x] The live top-5 leaves `Jujutsu Sorcerers vs. Sukuna` at position 6
  (linked, not paid for) — in-process `search()` trace, `hybrid.py:201/222-241`.
- [x] The old guard tested linkage, not payment — pre-fix `hybrid.py` 3b/3c.
- [x] The fix dedups + prepends the resolved block — `6af92ca`, `hybrid.py`.
- [x] Oracle 17/18 in-process; pytest 1239; eval 24/24; span-recall 100%.

## Evidence pins

- Oracle: `plan/ORACLE_v1.yaml` (A4 @ the outcome group), harness
  `reports/comprehension/raw/oracle_2c/oracle_run2c.py`.
- 2C bundles/results: `reports/comprehension/raw/oracle_2c/`.
- Fix: `scriptengine/retrieve/hybrid.py` (3b/3c), commit `6af92ca`; regression
  test `tests/test_context.py`.