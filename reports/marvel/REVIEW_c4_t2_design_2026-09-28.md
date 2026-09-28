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

---

# Rev 2 review (`399c6ec6`), 2026-09-28 ~08:4x

**Verdict: APPROVED with one binding amendment (R7).** R1–R5 are addressed:
- a heading-agnostic prose scope, with explicit furniture counted per heading;
- guard accounting;
- an override-declared store time axis (date / chain / order / partition), with `temporal` re-derived on stored rows;
- overlap dedup, with `passage` added to the PK;
- the full-scope pilot mix.

Proceed to code + tests with R7 folded in.

## R7 (binding): the "understood" denominator is the D3 panel's line definition

Rev 2 keeps a **20-word section floor** ("below-floor, a counted class"). But the 100% denominator (D3, the pinned tier-1 panel) counts every sentence of **≥6 words** (`span_recall.sentences(min_words=6)`). A short section holding one real sentence is a line in the panel, so the extractor must read it. Measured (architect, `strip_markup` + `sentences(min_words=6)` over `sections` with `word_count < 20`):

| series | below-20w sections | with ≥1 panel-eligible sentence | sentences hidden by the floor |
|---|---:|---:|---:|
| mcu | 111,533 | **20,178** | **21,010** |
| marvel | 20,420 | **3,336** | **3,497** |

**Required:**
1. **Prose test = "contains ≥1 panel-eligible sentence"**, the same `sentences()` function and `min_words` the panel uses. Not a 20-word section floor. The same rule applies to leads and fact values. The short passages batch naturally (the council's R6 batching lever), so this costs little.
2. **Mechanical D6 coverage check (the checkable 100%):** every panel sentence (and every tier-0-eligible sentence on the store) must lie inside a passage the extractor read, or inside a named furniture/floor class. Report `covered / total` per series in the dry-run and the receipt; the target is 100% with every exception named. This is the "understood" twin of D3's "recallable" number, over the same denominator.
3. Whatever is still below that rule (no ≥6-word sentence: pure markup, link stubs) remains the counted `below_floor` class, as rev 2 already specifies.
