# FACT LAYER COUNCIL — full record and verdict (2026-10-07)

Council run per `plan/FACT_LAYER_COUNCIL_BRIEF.md`, **strictly sequentially**: 5 advisors one at a
time, then 5 peer reviewers one at a time (anonymised), then the chairman. No two agents ever ran
concurrently; each saw a fresh context and no other's answer.

- Question (verbatim from the brief, sections A-F given to every advisor):
  **"What is the best way to make the event-labelled windows a COMPLETE, verifiable record of
  every fact the wiki text states (the owner's 'complete MCU brain'), fix every window already
  labelled and reviewed, and keep the result flawless and checkable — given the proposal in
  section D? Accept, amend, or replace each part of the proposal; name what is missing; give the
  order of work and how each step is verified."**
- Anonymisation map for the peer-review round (randomised so no positional bias):
  **A** = Expansionist, **B** = Outsider, **C** = Contrarian, **D** = Executor, **E** = First Principles.
- Ownership rule honoured throughout: `tools/train/big_flags.py`, `plan/BIG_REVIEW_PATTERNS.md` and
  `tools/train/label_hints.py` are Claude-only. No advisor or reviewer edited them; where a change
  is needed it appears below as a **proposal for Claude**.

**Grounded context the orchestrator verified in the tree before convening** (so the advisors argue
from facts, not assumptions):

| fact | where | status |
|---|---|---|
| `check()` compares coverage with `q in sent or sent in q` and has **no quote-length cap** | `tools/train/big_flags.py:197` | verified |
| `sentences()` filters `len(s) > 20` and splits only on terminal punctuation | `tools/train/big_flags.py:88` | verified |
| `relations` PK is `(character, other, relation)` — no `era`, no qualifier column | `scriptengine/stores/facts.py:1536` | verified |
| `save_relations` reads only `other/relation/era/section/quote`, truncates quote at 400 chars, and `DELETE`s every row for a character before inserting | `scriptengine/stores/facts.py:1589-1634` | verified by the orchestrator AND independently by advisor 4 and reviewers 2/4 |
| `relations_of(character, both_ways=True)` returns rows verbatim — no direction inversion marker | `scriptengine/stores/facts.py:1552` | verified |
| `events` table takes any verb; `extra_verbs: [defeated, escaped, captured]` already wired per-wiki | `facts.py:1770`, `series/marvel/overrides.yaml:208` | verified |
| measured event quality: P .769 / R .532 / F1 .629 on 96 reviewed windows; recall is the weak side | `tools/train/eval_hints.py`, `plan/WINDOW_METHOD.md` | verified |
| b7-b806 reviewed, ~70% needed correction; 13 of 98 already-OK rows still needed a change | `plan/BIG_REVIEW_PATTERNS.md` header | verified |

---

# ROUND 1 — THE FIVE ADVISORS

## 1. The Contrarian

## The fatal flaw: the completeness proof is a no-op that the model being measured can switch off

Section D §3 rests entirely on turning MISS? into a hard coverage gate. Read line 197 of
`tools/train/big_flags.py`:

```python
if cues and not any(q in sent or sent in q for q in quotes):
```

`check()` has **no quote-length check anywhere** — I grepped every `quote` reference: line 99
unpacks it, 189 collects it, 197 compares it, 237 prints it. So coverage is satisfied by `sent in q`.
One fact row with a 400-character quote covers all 40 sentences inside it. The 27B will discover
this in window one and start quoting paragraphs, because paragraphs are the cheapest way to hit a
coverage number. You will get 97% "coverage" from windows where the model emitted three rows and one
paragraph dump. That is not a gate; it is a metric the labeller optimises against. And `sentences(t)`
(line 88) filters `len(s) > 20`, so the systematically-uncovered sentences are exactly the short
declaratives ("She nods.", "He refuses.") where person→place and person→item facts live. D's
coverage rule reports precision about the sentences it kept and silence about the ones it discarded.

## Second fatal flaw: the add-only pass contaminates the gold it is measured against

`series/universal/training/big/big_audit.jsonl` is latest-per-id-wins and `eval_hints.py` scores
against it. Add machine-drafted fact rows to those ids and the gold is now self-graded: every future
P/R number measures the model against its own output. Irreversible, silent, and it poisons the only
evaluation instrument that exists. **Hard rule: facts go to a new file (`big_facts.jsonl`), joined at
read time, never merged into the audit.** Non-negotiable.

Third: "add-only" is false on the input side. Feeding the drafter the window *plus the final
reviewed rows* anchors it to the review's own drops — that is the entire bias we are trying to
remove. Draft from text + procedure; use reviewed rows only as a post-hoc dedup filter.

Fourth, unnamed by D: **`compose_big_set.py --empty-share 0.30` with 75% hard empties (lines 80-86)
becomes unobtainable.** Under reversed step 3, "hard empty" windows now carry fact rows. Either
empties are re-defined as *empty event rows* (a schema-wide semantic change touching the 9B) or the
student trains on a distribution the schema no longer describes. D says the 9B plan is untouched. It
is not.

Fifth: **coreference is a new first-order error source and the schema has no field for it.** Event
rows hide pronouns in the quote; fact rows expose them as `subject`/`object`. Wiki prose is "she",
"his father", "the girl". The R10 "one name per person" invariant must become a mandatory resolution
rule (unresolved antecedent → flag, do not emit).

## The five decisions

**1. Two layers — accept, with a hard amendment.** Two layers is right; `fought`/`met` must not be
stretched (the 9B and match-up reasoning depend on them). But reject the open `other` verb as a
*trained* relation: it is the "forced into silence" problem inverted into "forced into `other`", and
with no promotion mechanism it becomes a junk drawer. `other` goes to a logged, non-training bucket
with a promotion quota, and `other`-share becomes a vocabulary-failure metric (<10% or the vocabulary
is wrong).

**2. Schema — amend hard.** `modality` is not a free tag: closed enum `{actual, planned, attempted,
ordered, claimed, dreamed, hypothetical}`, and **any non-`actual` row must carry `asserted_by` (a
named character) and is never world-truth.** Without that, reversing step 3 makes the brain assert
Loki's lies. `certainty` → closed enum `{actual, reported, apparent, denied}`, not a scalar. Reject
`location` as a bare qualifier — `located_at` with an anchor slot (`resides` / `occurs_at`), or "his
apartment" becomes a decoration on an unrelated row. Split `alias_of` from `disguise_as` (temporary
and intentional; conflating them is a fact error the review already caught, R10). Membership as
`member_of` with `from`/`to`. Gate extension for facts: verbatim quote (keep), **max length, and the
quote must lie inside one sentence** — that is the anti-loophole rule. Ends must be named entities.
`other` verb must appear literally in the quote.

**3. Coverage — replace, don't tighten.** Clause-level, and a sentence counts as covered only if a
row's quote lies *within that sentence's span* **and** the row's subject resolves to a named entity
occurring in that sentence. That requires a new splitter module (not `big_flags.py` — it is
Claude-only and shared with `--repair`) handling `Washington, D.C.`, dialogue, table rows, list
entries, and a narrative classifier that excludes boilerplate. Report coverage as a **measured recall
proxy with its failure modes stated**, never as a pass/fail flag in v1.

**4. Repair of the past.** Drafting model: **27B**, on three grounds — already resident, and it is
the family the 9B student distills from, so fact-vocabulary drift is minimised. Use the 35B only if
a 50-window lane benchmark shows the 27B cannot clear the corpus. **Reject "Claude reviews only the
additions — far cheaper."** False: Claude must read window + additions, additions are 2-3x the row
count, the correction rate on reviewed rows was ~70%, and mechanical checks catch ~80%, not 100% (13
of 98 OK rows still needed a change). Re-reviewing the 806 under expanded rules is *more* expensive,
not less. Budget it as days, and say so. False additions poison a brain worse than missing ones.

