# Round-2 handoff — global fixes, remaining clusters, 200 fresh questions

> **Starting round 2 in a fresh session? Read this file top to bottom, then
> `HANDOFF_OPM.md` (environment rules) and `WRONG_ANSWERS.md` (the classified
> wrong-answer inventory).** The plan this round executes lives here; round 1's
> plan (`plans/opm-top25-page-campaign.md`) is done.

## Kickoff decisions (recorded 2026-08-22, round-2 session)

1. **`.py` scope** — confirmed. Round 2 authorizes bounded `.py` fixes; each is
   gated (canon-run holds 8/16 + 235/237 + 78.5% + 18/20, pytest 985, eval
   jjk 24/24 after any shared change, re-runs of every batch with revivals).
   Per-wiki specifics still live in `series/<name>/overrides.yaml`, never in
   `.py`.
2. **Ship set** — G1 + G2 + G5 + G6 ship this round. G3 (romaji/kanji
   chunking), G7 (how-many passages) and G8 (unchunked-region chunking) are
   deferred with reasons, recorded in the checklist below (round-3 candidates).
3. **Long tail** — continue past cluster 20 to the top-35 by corpus size:
   clusters 16-20 (Boros, Superalloy Darkshine, Phoenix Man, Fuhrer Ugly,
   Mysterious Beings), then the long tail (Homeless Emperor, Bad, Evil
   Natural Water, Fubuki, Overgrown Rover, Speed-o'-Sound Sonic, Gouketsu,
   King, Isamu, Puri-Puri Prisoner, Suiryu) plus the structural page
   `Characters aware of Saitama's power` (177 KB, unassigned).
4. **200-question split** — all 200 OPM
   (`questions/_opm_page_round2_fresh.json`).
5. **JJK queue** — deferred to round 3. Engine fixes reach JJK automatically
   (shared engine); JJK batches re-run after any shared `.py` change per the
   gate set, and eval jjk 24/24 stays the canary.

## 0. What changed since round 1

Round 1 (complete 2026-08-21): all 15 OPM clusters at a clean sweep — 12 at
100/100, Story Arcs 97/97, Flashy Flash 91/91, Deep Sea King 84/84 — under the
rule **no `.py` changes, no retriever tuning**. Two structural findings were
recorded, not fixed (chronology intercept, scorer one-s fold), and every
battle-result / relationship / Japanese-name / quote question that could not be
fixed by rephrasing was retired in place with a reason.

Round 2 has three phases:

1. **Global fix pass.** Read every wrong answer the engine got in the cluster
   runs (`WRONG_ANSWERS.md`), fix each failure mode *globally* — so the pages
   that were never in a cluster run inherit the fix — and verify each fixed
   answer manually against the wiki, not just the score.
2. **Remaining clusters.** Plan-queue rows 16-20 (Boros, Superalloy Darkshine,
   Phoenix Man, Fuhrer Ugly, Mysterious Beings umbrella), plus an optional
   long tail.
3. **200 completely new questions** not in any official bank, any cluster
   batch, or any retired list.

**Rule change (confirm at kickoff):** round 2 authorizes bounded `.py` fixes.
Each one is gated (below); per-wiki specifics still go in
`series/<name>/overrides.yaml`, never in `.py`. The round-1 campaign rule
stayed true for 15 clusters; this round relaxes it on purpose.

## 1. Environment & commands (unchanged from round 1)

- Repo `E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine`, Windows PowerShell
  5.1 (no `&&`; use `cmd1; if ($?) { cmd2 }`).
- Python: `E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine\scriptengine\.venv\Scripts\python.exe`,
  `$env:PYTHONIOENCODING="utf-8"` before anything that prints macrons.
  Throwaway scripts go in `C:\Users\Nikhil\AppData\Local\Temp\opencode\*.py`,
  never inline `-c`.
- Server: `python -m scriptengine.api.main` on `:8000`, `/health` must show
  `"device":"cuda"`. **Restart after any `.py` or overrides.yaml edit.**
- Scoring: `python -m scriptengine.cli page-run --series opm --batch <slug>`
  (loads `questions/_opm_page_<slug>.json`, exit 0 = 100%, 2 = failures).
- Gates: `python -m scriptengine.cli canon-run --series opm` (baseline
  **8/16 exact, 235/237 canon 99.2%, 78.5% precision, 18/20 fact**, held since
  2026-08-20-2312) and `python -m pytest tests/ -q` (baseline **985 passed**).
  Any `.py` change also runs `python -m scriptengine.cli eval --series jjk`
  (baseline **24/24**) — the engine is shared and JJK is the canary.

## 2. The wrong-answer inventory (read first)

`reports/page-campaign/WRONG_ANSWERS.md` — regenerated from every
`reports/page-campaign/<series>-<cluster>-*/scores.json` plus every batch's
`retired` field. **461 distinct failed questions, 301 retired.**

| mode | count | where the answer actually lives |
|---|---:|---|
| battle-result | 76 | `X_Battles` subpage tables (Result column, chunked) + battle-page infoboxes |
| ability-what | 39 | Abilities chunks (gold-phrasing + top-8 retrieval) |
| count-routing | 26 | prose numbers; `how many` routes roster, which carries no passages |
| quote-statement | 25 | Quotes sections / cquotes (often unchunked) |
| japanese-name | 24 | infobox `kanji`/`romaji` fields, `{{Nihongo}}`/`{{Ruby}}` cells (unchunked) |
| chapter-title | 16 | JJK `{{Volumes}}` scrollbox titles (unchunked) |
| relationship | 11 | `X_Relationships` subpages (chunked) + the extracted `relations` table (359 rows / 88 chars on OPM) — but the qa bundle never carries it |
| arc-structure | 8 | chronology chain |
| isbn | 4 | volume-page infobox ISBN fields |
| plot-detail | 10 | plot chunks (retrieval/phrasing) |
| other | 211 | long tail: trivia, attribute lookups, plural-wh misroutes |

## 3. Phase 1 — the global fixes

Each row: the gap, the fix, the gate, and the manual verification. Fixes are
ordered by value-per-risk; **the recommended ship set is G1, G2, G5, G6** (the
rest are decision gates at kickoff).

### G1 — battle-result questions (76) — *recommended*

