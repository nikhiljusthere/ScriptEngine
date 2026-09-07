You are the Chairman of an LLM Council. Your job is to synthesize the work of 5 advisors and their peer reviews into a final verdict.

The question brought to the council:

---

# Framed question — JJK D6-completion: definition of "done" + sequencing

## The system

ScriptEngine ingests a Fandom wiki (here: Jujutsu Kaisen, "JJK") into a
corpus (SQLite facts/graph + Qdrant vectors) and serves ordered, cited,
structured context over HTTP to the model that writes video scripts. The
engine does not write scripts; it feeds the writer-model.

## The mandate (owner, fixed)

Complete **JJK D6-comprehension**: the corpus must *understand* everything
about a character — what each line/fact/prose/event **means**, whether it is
an event, where it sits on the anime's timeline, and the structured
dimensions (facts, history, fights). **JJK only. Halt before P6** (no
cross-corpus work). The owner corrected a narrow earlier reading of the goal:
*"I did not mean only those 3 things, I meant everything."*

## Verified state (all DB-verified 2026-09-07, jjk store)

**Structured layers:**
- `events`: 2,748 rows; 2,594 placed on the arc time axis (`temporal=1`),
  154 unplaced (116 under generic headings on non-placement pages, 38 on
  `Modulo Chapter N` docs filed off the story chain).