**5. Order.** (a) New `fact_schema.py` + `fact_gate.py` + new splitter, no edits to Claude-owned
files. (b) Claude hand-factors a **40-window fact gold from the 96-window eval set, held out** — you
cannot measure precision against nothing. (c) Measure: fact precision/recall, coverage,
coreference-error rate, `other`-share, duplicate rate. (d) Gate the b7-b806 pass on fact precision
≥0.85; stop/rollback = `FACTS_ENABLED=0`, every existing path runs unchanged. (e) Then the sweep.
**Never promise the corpus beyond 14k** — one serialized GPU, 2-3x rows, multi-week; a
half-labelled fact layer with no coverage guarantee is worse than none, because downstream will trust
it. **Unchanged: the 12-verb gold, `big_flags.py`, `BIG_REVIEW_PATTERNS.md`, the 9B plan — except
the empty-share definition, which must be resolved before (b), not after.**

---

## 2. The First Principles Thinker

## The framing is wrong

We are not designing a fact layer. We are deciding **where each dropped fact lands in a schema the
engine already ships.** Read `scriptengine/stores/facts.py` before writing a single word of spec:

- `relations` (facts.py:1536) already has `RELATIONS = (family, friend, ally, rival, enemy, mentor,
  student, superior, subordinate, romantic, creator, creation)` with `era` and `quote`, keyed
  `(character, other, relation)`, read by `relations_of(character, both_ways=True)` (facts.py:1549).
  **"Hope trained Scott" is already a storable, queryable row today: `('Hope van Dyne','Scott
  Lang','mentor')`.**
- `events` (facts.py:1770) takes any `verb TEXT`; the widening mechanism is already wired per-wiki as
  `extra_verbs` — `series/marvel/overrides.yaml:208` already declares `[defeated, escaped, captured]`.
- `abilities` (facts.py:1360) holds `kind`/`acquired`/`reason` per character.
- Aliases are `nodes`/`aliases` (ingest/alias_align.py), locations are `location` type aliases in
  both overrides files. `alias of` and `his apartment` are **graph edges and nodes, not rows.**

So the owner's complaint is not a schema gap. The gap is that `ingest/relations.py` is asked only
over `DEFAULT_SECTIONS = ("Relationships","History")` — a sparring statement in a Plot/Background
section is never read. D invents a parallel fact schema that a brain cannot load. Reject that.

Three more things D misses:

1. **D §2's modality reversal corrupts the negative class.** `compose_big_set.py:40` composes the 9B
   with `--empty-share 0.30` and *hard* empties defined as plans/claims/hypotheticals — exactly what
   step 3 drops. Make them rows and the 9B's negative class becomes mislabeled.
2. **The relations PK omits `era`** while its own docstring says "a relationship that changed is two
   entries." `INSERT OR REPLACE` collapses them. That is a silent fact loss inside the target schema.
3. **D §3's coverage gate cannot be built on `big_flags.sentences`** (big_flags.py:88): `len(s) > 20`
   discards sentences and `(?<=[.!?])\s+` mangles dialogue. A gate on it reports 100% on windows it
   never segmented.

## The five decisions

**F1 — two layers, but not D's two layers.** Events stay byte-identical; `compose_big_set.py` and
b7–b806 gold must not move. Widening one inventory is out (kills hard empties). Facts go into the
three existing tables. The 12-verb gold and the 9B plan are unchanged — that is the point.

**F2 — schema: no new vocabulary, no qualifier bag.** relationship/interaction → `relations`; actions
not in the 12 → `extra_verbs` only if they are genuine plot acts (`helped`, `trained` are relations,
not verbs — that is the A71/R23 fix). Modality: **reject.** Plans and claims stay non-rows; they live
in `quote` and in the chunk the engine already indexes. `certainty`/`location`/`time` are rejected
too — `era` and `section_id`/`time_rank` already carry them. Gate extension: verbatim-quote and
both-ends-resolve copy from `ingest/events.validate_phase1_rows` (events.py:567) and `ingest/relations`
guards; do not touch `big_flags.check`.

**F3 — coverage rule.** A sentence-level coverage *report*, not a gate, until it beats the row gate.
Every row carries `sent_idx` from a new versioned segmenter (`tools/train/seg.py`, which I may write,
with its own tests). Denominator = that segmenter's output. Measured as clause coverage on the 96 gold
windows.

**F4 — repair of the past: replace add-only with whole-window re-label, scoped first.** You cannot
review only additions — there is no gold for them, so `eval_hints.py` has nothing to match, and
additions-only can never delete a wrong fact. Do it on b7–b806 (the only place gold exists), not 14k.

**F5 — order and verification.**

1. Claude hand-writes fact rows for the **existing 96 gold windows** and commits them as gold *before*
   code. Verification: Claude signs them; they are the new eval set.
2. `seg.py` + coverage reporter. Verification: no gate wired yet; report on 96 windows only.
3. Draft facts on those 96 with the loaded 27B (`EXTRACTION_PROCEDURE.md` + a facts procedure).
   Verification: fact P ≥ .60, coverage ≥ .85, **and event P/R unchanged at .769/.532** — any drift is
   the rollback trigger.
4. Extend to b7–b806, whole windows. Verification: event rows diff must be empty on all 806; fact rows
   diffed against Claude by `big_mkfix`.
5. Only then the 14k, and only after the engine can load the rows.

Stop criteria: event metrics move, or review exceeds ~2 days per 806 windows. Unchanged throughout:
`big_flags.py`, `BIG_REVIEW_PATTERNS.md`, `label_hints.py`, the 12-verb gold, the 9B plan.

---

## 3. The Expansionist

## The prize D leaves on the table

D prices the fact layer as a repair job on 14,000 windows. The measured prize is 18.6× larger and D
never costs it: `series/{marvel,mcu}/facts.db` hold **130,970 sections ≥20 words / 150,376,920
chars**. The 14k sample is **8,074,897 chars over 308 distinct pages** — 5.4% of corpus text, **0.11%
of the 279,970 documents**. At the sample's 576 chars/window that is **~260k windows** (86k at the
2,000-char pack), i.e. **200–370 GPU-hours**. Claude-reviewing every one at 1,000–1,500 tokens is
arithmetically dead past ~2–3k windows. So the winning move is not a better labelling run — it is:

**Make the fact layer an engine ingest pass (`scriptengine/ingest/facts.py`), with the 14k windows
demoted from deliverable to calibration/gold set.** That single reframe changes the verification
from "did Claude read it" to "is coverage ≥ threshold, mechanically, over the whole corpus".

Three concrete assets that make it nearly free:

1. **No new table, no migration.** `edges(source_id, relation, target_id, confidence, provenance,
   section)` = 4,039,752 rows; `facts(node_id, key, value, citation)` = 3,796,438; `relations`
   (facts.py:1536) with `relations_of` (1552). `provenance` is already a free-form channel
   (`category:<name>` from `ingest/category_relations.py`). Write facts as
   `provenance="fact:<prompt_version>:<window_id>"`; re-run = `DELETE WHERE provenance LIKE
   'fact:<v>:%'`. **Trap: do not route through `save_relations`** — it is replace-per-character and
   would nuke the 22,700 relations rows `relation_coverage.py` names.
2. **The gate is ~80% built.** `ingest.verbatim.quoted_in`, `relations.known_names` (nodes+aliases
   canon), `verify_save.BAD_END/PLACE_LIKE/SPECIES_LIKE`, `label_single.gate`. A **new**
   `tools/train/big_factflags.py` is *required structurally*, not stylistically:
   `big_flags.check(ev, text)` only ever receives `events`, and that file is Claude-only.
3. **Free recall gold.** `eval/relation_coverage.py` already scores against structure-derived gold
   (every subsection head in a Relationships section) — pure SQLite, no model, no Claude. Baseline the
   8 wikis **before** writing a line.

## F1–F5

