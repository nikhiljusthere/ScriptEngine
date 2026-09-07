# COUNCIL — Phase 5 closure: does not extracting the 5 prose dimensions lose data?

Date 2026-09-06. User directive (pause at checkpoint `2ea235e`): investigate
whether closing Phase 5 — *not* extracting Personality / Appearance / Overview /
Trivia / History as structured fact fields — loses any data given the JJK corpus
end goal (writing video scripts). Standing rule: the writer consumes a *cited
bundle* (beats + infobox facts), not raw DB rows. The open question: is
"not extracting" safe, and does "closed" (per Phase 5's own gate) also mean
"actually served"?

Method: 5 advisors (independent, parallel) → anonymized A–E → 5 peer reviewers
(independent, parallel, each weighted to a failure mode) → this chairman
synthesis. Every load-bearing claim re-verified against `series/jjk/facts.db`,
the raw crawl (`series/jjk/wikitext/*.json`), and the as-run span-recall (100%)
before recording.

Advisor roles (anonymized): **A** = First Principles, **B** = Outsider,
**C** = Executor, **D** = Contrarian, **E** = Expansionist.

## The step under review

Phase 5's own gate closed it: the 5 prose sections are kept as *prose* (verbatim,
in the crawl) and served as cited beats through the retrieval index; a structured
"trait" field was judged lossy (it drops nuance and severs the chapter/episode
citation the writing contract requires). This council pressure-tests whether that
closure is *safe* — i.e. whether "no data loss" holds, and whether "closed" is
actually *earned* (retrieval serves all of it).

**Investigation finding (no data loss):** the data *is* the wiki's verbatim
prose, preserved twice over — in the raw crawl and chunked into the retrieval
index (span-recall 100%). Per-dimension coverage on the 218 character pages:

| dimension  | pages with section | words  |
|------------|-------------------|--------|
| Personality| 138 | 42,518 |
| Appearance | 145 | 14,178 |
| Overview   | 41  | 16,724 |
| Trivia     | 121 | 15,326 |
| History    | 100 | 11,577 |
| (lead/intro)| 218 | 6,132  |
| **total**  | —   | **~106,000** |

545 (dimension,page) pairs exist (138+145+41+121+100). Not extracting loses
**no data**: fields are a lossy *derivative* of the preserved prose (and drop the
citation), so closing destroys zero data. The one narrow *capability* at risk —
cross-character trait aggregation ("which characters are kind?") — is not the
end goal and is cheaply addable (a TF-IDF index on the prose), not a 27B batch.

## Where the Council agrees

- **No data loss on retention.** Unanimous. Prose preserved + 100% span-recall;
  fields are lossy copies.
- **"Served" is un-proven, not "lost."** The evidence is E1–E4 = a 4/545
  personality-only sample wearing the confidence of a 545/545 claim; the other 4
  dimensions have *no* oracle items. Span-recall proves a line is *chunked*, not
  that a question *surfaces* the right one.
- **The decisive move is cheap and retrieval-only:** a ~545-question
  character-scoped relevance gate (one question per existing pair; top beat must
  be that character's own section with a valid chapter/episode citation; ~30 min
  GPU). Pass → close; fail → fix retrieval (scope-word misroute / cross-page
  confusion / chunker), never 27B. Every reviewer's "strongest response."
- **Closing is a reversible deferral, not a debt.** Fields can be re-derived from
  the preserved prose; the prose can never be recovered from fields.

## Where the Council clashes

- **Extract or not?** A/E: no — prose-direct is better; fields collide with the
  citation contract and burn the scarce GPU (the 27B batch is what caused the
  508/524 OOM). D: the writer loses an inventory/checkable-claim capability and
  moves silent failure onto the draft. They disagree only about *capability*
  (enumeration/roster), not data.
- **History time-ordering a real gap?** D/B: relevance prose mis-orders
  chronology. Counter (D's own blind spot): the engine already has a **narrative
  (chronological) retrieval path** that answers "what happened to X before
  Shibuya" — the concern is likely already covered.

## Blind spots the Council caught

- **Nobody tested the actual customer — the draft.** A retrieval gate proves
  reachability, not grounding; the writer model fabricates a plausible trait
  absent from the bundle, and tag-verification won't catch it. → A/B ~10 drafts
  with/without the dimensions + a claim→beat grounding check.
- **Demand is unmeasured.** If demand ≈ 0, close outright; if real, gate only the
  used dimensions.
- **It's 5 dimensions, not 1 bucket.** Uneven coverage (Overview 41/218; 80 pages
  have no Personality). Closure should be *per-dimension*; the gate passes
  vacuously on missing sections.
- **Absence ≠ miss.** Return an explicit "no section found" signal instead of a
  silent miss the writer fills by inference (which the rules forbid).
- **Arithmetic:** "1090 cells" should be ~545 (only dimensions that exist per
  page).

## Verdict

**"No data loss" is TRUE — but "closed" is not yet EARNED.** The data side is
settled (prose preserved, 100% span-recall, fields are lossy derivatives). What's
missing is evidence that retrieval actually *serves* all of it. Keep Phase 5
**closed on the data** (no 27B extraction owed; reversible deferral). Don't call
it *safe* until the three cheap, retrieval-only steps below pass.

## Top-priority tasks — run BEFORE continuing from checkpoint `2ea235e`

These four are the gate to clearing before resuming the phase plan (Phase 3,
etc.). Retrieval-only; **no 27B extraction, ever, for these.**

