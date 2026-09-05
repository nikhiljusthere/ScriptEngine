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
| **D6** | **Comprehension** (§2b, §2c): every extracted row is either a placed **event** (type + arc index + participants) or an explicitly marked **standing state**; all three survival checks pass; and cross-page accounts of the same event agree on placement. |

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

---

## 2c. The comprehension build

### The finding that shapes the whole design

The `relations` table places only 36% of its rows in an arc, and the obvious
reading is "the extractor fails 64% of the time." **That reading is wrong**, and
the measurement says so:

| relations from… | rows | carry an `era` |
|---|---:|---:|
| **arc-named sections** | 207 | **207 — 100%** |
| every other section | 614 | 91 — 15% |

And every one of the 523 era-less rows comes from a section naming no arc. The
top such sections are `Personality` (158), `Synopsis / History` (41),
`Abilities and Powers / Overview` (17), `Trivia` (15), `History` (13).

Two conclusions follow, and they are the foundation of this design:

1. **Placement is structural, not inferential.** Where the wiki files prose
   under an arc heading, placement is free and perfect. A better model buys
   almost nothing; more arc-named headings and citation parsing buy everything.
2. **Most of what was "unplaced" is correctly unplaced.** Personality is a
   standing trait. Abilities are capabilities. Trivia is out-of-universe. These
   are **atemporal by nature**, and dating them would be an error.

> **So the schema must distinguish a standing state from an event, and "no arc"
> must be a valid, correct answer — never a miss.** A design that tries to put
> every line on a timeline will manufacture false precision on roughly two
> thirds of the corpus.

### What is already built, and barely used

`chunk_nodes` holds **192,192 chunk-to-entity links** with alias resolution —
Yuji Itadori is linked to 3,567 chunks, **3,547 of them on other pages**. The
cross-page index the goal requires already exists.

It is referenced **7 times in the entire codebase**: the schema, the writer, a
table list, and **exactly one read query** (`stores/facts.py:1142`).

> **The lesson, and the sequencing rule that follows: wire the door before you
> fill the room.** `semantics` (0 rows) and `prose.db` (0 bytes, no tables) are
> two corpses of the same pattern — a structure built with no door reading it.
> Do not create a third. Prove a consumer exists using data already on disk
> *before* spending a GPU-week on extraction.

### The build, in order

**Step 1 — prove the door, with no extraction at all.** Hand-write ~25 event
rows for one arc into an `events` table. Point `narrative.py`'s beat ordering at
them instead of the `_INSTALMENT` title regex. Read the beats. **If a script
writer cannot tell the difference, no extractor is worth 5,507 sections.** One
round-trip, zero GPU. Equally cheap: make the narrative path read the 431 `arc`
facts and the 207 era-carrying relations that already exist. If free existing
data does not visibly beat the title regex, 50,000 extracted events will not
either.

**Step 2 — clone `ingest/relations.py`; do not invent.** It already carries
`revid` caching, `--dry-run`, verbatim-quote verification, `_era_for()` arc
mapping and work-gating. Copy to **`ingest/events.py`** and change only the
prompt, the vocabulary (social → eventive: fought, killed, awakened, sealed,
betrayed, saved, arrived, departed) and the row schema:
`(subject_node, verb, object_node, arc_key, section_id, quote, temporal)` —
where `temporal` is an explicit boolean, so a standing state is recorded *as*
one rather than as a placement failure.

**Step 3 — target extraction with the index you already have, in two passes.**
A chunk holding one entity is description; a chunk holding **two or more
character nodes is an interaction** — an event candidate, already localised,
already citable, already alias-resolved.

- **3a — the placement set (proof of mechanism, cheap).** Page-type scoping to
  `event` + `battle` + `story_arcs` (108 pages on JJK) is a valid, cheaper
  operationalisation of this filter than a raw chunk sweep, and it is where the
  container-gate problem (a battle/arc page standing in for its own
  participants) is easiest to catch and fix. **Build and prove the gate here
  first** — it is a fraction of the corpus and surfaces the failure modes
  cheaply.
