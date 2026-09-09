# R-2 engine fix draft — qa-passage leg (G-CSM-2): B verification record

**Provenance note:** the wave-2 R-2 worker (run `0024ad4e`) was killed by its
60-min timeout inside its final test-verification loop, after completing the
code, the tests, and the discrimination checks, and before writing its own
receipt (no `iter1_r2_passageleg_run.md` was saved). This record is B's
post-timeout verification of the on-disk state: the diff below is the
worker's work, verified by B's own runs on 2026-09-09. It stands as the
work record for the §3 council + four gates.

Worker claim (reconstructed from the code's WHY comments + the d5 evidence):
the qa bundle's passage leg evicts the answer chunk at the rerank step —
for every d5 miss row the target chunk was the lexical-rank-0/1 and
RRF-rank-0/2 shortlist entry and survived dedup; the cross-encoder, scoring
topical fit, reordered the shortlist by name-density and dropped the
verbatim-covering chunk. The fix makes the reranker a tie-breaker, not a
veto, for passages that cover the query's own words.

## Diff summary (worker's code, verified by B)

`scriptengine/retrieve/hybrid.py` (+38/−0), in `HybridRetriever.retrieve`:

- After dedup, **re-admission of query-covering passages the cut dropped**:
  `recovered = [p for p in deduplicated[top_k:] if _query_covered(query,
  p.text)]`; when non-empty the tail `len(recovered)` slots are freed and the
  recovered passages fill them **at the tail** (subject-floor pattern) — the
  beam never grows past `top_k`; no new dependency.
- New helper `_query_covered(query, text, threshold=0.8)`: a passage covers
  the query when ≥80% of the query's content words (letters/digits, length
  ≥4, lowercased) appear in it as substrings (deliberate recall direction:
  "devils" covers "devil"). Guard: only sentence-length queries qualify
  (≥3 content words) — short writer questions stay on the pre-fix path,
  where the helper returns `False` (inert).

`scriptengine/stores/facts.py` (+3/−1), `passages_for_subject` floor query:
`WHERE c.level = 2` → `c.level IN (0, 2)` — the subject floor now carries the
document's own level-0 lead card alongside its level-2 section chunks, so a
subject whose key line lives in the lead paragraph is in the floor by
construction (the d5 rows' target lines sit in lead/section prose the beam
missed; the card is the cheapest guaranteed anchor).

`tests/test_retrieve.py` (+122/−0), two new model-free classes:

- `TestQueryCoverage` (4): a verbatim passage covers; case + plurals do not
  break coverage; a topically-similar passage does NOT cover; a short
  question is below the guard (helper inert).
- `TestQueryCoverRecallGuard` (2): a buried verbatim passage (dropped by a
  hostile rerank) is re-admitted at the tail without growing the beam; the
  guard is inert when the rerank already ranks the target (no reorder).

`tests/test_csm_fixtures.py` (+23/−0): the G-CSM-2 debt fixture
("Denji's hybrid transformation trigger, documented only in the lead
paragraph") — now asserted against the floor shape (the level-0 card).

Zero series names in `.py` (the project rule): `_query_covered` and the
floor query are generic; the CSM-specific expectations live in the test
fixtures and the overrides file only. No JJK/OPM file touched.

## B's verification (2026-09-09, model-free, post-timeout)

```
$ pytest tests/test_csm_roster_scoping.py tests/test_csm_fixtures.py \
       tests/test_csm_router_count_rule.py tests/test_ability_owner.py \
       tests/test_retrieve.py -q
74 passed, 2 xpassed in 7.92s      # the 2 xpassed = the G-CSM-1 debt xfails (R-1)

$ pytest tests/test_roster.py tests/test_roster_scoring.py \
       tests/test_roster_validation.py tests/test_ability_class.py \
       tests/test_ability_extraction.py 'tests/test_stores.py::TestPassagesForSubject' -q
159 passed in 8.11s
```

(The worker's own last verified state, per its transcript, was the same
batteries green; B re-ran them after the timeout to confirm the on-disk state
matches.)

## Queue rows this class serves (from the frozen queue, fix_class R-2)

csm-fact-06 (Denji hybrid-transformation trigger, 0 passages pre-fix) + the
13 retrieval-side d5 rows (csmd5-01..07 + gate400-188/189/211/320/490/542,
all verified retrieval-side not chunking-side by the wave-1 override
package). The gate-time class re-sweep (B, after the four gates) re-probes
these rows against the live CPU `:8000`; closure per the amended rule =
≥1 own-new-row HIT or halt to council. Residual risk B flags for the council:
the level-0 floor change is cross-series (every wiki's subject floor now
carries its lead card) — JJK invariance is covered by the four standing
gates (esp. span-recall 48,572 + the 159-test battery), and the re-admission
guard is beam-bounded (no truncation growth).

Council R-2+R-3 addendum (2026-09-09, post-verdict):
- The "zero series names in .py" claim is corrected to **zero series names
  in .py logic**: WHY comments cite queue-row IDs and bug-instance names
  (house convention — comments explain which bug); no branch, string match,
  or default is keyed on a series slug.
- Post-amendment the splice is **capped at top_k − 1** (order-preserving, no
  re-sort): the pre-draft "beam-bounded, no top_k growth" claim was false in
  the L ≥ top_k regime (uncapped splice no-ops at L > top_k, swaps the
  rerank top at L == top_k) — the council's R-2 AMEND 1 closes it, pinned
  by the 17-distractor guard test in `tests/test_retrieve.py`.
- **CJK inertness**: `_query_covered` tokenizes `[a-z0-9]+`, so pure-CJK
  queries score zero coverage and the re-admission leg is inert for them;
  the cross-series inheritance claim holds for the floor leg + Latin-script
  queries only.
- **Zero gate headroom**: the 400-probe floor is exactly the 390/400
  baseline, so a level-0-card composition delta that keeps every line
  reachable passes all four gates green — documented residual (the
  pinned-panel mechanism exists for a pre/post JJK subject-bundle diff if
  the probe wobbles).

## PENDING (B, per the wave rule)

1. Combined §3 council (R-2 + R-3 drafts, one verdict per draft) — run in the
   `council_r2r3` package.
2. Four standing gates, one-copy 150k ordering (stop `:8000` → pytest CUDA →
   eval jjk → restart `:8000` CPU → span-recall jjk 48,572 + 400-probe →
   canon opm).
3. Class re-sweeps: R-2 rows (csm-fact-06 + d5 rows) + R-3 rows
   (csm-set-17/08/01 + csm-char-02/03/01/04/05) against the live service.
4. Selective commit of: `scriptengine/retrieve/hybrid.py`,
   `scriptengine/stores/facts.py`, `tests/test_retrieve.py`,
   `tests/test_csm_fixtures.py` (R-2) + `scriptengine/retrieve/roster.py`,
   `series/csm/overrides.yaml`, `tests/test_csm_roster_scoping.py` (R-3) +
   both records + the council package.