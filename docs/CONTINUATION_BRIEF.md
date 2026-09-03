# ScriptEngine - JJK ability classification: continuation brief (2026-08-17)

> **Read this first.** This document is the complete handoff for the next
> working session. It explains what the project is, what we are trying to
> achieve, how the engine works, exactly what has been done, what is broken,
> and which files to read before changing anything. Read it top to bottom,
> then read the "Files to read" section, then run the verification commands
> at the bottom, then start.

---

## 1. What the project is

ScriptEngine is a **local RAG (retrieval-augmented generation) engine** that
answers questions against **crawled Fandom wiki data** for eight anime series:
Jujutsu Kaisen (jjk), Bleach, Dragon Ball, One Piece, Hunter x Hunter,
Chainsaw Man, Berserk, One Punch Man. It does **not write scripts**; it serves
ordered, cited, structured context over HTTP (a POST /context endpoint on
:8000) to whatever writes the video scripts.

**Work is currently scoped to Jujutsu Kaisen (jjk) only.** The other seven
series are paused mid-survey. Do not touch them without new instruction.

### The governing mandate (the owner's words, verbatim)

> The purpose of the RAG is to fetch the wiki data as is, and develop
> relationships between all the data that exists through multiple pages and
> parts of the anime. We don't want to change anything from the wiki's
> definitions - its technique definition, cursed spirit definition, etc. Work
> in such a way that we get 100% of Fandom wiki knowledge in our local script
> engine, which we can fetch, process, cross-question, and use for generating
> 100% accurate scripts. The wiki shows 8 techniques for Yuji; similarly it
> has multiple things that are uniquely mentioned, and I want you to follow it
> for everything on the wiki.

**Operational reading of the mandate:** when a question's expected answer
doesn't match what the wiki itself would answer, the fix is to find where the
wiki already states the distinction (an infobox field, a category, a template
list, a heading) and read it. Never invent a rule, never hardcode a member
list to fit a gold, never let a model paraphrase something the wiki already
declares structurally.

### The current goal

**Get JJK to 100% accuracy.** Concretely: every closed-set question in
questions/jjk.json returns *exactly* its gold set (exact-match, not just
high recall/precision). The current number is **6/17 exact (35.3%)**.



## 2. How the engine works (architecture in one page)

Pipeline: **crawl -> index -> retrieve -> serve**.

