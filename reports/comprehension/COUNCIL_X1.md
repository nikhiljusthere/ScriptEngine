# COUNCIL — close X1 (the JJK 5-step census) and resume at P3.A?

Date 2026-09-07. End-of-sub-list council for excursion **X1** (standing rule 3b:
the council fires *before* the return pointer X1.g → P3.A). X1 is the JJK 5-step
retrieval census: a retrieval fix (`dedb949`), a census harness
(`tools/census_545.py`), a full 545-pair census (report
`reports/comprehension/STEP5_CENSUS_545.md`), the 2 genuine not-reached faults
fixed + tracked (`a5e93c3`), the milestone recorded in
`reports/page-campaign/STATUS.md` §1101, and the harness + pairs committed to
the repo. The open question: **does the evidence support closing X1 and resuming
at P3.A, or is there a gap in X1.a–f that would poison P3.A's ability census?**

Method: 5 advisors (independent, in parallel) → 5 peer reviewers
(anonymized, in parallel) → this synthesis. Protocol per the `llm-council`
skill. Per standing rule 1, every load-bearing claim was re-verified against
code + `series/jjk/facts.db` + the STEP5 report before recording; the
verification appendix (bottom) lists what held and what was struck.

## Where the Council Agrees

- **X1.a–f are real and on disk.** Commits `dedb949` and `a5e93c3` are in the
  trail; `tools/census_545.py` + `tools/census_545_pairs.json` are tracked;
  the STEP5 report and `STATUS.md` §1101 carry the milestone. No advisor found
  a sub-line that is not verifiable. Closing X1 is correct bookkeeping.
