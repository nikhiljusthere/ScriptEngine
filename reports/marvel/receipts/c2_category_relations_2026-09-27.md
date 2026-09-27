# C2 — category → relation edges (L5) — receipt, 2026-09-27

## What landed

The plan's pre-registered L5 mechanism (generic, wiki-agnostic) plus its two
series grammars:

- `scriptengine/ingest/category_relations.py` — matches each distinct category
  name against the series' `category_relations:` override patterns and writes
  the edge (or fact, for property captures) the category states. Targets
  resolve against the store's nodes then aliases: exact = confidence 1.0,
  alias = 0.9, unresolved = counted and skipped, **never invented**. One edge
  per (subject, relation, target) at the strongest confidence. Every edge
  carries provenance `category:<name>` so wiki-filed relations stay
  distinguishable from field-declared ones, and the `--audit` gate samples
  them against the infobox field the rule declares in `contradicts:` — an
  edge the page's own field denies is a **finding**, not a keep.
- `scriptengine/cli.py` — `category-relations --series <s> [--limit N]
  [--audit N]`, run after `index` (which rebuilds the graph).
- `tests/test_category_relations.py` — 10 tests: node edges under provenance,
  alias-vs-exact confidence, property captures in `facts` not `nodes`,
  unresolved skip, no-subject docs, idempotent re-run, rule validation, and
  the four audit outcomes.

## Grammars

`series/marvel/overrides.yaml` — the plan's four patterns (measured against
the G6-final store: 2,582,190 category rows / 212,341 names):

| pattern | relation | rows matched |
|---|---|---|
| `^(.+)/Members$` | `member_of <group>` (target) | 49,244 |
| `^([^/]+)/Creator$` | `created_by <creator>` (target) | 200,375 |
| `^(.+) casualties$` | `event_participant` (kind: casualty, target) | 993 |
| `^(\d{4}) Character Debuts$` | `debuted_year <year>` (value → facts) | 79,625 |

`series/mcu/overrides.yaml` — the plan's four patterns are Marvel-DB
conventions and hit zero on this wiki; it embeds the target in the category
name instead:

| pattern | relation | rows matched |
|---|---|---|
| `^(.+) Crew Members$` | `crew_of <production>` (target) | 19,849 |

`Episodes` (717 docs), `Soundtrack` (2,088), `Interviewees` (626) are
mechanism-ready but their edge direction is a per-wiki judgment: deferred,
recorded in `known_diffs_2026-09-25.md`, not guessed.

## Results (first run, 2026-09-27, G6-final stores)

| series | edges | facts | unresolved | no_subject |
|---|---|---|---|---|
| marvel | **247,543** | **79,625** | 3,063 | 0 |
| mcu | **19,507** | 0 | 342 | 0 |

marvel per-relation: `created_by` 198,177 · `member_of` 48,443 ·
`event_participant` 923 · `debuted_year` facts 79,625 (exact match to the
pre-quantified 79,625 rows). mcu: `crew_of` 19,507 (105 of 119 distinct
targets resolve; the 14 unresolvable productions account for the 342 rows).

**Idempotency verified**: second run on both series is a counting no-op
(marvel `already` = 327,168 = 247,543 + 79,625; mcu `already` = 19,507),
zero writes.

## Audit (marvel, sample 500 of 247,543, deterministic stride)

430 consistent · **70 contradictions** (14%), by relation:

- `member_of` 47 · `created_by` 23
- **22 of 70 are a wiki field artifact, not a disagreement**: the page's
  `affiliation` field is a broken multi-line `Formerly:` list the infobox
  parser renders as the literal string `Formerly:` (or `Formerly:\nand`).
  The category is the page's correct statement; the field is malformed.
  Logged in `known_diffs_2026-09-25.md`.
- The remaining 48 are genuine channel drift — the category files the work
  under one creator (or the character under one group) while the infobox
  field lists a different set (`Peter Gillis/Creator` vs field
  `Peter B. Gillis; Dave Cockrum`). Per the plan's gate these stay findings:
  the edges are kept (the category is the wiki's own statement, and it is the
  channel the plan trusts) and the contradictions are reported here, not
  silently dropped.

mcu has no `contradicts:` key on `crew_of` (this wiki carries no crew
infobox field), so its audit is unauditable-by-design.

## Gate position

C2 is the plan's entry into Phase C's L5 layer; it is deterministic and
model-free (T0), runs after `index`, and re-runs are no-ops. The
contradiction sample above is the standing record; a fresh `--audit` after
any future re-index re-checks the same stride.