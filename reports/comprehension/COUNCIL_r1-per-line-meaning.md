# COUNCIL — R1: the per-line / per-beat meaning index (design, pre-build)

The goal's core (§5): a writer can ask, of any line the wiki writes, **what it
means and where it sits**. R1 builds the per-line / per-beat *meaning* index that
makes the first clause true; it is the consumer the `semantics` corpse
(`retrieve/semantics.py`, a per-*page* classifier) was meant to serve, extended
to the *line a writer actually types*. This file is the **council's input** —
the design to pressure-test before the build. The advisors' positions, peer
reviews and the chairman's verdict are recorded below once run.

## What the council is handed

A new **`meaning`** door, read by a writer on a *line* (the wiki's prose), that
returns:

- **semantic class** — `event` / `standing state` / `trait` / `trivia` (§5's four);
- **`is_event`** (bool) — whether the line states something that *happened*;
- **participants** — the entities it is about (FK-stable, alias-resolved, never a guess);
- **`arc_index`** — the timeline position (a real arc page this wiki has), or NULL
  recorded as a *standing state* when the wiki gives no placement (mirroring
  `events` storing an unplaceable state `temporal=0`, never a guess).

Built by cloning the **`events.py` / `relations.py` model-extraction pattern**
(`scriptengine/ingest/`):

- a bounded **Qwen** batch (the extraction model, GPU-dedicated), with classification
  applied **after** the model answers, so a weaker model costs recall, not truth;
- guards: class from a **closed set**; participants resolve to real nodes; the
  **quote is verbatim** in the line's section; `arc_index` is a page the wiki
  actually has or NULL-as-standing-state;
- a `PROMPT_VERSION` bump invalidates stored rows (as `abilities` / `relations`);
- the **frozen set is a harvest of real script lines, not an invented gold**.

**Inputs already in hand (B5, re-scoped in `COUNCIL_b5-premise.md`):**

- the **107 cross-page disagreement corpus** (91 two-sided), via
  `gate.cross_page_agreement` + `continuity --triage`;
- the **refined grouping key `(verb, subject, object, chapter)`** — the chapter /
  temporal component that stops "the same pair in different arcs" (the 60
  repeat-encounters, 56%) reading as a contradiction.

**Binding standing rule:** "no third corpse" — the new `meaning` table ships with
the door that reads it.

## What is fixed (do not re-litigate)

- The **chapter component in the key** — set, not a question (the B5 re-scope;
  the 60 repeat-encounters point at exactly this).
- The **four classes** (event / standing state / trait / trivia) — §5.
- The **cloned pattern** (`events`/`relations`: closed-set + verbatim + FK-stable
  + `PROMPT_VERSION`) — spec-set.
- **Bounded Qwen GPU batch, frozen harvest** — spec-set.

## Open questions for the council

1. **Line unit + which chapter.** Is "the line a writer actually types" a
   sentence, a beat, or a section window? And the chapter in the key: the line's
   *source* chapter, the *arc's* chapter range, or a *placement* chapter? How does
   the chapter component disambiguate the 60 repeat-encounters **without
   manufacturing false precision** on the atemporal two-thirds (§2c)?
2. **Class boundaries + the escape hatch.** The event / standing-state / trait /
   trivia boundaries (e.g. "Gojo is the strongest sorcerer" = trait or standing
   state? "Shibuya fell" = event or standing state?). LLM-classified vs.
   mechanical? What is *unclassifiable*, and how is it stored (NULL-as-recorded-
   standing-state, mirroring `events`' `temporal=0`)?
3. **`arc_index` source.** Reuse `timeaxis`'s existing placement signals
   (arc-named section, chapter/episode citation — "the free signal R1's axis
   already computes," §R3) vs. new per-line inference? And the **overlap with
   R4's 154 residue** — one shared bounded inference pass, or two?
4. **Door contract + query-time cost.** The exact return (class, `is_event`,
   participants, `arc_index`, verbatim quote, provenance). Does it inherit
   `relations.py`'s "**never runs during a query**" (a pure offline read of the
   stored meaning table)? Confirm there is no query-time model call.
5. **Frozen set + pass criterion.** How to harvest real script lines; what "pass"
   means; and the anti-pattern to guard against (not tuning to one ambiguous line
   — standing rule: do not tune the retriever to make one ambiguous prompt green).
6. **Bounding + resume.** Batch size, the GPU-dedicated window (never during the
   `:8000` API), and resume / invalidation via `PROMPT_VERSION`.

## Verified-claims ledger (to be filled before recording)

- [ ] Where the door registry lives and the shape a new `meaning` door must take
      (cf. `retrieve/roster.py`, `retrieve/abilities.py`).
- [ ] What `timeaxis` already exposes for placement (`arc_index`; the three cheap
      signals — `TIME_AXIS.md` §"the three cheap signals").
- [ ] The `events` guard chain end-to-end (`events.py`: closed verb, ends resolve,
      verbatim quote, real arc, multi-page agreement, `temporal=0`) and the
      `relations` guard chain (three post-model guards + `era`).
- [ ] `semantics.py` today classifies the *page* (`semantic_type`); confirm R1 is
      the per-*line* extension and what it reuses vs. adds.
- [ ] The B5 107 corpus location + how `continuity --triage` lists the
      repeat-encounter / boundary groups.
- [ ] `PROMPT_VERSION` invalidation mechanics (cf. `abilities` / `relations`).

## Verdict (post-council)

_run 5 advisors (independent) → 5 peer reviews → chairman synthesis; record here
with the verified-claims ledger filled._

## Open (recorded, not acted on)

_(none yet)_