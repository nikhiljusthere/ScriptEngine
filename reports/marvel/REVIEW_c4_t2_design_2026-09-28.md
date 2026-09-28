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

---

# Architect finding on the T1 output (`ab5ab727`), 2026-09-28 ~09:0x: PARTICIPANT RESOLUTION (blocking before the large T2 run)

The T1 receipt's numbers match the stores:
- marvel: 1,221 events on 128 pages, so 85 are zero-event pages; 79 on the axis;
- mcu: 6,108 events, failed = 0; Battle of Wakanda 43, Infiltration into Westview 12.

Verifying *what* the rows point at turned up three defects. They must be fixed before the ~178k-passage run, or that run stores mostly mis-attributed rows.

## P1 (blocking): marvel participants resolve to the wrong entity

`known_participants` maps a bare lower-cased name to one node, with no reality awareness. Measured on the stored rows:
- **589 of 1,221 marvel event rows (48%) have a participant resolved to a DISAMBIGUATION page.** "Captain America", "Spider-Man" and "Peter Parker" are all `page_type=disambiguation` nodes.
- Others resolve to arbitrary alternate realities: "Conan" → `Conan (Earth-16356)`; "Kulan Gath" → `Kulan Gath (Impostor) (Earth-2099)`; inside the Earth-616 "Secret Invasion (Event)", participants land on `Khn'nr (Earth-10021)`, `Cobalt Man (Robot) (Earth-12041)` and `Beast (Alien) (Earth-616)`.

The FK gate passes (a node exists), so nothing flags it. Required:
1. **Reality-aware resolution.** The candidate set is the matching node, plus the disambiguation page's `main_articleN` targets (C3/A1b alias-alignment data already on disk), plus aliases. Pick the variant whose reality matches the passage page's reality (the title suffix, or the page's `reality` fact). A wiki-level default reality only where `overrides.yaml` declares one.
2. **Never guess.** An unresolvable ambiguity is stored as an explicitly ambiguous participant with its candidate list (a counted class for the council), not silently pinned to one variant and not dropped.
3. **Re-resolve the stored rows** with the new resolver. The quotes are kept, so no re-extraction is needed. Report before/after: rows on a disambiguation node, rows cross-reality.

## P2: mcu main character pages typed `list`

MCU's `Infobox List` template types **430 pages / 3.04 M words** as `list`. That includes Thanos (18,892 words), Gamora, Mantis, Adam Warlock and Knowhere: main articles. 3,656 of 6,108 mcu event rows touch these pages. Separately, "Tony Stark" is an unresolved node (the wiki titles the character differently).

Required: establish what `Infobox List` means on this wiki (a multi-version character hub?) and fix the typing through `type_aliases` in `series/mcu/overrides.yaml` if these are character articles. Resolve the name gaps through the alias data. Report affected rows before/after.

## P3: rejection accounting is silent

`extract_from_sections` drops candidates at INFO level: missing end / verb outside `EVENTIVE_VERBS` (no log at all), "unknown participant", "unquoted". The CLI does not show INFO. So the receipt cannot separate "the page states no event" from "every candidate was rejected", and the 85 zero-event marvel pages include "Civil War II", "Spider-Verse", "Secret Empire", "Infinity Gauntlet (Event)" and "Hyborian Age" (1,010 words).

Required: per-page counters for candidates proposed / kept / dropped by reason, in the run report and the receipt. Then re-account the 85 pages. A dry accounting pass on a sample with INFO logging is fine before the counters land.

---

# Review of `55c2cb9e` (R1/R2/R4 + P1 code + R3 scaffolding), 2026-09-28 ~11:1x

**Accepted as a safe checkpoint.** 131 tests pass (architect re-run: test_events_passages + test_stores + test_timeaxis + test_gate).

One fix before P1 is run on the stores:

## R8: the reality pattern belongs in overrides, not `.py`

`events.py:775` hard-codes Marvel's naming convention: `_REALITY_SUFFIX = r"\((?:[Ee]arth|[Tt]ierra)-?([\w-]+)\)\s*$"`. CLAUDE.md: "if a fix mentions a series name [or a series' convention] and lives in a `.py` file, it is in the wrong place." The resolver *logic* is generic and correct. Only the pattern moves:
- declare it in `series/marvel/overrides.yaml`, for example `events: reality: {title_pattern: '\((?:Earth|Tierra)-?([\w-]+)\)\s*$', fact_key: reality}`;
- the engine reads the declared pattern, and a wiki that declares nothing gets no reality partitioning (MCU, JJK unchanged);
- add a test with a non-Marvel pattern, to prove it is data-driven.

---

# Survey findings for the worker (architect, `franchise_kit/tools/survey_wiki.py --series marvel`), 2026-09-28 ~12:0x

## R9 (100% scope): `narrative_fact_keys` must cover every long prose fact, not only `history` + `synopsis*`

Long prose fact values on marvel (rows / total chars):

