# `page-gen` — deterministic page-question generation (design)

> **Fresh-session handoff.** A new `page-gen` command for the ScriptEngine CLI that
> auto-generates the *structured* ~80% of a wiki page's campaign question batch from
> `facts.db` (no manual field-reading), emits the roster declarations, produces a
> section-coverage ledger, and hands only the prose beats to a single subagent.
> It drives the JJK Round-3 page-campaign. Read this top to bottom, then
> `plans/jjk-round3-campaign.md` (the 17-cluster plan), `reports/page-campaign/STATUS.md`
> (the campaign record), and `graphify-out/GRAPH_REPORT.md` (the code map) before
> implementing.

---

## 0. Standing operating rules (bind the whole implementing session)

Two rules the user fixed for this campaign. Restate them to **every** subagent you
dispatch, verbatim.

### Rule A — the 1-subagent rule (no parallelism)
Exactly **one** subagent runs at a time. Every phase of `page-gen` that uses a subagent
(Phase 2 verify-structured, Phase 3 prose) dispatches a single subagent and **waits** for
it before the next step. Never two at once. Rationale: shared state — the
`overrides.yaml` roster registry, the batch file, and the running server — must not be
touched by concurrent agents. The campaign has always run this way.

### Rule B — the graphify rule (fast code map)
This repo is **graphified**. Before any subagent greps or crawls the codebase, it MUST
start from `graphify-out/GRAPH_REPORT.md` (god nodes, module communities, legacy→current
supersession) and consult `graphify-out/graph.json`. Put this in every subagent's prompt
verbatim, e.g. *"This repo is graphified — start from `graphify-out/GRAPH_REPORT.md` /
`graphify-out/graph.json` (god nodes, module ownership, supersession) and jump to the
right file before grepping."* Use the graph to find the file, then read only that file.
Worked example: "who owns the roster declared-member filter?" → the graph says
`retrieve/roster.py` `build_roster` (L1136) / `_declared_members` (L2881); don't re-derive.

---

## 1. What this is, and why

`page-gen` is a new command in `scriptengine/cli.py`. Given a wiki page it:

1. **Generates** the structured question set from `facts.db` (zero reading).
2. **Emits** the roster declarations + a **coverage ledger** + a **verify sheet**.
3. Hands the **prose** beats to a single subagent (the only manual reading left).
4. Drives **assemble → merge → page-run to 100% + 100% section coverage + six-class**.

**Why:** the current model is 6 subagent passes per cluster (S1 battles, S2 techniques,
S3 relationships, S4 identity, S5 synopsis, S6 counts), each re-reading the whole page and
hand-writing the *regular* questions. Those regular questions (infobox identity, the
per-battle outcome/location/episode/chapters/techniques block, roster sets, poll/favorite
counts) are **deterministic from structured data** — the fields are identical in shape
across every page. Only the *prose* beats (battle "how", synopsis, relationships, Trivia)
genuinely need reading. `page-gen` inverts the model: a fast deterministic generator for
the structured half, one prose pass for the rest. ~80% less manual work per page.

The user's three decisions (2026-08-23):
- **Prose:** the generator covers all structured data; the structured questions are then
  *verified against the wiki page* (confirm the generator declared the right things); the
  prose is *read manually, as before*, then formed into questions + declared.
- **Location:** an **engine CLI command** (gated by the test suite), not a throwaway.
- **Gate:** the method that covers **100% of the page's detail** — nothing left out, and
  everything retrievable at 100% accuracy.

---

## 2. Project context (for a fresh session)

**ScriptEngine** (`E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine`): a universal
knowledge engine over Fandom wikis. It ingests a wiki, derives that wiki's own entity
taxonomy, and serves ordered, cited, structured context over HTTP (`:8000`), the Typer
CLI, and an MCP server. It does **not** write scripts. No Docker, no DB servers: SQLite
holds facts + graph + FTS5 + categories; Qdrant runs embedded.

**The page-campaign:** a per-page accuracy campaign. For each top JJK page, build a
~300-question batch (`questions/_jjk_page_<slug>.json`), declare rosters in
`series/jjk/overrides.yaml`, run `page-run` to 100%, then the six-class review. The
round-3 plan (`plans/jjk-round3-campaign.md`): Phase 1 (global backport of old failure
modes), Phase 2 (17 uncovered clusters), Phase 3 (200 fresh questions), Phase 4 (repeat
the backport over Phase-3 failures).

