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
| **D5** | **Line-level reachability** (§2a) is exhaustively measured and its miss file is empty. |
| **D6** | **Comprehension** (§2b): a declared fraction of event-bearing lines carry a type, an arc index and a participant set, and the consistency checks return zero violations. |

D4, D5 and D6 are the load-bearing ones. D1–D3 are all measured by the party
being scored.

**D5 and D6 are different layers and neither substitutes for the other.** D5
certifies a line is *delivered*; D6 certifies something knows what it *means*.
A corpus can pass D5 at 100% while placing every event in the wrong arc.

**"100%" and "perfection" are retired as slogans** — but D5 gives the phrase a
real referent for the first time. See below.

---

## 2a. The line-level target — reachability vs answerability

The stated goal is *"every line of every page can be asked about and answered
accurately, in the same or natural wording, no matter how small."* That fuses
**two properties with opposite characters**, and every measurement pathology in
this project comes from grading the first through the machinery of the second.

| | **Reachability** | **Answerability** |
|---|---|---|
| question | does the served bundle contain line L? | is the answer meaning-preserving? |
| domain | **finite** — lines × doors | **infinite** — all natural phrasings |
| needs | nothing but a substring test | gold spans, judgment, humans |
| gameable | **no** — the probe *is* the wiki line | yes — this is where both reword violations happened |
| verdict | **this is the real 100%** | gets a confidence interval, never a gate |

**Reachability is the only one with a denominator, so it is the only one that
can terminate.** Drive it to zero misses across all three doors and stop.
Answerability is sampled forever and reported with error bars.

### The measurement that already exists, and the name that hid it

`span-recall` has two tiers and **the number everyone quotes is the wrong one**:

- **Tier 0** — "is this sentence inside some chunk of its own page?" This is an
  **indexing** check. It is exhaustive and cheap, and it is where
  *48,570 / 48,572* comes from. A chunker that emits every sentence passes it by
  construction. It is a tautology, not evidence of retrieval.
- **Tier 1** — "does the served bundle actually contain the line?" This is
  retrieval, it is the metric that matters, and it has **never been run
  exhaustively**. `cli.py` exposes `--probe N` defaulting to `0`, which *skips
  tier 1 entirely*.

*Measured 2026-09-05 on the committed sample rows:* verbatim **387/400
(96.75%)**, scoped **110/120 (91.7%)**. Extrapolated, roughly **1,200–1,600 of
48,572 lines are unreachable** and nobody knows which.

> **Rename `span-recall` to `chunk-containment` for tier 0.** The current name
> reads as retrieval recall to anyone who has not read the source. That single
> word bought months of false confidence, and it will keep doing so to every
> future reader until it is changed.

### Three things the metric does not currently cover

1. **Two of the three doors.** All 520 sampled probes routed `qa`. Roster and
   narrative have **zero** retrieval measurement. The denominator is lines ×
   doors, and two thirds of it is dark.
2. **Short lines.** `sentences()` ends with
   `len(s.split()) >= min_words and s.count("|") < 3`, so with the default
   `min_words=6` it drops **1,154 lines (2.3%)** — *precisely* the "no matter
   how small that line is" case. (Table rows: 0 dropped in this corpus.)
3. **Cross-page facts.** Nothing measures them. This is the requirement most
   worth building because it is the one currently at zero.

### Cross-page is the largest uncovered surface

*Measured 2026-09-05 — sections mentioning a character, by host page:*

| subject | own page(s) | elsewhere | % off-page |
|---|---:|---:|---:|
| Sukuna | 19 | 1,116 | 98.3% |
| Satoru Gojo | 6 | 855 | 99.3% |
| Yuji Itadori | 3 | 664 | 99.6% |
| Megumi Fushiguro | 2 | 489 | 99.6% |

Across all 146 character pages: **14,194 (entity, off-page section) pairs on 940
host pages** — roughly half the size of the entire hand-authored bank, and
**auto-generatable**, since the probe is again the wiki line itself.

Note what this implies: a fact about Yuji sitting on Kenjaku's page is **not a
missing question — it is a missing edge**. No volume of authored questions
repairs an index that keys chunks to their host page. Writing questions about it
paints green over a structural defect.

