# flow.md — the phase graph

**This file holds structure, never status.** No checkboxes, no progress counts,
no "current phase". Structure does not go stale; status does — four phantom
work items came from a document that tracked what remained. Status comes from a
query, never from this file. See `Plan_to_perfection.md` §0 and §15.

**Every step is a suggestion carrying a premise.** Check the premise first.

```
PREMISE   : the assumption the step rests on
VERIFY    : the exact command that confirms or refutes it — and STATE WHICH TREE
            it ran in (a verification on a stale worktree is worse than none)
IF HOLDS  : do the work
IF REFUTED: HALT. Log to deviation_reasons.md with the raw output that refuted
            it. Surface. Do NOT substitute a different action.
```

**Refusal authority, not substitution authority.** A refuted premise stops the
step. It does not authorise doing something else instead.

**Every phase ends in a GATE, never a hand-off.** A gate requires emitted query
output. It is never "continue to the next phase now."

**The run is continuous.** A green gate advances to the next phase
automatically — no pause for approval, no waiting for a human between phases.
The run ends when Phase 6 closes, not before.

> **What a gate is, now that nobody is waiting at it.** It is not a checkpoint
> for a human; it is a *precondition on advancement*. Advancement is contingent
> on emitted evidence and a council pass — never on having reached the last
> line of the phase. A bare "continue now" placed after steps the agent graded
> itself on is exactly the checkbox the false "100%" campaign would have
> ticked. A gate that fails does not pause the run for permission; it **halts**
> it, under the conditions below.

### Halt conditions — and what to do when one fires

A halt condition suspends the phase. **It does not end the run.** When one
fires:

1. **Stop the step immediately.** Do not work around it, do not proceed to the
   next phase, do not paper over it.
2. **Convene the council on the halt itself** — the framed question is the
   halt: what fired, the raw evidence, and what the phase was attempting.
   5 advisors, anonymised peer review, synthesis, serially.
3. **Then one of two outcomes, and the council does not get to choose freely:**
   - **Resolvable inside the plan as written** → apply the fix, re-run the
     check that fired, and **continue the run**. Record the halt, the council,
     and the resolution in `deviation_reasons.md` and the phase council report.
   - **Not resolvable inside the plan** — it needs scope that is not written
     here, or a decision only the owner can make, or it is a genuine
     irreparable regression → **stop and report.** This is the only stop before
     Phase 6 closes.

> **The council may repair a halt. It may never re-interpret one.**
> A council cannot rule that a fired condition did not fire, that a regressed
> number is acceptable, that lost rows did not matter, or that a floor should
> be lowered to fit the result. Those are re-interpretations, and a council
> that can clear its own halts by redefining them is the self-grading loop this
> whole structure exists to break. **Conditions 1, 2 and 4 below are
> non-negotiable in this sense:** the council may find and apply a *fix*, but
> the condition stands until the *evidence* changes.

**The conditions:**

1. **A standing gate regresses** below baseline: `pytest`, `eval jjk` 24/24,
   `canon-run opm` 10/16 · 236/236 · 79.0%, `span-recall`.
2. **An oracle item that previously passed now fails.** Regression in served
   behaviour outranks progress on any dimension.
3. **A premise is refuted** (per the step contract) — always a halt.
4. **Derived-row loss:** any table's row count drops without an explicit step
   in this file that intends it.
5. **A batch scores below its stated floor** — the extraction is wrong, not the
   data.
6. **Two consecutive phases close with no movement on their own metric** —
   stuck, escalate rather than grind.
7. **Any action that would require scope not written in this file.**

### Authorising the large GPU pass without a human

The 24,000-sentence `meaning` pass was held as "not authorised." Under a
continuous run nobody is waiting to authorise it, so **its preconditions are
the authorisation.** It proceeds automatically once all four are green, and
not before:

1. **Retention solved** — Phase 0C landed; a rebuild demonstrably remaps
   survivors instead of wiping them.
2. **Frozen class spec + prompt v1**, coupled to `PROMPT_VERSION`, with the
   participant guard in place.
3. **A pilot** on the 1,748 chapter-anchored rows, **scored against
   `ORACLE_v1.yaml`** — not merely "the guard fired."
4. **The pilot's accuracy is at or above its stated floor.** Below it, halt
   (condition 5): the extraction is wrong, not the data.