The data is on disk and chunked: `series/opm/wikitext/Bang_Battles.json` has a
`Participants | Chapter(s) | Episode(s) | Result` table ("Bang vs. Garou |
153, 155, 158 | None | Loss"), rendered into chunk text by the table parser.
The `X vs. Y` battle-page infoboxes carry combatants/arc/chapter edges, but
their `Outcome` field (present on only 31 of 139 battle pages) names
aftermath participants, not a win/loss — so the `X_Battles` table's Result
column is the authoritative win/loss source. 34 `X_Battles` subpages and 28
`X_Relationships` subpages exist in the crawl. What failed: "What is the
result of the battle between X and Y?" resolves subject=X (a character) and
the qa top-8 ranks X's own page above the battle table, so the Result cell
never surfaces.

- **Fix:** extend the roster battles-in path (`scriptengine/retrieve/roster.py`,
  the path that already answers "every fight X has been in" from the wiki's
  battle infoboxes) to (a) route "result of the battle between X and Y" to the
  subject's `X_Battles` table, and (b) read the per-fight **Result** cell from
  that table (the `X vs. Y` infobox `Outcome` field is aftermath participants,
  not a win/loss, so it is not the source). One mechanism covers all 34
  subpages.
- **Gate:** canon-run holds 8/16 / 235-237 / 78.5% / 18-20; pytest 985; then
  re-run the four OPM batches that retired battle questions (Bang, Orochi,
  Beaut, Flashy Flash) — the retired battle questions should now be
  **revivable** (re-add them and confirm they pass).
- **Manual wiki check:** for every revived battle question, open the subject's
  `X_Battles` subpage stored wikitext (`series/opm/wikitext/<X>_Battles.json`),
  read the Result column of the named fight's row, and confirm the answer
  matches that cell verbatim. Where the stored crawl looks stale, spot-check
  the live subpage (`https://onepunchman.fandom.com/wiki/<X>/Battles`).

### G2 — relationship questions (11 + retired) — *recommended*

The LLM-extracted `relations` table already holds OPM (359 rows across 88
characters, `series/opm/facts.db`). Two gaps: the qa bundle's `relations` comes
from graph edges only (`retrieve/hybrid.py:204-210`, `store.edges_for`), so the
extracted rows — which carry the verbatim `quote` that actually answers
"who is X to Y" — never reach the bundle; and the scorer's haystack
(`scriptengine/eval/canon_gold.py:113-115`) folds only
`source / relation / target`, dropping `quote` and `era`.

- **Fix:** merge `store.relations_of(subject, both_ways=True)` into
  `result.relations` (with `quote`/`era` fields), render the quote in
  `api/context.py` (the "## Relationships" section, line ~410), and include
  `quote`/`era` in `canon_gold.haystack`.
- **Gate:** canon-run + pytest + re-run the relationship questions from the
  Orochi / Beaut / Flashy Flash / Bang / God batches (revive the retired ones).
- **Manual wiki check:** for each revived relationship question, open
  `series/opm/wikitext/<X_Relationships.json>` and confirm the stored
  `relations` row's quote is verbatim in that page's text.

### G3 — Japanese names / romaji / kanji / Viz (24 + JJK retires) — *decision gate*

The romaji lives only in infobox `kanji`/`romaji` fields and inline
`{{Nihongo}}`/`{{Ruby}}` cells — unchunked by construction (the JJK campaign
retired the same class).

- **Fix (big):** the chunker emits infobox kanji/romaji fields and Nihongo
  cells as chunked text (`scriptengine/ingest/wikitext.py` /
  `scriptengine/index/chunker.py`), then `python -m scriptengine.cli
  index --series opm` (and `jjk`) re-parses the whole corpus from stored
  wikitext. Revive the retired romaji questions afterwards.
- **Fix (cheap):** keep them retired, documented as the wiki's unchunked
  region (round-1 precedent).
- **Gate (if big):** full reindex, then canon-run + pytest + **eval jjk 24/24**
  (the chunker is shared), then re-run the affected clusters.

### G4 — ability "what does X's Y do" questions (39) — *mostly gold rules, optional engine piece*

Most of these were paraphrase-vs-verbatim gold errors (the gold said
"regenerate with heart intact" where the wiki says "wore his own flaming
cloak"), a few were top-8 retrieval misses.

- **Gold rule (no code):** gold the exact contiguous substring of the
  chunked Abilities passage, and probe it live against `/context` before
  committing (the round-1 probe scripts are in
  `C:\Users\Nikhil\AppData\Local\Temp\opencode\probe2.py` / `validate4.py`).
- **Optional engine piece:** ability facts are also LLM-extracted into the
  `abilities` table (served by `/abilities/{series}/{entity}`) but are not in
  the context bundle. If ability questions should be bundle-answerable, add
  the subject's ability kit (`retrieve/abilities.collect_abilities`) to the
  bundle and to `canon_gold.haystack`. Gate as G2.

### G5 — scorer verb-form artifact (the DSK `smashed`/`smashe` finding) — *recommended*

`canon_gold.norm` (line 73) folds only a single trailing `s`; chunked text
inflections (`smashe`) never match golds of `smashed`, so ~18 DSK questions
had to be re-golded to sub-phrases.

- **Fix:** make the fold stem verb endings on both sides (strip `-ed`/`-s`
  before the existing one-s fold), in `scriptengine/eval/canon_gold.py`.
- **Gate:** canon-run must still show 8/16, 235/237, 78.5%, 18/20 (the fold
  runs on the official bank too), pytest 985, eval jjk 24/24. If any official
  number moves, revert and keep the gold rule instead.
- **Manual wiki check:** re-add the re-golded DSK questions with their
  original full-phrase golds and confirm they pass with the new fold.

### G6 — chronology intercepts declared rosters (Story Arcs + DSK sets) — *recommended*

`retrieve/chronology.py:516-523` (`wants_chronology`, `_NAMES_AN_ARC`,
`_ASKS_FOR_ARCS`) intercepts any "arc(s)"/"saga(s)"/"every battles" query and
returns the full 15-arc chain, ignoring declared per-saga and per-character
rosters. That is why the Story Arcs saga-membership sets (15 retired) and the
Deep Sea King battles set (1 retired) were "structurally unanswerable".

- **Fix:** a declared roster whose match phrase hits the query wins over the
  chronology intercept (router/chronology `.py`).
- **Gate:** canon-run + pytest + eval jjk; then re-run the Story Arcs and DSK
  batches with the retired set questions revived.
- **Manual wiki check:** confirm each revived set matches the wiki's own
  arc/saga listing (Story Arcs index page, stored wikitext).

### G7 — "how many" routes to roster (26) — *decision gate*

Contract limitation flagged in round 1 (JJK STATUS "flagged, not fixed"):
`how many` → roster, and rosters carry no passages, so prose-stated counts
never surface. Round-1 workaround: phrase as attribute lookups.

- **Fix (if wanted):** let count-shaped queries also carry the top passages
  (`router.py` `_COUNT` rule). This changes routing for every wiki — ship only
  with the full gate set and a re-run of both canon banks.

### G8 — unchunked regions: index-page leads/tables, cquotes, JJK scrollboxes (11 + 25 + 16 + 4) — *decision gate*

Story Arcs' index lead ("fan-made or community-made", the Arc Notes section),
Blast's cquote ("humanity is in peril"), and JJK's `{{Volumes}}` scrollbox
chapter titles are all unchunked template/lead regions.

- **Fix (if wanted):** chunker includes list-page leads + tables and cquote
  content; reindex both series; revive the retired questions.
- **Otherwise:** stay retired with reasons (round-1 precedent).

### Cross-cutting: manual wiki verification protocol (the user's explicit ask)

A fix is **not** done when the engine scores it. For every revived or new
question:

1. Fetch the answer from the live server (`page-run`, or the probe script).
2. Read the answer against the **stored wikitext**
   (`series/<series>/wikitext/<Page>.json`, field `wikitext`) — the exact
   source the engine indexes.
3. Where the crawl may be stale, spot-check the live fandom page.
4. Run the six-class review (STATUS.md "Review checklist") over the revived
   question — direction, completeness, circularity, grammar.
5. Record verification in `WRONG_ANSWERS.md` (add a `verified` line under each
   revived question) so the audit trail lives with the inventory.

## 4. Phase 2 — remaining clusters

Same per-cluster loop as round 1 (survey the page → 100 questions → declare
rosters in overrides.yaml → `page-run` to 100% → six-class review → gates →
STATUS.md row). After Phase 1, battle-result / relationship / romaji questions
can be written in their **natural phrasing** — the payoff of the global fixes.

| # | cluster | batch slug | page size | notes |
|---|---------|-----------|----------:|-------|
| 16 | Boros | `boros` | 126 KB | Saitama's benchmark fight; battle pages exist |
| 17 | Superalloy Darkshine | `superalloy_darkshine` | 124 KB | webcomic-era content — canon-scope notes |
| 18 | Phoenix Man | `phoenix_man` | 133 KB | + `Child Emperor vs. Phoenix Man_ Round 2` battle page |
| 19 | Fuhrer Ugly | `fuhrer_ugly` | 130 KB | done 2026-08-22 — 105/105, see STATUS row 28 |
| 20 | Mysterious Beings (umbrella) | `mysterious_beings` | 135 KB | `Mysterious Beings` + `_Unnamed` (135 KB) + `_Monster Association` (293 KB, the 6th-largest page; already used by cluster 14 — decide fold-in vs. separate) |

**Optional long tail (kickoff decision — how far down the size ladder):**
Homeless Emperor (117 KB), Bad (117), Evil Natural Water (117), Fubuki (113),
Overgrown Rover (111), Speed-o'-Sound Sonic (109), Gouketsu (107), King (107),
Isamu (106), Puri-Puri Prisoner (106), Suiryu (100). Plus the structural page
`Characters aware of Saitama's power` (177 KB — the 12th-largest page,
unassigned).

**JJK continuation (kickoff decision):** JJK is at 9/25 clusters; the queue
continues Kenjaku, Choso, Reverse Cursed Technique, Toji Fushiguro, Ten
Shadows Technique, Nobara Kugisaki (STATUS.md "Queue"). Round-2 engine fixes
apply to JJK automatically (shared engine) — re-run the JJK batches after any
shared `.py` change.

## 5. Phase 3 — 200 completely new questions

- **Bank file:** `questions/_opm_page_round2_fresh.json` — the underscore
  prefix keeps it out of the official bank, and `page-run --series opm
  --batch round2_fresh` scores it directly (no engine change needed).
- **Dedup before adding each question** — it must not appear in:
  (a) the official bank `questions/opm.json` (39 questions),
  (b) any of the 15 round-1 `_opm_page_*.json` batches,
  (c) the 301 retired questions (`WRONG_ANSWERS.md`),
  (d) any `questions/*.json` bank for that series.
  Write a small dedup script (NFKD-fold, exact match + contiguous-substring
  both directions) and run it over the finished sheet.
- **Content:** new angles the cluster batches did not cover — the long-tail
  S-Class and monsters from §4, organisation/association details, webcomic-only
  canon (scope `closed` + note, per round-1's canon-scope rule), and
  cross-character questions. Every answer verified verbatim in the stored
  wikitext **before** scoring (the gold-writing rule, not after).
- **Target:** ≥ 95% on the first `page-run`; triage every miss against
  wikitext to 100% (or retire with a reason, recorded in the batch's
  `retired` field).
- **Series split (kickoff decision):** default all-200 OPM; a JJK share is
  possible (JJK eval is the canary anyway).

## 6. Gates (after every phase, in this order)

1. `python -m scriptengine.cli canon-run --series opm` — holds **8/16 exact,
   235/237 (99.2%), 78.5% precision, 18/20 fact** (or improves).
2. `python -m pytest tests/ -q` — **985 passed**.
3. `python -m scriptengine.cli eval --series jjk` — **24/24** (only after any
   shared `.py` change).
4. Re-run every batch that retired questions the new fix revives.
5. Update `STATUS.md` (new rows + the round-2 section) and this file's
   checklist below.

## 7. Kickoff decisions (confirm before touching code)

1. **`.py` scope** — is the round-2 relaxation of the no-`.py` rule confirmed?
2. **Ship set** — recommended G1 + G2 + G5 + G6 now; G3/G7/G8 deferred. OK?
3. **Long tail** — stop at cluster 20, or continue to a size cut (suggest
   top-35 by corpus size)?
4. **200-question split** — all OPM, or OPM + JJK?
5. **JJK queue** — continue JJK clusters 10-25 this round or defer?

## Checklist (fill in as the session goes)

- [x] Kickoff decisions 1-5 recorded (2026-08-22: .py relaxation confirmed;
      ship G1+G2+G5+G6; continue to top-35; all 200 OPM; JJK queue deferred)
- [x] G1 battle-result fix shipped + gated + battle questions revived & wiki-verified
      **2026-08-22: shipped.** `roster.battle_result` reads the first-named
      side's `X/Battles` table (the wiki records the Result from the table
      owner's perspective, so the mirror table holds the mirror image of the
      answer -- `battle_result_fighter` keys the read to the `between` span's
      first party), with `series/opm/overrides.yaml` `series_titles` keeping
      the "in One-Punch Man?" tail out of the match. New router rule 2c
      (probe-gated). 12 battle questions revived across Bang/Orochi/Beaut/
      Flashy Flash (one duplicate deduped; the Orochi chapter-locator kept
      retired with reason); all four batches at 100% (103/104/102/94) and
      every revived gold read verbatim off the stored `X_Battles` table.
      Gates green: canon-run 8/16 + 235/237 + 78.5% + 18/20, pytest 985,
      eval jjk 24/24.
- [x] G2 relations merge shipped + gated + relationship questions revived & wiki-verified
      — **2026-08-22.** `hybrid.py` now appends `store.relations_of` rows for the
      top three linked entities (both_ways, deduped; edge rows gain empty
      quote/era so both kinds share one form); `api/context.py` renders
      ` (era)` + `: quote` on the Relationships lines and hoists rows whose
      two ends are both named in the question ahead of the top-20 slice (a
      pair's row filed under the other character's page was falling past it);
      `rank_relations` breaks confidence ties in favor of quoted rows;
      `canon_gold.haystack` folds era + quote. 7 relationship questions
      revived (Orochi 2, Beaut 1, Flashy Flash 2, Bang 2) re-golded to the
      distinct relation labels the store holds for the pair; 5 stay retired
      with refreshed reasons (no extracted row for the pair: Tatsumaki-Orochi,
      Genos-Beaut, Genos-FF, Psykos-God, Orochi-God). All five batches at 100%
      (orochi 106/106, beaut 103/103, flashy_flash 96/96, bang 105/105,
      god 100/100); sources point at the Relationships subpages (the Sonic
      questions add the Synopsis page, where three of their quotes live).
      Manual check: 29/29 gold-label quotes verbatim in rendered page text
      (27/29 by raw-wikitext match; the other two are link
      target/label interleavings, eyeballed against the stored wikitext).
      Gates green: canon-run 8/16 + 235/237 + 78.5% + 18/20, pytest 985,
      eval jjk 24/24.
- [x] G5 norm stem-fold shipped + gated (official bank unchanged)
      — **2026-08-22.** `canon_gold.norm` now drops a trailing `ed` before
      the one-s plural fold (`smashed` -> `smashe`, meeting the chunk's
      truncated inflection), same four-letter guard. A trailing-`e`
      extension (`smashe` -> `smash`) was tried and reverted: it merges
      `Normal Punch` with the `normal punches` alias of `Consecutive Normal
      Punches` and breaks the bank's distinctness invariant (opm-set-01,
      pytest 984/985). Manual check: all 18 re-golded DSK questions were
      re-added with their original full-phrase golds and none passed -- the
      class was broader than verb inflection (irregular `blew`/`blows`,
      `-ing` forms, and plain paraphrase). 17 were re-golded to the wiki's
      exact contiguous phrasing (the G4 gold rule, read off the stored DSK
      chunks); sea-100 retired (no supporting text on the page); sea-089
      retired (Trivia answer sits outside the top-8 beats, retrieval miss
      left un-tuned per campaign rule); sea-026 re-golded `Acid
      Manipulation` -> `Acid Spit` (the battle infobox's own term, old item
      kept as alias). DSK batch 100/100. Gates green: canon-run 8/16 +
      235/237 + 78.5% + 18/20, pytest 985, eval jjk 24/24.
- [x] G6 declared-roster-wins shipped + gated + Story Arcs / DSK sets revived
      — **2026-08-22.** `roster.build_roster` now resolves the declared
      rosters before the chronology intercept, and the intercept fires only
      when no declared roster claims the query (`declared is None and
      chronology.wants_chronology(query)`), so "the arcs in the hero
      association saga" returns the declared 6-member set instead of the
      15-arc chain (the single fix covers both the router rule-1 entry and
      direct roster calls). One declared roster added to
      `series/opm/overrides.yaml` — `Every overarching saga of One-Punch Man`
      (Introduction / Hero Association / Human Monster / Neo Heroes,
      transcribed from the index page's four `== <Saga> Saga ==` headings) —
      to make the "overarching sagas" phrasing answerable. Revivals:
      `opm-pg-story_arcs-098` (set: the 4 overarching sagas — EXACT on the
      declared roster; members verified against the index page's headings)
      and `opm-pg-sea-103` (fact: DSK battles, gold = the 7 battle pages of
      the DSK page's own `Major Battles` section, all present in the
      19-member roster superset, presence scoring). The other 14 story_arcs
      retires got refreshed live reasons (unchunked index lead/tables = G8;
      the two arc webcomic-range questions are partial coverage in the
      bundle; the three "in which arc does X appear" questions carry no arc
      attribution in the character bundles; the ordinals/arc-notes
      questions are unreachable through the chronology route). Two new
      structural findings recorded in STATUS.md (record-not-fix): the
      battles-in last-word over-match (DSK's `king` → 19-page superset vs
      the wiki-true 7; three intruders belong to the different character
      Suiryu) and the top-N borderline flip (`opm-pg-story_arcs-029`, the
      Garou chapter question — declared engine gap, retired with reason).
      Story Arcs 97/97 (run 2026-08-22-0045), Deep Sea King 101/101 (run
      2026-08-22-0040). Gates green: canon-run 8/16 + 235/237 + 78.5% +
      18/20, pytest 985, eval jjk 24/24.
- [x] G3 / G4 / G7 / G8 decisions recorded (shipped or deferred-with-reason) —
      **2026-08-22: all deferred.** G3 (romaji/kanji/Nihongo chunking):
      deferred — full OPM+JJK reindex on a shared chunker is the
      highest-risk gate in the plan; romaji/kanji questions stay retired as
      the wiki's unchunked region (round-1 precedent). Round-3 candidate.
      G4 (ability kit in bundle): the optional engine piece is deferred
      (not in the ship set); its no-code gold rule (exact contiguous
      substring of the chunked Abilities passage, probed live before
      committing) is applied to all round-2 batch writing. G7 (how-many
      also carries passages): deferred — changes routing for every wiki and
      requires the full gate set + both canon banks re-run. Round-3
      candidate. G8 (unchunked-region chunking: list-page leads/tables,
      cquotes, JJK scrollboxes): deferred — reindex-scale change; affected
      questions stay retired with reasons (round-1 precedent). Round-3
      candidate.
- [x] Clusters 16-20 at a clean sweep (+ long tail if approved)
       **Progress 2026-08-22: cluster 16 (Boros) done — 105/105 (runs
       2026-08-22-0106, 2026-08-22-0109), zero triage; no new rosters or .py
       changes; two quote questions retired up front (Quotes section outside the
       qa top-8, left un-tuned per campaign rule); gates held (canon-run
       2026-08-22-0111 = 8/16 + 235/237 + 78.5% + 18/20, pytest 985).
       Cluster 17 (Superalloy Darkshine) done — 102/102 (runs 2026-08-22-0133,
       2026-08-22-0136 after two grammar fixes); 1 set exact (G1 battles-in,
       4 battle pages), 9 G1 battle-result facts, 8 G2 relation facts; no new
rosters or .py changes; 3 retires (2 sequential before/after questions
        intercepted by the battles-in path, 1 unretrievable Synopsis sentence —
        all left un-tuned per campaign rule); 8 webcomic-only facts kept with
        scope notes. Gates unchanged (no engine edits; 2026-08-22-0111 baseline
        applies).
        Cluster 18 (Phoenix Man) done — 104/104 (first run 2026-08-22-0154
        101/104, final 2026-08-22-0156 after 3 live-probed rephrases for qa
        top-8 retrieval misses); 1 set exact (pre-declared `Phoenix Man's
        aliases`, 3 members), 3 G1 battle-result facts, 8 G2 relation facts;
        no new rosters or .py changes; 1 retire (the "Every battle" set — the
        battles-in path matches "phoenix" not "man" and returns a 4-member
        superset incl. two Suiryu-page intruders matched only on the
        video-game move "void phoenix ascension fist"; kept as a presence
        fact per the Deep Sea King 103 precedent, reason in the batch).
Gates unchanged.
         Cluster 19 (Fuhrer Ugly) done — 105/105 on the first and only scored
         run (2026-08-22-0213), zero triage; 2 sets exact (pre-declared
         `Fuhrer Ugly's aliases`, 1 member; G1 battles-in closed 3-page set),
         3 G1 battle-result facts, 2 G2 relation facts (Black Sperm, Kamikaze
         enemy rows); no new rosters or .py changes; no retires. Whole batch
         live-probed before authoring (109 probes; the 5 failures were all
         phrasing — Previous/Next infobox questions re-anchored as attribute
         lookups, 3 golds corrected to verbatim spans). Six-class review
         clean. Gate re-confirmed: canon-run 2026-08-22-0216 at baseline,
pytest 985 passed. See STATUS row 28.
          Cluster 20 (Mysterious Beings umbrella) done — 97/97 (first run
          2026-08-22-0241 75/97, final 2026-08-22-0246 after 22 live-probed
          rephrasings; all 22 first-run misses were phrasings, zero engine
          gaps). Three-page cluster (umbrella + /Unnamed + /Monster
          Association, the latter deduped against cluster 14's 7 covered
          angles); 0 set questions — the 4 set versions retired with
          intruder reasons and kept as 5 roster presence-facts scored
          against the pre-existing declared rosters (MB 207, Dragon Level
          45, Demon Level 68, MA 67); 1 further retire (the /Unnamed page's
          Removed section is gallery-dominated and its single prose line is
          not chunked — engine gap, left un-tuned per campaign rule). No
          new rosters, no .py or overrides.yaml changes; the 2026-08-22-0216
gate applies unchanged. See STATUS row 29 — this closes plan-queue
           rows 16-20.**
        **Long tail 2026-08-22: cluster 1 of the long tail, Homeless Emperor,
        done — 101/101 (first scored run 2026-08-22-0307 103/103, final
        2026-08-22-0314 after the six-class review: shabby-outfit gold
        completed to the wiki's full co-listed span with the two subsumed
        cape/crown questions removed, two circular golds trimmed; re-probed
        and re-run). Three-page cluster (character page + the `Zombieman vs.
        Homeless Emperor` battle page + cross-page facts from the `Zombieman`
        page); no new rosters, no .py or overrides.yaml changes (no `alias`
        field, no extracted relation rows). The battles-in path returned the
        8-member superset (two true battle pages + six Child Emperor pages
        via the combatant lists — the last-word over-match recurring), so the
        closed set was retired and kept as a presence fact per the DSK 103 /
        Phoenix Man precedent; 1 further retire (a Child Emperor-subject plot
        line the qa bundle retrieves from the Monster Association Arc page
        instead — retrieval miss, left un-tuned per campaign rule). 4 G1
        battle-result facts exercised. All 105 candidate golds verified
        against stored wikitext, full batch live-probed before authoring
        (101/101 active passed; the 2 misses were exactly the 2 retires).
The 2026-08-22-0216 gate applies unchanged. See STATUS row 30.
         **Long tail 2026-08-22: cluster 2 of the long tail, Bad (Metal Bat),
         done — 104/104 (final scored run 2026-08-22-0344, zero triage, after
         the six-class review fixed an "in in" grammar bug in the
         fight-style question and a circular gold on the ONE/monster-
         association question -- both re-probed live; a first 2026-08-22-0337
         pass covered the pre-review batch).** Ten-page cluster: character page
         (S-Class Rank 15 / C-Class Rank 223, alias Metal Bat, 7 named moves
         incl. the webcomic-only Whack-a-Mole Thrashing) + the `Battles`,
         `Relationships`, `Synopsis`, `Other Media` subpages + four battle
         pages; the sage battle page (`Garou and Metal Bat vs. Sage Centipede
         and Evil Ocean Water`) surveyed and excluded — stored as
         page_type=parent_tab (its Parent Tab Template precedes its Battle
         Infobox), so its infobox fields are unindexed and it is absent from
         the battle roster. One new roster: `Bad's aliases` (member "Metal
         Bat"; the alias field reads `Metal Bat (Kinzoku Batto)`,
         romaji/kanji out per G3) — per-request overrides reload, no server
         restart, no .py changes. The battles-in path returned the 133-page
         `battle` superset (the wiki's closed six-page `Metal Bat Fights`
         category unmatchable) with the sage page also missing from it, so
         the closed set was retired with no presence-fact twin (five of the
         six golds present; the sixth unreachable) — a stricter application
         of the DSK 103 / Phoenix Man / Homeless Emperor precedent. 12 G1
         battle-result facts exercised (ten manga table rows, the two
         webcomic-only rows with scope notes, the VGS audiobook "Loss") and
         4 G2 relation facts (Zenko family; Garou / Flashy Flash / Beaut
         rival rows). All 155 candidate golds verified against stored
         wikitext, full batch live-probed before authoring (129/155 first
         pass): the 26 misses = the undeclared roster (recovered by the new
         declaration), the unreachable superset, and 24 phrasings — 19
         recovered by live-probed rephrasings anchored on "Metal Bat" (the
         bare token "Bad" is weak: the voice-actor questions fell back to
         the series page's infobox facts), 1 gold error (the OVA-6
         katana-glow wording fixed to the page's verbatim "floating with
         green light surrounding it"), 5 retires (2 battle-outcome
         duplicates of kept G1 facts; 2 sage-page infobox facts on the
         misclassified page; the VGS audio-drama duplicate whose rephrase
         failed live, left un-tuned). 45 further candidates trimmed as
         lower priority to the batch cap. The 2026-08-22-0216 gate applies
unchanged. See STATUS row 31.
          **Long tail 2026-08-22: cluster 3 of the long tail, Evil Natural
          Water, done — 126/126 (final scored run 2026-08-22-0421; first run
          2026-08-22-0411 was 118/127, all 9 misses triaged against the stored
          chunks and fixed by live-probed rephrasings, zero engine gaps).**
          Cluster: character page (Dragon-level Mysterious Being / God-level
          Evil Ocean Water, MA executive, the Major Battles manga + webcomic
          tables) + the three battle pages (Atomic Samurai's Disciples,
          Child Emperor, Saitama vs. Evil Natural Water) + the `Saitama/Battles`
          and `Isamu/Battles` result tables + cross-page rows read off the
          `Tatsumaki/Battles`, `Genos/Battles` and `King/Battles` webcomic
          tables. Two new roster declarations in `series/opm/overrides.yaml`
          (per-request reload, no server restart, no .py changes): `Evil
          Natural Water's aliases` (2 members: Evil Ocean Water, Incarnation of
          Mother Sea — romaji/kanji out per G3) and `Evil Natural Water's
          battles` (6 members from the wiki's own `Evil Natural Water Fights`
          category — the battles-in discovery sees only the three battle pages
          whose infoboxes name it, the sage battle page is stored as
          page_type=parent_tab, and the two executive-raid pages name the
          executives rather than the water). The 9 first-run misses: 3
          mirrored-perspective battle-result golds (`battle_result` reads the
          first-named fighter's table — re-golded to the fighter-table values
          "Loss"/"Loss"/"Interrupted by Fubuki" read off the Tatsumaki/Genos/
          King battle tables, the ENW-perspective strings kept as three new qa
          questions from the character page's webcomic table), 2 "In which
          chapter" span questions (routed narrative; rephrased to "What manga
          chapters does the battle ... span"), 1 set phrasing stolen by the
          declared `Atomic Samurai's disciples` roster (rephrased to the
          singular attribute "What manga-original element is noted..."), 2
          Previous/Next infobox questions the battles-in wh-form intercepts
          (rephrased to "What is the preceding/following battle for"), and 3
          character-page retrieval misses (rephrased to name the subject or
          anchor "According to the ... page"). Six-class review: 1 retire
          ("How does Evil Natural Water meet its permanent demise?" — the
          verbatim gold "digested by him" is an unresolvable pronoun fragment;
          three phrasings that name Pig God were probed live and all fail
          retrieval, the 'Pig God' token crowds the Psychic Sisters Arc chunk
          out of the qa top-8, left un-tuned per campaign rule; the fact is
          covered by 071 "Pig God" and 102 "strong stomach acids"). Retires
          (3 total): the relation-typed question (the extracted `creator` row
          is unreachable — no retrieval path queries the `relations` table;
          the History prose question covers the fact), the webcomic Pig God
          result (duplicate of the kept manga-row question's string; Pig
          God's table records the mirror "Win", which the routing cannot
          reach), and the class-6 retire. All 126 golds verified against the
          stored chunks; the non-trivial phrasings live-probed against
          `/context` before committing. The 2026-08-22-0216 gate re-confirmed
          on this cluster (no engine edits): canon-run 2026-08-22-0422 =
          8/16 + 235/237 + 78.5% + 18/20 (identical to baseline), pytest 985
passed. See STATUS row 32. Long-tail queue remaining: Fubuki
           (113 KB), then the rest of the top-35 size ladder (Overgrown
           Rover, Speed-o'-Sound Sonic, Gouketsu, King, Isamu, Puri-Puri
           Prisoner, Suiryu, Characters aware of Saitama's power).**
           **Long tail 2026-08-22: cluster 4 of the long tail, Fubuki, done
           — 117/117 (both scored runs 117/117: 2026-08-22-0441 pre-review,
           2026-08-22-0444 post-review; zero triage, no retires).** Cluster:
           the character page (B-Class Rank 1 esper hero, 9 named abilities
           incl. the webcomic-only Psychic Whirlwind jamming effect, Hero
           Rating 50, alias Miss Blizzard / Blizzard of Hell, voices Saori
           Hayami / Laura Post, the yuki-onna origin trivia) + the
           `Battles`, `Relationships`, `Synopsis` and `Other Media`
           subpages + the five battle pages of the wiki's own `Fubuki
           Fights` category (Saitama vs. Fubuki…, Fubuki/Bang/Bomb vs.
           Do-S, Bang/Bomb/Fubuki vs. Overgrown Rover, Heroes vs. Do-S,
           Heroes vs. Psykos and Orochi) + the `Tatsumaki & Fubuki's
           One-Punch Song` page. One new roster declaration in
           `series/opm/overrides.yaml` (per-request reload, no server
           restart, no .py changes): `Fubuki's aliases` (2 members — the
           alias infobox field reads `Miss Blizzard (フブキ様,
           Fubuki-sama)` and `Blizzard of Hell (地獄のフブキ, Jigoku no
           Fubuki)`, romaji/kanji out per G3). First long-tail cluster
           where the battles-in path returned the closed set exactly: all
           five category pages name Fubuki in their battle-infobox
           combatant fields, so the set question stands as exact (no
           superset finding, no category fallback, no retire). 11 G1
           battle-result facts and 9 G2 relation facts exercised (incl.
           the reversed-direction Bomb and Tsukuyomi Spy rows). All 117
           golds verified against the stored chunks and the full batch
           live-probed before authoring (113/117 first pass; the 4 misses
           were 3 phrasings recovered by live-probed rephrasings — the
           King video-game-contest question (narrative routing missed the
           Relationships chunk; "Why was Fubuki shocked and awed…"), the
           Genos-OVA question (subject resolved to Genos, not Fubuki;
           "What did Fubuki find out about Genos…"), and the Grand
           Summoners question ("Which video game features…") — and the
           undeclared aliases roster, recovered by the declaration).
           Six-class review: 1 in-place gold fix (the main-attire question
           completed to the wiki's full co-listed span — dress + fur coat
           + heeled boots + pearl necklaces — re-probed and re-run).
           Webcomic-only canon kept with per-question scope notes on 6
           questions (the Garou and Tatsumaki webcomic battle results, the
           Psychic Whirlwind jamming effect, three webcomic-synopsis
           beats). Gate re-confirmed on this cluster (no engine edits):
           canon-run 2026-08-22-0442 = 8/16 + 235/237 + 78.5% + 18/20
           (identical to baseline), pytest 985 passed. See STATUS row 33.
Long-tail queue remaining: the rest of the top-35 size ladder
            (Overgrown Rover, Speed-o'-Sound Sonic, Gouketsu, King, Isamu,
            Puri-Puri Prisoner, Suiryu, Characters aware of Saitama's
            power).**
            **Long tail 2026-08-22: cluster 5 of the long tail, Overgrown
            Rover, done — 117/117 (first scored run 2026-08-22-0517 116/117,
            final 2026-08-22-0519 after the one rephrase; no retires in the
            final batch).** Four-page cluster: the character page (Dragon-level
            Mysterious Being, Monster Association executive, 4 named abilities,
            partner Black Sperm, the Don't Be Afraid extra chapter) + the three
            battle pages (`Garou vs. Overgrown Rover`, `Saitama vs. Overgrown
            Rover and Nyan`, `Bang, Bomb, and Fubuki vs. Overgrown Rover`).
            One new roster declaration in `series/opm/overrides.yaml`
            (per-request reload, no server restart, no .py changes):
            `Overgrown Rover's battles` (4 members from the wiki's own
            `Overgrown Rover Fights` category — the battles-in discovery path
            over-matches to a 5-page superset, the fifth page `Suiko vs.
            Mirror` matched only through its supporting-combatant infobox
            cell; the set question is phrased "What are all the battles of..."
            so the declared roster claims it before the battles-in path,
            mirroring the ENW precedent). 5 G1 battle-result facts exercised
            (both perspectives: the Rover-perspective "Loss"/"Win"/
            "Interrupted by..." strings from the character page's table and
            the mirror questions reading the battle pages' tables) and 2 G2
            relation facts (the Genos rival and Orochi superior rows in
            facts.db). All 119 candidate golds verified against the stored
            wikitext and the full batch live-probed before authoring: 17
            phrasings recovered by live-probed rephrasings (a "heroes"-word
            claim, four story-verb routing misses, the webcomic/manga locator
            phrasings ("Which chapter of the One-Punch Man webcomic/manga
            records..."), the five Previous/Next infobox questions the
            battles-in path intercepts ("What page precedes/follows ... in the
            One-Punch Man wiki navigation?"), and the plural-ask escape
            question — the roster route put "Garou and Tareo" only in a
            member-card's prose, outside the fact scorer's haystack, so it was
            re-asked singular as "Who does Overgrown Rover encounter...") and
            2 retires (a gallery-caption reindeer fact and a one-bullet
            Trivia-section line, both G5, left un-tuned per campaign rule).
            Six-class review: clean (the 038/067 "remains unclear" echoes are
            inherent to uncertainty questions; the 090/025/054 fragments are
            made explicit by their questions; "Caped Baldy" (027) is the
            wiki's own term for Saitama in the MA arc). Gate re-confirmed on
            this cluster (no engine edits): canon-run 2026-08-22-0521 =
            8/16 + 235/237 + 78.5% + 18/20 (identical to baseline), pytest
985 passed. See STATUS row 34. Long-tail queue remaining: the rest
of the top-35 size ladder (Speed-o'-Sound Sonic, Gouketsu, King,
Isamu, Puri-Puri Prisoner, Suiryu, Characters aware of Saitama's
power).**
              **Long tail 2026-08-22: cluster 6 of the long tail,
              Speed-o'-Sound Sonic, done — 103/103 on the first and only
              scored run (2026-08-22-0919), zero triage, zero retires.**
              Fifteen-page cluster: the character page (S-Class ninja, 4
              infobox abilities, the Ninjatō primary weapon, voices Yūki
              Kaji / Erik Scott Kimerer, the `A Hero Nobody Knows` game
              field) + the `Battles`, `Relationships`, `Synopsis` and
              `Other Media` subpages + the ten battle pages of the wiki's
              own `Speed-o'-Sound Sonic Fights` category + `Sonic's
              Hideout` + `Sonic's One-Punch Song`. One new roster
              declaration in `series/opm/overrides.yaml` (per-request
              reload, no server restart, no .py changes): `Speed-o'-Sound
              Sonic's battles` (10 members from the category — the
              battles-in discovery path returns a 12-page superset, because
              `Blast vs. Empty Void (Retconned)` lists Sonic on its
              combatant1 side and `Puri-Puri Prisoner vs. Baquma` names him
              among the deployed monsters, the last-content-word over-match
              recurring; the set question is phrased "What are all the
              battles of..." so the declared roster claims it before the
              battles-in path, per the ENW / Overgrown Rover precedent).
              22 G1 battle-result facts exercised across the table's
              manga/extra-chapter/audiobook/webcomic sections (Sonic-
              perspective, plus 2 Saitama-mirror questions whose tied rows
              all resolve "Win") and 5 G2 relation facts (rival/enemy/
              student rows, both directions). All 103 golds verified
              against the stored chunks and the full batch live-probed
              before authoring; two probe outcomes shaped the batch (the
              hideout's webcomic-debut fact does not surface in the
              narrative bundle — dropped for the hideout's status/type/
              anime-debut facts — and the infobox `game` field stores the
              link target `A Hero Nobody Knows` rather than the piped
              display title, so the gold is the stored value). Webcomic-only
              canon kept with per-question scope notes on 8 questions.
              Six-class review: clean. Gate re-confirmed on this cluster
              (roster added): canon-run 2026-08-22-0921 = 8/16 + 235/237 +
              78.5% + 18/20 (identical to baseline), pytest 985 passed. See
STATUS row 35. Long-tail queue remaining: the rest of the
               top-35 size ladder (Gouketsu, King, Isamu, Puri-Puri
               Prisoner, Suiryu, Characters aware of Saitama's power).**
               **Long tail 2026-08-22: cluster 7 of the long tail,
               Gouketsu, done — 107/107 on the first and only scored run
               (2026-08-22-0939), zero triage, 5 retires (4 engine gaps +
               1 unchunked infobox field).**
               Three-page cluster: the character page (Dragon-level
               Mysterious Being, formerly the human first Super Fight
               Champion, deceased, Monster Association, 3 named abilities,
               manga Ch 66 / anime Ep 18, voices Kenji Nomura / Kellen
               Goff) + the two battle pages of the wiki's own `Gouketsu
               Fights` category (`Gouketsu vs. Bakuzan` Ch 74, `Suiryu vs.
               Gouketsu` Ch 72-73, both Ep 20) + cross-page facts from the
               `Bakuzan` and `Suiryu` pages. Two new roster declarations in
               `series/opm/overrides.yaml` (per-request reload, no .py
               changes, no server restart): `Gouketsu's battles` (2
               members from the category — the battles-in discovery path
               returns the same closed two, the three pages that name
               Gouketsu in previous/next navigation only not counting as
               combatant-field matches, so the declared set equals
               discovery and the set question stands exact, no superset)
               and `Gouketsu's aliases` (1 member "Original Super Fight
               Champion"; romaji/kanji out per G3). 9 G1 battle-result
               facts exercised (the Suiryu-perspective "Loss" and the
               Gouketsu-perspective "Win" for the same battle, the
               Gouketsu-page table rows for the off-screen Genos/Saitama
               fights and the Orochi flashback, the Sneck and Max row, and
               Bakuzan's own "Bakuzan is killed" row) and 3 G2 relation
               facts (Orochi rival, Three Crows mentor, Gouketsu-to-
               Orochi subordinate). All 112 candidate golds verified
               against the stored wikitext and the full batch live-probed
               before authoring (104/112 first pass; the 8 misses: the 4
               Previous/Next infobox questions the battles-in path
               intercepts — retired, 2 rephrased to dodge the narrative
               route, and 2 gold fixes — "Chapter 72, 73" split into the
               two per-chapter renderings, and the unchunked partners
               infobox field retired). Retires (5): the four sequential
               Previous/Next infobox questions (the battles-in roster path
               intercepts every phrasing naming the battle and returns the
               declared 2-member set; rephrasings probed and intercept the
               same way, left un-tuned per the campaign rule) and the
               infobox `partners` field (routes to the Characters roster,
               which returns only the page subject; the field is not
               carried as a fact or relation — the mentor-relation
               question covers the partnership). Six-class review: clean.
               Gate re-confirmed on this cluster (roster added): canon-run
               2026-08-22-0941 = 8/16 + 235/237 + 78.5% + 18/20 (identical
               to baseline), pytest 985 passed. See STATUS row 36.
               Long-tail queue remaining: the rest of the top-35 size
               ladder (King, Isamu, Puri-Puri Prisoner, Suiryu,
               Characters aware of Saitama's power).**
               **Long tail 2026-08-22: cluster 8 of the long tail,
               King, done — 112/112 on the final scored run
               (2026-08-22-1011; first scored run 2026-08-22-1005 was
               109/112, the three misses all auto-router narrative
               hijacks re-asked to key the subject to the character,
               2026-08-22-1007 = 112/112), 4 pre-retires (engine gaps).**
               Cluster: the character page (S-Class Rank 5 (Currently) / 7
               (Formerly) / 6 (Giant Meteor Arc), Human, 29, 187 cm, King's
               Apartment (M-City), alias The Strongest Man on Earth, 4
               infobox abilities) + the `Battles`, `Synopsis`, `Other Media`
               and `Relationships` subpages + the `King Arc` + the `King's
               Apartment` and `King's Weekend-like Weekday` pages + the
               three battle pages of the wiki's own `King Fights` category.
               Two new roster declarations in `series/opm/overrides.yaml`
               (per-request reload, no .py changes, no server restart):
               `King's battles` (3 members from the category — the battles-in
               discovery path over-matches the last content word `king` to
               the wiki's many monster-King battle pages, so the set
               question is phrased "What are all the battles of..." which
               the declared roster claims before the battles-in path, per the
               ENW / Overgrown Rover / Sonic / Gouketsu precedent) and
               `King's aliases` (1 member "The Strongest Man on Earth"; the
               `alias =` infobox field is a shape discovery does not read;
               romaji/kanji out per G3). 12 G1 battle-result facts and 7 G2
               relation facts exercised. All 112 golds verified against the
               stored chunks and the full batch live-probed before scoring
               (111/112 first pass; the one miss — the MA-executives
               battle-result question keyed to the 9-member `Monster
               Association Executives` roster instead of King — re-asked as
               "the battle between King and the Monster Association
               executives" which keys to King). Pre-retires (4, engine gaps,
               left un-tuned per the campaign rule): the `Witness` Omake
               entry on `King/Other Media` (the game King picks up, and who
               King is mistaken for — un-chunked) and the Saitama-Introduction-Arc
               "mistaken for" beat plus the Neo Heroes Uprising pushups beat
               on `King/Synopsis` (un-chunked arc beats). Six-class review:
               direction fix (079 "S-Class heroes" -> "Dragon-level monsters
               and S-Class heroes" — Black Sperm is a Dragon-level monster,
               not an S-Class hero) and two grammar polishes (030/031),
               re-probed and re-run (2026-08-22-1011). Gate re-confirmed on
               this cluster (roster added): canon-run 2026-08-22-1000 =
               8/16 + 235/237 + 78.5% + 18/20 (identical to baseline),
               pytest 985 passed. See STATUS row 37.
Long-tail queue remaining: the rest of the top-35 size
                ladder (Isamu, Puri-Puri Prisoner, Suiryu,
                Characters aware of Saitama's power).**
                **Long tail 2026-08-22: cluster 9 of the long tail,
                Isamu, done -- 116/116 on the final scored run
                (2026-08-22-1046; first scored run 2026-08-22-1037 was
                107/116, all 9 misses triaged against the stored bundles:
                3 routing rephrasings + 7 gold-string fixes, zero engine
                gaps, zero retires).**
                Cluster: the character page (S-Class Rank 5 (Formerly),
                Human, 10, 135 cm, 35 kg, Y-City, alias Child Emperor /
                Wild Emperor, 4 infobox abilities, game A Hero Nobody
                Knows) + the `Battles`, `Relationships`, `Synopsis` and
                `Other Media` subpages + the eight battle pages of the
                wiki's own `Child Emperor Fights` category + cross-page
                facts from the `Underdog Man`, `Brave Giant` and `G5`
                pages. Two new roster declarations in
                `series/opm/overrides.yaml` (per-request reload, no .py
                changes, no server restart): `Isamu's battles` (8 members
                from the category -- the set question is phrased "What
                are all the battles of..." which the declared roster
                claims before the battles-in path, per the ENW /
                Overgrown Rover / Sonic / Gouketsu / King precedent) and
                `Isamu's aliases` (2 members: Child Emperor, Wild
                Emperor; the `alias =` infobox field is a shape discovery
                does not read; romaji, kanji and the Viz translation out
                per G3). 15 G1 battle-result facts and 8 G2 relation
                facts exercised. All 116 golds verified against the
                stored chunks and the full batch live-probed before
                scoring. The 9 first-run misses: 3 routing rephrasings
                (061 "In which video game" hijacked to the series-level
                narrative bundle -- re-asked "What game did Child Emperor
                appear in as a playable character", which routes qa to
                the Isamu page and surfaces the stored `game` value `A
                Hero Nobody Knows`; 069 re-asked keyed to the Underdog
                Man page as "What does Underdog Man No. 22 do to
                Eyesight", gold "grabs Eyesight and self destructs"; 114
                "Whom" -> "Who" dodges the narrative route) and 7
                gold-string fixes (033 the next-battle field stores
                "Round 2"; 055 the Height template renders to an empty
                (), so "135 cm"; 070 Cerberus "a fusion of three
                Underdog Mans" (G5 page); 074 "a powerful robot created
                by Child Emperor"; 077 the Round 2 battle page's
                "invisible wall with film" description; 112 the wikilink
                [[Okame-Chan|unfinished invention]] renders "unfinished
                invention", not "Okame-Chan"; 114 the contiguous stored
                phrase "seems to idolize King"). Webcomic-only canon
                kept with per-question scope notes on 2 questions
                (opm-pg-isamu-093, opm-pg-isamu-103). Gate re-confirmed
                on this cluster (roster added): canon-run 2026-08-22-1048
                = 8/16 + 235/237 + 78.5% + 18/20 (identical to
                baseline), pytest 985 passed. See STATUS row 38.
                Long-tail queue remaining: the rest of the top-35 size
                ladder (Puri-Puri Prisoner, Suiryu,
                Characters aware of Saitama's power).**
                **Long tail 2026-08-22: cluster 10 of the long tail,
                Puri-Puri Prisoner, done -- 122/122 on the scored run
                (2026-08-22-1113; zero triage, zero retires).**
                Cluster: the character page (S-Class Rank 13 (Currently)
                / 17 (Sea Monster - Psychic Sisters) / 16 (Giant Meteor),
                Human, 33, 220 cm, Smelly Lid Prison (J-City), partner
                Unnamed Boyfriend, game A Hero Nobody Knows, voices
                Masaya Onosaka / Ray Chase) + the `Battles`,
                `Relationships`, `Synopsis` and `Other Media` subpages +
                the seven battle pages of the wiki's own `Puri-Puri
                Prisoner Fights` category that concern him (Deep Sea
                King, the Melzargard group fight, Free Hugger, Baquma,
                Prisoners of Smelly Lid Prison, Nyan, and the
                webcomic-only `Puri-Puri Prisoner vs. Raiden`
                Missinginfo skeleton) + the `Garou vs. Puri-Puri
                Prisoner` page (the Garou cluster's, covered here by its
                result and infobox facts). One new roster declaration in
                `series/opm/overrides.yaml` (per-request reload, no .py
                changes, no server restart): `Puri-Puri Prisoner's
                battles` (10 members from the category -- the battles-in
                discovery path returns an eleven-page superset because
                `Puri-Puri Prisoner vs. Raiden`, webcomic exclusive and
                carrying no category tag, names him in combatant1; the
                set question is phrased "What are all the battles of..."
                which the declared roster claims before the battles-in
                path, per the ENW / Overgrown Rover / Sonic / Gouketsu /
                King / Isamu precedent). No alias roster: the live and
                stored character page carry no `alias =` infobox field.
                15 G1 battle-result facts (Major Battles rows
                Puri-Puri-Prisoner-perspective, the Omakes Urn Eel
                "Win", the three webcomic-scope rows with notes, the two
                Heroes-team-fight questions keyed to the subject, and
                the two Garou-mirror questions reading `Garou/Battles`)
                and 5 G2 relation facts (Darkshine comrades + the
                avenge-Garou vow, Saitama stable relationship, the
                inmates' control and sleep-assassination rows)
                exercised. All 122 golds verified against the stored
                chunks and the full batch live-probed before authoring
                (120/122 first pass; the 2 misses: "What did Puri-Puri
                Prisoner take as a child" rephrased to "What lessons did
                Puri-Puri Prisoner take as a child", and the Christmas
                question "What are ... plans for Christmas" stolen by
                the roster route, re-asked "What does Puri-Puri Prisoner
                plan to do for Christmas..."). Webcomic-only canon kept
                with per-question scope notes on 10 questions (the three
                webcomic battle-result rows, the four Raiden-skeleton
                facts, and three webcomic-synopsis beats). Gate
                re-confirmed on this cluster (roster added): canon-run
                2026-08-22-1115 = 8/16 + 235/237 + 78.5% + 18/20
                (identical to baseline), pytest 985 passed. See STATUS
                row 39.
                Long-tail queue remaining: the rest of the top-35 size
                ladder (Suiryu, Characters aware of Saitama's power).**
                **Long tail 2026-08-22: cluster 11 of the long tail,
                Suiryu, done -- 121/121 on the scored run
                (2026-08-22-1247; zero triage, zero retires), re-run
                121/121 (2026-08-22-1251) after the six-class review
                fix.** Cluster: the character page (occupation Neo Hero,
                race Human, status Alive, fighting style Void Fist,
                family Suiko (younger sister) / Suicho (grandfather),
                voices Masaya Matsukaze / Alan Lee, game A Hero Nobody
                Knows, manga Ch 53 (first mentioned) / Ch 60, webcomic
                Ch 124, anime Ep 16) + the `Battles`, `Synopsis` and
                `Other Media` subpages + the nine battle pages of the
                wiki's own `Suiryu Fights` category: the seven that name
                him as a combatant (Lightning Max, Sneck, Saitama, the
                Choze/Benpatsu/Volten/Hamukichi group, Gouketsu, the
                Three Crows team fight, and Garou) + `Puri-Puri
                Prisoner vs. Raiden` (the Puri-Puri cluster's page,
                covered here only in the roster and its next-battle
                fact) + the OVA-original `Dragon vs. Wolf (Video Game
                Tournament)`. One new roster declaration in
                `series/opm/overrides.yaml` (per-request reload, no .py
                changes, no server restart): `Suiryu's battles` (9
                members from the category -- eight of the nine name him
                in a combatant field, `Puri-Puri Prisoner vs. Raiden`
                names him in none because he leads the Neo Heroes
                uprising the wiki tags for him; the set question is
                phrased "What are all the battles of..." so the
                declared roster claims it before the battles-in path,
                per the ENW / Overgrown Rover / Sonic / Gouketsu / King
                / Isamu / Puri-Puri Prisoner precedent). 16 G1
                battle-result facts (the twelve Suiryu-perspective Major
                Battles rows incl. the Omakes/OVAs and the two
                webcomic-scope rows, plus the four mirror questions
                reading `Garou/Battles`, `Saitama/Battles` and
                `Sneck/Battles`) and 4 G2 relation facts (Garou rival;
                Suiko family; Suicho family + student; Saitama ally +
                rival, both directions, from the extracted rows in
                facts.db) exercised. All 121 golds verified against the
                stored chunks and the non-trivial questions live-probed
                before scoring (115/121 first pass; the 6 misses all
                phrasings: #38 re-asked singular "What manga chapter
                covers Saitama vs. Suiryu" with the `Chapter 70, 71`
                gold split into the two items the bundle carries
                separately, #103 re-anchored to dodge the Battle-Suit
                subject hijack, #108/110/113/124 re-asked to escape
                the roster/narrative routes -- each recovery probed
                live before committing). Six-class review: one in-place
                fix -- #80 the abilities gold completed with the
                co-listed `Master Martial Artist` (class 3, both items
                verified present in the bundle). Gate re-confirmed on
                this cluster (roster added): canon-run 2026-08-22-1250
                = 8/16 + 235/237 + 78.5% + 18/20 (identical to
                baseline), pytest 985 passed. See STATUS row 40.
                Long-tail queue remaining: the rest of the top-35 size
                ladder (Characters aware of Saitama's power).**
                 **Long tail 2026-08-22: cluster 12 of the long tail,
                 Characters aware of Saitama's power, done -- 95/95 on the
                 final scored run (2026-08-22-1314; first scored run
                 2026-08-22-1312 was 92/95, the 3 misses all routing/
                 phrasing misroutes to narrative rephrased in place -- the
                 lead fact re-asked page-keyed as "What does the page on
                 characters aware of Saitama's power say about Saitama's
                 power being unacknowledged?", and the Black Sperm and Nyan
                 second facts re-asked as wh-lookups naming the character --
                 zero engine gaps, zero retires).**
                 Cluster: the wiki's own list page
                 `characters_aware_of_saitamas_power` (the 12th-largest
                 page in the top-35 ladder), a LIST whose membership is its
                 own listing (37 main rows under `Extensive awareness` + 7
                 spoiler rows under `Partial awareness` = 44), plus the
                 lead and one subsection per listed character. One new
                 roster declaration in `series/opm/overrides.yaml`
                 (per-request reload, no .py changes, no server restart):
                 `Characters aware of Saitama's power` (44 members
                 transcribed verbatim from the page's own listing -- roster
                 discovery cannot read a list page, so the set question
                 auto-routed to the 8-member `Characters`-category superset
                 with the intruder `Custom Hero`; the set question is
                 phrased "Who are all the characters aware of Saitama's
                 power..." which the declared roster claims before
                 discovery). The set carries `subject: Saitama`: a declared
                 set that names its subject runs *instead of* the
                 character-kit path (without it, "power" (a kind word) +
                 "Saitama" (a character) would answer with Saitama's 28
                 techniques/traits/transformations and never reach this
                 roster; it also keeps the set's own words out of the
                 general set vocabulary). 5 affiliation/status subset
                 presence-facts (Saitama Group, Deceased, Dark Matter
                 Thieves, Neo Heroes, Ninja Village) ride the same declared
                 roster, alongside the lead's "mostly unacknowledged" and
                 "few characters aware" claims and the per-listed-character
                 subsection facts (character-keyed "How/When did X become
                 aware of Saitama's power" phrasings). All 95 golds are
                 verbatim contiguous substrings of the stored page
                 wikitext; the unchunked lead/cquote/list-table regions are
                 not used as golds (the cquote claim is carried by the
                 Jinzuren paraphrase). Six-class review: clean, no retires.
                 Gate re-confirmed on this cluster (roster added): canon-run
                 2026-08-22-1316 = 8/16 + 235/237 + 78.5% + 18/20
                 (identical to baseline), pytest 985 passed. See STATUS row
                 41.
                 **Long-tail queue remaining: none -- the round-2 long tail
                 (top-35 by corpus size) is complete.**
- [x] 200 fresh questions: dedup script run, first pass ≥ 95%, triaged to 100%
       — **2026-08-22.** `questions/_opm_page_round2_fresh.json` written: 200
       questions across 68 pages no earlier OPM batch covered (48 mid-tier
       character pages plus arc/event/episode/org/location/meta pages; 1484 of
       the 1571 OPM wikitext files had zero question coverage, and the fresh
       bank was drawn from the uncovered pages only). Dedup script run over the
       finished sheet: 3216 active + 279 retired OPM question strings, NFKD-
       fold, exact + contiguous-substring both directions -- 0 collisions, 5
       near-duplicate flags all confirmed false-positives. First scored run
       2026-08-22-1405 = 187/200 (93.5%): all four battles-in sets over-
       matched the wiki-wide 133-page generic `Fights` superset (each
       character's own closed `<X> Fights` category holds the true 1/2/2/2
       set), so four rosters declared in `series/opm/overrides.yaml` from the
       wiki's own categories -- `Genji's battles` (1, `Lightning Genji
       Fights`, the Isamu / Child Emperor alias-bridge), `Carnage Kabuto's
       battles` (2), `Royal Ripper's battles` (2), `Hammerhead's battles`
       (2) -- per-request reload, no `.py` or engine changes, no server
       restart (ENW / Overgrown Rover / Sonic / Gouketsu / King / Isamu /
       Puri-Puri Prisoner / Suiryu precedent). The 9 remaining failures are
       routing/retrieval engine gaps, retired in place with reasons in the
       batch's `retired` field: 2 debut-phrasings that do not extract their
       subject (Do-S manga ch 59, Chain'n'toad webcomic ch 95), 2 minor-
       character English-VA infobox facts not surfaced (Lily / Erika
       Harlacher, Gums / Ray Chase), 2 Major Battles `Result` cells not
       chunked (Mosquito Girl vs Genos "Interrupted and defeated by
       Saitama", Pesky Clown vs Sweet Mask "Loss"), 2 Monster Raid Arc
       infobox range facts mis-routed to the `TV Junkyard Monster` roster
       (chapters 52-65, episodes 16-18), and the Organization "primary
       combat robots" prose fact routed to the `Robots` roster (answer
       `The Machine Gods`) -- all left un-tuned per the campaign rule. Final
       runs 2026-08-22-1417, 2026-08-22-1421 and 2026-08-22-1425 (on the
       final bank file) = **191/191** (4 sets exact,
       187 facts present; 191 active / 9 retired; the active bank covers 67
       of the 68 authored pages -- the Monster Raid Arc page's two questions
       are both retired). Six-class review over the whole bank: clean
       (webcomic-only canon kept with per-question scope notes; the four set
       questions' stale "set candidate" notes updated to the declared-roster
       status).
 - [x] Final gates: canon-run 8/16 + 235/237 + 78.5% + 18/20, pytest 985, eval jjk 24/24
       — **2026-08-22.** `canon-run --series opm` 2026-08-22-1415 = 8/16 +
       235/237 + 78.5% + 18/20 (identical to baseline) and `pytest tests/ -q`
       = 985 passed, re-confirmed after the four fresh-bank roster
       declarations. `eval --series jjk` 24/24 not re-run: gate 3 applies
       only after a shared `.py` change, and the round-2 engine fixes
       (G1/G2/G5/G6) were already gated on 24/24 at ship; the phase-3 work
       touched `series/opm/overrides.yaml` only (per-request reload), which
       the gate pair above covers.
 - [x] STATUS.md updated with round-2 rows + section; this file's checklist closed
       — **2026-08-22.** STATUS row 42 (fresh bank) + queue line 42 + the
       "Phase 3: fresh bank complete" paragraph appended to the round-2
       section. Round-2 plan closed: G1/G2/G5/G6 shipped and gated,
       clusters 16-20 + the top-35 long tail at a clean sweep, and the 200-
       question fresh bank triaged to 191/191.