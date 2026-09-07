# COUNCIL — JJK D6-completion: definition of "done" + sequencing

Date 2026-09-07. Session: d6-completion run (opencode checkpoint
`8b6633e` → this pi session, `28d7ae8`). **Step:** the todo-2 fork — the
definition of "done" for JJK D6-completion and the sequencing of the
remaining work (§12 dimension map vs the retired R1–R5 remainder vs the two
unmeasured D5 doors), JJK only, halt before P6.

**Method (project convention, `CLAUDE.md` council rule).** 5 advisors in
parallel, each a *fresh-context* pi session on the local Qwen 27B
(`pi --no-tools --no-session --no-context-files`, identical framed question,
different advisor lens) → responses anonymized (A=first-principles,
B=contrarian, C=expansionist, D=outsider, E=executor — the mapping is
recorded here; the reviewers never saw it) → 5 peer reviewers in parallel
(fresh-context, same anonymized pack) → chairman synthesis (fresh-context,
higher thinking). Full transcript: `raw/council_d6-completion/`
(`framed_question.md`, `advisor_*.md`, `resp_*.md`, `reviewer_prompt.md`,
`review_1..5.md`, `chairman_prompt.md`, `verdict.md`).

---

## The framed question (abridged; full text in `raw/council_d6-completion/framed_question.md`)

The mandate: complete JJK D6-comprehension — the corpus must *understand*
everything about a character (what each line/fact/prose/event means, whether
it is an event, where it sits on the timeline, the structured dimensions).
JJK only; halt before P6. Verified state: events 2,748 (2,594 placed / 154
unplaced), 107/390 cross-page disagreements (27.4%, triaged; ~0 unambiguous
misplacements per the chapter-range spot-check), abilities 594/94 chars,
relations 821/136 (298 era), semantics 0 rows, edges 81% untyped; D5 tier-0
48,572/48,572, tier-1 545-census 540/545 (99.1%); **roster and narrative
doors unmeasured**; all five ability dims 3C-GREEN; P4 closed bounded
(interval facts durable via `overrides.yaml`). Decision: define "done" as a
checkable set and sequence (i) the §12 dimension map with its two
preconditions (eight-verb 100-sentence sample; per-NONE-dimension
retrieval-not-extraction test), (ii) the retired R1–R5 remainder, (iii) the
two unmeasured D5 doors. No user input during the run — the verdict is
executed as written.

## Advisor responses (full text in `raw/council_d6-completion/resp_*.md`)

**First Principles (A).** "Understands everything" is a *service property*,
not an extraction inventory: a fact that is stored but unreachable fails; a
fact that is absent but served by retrieval is not owed. Sequencing is
forced: (1) measure the two unmeasured doors (roster, narrative) — D6 cannot
be "done" while a serving door may be silently broken; (2) run the §12
preconditions (model-free, decisive: they separate true meaning gaps from
chunking/serving defects; any extraction scheduled before them is zombie
risk); (3) place the 154 (R4) — the mandate explicitly includes timeline
placement; (4) extract only where tests show failure, each with a consumer
door; R1 contingent, R2 iff retrieval misses, R3 on red relation questions;
R5 parked. Done = span-recall holds + all three D5 doors pass a fixed
census + every §12 dimension has measured retrieval-or-extraction evidence +
all events placed + gates green → halt before P6.

**Contrarian (B).** "Understand everything" is not checkable as written —
the 12+3 map was built *before* the owner's correction and is a proxy;
declaring done against it institutionalizes whatever it missed. The plan
sequences around two unmeasured walls (roster/narrative: a red narrative
door makes the "timeline understanding" claim fiction). 27.4% disagreement
triaged to "~0 unambiguous misplacements" is a *confession, not a pass* —
the spot-check grounded disagreements against chapter ranges, not ground
truth; the gate's **false-negative rate is unmeasured** and is the number
that matters. Precondition (a) has no failure branch: if 25% of sampled
sentences need a ninth verb, the run freezes mid-way with no user input —
define the red path now or the plan isn't a plan.

**Expansionist (C).** The unmeasured doors are the upgrade that turns D6
from "serves facts" into "understands a life" (roster + narrative serve the
time axis as a primitive). Sequence: doors FIRST (a red narrative door
reorders everything; a green one frees you), then the §12 preconditions in
parallel (model-free, cheap, convert the map from speculation to evidence —
if retrieval already serves the 42.5k-word Personality dimension,
understanding is proven *for free*), then extract only what the measurement
names. "Done" per-character: a fixed census where every dimension question
is reached, narratively ordered, across the doors. If the doors come back
green, done is reached sooner than priced.