| key | rows | total chars | note |
|---|---:|---:|---|
| `solicit` | 33,529 | 13.0 M | publisher solicitation text, comic issues |
| `powers` | 14,817 | 6.7 M | the abilities dimension |
| `abilities` | 7,319 | 1.4 M | the abilities dimension |
| `overview` | 4,119 | 1.6 M | |
| `personality` | 934 | 0.57 M | |
| `professionalhistory` | 896 | 0.47 M | |
| `properties` | 760 | 0.58 M | |
| `plot` | 227 | 0.78 M | |

Under the owner's 100% definition these are lines too. Declare them, or route `powers`/`abilities` to the `abilities` pass under a council sequencing ruling (never silence). Report per-key covered/total in the dry-run.

## P4 (typing): slash-titled comic crossovers treated as subpages

**306 marvel pages across 303 junk `page_type` ids** of the form `disambiguation_<...>`. Examples:
- `Avengers/Defenders War Vol 1 1`: `infobox_template` = `subpage of Avengers`;
- `Captain America/Iron Man Vol 1 1`: `page_type` = `disambiguation_iron_man_vol_1_1`.

Crossover issue titles contain `/`, so the subpage heuristic reads "Avengers" as a parent page. MCU uses `/` for genuine subpages (`Wanda Maximoff/Relationships`), so the fix must be generic. One option: treat `/` as a subpage separator only when the prefix is an existing page AND the suffix is not itself an infobox-bearing page title shape, or make the separator rule declarable per wiki. Small (306 pages / 28k words) but these comic issues miss comic handling; fold into P2's typing pass.

---

# Architect note, 2026-09-28 ~17:0x (after the owner's PC restart; nothing lost: the worker's `timeaxis.py` +435 lines are on disk, uncommitted)

**Wiring defect in the committed checkpoint `55c2cb9e` (found by the worker itself on resume):** `extract_events_series` still passes section rows and the flat `known` dict to `extract_from_sections`, which after P1 expects passage dicts, the candidate-set dict and `page_real`. Any `events-extract` run on `55c2cb9e` fails. The 131 green tests call `extract_from_sections` directly, so they never exercised the series driver.

**Required with the fix (T-gap):**
- an integration test driving a stub LLM through `extract_events_series`, from a tiny store to stored rows, for each passage kind (section, `fact:<key>`, lead) and the ambiguous-participant class;
- a CLI `events-extract --dry-run` smoke on a fixture store.

**No `events-extract` run (not even a pilot) until the fix + these tests + the four gates are green and committed.**

---

# Architect review of the MCU pilot rows, 2026-09-28 ~22:5x (SQL + code)

**(A) Data-loss bug: section rows store the section title in `events.passage`.**
- Observed values: `Plot`, `Battle of Titan`, … The committed design is `''` for sections, `lead`, `fact:<key>`.
- `facts.py` remap treats any non-empty `passage` as section-less. `passage_source()` then returns `''`, so the quote check fails and the row is dropped as unverified at the next re-index.
- **Impact:** all 231 MCU pilot rows, and every section row of the full run, would be lost on rebuild.
- **Fix:** the writer, or title-aware remap keying. Add a survives-`--force` test and repair the stored rows.

**(B) MCU ambiguity (~27% of pilot rows) is a candidate-set bug, not real ambiguity.**
- Bare names fold in variant subpages and hubs:
  - `Thanos` → `Hub:Thanos | Thanos | Thanos/Earth-838 | …`
  - `The Avengers` → `The Avengers | The Avengers (comic) | The Avengers/Home Video`
- Rules:
  - an exact title match wins over `(qualifier)` and `/subpage` variants;
  - a variant subpage is a candidate only when the passage links to it, or when the passage page is that variant;
  - hub pages (declared per wiki) and disambiguation pages are never participants.

## R10 (BLOCKING, architect 2026-09-29 ~00:45): Marvel's two biggest story keys are undeclared, and fact-only pages never enter the queue

R9's heading assumed `history` + `synopsis*` were already declared. They never were: `series/marvel/overrides.yaml` `events.narrative_fact_keys` lists only the eight R9 keys, and `narrative_fact_keys()` has no default. Measured on the live store (read-only):

| key | rows | chars | fact-only (400-row sample: text in no section of its page) |
|---|---:|---:|---|
| `history` | 127,035 | 106.7 M | 358/400 rows, 58% of chars |
| `synopsis1` | 22,952 | 47.9 M | 398/400, 99% |
| `synopsis` | 3,307 | 5.0 M | 359/400, 78% |
| `synopsis2..N` | ~12k | ~9 M | 394/400, 99% |

So the `all` queue as committed at `45d18b17` skips most of the comics' story. MCU has no such key (its long prose is in sections); only `book` (1,332 rows / 0.23 M) is a candidate there.

Second defect, same root: `fact_passages()` runs only for pages already in the queue, and the page queue is built from sections. A page whose story lives only in fact values (Children of the Comet (Earth-616): `history` 3.6k chars, 0 sections) is in no queue. The R9 census shows the effect: `solicit` 935/33,529 in queue, `powers` 3,067/14,817.

