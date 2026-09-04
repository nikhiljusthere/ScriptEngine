# Plan to Perfection

How the remaining seven corpora reach done, using what JJK actually proved —
not what JJK appeared to prove.

---

## 0. What this document is, and is not

This file holds **only things that do not change**: definitions, policy, floors,
exit criteria, the authoring rules, and the order of work.

It contains **no status**. No checkboxes, no progress counts, no "next step"
lines. Four separate phantom work items were generated in a single day by
planning documents that stated what remained; every one of them had been done
weeks earlier and the document had not been told.

> **The rule that follows from that:** if a number in this document is not
> either (a) a threshold you are choosing, or (b) a measurement stamped with a
> date and the command that regenerates it, it is a lie in progress. Status
> lives in generated reports. Section 10 lists how to regenerate everything.

Every measurement quoted below was taken **2026-09-05** and is reproducible.

---

## 1. The one idea

**Questions are the instrument. Filed engine gaps are the product.**

JJK produced 29,819 active questions and 30 numbered engine gaps (G1–G30). The
questions were never the deliverable — they were the apparatus that made the
gaps visible. Every gap fix is engine improvement that all eight corpora
inherit; the question bank is scaffolding that also happens to be a regression
suite.

This reframes the whole programme. You are not trying to write 660,000
questions for 21,958 pages. You are trying to make each new wiki's failure modes
visible at the lowest cost, fix them, and prove they stay fixed.

A corpus is finished when it has stopped teaching you anything — not when every
page has a question.

### The corollary nobody wants

**A 100% pass rate is a warning sign, not an achievement.** A bank that never
fails is not measuring the engine; it is measuring the author's willingness to
avoid what the engine cannot do. On JJK the "never reword a question to make it
pass" rule was violated twice and caught twice — both times by a human reading
output at 987 pages. At 21,958 pages nobody reads. See §5.5.

---

## 2. Definition of Done, per corpus

Four conditions. All four must be answerable by a query whose raw output you
paste, never by prose.

| # | Condition |
|---|---|
| **D1** | Every page is **covered or excluded in writing**. Exclusion is a committed artifact with a one-line reason per page, not an omission. |
| **D2** | Every **archetype** (§6) meets its declared depth floor, measured against *populated in-scope sections*, never raw page count. |
| **D3** | **Zero unfiled engine gaps**, and the red list is **not empty**. A corpus with no expected failures has not been probed. |
| **D4** | A **held-out probe set**, authored by someone other than the executing agent, passes at a declared threshold. |

D4 is the load-bearing one and it is new. D1–D3 are all measured by the party
being scored.

**"100%" and "perfection" are retired as targets.** They are why the goal kept
sliding. The target is the four conditions above. This document keeps its name
for continuity, not because perfection is the measure.

---

## 3. What JJK actually cost

*Measured 2026-09-05 across 896 base batches; see §10.1.*

**Composition of the bank:**

| source | share |
|---|---:|
| `page-gen` — deterministic, generated from infobox facts | **44.2%** |
| mechanical paraphrase (reword / yes-no / contextual variants) | **17.8%** |
| hand-authored prose | **~38%** |

**Density distribution:** median **11** questions per page; mean 33.4; **49%**
of batches hold fewer than ten; the top twenty batches hold 22% of the total;
five batches hold zero.

### The lesson

**Roughly 62% of JJK was machine-generated.** The "30 questions per page"
average is an artifact of a handful of enormous character batches sitting on top
of a long tail where the median page has eleven.

So the thing to scale is the machine, not the humans. The remaining corpora do
not need 660,000 hand-authored questions. They need the generator pointed at
them, and human effort reserved for the tier that cannot be generated.

---

## 4. The four supply tiers

Work the cheapest tier to exhaustion before spending a human round-trip on the
next one. This ordering is the plan's central economic claim.

### T0 — Structured generation. Free, mechanical.

`scriptengine/eval/page_gen.py` is **already series-agnostic**. Its
`IDENTITY_FIELDS` is a 16-entry dict mapping *infobox field names* to question
templates; the only `jjk` strings in the file are comments. It reads
`facts.db`, whose schema is identical across all eight series.

*Measured 2026-09-05 — structured questions available today, no new code:*