**Outsider (D).** "Understand" is load-bearing and undefined — done must be
a checkable set of retrieval properties (per dimension, a sample of
character-level questions reaches the answering paragraph). The two
unmeasured doors are the obvious first step, not an option alongside the
map. The 12+3 dimension list *itself* is unverified as "everything" — the
outider wants a small **open-ended sample (50 zero-shot character
questions)** checked against the map, off-map classes added and measured.
And the remainder doc's R1 incoherence: called "the goal's core", then
retired as a narrow reading — "retired" + "core" cannot both be true without
a sentence explaining the relationship.

**Executor (E).** Monday morning: census the two unmeasured doors — bounded,
model-free, the one item that could hide a reachability failure under a
"comprehension" label; but **verify each door exists before measuring it**
(a census through a missing door counts nulls). Then the two §12
preconditions — they are the "done" spine; do not build R1/R2 before them;
**R2 is already 3C-GREEN (313/315) — retire it, don't re-queue it**. R4 is
the only standalone build (clear first step, no precondition) — run it in
parallel. Hidden dependency nobody priced: "no third corpse" means R1 is
extractor + consumer door + census on that door, priced as a unit. "Done" =
checklist: (1) doors censused, passing a tier-1 bar; (2) preconditions
recorded; (3) unplaced = 0 or explicitly triaged; (4) every new table ships
with door + measured reach; (5) standing gates green; (6) halt before P6.
Skip R5; gate R3 on measured value.

## Peer reviews (full text in `raw/council_d6-completion/review_1..5.md`)

- **Strongest:** E (4 of 5 reviewers; rv3: A) — the only response that
  prices the "no third corpse" cost, retires R2 on evidence, and delivers a
  6-item checkable done-list.
- **Biggest blind spot:** C (4 of 5; rv3: B) — green-path-only pricing, no
  failure branch; equates "green doors + preconditions" with "everything,
  verified" on the unverified pre-correction map.
- **Missed by all five (convergent):** (1) the **R4 → narrative
  input-stale dependency** — a narrative census before the 154 are placed
  measures a stale timeline (rv1); (2) the **empty `semantics` table** (0
  rows) — R1's natural home under "no third corpse"; done cannot be
  declared with a door-less table standing in the store (rv2/3/5);
  (3) **no failure branch for the 8-verb sample** (B named it; nobody
  designed it — a pre-committed rule is required, no user input)
  (rv2/3/4/5); (4) **outcomes + causality** — the map's two live additions
  are the dimensions most likely to need extraction and were in no done
  criterion (rv4); (5) **the gate's false-negative rate** never turned into
  a measured done-item (B + rv5); (6) **no numeric census size or pass bar**
  anywhere (rv1/3); (7) the unpriced R1 door cost (E + rv1/2/4); (8) GPU
  sequencing — model-free work first, any LLM extraction sized into the
  final window before the P6 halt (rv5).

## The verdict (chairman synthesis, full text in `raw/council_d6-completion/verdict.md`)

**Definition of "done" — checkable set, all must hold (D1–D10):**

- **D1.** Roster census: 100 fixed enumeration questions, stratified
  (characters / techniques / organizations / items) — ≥99% reached; every
  miss triaged (retrieval-controlled → fixed + tracked; reachability defect
  → repaired + re-censused).
- **D2.** Narrative census: 100 fixed chronological queries, stratified
  (characters/arcs), **run on the post-R4 timeline** — ≥99% reached, same
  triage.
- **D3.** Tier-0 re-verified (span-recall 48,572/48,572 rc=0); tier-1
  re-censused on the final corpus, ≥99%.
- **D4.** Preconditions recorded: (a) 8-verb 100-sentence sample with its
  branch executed; (b) 10-question retrieval-not-extraction test for all 12
  dimensions **plus outcomes and causality** (140 questions); (c) the
  50-question open-ended census — off-map classes (≥3 in one class) added to
  the map and measured under (b).
- **D5.** Placement-gate audit clean: stratified sample (40 agreeing
  multi-page groups + the 107-disagreement set) re-grounded post-R4 against
  chapter ranges; 0 unflagged unambiguous misplacements in the agreeing
  sample, else B5 key-refinement runs first.
- **D6.** Unplaced events = 0, or each remainder explicitly triaged with a
  recorded reason.