**F1. Accept two layers; reject one widened inventory; amend the destination.** Events stay 12-verb →
9B gold unchanged (`compose_big_set.py --reviewed --empty-share 0.30`, hard empties intact). Facts go
to `edges`/`facts` + a new auditable `window_facts` table. Amendment: relations are **per-wiki data**,
not code — `relation_sections:`/`category_relations:`/`extra_verbs:` (overrides.yaml:208) are the
project's own idiom.

**F2.** `{s, r, o, quote, kind: plot|production, qualifiers:{modality, certainty, time}}`. Closed list
in a new `plan/fact_relations.yaml` with `inverse`/`symmetric`; recurring `other` verbs promoted by a
**measured** threshold (≥0.5% of rows over the 50-window calibration), not judgement. Entity-valued
qualifiers become rows, not strings: `location`, `member_of`, `alias_of`/`posed_as`/`revealed_as` as
edges — this kills R10 structurally instead of by "use one name". **Non-node ends (places, items,
orgs) must NOT be dropped as they are in events**; they go to `facts` keyed by the subject.

**F3. Sentence = `ingest.windows.sentence_spans()` (the pinned grid, mirrored to the chunker and
test-pinned), **not** `big_flags.sentences()`.** Covered = some row's `quote_grid_span` inside the span
(reuses the G1 straddle guard). Tag-exempt closed set: dialogue, list/infobox furniture,
production/BTS, citation, `below_floor` (<6 words, reusing `panel_sentences`). Number: **coverage =
covered / panel_sentences ≥ 0.98 per window**, with the uncovered list printed per window. Every
uncovered sentence is a repair target — coverage is the **recall oracle**, making R measurable without
a human gold.

**F4. Three tiers.** **T0 (free, no GPU, today):** run coverage over the 806 reviewed windows' existing
rows; Claude reads only the uncovered-sentence list. T1: add-only 27B pass on the 806, diff-gated,
Claude reviews the diff. T2: corpus. **Routing is the whole game:** auto-accept a window iff 0
uncovered ∧ 0 `other` ∧ 0 hedge rows; everything else to Claude. 27B drafts (already resident; no 35B
switchpoint round-trip). Never regenerate event rows.

**F5. Order + verification.** (1) `big_factflags.py` + `fact_coverage.py` → verify against history:
the uncovered lists for the sparring/joining/call windows must reproduce A71/R4/A67, whose `why`
fields are already in `big_audit.jsonl`. (2) `FACT_SCHEMA.md` + `fact_relations.yaml` → verify: every
owner drop-class maps to ≥1 relation; Claude approves. (3) baseline `relation_coverage` on 8 wikis.
(4) `label_facts.py` on 50 windows → 100% verbatim quotes, 0 unresolved ends, 0 out-of-registry
relations, ≥45/50 at coverage ≥0.98. (5) T1 add-only over the 806. (6) `ingest/facts.py`; verify
provenance-prefix idempotence + a 20-question "who trained X" set answered from `relations_of`. (7)
Corpus campaign with auto-accept — enable the tier only after its precision is **measured** on 100
human-read windows. **Rollback:** `window_facts` is a new file; delete it. **Unchanged:** the 12-verb
gold, `EXTRACTION_PROCEDURE.md` step 3, the 9B plan, `big_flags.py`, `BIG_REVIEW_PATTERNS.md`,
`label_hints.py`, owner files.

---

## 4. The Outsider

Four things in this brief are presented as settled. None of them are. I checked the store the facts
would have to live in, and it cannot hold them.

**Verified in `scriptengine/stores/facts.py`:**

1. `save_relations` (line 1586) reads exactly five string fields — `other, relation, era, section,
   quote` — and every other dict key is **silently discarded**. D's `modality`/`certainty`/`source`
   qualifiers do not survive ingest. You would burn multi-day GPU time producing 2–3× rows and write
   them into a void, with no error anywhere.
2. `INSERT OR REPLACE` into `PRIMARY KEY (character, other, relation)` (line 1540). "Hope trained
   Scott (planned)" and "Hope trained Scott (actual)" are the same key. One silently vanishes. D §2's
   modality reversal is not storable as designed.
3. `relations_of(..., both_ways=True)` (line 1562) returns the row verbatim — no inversion marker. The
   docstring says "who is Gojo to": symmetric by assumption. Every new relation D proposes — trained,
   mentored, recruited, persuaded, betrayed-by — is **directed**. Query Scott, get back
   `character=Hope, relation=recruited`, and any consumer normalizing to (query, counterpart) asserts
   "Scott recruited Hope." A symmetric store cannot hold an asymmetric fact layer. The 12 verbs are
   mostly self-reversing, which is exactly why this has never bitten before.
4. `save_relations` `DELETE`s every row for that character before inserting (line 1609). D §4's
   "add-only pass" is additive in the JSONL and **destructive in the store** unless every additive run
   re-writes the union.

**The naive question nobody asked:** the engine has no canon field. `era` and `section` are the only
annotation slots on `relations`. The Marvel corpus mixes MCU films, main continuity, comics,
alternate-continuity. "Every line is a fact" without a canon discriminator means the brain answers
with cross-continuity contamination stated as truth. The owner said "it was in a movie/series or
manga/comic" — that sentence *is* the canon tag, and it has nowhere to go. `era` is its home; don't
invent `source`.

**F.1 — Two layers, amended.** Keep D's two layers. The 9B is being trained on precisely-labelled
conflicts; widening that inventory corrupts it and match-up reasoning. But the split must be
*physically* two corpora with disjoint prompts and disjoint labels, never one labeller reading a mixed
prompt — otherwise train/serve skew is silent.

**F.2 — Schema.** The relation list is fine and I'd keep it verbatim. Non-negotiable additions: a
qualifier payload column (or side table), a PK discriminator, **direction metadata**, and `era`
carrying canon. Representing aliases via `alias_align.py` nodes, not symmetric `relations` rows,
sidesteps finding 3 for the identity group. The `other` relation name collides with the `other`
*column* name in the same table and the same ingest dict — name it `other_verb`. The existing gate
extends by requiring every fact row's quote to be verbatim ≥12 chars, ≥1 named character per endpoint,
and — new — *endpoint direction must be stated in the row*, not inferred.

**F.3 — Coverage.** Sentence coverage is the wrong unit and will manufacture false confidence: one
sentence states three facts and gets one row; one states zero and gets forced into `other`. Measure
**character coverage** — the fraction of each window's non-whitespace characters inside a quoted span
or an explicit tag. It is splitter-independent, cannot be gamed by row-merging, and is one regex.
Also: `big_flags.py`'s `sentences()` filters `len(s) > 20`, so any gate reusing it structurally
*cannot see short declaratives* — "He is her student" is exactly the owner's complaint, and it lives
near that boundary. Use an independent splitter with no length filter.