| series | pages | fact rows | identity-field matches | field coverage |
|---|---:|---:|---:|---:|
| onepiece | 7,613 | 59,823 | 3,390 | 6/16 |
| db | 7,205 | 62,612 | **10,519** | 9/16 |
| bleach | 2,252 | 21,532 | 2,534 | 8/16 |
| hxh | 2,018 | 19,463 | 2,395 | 9/16 |
| opm | 1,571 | 14,527 | 2,102 | 9/16 |
| berserk | 762 | 4,670 | 340 | 8/16 |
| csm | 537 | 5,081 | 535 | 6/16 |
| **total (7 series)** | **21,958** | | **21,815** | |

**21,815 structured questions are available right now for zero authoring** —
73% of JJK's entire active bank, sitting in databases that already exist.

Field coverage is the per-wiki readiness metric. One Piece hits only 6 of 16
identity fields despite being the largest corpus; that is where field-mapping
pays most, and it is a dict entry, not a campaign.

> **The limit of T0, which must not be forgotten.** Generated questions are
> instances of shapes the engine already handles. They buy **D1 and D2** —
> coverage and regression protection — and they buy them cheaply. They will
> **not** buy D3. A template that passes today cannot surface G31. Minting
> 21,815 questions from sixteen fixed templates and declaring the corpus probed
> is precisely the coverage theater this plan exists to avoid. **Gap discovery
> comes disproportionately from T3 and from novel question shapes.** Do not let
> a large T0 number end a campaign.

### T1 — Mechanical paraphrase. Free transform.

Reword / yes-no / contextual variants over T0 output — 17.8% of JJK. Costs
compute, not round-trips. Carries the same limitation as T0: a paraphrase of a
passing question usually also passes. Its value is robustness, not discovery.

### T2 — Sets and rosters from structure. Free `SELECT`.

JJK carries 1,355 hand-declared rosters; the other series carry 18–62, and this
looks like a debt to be repaid sevenfold. **It is not.**
`series/jjk/overrides.yaml:26` says so in its own words:

> *"The sets this wiki maintains. Discovery already answers most of these
> correctly; declaring them makes the answer the same every time."*

Roster declarations are **determinism hardening over discovery that already
works** — not a prerequisite. And the structural ground truth is richer
elsewhere than in JJK:

*Measured 2026-09-05:*

| series | edges | edges/page | categories | cats/page |
|---|---:|---:|---:|---:|
| onepiece | 440,245 | 57.8 | 1,702 | 0.22 |
| db | 312,598 | 43.4 | 322 | 0.04 |
| bleach | 130,670 | 58.0 | 165 | 0.07 |
| hxh | 62,066 | 30.8 | 271 | 0.13 |
| opm | 43,077 | 27.4 | 389 | 0.25 |
| jjk | 35,026 | 35.5 | 230 | 0.23 |
| berserk | 18,418 | 24.2 | 51 | 0.07 |
| csm | 11,261 | 21.0 | 83 | 0.15 |

Typed relations (`participants`, `side1`, `result`, `affiliation`, `race`,
`relatives`, `located in`) are denser per page in One Piece and Bleach than in
JJK. That is provenance-bearing set gold for free.

> **A correction to guard against.** It is tempting to conclude that JJK has an
> unusually thin taxonomy and other wikis are therefore trivial. Per page, JJK
> sits at 0.23 categories — essentially tied with One Piece (0.22) and OPM
> (0.25), and *ahead* of Dragon Ball (0.04), Bleach and Berserk (0.07). Berserk
> has 51 distinct categories to JJK's 230. One Piece leads in absolute count
> only because it has 7.7× more pages. The genuine advantage elsewhere is in
> **edges**, not categories.

**Method for T2:** run discovery against JJK's 1,355 declared rosters as a
labeled oracle. Measure agreement. Fix the extractor where they disagree.
Declare only the residue. One engineering task replaces seven authoring
campaigns.

### T3 — Prose. The only expensive tier, and the only reliable source of gaps.

Summary / plot / synopsis / ability narrative. This is what humans must write,
it is the only tier whose cost scales with corpus size, and — per the limit
noted under T0 — it is where new engine gaps actually come from. Budget here
and nowhere else.

**Blocker:** only `series/jjk/` has a `prose.db`. The other seven have none.
T3 cannot start on any other corpus until that is produced (§5.4).

---

## 5. Phase 0 — blockers that must close before any corpus begins

Every one of these was found by inspection, and every one silently corrupts the
work that would follow it.

### 5.1 The scoreboard is hardcoded to JJK

`tools/coverage_report.py:32-33`:

```python
IN_SCOPE_TYPES = {"item", "location", "organizations", "species", "simple_box", "occupation"}
IN_SCOPE_PAGES = {"Jujutsu Regulations"}
```