- **3b — widen to the full corpus (do not skip this).** Once the gate (§ below)
  is proven on 3a, re-run extraction filtered on node degree ≥ 2 **and** a
  narrative-family heading across **all 19,684 chunks**, not just the 108
  placement pages. This specifically reaches character `Synopsis`/`History`
  sections and chapter `Plot Details` — excluded from 3a — which is where most
  of a character's own history actually lives (96–99.6% of what a corpus says
  about a character sits **off** that character's own page; see §2a). Skipping
  3b leaves D6 satisfied only for battles and arcs, not for characters, which
  is the case the user asked for by name (a Yuji stat on Kenjaku's page).

**Per-section, gated — not per-line**, in both passes. Per-line buys resolution
nothing consumes.

**Step 4 — build the time axis from the cheap signals first, model last.**
- arc-named headings: **100% reliable** where present (207/207)
- `(Chapter N)` / `(Episode N)` citations: present in **15.1%** of chunks and
  **15.9%** of sections — deterministic, parsed already by `citations.py`
- `chronology.py`'s arc chain: converts an arc *name* into an orderable **arc
  index**. A name does not sort; an index does.

Spend inference only on the residue none of those three reach.

### The gate: three equality checks, nothing to grade

An extracted row survives only if all three hold:

1. its `quote` appears **verbatim** in the source passage,
2. every participant resolves to a real `nodes.id`,
3. its `arc_key` exists in the known arc set — **or** `temporal` is false.

String and foreign-key equality. No judgment, no gold to author, nothing an
agent can be generous about. Report the **percentage of narrative beats carrying
a surviving row**, split by temporal and atemporal.

**Second, ungameable, and better: cross-page agreement.** The Shibuya fight is
described on Yuji's page, on Sukuna's page and on the arc page — by different
human editors. Extract independently from each and check the same event surfaces
with a consistent arc placement. **An agent cannot reword its way into agreement
between authors it did not write.**

### Before any of this: write down twenty failures

No script line that came out wrong has been recorded anywhere. Every number in
this document describes the corpus, not a defect. Write **twenty real failing
script lines with their correct output**, frozen as acceptance cases, before
spending a GPU-week. If twenty cannot be produced, the event graph is not yet
the highest-value work — and that is worth knowing for the cost of an afternoon.

### What it unlocks

Once events carry an arc index you can ask what a character **knew at a given
moment**, and reject a script line referencing an event three arcs early. That
is continuity checking; it is what "understanding" actually buys a script
writer; and it is deterministically testable.

**Sequencing:** D5 (reachability) and D6 (comprehension) are independent. Ship
D5 first because it is finite and nearly done — but stop describing it as if it
were D6.

### Build status (2026-09-05) — all five phases built and green; the goal is not yet met

The five phases above are **shipped** on `jjk`: Phase 1 door (`DOOR_TEST`),
Phase 2 `ingest/events.py` (714-event placement set), Phase 3 time axis
(`arc_index` on every placed event), Phase 4 targeted extraction (3a 108-page
placement set → 3b full-corpus 524 pages = **2,748 events**, + the
section/chapter placement-signal fix), Phase 5 the mechanical gate +
cross-page agreement (+ the continuity-check scaffold). Records live in
`reports/comprehension/` (`GATE.md` is the live record; standing gates green:
pytest 1,202, span-recall 48,572/48,572 (tier 0), eval 24/24, canon-run opm 79.0%).

What is **not** done is the *goal*, not the mechanism. Split the "100%":

- **Reachability (D5): not met** — 48,572/48,572 lines sit whole in a chunk is
  **tier 0 (indexing, a tautology)**. The retrieval tier (the real D5) was
  sampled 2026-09-03 over 545 probes (1.1% of lines, now stale): verbatim
  387/400 (96.8%), scoped 110/120 (91.7%), terms 24/25 (96%).
- **Comprehension (D6): not 100%** — 154 events unplaced on the axis (the
  reserved inference residue), 107 cross-page disagreements (31 interaction-verb
  anachronisms), `abilities` narrow (94 characters), `relations` social-only with
  64% era-less, `semantics` 0 rows (no per-line meaning layer), 81% of `edges`
  untyped.

The remaining work, in priority order (R1 per-line meaning index → R2 abilities
coverage → R3 relations era+eventive → R4 place the 154 → R5 typed edges), with
its done-gates and the standing council/GPU/gate/commit requirements, is the
**updated plan** in `reports/comprehension/COMPREHENSION_REMAINDER.md`. Do not
read the five green phases as "the corpus understands a character"; R1 is what
makes a writer's line *mean* something the engine can state.

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

### Wave 0 — the reachability pre-pass (all seven, before any prose)

JJK closed at 0 unreachable lines only after the D5 fix: its `References`
section carries per-chapter trivia the span-recall oracle deliberately counts as
reachable, but the chunker skipped it — the chunker's skip-policy and the
oracle's content-policy had diverged. The other seven are still red, and the
surface is large (measured wave-0 baseline):

| series | unreachable lines |
|---|---:|
| csm | 439 |
| opm | 1,039 |
| bleach | 1,171 |
| hxh | 1,224 |
| berserk | 1,256 |
| db | 8,438 |
| onepiece | 7,088 |
| **total** | **20,655** |

`opm` (1,039) and `bleach` (1,171) are the already-known Trivia chunking gap;
the rest is a mix of causes. The first action on each wiki is to **break its
unreachable lines down by cause** — the D5-class (chunker skips a section the
oracle counts: `references`/footnote lists, and any other title the oracle treats
as content), the Trivia bullet gap, and anything else — then fix each cause. The
D5-class fix is now mechanical: the `effective_boilerplate_sections(overrides)`
helper subtracts a wiki's `content_sections` override from the chunker's skip
set, so a per-wiki `content_sections:` in `series/<s>/overrides.yaml` closes it
without touching the engine's global set or the other six.

Two constraints from the D5 council: (1) keep the oracle the stricter canary —
the span-recall `BOILERPLATE` stays independent of the chunker's skip policy, or
it becomes a tautology that can never flag a new gap; (2) route
`roster._member_prose` and `export._write_document` through the same helper so
the skip policy has one source.

**Gate, per wiki:** `span-recall` down to 0 unreachable (or a documented floor,
recorded in the wiki's audit), `pytest` green, `eval` green. **This pass is a
prerequisite to §5.4** (a per-corpus `prose.db`): prose is not authored against
an index with unreachable lines.

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

## 12. The dimension map — what "everything about a character" means

R1–R5 are retired. They were written against a narrow reading of the goal
(semantic class + is_event + participants + arc_index) and the owner has
corrected it: *"I did not mean only those 3 things, I meant everything."*

*Measured 2026-09-05 from `sections` on `character` + `character_synopsis`
pages. Regenerate per §10.*

| dimension | words | extracted today | consumer — the query this buys | acceptance |
|---|---:|---|---|---|
| arc synopses | ~174,000 | 8-verb events only | "what happened, in order" | events placed + agreeing |
| **Personality** | 42,533 | **none** | how a character *speaks and behaves* | trait rows w/ quote + era |
| Overview | 16,731 | none | one-paragraph character brief | brief per character |
| Trivia | 15,887 | none | colour, out-of-universe notes | tagged, in/out of universe |
| **Appearance** | 14,180 | **none** | how to describe them on screen | descriptor rows, era-scoped |
| Cursed Technique | 13,611 | names only | what the ability *does* | mechanics per named technique |
| History | 11,595 | barely | pre-series backstory | placed before arc 0 |
| Physical Prowess | 10,595 | none | feats, limits | feat rows w/ quote |
| Intelligence | 9,674 | none | tactics, how they think | same |
| Abilities and Powers | 8,481 | names only | ability inventory | 146/146 characters |
| Cursed Energy | 6,416 | none | capacity, output | same |
| Equipment | 3,782 | none | what they carry | item rows, era-scoped |
| **Quotes** | 1,518 | **none** | the character's actual voice | attributed lines |

~106,000 words of character prose have zero structured extraction.

> **Word count is not priority.** Two columns above exist because ranking by
> volume would push work toward Personality and Overview (59k words of
> subjective prose that may not extract into anything queryable) ahead of
> Cursed Technique (13k words, mechanically structured, schema half-built, 594
> names already landed). **A dimension is only scheduled once its consumer
> column names a real query and its acceptance column names a test that can
> fail.** A dimension with "NO" → "yes" and no failing test is how an indexing
> tautology got reported as retrieval coverage.

### The precondition the map rests on, and nobody has measured

**Nothing schedules off this map until the eight-verb coverage is measured.**
`fought / killed / saved / arrived / departed / awakened / sealed / betrayed`
was typed by someone; 174,000 words went through it and 2,594 rows came out.
Nobody has recorded what the *other* verbs were.

> Sample 100 random plot-summary sentences. For each, record whether the eight
> verbs can express what it describes. **Report the fraction they cannot hold,
> with the sentences.** That single number decides whether 2,594 events are a
> foundation or a sample — and it needs no model, only reading.

### Extraction is not always the answer — the test that decides

A dimension reading "NONE" is a defect **only if structure is what it needs.**
The consumer here is a model that writes; it does not need Personality
pre-parsed, it needs the right paragraph, cited and placed. **Structure earns
its cost only where prose cannot do the job:** joins, ordering, filtering,
aggregation, state-at-a-moment.

By that test the map splits:

- **Genuinely structural** — battle outcomes, state-over-time, causality,
  chapter→episode. A model cannot infer these reliably from chunks in a window.
- **Probably retrieval, not extraction** — Personality, Appearance, Overview,
  Trivia, History. Before scheduling any extraction here, run the retrieval
  test: for ten "how does X behave / what do they look like" questions, does the
  served bundle contain the paragraph that answers it? **If yes, no extraction
  is owed. If no, that is a chunking defect, not a missing table.**

This replaces "last because biggest," which was a restatement, not a reason.

### Three dimensions the map does not cover, and must

1. **State over time.** What was *true* of a character during an arc — grade,
   allegiance, alive/dead, sealed, possessed. You cannot write a Shibuya scene
   without knowing Gojo is sealed from that point. Nothing models this.
2. **Outcomes.** `events` records that a fight happened, not who won — though
   battle pages carry result fields already.
3. **Causality.** Why something happened and what it caused.

---

## 13. Phase 0 — the retention decision (blocks everything downstream)

*Verified in source 2026-09-05.* `FactStore.reset()` drops `events` **and**
`meaning` first, by design — its own comment says *"an `index` rebuild
invalidates it: the rows reference this build's ids, so `events-extract` is the
only way back."* `build.py` calls `reset()` unconditionally at the top of every
index run.

So **the 2,594 events already in the store are wiped by any routine re-index,
today.** That is a live exposure, not a hypothetical, and it becomes
prohibitive the moment a 24,000-sentence GPU batch sits under the same scheme.

`abilities` survives a rebuild because it is keyed on character *name*.
`events` and `meaning` are keyed on `section_id`, which renumbers.

**This was written up as a decision for the owner. The council cancelled it,
and three of four advisors reached that independently: it is not a choice
between a known and an unknown — it is a choice about whether to copy something
already working in this repo.**

`abilities` survives rebuilds. The precedent is in-tree. So:

- **Do the durable key.** `document.title` + section ordinal + sentence ordinal
  + content hash, with a remap on rebuild. Not a memo, a precondition.
- **First, the five-line guard:** `build.py` refuses to `reset()` while derived
  tables are non-empty unless `--force`. A reflexive `cli index` destroying a
  24,000-sentence pass is the one failure that costs days, and this is the
  cheapest item in the entire plan.

The "wipe is the feature" rationale was written when re-extraction was cheap.
It also conflates two things: a rebuild invalidates row *ids*, not row
*content* — and `revid` already tracks whether the source text actually
changed. Rows are being discarded for a key choice, not for staleness.

---

## 14. Step semantics — suggestion, verification, refusal

Every step in a phase is a **suggestion carrying a premise**. The executing
agent checks the premise *first*, and only works if it holds.

**A step is written in three parts:**

```
STEP 3B — widen abilities to full character coverage
  PREMISE   : 94 of 146 character pages have ability rows; the other 52 have
              an Abilities section with >0 words.
  VERIFY    : <the exact query that confirms or refutes it>
  IF HOLDS  : <the work>
  IF REFUTED: halt, record in deviation_reasons.md, surface — do not substitute
```

> **Refusal authority, not substitution authority.** The executing agent has
> twice declined an instruction and been right both times — and both were
> *refusals* (declining to rewrite `arc_key`, which would have broken the only
> consumer). Refusal is cheap to review and fails safe. Substitution — doing
> something else instead — has no track record here and fails silently. **A
> refuted premise halts the step and surfaces it. It does not authorise a
> different action.**

### `deviation_reasons.md`

One entry per refuted premise. **Each entry must carry the query output or the
file:line citation that refuted it** — a deviation justified by narrative
rather than evidence is not a deviation, it is a story. This file is
agent-authored, which puts it in the same class as the self-reports that have
been wrong five times; the evidence requirement is what makes it checkable.

```
## <step id> — premise refuted <date>
- premise as written:
- what the check actually returned:   <raw output / file:line>
- why the step cannot proceed as written:
- halted at:                          <what is now blocked>
```

---

## 15. `flow.md` — the phase graph, and why it holds no status

The need is real: phases get forgotten while sub-phases run. But a
hand-maintained checkpoint file is **exactly** the artifact §0 forbids, and for
a reason this project paid for — four phantom work items in one day came from a
planning document that claimed work remained when it was already done.

**The resolution: `flow.md` holds structure, never state.**

- **It holds:** the phase graph — phases, their sub-steps, what each depends
  on, and the gate that closes each phase. This does not change as work
  proceeds, so it cannot go stale.
- **It does not hold:** checkboxes, progress counts, "current phase", "next
  step", or any claim about what is done.
- **Status comes from a query**, appended by the generator, never typed.

### The phase gate — why the last item is a gate, not a step

The requested pattern is that a phase decomposing into 1A–1E gets a 1F reading
"continue to Phase 2 now." **Write it as a gate instead:**

```
1F — GATE: emit the query output proving 1A–1E landed. Council verifies.
     Only on green does Phase 2 open. Never "continue now."
```

A bare "continue now" is a checkbox authorising advancement, placed directly
after steps the agent graded itself on. The campaign once reported as "100%"
while stepping around the same bug eight times **would have ticked it**. The
gate makes advancement contingent on evidence rather than on completion of the
preceding line.

---

## 16. Who runs which work

Two engines, and the split is not about capability — it is about volume,
judgment, and what each one is metered on.

| work | engine | why |
|---|---|---|
| bulk extraction (24k sentences) | **local 27B (ninfer)** | high volume, low judgment, schema-constrained. Costs electricity, not quota. |
| verification against the store | **reviewer (Claude)** | low volume, high judgment; every defect this project found was caught this way |
| the **accuracy oracle** | **reviewer (Claude)** | see below — top-down, not a labelled sentence set |
| design review, gate adjudication | reviewer | |

**The bulk pass must not move to the reviewer.** A 24,000-sentence batch is
roughly four orders of magnitude beyond what the reviewer's own quota sustains
— an attempt to run five council advisors in parallel on 2026-09-05 hit a
session rate limit after four. The local model is the right engine for this
work precisely because it is free and resident.

**What should move to the reviewer is the oracle — and it is top-down, not
bottom-up.** Every batch so far has proved that the guard fires, never that the
labels are right. But a set of hand-labelled sentences scores the *extractor*,
not the goal: a ruler built on event verbs cannot measure whether a personality
description was understood.

**The oracle is real script beats.** Take beats a writer actually needs, ask
what the corpus had to supply, and log what it could not. That is the only
instrument that distinguishes "this dimension needs structure" from "this
dimension needs a better chunk" — and it is the distinction the whole dimension
map turns on. The executing agent must not author it; an agent grading its own
work is the loop that produced five unreported defects.

---

*Council-reviewed 2026-09-05. The findings in §5 were produced by source and
database inspection; each is reproducible via §10. §12–§16 added after the
owner corrected the goal's scope; the §13 retention finding and the §16 quota
evidence were verified the same day.*