**F.4 — Repair of the past.** The add-only design is right at the file layer and wrong at three other
layers. Do **not** feed Claude's R4/A67/A71 reason strings to the labeller as hints: that teaches
conclusions, not criteria, and will hallucinate facts elsewhere. And say plainly what nobody has said
— *flawless is not an achievable acceptance criterion for 14k windows.* Mechanical checks catch ~80%;
13 of 98 OK rows still needed a change; b7–b806 took a day for 5.7% of the corpus. Replace "flawless"
with a number: fact-layer precision ≥ .769 (today's event P), character coverage ≥ 0.90, Claude
review on a fixed random 150-window sample of the repair for a measured error rate. That is a
checkable promise; "flawless" is a multi-week promise that ends in silent drift.

**F.5 — Order and verification.**

0. **Store first.** Extend `save_relations`/`relations` for qualifiers, direction, PK discriminator,
   canon; add an end-to-end test writing Hope/Scott and reading them back. Until a round-trip
   survives, no extraction code is worth writing. This is where projects like this die.
1. Freeze v1 gold to a read-only snapshot, hash it. Acceptance numbers written down *before* any
   schema.
2. Write the fact-row JSONL schema + validator + character-coverage gate as **new** files.
3. Pilot on 3 windows by hand, including "seemingly killed", alias, "member of".
4. Measure on the existing 96 reviewed windows. **Verify**: fact P, fact R, character coverage, zero
   qualifier-loss round-trip. Gate to proceed.
5. Only then the 9B sets: recompute hard-empties under v2 semantics or `compose_big_set.py --reviewed
   --empty-share 0.30` ships a poisoned set — the ~75% "hard empties" in v1 gold are mostly v2 facts.
6. b7–b806 repair, then the rest, reviewed by sample not exhaustively.

**Rollback:** if fact precision < .70 or character coverage < 0.85 at step 4, revert the *extractor*,
keep the store changes and the gate. **Unchanged:** the 12-verb gold b7–b806 (immutable,
`prompt_version`-tagged), `big_flags.py`, `BIG_REVIEW_PATTERNS.md`, the review cursor, all protected
files. Report the store findings to Claude now — they change what step 0 means.

---

## 5. The Executor

## Executor verdict

Measured baseline I need everyone arguing from (I computed it, not guessed): across the 806 reviewed
windows, **3.2 final event rows/window, 4.77 narrative sentences/window, and only 34.7% of narrative
sentences are touched by any row quote**. 318/806 (39%) are empty after review. `compose_big_set`
wants `--empty-share 0.30` with 75% hard empties. So the fact layer is not a nice-to-have; today's
layer covers a third of the prose.

**Monday morning, first command:** nothing GPU. Write `plan/EXTRACTION_PROCEDURE_V2.md` +
`tools/train/fact_gate.py` + `tools/train/fact_coverage.py`, run them over the 806 gold windows to
publish the missing-sentence report. Claude can verify a doc and a diff without a GPU hour.

### F1 — Two layers. Accept D, unchanged.

Widening the 12-verb inventory corrupts the 9B target: `eval_hints.keys()` matches on
`(subject,verb,object)` and `compose_big_set --reviewed` trains on those rows; a 60-verb mix makes
P/R uninterpretable and match-up reasoning ("who would win") reads `trained` as a conflict. Decisive
engineering fact: the engine **already** accepts fact rows with zero code — `facts.py:1589
save_relations` reads `other/relation/era/section/quote` from a dict and keys on
`(character,other,relation)`. `relations_of()` answers "who trained Ant-Man" today, empty. Fact rows
land in `relations` as-is.

### F2 — Schema. Accept with three hard additions.

Row: `{"subject","relation","object","qualifiers":{modality,certainty,location,time,type},"quote","sent_i","type":"plot|production"}`.

1. **Per-relation end-type whitelist.** The event gate's `BAD_END` species/crowd rules and "places
   only for arrived/departed/escaped" must NOT apply to facts: `resides at` needs a place object,
   `used` needs an item, `trained` needs no person. Reuse `draft_v2.check_rows` +
   `verify_row_wiki.Wiki.resolve`, but index the allowed end types by relation. Otherwise the gate
   deletes the fact it exists to keep.
2. **Qualifier storage.** `relations` has no column for modality/certainty/location. Add
   `tools/train/fact_vocab.py`-side tally plus a new `fact_qual(character,other,relation,qualifiers
   JSON,quote)` table in a new store — do not ALTER core `relations` while it holds 131k sections of
   other series.
3. **`empty_class` per window**: `hard_empty` / `nonfact_only` / `fact_bearing`. Reversing D's step-3
   drop rule turns most of today's empties non-empty, which breaks the 9B `--empty-share 0.30` design.
   This field is what keeps it breakable-free.

### F3 — Coverage. Accept, but the rule is clause-level and the metric is gated.

`big_flags.sentences()` splits only on terminal punctuation and drops ≤20 chars; "Hope trained Scott
and later met him" is one sentence, two facts. Write a deterministic regex clause splitter (no new
dependency) and an allowlist tag set: dialogue, apposition, attire/appearance aside, list header,
transitional/deictic, editorial/behind-the-scenes, redundant restatement. **Verified target: ≥90% of
non-allowlisted clauses covered by ≥1 row quote, measured on the 806 gold windows** (baseline 34.7%).
Report per-window misses as exact clause text — it is the MISS? trick turned into a worklist, and it
is what makes Claude's review bounded.

### F4 — Repair of the past. Amend D to uniform add-only.

5,405 windows already carry event rows; re-deriving them risks regressing .629 and burns the GPU on
work Claude will just re-correct. Add-only for all 5,405 (806 reviewed ≈ 1 h; rest ≈ 8-12 h), event
rows copied byte-identical into a new `labels_v2_facts.jsonl` keyed by `id`, one line per window,
resumable by id-set. 35B is stopped and the 27B is loaded → **no model switch, no SWITCHPOINT entry**.
The remaining 8,595 unlabelled windows get one full v2 pass, and only after the pilot gate passes.
Do not extend `label_single.py`; write `label_facts.py`. Touching it costs me the baseline
re-measurement.

### F5 — Order, verification, stops.

1. Schema v2 doc → verify: a mapping row for every drop class in §C, 0 unmapped.
2. `fact_gate.py` + `fact_coverage.py` + `tests/test_fact_layer.py` → pytest green; coverage baseline
   on 806 published.
3. Pilot 50 gold windows, add-only → verify fact precision hand-scored on 20, event rows
   byte-identical (sha), coverage ≥90%.
4. **Stop rule:** if coverage <80% or fact precision <0.75 after two prompt revisions, write evidence
   to `FACT_LAYER_PROPOSALS_FOR_CLAUDE.md` and halt. Do not launch the fleet.
5. Run all 5,405 → verify every 200: parse-fail 0, `other`-verb tally, coverage report, commit
   progress log with pathspec.
6. Build a 200-window fact gold set so Claude reviews additions only; `other` verbs promoted to
   vocabulary from the tally, not by taste.
7. Then the 8,595. **Unchanged:** 12-verb gold, `compose_big_set`, `big_flags.py`,
   `BIG_REVIEW_PATTERNS.md`, owner's files. `relations` table untouched.

---

# ROUND 2 — THE FIVE PEER REVIEWS (anonymised)

## Reviewer 1

Verified the load-bearing claims myself: `save_relations` (facts.py:1589) reads only 5 keys,
`PRIMARY KEY (character, other, relation)` omits `era`, it DELETEs per character, and
`relations_of(both_ways=True)` returns rows verbatim with no inversion. `big_flags.check` line 197
really is `sent in q` — so C's paragraph-quote loophole is real, and `sentences()`' `len(s) > 20`
really does blind the gate.

**1. Strongest: C.** It is the only response that attacks the *instrument* rather than the extractor.
Two of its findings are verified lethal: (a) `sent in q` makes coverage a metric the labeller games —
the cheapest path to 98% is one paragraph quote per window, which is exactly the "forced into silence"
failure reappearing as "forced into quotes"; (b) mixing drafted rows into `big_audit.jsonl` makes the
only evaluator self-graded. Its "quote must lie inside one sentence" is the correct anti-loophole
invariant, and its held-out 40-window fact gold is the step everyone else skipped. B is a close second
on store forensics (its five verified findings are all true) but leads with diagnosis and
under-specifies the mechanism.

**2. Biggest blind spot: E.** "Don't build a fact schema, the engine already has one" is the one move
that can silently deliver nothing. `ingest/relations.py` reads only `DEFAULT_SECTIONS =
("Relationships","History")`, so no marginality: extending the section list is re-mining, not proof.
Its "reject modality outright" leaves plans/claims invisible — which is the owner's actual complaint,
restated. It also breaks its own stop rule: step 3 demands event P/R unchanged while step 4 re-labels
whole windows, and hand-writing gold for 96 windows before any code is an unfalsifiable schedule.