…and line 177 accepts `series` with `default="jjk"`, so it runs on any corpus
today. *Measured 2026-09-05 — pages matching those types:*

| series | matched / total |
|---|---:|
| hxh | **0 / 2,018** |
| csm | **0 / 537** |
| bleach | 16 / 2,252 |
| berserk | 46 / 762 |
| jjk | 52 / 987 |
| opm | 61 / 1,571 |
| db | 233 / 7,205 |
| onepiece | 258 / 7,613 |

Point it at HxH or CSM and it prints the same green *"in-scope remainder 0"*
that JJK earned over a month of work. The tool designated as the un-fakeable
source of truth is an allowlist for one campaign phase of one series — note it
matches only 52 of JJK's own 987 pages. Even near-identical types miss:
`organizations` (jjk) versus `organization` (opm).

**Fix:** move scope into `series/<s>/overrides.yaml` as declared in-scope and
excluded-in-writing type lists. The tool **exits non-zero** on any `page_type`
it has not been told how to classify. Silence must become an error, because a
zero denominator currently reads as success.

### 5.2 Gold spans are unpinned to a wiki revision

Every `documents` row carries a `revid` (987/987 on JJK). **No question or
verify file references a revid or content hash.** Gold answers must be verbatim
substrings of live wiki text, and wikis are edited continuously. The corpora
were crawled in August 2026; over a multi-month campaign across eight of them,
gold rots silently and the failure presents as an engine regression.

**Fix:** stamp `revid` (or a section content hash) at authoring time.
Re-verification after any re-crawl becomes a diff, not a re-read.

### 5.3 "G1–G30 transfers free" is asserted, never tested

The gap fixes are series-agnostic *in principle*. The regression suite is not:
44 `series_paths("jjk")` references against 13 for all other series combined,
and in the router and narrative tests specifically, 35 JJK against one One Piece
and one OPM. The fixes were tuned on JJK shapes and are guarded almost entirely
by JJK fixtures.

**Fix:** a cross-series regression gate — each numbered gap gets at least one
non-JJK fixture before its corpus campaign starts.

### 5.4 Only JJK has a `prose.db`

Blocks T3 everywhere else. Must be produced per corpus before prose authoring.

### 5.5 The author is the grader

The executing agent writes the question, selects the gold span, and reports its
own pass rate. That is not a weak measurement; it carries no information. Two
rewording violations were caught on JJK only because a human read output at 987
pages — that does not survive 22× scale.

**Fix, in order of strength:**

1. **Generator-sliced gold.** Where the generator slices the gold span directly
   out of `sections.text`, verbatim-substring becomes a structural guarantee
   rather than a policed rule. Rewording to pass becomes impossible instead of
   forbidden. Prefer this everywhere it applies.
2. **Held-out probe sets** authored by a party that is not the executing agent,
   which that agent runs but may never edit. A failure there is a finding, never
   an authoring defect.
3. **A pre-registered red list** of expected failures, written before the wave.

### 5.6 The seven are not greenfield

`questions/` already holds OPM page batches and seed banks of roughly 35–42
questions each for bleach, csm, db, berserk, hxh and onepiece. Any plan step
that assumes an empty starting state will duplicate work or clobber it. Inventory
before authoring — this is exactly the phantom-work failure mode from §0.

---

## 6. Archetypes, not taxonomies

Page types are wiki-specific — `char_box`, `hunterpedia_character`,
`character_updated`, `bleach_wiki_episode`, `episode_manga`, `chapter_box`. It
is tempting to conclude that seven taxonomies must be rebuilt.

They collapse. `char_box` / `character` / `hunterpedia_character` /
`character_updated` are one archetype. A small set — character, chapter,
episode, battle, technique/ability, location, and a release/merchandise class —
covers the overwhelming majority of pages in every corpus.

**So the per-wiki work is a mapping file, not a campaign:**
`infobox_template → archetype`, declared in `series/<s>/overrides.yaml`.

This is the most important structural claim in this plan, because it changes
what round-trips scale with:

> **Humans review archetypes, not pages.** Round-trips scale with archetype
> count (~7), not page count (21,958).

Question templates, depth floors, and section scoping are defined **per
archetype, once**, and inherited by every wiki that maps into them.

---

## 7. Order of work

Smallest first, to calibrate the estimate before betting on it.