**Current state (as of 2026-08-23):**
- Phase 1 (G3+G7 engine fixes) shipped and gated. The gate triple:
  `eval --series jjk` = **24/24**; `canon-run --series opm` = **8/16 exact, 235/237 canon
  (99.2%), 78.5% precision, 18/20 fact**; `pytest tests/ -q` = **985 passed**. These held
  because the campaign so far only touched `overrides.yaml` + batch JSON, never `.py` or
  the official bank. **`page-gen` IS a `.py` change → the full gate now applies to it.**
- Done clusters (STATUS.md rows 43–49): 43 Kenjaku 100/100, 44 Choso 100/100, 45 Toji
  299/299, 46 Nobara 299/299, 47 Aoi 300/300, 48 Kento Nanami 300/300, 49 Naoya Zenin
  290/290. `overrides.yaml` holds **114 rosters** after Naoya.
- **In progress: Angel** (row 50). S1–S4 are drafted
  (`questions/_jjk_page_angel.section1..4.json` + `decl1..4.yaml`); **S5/S6 are not
  started.** See §9 Rollout for how to reconcile Angel with `page-gen`.
- **Remaining Phase-2 clusters (10):** Angel (finish), Shibuya Incident Arc, Culling
  Game (mechanic), Reverse Cursed Technique, Ten Shadows Technique, Kinji Hakari,
  Shinjuku Showdown Arc, Sorcerer Clan, Jujutsu Sorcerer, List of Characters. Then
  Phase 3 (200 fresh Q) + Phase 4 (backport).

**Environment (Windows PowerShell 5.1):**
- **No `&&`** — use `cmd1; if ($?) { cmd2 }`.
- Python = `scriptengine\.venv\Scripts\python.exe` (not the system python; no inline `-c`
  for multi-line — write throwaway scripts to
  `C:\Users\Nikhil\AppData\Local\Temp\opencode\*.py`).
- Set in the **same call** before anything that prints macrons/CJK:
  `$env:PYTHONPATH="<repo>"` and `$env:PYTHONIOENCODING="utf-8"` (cp1252 stdout otherwise
  crashes mid-run).
- Server: `python -m scriptengine.api.main` on `:8000`; `/health` must show
  `"device":"cuda"` and list `jjk`. **A `.py` change → restart the server; an
  `overrides.yaml` change → NO restart** (it is reloaded per query via `config.py`
  `load_overrides`).
- Scoring: `python -m scriptengine.cli page-run --series jjk --batch <slug>` (loads
  `questions/_jjk_page_<slug>.json`; exit 0 = 100%, exit 2 = failures remain).

**The batch + overrides flow (unchanged by `page-gen`):** the batch is
`questions/_jjk_page_<slug>.json`; rosters merge into `series/jjk/overrides.yaml` →
`rosters:` by **TEXT-INSERT** (3-space `- name:`, 5-space sub-keys, inline `members:`;
never `yaml.safe_load` round-trip — it destroys the house comments). The reusable
assembler is `C:\Users\Nikhil\AppData\Local\Temp\opencode\jjk_assemble.py` (takes a
`SLUG` env var; assembles section files into the batch + text-inserts the decl rosters,
cross-checking each new roster against its decl source).

**Start-of-session order:** this doc → `reports/page-campaign/STATUS.md` (the running
campaign record, in-repo) → `C:\Users\Nikhil\.local\share\opencode\plans\jjk-round3-
campaign.md` (the 17-cluster plan, **outside** the repo) → `graphify-out/GRAPH_REPORT.md`
(the code map).

---

## 3. The data model (what `page-gen` consumes)

`facts.db` (SQLite: facts + graph + FTS5 + categories; Qdrant embedded for vectors).
Tables: `documents, sections, categories, nodes, aliases, edges, facts, chunks,
chunk_nodes, semantics, emphasis, abilities, relations, meta`.