**3. All five missed:** none distinguished *measured* recall from *claimed* recall. Every response
treats coverage as recall, but coverage only bounds recall under an independently verified splitter —
C alone flags this, and even C still gates on it. Also missing: whether the 9B student can consume a
second layer at all (nobody tests a two-layer batch); that 806 reviewed windows are the *only* place a
fact precision can be computed, so sampling must come from b7–b806, not random (B alone notices); and
none costed the corpus honestly (A alone gives numbers, and only A flags Claude-review as
arithmetically dead past ~3k windows).

## Reviewer 2

**1. Strongest: B.** It did the one thing the others skipped: read the destination before designing the
payload. Its four store findings are verified and each one **changes the plan**, not just annotates it
— `save_relations` discards `modality`/`certainty` silently; `PRIMARY KEY(character,other,relation)`
collapses planned-vs-actual; `relations_of(both_ways=True)` inverts directed facts ("Scott recruited
Hope"); the DELETE makes "add-only" destructive at the store. That justifies "store first, no
extraction code until round-trip survives," plus the canon-in-`era` point and replacing "flawless"
with three numbers. C is a close second (the `sent in q` loophole and self-graded gold are both real
and neither is mentioned elsewhere).

**2. Biggest blind spot: E.** It rejects the very thing the owner asked for. "Modality: reject. Plans
and claims stay non-rows" reinstates the silent drop; `certainty`/`location`/`time` likewise. It
assumes facts map onto the 12 social relations — `mentor` covers "trained", but `recruited`,
`persuaded`, `wielded`, `member of`, `located_at` have no home, and the `era` PK collapse it *notices*
is never fixed. It also demands whole-window re-label, discarding add-only safety and re-burning 5,405
windows.

**3. All five missed:** A consumer and a CI gate. `eval_hints` keys on `(subject,verb,object)`.
Nothing in any answer makes fact P/R or coverage a standing test — the layer ships unmeasured forever.
Cross-page conflict policy: 308 pages, repeated and contradictory facts; nobody specifies dedup,
contradiction, or which quote wins. Who audits the coverage gate: C proves the gate is gameable but no
answer proposes an independent audit of gate results on a held-out set.

## Reviewer 3

**1. Strongest: C.** It alone found the two killers by reading code instead of guessing. C verified
`big_flags.py:197` — coverage is satisfied by `sent in q`, so one paragraph-long quote "covers" 40
sentences; a coverage gate without a quote-length/one-sentence constraint is a number the labeller
learns to game in window one. C also found `sentences()` at line 88 drops ≤20-char spans, so the
metric is silently blind exactly where short declaratives live, and that the add-only pass written into
`big_audit.jsonl` self-grades the only eval instrument. Both claims check out. C's follow-ons
(coreference as a new error class with no field for it, `--empty-share 0.30` becoming unobtainable) are
real and none of the others found them.

**2. Biggest blind spot: D.** D's decisive claim is that fact rows "land in `relations` as-is" because
`save_relations` reads the five keys — verified, but D reads that as *permission*.
`save_relations` DELETEs all of a character's rows first (`facts.py:1609`), so an add-only pass is
destructive in the store, and the PK `(character,other,relation)` (line 1540, confirmed) collapses
"trained Scott (planned)" and "(actual)" into one row. D's whole F2 step 2 proposes a side table as
if the collision weren't there; the collision is upstream of it. D is also the only response that
reuses `big_flags.sentences()` — the exact splitter C and E flagged as unusable — while still claiming
a 34.7% baseline from it.

**3. What all five missed.** Nobody computed the arithmetic that decides feasibility: 14k windows ×
~2–3× rows on one serialized GPU, against the 806-window review rate already measured at one day for
5.7%. Only A prices the corpus (260k windows) but uses it to *escape* the sample rather than to argue
sequencing. Second, nobody verified whether `relations` is even the right destination — A points at
`edges`/`facts` (4.0M/3.8M rows) and nobody rebuts it. Third, B's canon-contamination point (no canon
field; `era` as the only slot) is raised and dropped by everyone else — cross-continuity contamination
stated as fact is arguably worse than a missing fact, and it belongs in the row schema, not just the
store.

## Reviewer 4

**1. Strongest: B.** It is the only response that verified the destination before designing the
payload. I confirmed in `scriptengine/stores/facts.py`: PK is `(character, other, relation)` with no
`era` (E independently found the same collapse), `save_relations` DELETEs every row for a character
then inserts, and only `other/relation/era/section/quote` are read. B's four findings — qualifier loss,
planned/actual key collision, direction blindness in `relations_of`, destructive "add-only" — are
exactly the failure mode D's proposal walks into. Its store-first ordering, gold-freeze-before-schema,
and explicit "flawless is not an acceptance criterion" (replace with numbers) are the right spine.

**2. Biggest blind spot: D.** F1 asserts the engine "already accepts fact rows with zero code — fact
rows land in `relations` as-is." That is false and self-contradicted by its own F2.2. Every asymmetric
relation B describes gets stored symmetrically and read back as its inverse; qualifiers vanish
silently; F5's "relations table untouched" leaves the layer unqueryable. D is also the only response
claiming a baseline ("34.7% of narrative sentences touched") without naming its segmenter — and its
own C-and-E peers prove that segmenter drops short declaratives.

**3. What all five missed.** `save_relations` truncates quote to **400 chars**
(`row.get("quote")[:400]`). Any quote-long fact row is mangled in store; none of the five flagged it.
The window-label universe and the page-ingest universe (`ingest/relations.py` over `DEFAULT_SECTIONS`)
are different schemas keyed on different IDs; nobody designed the join or the read path that makes the
brain *use* these rows. Nobody budgeted Claude's review against the 2–3× row explosion except C, and
nobody treated `relation_state`/`prompt_version` as implying full re-extract per revision — so "add-only"
may be unachievable in the store even where it is true in the JSONL.

## Reviewer 5

**1. Strongest: C.** C is the only response that audited the gate itself instead of assuming it. Two
verified defects kill D §3 as written: `big_flags.py:197` — `if cues and not any(q in sent or sent in
q for q in quotes)` has **no quote-length cap**. `sent in q` means one 400-char quote covers 40
sentences. Coverage becomes a metric the labeller minimizes by dumping paragraphs. I verified this.
`sentences()` at line 88 filters `len(s) > 20`, so exactly the short declaratives that carry
person→place facts are invisible to the denominator. C's second and third findings are also unique and
correct-in-kind: `big_audit.jsonl` is latest-per-id-wins, so adding machine drafts into those ids makes
the gold self-graded — irreversible, and it kills the only measurement instrument. And "add-only" is
false on the *input* side: feeding reviewed rows to the drafter anchors it to the review's own drops.
Its coreference-first-order-error point and the `--empty-share` contradiction are the two things nobody
else caught cleanly.

**2. Biggest blind spot: E.** E's whole argument is *storage exists therefore no schema is needed*, and
it rests on the store being able to hold the target facts. It isn't: `save_relations` reads five keys
and discards the rest, `PRIMARY KEY (character, other, relation)` collapses modality variants, and it
`DELETE`s per-character before insert. So E's "already storable, queryable today" is false for precisely
the rows the owner complained about — `('Hope','Scott','mentor')` fits, but "Hope *planned* to train
Scott" does not, and E answers that by *rejecting modality entirely*, which is re-introducing the drop
the owner is paying to fix. E also drops the qualifier dimension wholesale and never prices what
`ingest/relations.py`'s section filter misses across a corpus where facts live in Plot/Background, not
Relationships.

