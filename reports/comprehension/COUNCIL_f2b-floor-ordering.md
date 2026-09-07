# Council 14 — F2b: the floor-ordering / budget-eviction fix

Record: the full council transcript (5 advisors → 5 peer reviewers → chairman).
Ledger row: `COUNCIL_HISTORY.md` #14. Companion diagnosis: `F2_HISTORY_PROBE.md`.

## Framed question

How to fix **F2b**, a retrieval gap in ScriptEngine's JJK QA context builder.
A 6000-token QA bundle has a **BEAM** (top-K cross-encoder-reranked passages,
walked first, hard break on budget) and a **FLOOR** (the subject's own page's
sections in wiki order, walked after the beam, filling leftover). For
high-degree subjects a "history of X" question misses the subject's own History:
the floor walks ~23 duplicated main-page beats (Appearance ×4, Personality ×8,
Abilities ×7) and burns all 5985/6000 tokens before the subpage History (the 15th
floor beat) is reached, so it is evicted. Candidates: **(C1)** re-rank the floor
by query-term overlap (order only, beam untouched); **(C2)** cap per-section
floor duplication; **(C3)** defer to the 545-pair census. Constraints: no
retriever-parameter tuning to dodge; **B1** (the beam's cross-page contribution,
gated by eval 31/31) preserved; method is "diagnose root cause, fix the gap,
never rephrase to dodge."

## The five advisors

- **Contrarian:** all three fiddle with the floor's tail; the root cause is
  structural — the walk is beam-first with a hard break, so the floor gets
  *leftover* only, and for high-degree subjects it never completes. C1 is
  "a dodge in a suit" (a new query-dependent tunable surface); "subject name as
  a signal" is inert (every first sentence says the name). Fix: **reserve a
  minimum floor budget (trim the beam) + de-dupe within the floor**, query-independent.
- **First-Principles:** the floor is a recall net, not a relevance mechanism; its
  value is *which distinct facts* it guarantees, not every sub-chunk. Reordering
  a bloated dump just moves the eviction. Root cause = the floor is **unbounded**
  (every sub-chunk of every section in wiki order; main-cast footprint > 6000).
  Two-pronged: **(1) make the footprint fit** (de-dup/cap first), **(2) then order
  by query relevance**. Reject deferral; fix the *class*.
- **Expansionist:** do C1 + C2, don't defer. The class is the upside: a
  **query-aware floor** (generalizes to every query shape, series-agnostic) that
  *composes* with the beam (breadth + depth) instead of a zero-sum fight. Use the
  census as the *acceptance test*, not a reason to defer.
- **Outsider:** the 8 "Personality" chunks are a **chunker symptom**, not a
  retrieval one — if the chunker fragments a section, reordering a bigger pile of
  junk won't help. C1 "retires the floor" (a second, weaker beam). Wants: F2b's
  definition, the section→beat invariant, and whether eval survives C1 or only C2.
- **Executor:** ship C1 today — one sort key in `context.py`, ~1 hr, gate
  pytest→eval→re-probe. C2 is the wrong lever (root cause is order, not volume).

## Peer review (anonymized A–E; B = Executor)

Unanimous: **B has the biggest blind spot** — (a) "order not volume" is wrong
(reordering an over-6000 floor just moves the cliff), (b) "beam untouched →
B1/eval holds by construction" is a **non-sequitur** (reordering the floor
changes the bundle for *every* question → eval must be re-gated empirically),
(c) "subject name as a strong signal" is inert. Strongest: **E (First-Principles)**
×3, **C (Contrarian)** ×2. **All five missed the same things**: the token
arithmetic (does the fix put History *within* budget?), a B1-safe budget split,
a cheap evidence step first (dump the beam/floor token split), and
**verify-before-fix on the section→beat invariant** (`span-recall`) — the 23
beats may be chunker *fragments* (→ a chunker fix, not a floor-side cap).

## The recommendation (chairman)

A **two-stage, floor-side, query-independent fix, funded by shrinking the floor's
own bloat — never by trimming the beam (B1-safe)**:

1. **Stage 1 (load-bearing): make the floor's footprint *fit* the budget.**
   De-duplicate it so it guarantees *distinct facts*, not repeated sub-chunks.
   Query-independent, B1-safe, closes the class.
2. **Stage 2 (value-add): only once the footprint fits, order the floor by
   query-term overlap** (section-title + first-sentence terms, wiki order as a
   stable tiebreaker) as a **fixed sort key, not a tunable surface** (a title
   mismatch is fixed by widening the matched-term *class*, never a per-question knob).
3. **The exact de-dupe strategy** (de-dupe-against-beam vs. cap-section-chunks vs.
   main/subpage de-dup) is chosen **from beat-composition evidence, not assumption**.

Reject C3 (dodge). Reject "ship C1 today" (a partial fix on false gate-safety).
Reject trimming the beam (violates B1). **Gate: re-gate eval (do not assume
31/31) + a targeted non-history re-probe + the Yuji re-probe + repeat on the other
7 high-degree subjects.**

## The one thing to do first (pending)

Instrument the F2b repro: dump per-beat token offsets (beam + floor), the
beam/floor split, and the break point for **Yuji + the other 7 high-degree
subjects**, and cross-check the section→beat invariant via `span-recall` —
classify each of the 23 "duplicated" beats as **(a) beam-duplicate, (b) chunker
fragment of one section, or (c) main/subpage overlap**. This confirms the
eviction, supplies the missing token math, and picks the recall-safe de-dupe
strategy *before* a line of fix code is written.