`FactStore` API (`scriptengine/stores/facts.py`):
- `facts_for(name)` — infobox key→value dump (a lookup, not a search). A character page
  carries its infobox fields here (e.g. Angel: `name, kanji, romaji, race, age, gender,
  status, occupation, debut`).
- `edges_by_relation(rel)`, `edges_for([ids])` — typed wikilink edges.
- `categories_of(title)`, `documents_in_category(cat)` — MediaWiki categories (e.g.
  `Aoi Todo Battles`, `Culling Game Arc Battles`).
- `abilities_of(char)`, `relations_of(char)`, `document_sections(title)`,
  `document_lead(title)`, `fact_keys()`.

**What maps to what:**
- **Identity** = `facts_for(page)` → one question per field.
- **Battles** = `edges` where `relation IN ('side1','side2')` (battle → fighter).
  SQL: `SELECT s.name FROM edges e JOIN nodes s ON s.id=e.source_id JOIN nodes t ON
  t.id=e.target_id WHERE t.name=? AND e.relation IN ('side1','side2')`. JJK declares the
  side/ability vocabulary as `side1/powers1`, `side2/powers2` (`overrides.yaml`
  `battle_relations`, resolved by `battle_relations(overrides)` `retrieve/roster.py:467`;
  default is `combatant1/abilities1`).
- **Per-battle facts** = the battle page's own `facts` (`outcome, place, date, chapters,
  arc, episodes, prev, conc, event`) + `powers1/powers2` edges (techniques per side).
  `episodes` is schema-available but often **absent** on manga-only fights → generate the
  episode question only when the fact/edge exists (key off `fact_keys()`).
- **Techniques** = `collect_abilities(paths, entity)` (`retrieve/abilities.py:67`, a
  user-edge walk + the `Usage/<char>` section + per-character chapter refs), or the
  `Cursed Technique` section of the page.
- **Closed sets / rosters** = battles-in + technique sets + alias/affiliation
  single-fields + relative/cousin sets (from `relations` / `edges`).

**Gaps (not queryable today — handle explicitly, do not silently re-gold around them):**
- **No single-page parse helper.** Compose `WikiPage.from_dict` (`ingest/documents.py:123`,
  the crawl JSON shape) + `reextract(page, ontology)` (`ingest/crawler.py:748`) +
  `Ontology.from_dict(manifest['ontology'])`. A ~10-line `parse_page(paths, title)`
  helper would make `page-gen` clean.
- **Poll / favorite counts are prose-only.** Each poll's table sits in an un-crawled
  `{{Popularity_Poll_N}}` template (main-namespace crawl only; zero `Template:*` pages).
  The only stored source is the character's Trivia prose ("Angel ranked 69th in the third
  Popularity Poll with 7 votes") + the poll section's announcement issue + total votes.
  → the **prose pass** owns them (do NOT crawl the templates).
- **No citation-span table in `facts.db`.** Section-level `{{Ref}}` locators live in the
  crawl JSON `sections[].citations` (or `citations.parse_markers` on `sections.text`).
  `citations.attribute(text, index)` / `span(found)` compute the `sourced:` string a beat
  carries.
- **Battle result is owner-perspective** (`battle_result`, G2). A generated result
  question must be phrased from the table-owner's side (or carry the subject) or it
  scores the mirror answer.

---

## 4. The batch schema (what `page-gen` emits)

`questions/_<series>_page_<slug>.json`:
```
{ series, wiki, updated, note,
  retired:   [ {id, question, item, reason} ],
  questions: [ {
        id: "jjk-pg-<slug>-NNN",        # unique across the whole bank
        kind: "set" | "fact",           # KINDS (eval/questions.py:52)
        question: "...",
        subject: "...",                 # required
        tier: "wiki",                    # TIERS (questions.py:38)
        scope: "closed" | "core",       # core => recall-only, no precision
        expect_mode: "roster"|"qa"|"narrative",   # judged by the harness
        answer: [ {item, aliases: [], sources: [], tier: ""} ],  # >=1, non-community items score
        sources: ["https://..."],        # required URL, not in BLOCKED_DOMAINS
        verified: "YYYY-MM-DD",          # required date
        absent: [], accept: "all", note: ""
  } ] }
