# Release R6 — numbering hygiene + entity-anchored recall floor

Three parts: (A) a documentation/numbering pass, (B) the entity-anchored recall
floor (designed and gated), and (C) a scoped paraphrase-recall measurement
(first 10% slice). Every number below is a live run or a store measurement, not
an estimate.

## Part A — numbering hygiene

### G-number corrections (old wrong number -> new number)

The campaign's open-gap register had drifted: G19 had been carried unnumbered
inside a character row, and G20 (the discourse-opener gap found while verifying
the floor) was new. Corrections made in `HANDOFF_PROSE_PASS.md`:

| gap | before R6 | after R6 |
|---|---|---|
| G19 | unnumbered, folded into the Tsumiki character row ("the 2 active kanji-meaning Qs") | formally opened **and closed** in R6; its own entry with the closure mechanism named |
| G20 | did not exist | opened, **FIXED + gated** in R6 (discourse-opener: once-fronted clause) |

The tail block's open-gap list shrank from **14** documented-opens to **11**
(Kechizu `036/038`, Tsumiki `129/130`, and Toge `051` closed by the floor +
G20 in this release).

### Handoff tail-summary fix

The tail block now states, per gap, which R6 mechanism closed it (floor, G20,
or gold re-verbatim) and the re-run artifact, so a resuming session does not
re-open a closed gap.

## Part B — the entity-anchored recall floor (as implemented)

**Idea.** A resolved-subject qa question should be able to answer from the
subject page's *own* passages even when BM25 ranks the right bullet below the
beam. The floor pays for the subject page's level-2 passages first, in reading
order, before the ranked beam fills the rest of the budget.

**Files / lines.**
- `scriptengine/stores/facts.py:1149` — `FactStore.passages_for_subject(subject)`
  returns the page's own level-2 passages (reading order, verbatim).
- `scriptengine/api/context.py:324` — `_qa_context` is the qa-mode builder;
  at `context.py:364` it walks `passages_for_subject(subject)` first and pays
  those passages before the ranked beam.
- `scriptengine/retrieve/router.py` — **G20 fix**: `once` joins
  `_LEADING_DISCOURSE` (the G2b/G8a-style marker family) so a
  once-fronted mechanism question ("Once X enters a target … what happens?")
  is read as interrogative and claimed by rule 3 (qa) instead of falling to
  the narrative default. The `_WH_ANY` guard keeps a plain statement that
  merely opens with "once" a statement. Regression:
  `tests/test_router.py::TestG20OnceFrontedMechanism`.

**What it fixes.** The G5/G11/G13/G14 family (the subject page's own Trivia /
technique bullets ranking below the beam for a generic phrasing) — most visibly
the kanji-meaning class (G19): the bullet is the only home of the meaning, and
a generic "what does the kanji in X's surname mean?" query has low keyword
overlap with it, so BM25 never surfaces it. The floor serves the bullet
regardless of ranking. The match side still needed the golds re-verbatim over
the stored bullets (kanji + romaji inline), because the plain-meaning spans
were not verbatim substrings and could never word-boundary-match.

### Before / after page-run scores (known G5/G11/G13/G14-family pages)

| page | family | before | after (R6) | artifact |
|---|---|---|---|---|
| Kechizu | G20 once-fronted (`036`) + G19 readings (`038`) | 37/39 | **39/39** | before `jjk-kechizu-2026-08-31-2330`; after `jjk-kechizu-2026-08-31-2342` |
| Tsumiki Fushiguro | G19 kanji-meaning (`129/130`) | 128/130 | **130/130** | before `jjk-tsumiki_fushiguro-2026-08-31-1030`; after `jjk-tsumiki_fushiguro-2026-08-31-2343` |
| Toge Inumaki | G11/G13 outcome-sentence (`051`) | 85/86 | **86/86** | before `jjk-toge_inumaki-2026-08-27-0101`; after `jjk-toge_inumaki-2026-08-31-2345` |

### Three gate results (verbatim)

| gate | result |
|---|---|
| `pytest tests/ -q` | **1086 passed** |
| `eval --series jjk` | **24/24** |
| `canon-run --series opm` | **8/16 exact, 235/237 (99.2%), precision 78.5%**, confident-and-wrong 0 |

### Production-budget token fit (small vs large page)

Measured with `r6_floor_fit.py` (store walk + live `build_context`), qa mode,
`top_k=50`:

| page (level-2 passages) | all-paid cost | floor @6000 | floor @60000 | live @6000 (beats / from-subject / truncated / tokens_used) |
|---|---:|---|---|---|
| Kaito Yuki (5) | 575 tok | 5/5 | 5/5 | 25 / 5 / True / 5832 |
| Ko-Guy (12) | 1396 tok | 12/12 | 12/12 | 43 / 12 / True / 5939 |