1. **Demand audit.** Grep the finished scripts + the gold question bank for
   Personality/Appearance/Trivia/History/Overview usage. If demand ≈ 0 → close
   outright (skip the gate for unused dimensions); if real → gate only the used
   dimensions.
2. **545-question relevance gate** on the actually-used dimensions. One question
   per existing (dimension,character) pair; top beat must be that character's own
   section with a valid chapter/episode citation; retrieval-only (~30 min GPU).
   Pass → close with the rate recorded in `COVERAGE.md`; fail → fix retrieval
   (scope-word misroute / cross-page confusion / chunker), still no 27B.
3. **Explicit "no section found" signal.** Make retrieval return an explicit
   absence signal (not a silent miss the writer fills by inference). This
   resolves absence-vs-miss without any extraction.
4. **Cross-character facet queries → separate, optional TF-IDF trait index** on
   top of the preserved prose. Not a 27B extraction, and not a reason to reopen
   Phase 5.

## Demand audit results (task 1) — 2026-09-06

**Sources:** 44 scripts in `sample scripts/` (the genre library the writer
produces) + 2 finished engine outputs in `scripts output/`; the two standing
question sources `scriptengine/eval/gold_jjk.json` (24 Q) and
`plan/ORACLE_v1.yaml` (18 items).

**What the standing question banks cover:** `gold_jjk.json` = 24 questions across
fact / alias / semantic(technique) / lexical / multihop / narrative / roster /
sourcing. **Zero target Personality, Appearance, Overview, Trivia, or History.**
`ORACLE_v1.yaml` = 18 items; **only E1–E4 (Personality)** among the five — no
Appearance/Overview/Trivia/History items. So the standing gate currently protects
*none* of the five dimensions.

**What the genre library consumes (word-level, 44 scripts):**

| dimension   | matches | reading |
|-------------|---------|---------|
| Personality | 445     | HIGH — motive/psychology/behavior is the spine of "Most Evil", "Overpowered Character", "What It's Like To Be Every…" |
| History     | 415     | HIGH — "Saitama's Life Story", "Every S-Class Hero Backstory", "Entire Life of X"; every character profile carries a chronology |
| Appearance  | 266     | MODERATE — physical description appears throughout, less load-bearing |
| Overview    | 30      | MOD-LOW — the "X is a… / known for" framing |
| Trivia      | 18      | LOW — no trivia-driven genre; scattered "interestingly/notably" |

**Confirmed by reading two diagnostic scripts:**
- `SAITAMA'S LIFE STORY EXPLAINED.md` is a pure **History** genre (headed
  "**HISTORY**"; childhood → training → hero chronology) and is **sourced to
  chapters/episodes** — the writer consumes *cited prose*, not a pre-extracted field.
- `Most Evil Characters in Anime History.md` is roster+aggregation; each entry is
  a dense **Personality + History + Appearance** profile, again **chapter-cited**.

**Verdict per dimension (demand):**

| dimension   | demand    | gate? |
|-------------|-----------|-------|
| Personality | HIGH      | YES — in the 545 gate |
| History     | HIGH      | YES — in the 545 gate (time-ordering rides the narrative/chronological path) |
| Appearance  | MODERATE  | YES — in the 545 gate |
| Overview    | MOD-LOW   | YES (cheap; only 41/218 pages have it) |
| Trivia      | LOW       | include, lowest weight; not a driving genre |

**Consequences:**
1. Phase 5 is **not** "no demand" — four of five dimensions (Personality, History,
   Appearance, Overview) are genuinely consumed by the script genres; Trivia is
   lightly used. The council's "close outright if demand ≈ 0" branch is **not**
   taken; the **545-question relevance gate** (task 2) is required for the four
   high/moderate dimensions (Trivia carried at low weight).
2. Because the standing `gold_jjk.json` covers **none** of the five, the 545 gate
   should also **feed representative items back into the gold bank** so the
   standing regression gate protects the dimensions scripts actually use.
3. Demand is for **cited prose** (chapter/episode-sourced), which is exactly what
   retrieval serves — reinforcing "no extraction, retrieval-only."

## Verified-claims ledger (checked this run)

- [x] 218 character pages; per-dimension page/word counts (table above) —
  `series/jjk/wikitext/*.json`.
- [x] 545 (dimension,page) pairs exist (138+145+41+121+100).
- [x] span-recall jjk = 100% (every line sits whole in some chunk) — prose is
  preserved and chunked.
- [x] 27B extraction (Qwen) is build-time; reranker/embedder is query-time
  retrieval only — `scriptengine/llm/client.py`, `ingest/abilities.py:406`,
  `ingest/classify.py:228`, `cli.py:640`.
- [x] The 27B batch previously OOM-crashed at 508/524 pages when co-located with
  the :8000 reranker (infrastructure hard rule) — extraction is the scarce,
  load-sustaining path.
- [x] Engine already has a narrative (chronological) + roster (enumeration)
  retrieval path — `retrieve/` (CLAUDE.md layout).
- [x] E1–E4 are 4 personality oracle items; the other 4 dimensions have no oracle
  items (span-recall ≠ relevance).

## Evidence pins

- Investigation: `series/jjk/wikitext/*.json` (218 character pages),
  `series/jjk/facts.db`.
- Prior gate: `reports/comprehension/COUNCIL_1.md` (Phase 1C; E1–E4 pass),
  `plan/flow.md:231-243` (Phase 5 gate).
- Oracle: `plan/ORACLE_v1.yaml`.
- Span-recall: `reports/span-recall/` (jjk 100%).