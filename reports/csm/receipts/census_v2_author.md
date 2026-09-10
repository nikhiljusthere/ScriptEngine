# Receipt — census v2 authoring (census_dimensions_csm_v2.json)

Author: worker subagent (authoring only). Timestamp: 2026-09-10 08:10 UTC (13:40 IST).
Task: author one new CSM census file for the 5 new non-character page-type classes;
no census runs, no grading, no `:8000` calls, no file changes except the two outputs.

## Outputs written

- `reports/csm/census_dimensions_csm_v2.json` (UTF-8, 2-space indent, valid JSON)
- This receipt: `reports/csm/receipts/census_v2_author.md`

`reports/csm/census_dimensions_csm.json` (v1) was NOT modified (mtime unchanged:
Sep 9 03:31; git untracked, no diff).

## Shape

- Top level: `meta` + `items` — mirrors v1's top-level shape.
- `meta` keys: v1's seven keys (`series`, `generated`, `seed`, `dimensions`,
  `expect_verified`, `revid_note`, `source`) mirrored, plus the new
  `denominator` field: `{chapter_box: 232, episode: 12, volume_box: 26,
  story_arcs_box: 14, organization: 11}` (owner-provided page counts).
- `meta.dimensions` = `["chapter_box","episode","volume_box","story_arcs_box","organization"]`.
- `meta.generated` = `2026-09-10`.
- `items`: 50 total — 10 per class. Item keys exactly
  `id`, `class`, `subject`, `q`, `expect`, `source` (v1 item shape).
  Ids: `csm-dim-<chap|ep|vol|arcb|org>-NN`, NN 01–10 per class, unique.

## Subjects (10 per class, spread across the class's page range, content-rich)

- `chapter_box`: Chapters 1, 2, 52, 84, 97, 115, 146, 165, 191, 232 (first/last/middle spread).
- `episode`: Episodes 1, 2, 4, 5, 6, 7, 8, 10, 11, 12 (all 12 minus 3, 9 — 9 is the thinnest page).
- `volume_box`: Volumes 1, 4, 9, 13, 15, 18, 20, 22, 24 + "Love, Flower, Chainsaw Guide" (the 26th volume-type page).
- `story_arcs_box`: Introduction, Bat Devil, Eternity Devil, Gun Devil, Katana Man, Falling Devil, Bomb Girl, Justice Devil, Control Devil, War Devil arcs.
- `organization`: Four Horsemen, Chainsaw Man Church, Prophecy of Nostradamus, American Thugs, Tokyo Special Division 5, Yakuza, Devil Hunter Club, Weapon Devils, Anti-Makima Squad, Tokyo Special Division 4.

Each item: one single-answerable factual question about that specific page;
`expect` = 3 verbatim phrases from the page's richest section; `source` cites
`{page, section}`.

## Denominator verification

Owner-provided denominators checked read-only against
`series/csm/facts.db` `documents` table page-type counts:

| class | owner denominator | DB count | match |
|---|---|---|---|
| chapter_box | 232 | 232 | yes |
| episode | 12 | 12 | yes |
| volume_box | 26 | 26 | yes |
| story_arcs_box | 14 | 14 | yes |
| organization | 11 | 11 | yes |

No discrepancy → owner numbers recorded in `meta.denominator` as-is.

## Verbatim verification of expect terms

Method (same spirit as v1): every `expect` term must be an exact substring of
the DB fields v1 verifies against — `sections.text`, `facts.value`,
`abilities.name`, `documents.title` — checked with `LIKE ? ESCAPE '\'`
(wildcards `%`/`_`/`\` escaped in the term), read-only connection.
150/150 terms (50 items × 3) verified 2026-09-10. During authoring, 3
initially-drafted terms failed the check (missing words "then"/"also"/"later"
in the source text) and were corrected to the exact DB phrasing; all pass now.

## Commands run (all < 15 s, no server, no model)

- `sqlite3`/`python3 -c` read-only dumps of section text for the 50 subject pages (scratch files under /tmp)
- `python3 /tmp/census_v2_author.py` — builds the 50 items, verifies all 150 terms against facts.db, writes the JSON only if 0 failures
- `python3 -c` JSON re-parse + shape/id-uniqueness check on the written file

## Note for the parent

A superseded earlier attempt (13:33, untracked) left
`reports/csm/receipts/census_csm_v2_authoring.md` describing a different design
(110 items = v1's 60 copied + 50, `meta.widened`, indent=1). It does not match
this task's spec (50 items, mirrored v1 meta, 2-space indent). Left untouched
(out of scope); safe to delete if the 50-item spec is the standing one.