Record which of the four were green, with evidence, in the phase's council
report. Never run the pass on the strength of three.

---

## Phase 0 — Answer the open question; make the store durable

*This phase exists because the executing agent is currently blocked asking
whether to apply three pre-commit fixes and how to handle retention.*

**0A — apply the three pre-commit fixes**
- PREMISE: the `meaning` DDL is committed-but-unconfirmed, its model columns
  empty, and three defects its own council found are cheap to fix.
- VERIFY: `meaning` exists; its model-populated columns are empty.
- IF HOLDS:
  1. Rename "atemporal complement" → **"unverified complement"** everywhere,
     and fix the `schema.sql` comment that calls a NULL `arc_index` "an
     atemporal line." This one decides whether the index launders the
     extractor's recall errors into truth.
  2. Stop citing the events-key proof as validating the meaning key. It
     validates a lookup; the meaning PK is unique by construction.
  3. Add the minimal quality contract: a `CHECK` on the frozen class
     vocabulary, and state in the DDL whether `is_event` is derived or an
     independent recovery channel.

**0B — the reset guard (five lines, highest value-per-line in the plan)**
- PREMISE: `build.py` calls `reset()` unconditionally, and `reset()` drops
  `events` and `meaning`.
- VERIFY: read both; confirm on the tree you are working in.
- IF HOLDS: `build.py` refuses to `reset()` while derived tables are non-empty
  unless `--force`. A reflexive `cli index` destroying a 24,000-sentence pass
  is the one failure that costs days.

**0C — the durable key**
- PREMISE: `abilities` survives rebuilds because it is name-keyed; `events` and
  `meaning` are keyed on `section_id`, which renumbers.
- VERIFY: confirm `abilities` has no `section_id` FK and survives; confirm the
  other two do not.
- IF HOLDS: key `events`/`meaning` on `document.title` + section ordinal +
  sentence ordinal + content hash, with a remap on rebuild.
- NOTE: this was written up as a decision for the owner. The council cancelled
  it — three of four advisors independently held that copying a working in-tree
  precedent is not a design choice. The "wipe is the feature" rationale
  conflates row *ids* with row *content*; `revid` already tracks real staleness.

**0D — GATE.** Emit: the diff; the guard refusing a `reset()` on a non-empty
store; a rebuild showing `events` rows surviving with remapped keys. Run the
council. On green, continue into Phase 1 without pausing.

---

## Phase 1 — Measure before building (no GPU, may delete whole phases)

*Both steps here are cheap and either can remove scope. Neither needs a model.*

**1A — run the held-out oracle**
- PREMISE: `plan/ORACLE_v1.yaml` exists, sha256
  `a788fa29652a58152edf0f2ce16caea626db35d7e4463ec66176b5635a15935e`.
- VERIFY: hash matches.
- IF HOLDS: run all 18 items under `auto`. Report per item — PASS/FAIL, what
  was served, routed door — and **totals split by category, never an aggregate
  alone.** Report both kinds of surprise against the recorded `expect`.
- **You run this file. You never edit it.** An item that looks wrong is a
  finding to report, not a licence to change it.

