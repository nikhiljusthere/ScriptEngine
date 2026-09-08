# CSM-2 — scoreboard generalized + every CSM page type classified (2026-09-08)

Council item 2 (5.1 + archetype mapping merged). Raw receipts.

## What landed

- `series/csm/overrides.yaml` — `page_scope` (all 13 store types: 5 in-scope,
  7 excluded-in-writing with one-line reasons, `unknown` defaulting to
  excluded), `unknown_pages` (all 14, each classified or excluded in
  writing: 4 in — Contract / Hell / World / Aging's World; 10 out —
  list/author/meta/release pages, JJK precedent), the reusable `archetypes`
  schema (9 archetypes, `depth_floor` declared 1 for in-scope, 0 for
  release — deeper floors set by the CSM-6 census, never guessed), and
  `remainder_note` (the report's paragraph, kept out of the tool).
- `series/jjk/overrides.yaml` — the same keys encoding the retired
  hardcoded behavior verbatim (the six legacy in-scope types, the 11
  unknown pages with `Jujutsu Regulations` as the lone in-scope one, the
  former paragraph as `remainder_note`).
- `tools/coverage_report.py` — `IN_SCOPE_TYPES` / `IN_SCOPE_PAGES`
  retired; scope loaded from the series' overrides via the engine's
  `load_overrides`; **exit 3** on (a) a series with no `page_scope` at
  all, (b) a store page_type not classified, (c) an `unknown` page
  without a per-page disposition. No series name in the tool.
- `tests/test_coverage_scope.py` — 7 tests: the violation paths
  (unclassified type, undisposed unknown page), the in-scope predicate,
  the missing-`page_scope` error, the CSM whole-store check (537 pages,
  0 violations, in-scope = 227, the 14 unknowns all disposed, the 4
  in-scope ones flagged), and the JJK legacy-encoding regression.

## Done-criteria (council item 2), raw

| criterion | result |
|---|---|
| `coverage_report --series csm` denominator = 537 | `csm: 0/537 pages (0.0%), 0 questions; in-scope content remainder 227; orphans 0.` (exit 0) |
| 0 unclassified | `scope_violations == []` (test `test_csm_scope_classifies_the_whole_store`) |
| 0 unknown-type pages unresolved | the 14 unknowns all in `unknown_pages` (same test); the report's `unknown` row lists the 4 in-scope names |
| in-scope content remainder | **227** = 175 character + 22 character_history + 12 episode + 11 organization + 3 establishment (type pages) + 4 unknown (Contract, Hell, World, Aging's World) |
| `--series jjk` output byte-identical | `diff` of regenerated vs committed `COVERAGE.md` **empty modulo the `Generated:` line** (2026-09-08) |
| non-zero-exit path | `coverage_report opm` → **rc 3** (`no 'page_scope' declared in series/opm/overrides.yaml` — the six non-campaign series stay out of scope until P6; the error names the fix) |
| CSM scope test in `tests/` | `tests/test_coverage_scope.py` — 7/7 |
| pytest | **1249 passed** (1242 baseline + 7 new), 0 failed (CPU run 2026-09-08; the official GPU re-baseline is `reports/csm/GATE_REBASELINE.md`) |

## Notes for the record

- The CSM scoreboard is `reports/csm/COVERAGE.md` (regenerated, committed;
  the JJK one stays at the default path). CSM starts at 0/537 covered —
  no CSM page batches exist yet; the closure loop (CSM-7) is what
  authoring/coverage happens against.
- Other series (bleach/db/hxh/onepiece/opm/berserk) have no `page_scope`
  yet: the tool exits 3 for them by design (silence = error). Declaring
  their scopes is P6 cross-corpus work.
- Archetype depth floors are the *declared minimum* (1 content section);
  the D2 floors the campaign actually enforces per archetype are set when
  the CSM-6 census runs (council item 6: "a dimension is scheduled only
  when its consumer column names a real query and its acceptance column
  names a test that can fail").