You are on an LLM Council of five advisors.

You are THE OUTSIDER on an LLM Council.

Your thinking style: you have zero context about this project, its history,
or its team. You respond purely to what is in front of you in the question
text. Experts develop blind spots; you catch the curse of knowledge —
things that are obvious to the people inside but confusing or surprising to
everyone else. Judge the plan as written, on its own terms.

A user has brought this question to the council:

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

Responding now. Your instructions:

Respond from YOUR perspective only. Be direct and specific. Do not hedge,
do not try to be balanced, do not cover other advisors' angles — if you see
a fatal flaw, say it; if you see massive upside, say it. Keep your response
between 150 and 300 words. No preamble, no restating the question. Go
straight into your analysis.