- Cross-page agreement (the gate's only non-tautological placement signal):
  **107 disagreements of 390 multi-page groups (27.4%)**. Triage: 31
  interaction-verb anachronism core (9 premature + 22 delayed), 50 state-verb
  keying (arrived/departed — a coarse `(verb, participant)` key, not a wiki
  contradiction), 26 adjacent boundary straddles. 98/107 touch a
  section-placed row. A spot-check grounded all 107 against chapter ranges:
  ~56% are key-coarse repeat-encounters (the same pair genuinely spanning
  arcs), ~21% arc-boundary artifacts, **~0 unambiguous misplacements**.
- `abilities`: 594 rows over **94 distinct characters** (narrow; the
  character population is larger).
- `relations`: 821 rows over 136 characters; only 298 (36%) carry an `era`;
  vocabulary is social-only (family/ally/enemy/mentor/rival/superior) — no
  eventive predicates (those live in `events`).
- `semantics`: table exists, **0 rows**, no consumer door.
- `edges`: 35,026 rows; only 6,543 typed (19%); 81% untyped `mentions`.
- Temporal keys in `facts` (`arc`/`date`/`anime episode`): ~990 lines
  (<1% of the 48,572 corpus lines) — only `events`+`arc_index` carry "when".

**Reachability (D5):**
- Tier 0 (indexing tautology): span-recall 48,572/48,572, rc=0.
- Tier 1 relevance door: 545-pair census = 540/545 reached (99.1%); 5
  retrieval-controlled misses, both genuine faults fixed + tracked.
- **The two other retrieval doors are UNMEASURED: `roster` (enumeration —
  "who are all the X") and `narrative` (chronological serving).** Nobody has
  run a census through either door yet.

**What is already proven (do not re-litigate):**
- All five ability dimensions are **3C-GREEN**: a 315-pair census shows
  retrieval already serves the ability paragraphs (313/315 reached, miss ≤
  1.1%, thin ≤ 1%, held-out oracle 16/18). No ability widening/mechanics
  extraction is owed by that evidence.
- P4 (state-over-time) is **closed at a bounded scope**: 2 durable interval
  facts (e.g. "Nanami during the Culling Game") re-landed on every index via
  `overrides.yaml`; oracle 4/4. A wiki-wide interval model (4B) is on the
  backlog, not the plan.
- The 8-verb event mechanism (fought/killed/saved/arrived/departed/awakened/
  sealed/betrayed) is built, placed, and gated; the 107-disagreement corpus
  feeds a per-line meaning index, not a demotion gate.

**The dimension map (`Plan_to_perfection.md` §12):** ~106,000 words of
character prose across 12 dimensions (Personality 42.5k, Overview 16.7k,
Trivia 15.9k, Appearance 14.2k, Cursed Technique 13.6k, History 11.6k,
Physical Prowess 10.6k, Intelligence 9.7k, Abilities & Powers 8.5k, Cursed
Energy 6.4k, Equipment 3.8k, Quotes 1.5k) plus 3 the map must also cover:
state-over-time (bounded version closed; wiki-wide deferred), **outcomes**
(battle result fields exist on battle pages but no layer models "who won"),
and **causality** (why/what-caused). The map carries two preconditions:
(a) **eight-verb coverage sample** — sample 100 random plot-summary
sentences, record which the eight verbs cannot express; model-free;
*nothing schedules off the map until it is measured*; (b) a
**retrieval-not-extraction test** per "NONE" dimension — 10 questions; if
the served bundle contains the answering paragraph, no extraction is owed;
if not, it is a chunking defect, not a missing table.

**The retired remainder (R1–R5 + B5 in `COMPREHENSION_REMAINDER.md`):**
R1 per-line/per-beat meaning index (cloned from the events extractor; the
goal's core per that doc), R2 abilities to full character coverage, R3
relations era + eventive predicates, R4 place the 154 unplaced events,
R5 typed edges (deferred, lowest value), B5 key-refinement (diagnostic).
§12 retired R1–R5 as a *narrow reading of the goal*; the remainder doc has
not been rewritten yet.

**Standing gates (re-run after every build):** pytest 1,239 · eval jjk
31/31 · span-recall jjk 48,572/48,572 rc=0 · canon-run opm 10/16 exact,
236/236 canon, 79.0%.

**Operating rules:** no user input during the run — every fork goes to a
5-advisor council; "no third corpse" (every new table ships with the door
that reads it); GPU: the 27B Qwen model owns the card for sustained LLM
batches; short retrieval jobs co-locate; council claims are DB-verified
before recording.

## The decision

Define **"done" for JJK D6-completion** — a checkable set of conditions,
not a score — and the **sequencing** of the remaining work, choosing among
and ordering: (i) the §12 dimension map with its two preconditions,
(ii) the retired R1–R5 remainder items (in whole or in part), (iii) the two
unmeasured D5 doors (roster, narrative). What must be true, in what order,
for the corpus to *understand everything about a character* on JJK — and
when does the run halt (before P6)?

## What's at stake

The mechanism (events, time axis, three-check gate, continuity scaffold,
durable keys) is built and green. The open question is the *goal itself*: a
checkable definition of "understands everything" that does not (a) re-queue
zombie work the evidence already retired, (b) schedule extraction before the
measurement that decides whether it is owed, or (c) let the two unmeasured
D5 doors hide a reachability failure under a "comprehension" label. The
verdict will be executed without further user input, so it must be
unambiguous.

---

ADVISOR RESPONSES (de-anonymized):

**The First Principles Thinker:**

First principles: we are not asking whether tables exist; we are asking whether the writer-model can retrieve every character-relevant proposition, with provenance, through a door. “Understands everything” is a service property, not an extraction inventory. If a fact is stored but unreachable, the corpus fails. If a fact is absent but retrieval serves the source paragraph, extraction is not owed.

Sequencing is forced. First measure the two unmeasured D5 doors, roster and narrative. Until then, D6 cannot be “done” because enumeration/chronology could be silently broken. A characterization layer cannot compensate for a missing serving door.

Second, run the §12 preconditions. The eight-verb sample and per-dimension retrieval-not-extraction tests are model-free and decisive: they tell us which gaps are true meaning gaps and which are chunking/serving defects. Any extraction scheduled before those tests is zombie risk.

Third, place the 154 unplaced events (R4) because the mandate explicitly includes timeline placement. Fourth, add extraction only where tests show failure and only with a consumer door: R1 per-line meaning if event-level verbs cannot carry the content, R2 abilities if retrieval misses, R3 era/eventive predicates if relation questions fail. R5 stays parked unless an answer trace shows untyped mentions block retrieval.

Done means: span-recall holds, all three D5 doors pass a fixed question census, every §12 dimension has measured retrieval-or-extraction evidence, all events placed, gates green. Then halt before P6.


**The Contrarian:**

Three things will sink this.

First, "understand everything" is not checkable — it's a feeling. The 12+3 dimension map was built before the owner's correction from "3 things" to "everything." It's a proxy, not the mandate. If motivations or how others perceive a character aren't on the map, they're not owed, and that gap is now institutionalized. You can't declare done against a list written before the goal was stated.

Second, you're sequencing around two load-bearing walls you haven't inspected. The roster and narrative doors have zero census. If the narrative door misses 30% of chronological queries, your "timeline understanding" claim is fiction — the corpus can't serve what it can't retrieve. Run those censuses before any work that touches "when" or "who." You're asking the council to order a plan built on blind spots.

Third, 27.4% cross-page disagreement triaged to "~0 unambiguous misplacements" is a confession, not a pass. The spot-check grounded 107 disagreements against chapter ranges, not ground truth. 107/390 groups disagree, and you're calling the gate green because every disagreement has an explanation. But what's the false-negative rate? If the gate should catch real misplacements and 27% of groups disagree, you don't know how many errors it's missing. That's the number that matters, and nobody's measuring it.

Finally, precondition (a) — the eight-verb sample — has no failure branch. If 25% of sampled sentences need a ninth verb, what happens? No council is scheduled for that, no user input is allowed. You'll hit it mid-run and freeze. Define the "if it fails" path now or the plan isn't a plan.


**The Expansionist:**

The upside everyone is underpricing: the two unmeasured doors are not housekeeping — they're what upgrades D6 from "serves facts" to "understands a life." Roster (enumeration) and narrative (chronological serving) turn the time axis + events layer into a *serving primitive*: the corpus can return a character's whole arc in order and answer "who are all the X" — capabilities no fact-retrieval gives. If both are green, "done" is a stronger, provable claim than anyone is scheduling for, at near-zero cost.

Sequence: measure the two doors FIRST. They gate the entire D6 claim — you cannot say "understands a character's history" if you can't serve that character chronologically. A red narrative door reorders everything; a green one frees you. Then batch the §12 preconditions (100-sentence 8-verb sample + per-NONE-dimension 10-question retrieval test). They're model-free, cheap, and run in parallel — and they convert the whole 12-dimension map from speculation into evidence. If retrieval already serves Personality (42.5k words — the biggest dimension, currently table-less), you've just *proven* understanding for free.

Then extract only what the measurement says is owed, strictly in that order. R1–R5 don't get re-queued on faith; they get re-queued *if and only if* a red precondition or a red door names them.

The fatal error the risk advisor will make: schedule the pessimistic extraction path. The measurement-first path is simultaneously the safe and the fast one — it cannot hide a reachability failure (it exposes it), and it can only reveal upside. Define "done" per-character, not per-table: a fixed census where every dimension question is reached, narratively ordered, across the roster and narrative doors. That's the checkable set, and it's the big version. If the doors come back green, you're done sooner than the council is pricing, with the claim the owner actually asked for: *everything*, verified.


**The Outsider:**

The word "understand" is load-bearing and undefined. A SQLite store doesn't understand; it stores and retrieves. "Done" must be checkable as a set of retrieval properties: for each dimension, for a sample of N character-level questions, the served bundle contains the answering paragraph at acceptable precision. If you can't state the checkable property, you can't verify the mandate.

The two unmeasured D5 doors (roster, narrative) are the obvious first step, not a sequencing option alongside the dimension map. "Who are all the X" and "serve me their history in order" are Tier 1 functional requirements. If roster enumeration fails, no amount of per-line meaning indexing makes the corpus "understand" anything. Run those two censuses before scheduling any extraction work. They're cheap, model-free, and their results gate everything downstream.

The dimension map asserts 12 dimensions + 3 = "everything." Nothing verifies that assertion. Precondition (a) samples eight verbs; precondition (b) tests retrieval for "NONE" dimensions. But the dimension list itself — that these 12 categories exhaust "everything about a character" — is taken on faith. An outsider would want a small open-ended sample (50 character questions from zero-shot prompts) checked against the 12+3 to catch dimensions the map missed, before any extraction is scheduled.

Finally, R1 (per-line meaning index) is called "the goal's core" in the remainder doc, then retired as a "narrow reading." That's incoherent as written. Either R1 is subsumed by the dimension map work (say where) or it's a genuine gap (say why it was retired). "Retired" + "core" cannot both be true without a sentence explaining the relationship.


**The Executor:**

Monday morning you run the two unmeasured D5 doors — roster and narrative — as censuses. That's the whole fastest path: bounded, model-free, cheap, and it's the one item that could hide a reachability failure under a "comprehension" label. Nothing else schedules until those two numbers exist. But if a door isn't even built, "census through it" is a fiction — verify each door exists before you measure it, or you're counting a null.

Then run the two §12 preconditions — the 100-sentence eight-verb sample and the 10-question retrieval-not-extraction test per NONE dimension. Model-free, bounded, and they are the actual "done" spine: they decide whether any extraction is owed. Do NOT build R1 or R2 before this. R2 is already 3C-GREEN (313/315), so it isn't owed — retire it, don't re-queue it.

R4 is the only standalone build: place the 154 unplaced events. Clear first step, no precondition — 116 generic-heading rows + 38 Modulo Chapter docs. Do it in parallel, not in sequence.

The hidden dependency nobody priced: "no third corpse" means R1 (per-line meaning index) isn't "clone the extractor." It's extractor + a consumer door that reads it + a census proving that door reaches. The door and its census are the cost, and they're unpriced.

"Done" = a checklist, not a score: (1) roster+narrative censused and passing the Tier-1 bar; (2) both preconditions recorded; (3) unplaced events = 0 or explicitly triaged; (4) any new table ships with its door + measured reach; (5) standing gates green (pytest 1,239, eval 31/31, span-recall 48,572 rc=0, canon 79%); (6) halt before P6. Skip R5 (deferred, lowest value); gate R3 on measured value.


PEER REVIEWS (five independent reviews of the anonymized responses):


**Peer review 1:**

**1. Strongest: E.** It delivers the decision's ask — a 6‑item checkable "done" checklist plus sequencing — and uniquely (a) retires R2 as a zombie (3C‑GREEN), (b) uncovers the unpriced "no third corpse" cost (R1 = extractor + consumer door + its census), (c) runs R4 in parallel. A's "done as a service property" is the best frame, but A's "R2 if retrieval misses" re‑queues a zombie; E is executable, A is philosophy.

**2. Biggest blind spot: C.** It prices only the upside and equates "green doors + passing preconditions" with "everything, verified" — exactly the over‑claim the mandate warns against: the 12‑dim map is a pre‑correction proxy, and the gate's 27.4% disagreement has an unmeasured false‑negative rate. C would declare done on a reachability proxy dressed as the owner's "everything."

**3. All five missed the R4→narrative dependency.** Everyone sequences the doors first (census on the current timeline), then places the 154 events. Placing them changes the timeline the narrative door serves, so a narrative census run before R4 is input‑stale. The council must run R4 first or re‑run the narrative census afterward. (Nobody fixes a numeric pass bar for the censuses.)

**Peer review 2:**

Reviewing `/home/goblin/ScriptEngine/reports/comprehension/raw/council_d6-completion/reviewer_prompt.md`:

**1. Strongest: E.** Most operationally complete: a 6-item checkable done-checklist (not a score); retires R2 on the 3C-GREEN evidence (313/315) instead of re-queuing zombie work; orders doors → preconditions → R4 (parallel, the only standalone build); and uniquely flags the door-existence precheck ("verify each door exists before you measure it") and R1's unpriced "no third corpse" cost (extractor + consumer door + census). A is close but serial and generic; D's exhaustiveness probe and B's failure-branch critique are sharp, but neither is an executable plan.

**2. Biggest blind spot: C.** C prices only the green path ("near-zero cost", "done sooner if green") and has no failure branch: red doors or a failed 8-verb sample leave no next step, no scheduled council, no user input — a mid-run freeze, exactly what B warned about. Its "done" is conditional on green outcomes, so it isn't a checkable set of conditions.

**3. What all five missed:** the empty `semantics` table (0 rows, no consumer door). Nobody addressed whether it is owed, retired, or the ready-made consumer door that R1's per-line meaning index must ship with under "no third corpse."

**Peer review 3:**

**1. Strongest: A.** It defines "done" as a checkable set (span-recall holds, three D5 doors pass census, every dimension has measured evidence, all events placed, gates green), sequences cleanly (measure → preconditions → place R4 → extract only where red), and commits to "no extraction before measurement." E is close but A's structure is tighter and more executable.

**2. Biggest blind spot: B.** It is pure critique with no constructive plan. It identifies real problems (27.4% disagreement is a confession, the 8-verb sample has no failure branch, the dimension map predates the owner's correction) but proposes *nothing*. No checkable definition, no sequence, no "what if red" path. It blocks without unblocking.

**3. All five missed:**
- The `semantics` table (0 rows, no consumer door) and the 81% untyped edges problem — no response mentions either.
- The owner's correction "I meant everything" means the 12+3 dimension map itself is unverified; D flags this but no response proposes the 50-question open-ended census as a hard gate *before* any other work.
- No one specifies the concrete census size (N questions per dimension) or the pass threshold. "Fixed question census" is asserted but never defined, leaving "done" ambiguous at execution time.

**Peer review 4:**

**1. Strongest: E.** Only it prices the hidden costs: under "no third corpse" R1 needs a consumer door + reach census — unpriced by all — and "verify the door exists before measuring" kills the null-census fiction. It retires R2 (3C-GREEN), parallelizes R4, and its 6-item done checklist with gate numbers is the most checkable set. A is close but leaves R2 in play and the door-cost unpriced.

**2. Biggest blind spot: C.** It conflates reach with comprehension: a green roster/narrative door proves you can *serve* chronology, not that the corpus *understands* it. C's "done sooner — everything, verified" rests on the 12-dimension map, the pre-correction proxy B and D attack; C packages a bounded claim as the owner's "everything," and pre-judging B's critique as a "fatal error" seals the blind.

**3. All five missed:** The failure branch. B flags that the 8-verb sample has no if-fails path; none designs one. With user input banned, a pre-committed rule is required (e.g., >X% unexpressible → new-verb council/scope memo). No one also treats the map's 3 additions — outcomes ("who won"), causality ("why") — which no layer models; they are the extraction most likely owed, and appear in no done criterion.

**Peer review 5:**

**1. Strongest: E.** Only response that sequences correctly (doors → preconditions → R4 in parallel), prices R1's hidden cost (extractor + consumer door + census under "no third corpse"), and delivers a checkable 6-item done list (incl. halt-before-P6) while correctly retiring R2 (3C-GREEN). A converges on the same order but is thinner: no R1 door cost, no R2 retirement, weaker done-list.

**2. Biggest blind spot: C.** Treats the unmeasured doors as pure upside ("done sooner") and assumes the pre-correction 12+3 map is exhaustive "everything" (the gap D flags). No failure branch: if the narrative door is red or the 8-verb sample needs a 9th verb, C freezes mid-run with no user input — B's exact warning — and never schedules the gate's false-negative rate.

**3. All five missed:** No one schedules a placement-gate **error-rate** (false-negative) measurement as a checkable done-condition — B names the number that matters but none turns it into a measured gate/done item. All five also ignore the existing empty `semantics` table (0 rows, no consumer door), R1's natural home under "no third corpse," and none sequence around the GPU constraint (Qwen owns the card for LLM batches; any R1/R3 extraction must fit before the P6 halt).

Produce the council verdict using this exact structure:

## Where the Council Agrees

[Points multiple advisors converged on independently. These are high-confidence signals.]

## Where the Council Clashes

[Genuine disagreements. Present both sides. Explain why reasonable advisors disagree.]

## Blind Spots the Council Caught

[Things that only emerged through peer review. Things individual advisors missed that other advisors flagged.]

## The Recommendation

[A clear, direct recommendation. Not "it depends." A real answer with reasoning. This verdict will be executed without further user input, so state the sequencing as an explicit ordered plan with failure branches pre-committed for each measurement that could go red.]

## The One Thing to Do First

[A single concrete next step. Not a list. One thing.]

Be direct. Don't hedge. The whole point of the council is to give the user clarity they couldn't get from a single perspective.