| order | series | pages | why |
|---|---|---:|---|
| 1 | **csm** | 537 | Pilot. Smallest corpus. Its only job is to produce the first real cost number. |
| 2 | berserk | 762 | Second-smallest; different archetype mix (`episode_manga`) tests the mapping. |
| 3 | opm | 1,571 | Already has batches and is the standing canon gate. |
| 4 | hxh | 2,018 | |
| 5 | bleach | 2,252 | |
| 6 | db | 7,205 | Largest structured yield (10,519). |
| 7 | onepiece | 7,613 | Largest, lowest field coverage (6/16) — do it once the mapping is proven. |

**Every schedule estimate in any document is fiction until the CSM pilot
produces a real number.** Do not commit to a timeline before it exists.

### The pilot's job

CSM is not there to be finished. It is there to answer four questions: how many
T0 questions actually emerge; what fraction survive verification; how many new
gaps a fresh wiki produces; and how many human round-trips the whole thing took.
Those four numbers set every subsequent estimate.

---

## 8. The stop rule

**Gap saturation, not coverage.** A corpus is done when N consecutive waves
produce zero new numbered gaps — with one essential caveat:

> In a closed loop, "no new gaps" and "stopped looking" are indistinguishable.
> Saturation only counts when measured against the **held-out set (D4)**, which
> the executing agent did not author and cannot edit.

Without D4, saturation is fatigue with a certificate.

---

## 9. Rules that carry over unchanged

These were paid for in JJK. They transfer verbatim.

1. **THE KEY RULE.** Never reword a question to make it pass. A failure is a
   gold error or an engine gap — never a phrasing problem.
2. **The 3-phrasing probe, mandatory before any rephrase.** Probe at least three
   natural phrasings of the same fact. Most pass and one stilted form fails →
   authoring, rephrase permitted. Most fail → the fact is not broadly reachable
   → engine gap: leave the question failing and file it. The probe table is
   pasted into the triage file every time — never summarized, never asserted.
3. **Execution tier.** The executing agent does not edit engine code or series
   config. It proposes and stops.
4. **Continuous waves.** A failing question goes to a triage file; it does not
   stop the run. Router and chunker gaps are batched and proposed at the end,
   never one round-trip each.
5. **Round-trip economy.** The unit of cost is the human round-trip, not the
   question. Ten waves of twenty questions cost far more than two waves of a
   hundred.
6. **Every batch reports actual/estimate.** Below 0.9 halts for approval. A
   campaign that delivered 232 questions against its own 382 estimate and
   reported success must be structurally impossible.
7. **Every failure is classified** gold error or engine gap, and the **split is
   reported**. That ratio says which side is weak.
8. **Receipts are raw query output**, not prose. "100% pass rate" is banned as a
   completion claim.
9. **Coverage is generated, never hand-maintained.** No document states what is
   next or what remains; it points at the generated report.
10. **Named paths only.** Never `git add -A`.

---

## 10. Regenerating every number in this document

Nothing above should be trusted because it is written down. Each measurement is
reproducible; if a number here disagrees with a fresh run, **the fresh run wins
and this document is wrong.**

| § | measurement | how |
|---|---|---|
| 3 | bank composition, density | classify each question in `questions/_<series>_page_*.json` by `note` prefix (`page-gen:` / `R<n> paraphrase` / `prose:`), excluding `.verify` / `.coverage` / `.decl` / `.section` sidecars and the cross-page `paraphrase_r6` batch; report the per-batch count distribution |
| 4 (T0) | structured yield | count `facts` rows whose key is in `page_gen.IDENTITY_FIELDS`, per series, plus distinct keys hit |
| 4 (T2) | structural ground truth | count `edges` and distinct `categories` per series from `series/<s>/facts.db`, normalized per page |
| 5.1 | scoreboard defect | count `documents` whose `page_type` is in `coverage_report.IN_SCOPE_TYPES`, per series |
| 5.2 | gold pinning | count `documents` carrying a `revid`; grep the question corpus for `revid` / `content_hash` |
| 5.3 | cross-series regression coverage | count `series_paths("<s>")` occurrences per series across `tests/` |
| 5.6 | existing seed banks | inventory `questions/` per series before authoring |
| 7 | corpus shape | pages and sections per series, and the `page_type` histogram, from `documents` and `sections` |

---

## 11. Standing gates

Unchanged, and they gate every corpus:
`eval --series jjk` · `canon-run --series opm` · `pytest tests/ -q` ·
`span-recall --series jjk`. Their expected values live in `CLAUDE.md`, which has
itself gone stale twice — verify before trusting.

---

*Council-reviewed 2026-09-05. The findings in §5 were produced by source and
database inspection; each is reproducible via §10.*
