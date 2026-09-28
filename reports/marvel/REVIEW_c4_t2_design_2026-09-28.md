# Architect review: `DESIGN_c4_t2_passages.md` (C4 T2), 2026-09-28 ~08:3x

Verdict: **APPROVE THE MECHANISM, REJECT THE SCOPE.** The passage model is sound:
- fact keys declared in `overrides.yaml` (`narrative_fact_keys`, fnmatch, case-insensitive);
- generic lead passages;
- the ≥2-character audit routed as `under2`;
- the `passage` column with the migration and the remap re-anchor;
- no series names in `.py`;
- tests, then the four gates.

Keep all of it. But the design sizes the problem at roughly 5% of MCU's prose. Under the owner's 100% definition ("every single line … understood, recallable and traceable … nothing left anywhere", SWITCHPOINT round 7), it is not complete.

## R1 (blocking): heading-agnostic scope; every prose section is read

`--scope all` still only reads sections whose heading passes `is_narrative_heading` (the `NARRATIVE_SECTION_TITLES` list or "… arc"), plus the placement and `under2` sets. Measured on the stores (architect, SQL over `sections` × `_excluded_section_titles()`):

| series | sections | NOT narrative-titled and not furniture | words never read in ANY scope |
|---|---:|---:|---:|
| mcu | 187,342 | **148,710** | **11,568,192** |
| marvel | 69,829 | **68,577** | **11,530,346** |

- **MCU top titles:** External Links 24,020 · Biography 5,115 · Relationships 5,041 · Allies 4,523 · Appearances 4,265 · Enemies 3,473 · Dialogue 2,811 · Behind the Scenes 1,902 · Facilities 1,855 · Abilities 1,699 · Equipment 1,623 · Aftermath 1,447 · Family 1,389 · Vehicles 1,249.
- **Marvel top titles:** Comics 2,114 · Interior Art 2,113 · Publication Notes 1,222 · Origin 1,168 · Chronology Notes 939 · Early Life 916 · Screenshots 908 · Continuity Notes 904 · Cover Art 841 · Origins 800 · Modern Age 684 · Legacy Numbering 465 · Alternate Realities 452.

MCU character biographies are split into story-named sub-sections (for example "Battle of Sokovia"); the same shape as Marvel's "Civil War" / "Early Life". A heading allow-list cannot reach them.

**Required:**
1. `all` = every section carrying prose. Heading-agnostic, with the extractable-prose test decided on content, not title.
2. Exclude only an explicit, per-wiki-declarable **furniture** list (link lists such as External Links, galleries, image-only sections, references). Every excluded section is counted in the dry-run and the receipt, by heading, with a named cause.
3. List-shaped sections (Allies / Enemies / Appearances / Family / Equipment) are text too. Either the extractor reads them (relations / standing-state rows), or they become a named class with counts that the council rules on (plan C5 `relations`). They are never silently skipped.

## R2 (blocking): no silent thresholds

Three guards currently drop text without accounting for it:
- the 20-word guard (leads, fact values, sections);
- the ≥40-word lead measurement;
- the junk-key drop (`synopsis    header`, `synopsis¿5`).

Each guard must report, in the dry-run and the receipt, how many passages and words it excludes and why. Anything with real prose is read. A true floor (pure markup, an empty template stub) is a named, counted class for the council, never silence.

## R3 (blocking for D4/D6): time axis, not `temporal=0`

The design calls "unplaceable eventive rows flip to `temporal=0` standing-state rows" "the 100% shape". It is not, on wikis that publish their order.

After placement: `temporal` is **marvel 20/1,149 and mcu 0/6,053**, because `timeaxis.placement_time_axis` only knows manga signals. The deterministic signals are on disk (SWITCHPOINT architect note 06:2x):
- MCU: `date` on 1,287/1,324 conflict/event pages, plus a `previous`/`next` chain (1,281/1,278).
- Marvel: `first`/`last` issue, `part1..N`, and `reality` (one axis per reality, publication order).

T2b is required: an override-declared axis extension, then re-derive `temporal`/`arc_index` on stored rows. The fact passages then inherit their page's axis position, instead of in-value ordinal alone.

## R4: window overlap dedup

4,000-character windows with 300-character overlap will surface the same verbatim quote twice. Dedup on (doc, passage, subject, verb, object, quote) before storing, or the D4 cross-page checks double-count.

## R5: pilot mix

Pilot on the full scope, not only fact values:
- marvel: `history`, `synopsis*`, Origin/Early Life sections, a Chronology/Publication Notes section;
- mcu: Biography sub-sections, Relationships, Abilities, Dialogue, an Allies/Enemies list section.

Record rows per passage and gate-reject reasons per class, plus the batching probe.

## R6: budget framing for the council (coverage fixed)

The honest queue is now:
- MCU ≈ 11.6 M section words + leads;
- Marvel ≈ 11.5 M section words + the ~168 M-character fact values (174k windows) + leads.

That is far beyond "~7 days on 3 slots". The council's job (T4) is throughput: batching (the pilot probe), Qwen dial and slot use, run length, and ordering (event-dense first so D4 rows land early). Coverage is not on the table.

## Next action for the worker

Revise the design for R1–R5 and re-dry-run with the per-class exclusion counts. Then pilot (R5), then the four gates on the code change, then the council (R6). Meanwhile T1 is still open:
- receipts;
- the marvel `story_arc` re-run (15 pages);
- the 2 mcu retries at `SCRIPTENGINE_ANSWER_TOKENS=20480`.

Those are cheap and can run on the free slot now.
