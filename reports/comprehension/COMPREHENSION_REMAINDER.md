# The comprehension build — state, and what remains to full understanding

Date 2026-09-05. Companion to `GATE.md` (the live gate record) and
`Plan_to_perfection.md` §2b/§2c (the design). This file is the *updated plan*:
it records which of the five build phases are done, answers "are we at 100% of
JJK?", and lists, in priority order, the work still open against the goal.

**The goal (user, verbatim intent).** The corpus should *understand* everything
about a character — not just retrieve their lines, but know **what each thing
means**: all the structured facts, lines, prose, history and fights. While a
script is written, every line that is a wiki page's data/prose in natural
phrasing should be something ScriptEngine can say **what it means, whether it
is an event, where that event sits on the anime's timeline, and the other
details** (participants, era, source).

---

## 1. The five phases — all built, all green

| Phase | What it is | Record | Status |
|---|---|---|---|
| **1 — prove the door** | hand-written event rows drive the read before any extraction | `DOOR_TEST.md` | done |
| **2 — events.py, cloned not invented** | `ingest/events.py` (clone of `relations.py`) → `events` table, 714-event placement set | `MODEL_EXTRACTION.md` | done |
| **3 — time axis, cheap signals first** | `ingest/timeaxis.py` `arc_index` on every placed event (arc-page / arc-fact / citation / section) | `TIME_AXIS.md` | done |
| **4 — extraction, targeted** | 3a placement set (108 pages) then 3b full corpus (524 pages) → **2,748 events**; placement-signal fix (section + chapter/episode) | `GATE.md` "Step 3b", "Placement-signal fix" | done |
| **5 — gates, all mechanical** | `ingest/gate.py` three equality checks + cross-page agreement; `comprehension-gate` door; continuity-check scaffold | `GATE.md`, `COUNCIL_continuity-check.md` | done |

Supporting, also shipped: **scope-shrink check + `--scope all`** (`cffa207`),
**continuity-check scaffold** (`4f9ef82`), **id-stability FK on `events`**
(`ef94896`), **GPU device rule** (`0dd3ead`). Standing gates all green
(pytest 1,202; span-recall 48,572/48,572; eval 24/24; canon-run opm
10/16 · 236/236 · 79.0%).

> So the *mechanism* of the plan is complete. The question is whether the
> *goal* (full understanding) is met. It is not — and "100%" has to be split
> into two different numbers before it means anything.

---

## 2. "Are we at 100% of JJK?" — two different 100%s

The plan (§2b) is explicit that **reachability ≠ comprehension**: a 100%
retrieval gate is compatible with every event sitting in the wrong arc. So the
answer depends on which "100%" is meant.

### 2a. Reachability (can a question be *asked about* every line?) — **NO, D5 not met**

Two tiers, and the number everyone quotes is the wrong one:

- **Tier 0 (indexing)** — live `span-recall --series jjk` (2026-09-05):
  **48,572 / 48,572 sentences sit whole inside some chunk, 0 unreachable**
  (52 link-list boilerplate sentences excluded by default). This is a
  **tautology** — "every line is inside some chunk" is a property of the
  chunker, not of retrieval; a chunker that emits every sentence passes it by
  construction. It is *not* reachability.
- **Tier 1 (retrieval, the real D5)** — does `/context` actually *serve* the
  line? Baseline **2026-09-03** over a 545-probe sample (**1.1% of the lines**):
  **verbatim 387/400 (96.8%), scoped 110/120 (91.7%), terms 24/25 (96%)**. Misses
are `MISS_DOC` (a sibling page is served instead) and `MISS_SPAN` (the page is
   served, the line is not). A **fresh verbatim re-run landed 2026-09-05**
   (GPU `:8000`; the index is unchanged since Sep 3 — no re-crawl or re-index):
   **478/492 HIT (97.2%)**, 3 `MISS_DOC` + 9 `MISS_SPAN` + 2 `TRUNCATED`, 0
   errors — **unchanged, not improved**, from the 2026-09-03 baseline (387/400 = 96.8%): 96.8%→97.2% at n≈400 is inside sampling noise (±~1.7pp at 95%), so the index is confirmed healthy. D5
   is **still not met** — only ~400 distinct probes (≈0.8% of the 48,572 lines) and an exhaustive tier-1 has never run. *Known measurement defect:* the jsonl is append-mode (892 rows; a naive all-rows recompute gives 97.0%) and 92 rows re-probe across the resume boundary (done-dedupe keyed on bare sentence text) — it inflates row counts and would corrupt any future paired comparison.