### Four traps in building a loop on this metric

Verified in source; each one silently invalidates run-to-run comparison.

1. **The sample is not a fixed panel.** Probes are built only from
   tier-0-passing sentences, then `random.Random(seed).shuffle(probes)[:N]`.
   Change the chunker and the eligible list changes, so the panel silently
   swaps. Deltas are sample churn, not progress.
2. **The seed is fixed at 7 and unexposed.** So every run grades the *same* 400
   lines — an agent optimising that number overfits a static held-in set.
   Together with (1): **frozen or incomparable, never a trend.** Pin a hashed
   probe panel, and hold out a split the executing agent never sees.
3. **`done` dedupes on bare sentence text.** A resume built naively on it would
   silently skip the same sentence appearing on a *different page*. The key must
   be `(title, sentence)`.
4. **`hit_rate` divides by rows actually run**, so a resumed sweep reports a
   partial denominator as though it were the whole.

### What this costs, honestly

At roughly 4s per probe on GPU: **~54 GPU-hours per mode**, ~7 GPU-days for
three modes — on a GPU that another process frequently holds. Resume is not
currently wired (`recall()` accepts `done`; the CLI never passes it).

**So this is a job with an end, not a perpetual process.** Queue it, checkpoint,
resume when the GPU frees. A "continuous loop" aimed at an infinite target
random-walks; a finite sweep terminates.

---

## 2b. The comprehension layer — what "understanding" would require

Reachability (§2a) certifies that a line is **delivered**. It says nothing about
whether anything knows what the line *means*. Those are different layers, and
the honest answer to "does the plan as written deliver understanding?" is **no** —
reachability is a plumbing gate, and passing it at 100% is compatible with
placing every event in the wrong arc.

This is the same substitution the project has already made twice: `span-recall`
was an indexing check wearing a retrieval name; reachability is a retrieval
check wearing a comprehension name.

### What exists today

*Measured 2026-09-05.*

| asset | state | verdict |
|---|---|---|
| `chronology.py` (608 lines) | walks arc `previous`/`next` as a linked list; deterministic, no model | **real, and the timeline spine** |
| `relations` table | 821 rows, 136/146 characters, **6.0 per character**; **100%** carry a source quote, **36%** carry an `era` | real, thin, **social-only** |
| `abilities` table | 594 rows | real, narrow |
| `narrative.py` beat order | `_INSTALMENT` regex on the page title (`chapter|episode|volume|…`), then section order | ordering by instalment number, not by story time |
| `semantics` table | **0 rows** | see the trap below |
| `edges` | 35,026 rows, **28,483 (81%) are untyped `mentions`** | a concordance, not a graph |
| temporal keys in `facts` | `arc` 431 · `date` 374 · `anime episode` 185, against 48,572 lines | **under 1% of the corpus knows when it happened** |

### The trap: `semantics` being empty is not the gap

It is tempting to read "0 rows" as "the comprehension layer was built and never
switched on." It was not. `cli classify` is an **ability classifier by
construction** — `ingest/classify.py:needs_classifying()` skips any page whose
type is not in `semantics.ABILITY_TYPES` (`TECHNIQUE, TRANSFORMATION, POWER_UP,
FUSION, TRAIT`). Fully populated, its ceiling is a few hundred rows of booleans
about cursed techniques. **Filling that table would not tell you that a line is
an event, or when it happened.**

Note also that the `semantics` *module* is live and load-bearing — the router
imports it and `semantic_type()` drives the story-type rule. But
`semantic_type()` reads `documents.page_type` and the infobox `Class` field. It
knows a page *is a character*; it does not know what a sentence *means*.

### The actual gap

**The relation vocabulary is entirely social** — family, ally, enemy, friend,
mentor, rival. There is no predicate anywhere in the store for *X did Y at time
Z*. Fights, deaths, awakenings, arrivals, betrayals — the events a script is
made of — are stored only as prose, and prose is what reachability delivers
without understanding.

### The gate that makes this checkable

The previous council relegated answerability to "a confidence interval, never a
gate" because it quantifies over infinite phrasings. **That reasoning does not
apply here.** You are not quantifying over phrasings; you are quantifying over
**commitments**, and a line's commitments are finite and enumerable: an entity,
a time, a relation, a state change.