**Recommendation.** At the production 6000-token budget the floor is cheap
enough to pay for the whole subject page on both a small page (575 tok) and a
large one (1396 tok), and it is the *first* thing paid, so the subject's own
prose is guaranteed in the bundle. Make the entity-anchored floor the default
qa behavior (it already is, for resolved subjects); no production default
change is required beyond keeping `_qa_context` on the floor path. The 60000
campaign budget changes nothing (both pages still pay in full).

## Part C — first paraphrase-recall slice (10% rotating)

### Batch (corrected)

Slice 0 of 10 (`sha1(id) % 10 == 0`): **2,321 source questions**, each emitted
in 3 forms (reworded / yes-no / contextual) by `Qwen3-VL-4B-Instruct`
(text-only), single-fallback temps 0.7/0.85/1.0. The slice carried **165 source
IDs that appear in more than one slice file**; dedup removed them
(`2,321 -> 2,156` distinct), keeping one canonical row per `(id, slug, seq)`.
**24 of those 165 duplicates carried differing content across their
occurrences** (a regeneration collision) — flagged in
`r6_duplicate_slice_report.json` for review, dedup kept the canonical one. 2,155
sources generated cleanly (3 forms each = 6,465 rows); one source
(`jjk-pg-yuji_itadori-286`) failed its first generation and was filled
separately (3 rows) → **6,468-row batch** (was mis-reported as 6,963 pre-dedup).

### Result (page-run, PID 30264, wall 5563.5 s)

**5,970 / 6,468 passed (92.3%); 498 failed (7.7%).** Failure routed-mode mix:
narrative 312 / qa 120 / roster 66. Full per-question rows:
`jjk-paraphrase_r6-2026-09-01-0300/REPORT.md` + `scores.json`.

### Root-cause table (all 498, decision-ready)

Each failure's missing answer phrase was checked against (a) the cited source
page's prose, (b) every page in the 988-page corpus, and (c) the structured
layer (`facts.db`). Each question lands in exactly one bucket:

| bucket | n | narr / qa / roster | what it is | fix owner |
|---|---:|---|---|---|
| **RETRIEVAL** — answer *is* on the cited page's prose; the served bundle didn't surface it | 162 | 142 / 7 / 13 | 142 are static-lookup / trivia / appearance / power / date / "which chapter" questions mis-routed to **narrative** mode (the 77-beat chronology omits the static section that holds the answer) | router mode-misroute (new **G22**); small beam/floor tail |
| **CROSS-PAGE** — answer is prose on a *sibling* page (arc / synopsis / battle) | 155 | 85 / 21 / 49 | bundle scoped to the cited page; the fact lives on a sibling (dates 77, arcs, battle-results-in-prose, schools, locations) | router subject-focus (G3-family); a gold-cites-wrong-page subset |
| **NOT-IN-CORPUS** — answer nowhere in any page's prose | 181 | 85 / 92 / 4 | **100% structured-only** (174 exact + 7 substring matches in `facts.db`: battle-outcome sentences, episode ranges, chapter/issue numbers); **0 genuinely absent** | batch/scorer instrument mismatch — verify structured answers via the canon/structured path, not the prose page-run |

**Headline.** ~2/3 of the 498 (336 = 155 cross-page + 181 structured-only) are
*instrument/scoping* artifacts: a prose-containment page-run is the wrong tool
to verify a fact that lives in the structured layer or on a sibling page. Only
the 162 RETRIEVAL cases are true "answer on the cited page but the bundle
missed it," and 142 of those are a single router mode-misroute.

### Decisions (no engine code changed this pass)

- **G22 (new, OPEN).** The router sends static-lookup / trivia / appearance /
  power / date / "which chapter" questions to **narrative** mode; the 77-beat
  chronology cannot carry the static section, so the answer is missed. Evidence:
  142/162 RETRIEVAL failures are narrative-routed. Fix = a qa-claim rule for
  static-attribute questions (the `_LEADING_DISCOURSE` marker family G20 joined
  already half-serves it); needs its own focused pass + regression. Not touched
  in R6 — a router change would invalidate the current 6,468 measurement.
- **Structured-answer instrument mismatch (181).** The slice samples the full
  live fact pool, which includes structured facts (battle outcomes, dates,
  chapters). The prose page-run scorer (word-boundary containment in the served
  bundle) structurally cannot match a value that exists only in `facts.db`.
  Defer to R7: the generator filters structured-answer questions out of the
  prose batch, and/or the scorer's haystack also accepts a match in the served
  bundle's `facts` field when the routed subject carries it.
- **Cross-page scoping (155).** Recorded as the router subject-focus gap
  (G3-family) with a gold-citation-error subset to triage in R7.
- **No engine code changed in Part C** → the Part B gate numbers stand
  (pytest **1086**, eval jjk **24/24**, canon opm **8/16 exact, 235/237,
  78.5%**). No re-gate required.

_G21 (generator-checker word-set inclusion: the `PROPER` regex merged
consecutive capitalised runs; fixed with a `name_words` word-list + `variants_ok`
word-set check) was fixed and gated in the generation step by the checker unit
suite (`r6_check_unit.py`), not an engine change. See the HANDOFF ledger._