```
- **Validator** `Q.validate` (`scriptengine/eval/questions.py:262`): unique ids; `subject`
  + `verified` date present; all `sources` are non-blocked URLs; a `set` needs >=1
  `wiki`-tier item + >=1 scored (non-community) item. `Q.load_all` (L250) skips `_*.json`
  (campaign batches stay out of the official bank).
- **Consumer** `page_campaign.run(series, slug, ...)` (`eval/page_campaign.py:45`):
  `Q.load_file` + `Q.validate`, splits set/fact, scores sets with `canon_gold.score_sets`
  (exact: found / missing / intruders) and facts with `canon_gold.score_facts` (answer
  present in the `/context` bundle); writes
  `reports/page-campaign/<series>-<slug>-<run-id>/{scores.json, run.json, REPORT.md}`;
  exit 2 until 100%. CLI: `page-run --series jjk --batch <slug>` (`cli.py:1511`).
- **Roster decls** → `overrides.yaml → rosters:` (YAML fragment: `name / match / subject
  / members`). Consumed by `build_roster` (`retrieve/roster.py:1136`); declared beats
  discovery (G6, `_declared_members` L2881); `battles_in` (L992); `battle_result` (L832).
  A member may be a page title, a section, or a bare string — so a set the wiki never
  filed as a category is still answerable.

---

## 5. The `page-gen` command (the design)

Signature:
```
python -m scriptengine.cli page-gen --series jjk --page "Angel" \
    [--out PATH] [--verify-sheet PATH] [--no-prose-scaffold]
```

`page-gen` owns **Phase 1** (deterministic) and **emits the artifacts** Phases 2–4
consume. Phases 2 and 3 are single-subagent passes (Rule A). Phase 4 is the existing
assemble/merge + `page-run` + coverage gate.

### Phase 1 — Generate (structured, zero reading)
Read `facts.db`; write the **structured half** of the batch + artifacts:
- `questions/_jjk_page_<slug>.json` — the structured questions, each with a
  **provenance marker** in `note` (e.g. `note: "page-gen:identity:status"`).

**Batch-file ownership (single file, not six section files):** `page-gen` writes the
structured half directly into the one batch `questions/_jjk_page_<slug>.json`. The
Phase-3 prose subagent then *appends* the prose half to the **same file** (never touching
the `page-gen:`-marked questions). The old "six `sectionN.json` files → assembler" step is
superseded; `jjk_assemble.py` is used only for its `overrides.yaml` **merge** step
(text-insert). Idempotency: re-running `page-gen` regenerates only the `page-gen:` subset.
- `questions/_jjk_page_<slug>.decl.yaml` — the roster decls (§5.4).
- `questions/_jjk_page_<slug>.coverage.json` — the **coverage ledger** (§5.3).
- `questions/_jjk_page_<slug>.verify.json` — the **verify sheet** (§5.2).

Catalog (deterministic templates, keyed to `facts.db` — §6): identity (one question per
`facts_for` field, empty field → auto-retire), per-battle block (per battle in
`battles_in`), technique + closed-set rosters.

**Idempotent + non-clobbering:** re-running `page-gen` regenerates only the
`page-gen:`-marked (structured) questions and **never touches** hand-authored prose
questions. It reads any existing batch, keeps non-`page-gen` questions, and replaces the
structured subset. This is what lets it reconcile the in-progress Angel cluster (whose
S1–S4 are hand-written) — see §9.

### Phase 2 — Verify structured (the user-added step)
`verify.json` lists each structured question + the exact field/edge/span it came from +
the page section it should match. A **single subagent** (Rules A+B) reads the actual wiki
page (`series/jjk/wikitext/<Page>.json`, field `wikitext`) and cross-checks each
structured question — "did the generator declare the right things?" (right members, no
stale value, no missed field, direction correct, alias-vs-name clean). Wrong declarations
get **fixed in the batch here**, before they become campaign questions. Output: a short
table of fixes/retires + the count still clean.

### Phase 3 — Prose (read manually, as before)
A **single subagent** (Rules A+B) reads ONLY the **uncovered sections** from
`coverage.json` (battle *Battle* beats "how did X defeat Y", Synopsis beats,
Personality/relationships, Trivia polls/favorites) and **authors** the prose questions +
declares prose-derived rosters, appending them to the batch (never touching the
structured half). This is now ~1/3 of the questions (prose only), not the full 300.

### Phase 4 — Assemble + merge + completeness gate
- Assemble/merge: merge `decl.yaml` (+ any prose subagent decls) into `overrides.yaml`
  by text-insert (the `jjk_assemble.py` merge step).
- `page-run --series jjk --batch <slug>` to **100%** (everything retrievable).
- **100% section coverage**: the `coverage.json` ledger proves no section of the page is
  left out; any uncovered section must be explained (prose-passed or retired-with-reason).
- **Six-class scan** (the 6 classes, plan §six-class).

### 5.2 The verify sheet (`verify.json`)
```
[ { question, kind, answer,
    source: "facts.status | edges.side1-><battle> | abilities-><technique>",
    page_span: "<the page text the answer must match>",
    section: "<header path where it should be confirmed>" } ]
