# Changelog

Dated log of changes made through prompt-driven work sessions on this project.
Newest entry first. Git commit history (`git log`) remains the authoritative
record of code changes; this log exists to track intent and doc/workflow
changes at a coarser grain, including things that don't map to a single
commit.

## 2026-08-17 (continuation session)

### P0: jjk-set-10 gold corrected against the wiki — dedupe regression resolved

- Corrected `jjk-set-10` (`What are Satoru Gojo's named cursed techniques?`) in
  `questions/jjk.json` against the Satoru Gojo page's `Cursed Technique`
  section, in the same family as the `jjk-set-09` / `jjk-set-12` corrections
  (cited note added, `verified` bumped to 2026-08-17):
  - Bare names replaced with the wiki's page titles: `Blue` ->
    `Cursed Technique Lapse: Blue`, `Red` -> `Cursed Technique Reversal: Red`,
    `Purple` -> `Hollow Technique: Purple`, `Simple Domain` ->
    `New Shadow Style: Simple Domain`.
  - `Six Eyes` dropped: the page files it under a separate `Special Abilities`
    heading and its infobox types it `Jujutsu Trait`, not a cursed technique.
  - `Curtain` (under `Barrier Techniques`) and `Cursed Technique Lapse -
    Maximum Cursed Energy Output: Blue` (the wiki's own section heading) added,
    which the old gold omitted. Gold is now 11 items.
  - Carries the wiki's own section-heading names as aliases (e.g.
    `maximum cursed energy output` for the Max Output form), matching how the
    bank already aliases bare names elsewhere.
- Full suite still **813 passed**; server restarted (staleness guard).
- **Canon-run 2026-08-17-1157:** set-10 went from **5/10 -> 11/11 recall (85%
  precision)** — the dedupe regression is gone and the question returns the
  wiki's full set. Aggregate: **6/17 exact** (unchanged), canon items
  **207/212 (97.6%)**, precision **63.0%** (from 60.2%). The two remaining
  set-10 members are engine-side intruders (`Cursed Energy Reinforcement`, a
  cursed-energy trait; `Hollow Purple`, a variant that survives dedupe), both
  tracked by P5/P8 rather than the gold.

### Parallel research agents (P1-P7): findings

Dispatched five read-only research agents in parallel. Results:

- **P1 (template transclusion resolver).** The real corpus has **18 curated
  list templates / 26 transclusions / 14 host pages** (brief's per-template
  counts were slightly off; e.g. `{{Shikigami}}` is 3 uses, not 6). Confirmed
  live that `action=expandtemplates` (not `parse`) returns resolved wikitext
  (a 14k-char table for `{{Ten Shadows Shikigami}}`). The wiki's canonical
  shikigami list is the 10 base shikigami; the declared 11-member roster adds
  `Divine Dog: Totality` and `The Well's Unknown Abyss`. Implementation plan:
  rewrite the stored `wikitext` (post-crawl, pre-index) so `load_extracted` ->
  `reextract` ingests the resolved list with zero changes to `index/build.py`.
- **P2 (Yuta acquired column).** The `acquired` column is **degenerate**: every
  row in the corpus is `innate`; the extraction prompt (which even special-cases
  Yuta) wrote copy evidence into free-text `reason` instead. A filter on
  `acquired == "copied"` is a strict no-op on current data — wiring it alone
  changes nothing. Needs either re-extraction honoring the instruction or a
  `reason`-language fallback (which would drop ~13 of Yuta's 21 returned
  members, ~19% -> ~44-50% precision, recall unchanged at 4/5). Directionally
  sound; data-blocked.
- **P3 (Disaster Curses intruders).** The brief's prose-row hypothesis is
  **wrong**: all 18 intruders arrived via the `Cursed Spirits` category through
  discovery (no `Disaster Curses` category/page exists; the word "disaster"
  matches no category). The wiki's own declaration is the Mahito page lead +
  infobox `affiliation = Mahito's group` (names exactly Mahito, Jogo, Hanami,
  Dagon; Ko-Guy also carries that affiliation — a wiki inconsistency). A
  declared roster `match: [disaster curse, disaster curses]`, `subject: Mahito`,
  `members: [Mahito, Jogo, Hanami, Dagon]` was validated in-process:
  22 -> 4 members, all 20 other jjk questions byte-identical, canon-run expected
  6/17 -> **7/17 exact**.
