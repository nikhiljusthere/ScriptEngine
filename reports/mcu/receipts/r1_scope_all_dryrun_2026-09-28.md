# R1 scope-`all` re-dry-run coverage receipt (2026-09-28)

Commit piece: **the page-type scope fix** — the R1 prose scope joins the
`all` scope of the event extraction, heading-agnostic.

Steer: `reports/marvel/REVIEW_c4_t2_design_2026-09-28.md` R1 (blocking):
"`all` = every section carrying prose. Heading-agnostic, with the
extractable-prose test decided on content, not title." The pre-fix
`all` read only sections whose heading passed `is_narrative_heading`,
plus the placement and `corpus` rule sets — so a Biography or Origin
sub-section of an episode, location, organization or character page
was never in any queue (mcu: 148,710 such sections, 11.6 M words,
per the review's own SQL census).

## Code

- `scriptengine/ingest/events.py` (the scope hunks): `scope_plan` under
  `all` now unions placement, corpus and the R1 prose scope
  (`prose_scope` — every prose section of every page type) in that
  order, with a three-way id-dedup a page several rules name reads a
  section once; the `placement`/`corpus` scopes are untouched. The
  `extract_events_series` docstring states the new `all` shape.
- `tests/test_gate.py`: `TestScopePlan::test_all_covers_both_rule_sets`
  now asserts `pages == placement | corpus | prose_pages` (the pre-fix
  two-rule assertion would silently regress the deferral).

## Re-dry-run (model-free, `events-extract --dry-run --scope all`)

Before = the tree without the scope fix (this commit's parent + the
bug-B piece); after = the tree with it. Same stores, same prompt
(`events-2026-09-05.3`); the run calls no model and mutates nothing
(`ensure_events` is a no-op on both stores; the marvel run overlapped
the marvel `recompute_temporal` write, which touches only
`arc_index`/`temporal`/`partition` — none of which the queue reads).

| series | pages before -> after | sections before -> after |
|---|---|---|
| mcu | 3,611 -> **14,869** | 7,732 -> **83,127** |
| marvel | 314 -> **12,434** | 940 -> **51,723** |

Marvel declared narrative fact keys, `in queue` before -> after:

| key | store rows | in queue before | in queue after |
|---|---:|---:|---:|
| `abilities` | 7,319 | 4 | 2,049 |
| `overview` | 4,119 | 10 | 1,931 |
| `personality` | 934 | 0 | 335 |
| `plot` | 227 | 0 | 77 |
| `powers` | 14,817 | 13 | 3,067 |
| `professionalhistory` | 896 | 0 | 56 |
| `properties` | 760 | 10 | 198 |
| `solicit` | 33,529 | 1 | 935 |

The queue is the read plan only — the full-scope `--refresh` run
itself is the council's T4 throughput item (the review's R6: coverage
is not on the table, throughput is). The R2 guard accounting
(per-class exclusion counts in the receipt) and the R7 panel-sentence
coverage check land with their own pieces.

## Store state

None — the dry run reads stores and calls no model; both series'
stores are unchanged by this piece.

## Tests

`tests/test_gate.py` 18/18 green on this tree. (The first run of the
piece window showed 2 TestGateReport/TestCrossPageAgreement fails;
both passed on immediate re-run — they opened the marvel store while
the marvel `recompute_temporal` was mid-write. Re-run clean before
this commit.)