- **The 545 instrument is the wrong *shape* for the 3B decision as written.**
  "Reached" is a *presence* check (a beat from the target section is in the
  6000-token bundle). For prose dimensions presence ≈ sufficiency; the decision
  P3.A must feed ("does retrieval serve abilities well enough to close the 3
  extraction steps?") needs a *sufficiency* bar. Strongest independent
  convergence (Contrarian + First-Principles).
- **The pool is 300, not ~313.** The section inventory in `facts.db` gives
  exactly 300 (dimension, page) rows for the five ability titles; the ~313
  figure sloppily folded in title-variant sections ("Cursed Techniques" ×12,
  "Cursed Restrictions" ×14). Reconcile before running.
- **The harness `DIMS` is hardcoded** (`tools/census_545.py:65`) to the five
  prose dimensions, so the per-dimension summary blanks for ability dims.
  Derive it from the pairs file.

## Where the Council Clashes

- **Is the "reached" metric a false-green risk?** The Contrarian + First-
  Principles said **yes**: the structured `abilities` table is names-only (594
  names, 94/146 pages), so a "reached" read would feed a false ~98% green into
  the 3B fork and close extraction on *names, not mechanics*. The Executor + a
  peer reviewer **disagreed**, after DB-checking the corpus: the *on-page*
  ability sections carry **mechanics prose** (Gojo's Cursed Technique section
  is 7,476 chars — "nigh-absolute control over space… at an atomic level"), so
  for the on-page census "reached" is a *fair proxy*. **Resolution (verified):**
  the false-green fear is overstated for the on-page census (the sections hold
  mechanics) but real for the *structured* `abilities` layer (names only). The
  census measures on-page reach; the extraction decision also needs the bundle
  to *carry* the mechanics, not just a beat — a caveat for long sections.
- **Was the minor tier re-measured post-fix?** The Contrarian said **no** (the
  471-pair minor tier, where 5 of the 7 not-reached live, was never re-run on
  current code; per-pair results sit in `/tmp`, untracked; the global table
  still reads 7). A peer reviewer read STEP5 §80-94 as "records a post-fix full
  545 re-run (7→5)." **Resolution (verified):** STEP5 §80-94 says a full re-run
  *"refreshes the global not-reached count 7 → 5"* — the stated effect of
  *running* the command, but the global table still reads 7, so the re-run was
  never committed. The Contrarian is right: **re-run + commit is still owed.**

## Blind Spots the Council Caught

- **The 3B fork's decision rule is undefined.** `plan/flow.md:244-247` defines
  3A (widen `abilities` to 146), 3B (extract mechanics), 3C (gate) — but no
  branch maps a census % to a decision. The "4 branches; 3 close extraction, 1
  opens" has no trigger. Define it before the fork is meaningful.
- **The sufficiency instrument is the 3C held-out oracle (A/F re-run), not the
  reachability %.** Reaching a section ≠ answering the question. The 2C pattern
  (emit oracle A/F re-runs) is what should drive the 3B fork.
- **The 300 pairs are not disjoint.** "Abilities and Powers" is the level-2
  parent of Cursed Energy / Cursed Technique / Intelligence / Physical Prowess
  (level-3 children). Interpret per-page, not per-dimension.
- **The GPU policy.** "Run on GPU" hits the hard rule (Qwen owns the card, ~7
  GB headroom). A ~5-min co-located CUDA census fits the *short-borrow*
  exception (quiet window + Qwen health check before/after + restore CPU
  steady-state); otherwise it is the ~65-min CPU overnight. `STATUS.md:1107`
  already prescribes `CENSUS_DEVICE=cuda`.

## The Recommendation

**Close X1 (with the corrected number) and resume at P3.A, but fix the
instrument before trusting the 3B fork.** Concretely:

1. **Re-run the full 545 on current code** (`CENSUS_DEVICE=cuda python
   tools/census_545.py`), commit the per-pair results to the repo, and record
   the corrected global (not-reached 7 → 5, 99.08%). Turns X1's closing number
   from a stale 98.7% into a measurement.
2. **Build the ability pool from the section inventory** (300 pairs, not 313):
   one `SELECT` over `sections ⋈ documents` for the five ability titles on
   character/synopsis pages; emit `tools/census_ability_pairs.json` in the 545
   schema. Record title-variant inclusion + the parent-child overlap in the
   file header.
3. **Generalize the harness `DIMS`** to derive from the pairs file (one-line
   change at `census_545.py:65`).
4. **Add a content-bearing class** (`reached-names-only`) so the census
   distinguishes "a beat from the section is present" from "the bundle carries
   the mechanics" — what makes the 3B fork defensible.
5. **Define the 3B fork decision rule** (which census % + sufficiency result →
   which of the 4 branches) *before* running; run the census; then the 3C
   oracle A/F re-run as the sufficiency gate.

## The One Thing to Do First

Re-run the full 545 on current code and commit the results to the repo — the
single action that turns X1's closing number from a stale 98.7% into a
measured 99.08%, and a prerequisite to trusting any P3.A / 3B decision.

---

## Verification appendix (standing rule 1)

- **VERIFIED** `git log`: `dedb949` and `a5e93c3` in the trail; tip `10729b0`.
- **VERIFIED** `tools/census_545.py` (8,981 B) + `tools/census_545_pairs.json`
  (77,309 B, 545 rows) tracked; `reports/comprehension/STEP5_CENSUS_545.md`
  (4,817 B) on disk; `STATUS.md:1101` carries the "545 census" milestone.
- **VERIFIED** `facts.db` `abilities` table = **594 rows**, keyed by `character`
  (string), not `character_id`.
- **VERIFIED** on-page ability sections carry **mechanics prose**: Gojo
  "Cursed Technique" section = 7,476 chars. → the "false-green" fear is
  overstated for the on-page census (5th reviewer + peer reviewer 5).
- **VERIFIED** `sections ⋈ documents` (character + character_synopsis): the
  five ability titles total **300** distinct (dimension, page) rows;
  "Abilities and Powers" (level 2) is the **parent** of Cursed Energy / Cursed
  Technique / Intelligence / Physical Prowess (level 3) → the 300 pairs are not
  disjoint.
- **VERIFIED** `tools/census_545.py:65` hardcodes `DIMS` to the five prose dims.
- **STRUCK (as a peer reviewer stated it):** "STEP5 records a post-fix full
  545 re-run (7→5)." STEP5 §80-94 states a re-run *would refresh* 7→5; the
  global table still reads 7, so the re-run was **not committed**. Corrected
  claim: re-run + commit is still owed (Contrarian's Hole 2 stands).