The only open *indexing* defect is the Trivia chunking gap (standing open #5);
it does not affect tier 0 (those lines are still indexed) — it is about
*serving* them for generic questions, which is a tier-1 concern.

### 2b. Comprehension (does the engine know what a line *means*?) — **NO**

Same live store, measured 2026-09-05:

| layer | live state | gap vs the goal |
|---|---|---|
| `events` (the "X did Y at Z" predicate) | **2,748** rows; **2,594 `temporal=1`** (= placed), **154 `arc_index IS NULL`** | 154 events (5.6%) have no orderable position — **116 rows under generic headings + 38 rows on `Modulo Chapter N` docs (17 distinct docs)** filed off the story chain. After the Step-1 recompute, `temporal` tracks the live placement (`eventive verb AND arc_index IS NOT NULL`), so the temporal set **is** the 2,594 placed rows (it was 714 before). This is the plan's *residue* (where inference is allowed, not yet run). |
| cross-page agreement (gate check 2) | **107 disagreements of 390 multi-page groups (27.4% rate)** | triage (`continuity --triage`): **31 interaction-verb** anachronism core (9 premature + 22 delayed), 50 state-verb keying, 26 adjacent straddles. The 31 are the real comprehension failures. **A5 provenance split:** 98/107 (92%) of the disagreements touch a section-placed row; pure arc-named groups sit at 10.5% vs. 35.6% mixed. Since D6 is tautological, this is the *only* non-tautological placement signal → **B5**, now a **diagnostic + key-refinement** (spot-check showed 60% of the 107 are key-coarse repeat-encounters, 21% boundary noise — not a demotion gate; see B5 below). |
| `abilities` | **594** rows, **94 distinct characters** (376 technique · 187 trait · 24 item · 7 transformation) | "narrow": only ~94 of the character population carry abilities; characters with an `Abilities and Powers` section the extractor never read (or that predate the prompt) are missing. |
| `relations` | **821** rows, **136 characters**, only **298 (36%) carry an `era`** | vocabulary is **social-only** (family/ally/enemy/mentor/rival/superior). No eventive predicate (that is what `events` now carries). 523 era-less rows sit in sections naming no arc. |
| `semantics` | **0 rows** | no per-entity / per-line "what does this mean" classification. (§2b calls the *gate* a red herring; the *goal* still wants a meaning layer — see R1.) |
| `edges` | 35,026 rows, only **6,543 typed (19%)**, 28,483 untyped `mentions` (81%) | a concordance, not a typed graph. |
| temporal keys in `facts` | `arc` 431 · `date` 374 · `anime episode` 185 = **990 lines (<1% of 48,572)** | only events+`arc_index` now carry "when"; a standing-state line still has no time. |

**Honest answer: tier-0 indexing is 100% (48,572/48,572 lines in a chunk) and
event placement is ~94%, but D5 reachability is *not* met (tier 1 ~92–97%; the
2026-09-05 verbatim re-run held at **97.2%** on ~400 distinct probes (≈0.8% of lines), unchanged from the 2026-09-03
baseline of 96.8% within sampling noise — D5 still unmet, an exhaustive tier-1 has never run) and we are not at 100% comprehension.** The residuals above
are the distance to the goal.

---

## 3. What remains, in priority order

Each item is a *build* (new or widened extractor / index), gated the same way
the phases were: council pass before a big one, the CUDA-first GPU rule for any
LLM batch, the four standing gates re-run, and a `comprehension:` commit of the
named paths. "Do not create a third corpse" (§2c) applies: every new table ships
with the door that reads it.

### B5 — cross-page agreement: **diagnostic + key-refinement, not a demotion gate**
(spotted-check done 2026-09-05 — *the "first, above R1–R5" call is superseded*)

With D6 tautological (Step 1: `temporal` reduces to `arc_index IS NOT NULL`, the
same signal that placed the row), **cross-page agreement is the only non-
tautological placement signal.** It is half-built (`gate.cross_page_agreement` +
`continuity --triage`). The A5 split (GATE.md) shows the 107 disagreements
(27.4% of 390 multi-page groups) are driven by the **995 section/citation-backfill
rows** (98/107 touch a section-placed row; mixed groups disagree at 35.6% vs
pure-arc-named 10.5%).

**Council round 2 + the spot-check (`COUNCIL_b5-premise.md`) re-scoped B5.**
The premise — *adjudicate the section rows against the arc-named majority, demote
the loser* — **fails the empirical test.** Grounding the 9-arc chapter table and
classifying all 107 with a chapter-in-range oracle:

| Class | Groups | Share | What it actually is |
|-------|--------|-------|---------------------|
| Repeat-encounter (every row's chapter validly inside its *own* arc) | 60 | 56% | the `(verb, subject, object)` key is **too coarse** — it merges the same pair genuinely spanning arcs (Gojo *fights* Jogo in Fearsome Womb, vs. Mahito, *and* Shibuya). No single right arc → **nothing to demote** |
| Out-of-range row | 23 | 21% | almost all **arc-boundary artifacts** (ch 53 just past Kyoto, ch 222/269 around Shinjuku); only ~2 non-nearest. Likely correct filings |
| No chapter signal (both sides synopsis sections) | 24 | 22% | unjudgeable mechanically; a raw-wiki read (R1's job) |

**~0 of the 107 are unambiguous misplacements.** So B5 is **not** a corrective
gate — one that demoted the "loser" would demote legitimate multi-arc events and
amplify the key's coarseness. Re-scoped:

1. **Diagnostic, not corrective.** Surface the repeat-encounter + boundary groups
   to a human; `continuity --triage` already lists them. No `event_disagreements`
   overwrite, no confidence demotion.
2. **Refine the key.** Add a chapter/temporal component to the grouping key so
   "the same pair in different arcs" stops reading as a contradiction. This is
   the real fix the 60 repeat-encounters point at.
3. **The 107 stay a corpus** (91 two-sided) for R1's per-line meaning index, not a
   gate target.

The **105/154 sibling-propagation** lead (copy a placed twin's `arc_index` onto an
unplaced row) is now **deprioritized**: if the section rows are mostly
repeat/boundary noise, propagation copies that noise onto ~105 more rows. Hold it
until the key is refined and the 24 unjudgeable are read.

### R1 — the per-line / per-beat *meaning* index (the load-bearing one)

The goal's core: given a script line (which is the wiki's prose), say **what it
means** — its semantic class (event / standing state / trait / trivia), whether
it is an event, its participants, and its `arc_index` (timeline position).
Today the understanding is keyed to *sections and events*, not to the *line a
writer actually types*. This closes the "understand what each thing means" half
of the goal and is the consumer the `semantics` corpse was meant to serve.
Clone the `events.py`/`relations.py` pattern (verbatim-quote verified, alias
resolved, FK-stable); read by a new `meaning` door a writer can call on a line.
Bounded GPU batch; the frozen set is a harvest of real script lines, not an
invented gold.

### R2 — abilities to full character coverage

Widen `abilities` from 94 characters to the full character population: every
character page with an `Abilities and Powers` section gets its techniques/
traits/items, and a character with **no** such section is explicitly marked
"no abilities" (so absence is a recorded fact, not a silent miss). Same
extractor, `--scope corpus`, the CUDA-dedicated GPU.

### R3 — relations: era on the 523 + eventive predicates

(a) attach an `era` to the 523 era-less `relations` rows where the section names
an arc or carries a chapter/episode citation (the free placement signal R1's
axis already computes); (b) add the eventive predicates ("X fought/killed/saved
Y") as relations that **reference the `events` row**, so the social graph and
the event graph are one. No new model where the axis already answers.

### R4 — place the 154 unplaced events (the plan's inference residue)

The 154 `arc_index IS NULL` rows are the one place the design reserves
inference. A bounded, per-row inference pass (the Qwen GPU, dedicated) files
each under its best-supported arc with a quoted justification; a row the wiki
gives no signal for stays NULL *as a recorded standing state*, never a guess.
Updates `TIME_AXIS.md`'s residue list and the gate's placement tally.

**Diagnosis (2026-09-05, Step 2):** all 154 are *genuine narrative residue*,
**not** a second predicate gap. By page type: character 99, chapter 38,
character_synopsis 11, location 4, technique 2. **0** of the 154 sit on a page
that carries a real arc position (a placement signal the inferer *should* have
used would surface here; none do) and **0** sit in an arc-named section.
- 116 are on **non-placement pages** — character `Overview`/`History`,
  location, technique, character_synopsis — whose prose is eventive but names
  no arc to anchor to.
- 38 **rows** (across **17 `Modulo Chapter N` docs**) are on chapter pages
  (residue placement: the wiki does not file them under an arc) in
  `Plot Details`/`Summary`.
- Data-quality flag: several `Modulo Chapter N` pages carry non-JJK names
  (e.g. "Simurians", "Naunax", "Dabura Karaba") — likely a crawl/translation
  artifact; worth a separate look before R4 inference is spent on them.
So R4's remaining work is *filing* residue, not a new verb/placement rule.

### R5 — typed edges (optional, lowest value)

Convert the 28,483 untyped `mentions` toward a typed graph where the infobox
already types the relation. Cheap where the signal is free; deferred — it does
not advance the goal as directly as R1–R4.

**Order:** R1 (the goal's core — per-line meaning index; full council) → R2 ∥ R3
(coverage, independent) → R4 (residue) → R5. **B5 is no longer "first."** The
spot-check showed the cross-page signal is dominated by key-coarseness (60% repeat-
encounters) + boundary noise (21%), so it is a **diagnostic + key-refinement** that
feeds R1 (its 107-group corpus and the refined `(verb, subject, object, chapter)`
key are inputs to the per-line meaning index), not a gate that runs ahead of it.
R4's sibling-propagation stays held (it would copy the same noise).

---

## 4. Standing requirements (unchanged, apply to every R)

- **Council before a big build** (5 advisors → 5 peer reviews → verified
  ledger), recorded under `reports/comprehension/COUNCIL_<name>.md`.
- **GPU device rule (CUDA first):** the 27B Qwen model owns the card for any
  LLM batch — stop the `:8000` API (or run it `SCRIPTENGINE_DEVICE=cpu`) and
  confirm ~7 GB free before launching; never run the extraction LLM on CPU as a
  workaround. The `:8000` API itself: CUDA if the card is free, else CPU — with
  one exception, a **short, bounded `:8000` probe in a Qwen quiet window** may
  borrow the ~7 GB of pre-reserved headroom (embedder+reranker load lazily, ~5.3 GB)
  while Qwen idles between prompt bursts (verified 2026-09-05: a 400-probe ran to
  97.2% with Qwen alive throughout; check Qwen's health after and restore the CPU
  `:8000` steady-state). Not for `events-extract` / heavy LLM batches.
- **Four standing gates re-run after each R:** pytest (1,202), span-recall
   jjk (48,572/48,572, rc=0 — **tier 0 only**; the tier-1 reachability sample is
   separate — verbatim re-run 2026-09-05 on GPU `:8000` = **97.2%** (478/492 new rows; ~400 distinct probes ≈ 0.8% of lines),
   unchanged from the 2026-09-03 baseline of 96.8% within noise; D5 still unmet — an exhaustive tier-1 has never run), eval jjk (24/24),
   canon-run opm (10/16 · 236/236 · 79.0%). `span-recall` after any index;
   `audit` before any index.
- **Commit:** branch `character-scoped-questions`, named paths only, author
  `nikhiljusthere <nikhil.shrivastava003@gmail.com>`, prefix `comprehension:`,
  no push. `series/` is gitignored; dated `reports/` dirs untracked.
- **No third corpse:** a new table ships with the door that reads it.

## 5. Definition of "100% comprehension" (so the goal is checkable)

Not "every line has an arc" (that manufactures false precision on the atemporal
two-thirds, §2c). It is: **every line a writer serves is classified (event /
standing state / trait / trivia), every event carries a participant set and —
where the wiki names one — an `arc_index`; the cross-page and continuity checks
return zero *interaction-verb* violations; and a writer can ask, of any line,
what it means and where it sits.** R1 is what makes the first clause true; R4
the second; the gate + `continuity` the third.