- **P6 (Zenin Family / Noritoshi Kamo).** The wiki **never connects** the
  student Noritoshi Kamo to the Zenin Family: his page is filed under
  `Kamo Family`, affiliation/occupation are "Kamo Clan (Formerly)", and the only
  Zenin-page mention calls him "the heir of the Kamo Clan". The Sorcerer Clan
  page's Zenin Members table lists exactly 11 (no Noritoshi). So the gold's 12th
  member is a canon-based judgment the wiki's pages don't support; the engine is
  right at 11/11. Fix is a gold decision (remove him -> 11/11 exact, or document
  the divergence), not an engine change.
- **P7 (audit jjk gold bank vs wiki).** Swept every jjk set question against the
  stored crawl. Correct (clean): set-01/02/03, set-06/08/12/13/19, char-01..05.
  Additional gold-vs-wiki defects found (same correction family as set-10):
  set-05 includes `Pure Love`, which the wiki never names as a technique (the
  Rika page names the entry `Cursed Energy Blast` and marks it `(Unnamed)`;
  "Pure Love" is a soundtrack/domain-train name) — strong; set-18 over-claims
  Noritoshi Kamo (see P6) — strong; set-11 includes `The Well's Unknown Abyss`
  (typed `Extension Technique`, not `Shikigami`) and omits Round Deer / Piercing
  Ox / Tiger Funeral (typed `Shikigami`) — strong/medium; set-07 under-returns
  (the page's prose names all nine Death Paintings, not three) — strong;
  set-09's last item `Domain Expansion` is actually the wiki's `Hometown
  Domain` (table-header vs technique name, also in the declared roster) —
  medium; set-02 primary `Furnace` is `Divine Flame` on the wiki — weak naming;
  set-03/set-10 consistency nit (`Hollow Purple` vs `Hollow Technique: Purple`)
  — weak. None applied this session (P0 was the only gold change).

### P1 implementation (in progress, NOT yet live)

- `scriptengine/ingest/crawler.py`: added `WikiCrawler.expand_templates()`
  (reuses the throttled `_get`; `action=expandtemplates`).
- `scriptengine/ingest/templates.py` (new): `declared_lists()`,
  `find_unresolved()`, `splice()`, `TemplateCache`, `resolve_series()` — splices
  declared transclusions' expansions into the stored wikitext, incremental via
  a per-template cache and idempotent because resolved transclusions disappear.
- `scriptengine/cli.py`: added the `resolve-templates --series jjk [--refresh]`
  command.
- **Not yet done:** `template_lists:` block not added to
  `series/jjk/overrides.yaml`, `tests/test_templates.py` not written, module
  untested and unrun, no re-index/canon-run. P1 is intentionally paused here.

## 2026-08-17

### Session start: baseline re-established

- Confirmed the working tree matches the continuation brief: branch
  `character-scoped-questions`, ahead of origin by one commit (`edac08f`,
  the 29-value `ability_class` map). The prior session log's "one further
  commit" hash was confirmed as `edac08f`, local-only.
- Installed missing deps (`pytest`, `lxml`, `httptools`, `watchfiles`) into
  the active environment. Full suite: **790 passed**, matching the recorded
  baseline, so nothing regressed before building.
- Fresh canon-run (server restarted first, per the staleness guard):
  **6/17 exact (35.3%)**, canon items recovered 205/211 (97.2%), precision
  58.5% over 17/20. The `edac08f` class-map extension is confirmed neutral:
  the number matches the last confirmed score exactly.
  - Yuji's named cursed techniques: **8/8 exact (declared)** — the class filter
    fix holds.
  - Yuta's cursed techniques: 80% recall / 17% precision, 20 intruders — the
    copied-technique problem (Open work item 3) is the single worst question.
  - Disaster Curses: 4/4 canon but 18% precision — 18 intruders, mostly
    `Abilities and Powers / Cursed Techniques` prose rows.
  - Zenin Family remains the one under-return (11/12, Noritoshi Kamo unlinked).

### Template transclusion gap (Open work item 1): investigated and confirmed

- Grepped stored wikitext for `{{` markers on non-chapter/episode pages.
  Confirmed the Ten Shadows Technique page's `List of Ten Shadows Technique
  Shikigami` section is a bare `{{Ten Shadows Shikigami}}` transclusion — 28
  characters, no links, as the brief described.
- Resolved the template live via the MediaWiki `parse` API action. The
  wiki's canonical curated list contains **10 shikigami**: Divine Dogs, Nue,
  Toad, Great Serpent, Max Elephant, Rabbit Escape, Round Deer, Piercing Ox,
  Tiger Funeral, and Mahoraga (full title `Eight-Handled Sword Divergent Sila
  Divine General Mahoraga`). Also surfaced: `Shikigami` (6 uses), `Cursed
  Corpses` / `Cursed Objects` / `Innate Techniques` / `Inherited
  Techniques` / `Barrier Techniques` / `Cursed Tools` list templates on the
  umbrella pages. The `parse` action resolves all of them; a resolver that
  fetches transcluded template content before storage is feasible and is the
  intended fix (not yet implemented — see work log).
- This is the number the two existing Megumi shikigami golds (9 each, mutually
  disagreeing) and the declared 11-member roster all have to be measured
  against once the transclusion is ingested. The declared roster is still
  blocked on that.

### Dedupe module: tests written, wired, measured — and the direction is wrong

- `scriptengine/retrieve/dedupe.py` (untracked survivor of last session's
  killed "duplicate collapsing" agent) turned out to be complete. Its docstring
  promised `tests/test_dedupe.py`; it did not exist. Wrote it: **23 tests**
  covering `normalise`, `_fragments`, and `collapse_variants`, including the
  load-bearing `Divine Dogs` vs `Divine Dog: Totality` non-merge safeguard.
  All 23 pass. Full suite: **813 passed**.
- Wired `collapse_variants` into `build_roster` on both return paths: a new
  `_dedupe_roster` applied inside `_class_filtered`, and an inline pass on the
  discovered-category path, both running **after** class filtering so a
  class-rejected member cannot protect its variant. Rejections are recorded in
  `roster.rejected` with rule `dedupe`.
- Re-ran canon-run. Aggregate: still **6/17 exact**, precision 58.5% → 60.2%,
  but canon items recovered **205/211 → 201/211 (95.3%)**. The regression is
  one question: `What are Satoru Gojo's named cursed techniques?` went 9/10 →
  5/10. The gold (jjk-set-10) names the **bare** forms — Blue, Red, Purple,
  Simple Domain — while the dedupe keeps the **qualified** page titles
  (Cursed Technique Lapse: Blue, Cursed Technique Reversal: Red, Hollow
  Purple, New Shadow Style: Simple Domain). The pair appears in one answer and
  the wrong half survives.
- Key finding: the direction of the collapse is not decidable from the strings
  alone — `Every cursed technique of Satoru Gojo` (jjk-set-03) uses the
  **qualified** names in gold and improved 59% → 77% precision, while
  `What are Satoru Gojo's named cursed techniques?` (jjk-set-10) uses the
  **bare** names and broke. Two golds of the same wiki disagree on which half
  of each pair is the answer. Next step: either the asks/phrasing must choose
  the direction (short-form question → keep bare), or the golds must agree on
  the wiki's own page titles, or the dedupe must be gated to only fire when
  both members arrive from the same section. The wiring is in place; the
  direction decision is open.

### Gojo gold-vs-wiki audit: set-10's gold disagrees with the wiki's own page

- Read the wiki's `[[Cursed Technique]]` section on `Satoru Gojo` directly
  (stored wikitext). The wiki lists, in order: Limitless (Inherited
  Technique), Infinity (neutral form), **Cursed Technique Lapse: Blue**
  (Extension Technique), **Cursed Technique Lapse - Maximum Cursed Energy
  Output: Blue**, **Cursed Technique Reversal: Red** (Extension Technique),
  **Hollow Technique: Purple** (Extension Technique), Reverse Cursed
  Technique, Curtain, Simple Domain, Falling Blossom Emotion (Anti-Domain
  Technique), Unlimited Void (Domain Expansion) — and **Six Eyes under a
  separate `Special Abilities` heading**, not under Cursed Technique.
- The `type` field in the facts store agrees with the class map: Six Eyes =
  `Jujutsu Trait` (mapped to `trait`), Cursed Technique Lapse: Blue /
  Reversal: Red / Hollow Technique: Purple = `Extension Technique`,
  Limitless = `Inherited Technique`, Falling Blossom Emotion =
  `Anti-Domain Technique`, Unlimited Void = `Domain Expansion`. Bare
  names (Blue, Red, Purple) and `Hollow Purple` have **no page and no type**;
  the wiki's page titles are the qualified forms.
- Verdict on the two golds:
  - **jjk-set-03** (`Every cursed technique of Satoru Gojo`): correct against
    the wiki. Uses qualified page titles, carries bare-name aliases
    (`Cursed Technique Lapse: Blue` aliases `blue`, `lapse blue`), and
    omits Six Eyes. The dedupe helped it 59% → 77% precision.
  - **jjk-set-10** (`What are Satoru Gojo's named cursed techniques?`): wrong
    on two counts per the wiki's own structure. (1) It uses bare names with
    no aliases (Blue, Red, Purple, Simple Domain) where the wiki's page
    titles are qualified; the dedupe keeps the qualified titles, so those
    gold items now miss. (2) It includes **Six Eyes**, which the wiki files
    under `Special Abilities` and types `Jujutsu Trait` — the exact shape
    of gold-vs-wiki disagreement fixed for Yuji (Divergent Fist / Black
    Flash = Taijutsu). This is a gold correction in the same family as
    `jjk-set-09` / `jjk-set-12`, with the wiki's own page as the citation.
- The dedupe itself is not at fault: its rule (keep the wiki's qualified page
  title, drop the bare form) is the fidelity-correct direction. The failure
  mode is the gold using bare names. Next step is to correct `jjk-set-10`
  against the wiki (qualified titles, drop Six Eyes, add Curtain and the
  Maximum Output variant as the wiki lists them), exactly as `jjk-set-09`
  and `jjk-set-12` were corrected with cited notes.

### Work log (in progress)

- Todo list active: correct `jjk-set-10` against the wiki (qualified titles,
  drop Six Eyes), then re-measure the dedupe; template resolver (next) to
  ingest `{{Ten Shadows Shikigami}}` and fix Megumi's roster; Yuta
  `acquired` column attribution; Disaster Curses prose-row intruders;
  Zenin Family Noritoshi Kamo link; further canon fixes toward 100%.

## 2026-08-14

- Added `questions/`, the online-canon question bank, one JSON file per
  series, tracked in git. The 37 questions and 217 canon items that lived as a
  Python literal in `scriptengine/eval/canon_gold.py` moved here, with the URL
  each answer was researched from recorded beside the answer instead of in a
  `#` comment. The series list is now discovered from the filenames; no `.py`
  file names a series.
  - Four Meruem items (`Aura Synthesis`, `Photon`, `Rage Blast`, `En`) were
    **not** migrated. Their only source was VS Battles, a powerscaling wiki
    whose entries are argued rather than documented. They sit in `hxh.json`'s
    `retired[]` with the reason, so nothing silently re-adds them.
  - A blocking A/B check proved the loader reproduces the old literal exactly:
    36 questions / 213 items, zero drift apart from the retired block. A
    dropped alias would have moved the score with no engine change.
- Added `scriptengine/eval/questions.py` (the loader) and
  `tests/test_question_bank.py`, which refuses a banned domain, a missing
  source, an undated question, a set with no wiki-tier source, a duplicate item
  after normalisation, or a reused id. The bank decides what counts as a wrong
  answer, so a defect in it moves the score with no engine change at all.
- Added `reports/`, one folder per run, tracked in git, holding `run.json`
  (git sha, `/health` payload, bank counts, wall clock), the scores, the
  diagnosis, `eval.json`, and the consolidated `REPORT.md`. `reports/index.md`
  carries one row per run. Only `reports/*/answers.md` is gitignored. The
  answer sheet this replaces was lost because it lived in a gitignored folder.
- Added `scriptengine/eval/canon_report.py` and `scriptengine/eval/canon_run.py`,
  and the `canon-run` CLI command. `canon-run` refuses to start when the
  measurement would be untrustworthy: no server, or a server whose start time
  predates the newest `.py` under `scriptengine/`. That second check exists
  because a measurement has already been taken against a stale server once and
  reported no change from a fix that had in fact worked. It never exits
  non-zero on a bad score: a low number is the finding.
- `canon_gold.py` now loads from the bank. `norm()` is unchanged byte for byte
  and `GOLD`/`RECALL_ONLY` still materialise at module level, because
  `diagnose_misses.py` imports both, a compatibility contract rather than a
  convenience. Added `haystack()`, `present()` and `score_facts()` for the new
  fact-question path, which matches on word boundaries rather than plain
  containment so `Gon` cannot match inside `Gonta`.
- Fixed a `UnicodeEncodeError` in `diagnose_misses.py`: the diagnosis file is
  now written *before* the print loop, which could throw on a macron on a
  cp1252 stdout and discard a completed run's work at the last step.
- Expanded the bank from 36 questions to 135. The old spread (db 8, berserk 2)
  silently made the aggregate mean "the engine on Dragon Ball"; every series
  now carries a comparable share. Three batches:
  - **60 general questions**, 12 per series, weighted toward the measured
    defect: short complete sets where padding cannot hide (God Hand 5,
    Horsemen 4, Royal Guards 3), current-versus-former membership probes
    (current Yonko, current S-Class), thinly-filled categories, and the bank's
    first `fact` questions. Roadmap phases 20 and 21 previously had no question
    that could fail for their reasons, and so no number attached to either.
  - **39 character questions**, `Every ability of <character>` for the five
    most prominent characters in each series, so a failure can be attributed to
    a character rather than to the series. Casca was skipped deliberately: her
    Berserk page documents abilities in prose with no named entries, and there
    is nothing there to score without inventing it.
  - Scope matters on these: a character with an open-ended technique list is
    recorded as `core`, because the Dragon Ball wiki credits Goku as a user of
    194 techniques and a correct answer against a `closed` reading of that
    would score about 4% precision.
- The web research and transcription for both batches was delegated to
  `opencode` driving `deepseek-v4-flash-free`, one unattended background run
  per pair of series. Nothing from that path was taken on trust: every batch
  was checked by the test suite, and then every cited page was re-fetched and
  searched for the items the bank claims are on it.
  - That check earned its keep immediately. `bleach-set-07` asserted that
    classes 90 and above hold exactly six Kido spells and cited the `Kido`
    page, which documents two of them, and no page on that wiki lists all six
    together, so the completeness claim could not be sourced at all.
    `jjk-set-07` asserted the four registered special-grade sorcerers of 2018
    and cited `Grade`, whose wikitext does not contain the string "Gojo"
    anywhere; its Grade Registry transcludes those names from elsewhere. Both
    passed the test suite, which checks that a source exists and not that the
    source says what the bank claims. Both are retired with the reason, and
    replaced by `Every Visored` (9) and `Every named Cursed Womb: Death
    Painting` (3, of nine that exist; the under-fill is the point).
- `tests/test_question_bank.py` now refuses two questions that share a question
  string, across series as well as within one. Question text is a key in two
  places. `canon_report.render()` selects the subset comparable with earlier
  runs by matching it, and `diagnose_misses.py` resolves an item's canon list
  and series the same way, so a duplicate is the id-collision defect one field
  over. It was found in the first real run: the per-character batch produced
  `Every ability of Power` for Chainsaw Man, word for word the existing
  `csm-set-02`, and the comparable subset came out as 37 questions over 229
  canon items where the migration had established 36 over 213. The character
  question is now `Every documented ability of Power`; both questions are real
  and only the collision was wrong.
- **Engine finding, from fixing that collision: a parenthetical in the query
  destroys subject resolution.** The first re-phrasing was
  `Every ability of Power (the complete set her wiki page documents)`. The same
  question, same answer list, same server, went from 15/16 canon at 88%
  precision on basis `Power, by section and prose` to **0/16** on basis
  `Character Subpage`. Chainsaw Man's Power is already the pathological
  subject-resolution case (both words of her name are ordinary English) and
  the trailing clause is enough to push resolution onto the wrong basis
  entirely. Worth a roadmap line: resolution should strip a trailing
  parenthetical before matching, and `Every current Espada (…)` scoring 7/10
  suggests the failure is specific to a subject that is already ambiguous
  rather than to parentheses as such.
- **`diagnose_misses.SUBJECT` was a 37-entry literal and had silently stopped
  covering the bank, inverting the report's remediation ordering.** It maps a
  question to whose ability prose the question is about, and every check that
  distinguishes one miss bucket from another reads from it: ownership edges,
  extracted rows, and the subject's own section headings. Once the bank grew to
  135 questions, the 99 new ones resolved to `character = ""`, all three checks
  read empty, and those misses could only ever land in `unlinked page` or
  `corpus gap`. Now read from the bank's `subject` field via
  `questions.subjects()`, and `GOLD_ERRORS` from `questions.retired()` (which
  had been an empty dict, so no retired item was ever excluded from the score).

  Re-bucketing the same run's scores with the subject resolving moves 40% of
  every item in the table:

  | bucket | as published | with the subject resolving |
  |---|---:|---:|
  | retrieval gap | 52 (21%) | **78 (31%)** |
  | unlinked page | 116 (46%) | 80 (32%) |
  | extraction gap | 6 (2%) | **68 (27%)** |
  | corpus gap | 78 (31%) | **26 (10%)** |

  The conclusion reverses. `corpus gap`, "the wiki does not support this claim,
  and a script must not make it", was the second-largest bucket at 31% and is
  actually 10%, of which only **3 items in the whole bank** are `nowhere on this
  wiki`. What looked like a data-coverage problem is an extraction and retrieval
  problem: 68 items are named in prose the extractor read and did not emit, and
  78 are reachable in the store and were not returned. The recall ceiling is
  about 99.7%, not the 71.3% recorded.

  `tests/test_question_bank.py` now asserts `SUBJECT` covers every question in
  the bank, which is the guard that was missing: the literal drifted out of
  coverage without a single test failing.
- `question_sheet.py` now resolves its destination through
  `Settings().reports_root` instead of the CWD-relative `Path("scripts output")`.
  It only worked from the repo root, and it wrote measurement output into a
  gitignored folder, the same shape as the loss this pipeline exists to stop.

## 2026-08-12

- Deleted `OBSIDIANPLAN.md` (root), a pre-implementation design doc for the
  Obsidian export feature; the feature it planned is now fully built
  (`scriptengine/export.py`, the `export` CLI command, `tests/test_export.py`,
  and README/CLAUDE.md both list it done). Nothing referenced the file.
- Deleted `Plan to follow.md` (root), an untracked scratch planning file.
- Deleted six superseded dev-log snapshots from `scripts output/`:
  `Engine Answer Sheet.md`, `Engine Answer Sheet 2.md`,
  `Engine Answer Sheet 3 - Ontology.md`, `Engine Answer Sheet 4 - Real Topics.md`,
  `Engine Answer Sheet 5 - Character Scoped.md`,
  `Engine Answer Sheet 6 - Online Comparison.md`. Kept
  `Engine Answer Sheet 7 - Canon Recheck.md` as the current one.
- Deleted four superseded canon-score snapshots from `scripts output/`:
  `canon_scores_after.json`, `canon_scores_after_diagnosis.json`,
  `canon_scores_before.json`, `canon_scores_before_diagnosis.json`. Kept
  `canon_scores_pagefirst.json` as the latest.
- Added `docs/STRUCTURE.md`, a full directory/module inventory complementing
  `ARCHITECTURE.md`'s design rationale.
- Added `docs/ROADMAP.md`, a phase status table plus narrative on open phases
  (5, 6, 20, 21) and longer-term direction.
- Added `docs/CHANGELOG.md` (this file).

## 2026-08-04, preserved from `Engine Answer Sheet 7 - Canon Recheck`

That sheet was deleted on 2026-08-12 to make way for the `reports/` pipeline. It
lived in the gitignored `scripts output/`, so git holds no copy. The scores it
reported are regenerable by re-running; the findings below are not, and are
recorded here instead.

**Headline at the time.** Canon recovered on the 17 original questions rose from
75/120 (62.5%) to 92/118 (78.0%); across all 37 questions, 162/217 (74.7%). Two
of 37 questions at recall 0, 24 of 37 at recall ≥ 0.8, zero confident-and-wrong,
precision 22.0% on closed sets. The gold set grew from 17 questions over 14
characters to 37 questions / 217 canon items across all eight series.

**Six defects found by reading output, each measured.**

1. *Prose-extracted members skipped canon validation.* Enabling Dragon Ball prose
   put `Super Saiyan (Berserk)` back among Goku's forms, because the game-only filter the
   category path applied never ran on extracted rows. Fix applies the canon rule
   but not the user-field rule: running full validation instead deletes Sukuna's
   `Dismantle`, `Cleave` and `Shrine` and Goku's `Ultra Instinct`, each for "no
   field on this page names X as a user", the exact condition prose extraction
   exists to work around.
2. *Technique and transformation were folded unconditionally.* `Kamehameha`
   answered a question about *forms*. Asked-kind only vs folded: Killua 2→4 canon
   (+3 members), Sukuna 7→7 (+10), Vegeta 11→11 (+16), Goku 10→11 (+26). The fold
   pays on Killua and nowhere else; what separates them is proportion: his
   off-kind rows are 3 against 16, Goku's 26 against 31. Now folded only below a
   one-third ratio.
3. *`wants_chronology` matched any query containing "Arc".* `Fearsome Womb Arc`,
   one arc's story, the shape a script needs, was answered with the ordered list
   of arcs. jjk eval 23/24 → 24/24, plus 12 regression tests.
4. *The kind vocabulary was a fixed English word list.* `shikigami`, `style` and
   `contract` were absent, so those questions never became character-scoped:
   `Every shikigami of Megumi Fushiguro` returned none of the nine in the table.
   Generic words went into the module, series words into `overrides.yaml` under a
   new `ability_kinds:` block. `Every sword style of Zoro` 0→5/5, Megumi 0→4/9.
5. *A character whose name is a kind word could never be resolved.* Chainsaw Man
   has a character called Power, so `Every ability of Power` had both words struck
   out and returned nothing. A strict fallback accepting only an outright
   `character` page now runs when nothing else resolves: 0→4/6.
6. *The race vocabulary swallowed two characters.* It kept any word from a
   free-text race field that had a page, and `Gohan` entered through two values
   reading `1/2 Glind-1/2 Saiyan (Gohan Black)`. A real race is declared by many
   pages and an accident by two: saiyan 157, human 148, namekian 80, frieza 44,
   majin 43, quincy 47, against gohan 2 and buu 2. Gohan 0→5/6. The same rule was
   separately keeping Frieza out of his own question, correctly, since `Frieza` really
   is a race here. A race word may now name the subject when the topic does not
   mark a race itself: `Every transformation of Frieza` 2/8 → 7/8, and the gold
   case asserting `Every Frieza Race transformation` still passes.

**What it cost, and one trade still open.** Ichigo lost three canon items to fix 2
(forms 6→5, techniques 4→2) because his off-kind ratio is 0.81 to 1.29 and the
fold is now off for him. Against that, the same rule removed roughly eighty junk
members from Goku, Vegeta, Sukuna and Ichigo; his answers fell from 41 and 42
members to 21 and 26. A variant letting the wiki's page type override the model's
guess was measured and **rejected**: it rescues one canon item (Goku's
`Super Saiyan Blue Kaio-ken`) and admits six junk ones on Sukuna. Ichigo's three
have no page typed as the asked kind, so nothing in the data recovers them. This
is an open trade, not a solved one: the kind-fold threshold is one number with a
measured table behind it, and if recall matters more than precision for script
writing, raise it and take the junk.

**Miss buckets at the time** (see the caveat below): retrieval gap 18 (33%),
unlinked page 15 (27%), corpus gap 15 (27%), extraction gap 7 (13%). At the start
of that run the same tool over the same 17 questions read retrieval 16,
extraction 9, corpus 8, unlinked 6. Extraction gaps fell from 9 to 7 while the
question count more than doubled, so the model stopped being the bottleneck.

**Caveat on those bucket numbers, smaller than it first appeared.** They were
computed with the `owned` signal dead: `diagnose_misses.py` called `row["name"]`
on the plain strings `FactStore.owned_by()` returns, raising `AttributeError`
into a bare `except`, so `owned_names` was empty on every question. The bug was
real and is fixed as of 2026-08-12, but it did **not** distort the split: the
test is `owned or mine or heading`, and re-running the same scores with and
without the fix moves no item between buckets and changes four evidence strings
out of fifty. The bucket counts above stand; what was missing was the reason
attached to four of the misses.

**Three structural misses, with evidence.**

- *Every form of Majin Buu, 0/7.* Five of seven are unlinked pages: `Innocent
  Buu`, `Evil Buu`, `Super Buu`, `Kid Buu` and `Good Buu` all exist as their own
  articles and nothing ties them to a page called `Majin Buu`; there is no such
  page. His forms are filed as separate characters, a data shape no
  character-scoped question can reach. Retrieval resolves the topic to `Kid Buu`
  and answers from there.
- *Every technique of Zoro, 1/8.* Five corpus gaps: `Sanzen Sekai`, `Tatsumaki`,
  `Shishi Sonson`, `Yakkodori` and `Toro Nagashi` appear only on episode and
  chapter pages, never in his ability prose. `Every sword style of Zoro`, asked
  separately, scores 5/5.
- *Every devil contract of Aki Hayakawa, 0/3.* The character path returns what his
  ability sections describe (`Precognition`, `Summoning`, `Bullet Projection`)
  which is what the contracts *do*. The wiki does not name `Fox Devil`,
  `Curse Devil` and `Future Devil` as his abilities; it records them as
  relationships to devils.

**Two scorer changes, both of which had been understating the engine.** Plurals
now fold on both sides (four-letter words and up, so `gas`, `ren` and `nen`
survive; substring matching stays out, `Super Saiyan` must not match
`Super Saiyan 2`). The engine returned `Machine Gun Blow` for the wiki's
`Machinegun Blows` and was scored a miss. And precision became meaningful: it
read 14.5% mostly because `Every technique Goku uses` returns 181 members against
a gold list of 8 core techniques, and the wiki really does record 194 with Goku as a
user. That question is marked `recall_only` and excluded from the aggregate.

**Extraction run of record.** All eight series, top 50 characters each,
`qwen/qwen3.5-9b` on LM Studio with thinking off, four series at a time (45
minutes wall clock against ~7.5 hours serial). Rows 2,542 → 3,943; characters 347
→ 359; series with rows 7 (db empty) → 8; failures 0. `PROMPT_VERSION` was bumped
to `2026-08-04.1`; without it the seven already-extracted series would have kept
cached answers straight through the page-lead change, the single biggest source
of recovered items.

**A stale server produced one false measurement in that run.** It reported no
change from a fix that had in fact worked, because the replacement exited 3 on a
bound port while the old process kept answering. The sheet referenced a
`restart_api.sh` that kills by listener PID; **that file does not exist in the
repo**. Restart after any change under `scriptengine/`.

**Priorities it left, in items per unit of effort.**

1. The retrieval gaps are the biggest bucket and the cheapest: every one is
   already in the store. Megumi's shikigami are extracted rows and 3 of 9 still do
   not come back; Ichigo's are the same shape. Trace one end to end before writing
   code; the tool names the row it expected.
2. Declare what the wikis file oddly. Buu's forms are separate character pages and
   Aki's contracts are relationships; both need an `overrides.yaml` declaration or
   they stay at zero, and neither is a retriever bug.
3. Settle the Ichigo trade (above).
4. Leave the corpus gaps alone. Zoro's five named attacks are not in his ability
   prose on that wiki. No prompt recovers them, and a script should not claim them.
