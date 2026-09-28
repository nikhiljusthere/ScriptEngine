# MCU 231-row pilot repair receipt (2026-09-28)

Commit piece: **bug A — the section-passage writer/remap fix + the 231-row
repair**.

## The bug (A)

`_section_passage` (scriptengine/ingest/events.py) wrote the section's
`title` into the row's `passage`. The committed contract (remap side,
`facts.remap_derived`): a section row carries `passage = ''` and is
re-keyed on `(doc_title, section_ordinal)` at rebuild; any other
non-empty value is dropped as unverified (it has no section/quote
verification path). The 09-28 pilot (prompt `events-2026-09-05.3`,
`extracted_at` 17:00) therefore stored 229 section rows with
`passage = <section title>` and `section_ordinal = 0` — the 21:36
re-index only *kept* them by luck (quote + doc_title still verified);
the next `--force` rebuild would have dropped all 229.

The writer now keeps the `''` marker:

```python
def _section_passage(section):
    return (title, "")
```

and `durable_of`/`save_events` derive the ordinal correctly for
`passage = ''` section rows again.

## The 231-row repair (series/mcu/facts.db, untracked)

Pilot cohort: 231 rows (`extracted_at` 2026-09-28T17:00, prompt
`events-2026-09-05.3`) — 229 section rows + 2 lead rows (the leads were
already correct: a lead-section event carries the `passage='lead'` marker
with `section_id` NULL — the lead is the intro before the first heading,
not a section — and the remap verifies it against the page's lead text,
so it survives the rebuild).

| step | effect |
|---|---|
| 229 section rows re-keyed `passage title → ''`, `section_ordinal` set from `sections` | 222 rows moved off ordinal 0 (7 pilot sections genuinely are the page's first section, ordinal 0) |
| 13 old-side rows deleted | 09-27 same-prompt siblings whose PK `(…, passage)` collided with the re-keyed pilot rows; the fact survives on the pilot side |
| 2 intra-pilot ambiguous pairs kept | distinct facts sharing a key only via SQLite NULL semantics |
| **net** | **6,339 → 6,326 rows** |

Verification, post-repair (live store):

- `passage = <its own section title>` rows: **0** (was 229).
- every re-keyed row verifies its quote + `doc_title` under the remap
  gate → all 231 rows survive a `--force` rebuild (re-keyed on
  `(doc_title, section_ordinal)`).
- new test `tests/test_events_passages.py` (the pilot-shaped rebuild:
  `build_passages` → `save_events` → `remap_derived`) pins the writer
  contract, so the bug cannot silently regress.

Pre-repair backup (not committed, ~870 MB):
`/tmp/se_p2/mcu_facts_pre_repair_20260928_2313.db`.

## Store state produced

`events` 6,339 → **6,326**; placed `arc_index` rows 6,110 → **6,097**
(the 13 deleted collision rows were placed); 0 bad title-passage rows.
Hub-pointing rows (236 at repair time) are a bug-B matter — re-resolved
store-wide by the later commit; see `bug_b_re_resolution_2026-09-28.md`.

## Tests

`tests/test_events_passages.py` green; full suite at commit time
`4 failed, 1,419 passed, 2 xpassed` (the 4 = known environmental set).