**1B — the eight-verb coverage measurement**
- PREMISE: the extractor's vocabulary is `fought / killed / saved / arrived /
  departed / awakened / sealed / betrayed`, and nobody has recorded what the
  other verbs were.
- VERIFY: confirm the closed set in `events.py`.
- IF HOLDS: sample 100 random plot-summary sentences. For each, record whether
  the eight verbs can express what it describes. **Report the fraction they
  cannot hold, with the sentences.** No model needed — only reading.
- This decides whether 2,594 events are a foundation or a sample.

**1C — GATE.** Emit both reports, run the council, and continue into Phase 2 on
green. Two results change the plan directly, and you act on them yourself
rather than asking:
- **Oracle E1–E4 pass** → Personality is a retrieval problem, no extraction is
  owed, and ~42,500 words leave the build list. **E1–E4 fail** → a chunking
  defect, still not a missing table.
- **1B shows high uncovered fraction** → the verb set is widened before any
  further extraction, or every downstream phase inherits the gap.

---

## Phase 2 — The cheap structural wins

**2A — battle outcomes.** Battle pages carry structured outcome fields;
`events` records that a fight happened but not who won. Join them. Mechanical,
no model. Oracle items A1–A4 measure this directly.

**2B — Equipment (3,782 w) and Quotes (1,518 w).** Together under an hour on a
resident 27B. Quotes is a character's actual dialogue, for a project that
writes scripts — the smallest item on the map and plausibly the highest value.
Oracle F1–F2 measure it.
- PREMISE: oracle F1/F2 failed at 1A (i.e. retrieval does not already serve
  these). IF REFUTED: no extraction owed — halt and record.

**2C — GATE.** Emit oracle A- and F-group re-runs showing the change. Council,
then continue into Phase 3 on green.

---

## Phase 3 — Ability depth

Cursed Technique *mechanics* (13,611 w — names already extracted, behaviour
not), Physical Prowess (10,595 w), Intelligence (9,674 w), Cursed Energy
(6,416 w). Schema half-built; 594 ability names already landed across 94 of 146
characters.

- **3A** widen `abilities` to all 146 characters, with an explicit "no
  abilities" for those that genuinely have none.
- **3B** extract mechanics, not just names.
- **3C — GATE.** Council, then continue into Phase 4 on green.

---

## Phase 4 — State over time

*The load-bearing dimension for script writing, and nothing models it today.*

What was **true** of a character during an arc: grade, allegiance, alive/dead,
sealed, possessed. A Shibuya scene cannot be written without knowing Gojo is
sealed from that point. Oracle B1–B4 measure this; B1/B2 are expected to fail
today and exist to size the gap.

- **4A** model intervals (state, start arc, end arc, source quote).
- **4B** populate from infobox facts carrying "(Former)" markers and from
  synopsis prose.
- **4C — GATE.** Oracle B-group re-run; B1 and B2 must move. Council, then
  continue into Phase 5 (or close it, per its premise) on green.

---

## Phase 5 — The subjective set, gated behind retrieval

Personality (42,533 w), Appearance (14,180 w), Overview (16,731 w), Trivia
(15,887 w), History (11,595 w).

**This phase may not exist.** It opens only if oracle E1–E4 failed at 1A. A
model that writes needs the right paragraph, cited and placed — not pre-parsed
traits. Structure earns its cost only where prose cannot do the job: joins,
ordering, filtering, aggregation, state-at-a-moment.

- PREMISE: E1–E4 failed, and the failure is retrieval-shaped rather than
  chunking-shaped.
- IF REFUTED: close the phase, record that ~106,000 words need no extraction.

---

## Phase 6 — Cross-corpus

Everything above is series-agnostic by construction. Seven corpora are already
crawled and indexed: One Piece 7,613 pages, Dragon Ball 7,205, Bleach 2,252,
HxH 2,018, OPM 1,571, Berserk 762, CSM 537 — JJK is ~4% of what is owned.

Order and per-corpus gates: `Plan_to_perfection.md` §7. Do not open Phase 6
until JJK's Phase 4 gate is green — a mechanism that has not survived one
corpus should not be replicated across seven.

---

## Standing rules (all phases)

- **Run continuously to the end of Phase 6.** Do not pause between phases, do
  not ask for approval to advance, do not stop to report progress. A halt
  condition suspends a phase and triggers a council; the run stops only when
  that council finds the halt unresolvable inside this plan, or when Phase 6
  closes.
- **Council pass at the close of every phase**, before advancing — 5 advisors,
  then anonymised peer review, then synthesis, run serially since only one
  sub-agent runs at a time. **DB-verify every council claim before recording
  it.** Advisors assert things that are wrong: one recently "verified" that
  half the codebase was missing, having read a stale worktree. A council claim
  that fails verification is struck, with the correction noted.
- **Write each council to `reports/comprehension/COUNCIL_<phase>.md` and commit
  it with that phase's work.** The council is evidence, not a conversation —
  if it is not on disk it did not happen.
- Bulk extraction runs on the local model. The reviewer takes verification and
  the oracle. A 24k batch is ~4 orders of magnitude beyond reviewer quota.
- Standing gates stay green: `pytest`, `eval jjk` 24/24, `canon-run opm`
  10/16 · 236/236 · 79.0%, `span-recall`.
- Named paths only. Never `git add -A`. Do not push.
- Halt rather than work around. Log to `deviation_reasons.md` with evidence.
