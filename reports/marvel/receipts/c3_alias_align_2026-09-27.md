# C3 — alias & universe alignment (within-wiki, A1b) — receipt, 2026-09-27

## What landed

The plan's C3 within-wiki half (deterministic, no model):

- `scriptengine/ingest/alias_align.py` — reads each disambiguation page's
  list fields (the `disambig_list_keys:` override declares the field names:
  a wiki convention, not an engine fact), parses each `;`-part (first
  non-image line; `<name> from <file>.jpg` stripped; bare image filenames
  file nothing; `X and Y` / `X, Y` joins unpacked), and resolves each
  entry against the store's nodes then aliases (exact = 1.0, alias = 0.9).
  Resolved names are promoted into the `aliases` table; unresolved names
  are counted, written to a `disambig_unresolved` fact under
  `disambig:<page>` provenance, and flagged — never invented.
- `scriptengine/cli.py` — `alias-align --series <name> [--limit N]`.
- `series/marvel/overrides.yaml` — `disambig_list_keys:` (others, related,
  teams, media, main_article1, main_article2). The MCU wiki has zero
  disambiguation pages (measured 2026-09-27), so it declares none.

## Numbers (marvel, G6-final store, 2026-09-27)

| outcome | count |
|---|---|
| disambiguation pages | 606 |
| entries parsed (after `and`/`,` unpacking) | 8,510 |
| image-only parts (filed nothing) | 336 |
| alias rows promoted (run 1 + run 2) | **6,157** (5,845 exact / 312 alias-hit) |
| already present in `aliases` (builder-harvested) | 7,436 |
| unresolved (flagged, not invented) | 746 entries / 742 fact rows / 677 distinct values |

Idempotent: a third run writes 0 rows (7,764 already). Two runs were
needed because run 2 added the `and`/`,` unpacking (203 of the 919
run-1-unresolved values were multi-entity entries that unpack into
resolvable names); the 915 stale run-1 `disambig_unresolved` rows were
deleted before run 2 so the flag set is the post-split one.

## Unresolved class (746)

Bounded, flagged, and recorded as the raw material for the cross-corpus
pass: names the wiki files as referents of a bare term but the store has
no node for — e.g. `A'Lars (son of Thanos)`, `Abomination (Morlock)`,
`Ultron / "Adam Warlock"`, `A.I.M. (Heroes Reborn)`. These are either
missing character pages (gap-fill candidates) or compound/informal names
the wiki itself uses inconsistently.

## Deferred (owner call)

The cross-corpus half of plan §C3 — `marvel` (Earth-616) ↔ `mcu`
(199999) ↔ `cc.db` speakers via explicit `subject_aliases:` override
tables, cross-checked against the MCU-wiki `Appearances` lists — needs
those tables, which do not exist yet. It is recorded in
`known_diffs_2026-09-25.md` and is not scheduled; the 742
`disambig_unresolved` facts are the queryable seed for it.