**3. What all five missed.** Nobody wrote down the unit cost. All five propose gold sets, gates, and
sweeps but none gives wall-clock/GPU-hour estimates per phase with the 2–3× row multiplication — so the
"order of work" is unexecutable as written. Nobody addressed the 2,000-char pack vs 576-char window
split, which changes the sentence denominator and makes windows non-comparable across the corpus.
Nobody raised duplicate/overlap windows — `big_flags.py` itself flags DUP and OVERLAP (b365 = tail of
b188). Add-only passes will double-count facts across overlapping windows and inflate coverage. No one
specified what happens to windows whose text the 27B cannot parse, nor the failure mode when fact rows
reference entities absent from `nodes` — an unresolvable `other` silently becomes a fact that can't be
queried, which is the "complete brain" promise failing quietly.

---

# ROUND 3 — THE CHAIRMAN'S VERDICT

All five advisors' load-bearing claims were independently re-verified against the tree before writing
this verdict. The ones that decide the plan:

- `scriptengine/stores/facts.py` ~1536: `relations` PK is `(character, other, relation)` — no `era`,
  no qualifier column.
- `save_relations` reads only `other/relation/era/section/quote`, **truncates quote at 400 chars**
  (`row.get("quote").strip()[:400]`), and `DELETE`s every row for that character before inserting.
- `relations_of(character, both_ways=True)` returns rows verbatim — no inversion marker.
- `tools/train/big_flags.py:88`: `sentences()` filters `len(s) > 20`; line 197: `if cues and not
  any(q in sent or sent in q for q in quotes)` — no quote-length cap, so `sent in q` lets one 400-char
  quote "cover" forty sentences.
- `series/{marvel,mcu,jjk,csm,opm}/overrides.yaml` all already declare `extra_verbs: [defeated,
  captured, escaped]`.
- `scriptengine/ingest/relations.py:69`: `DEFAULT_SECTIONS = ("Relationships", "History")` — the
  section filter the First Principles Thinker claimed is the real bottleneck.
- `compose_big_set.py --reviewed` sources training rows from `big_review.reviewed_labels()`, which is
  **latest-per-id-wins over `big_audit.jsonl`**. Self-grading is confirmed mechanically, not
  hypothetically.
- `schema.sql`: `edges(source_id, relation, target_id, confidence, provenance, section,
  UNIQUE(source_id,relation,target_id,section))` and `facts(node_id, key, value, citation)` exist and
  are large. The Expansionist's "no migration" claim survives.
- Operational: `big_review.ROOT = parents[2]`, and `series/universal/training/big/` does **not** exist
  in this worktree. All data-file work runs in the main checkout.

## Where the Council Agrees

**Two layers, event layer byte-identical.** All five, unprompted. Every advisor reached it from a
different direction — the 9B's `eval_hints.keys()` match on `(subject,verb,object)`,
`compose_big_set.py:72` filtering on `ok`/`reviewed_fix`, match-up reasoning reading `trained` as a
conflict. The 12-verb gold and the 9B plan do not move. This is the council's highest-confidence
signal.

**Widening the one inventory is out.** Nobody proposed it seriously. The 12 verbs are also, as the
Outsider noted, mostly self-reversing — which is exactly why the store's missing direction metadata has
never bitten before and is now fatal.

**The store cannot hold D's payload as written.** Four advisors found this independently; two reviewers
confirmed it by re-reading the file. `save_relations` discards `modality`/`certainty` silently, the PK
collapses planned-vs-actual into one row, `both_ways=True` inverts directed facts ("Scott recruited
Hope"), the per-character `DELETE` makes "add-only" destructive in the store, and the 400-char
truncation mangles long quotes. Nobody needs to be persuaded that step 0 is the store, not the
extractor.

**Mixing drafted rows into `big_audit.jsonl` is forbidden.** Confirmed mechanically:
`reviewed_labels()` is latest-per-id-wins over the audit file and feeds `compose_big_set --reviewed`.
Facts go to a new file, joined at read time. Non-negotiable, and cheap to honour — the contamination is
a single careless `git add`.

**`big_flags.sentences()` cannot be the coverage instrument.** `len(s) > 20` and
terminal-punctuation splitting both confirmed. Any gate built on it reports 100% on windows it never
segmented, and is blind precisely where person→place facts live.

**The coverage gate as written in D is a metric the labeller learns to game.** The `sent in q`
direction at line 197 means paragraphs are the cheapest path to a coverage number. This is the single
most important finding in the council and it came from reading code rather than reasoning about schema.

**"Flawless" is not an acceptance criterion.** Three advisors said so independently. Mechanical checks
catch ~80%; 13 of 98 already-OK rows still needed a change; 806 windows took a day for 5.7% of the
corpus. Replace with numbers.

**Order of work is the same in all five:** schema + gate + splitter first, a small hand-made gold set
before any sweep, pilot on reviewed windows, measure, gate, then extend. The disagreements are about
*where the rows land* and *how hard the coverage gate bites*, not about the shape of the plan.

## Where the Council Clashes

**Does the fact layer get its own file, or go into `relations`?** The Contrarian wants a standalone
`big_facts.jsonl` with a wide vocabulary. The Executor says "fact rows land in `relations` as-is" and
calls that a decisive reason to stop designing. The First Principles Thinker says neither: put
everything in `relations`/`events`/`abilities` and never invent a schema. Reviewers 1, 2, 3 and 4 all
called the Executor's claim false — it is self-refuted by its own F2, which proposes a side table for
qualifiers. But the First Principles Thinker's version is worse, for a different reason:
`ingest/relations.py` reads only `("Relationships","History")`, so widening the section list is
re-mining, not proof of completeness, and `RELATIONS` is 12 social terms that cannot hold `recruited`,
`wielded`, `member_of`, `located_at`. Reviewers 2 and 5 killed it on the owner's own terms — "modality:
reject, plans stay non-rows" reinstates the exact silent drop the owner is paying to fix.

Reasonable people disagree here because "reuse what ships" is genuinely right for ingest-time page facts
and genuinely wrong for window-time text facts. They are different universes keyed on different ids
(Reviewer 4). The verdict below resolves it: reuse the store's *shape and machinery*, not its schema.

**Is coverage a gate or a report?** The Contrarian says replace the gate with clause-level coverage and
**never gate on it in v1**. The Executor and Expansionist both gate, at 0.90 and 0.98 respectively.
Reviewer 1 landed the real point: coverage only bounds recall under an independently verified splitter,
and even the Contrarian still gates on it. Both sides are right about different halves — the gate is the
correct *target* and the wrong *instrument*, because the labeller writes the same rows the instrument
scores. That is why the instrument has to be human-scored precision, with coverage as a routing signal.

**Add-only, or re-label whole windows?** The Contrarian and Executor say add-only for all 5,405
already-labelled windows, event rows sha-identical. The First Principles Thinker says whole-window
re-label on b7–b806, because additions can never *delete* a wrong fact and `eval_hints` has no gold for
additions. Both are half right, and the disagreement is about which error is worse: a false addition
poisons a brain harder than a missing one (Contrarian), while a fact layer that can only add is not a
repair at all (First Principles). Resolution: add-only *mechanically*, with an explicit prune pass for
rows the reviewer marks bad. Both properties, both cheap.

**27B or 35B for drafting?** Unanimous: 27B, already resident on :18080. Zero switchpoints, and it is
the family the 9B distills from, so vocabulary drift is minimised. Reviewers found this uncontroversial;
it is worth stating because it removes an entire category of risk from the plan.

**Claude reviews additions only, or the whole window?** The Contrarian rejects the cheap version: Claude
must read window + additions anyway, additions are 2–3× the row count, the correction rate on reviewed
rows was ~70%, and mechanical checks catch 80%. Reviewer 5 adds the unit cost nobody priced. First
Principles disagrees (review additions against a gold set). Both resolve to the same operational answer:
review a *measured sample*, not a promise.

## Blind Spots the Council Caught

**The self-grading trap is the worst one, and it is silent.** No advisor proposed it as a
*contamination of the training set*; it is worse than that. `big_audit.jsonl` is the only gold that
exists, `reviewed_labels()` is latest-per-id-wins, and `compose_big_set --reviewed` reads it. Add
machine-drafted rows to those ids and every future P/R measures the model against its own output.
Irreversible in a way that never raises an error.

**The quote-400 truncation.** Found only by Reviewer 4, verified here: `row.get("quote").strip()[:400]`.
Any long fact quote is mangled in the store with no error. Nobody among the five flagged it, and it
directly contradicts "quote may be a paragraph."

**Measured recall vs claimed recall.** Reviewer 1: every advisor treats coverage as recall. It is only
a recall *bound*, and only under a verified splitter. Coverage numbers from an unverified segmenter are
decoration.

**Nobody tested whether the 9B student can consume a second layer at all.** Reviewer 1. Not one advisor
ran a two-layer batch. If the student can't, the entire downstream value is zero and we find out in week
three.

**Sampling must come from b7–b806, not at random.** Reviewer 1: the 806 are the only windows where a
fact precision can be computed at all. Random sampling measures nothing.

**Cross-page conflict policy is unspecified.** Reviewer 2: 308 pages, repeated and contradictory facts,
no dedup/contradiction/which-quote-wins rule anywhere.

**Who audits the coverage gate.** Reviewer 2: the Contrarian proves the gate is gameable, but proposes
no independent audit of gate *results* on held-out data.

**Overlapping windows will double-count.** Reviewer 5: `big_flags.py` itself flags DUP and OVERLAP
(b365 is the tail of b188). Add-only passes inflate coverage across the overlap seam. Nobody assigned a
seam rule.

**Unparseable windows and unknown-entity facts fail quietly.** Reviewer 5: a row whose entity is absent
from `nodes` is a fact that cannot be queried — the "complete brain" promise failing with no error.

**The join was never designed.** Reviewer 4: window-label ids and page-ingest ids are different
universes. Nothing in any answer specifies the read path that makes the brain actually *use* these
rows.

**Nobody costed the phases.** Reviewer 5: no wall-clock or GPU-hour estimate anywhere, with 2–3× row
multiplication on one serialized GPU. The 2,000-char pack vs 576-char window split also changes the
coverage denominator, making windows non-comparable.

**Canon contamination.** The Outsider raised it and everyone dropped it: `era` and `section` are the
only annotation slots, the corpus mixes MCU/main/comics/alt-continuity, and "it was in a movie or a
comic" has nowhere to go. Reviewer 3 argues cross-continuity contamination stated as truth is *worse*
than a missing fact. That belongs in the row schema, not deferred to the store.

**Coreference is a new first-order error class with no field for it.** Contrarian only. Fact rows
expose pronouns as `subject`/`object`; event rows hide them in the quote. Wiki prose is "she", "his
father". Unresolved antecedent → flag, do not emit.

## The Recommendation

**Accept D's architecture. Reject D's storage, D's coverage gate, D's self-grading, and D's word
"flawless."**

Concretely:

1. **Two layers, event layer frozen.** The 12-verb gold, `compose_big_set.py`,
   `EXTRACTION_PROCEDURE.md` step 3, and the 9B plan are untouched. Facts are a second corpus with
   disjoint prompts and disjoint labels, never a mixed prompt.
2. **New file, new tables, join at read time.** `big_facts.jsonl` + a new `window_facts` table
   modelled on `edges`' shape (`source_id, relation, target_id, confidence, provenance, section`,
   `UNIQUE(source_id,relation,target_id,section)`) and `provenance =
   "fact:<prompt_version>:<window_id>"` for idempotent re-runs. Do **not** route through
   `save_relations`. Its five-key reader, its `DELETE`, its 400-char truncation and its symmetric
   `both_ways` read are four separate ways to lose a fact silently. The existing 131k sections in other
   series stay untouched, which is also why this is additive rather than a migration.