So the comprehension gate is not *correctness* (which needs gold) but
**consistency** (which does not):

- Does any served bundle place one event in **two different arcs**?
- Does any extracted relation or event ship **without an `era`**?
- Does any beat ordering **contradict an `anime episode` number already in
  `facts`**?
- Does any cross-page fact about an entity **disagree** with the same fact on
  that entity's own page?

Zero human judgment, zero agent-authored gold, ungameable, and currently
unmeasured. Add it as **D6**.

| # | Condition |
|---|---|
| **D6** | **Placement coverage and consistency.** A declared fraction of event-bearing lines carry a type, an arc index and a participant set; and the consistency checks above return zero violations. |

### What to build

`ingest/relations.py` is the working template and should be copied, not
reinvented: a per-section LLM pass, cached on `revid`, emitting a **source
quote** for provenance and an **`era`** for arc placement, with `--dry-run`.
Its `_era_for` docstring is the model of honesty to follow — it records that
"63 of 109 Jujutsu Kaisen rows sit under an arc-named section while only 28
carried an era of their own."

1. **`ingest/events.py`** — the missing predicate. Emit
   `(subject, event, arc, section, quote)` over the pages already known
   tractable. Same prompt shape, same cache, same dry-run.
2. **Placement** — join event rows to `chronology.py`'s arc chain so every event
   carries an **arc index**, not just an arc name. An index is orderable; a name
   is not.
3. **Cross-page attribution** — the 14,194 (entity, off-page section) pairs
   (§2a). A fight lives on the opponent's page; a character's history is mostly
   other characters' pages.

Then the 28,483 untyped `mentions` edges stop being debt: each is a
pre-located, pre-linked **candidate event awaiting a type**.

> **What this unlocks, and why it is the real product.** Once every event
> carries an arc index, you can ask what a character *knew at a given moment* —
> and reject a script line where someone references an event three arcs early.
> That is continuity checking, it is what "understanding" actually buys a script
> writer, and it is deterministically testable.

**Sequencing:** reachability (D5) and comprehension (D6) are independent and can
run in parallel. Ship D5 first because it is finite and nearly done — but stop
describing it as if it were D6.

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

## 9a. The serial closure loop

The executing agent can run **one subagent at a time**. That is not a
limitation to work around — it is the correct shape, because the agent should
never be doing discovery in parallel. Discovery is a batch sweep; the agent only
does closure.

**The separation that makes the loop safe:**

| stage | who | why |
|---|---|---|
| **Sweep** (discovery) | a batch job, no agent | the probe is the wiki line — nothing to author, no gold to pick, nothing to reword |
| **Triage** (queue) | derived from the miss file | MISS_DOC = ranking; MISS_SPAN = chunk selection; each is a class, not a question |
| **Closure** (fix) | the agent, serially | one engine fix can move thousands of lines; one question moves one |
| **Re-score** | the next sweep | **the agent never runs the sweep that grades it** |

That last row is the whole design. Every integrity failure in this project's
history happened where one actor authored, graded, and reported. Here the agent
cannot reach the scoreboard.

**Loop invariants:**

1. **Work units are engine fixes, never questions.** If a proposed fix closes
   only one miss row, it is the wrong altitude — find the class it belongs to.
2. **The queue is pre-triaged.** The agent never chooses what to work on; it
   takes the top of the miss queue. This removes the judgment call where
   avoidance lives.
3. **Every iteration ends with a committed miss-count delta** from a pinned
   panel, not a fresh sample (§2a trap 1).
4. **The loop halts on:** an empty miss file (done), a fix that raises the miss
   count (regression — stop and report), or two consecutive iterations with no
   net reduction (stuck — escalate, do not grind).
5. **A council-style confirmation** is invoked only at decision points that
   change scope or definitions — never per fix. Confirmation loops per iteration
   would reintroduce the round-trip cost the batch design exists to remove.
6. **Nothing is unsupervised at the boundary.** The agent proposes engine
   changes; it does not apply them (§9 rule 3). Serial execution makes that
   review load tractable.

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
