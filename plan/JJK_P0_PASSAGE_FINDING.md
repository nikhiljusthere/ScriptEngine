# P0 finding — the `passage` column holds passage LABELS, not passage TEXT

**Found 2026-09-29, pre-P0. Read this before any training or any re-extraction.**

## The bug

`events.passage` is a **label/key**, not the text. `ingest/events.py` sets it to
`"lead"` (line 1655), `f"fact:{key}"` (line 1861), or `""` for a section row
(line 1631 / 2352's `label`), and `stores/facts.py` depends on that: the
per-passage replace keys on it (`save_events`, line ~2040, "A passage row
carries no section: its anchor is (arc's page, passage) itself").

So the column is **correct as designed**. What is wrong is my plan's
assumption that it should hold the input text.

## Measured corruption

Every non-empty value is a label, and **none of them is the passage the row was
read from**:

| series | rows | passage empty | passage non-empty | non-empty that are labels | of those, quote found in own section |
|---|---:|---:|---:|---|---:|
| jjk | 2,748 | 2,748 | 0 | — | — |
| marvel | 9,004 | 2,568 | 6,436 | 6,436 | **0** |
| mcu | 13,194 | 12,804 | 390 | 390 | **0** |
| **total** | | | **6,826** | | **0 / 6,826 (100% corrupt)** |

Label values seen: `fact:history` (3,742), `fact:synopsis1` (1,662), `lead`
(500), `fact:solicit` (131), and mcu's 390 × `lead`.

## Why this is dangerous, not cosmetic

A training example is (input passage → label). The **input is not stored
anywhere**. So a naive `passage`-based training set would train on *labels as
inputs* — the model would learn to emit `fact:history` and then hallucinate a
quote, because the quote is no longer grounded in any text it was given. This
silently produces a model that looks trained and is worse than the teacher.

The `section_id` join does recover the true input: for jjk, **2,748 / 2,748
rows recover via `section_id` alone, and 2,748 / 2,748 quotes verify verbatim
in the recovered section.** Both independent join paths (by `section_id`, and
by `doc_title` + `section_ordinal`) agree on the section id for every jjk row,
with zero fan-out. So the input is recoverable for jjk without touching the
column.

## The correction to `plan/JJK_100_PLAN.md`

P0 as written ("rebuild `passage` from `sections`") is **wrong and must not be
run**. It would either overwrite a column the store depends on, or write text
into a column whose semantics are "which passage was this read from".

Corrected P0 — **do not mutate `events.passage`**:

- **P0a.** Build the training/audit corpus as a **derived table or view**,
  `events_audit`, joining `events` → `sections` for the input text. `events`
  keeps its meaning; the text lives beside it, verified at insert time.
- **P0b.** Every row entering it must pass `quoted_in(quote, passage_text)`
  against the joined section. A row that fails is excluded and counted, never
  stored with a guessed input.
- **P0c.** For jjk, path `section_id` alone is sufficient (2,748/2,748, 100%
  verified, no fan-out). Do not use the ordinal fallback for jjk.
- **P0d.** The 6,826 label-valued rows in marvel/mcu are **not** to be "fixed"
  by overwriting. They are the majority of marvel's rows. Treat clearing them as
  a separate, council-ruled decision — the store's per-passage replace may
  depend on those labels. **Out of scope for JJK.**

## Also corrected

- `passage` is **not** empty on all rows. jjk: 2,748/2,748 empty. marvel:
  2,568/9,004 empty, 6,436 label-valued. mcu: 12,804/13,194 empty, 390
  label-valued. My earlier "empty on all 22,666 rows" was wrong.
- mcu's real row count is **13,194**, not the 10,581 I quoted earlier; the
  store has grown since (a `crawl_mcu_delta_0929` run). Any percentage computed
  against 10,581 is wrong.
