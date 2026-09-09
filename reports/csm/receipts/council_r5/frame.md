# Council R-5 — the relations-mode question (frame, reconstructed for the review wave)

Reconstruction note: the original advisor prompt (council workflow 429d9efa) is redacted
in the persisted oracle transcripts. This frame is reconstructed from
/tmp/csm_iter1_records/r5_class_plan.md (verbatim class-plan draft), the working-tree
diff, the CSM red list, and reports/master-work/work_log.md. The five advisors
(recovered as adv_A..adv_E) were given the equivalent content.

## The decision under council review

The R-5 fix class (frozen miss queue: 11 "documented relationships of X" rows, all
0/11 under qa/roster/narrative) lands as a **fourth router mode `relations`**:

- Root cause: the router has 3 modes (qa/roster/narrative); relationship phrasings fall
  into `looks_like_enumeration` → roster, while the relations channel (facts.db,
  11,261 edges) is served only as a qa-bundle side channel (context.py, hybrid.py) —
  structurally unreachable for enumeration-shaped queries.
- Fix shape: a 4th router mode `relations` (phrasing trigger, series-agnostic, checked
  before the enumeration branch) + a dedicated budgeted bundle builder (edges as the
  primary answer) + MODES/endpoint update. No per-wiki override.
- Blast radius: relationship phrasings on ALL series — JJK/OPM invariant pins per the
  R-1 pattern. The R-2+R-3 council's forward note applies (cite-the-edge-not-the-set).
- Tests: 8 collected tests (3+2 parametrized router trigger + 3 builder; none
  store-free pre-amendment; the store-free trigger test is amendment A5(a)) + a live
  `validate_relations.py` at gate time (R5 meter: the 4 own rows off 0/11).
- The working tree (uncommitted, at HEAD 41160cd) holds the implementation:
  5 files, +223/−4 — scriptengine/retrieve/router.py, scriptengine/api/context.py,
  scriptengine/api/main.py, tests/test_router.py, tests/test_context.py.
  The exact diff is in package_diff.md beside this file.

## Gate expectations (the four standing gates, after any amendments land)

1. `pytest tests/ -q` — 1,305 pin + the 8 new R-5 tests = 1,313 (Ruling 5e: a known +N
   test delta does not itself re-run the gates; the full re-run happens at closure).
2. `eval --series jjk` — 31/31 (invariant).
3. `span-recall --series jjk` — 48,572/48,572 offline rc=0 (invariant) + live probe
   ≥390/400.
4. `canon-run --series opm` — ≥10/16 exact, 236/236 canon (invariant), ≥79.0% (floor 74.0%).
5. R5 meter — ≥1 HIT on the class's own new rows (validate_relations.py); JJK/OPM
   frozen-queue invariants (no new miss = a regression = halt).

## Pre-registered close-council item (carried from council_r2r3, chairman.md finding 8)

The R-6 `subject_aliases` hook design (aliases-table vs query-time override) must answer
whether alias-resolved subjects inherit the new level-0 card via the floor. Recorded for
R-6 drafting. The R-5 council should state whether the relations door changes anything
about that question.

## The council question (what the five advisors answered)

SHIP / AMEND / REJECT the R-5 relations mode as it stands in the working tree?
Each advisor owned one focus lane, declared inside its own response:

- Response A — trigger precision (the 5-alternative `_RELATIONS` regex)
- Response B — route placement (rule 2d position vs the enumeration branch)
- Response C — builder correctness (`_relations_context`)
- Response D — API plumbing + empty-case fallback
- Response E — test adequacy + R-6 floor inheritance

Verdict vocabulary (project convention, per council_r2r3/chairman.md): SHIP / AMEND
(with numbered, zero-series-name, model-free-testable amendments) / REJECT.
---

## ADDENDUM — a costed governance question, for the CHAIRMAN ONLY

Added by the directing session mid-council, on owner instruction (2026-09-10),
**after** the advisors and reviewers had answered. It is deliberately scoped so it
cannot contaminate their work: it asks nothing about R-5's technical merits, and the
advisor/reviewer rulings stand untouched. Answer it in a separate, clearly-labelled
section of `chairman.md`, after the R-5 verdict.

**The question.** Is the standing 11-member council form (5 advisors → 5 peer
reviewers → chairman) proportionate for *each* of the remaining fix classes
(R-1…R-7), or should the composition change? Give a pre-registered rule for which
changes get which form.

**Measured cost of this council's reviewer wave** (live `ninfer-serve` request log,
15-minute window, 99 model calls, post-serialization):

| | tokens |
|---|---:|
| prompt sent | 5,172,779 |
| served from prefix cache | 3,748,956 (72 %) |
| **actually re-prefilled (real compute)** | **1,423,823** |
| completion generated | 112,292 |

- **~29–32 assistant turns per member** — the dominant cost multiplier: each turn
  re-sends the member's whole conversation.
- re-prefill : completion = **12.7 : 1**, improved from **32 : 1** before the
  one-member-at-a-time fix (cache hit 1.5 % → 72 %). The concurrency defect is fixed;
  this question is about what remains.

**Evidence that the peer round earns its cost** (do not trade this away):
`rev_1.md` verified A's over-match claim at `router.py:481` against the `_`-batches,
**falsified advisor B's proposed fix** with a live counterexample
("Who is left to stand against Mahito, per Chapter 131?" still matches alt-5), and
caught a who-branch class **all five advisors missed**. Those findings came *from* the
disk-verification turns, so cutting turns, or pre-seeding members with only the
evidence a seeder chose, would likely have suppressed them.

**Evidence of redundancy in the advisor round** (the candidate saving): 4 of 5
advisors missed the same who-branch class, and one (B) proposed a fix a reviewer
immediately falsified.

**What to decide, concretely:**
1. Does the **advisor** round shrink (e.g. 5 → 3) while the peer round and chairman
   stay intact? State the expected loss.
2. Is there a **lighter form** for narrow, single-file fix classes, with the full
   11-member form reserved for structural changes — and what is the *pre-registered
   test* that sorts a class into one or the other (decided before the class opens, not
   after)?
3. Should a **turn budget** per member be set, given the 29–32 turn multiplier — and
   if so, how is it kept from suppressing exactly the disk-verification behaviour that
   produced this council's best finding?

Rule as usual: claims DB/disk-verified before recording; a claim that cannot be
verified did not happen.