```
This is what makes Phase 2 a *check* (not a re-derivation): the subagent confirms each
generated answer against `page_span` on the page.

### 5.3 The coverage ledger (`coverage.json`)
```
{ sections: [ { path: "Synopsis/Culling Game Arc", covered_by: ["jjk-pg-angel-208", ...] } ],
  uncovered: [ "Trivia/Popularity Polls" ],   # prose-pass targets
  retired_sections: [ { path: "...", reason: "unchunked infobox kanji cell" } ] }
```
Built from `document_sections(page)`. It is the **mechanism for "nothing left"**: the
gate fails if a section is neither `covered_by` a question nor explained in
`retired_sections`.

---

## 6. The structured-question catalog (deterministic templates)

The field→question table (this is the "fields are identical in every page" part the
generator automates). Golds are the field's verbatim value; empty field → auto-retire.

**Identity (from `facts_for(page)`):**
| field | question | note |
|---|---|---|
| `status` | "What is X's status?" | e.g. Deceased |
| `alias`/`aliases` | roster "X's aliases" + "What are X's aliases?" | single-field set |
| `affiliation` | roster "X's affiliations" | single-field set |
| `debut` (manga ch / anime ep) | "In which manga chapter does X first appear?" / "In which anime episode is X first depicted?" | one per medium present |
| `creator` | "Who created X?" | only if present |
| `voice_actor` | "Who is X's Japanese/English voice actor?" | JP/EN separately |
| `grade`/`rank`, `race`, `age`, `gender`, `occupation`, `bloodtype`, `height`, `weight`, `birthday` | one attribute question each | verbatim value |
| `kanji`/`romaji` | "What are the kanji for X's name?" | **only if chunked**, else retire (unchunked infobox cell) |

**Per-battle (per battle B naming X, from `battles_in` + B's `facts` + `powers1/powers2`):**
- "What is the outcome of B?" (B's `outcome`, phrased from the owner's side)
- "Where did B take place?" (B's `place`/`event`)
- "In which episode is B depicted?" (**only if B has an `episodes` fact/edge**)
- "Which manga chapters cover B?" (B's `chapters`; a range → narrow to the retrievable
  start endpoint, "In which manga chapter does B begin?")
- "Which techniques did X use in B?" (X's side's `powers1`/`powers2`; a set → roster, or
  qa if a contiguous span)
- roster: "Every battle involving X" (the `battles_in` set)

**Technique + closed sets:**
- roster "Every named technique of X" (`collect_abilities`)
- alias/affiliation single-field rosters (above)
- relative/cousin/affiliation rosters (`relations`/`edges`)

**NOT in the catalog (prose → Phase 3):** battle "how"/key beats, Synopsis beats,
Personality/relationship prose, Trivia polls/favorites.

**Routing-trap rules the generator enforces by construction** (so the generated
questions don't re-introduce the known misses): wh-word-first (never a leading
"According to X"); "Who" not "Whom"; no "in order to"; no "how many" (phrase counts as
attribute lookups); `arc`/`saga` not in a roster `match` phrase (the chronology path
intercepts `every/all` + `arc|saga`); singular for relatives; digit-vs-word must match
the page.

---

## 7. Verification & gates

- **Per cluster:** `page-run` to **100%** (everything retrievable) **+ 100% section
  coverage** (the ledger) **+ the six-class scan** (possessive-ownership, alias-vs-name,
  incomplete answers, garbled names, direction, sentence-worthiness).
- **`page-gen` is a `.py` change** → after implementing and running it, the **full gate
  applies**: `eval --series jjk` 24/24, `canon-run --series opm` at baseline (8/16 +
  235/237 + 78.5% + 18/20), `pytest tests/ -q` 985. **Restart the server** after the `.py`
  change.
- **TDD the generator itself:** a new `tests/` file covering the catalog (each field
  template), the coverage ledger (uncovered detection), the verify-sheet shape, and
  idempotency (re-run never clobbers a non-`page-gen` question). Run with the suite.

---

## 8. Gaps & recorded decisions

- **Poll/favorite counts:** prose-only source → the Phase-3 prose pass owns them (gold
  from Trivia prose, as the S6 subagents already did). Do **not** crawl
  `Template:Popularity_Poll_*`.
- **No single-page parse helper:** add a small tested `parse_page(paths, title)` in
  `ingest/crawler.py` (compose `WikiPage.from_dict` + `reextract` + `Ontology`).
- **Battle `episodes` often absent:** generate the episode question only when the
  fact/edge exists (`fact_keys()` presence).
- **Battle result owner-perspective:** phrase generated result questions from the
  owner's side.
- **Uncchunked regions** (`{{Volumes}}` scrollbox, infobox `kanji`/`romaji`,
  `{{Nihongo}}`/`{{Ruby}}` cells) are not retrievable → the generator retires them
  with the reason in `retired`; it does not silently re-gold.

---

## 9. Rollout plan

1. **Implement `page-gen` (TDD):** the catalog, the coverage ledger, the verify-sheet
   emitter, idempotency, and the `parse_page` helper. Gate triple green (eval /
   canon-run / pytest); restart the server.
2. **Angel (finish the in-progress cluster):** reconcile the hand-written S1–S4 with
   `page-gen`. Default: run `page-gen` on Angel (it regenerates the structured half and
   keeps the hand-authored prose), then Phase 2 (verify structured) + Phase 3 (prose, now
   only the uncovered S5/S6-equivalent sections: Synopsis beats + Trivia) + Phase 4 gate.
   Alternative if cleaner: finish Angel's S5/S6 the old 6-section way first, then let
   `page-gen` own every *future* cluster. Decide at build time; record the choice in
   STATUS.md.
3. **Remaining 9 Phase-2 clusters** (Shibuya Incident Arc, Culling Game (mechanic),
   Reverse Cursed Technique, Ten Shadows Technique, Kinji Hakari, Shinjuku Showdown Arc,
   Sorcerer Clan, Jujutsu Sorcerer, List of Characters) end-to-end through `page-gen`.
4. **Phase 3** — 200 fresh questions in `questions/_jjk_page_round3_fresh.json`; the
   fresh-question generator reuses the `page-gen` catalog + a cross-corpus spread, with
   hard dedup against `jjk.json`, `_jjk_battles.json`, every `_jjk_page_*.json`, and
   every `retired` entry (a temp-dir script, not by eye; report the collision count).
5. **Phase 4** — repeat the global backport over the Phase-3 failures.

---

## 10. Definition of done (for this design)

- `page-gen` implemented, TDD'd, gated (eval 24/24, canon-run opm at baseline, pytest
  985; server restarted after the `.py` change).
- Reusable across all remaining clusters; Rules A (1-subagent) and B (graphify) honored
  in the implementing session (every subagent prompt carries both).
- At least one cluster (**Angel**) completed end-to-end through `page-gen` at 100% +
  100% section coverage.
- `reports/page-campaign/STATUS.md` gains a row per `page-gen` cluster (structured Qs
  generated, prose Qs, rosters declared, retires with reasons, coverage result).
- `STATUS.md` / a round-4 handoff note where the spec lives and how to run `page-gen`.

## Out of scope
- No retriever tuning for a single prompt. If a page reveals a routing gap that cannot
  be fixed by a rephrase, a roster declaration, or a bounded gated `.py` fix, stop and
  report (per the campaign rule).
- No spelling-correction layer (deferred).