3. **Store round-trip first.** Direction metadata, a qualifier side table, a PK discriminator that
   includes modality, and canon in `era` — then an end-to-end test that writes "Hope *planned to* train
   Scott" and reads it back with direction intact. Until that passes, no extraction code is worth
   writing. This is where projects like this die.
4. **Modality is a closed enum, not a free tag** — `{actual, planned, attempted, ordered, claimed,
   dreamed, hypothetical}` — and **any non-`actual` row carries `asserted_by` (a named character) and
   is never world-truth.** Without that, reversing step 3 makes the brain assert Loki's lies. `certainty`
   is a closed enum, not a scalar. Canon lives in `era`. `other` verb goes to a logged, non-training
   bucket with a promotion quota; `other`-share is a vocabulary-failure metric with a <10% target.
5. **Coverage is a measured recall proxy, routed, not a pass/fail gate.** Independent splitter
   (`tools/train/seg.py`, versioned, test-pinned, no length filter, no reuse of
   `big_flags.sentences()`), quote must lie inside one sentence span, subject must resolve to a named
   entity in that sentence, `sent_idx` on every row. Report per-window misses as exact sentence text —
   that is the MISS? trick turned into a worklist. Route: auto-accept iff 0 uncovered ∧ 0 `other` ∧ 0
   unresolved-coreference ∧ 0 unresolvable-entity; everything else to Claude.
6. **Hand-written fact gold before any code.** 40 windows by Claude from the reviewed set, held out,
   committed. You cannot measure precision against nothing. Sample for later audits from b7–b806, never
   randomly.
7. **Repair: add-only mechanically, with an explicit prune pass.** Event rows copied sha-identical into
   the new file, keyed by `id`, resumable. The drafter sees **text + procedure only** — not the reviewed
   rows, which anchor it to the review's own drops. Reviewed rows are used as a post-hoc dedup/prune
   filter only.