1. **Crawl** (cli crawl): fetches pages from the MediaWiki API into
   series/<name>/wikitext/*.json - one JSON per page with wikitext,
   parsed sections, facts (infobox fields), edges (links), citations,
   categories, templates. 987 pages on jjk.
2. **Index** (cli index): re-parses from stored wikitext (no re-crawl) into
   the SQLite facts.db - nodes, facts, edges, categories, FTS5 - and the
   Qdrant vector store. Fast, repeatable.
3. **Abilities** (cli abilities): prose-extraction of abilities via a
   local LLM (Qwen 3.5-9B on LM Studio at localhost:1234, or
   SCRIPTENGINE_LLM_BACKEND=opencode). **This is the only place a model is
   used.** Everything structural comes from SQL reads.
4. **Retrieve**: three modes.
   - qa - hybrid retrieval (BM25 + vectors + graph hops), top-8 passages.
   - narrative - chronological walk of one page's sections.
   - roster - **enumeration**, "every X" questions. This is where almost
     all the JJK work lives (scriptengine/retrieve/roster.py).

### The roster pipeline (where the action is)

build_roster(series_paths, query, token_budget) in
scriptengine/retrieve/roster.py decides which set a question means, then
reads members from one of:

- **Declared rosters** (rosters: in series/jjk/overrides.yaml): a
  hand-written members: list, a category:, groups:, or sections_of: page.
  Matched by longest phrase.
- **Discovery**: score the wiki's own category names and page types against
  the query's words (_choose_set).
- **Ownership edges**: "users"/"user" edges from the infoboxes
  (_owned_roster).
- **Extracted rows**: model-extracted abilities from the character's prose
  (_extracted_roster).
- **Sections**: headings on the character's page (_section_roster).

Members are rendered (_render_member), validated (apply_constraints),
class-filtered (drop_off_class / _class_filtered), and deduplicated
(_dedupe_roster, dedupe.collapse_variants).

### The ability-class system (the core JJK fix, working)

The wiki's **technique infobox type field** is the structural answer to
"what kind of ability is this?" - one class per ability entity, correct for
every holder, regardless of which section mentions it. The section an ability
sits under is editor noise (Black Flash is under 4 different headings across 8
pages). Declared in series/jjk/overrides.yaml:

    ability_class:
      field: type
      map:
        Innate Technique: cursed_technique
        Inherited Technique: cursed_technique
        Extension Technique: cursed_technique
        ... (29 values total, 7 classes)
        Shikigami: shikigami       # separate from cursed_technique
        Taijutsu: physical         # Divergent Fist, Black Flash
        Jujutsu Trait: trait       # Six Eyes
        Cursed Tool: item
        Ending/Opening/Soundtrack: media
        School/Building/Prefecture: place
      asks:
        - phrases: [cursed technique, cursed techniques, technique, techniques]
          keep: [cursed_technique]
        - phrases: [shikigami]
          keep: [shikigami]

Implementation in roster.py: ability_class_rules parses the YAML;
ability_class reads the type from the facts/nodes tables via a memoized
SQL join; wanted_classes longest-phrase-matches the query against asks;
drop_off_class removes members *positively* classed outside what was asked
- **never emptying a non-empty set** (same guarantee as apply_constraints,
asserted in tests/test_roster_validation.py). A member with no page/no type
(Dismantle, Hometown Domain, New Shadow Style: Simple Domain) is **kept**:
rejection needs positive evidence.

**Acceptance check that must keep passing:**

    build_roster(series_paths("jjk"), "Every technique of Yuji Itadori", 200)
    # expect exactly the 8: Blood Manipulation, Convergence, Piercing Blood,
    # Shrine, Dismantle, Reverse Cursed Technique, Simple Domain, Domain Expansion

    build_roster(series_paths("jjk"), "Every ability of Yuji Itadori", 200)
    # expect the wider set, still including Divergent Fist and Black Flash

---

## 3. Current state (measured 2026-08-17)

### Test suite: 813 passing

790 baseline + 23 new tests/test_dedupe.py. Must not drop below 813.

### Canon-run: 6/17 exact (35.3%), precision 60.2%, recall 201/211 (95.3%)

The 17 comparable set questions and their scores (from the latest run):

| Question | Recall | Prec | Exact? | Problem |
|---|---|---|---|---|
| How many 1v1 battles Yuji had | 100% | 38% | exact (9/9) | 15 intruders (battle pages) |
| Every cursed technique of Sukuna | 100% | 56% | exact (10/10) | 8 intruders |
| Every cursed technique of Gojo | 100% | 77% | exact (10/10) | 3 intruders |
| Every shikigami of Megumi | 100% | 82% | declared (9/9) | 2 intruders |
| Every cursed technique of Yuta | 80% | 19% | exact (4/5) | **20 intruders, copied techniques** |
| Every Disaster Curse | 100% | 18% | exact (4/4) | **18 intruders** |
| Every named Cursed Womb | 100% | 100% | exact (3/3) | clean |
| Every first-year of Tokyo High | 100% | 100% | declared (3/3) | clean |
| Every ability of Yuji | 100% | 88% | partial (23/23) | 3 intruders |
| Every ability of Gojo | 95% | 88% | partial (21/22) | 3 intruders |
| Every ability of Megumi | 100% | 84% | partial (16/16) | 3 intruders |
| Every ability of Nobara | 100% | 100% | partial (4/4) | clean |
| Every ability of Sukuna | 94% | 81% | partial (30/32) | 7 intruders, 2 missing |
| What are Yuji's named techniques? | 100% | 100% | declared (8/8) | **clean - the flagship fix** |
| What are Gojo's named techniques? | 50% | 38% | exact (5/10) | **BROKEN by dedupe - see section 5** |
| What are Megumi's named shikigami? | 100% | 82% | declared (9/9) | 2 intruders |
| What are Nobara's named techniques? | 100% | 100% | exact (3/3) | clean |
| What are Sukuna's named techniques? | 100% | 56% | exact (10/10) | 8 intruders |
| Zenin Family members | 92% | 100% | declared (11/12) | **under-return: Noritoshi Kamo** |
| Death Painting Wombs | 100% | 100% | declared (9/9) | clean |



## 4. What was done this session (2026-08-17)

### Baseline re-established

- Branch character-scoped-questions, **1 commit ahead of origin**
  (edac08f - the 29-value class map extension; local-only, never pushed).
  Latest commits: 659b360 plan -> 647577a exact metric -> 125eac4 class
  filter -> b8d35b4 gold corrections + declared-roster fix -> c6d8285 metric
  surfaced -> edac08f class map to 29 values.
- 790 tests pass; canon-run 6/17 exact - the class-map extension is neutral.
- Dedupe module found untracked on disk from the previous session's killed
  agent; scriptengine/retrieve/dedupe.py was complete but had no tests and
  was not wired.

### Dedupe module: tested, wired, measured - direction bug found

- Wrote tests/test_dedupe.py (23 tests). All pass.
- Wired into build_roster at both return paths via _dedupe_roster
  (inside _class_filtered) and an inline pass on the discovered-category
  path. Both run **after** class filtering.
- **Measured regression**: recall 205/211 -> 201/211. One question broke:
  What are Gojo's named cursed techniques? (jjk-set-10) went 9/10 -> 5/10.
  Cause: the dedupe keeps the wiki's **qualified page title** (Cursed
  Technique Lapse: Blue) and drops the bare form (Blue); jjk-set-10's gold
  uses bare names with **no aliases**, so the surviving qualified name does
  not match. See section 5 - this is now understood as a gold defect, not a
  dedupe defect.

### Template transclusion gap confirmed and sized

- {{Ten Shadows Shikigami}} on the Ten Shadows Technique page renders as
  28 characters of wikitext with no links; the crawler skips the
  Template: namespace. **The wiki's canonical curated shikigami list lives
  in that template** and is currently invisible to the engine.
- Resolved it live via the MediaWiki parse API action: the template lists
  **10 shikigami** - Divine Dogs, Nue, Toad, Great Serpent, Max Elephant,
  Rabbit Escape, Round Deer, Piercing Ox, Tiger Funeral, Mahoraga.
- Other list templates found: Shikigami (6 uses), Cursed Corpses, Cursed
  Objects, Innate Techniques, Inherited Techniques, Barrier Techniques,
  Cursed Tools on the umbrella pages.
- **This is the number Megumi's roster must be measured against.** See
  section 6, priority 1.

### Gojo gold-vs-wiki audit

Read Satoru Gojo's [[Cursed Technique]] section in the stored wikitext.
The wiki lists: Limitless (Inherited Technique), Infinity, Cursed Technique
Lapse: Blue (Extension Technique), Cursed Technique Lapse - Maximum Cursed
Energy Output: Blue, Cursed Technique Reversal: Red (Extension Technique),
Hollow Technique: Purple (Extension Technique), Reverse Cursed Technique,
Curtain, Simple Domain, Falling Blossom Emotion (Anti-Domain Technique),
Unlimited Void (Domain Expansion) - and **Six Eyes under a separate
Special Abilities heading**, not under Cursed Technique. The type field
confirms: Six Eyes = Jujutsu Trait; bare Blue/Red/Purple and Hollow Purple
have no page and no type.

---

## 5. The one active regression: jjk-set-10 (Gojo's named techniques)

**Symptom:** after the dedupe wiring, What are Satoru Gojo's named cursed
techniques? scores 5/10 (was 9/10). The diagnosis names Blue, Red, Purple,
Simple Domain, Six Eyes as missing.

**Root cause:** the two Gojo golds disagree on naming convention, and one of
them is wrong per the wiki:

- **jjk-set-03** (Every cursed technique of Satoru Gojo) - **correct**.
  Gold uses qualified page titles with bare-name aliases:
  Cursed Technique Lapse: Blue (aliases blue, lapse blue),
  Cursed Technique Reversal: Red (aliases red, reversal red),
  Hollow Purple (aliases hollow technique purple, purple),
  New Shadow Style: Simple Domain, and does **not** include Six Eyes.
  The dedupe *helped* it (59% -> 77% precision).
- **jjk-set-10** (What are Satoru Gojo's named cursed techniques?) -
  **wrong on two counts**. (1) Gold uses bare names with **no aliases**
  (Blue, Red, Purple, Simple Domain) where the wiki's page titles are
  qualified; the dedupe keeps the qualified titles so those gold items miss.
  (2) It includes **Six Eyes**, which the wiki files under Special
  Abilities and types Jujutsu Trait - exactly the shape of gold-vs-wiki
  disagreement already fixed for Yuji (Divergent Fist / Black Flash =
  Taijutsu) in jjk-set-09.

**The fix (decided):** correct jjk-set-10 against the wiki, in the same
family as the jjk-set-09 / jjk-set-12 corrections:

- Replace bare names with the wiki's page titles: Blue -> Cursed Technique
  Lapse: Blue, Red -> Cursed Technique Reversal: Red, Purple -> Hollow
  Purple (per the wiki's own title) or Hollow Technique: Purple.
- Drop Six Eyes (Jujutsu Trait, filed under Special Abilities, not a cursed
  technique).
- Add the items the wiki lists that the gold omits: Curtain, and the
  Maximum Output variant if the question intends the full set.
- Add a note citing the Satoru Gojo wiki page (source URL) for each change,
  because tests/test_question_bank.py re-verifies any gold change cites a
  real wiki source.

**Do NOT** revert the dedupe wiring or reverse its direction to keep the bare
names: that would trade a correct, fidelity-driven rule for a gold that is
itself wrong. Fix the gold.

---

## 6. Open work, in priority order

### P0: Fix jjk-set-10 (Gojo's named cursed techniques) to match the wiki

Correct the gold as described in section 5, then re-run canon-run to confirm
the dedupe regression is resolved and the question returns to 10/10 exact.
This is a one-line change to questions/jjk.json (with a cited note) and the
dedupe wiring stays as-is.

### P1: Template transclusion resolver

The biggest structural gap. The wiki's canonical curated lists live in
{{Template}} transclusions, and the crawler skips the Template: namespace
entirely. The Ten Shadows Shikigami template lists 10 shikigami; the current
declared roster has 11 (including Divine Dog: Totality and The Well's Unknown
Abyss), and the two golds disagree (9 each, different composition). The only
number that matters is the wiki's own list.

**Approach (decided but not yet implemented):** add a post-crawl or
pre-index step that resolves template transclusions. The MediaWiki parse
API action already works (confirmed live). For each page whose templates[]
list includes a known list template, fetch the expanded content via the
API and store it as a facts edge or a document section. Or use the
expandtemplates action to get the resolved wikitext before storage.

**What to build:** a template resolver module
(scriptengine/ingest/templates.py or similar) that:
1. After crawl, for each page with templates in its wikitext, calls the
   MediaWiki parse action to resolve the transclusions.
2. Stores the resolved content either in the wikitext JSON (replacing the
   transclusion with resolved text) or in a parallel facts table.
3. Is incremental: only fetch templates that haven't been fetched yet.

**Scope before building:** grep the stored wikitext for {{ pattern on
technique/ability pages to know how many templates exist. The count from
this session: {{Shikigami}} (6 uses), {{Cursed Corpses}} (4), {{Cursed
Objects}} (4), {{Innate Techniques}} (4), {{Inherited Techniques}} (4),
{{Barrier Techniques}} (4), {{Cursed Tools}} (4), and {{Ten Shadows
Shikigami}} (1). That's ~31 template transclusions on ability pages.

### P2: Yuta's copied-technique attribution (the precision killer)

Twenty of Yuta's returned items genuinely class as cursed_technique but
belong to other people; Yuta copies techniques. The abilities table has an
acquired column that is not wired into the roster filter yet. Using it to
separate "innate to this character" from "copied by this character" should
fix this without touching the class map.

**Approach:**
1. Read the acquired column from the abilities table for each member.
2. When a question asks about "Yuta's cursed techniques", filter out
   members where acquired = "copied" or similar.
3. Can be done in roster.py, similar to how drop_off_class works.

### P3: Disaster Curses prose-row intruders (18 intruders, 18% precision)

The question "Every member of the Disaster Curses" returns 4/4 canon but
18 intruders, mostly from Abilities and Powers / Cursed Techniques prose
rows. The Disaster Curses are a specific group (Mahito, Jogo, Hanami, Dagon)
and the intruders are other cursed spirits or abilities the engine reads
from the same section. This is a category: Cursed Spirits + qualification
problem: the engine picks up unrelated cursed spirits that share a heading.

### P4: Duplicate and granularity collapsing (dedupe - already wired)

The dedupe module is wired and tested. The remaining issue is the direction
decision (keep qualified vs. bare), which is resolved by the P0 gold fix.
After P0, the dedupe should improve Gojo's set-03 (77% precision -> higher)
and not regress anything else.

### P5: "Definition beats mention" (not yet implemented)

The abilities table is PRIMARY KEY (character, name) with INSERT OR REPLACE,
so if a later section merely mentions an ability, that overwrites an earlier
section that actually defines it. Confirmed example: Dismantle's real
definition was overwritten by a passing "binding vow" reference, so it's
filed under "Cursed Restrictions" for both Sukuna and Yuji. This was
priority #2 in the plan twice and got bumped. It likely contributes to some
over-return noise.

### P6: Zenin Family question - the one under-return

11/12 exact. Noritoshi Kamo is unlinked: the page exists but nothing ties
it to "Zenin Family". The declared roster has 11 members (copied from the
wiki's page), and the gold has 12 (added Noritoshi Kamo). The under-return
means the engine returned 11 of 12 gold items. Need to investigate what
source links Noritoshi Kamo to the Zenin Family.

### P7: Re-run the two agents that errored out

"Audit jjk gold bank vs wiki" (systematic sweep for other Nobara/Yuji-style
gold-vs-wiki disagreements) and "Survey jjk question noise" (fresh
per-question breakdown). Both hit session-limit errors mid-task in the
previous session. Assume no salvageable output.

### P8: Re-measure ability_owner_sections

Flagged as a risk: it was costing 2.1 points of precision for zero recall
gain on its target question (9/9 before and after). Worth confirming
against the post-dedupe, post-gold-fix canon-run.

---

## 7. Files to read before changing anything

### Essential (read in this order)

| File | What it contains |
|---|---|
| docs/CHANGELOG.md | Full log of all changes. The 2026-08-17 entry is this session. |
| docs/CONTINUATION_BRIEF.md | This file. Read it first. |
| series/jjk/overrides.yaml | The ability_class map, declared rosters, and all per-wiki config. |
| scriptengine/retrieve/roster.py | build_roster, ability_class_rules, drop_off_class, _class_filtered, _dedupe_roster, dedupe.collapse_variants calls. |
| scriptengine/retrieve/dedupe.py | The dedupe module. collapse_variants is the main function. |
| scriptengine/eval/canon_gold.py | Scorer: norm(), present(), score_sets(). |
| tests/test_dedupe.py | 23 tests for the dedupe module. |
| tests/test_ability_class.py | 14 tests for the class filter. |
| tests/test_roster_validation.py | Never-empty guarantee (line 429). |
| questions/jjk.json | The gold bank. jjk-set-03, jjk-set-10, jjk-set-09, jjk-set-12 are the most relevant. |

### For the template transclusion issue

| File | What it contains |
|---|---|
| series/jjk/wikitext/Ten Shadows Technique.json | The page with {{Ten Shadows Shikigami}} transclusion. |
| scriptengine/ingest/abilities.py | Prose-extraction path (untouched, needed for pageless abilities). |
| scriptengine/stores/facts.py | FactStore.add_aliases (line 270), not yet fed jjk's romaji/kanji. |

### For Yuta's copied-technique issue

| File | What it contains |
|---|---|
| scriptengine/retrieve/roster.py | build_roster, _extracted_roster, _owned_roster (where the acquired column could be read). |

---

## 8. Verification commands

Run these in this order, every time, before and after any change:

    # 1. Full test suite (must be 813+)
    python -m pytest tests/ -q

    # 2. Index from stored wikitext (no crawl, no model)
    python -m scriptengine.cli index --series jjk

    # 3. Ability extraction (needs local LLM or SCRIPTENGINE_LLM_BACKEND=opencode)
    python -m scriptengine.cli abilities --series jjk --workers 4

    # 4. Restart server before canon-run (staleness guard!)
    python start_scriptengine.py
    # Then Ctrl+C and re-run if it fails, or kill the port first

    # 5. Canon-run
    python -m scriptengine.cli canon-run --series jjk --skip-eval

### Workflow gotchas (cost real time, do not skip)

- **The edit tool rejects a patch to a file it hasn't seen through its own
  read call.** Use tools.read() before tools.edit(). Shell commands (cat,
  sed) don't count.
- **canon-run has a staleness guard.** It refuses to run against a server
  process that predates your latest code change. Restart the server; don't
  just re-run canon-run.
- **The server is on port 8000.** If it fails to start with "port in use",
  run: Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess
  | Stop-Process -Force; then retry.
- **UnicodeEncodeError in the CLI.** The query command uses rich tables
  that crash on cp1252 with Japanese characters. Use PYTHONIOENCODING=utf-8
  or python -X utf8 to avoid this. canon-run does not have this problem.
- **The dedupe direction is correct.** It keeps the wiki's qualified page
  titles. Do not reverse it. If a gold breaks, fix the gold (as jjk-set-09
  and jjk-set-12 were fixed), not the dedupe.