Required:
1. Declare in `series/marvel/overrides.yaml` (data, not code): `history`, `synopsis*` (fnmatch), `weaknesses` (abilities dimension, 3,938 / 0.85 M), `alternateversions` (198 / 0.41 M). For `notes`, `trivia`, `pointsofinterest`, `others`, `related`, `appearances`: declare them, or list them under a new counted exclusion key (inert default) with a one-line reason each. Never silence. `appearing*` lists are roster/structure (C1), not prose; record that in the receipt.
2. `scope_plan('all')`: a page with any declared fact value that holds a panel-eligible sentence joins the page queue (generic; no series names in `.py`). A test: a fact-only fixture page is in `all`.
3. Re-dry-run Marvel: per-key `in queue == prose` for every declared key (100%), plus the new page/section/fact-passage totals. Amend the `r1_scope_all_dryrun` receipt, or write a new one.
4. JJK/CSM stay byte-identical (they declare no fact keys; prove the `all` page list is unchanged on jjk).
5. Then the four gates, once, on the final tree.

## R11 (architect 2026-09-29 ~01:10): the full-run throughput wall, and what the pilot must measure

After R10 the read plan is Marvel 179,276 pages / 51,723 sections / 225,045 fact passages, plus MCU 14,869 pages / 83,127 sections. At the MCU pilot's measured **14.36 s/passage** (workers=2; `/tmp/se_p2/mcu_pilot_report.json`: 51 passages, 732 s, 4.5 rows/passage), about 360k passages take about 5.2M s, **about 60 days** on one card. Coverage is not the variable (R6); throughput is.

The shape of the work (Marvel declared fact values, 233,973 rows, 194 M chars): **median 281 chars, p90 1,881, p99 7,804; 87% under 1,500 chars.** For those, per-call overhead (system prompt + the reasoning preamble) dominates, not the passage. The earlier "batching gave no gain" measurement was on section passages, so it does not rule out packing short fact values.

The Marvel pilot must measure, on one fixed, seeded sample (e.g. 60 section + 140 fact passages, stratified by length), each lever **alone** and then combined, with s/passage, rows/passage and a row-level diff against the lever-free baseline:
1. **Concurrency:** Qwen `--max-concurrency` 3 → 4/6 (the `qwen-switch` profile; KV headroom permitting), `--workers` to match.
2. **Packing:** several short fact values of one page (the same page, the same key family) in one call, each keeping its own `passage` anchor (`fact:<key>`, value order) so the remap still verifies every row's quote. A generic mechanism with an inert default (pack size 1).
3. **Reasoning budget:** thinking capped or off for fact passages under N chars. It must show a row-set diff within tolerance against the baseline (the council sets the tolerance); never adopted on speed alone.

Adopt only what the diff proves. Report the projected full-run days for each combination to the owner; the owner picks from measured numbers. No full run before that.

## R12 (architect 2026-09-29 ~02:00): model trial measured; the resolver, not the model, is the quality gap

Same 160 seeded-random pages of the Marvel `all` queue (285 passages), workers 8, row sets in `/tmp/se_p2/marvel_tput_rows_{ninfer,unc}.json`:

| | ninfer Qwen3.8-27B, thinking low | uncensored Qwen3.8-27B (SGLang), thinking off |
|---|---:|---:|
| wall | 1,150 s (4.04 s/passage, Beast tail) | **358 s (1.26 s/passage)** |
| rows | 471 | 481 |
| rows with both ends resolved | 292 | 237 |
| ambiguous (kept) | 210 | 301 |
| dropped unknown participant | 217 | 259 |
| unquoted / incomplete | 3 / 2 | 0 / 0 |
| pages with rows | 66 | 80 |
| failed pages | 0 | 1 (empty reply, retryable) |

Row agreement is 42%; neither set contains the other. A read of 16 rows from each model's disjoint set: both make some extraction mistakes (ninfer read a powers sentence, "Hank … immunity to tranquilizers", as `met` Kravinoff), but **most wrong rows in both are resolver errors**:
1. `Henry McCoy` → `Henry McCoy (Clone) (Earth-616)`: on a wiki whose titles all carry the reality suffix, "exact title wins" never fires. Rule: the candidate whose title minus the reality suffix equals the mention, with no extra qualifier, wins.
2. `Hank` → `Blast-Hands (Hank) (Earth-616)` on Henry McCoy's own page: the page's own entity must win for its own names, aliases and nicknames.
3. `Character Index/M` as a participant: an index page. Declare it in marvel `participant_excludes` (data).

**Blocking for the full run: rows store the resolved name, not the model's mention.** A resolver error is baked in, and fixing it means re-extraction (days). Store the raw `subject_mention`/`object_mention` on every row, so `re_resolve_participants` can repair any resolver change in minutes.

Throughput verdict: thinking-off is 3.2× faster at comparable extraction quality on this sample. Adopt it for the full run once (a) raw mentions are stored, (b) resolver fixes 1–3 land, and (c) a re-run of this sample shows the resolved-both-ends share at or above ninfer's. Packing (`SCRIPTENGINE_EVENTS_PACK_CHARS`, `1cde6013`) is measured on the same sample next.