- **D7.** No door-less table in the store: `semantics` resolved (populated
  with a door + census if R1 triggers, else formally retired); every new
  table ships with its door + reach census.
- **D8.** Every contingent build named by a red measurement is complete with
  door + census — or the terminal state is **not-done + diagnostic memo**
  (the run reports not-done honestly; it does not manufacture done).
- **D9.** Standing gates green: pytest 1,239 · eval jjk 31/31 · span-recall
  jjk 48,572/48,572 rc=0 · canon opm 10/16 · 236/236 · 79.0%.
- **D10.** Halt: no P6, no cross-corpus work. Completion memo committed with
  all census numbers and the triage log.

**Sequencing (failure branches pre-committed):**

- **Phase 0 — door pre-check (model-free).** Verify roster + narrative doors
  exist and are callable. *Branch: door missing → build the serving plumbing
  first (reachability, not extraction, no LLM) → verify → proceed. No census
  through a null door.*
- **Phase 1 — R4 (standalone, model-free, before any timeline census).**
  Place the 154 (116 generic-heading + 38 Modulo-Chapter docs) — bar:
  unplaced = 0 or each remainder triaged with a recorded reason (a
  genuinely unplaceable event is a legal triage outcome, not a silent
  one). Re-run the cross-page gate + standing gates on the updated corpus.
  *Branch: an event that won't ground against chapter ranges → triage
  record (reason + source page), never a forced placement.*
- **Phase 2 — door censuses (model-free, post-R4 corpus).** Roster 100 +
  narrative 100 fixed questions; bar ≥99% reached each; every miss
  triaged. *Branch: a door still red after repair → bounded repair budget of
  2 iterations; still red → the fork goes to a fresh 5-advisor council on
  the reachability repair (a red door is never waved through under a
  "comprehension" label; a freeze is not an option either).*
- **Phase 3 — measurement batch (model-free, parallel):**
  - **3a** 8-verb sample (100 plot-summary sentences). *Pre-committed
    branch: ≤10 inexpressible → mechanism adequate, no verb work. >10 →
    cross-check those sentences against retrieval: retrieval green → record
    as gate-coarseness diagnostic (B5-class), no build; retrieval red →
    genuine meaning gap → R1 triggers (Phase 4).*
  - **3b** per-dimension retrieval-not-extraction: 10 questions × 12
    dimensions + outcomes + causality = 140. Green → no extraction owed,
    recorded. Red with the paragraph present in source → chunking repair,
    not a new table. Red with content unserved from anywhere → name the
    layer owed → Phase 4, ships with a door.
  - **3c** open-ended 50-question census (generated with no map reference).
    ≥3 off-map questions in one class → add the dimension, measure under
    3b. *Done is declared against the verified map (12+3+additions); the
    map can only grow via 3c, and every addition is measured before the
    done-declaration — the checkable form of the owner's "everything"
    correction.*
  - **3d** placement-gate false-negative audit (the D5 item above).
- **Phase 4 — contingent extraction (only what a red measurement named; LLM
  work sized into the final Qwen window before the P6 halt).** Priority:
  1. reachability repairs named by red doors (model-free); 2. **R1 per-line
  meaning index** — iff 3a >10 AND 3b red on that content; priced as a unit
  (cloned extractor + consumer door + reach census; populates the empty
  `semantics` table as R1's home); 3. **outcomes layer** — iff 3b red on
  "who won" and chunking repair doesn't close it (field extraction from
  battle-page result fields, not freeform); 4. **causality layer** — iff 3b
  red on "why" (per-event causal notes + door; most likely owed); 5. **R3
  relations era** — iff era/relation questions red (era backfill on the 821
  rows + eventive predicates as cross-references into `events`, no new
  predicate layer). **Retired, not re-queued: R2** (3C-GREEN; a red
  ability-enumeration is repaired as a door/chunking defect first per
  §12(b); reopens only as a coverage backfill with door + census if the
  content is unserved from anywhere) **and R5** (parked; 81% untyped
  recorded as accepted state). *If R1 never triggers, `semantics` is
  formally retired (drop or deprecate, recorded) — no door-less table
  survives into done. Branch: an owed build that cannot fit the remaining
  Qwen window → terminal not-done + diagnostic memo.*
- **Phase 5 — done-declaration.** All of D1–D10 hold → completion memo
  (census numbers, triage log, map verification, audit result, gate
  transcripts) → **halt: no P6, no cross-corpus work.**