8. **Acceptance is numbers, not "flawless":** fact-layer precision ≥ 0.769 (today's event P) on a fixed
   150-window Claude-scored sample drawn from b7–b806; character coverage ≥ 0.90; zero qualifier/direction
   loss on the round-trip test; event P/R unchanged at .769/.532. Rollback is `FACTS_ENABLED=0` — every
   existing path runs unchanged.
9. **Promise only b7–b806.** One serialized GPU, 2–3× rows, Claude-review arithmetically dead past ~3k
   windows. A half-labelled fact layer with no coverage guarantee is worse than none, because downstream
   will trust it. The 14k is corpus-scale work and belongs behind the pilot gate, and the 260k-window
   corpus is a separate campaign with `relation_coverage.py` as free recall gold.
10. **Escalate to Claude before step 3:** the store findings (direction blindness, PK collapse, silent
    qualifier loss, 400-char truncation, destructive replace) are changes to engine code and the
    `plan/` vocabulary, so they are **proposals in `FACT_LAYER_PROPOSALS_FOR_CLAUDE.md`**, not edits by
    this agent.

## The One Thing to Do First

Write `plan/EXTRACTION_PROCEDURE_V2.md` and `plan/FACT_LAYER_PROPOSALS_FOR_CLAUDE.md` — the first as
the fact-row schema with a mapping row for every drop-class in §C (verify: 0 unmapped), the second
carrying the four verified store defects with `facts.py` line numbers and the concrete DDL/reader
changes needed to make the rows survive a round-trip.

No GPU, no model switch, no edits to protected files. It costs an afternoon, and it converts the
council's findings into the two artifacts that make every later step unambiguous. Do **not** start the
gold set or the sweep first — the store findings change what the schema has to look like, and gold
written before the store question is settled is gold written twice.

---

# THE NUMBERED IMPLEMENTATION PLAN

Paths are repo-root relative. **Protected (proposals only, never edits):**
`tools/train/big_flags.py`, `plan/BIG_REVIEW_PATTERNS.md`, `tools/train/label_hints.py`.
**Read-only data:** `series/universal/training/big/{labels.jsonl,big_audit.jsonl,review_cursor.txt}`.
All data-file runs execute in the main checkout (this worktree has no
`series/universal/training/big/`; `big_review.ROOT = parents[2]`). Model: 27B on `:18080`, no switch,
no SWITCHPOINT entry. Kills by exact PID. Commits with explicit pathspecs only.

| # | step | creates / edits | verification check (Claude runs this before approving the next step) |
|---|---|---|---|
| **1** | **Freeze the gold and write the numbers down** | new `plan/FACT_LAYER_ACCEPTANCE.md` (sha256 of `labels.jsonl`, `big_audit.jsonl`, `review_cursor.txt`; targets: fact P ≥ 0.769, char coverage ≥ 0.90, event P/R unchanged at .769/.532, rollback `FACTS_ENABLED=0`); new `plan/FACT_LAYER_PROPOSALS_FOR_CLAUDE.md` (the four verified store defects + DDL for `window_facts`, direction column, qualifier side table, PK discriminator, canon in `era`) | `sha256sum` the three data files, confirm they match the record in `FACT_LAYER_ACCEPTANCE.md`; confirm the proposal file cites `facts.py` lines 1536/1552/1589/1609/1623 and `big_flags.py` lines 88/197; confirm the new files are the only things changed. Claude signs before step 2. **No GPU.** |
| **2** | **Hand-write the fact gold** | new `plan/FACT_GOLD_40.md` and `series/universal/training/big_facts_gold.jsonl` — 40 windows Claude picks from b7–b806, covering every drop-class: Hope/Scott sparring, an alias, `member_of`, "seemingly killed", a canon-crossing line | exactly 40 lines, one JSON object per line; every quote substring-verified against the source text by a script assert (not by eye); every subject/object present in `nodes` + `aliases`; every relation in the registry from step 3; **0 drop-classes from §C of the brief unmapped** |
| **3** | **Registry and schema** | new `plan/fact_relations.yaml` (closed vocabulary; each entry carries `inverse`, `symmetric`, `end_types`); new `tools/train/fact_schema.py` (validator: verbatim quote, quote inside one sentence, both ends named entities, `modality` ∈ closed enum, non-`actual` ⇒ `asserted_by` present) | `python3 -c "import fact_schema"` validates 40/40 gold rows; it must **reject** three deliberately bad rows: a multi-sentence quote, a free-text modality, an unresolved antecedent; `other`-share on gold < 10% |
| **4** | **Splitter** | new `tools/train/seg.py` (versioned sentence/clause spans; handles `Washington, D.C.`, dialogue, table rows, list furniture; **no length filter**; explicitly NOT `big_flags.sentences()`); new `tools/train/test_seg.py` | `python3 -m pytest tools/train/test_seg.py -q` green, with pinned cases: a ≤20-char declarative **is retained**; a `D.C.` sentence is not split; `b365`/`b188` overlap yields consistent spans. Record the coverage-denominator delta versus `big_flags.sentences()` over the 806 |
| **5** | **Coverage reporter (no gate wired)** | new `tools/train/fact_coverage.py` (reads gold windows + a facts file, emits per-window uncovered sentences as exact text); new `tests/test_fact_layer.py` | pytest green. Run over the 806 reviewed windows using their **existing event rows only**; publish the baseline (the Executor reported 34.7% via the *bad* splitter — recompute under `seg.py` and record both numbers). The uncovered list for the known sparring/joining/call windows must reproduce A71/R4/A67 from `big_audit.jsonl` `why` fields |
| **6** | **Pilot: 50 windows, add-only, 27B** | new `tools/train/label_facts.py` (27B on `:18080`; prompt = `EXTRACTION_PROCEDURE.md` + the fact procedure; **input is window text only, never the reviewed rows**; output to a NEW `series/universal/training/big_facts.jsonl`; resumable by id-set). **Do not extend `label_single.py`** — it owns the frozen F1 baseline | event rows in the pilot output are sha-identical to `labels.jsonl` for all 50 ids; 100% verbatim quotes; 0 unresolved ends; 0 out-of-registry relations; ≥45/50 windows at coverage ≥ 0.90; Claude hand-scores 20 → **fact precision ≥ 0.75 to continue** |
| **7** | **Gate the whole thing + two-layer smoke test** | new `tools/train/fact_gate.py`; extend `tests/test_fact_layer.py`; two-layer batch smoke test for the 9B student (Reviewer 1's gap: does `compose_big_set`-style batching accept fact rows at all?) | pytest green; the two-layer batch runs; `eval_hints` P/R on the event gold are unchanged at **.769/.532**. **Any event drift is the rollback trigger**: `FACTS_ENABLED=0`, revert the extractor, keep `seg.py` and the gate |
| **8** | **Reconcile `--empty-share`** | record `empty_class` per window (`hard_empty` / `nonfact_only` / `fact_bearing`) in the facts file; propose the `compose_big_set.py` change (75% hard empties are mostly v2 facts) **in `FACT_LAYER_PROPOSALS_FOR_CLAUDE.md`** — it is not ours to edit | the tally over the 806 shows how many current empties become fact-bearing; **Claude approves or rejects the redefinition before step 9** |
| **9** | **T0 — free repair triage, zero GPU** | run coverage over all 806 reviewed windows' existing rows; publish the uncovered-sentence list per window | the list is non-empty for a known window (it must reproduce A71/R4/A67); Claude reads only that list. Costs zero GPU-hours and bounds every later review |
| **10** | **T1 — add-only pass over the 806, 27B, no switchpoint** | run `label_facts.py` over b7–b806 into `series/universal/training/big_facts.jsonl` | every 200 windows: parse-fail 0, event-row sha identical, `other`-verb tally published, coverage report published, per-window counts recorded. Commit `series/universal/training/big_facts.jsonl` with an **explicit pathspec only** |
| **11** | **Prune + review a measured sample** | routing: auto-accept iff 0 uncovered ∧ 0 `other` ∧ 0 unresolved coreference ∧ 0 unresolvable entity; explicit prune pass for rows Claude marks bad; Claude scores a fixed random **150-window sample of the 806** (sampled from the reviewed set, where precision is computable at all) plus the whole prune list | measured fact-layer precision ≥ **0.769** and character coverage ≥ **0.90**. Below that: halt and iterate the prompt rather than shipping |
| **12** | **Store round-trip, after the pilot passes** | implement `window_facts` + direction + qualifiers **per Claude's approved proposal**; end-to-end test writing "Hope *planned to* train Scott" and reading it back | the test asserts direction, modality, canon, and that a 400+ char quote is stored **whole** (not truncated at 400). Until this passes, the layer is a file, not a brain |
| **13** | **2,000-char vs 576-char pack, and overlap seams** | extend `seg.py` coverage reporting to the pack size; add a DUP/OVERLAP seam rule so facts in b365/b188 are not double-counted | windows are comparable — the same text yields the same uncovered-set whether read at 576 or 2,000 chars; measure and record the denominator change |
| **14** | **Only then the 8,595 unlabelled windows** | one full v2 pass; auto-accept routing enabled **only after step 11's precision is measured and published** | per-200 spot checks as in step 10; coverage report per window; `git log` shows explicit-pathspec commits only |
| **15** | **Stop and declare** | — | if fact precision < 0.70 or coverage < 0.85 at step 11: revert the extractor, keep `seg.py`, `fact_schema.py`, the gate and the gold; write the evidence to `FACT_LAYER_PROPOSALS_FOR_CLAUDE.md`; do **not** launch the fleet |

**Standing constraints for every step:** 27B on `:18080`, never a model switch without a
`plan/SWITCHPOINT.md` entry; kill by exact PID only; `big_flags.py` / `BIG_REVIEW_PATTERNS.md` /
`label_hints.py` proposed to Claude, never edited; `labels.jsonl` / `big_audit.jsonl` /
`review_cursor.txt` read-only; commits with explicit pathspecs only.

---

# STATUS

Council complete and committed. **No code has been written and no other file has been changed** —
per the brief's instruction, this record is the only artefact of step 1. Work begins at step 1 of the
plan above, and only after Claude has verified this record and named the step to implement.