**The one thing to do first:** place the 154 unplaced events (R4) — 116
generic-heading rows + 38 Modulo-Chapter docs — bar "unplaced = 0 or each
remainder explicitly triaged with a recorded reason", then re-run the
cross-page gate and standing gates. The only non-contingent build, named in
the mandate, and it fixes the narrative door's input (every census that
measures "when" is stale if run before it). The ten-minute door-existence
pre-check rides along; the roster census may co-locate (placement-invariant);
nothing touching the timeline moves until R4 is placed and the gates are
green.

---

## DB-verification ledger (claims verified before recording, 2026-09-07)

| claim | verified how |
|---|---|
| events 2,748 / 2,594 temporal=1 / 154 `arc_index IS NULL` | `sqlite3 series/jjk/facts.db` COUNT queries, this session |
| 154 = 116 non-placement pages (character 99, character_synopsis 11, location 4, technique 2) + 38 chapter rows across 17 distinct `Modulo Chapter` docs | same store: `events ⋈ sections ⋈ documents` GROUP BY `page_type` + `DISTINCT document_id` on `title LIKE '%Modulo Chapter%'` |
| cross-page: 684 groups, 390 from 2+ pages, 283 agree, 107 disagree (27.4%); 154 recorded standing states; temporal set 2,594 | `comprehension-gate --series jjk` (offline, this run) — live output matches `GATE.md` |
| tier-0 span-recall 48,572/48,572, 0 unreachable, rc=0 | `span-recall --series jjk` (offline, this run) |
| abilities 594 rows / 94 distinct characters; relations 821 / 298 era; semantics 0 rows; edges 35,026 | COUNT + DISTINCT queries, this session |
| "semantics table is door-less" (reviewer claim) | **Corrected:** the `semantics` table (entity-keyed classification: `title` PK, `semantic_type`, `properties`) has an upsert *and* a read path in `scriptengine/stores/facts.py` (`INSERT INTO semantics` :1905, read :1873) — it is not door-less, it is **empty with no extractor**. `retrieve/semantics.py` (the entity-type classifier the roster door uses) is a different, working mechanism. D7 stands as "resolve the empty table": populate with door + census if R1 triggers, else formally retire. |
| "roster and narrative doors exist" (Phase 0) | Code-level verified this session: `/context` accepts `mode: qa | narrative | roster | auto` (`api/main.py:79`), `retrieve/roster.py` + `retrieve/narrative.py` exist, the router routes `auto` between them. Operational callability (live `:8000`) is Phase 0's work item, not an assumption. |
| all five ability dims 3C-GREEN (313/315, miss ≤1.1%, thin ≤1%, oracle 16/18) | `P3A_ABILITY_CENSUS.md` + `raw/census_ability_results.json` (2026-09-07 run) |
| 545 census 540/545 (99.1%), 5 retrieval-controlled misses fixed + tracked | `STEP5_CENSUS_545.md` (post-`a5e93c3` re-run) |
| standing gates (pytest 1,239 · eval 31/31 · canon 79.0%) | recorded baselines; re-run as part of execution (Phase 1 re-gates after R4) |

## What this council changed in the plan

1. **R2 and R5 are retired, not deferred** — re-queue only on new red
   evidence (R2: content unserved from anywhere; R5: never scheduled this
   run).
2. **R4 is Phase 1** — the only non-contingent build, and it gates the
   narrative census (input-stale dependency caught by the reviews).
3. **The two unmeasured D5 doors become censuses** (100 questions each,
   ≥99% bar, post-R4) — D1/D2.
4. **The map is verified, not assumed**: 3c's 50-question open-ended census
   can only *grow* the map, and done is declared against the verified map.
5. **Outcomes + causality join the 3b regime** (140 questions, not 120).
6. **B5 becomes a measured done-item** (3d false-negative audit: 40
   agreeing groups + the 107 re-grounded post-R4).
7. **`semantics` must be resolved** (D7) — populated (as R1's home) or
   formally retired; no door-less table at done.
8. **Failure branches are pre-committed** at every measurement (8-verb
   ≤10/>10; red door → 2 repair iterations → council; R4 ungroundable →
   triage record; owed build doesn't fit the window → not-done memo).
9. **R1's "core vs retired" incoherence is resolved**: retired-by-default,
   re-queued-by-evidence — the preconditions may show retrieval already
   serves per-line content; if not, R1 is the named fallback, priced as
   extractor + door + census (no third corpse).

## Ledger row

`COUNCIL_HISTORY.md` row 19.