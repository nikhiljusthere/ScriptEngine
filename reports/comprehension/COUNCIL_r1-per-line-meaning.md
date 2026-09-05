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
   manufacturing false precision** on the unverified two-thirds (§2c)?
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

## Verified-claims ledger (filled by the chairman, pre-verdict)

- [x] Where a door lives + the shape a new `meaning` door takes. A "door" is a
      FastAPI endpoint (`api/main.py:306` `/abilities/{series}/{entity}` →
      `retrieve.abilities.collect_abilities`) + a `retrieve/` reader + the `ingest/`
      extractor that populated the table. So the `meaning` door = a
      `/meaning/{series}/…` endpoint + a `retrieve/meaning.py` reader +
      `ingest/meaning.py` + a `meaning` table in `stores/facts.py`. There is no
      central "door registry" object; doors are endpoints + retrieve modules.
- [x] What `timeaxis` exposes for placement. `events.arc_index` (a stored column,
      `timeaxis.py:44-47` recompute via `backfill_event_arc_index`) from **three
      cheap signals** (`TIME_AXIS.md:13-34`): 1 arc-page (the page *is* an arc, 9),
      2 arc-fact (page carries an `arc` fact, 97), 3 citation (page carries a
      `chapters` fact → arc via `chapter_arc_index`, 1); 1 residue (inference).
      `section_arc_index` (`timeaxis.py:110`) is a *computed* dict, **338/7,601**
      sections — not a stored table.
- [x] The `events` guard chain end-to-end (`events.py`): closed verb
      (`EVENTIVE_VERBS:42`), ends resolve (`_name_in:500,578`), verbatim quote
      (`_quoted_in:487`), real arc, post-model guard (`:1042`), `temporal=0`
      stored (never dropped). `relations`' three post-model guards + `era`
      (`relations.py:16` "never runs during a query", runs on two section titles
      at `:66`). Verified at the cited lines.
- [x] `semantics.py` today classifies the *page* (`semantic_type`); R1 is the
      per-*line* extension. Confirmed.
- [x] The B5 107 corpus + `continuity --triage` (`cli.py:801,880`); the 107 =
      60 key-coarse + 21 boundary-noise + ~0 true misplacements (a *corpus*, not a
      defect — `COUNCIL_b5-premise.md`).
- [x] `PROMPT_VERSION` invalidation (`abilities.py:54` comment "Bump to invalidate
      every stored relation"; `events.py:1160-1179` resume on `(revid,
      PROMPT_VERSION)`).

**Live-verified data claims (checked against `series/jjk/facts.db` this run):**
- [x] `events`: **2,748** rows; **no chapter column** (columns: `subject_node,
      subject_name, object_node, object_name, verb, arc_key, section_id, quote,
      temporal, time_rank, arc_index, revid, prompt_version, model, extracted_at`);
      **154** rows `arc_index IS NULL` (the R4 residue); **112** distinct
      `(subject_name, verb, object_name)` triples split across 2+ `arc_index` (of
      774 placed) — the live proof the key's temporal component splits real data.
- [x] `sections`: **7,601** rows. The `chapters` fact (the only per-line "chapter"
      in the store) is carried by **99** nodes.
- [x] **Correction to the brief:** the "7,548/48,572 (87%) carry a chapter
      locator" figure is wrong — 7,548 is a corpus-wide *ref count* (not in
      `facts.db`/reports) and 7,548/48,572 = **15.5%**, not 87%; the honest
      coverage numbers are the 99-node `chapters`-fact count and the 338/7,601
      `section_arc_index`.

## Verdict (post-council)

Five advisors ran independent, then five peer reviewers (anonymized A–E, each
weighted to a failure mode: consistency / writer / buildability / data-DB /
goal-scope), then this synthesis. Position letters: **A**=Outsider,
**B**=Expansionist, **C**=Executor, **D**=Contrarian, **E**=First-Principles.

**Where the council converges (high confidence):**
- Line unit = the **sentence** (the `split_sentences` atom, `index/chunker.py:106`)
  — not a section window, not a writer-composed beat. (A/B/C/E)
- The chapter component = the line's **source locator or NULL** — the section's
  own `chapters` fact (a real wiki locator; 99 nodes carry it, mapped to an arc by
  `timeaxis.chapter_arc_index`, `timeaxis.py:183`), recorded NULL for the unverified
  two-thirds that carry none. **Not** an arc range, **not** a placement inference.
  (A/B/C/E. Source confirmed: the `events` table has **no chapter column**, so the
  `meaning` table must carry it as a **new column sourced from the `chapters`
  fact, never guessed**.)
- `arc_index` for event-class lines **reuses `timeaxis`'s three cheap signals**
  (`section_arc_index`, `timeaxis.py:110`, 338/7,601 sections); unplaced lines
  are **structurally NULL** — the wiki doesn't place them, and NULL-as-standing-
  state (mirroring `events.temporal=0`) is the *recorded* answer, never a dropped
  row (span-recall is the gate). (A/B/C/D/E)
- The door is a **pure offline read** — `relations.py:16` "never runs during a
  query"; no query-time model call. (all five)
- Rows are **FK-keyed** (like `events`, not name-keyed `relations`), so a
  re-crawl/renumber invalidates cleanly; clone `ensure_events` +
  `_migrate_events_to_fk` (`facts.py:1038`, `facts.py:1112`). (B/C; the FK
  machinery exists and was checked.)
- `is_event` is **derived** (`class == event AND arc_index IS NOT NULL`), not
  LLM-guessed; the class comes from a closed set applied *after* the model
  answers, so a weaker model costs recall, not truth. (B/C/D/E)

**Where the council clashes (the rulings the build needs):**
1. **Scope / price: whole-corpus (48,572) vs complement (~32k unverified).** B
   wants 100% row coverage (every line gets a row); E scopes R1 to the
*complement* — the unverified two-thirds `events` can't see (events' 2,748 rows
    already carry the event 1/3). The unverified ~32k is the real cost center and
   **no one priced it** (D names the OOM-class risk + unpriced `PROMPT_VERSION`
   iteration; C's `--refresh` is the unpriced full re-run). *Ruling: bound R1 to
   the unverified complement + a bounded harvest, not 48k; event-class lines stay
   in `events`, R1 points to them or stores a thin `class=event` row — do not
   re-run events' 2,748 through a new unbounded window.*
2. **R1 vs R4 shared-pass.** E: R4's 154-residue (the 154 `events` rows with
   `arc_index` NULL, confirmed live) is a **separate bounded job** — R1 must not
   absorb it. B/C lean "one shared pass" (R4's 154 is a subset that reads R1's
   table). Reviewer-1 notes the A/B/C "convergence" is really 3-1; Reviewer-3 notes
   one-pass contradicts B5's "sibling-propagation multiplies correlated errors,
   gate behind a spot-check." *Ruling: keep R4's 154-residue placement as its own
   bounded pass that **reads R1's output**; R1's `arc_index` is class-conditional
   (event-class lines reuse timeaxis; unplaced lines structurally NULL) — do not
   manufacture placement for lines the wiki left unplaced.*
3. **Participants: strict FK-guard vs unresolved marking.** D: the cloned
   "never a guess" FK guard (`events.py:709`, `_name_in:500,578`) **guts the
   unverified payload** — it empties `participants` on exactly the trait/trivia
   lines the writer narrates (a voice actor, e.g. Gojo's VA Junya Enoue, is not a
   node). A's fix: make "never a guess" **class-conditional** — strict FK for
   event-class, mark non-node entities `unresolved` (don't drop) for trait/trivia.
   B presumes participants inline into `Beat.participants` at near-zero cost
   (contradicted by D's empty-payload point). *Ruling: class-conditional — strict
   FK-resolved participants for events; `unresolved`-marked for trait/trivia. The
   guard is kept (no invented entities), but "can't resolve" is a stored value,
   not a dropped field.*

**Blind spots the council caught (all five missed):**
- **No field carries the line's actual *meaning*.** The four fields are metadata
  (kind / eventness / cast / location). "class=trivia is a bucket, not an
  interpretation" — the door as designed answers *what-kind + where*, not *what
  it means*. (Reviewer 2, the Writer.) This is the §5 goal question: is R1 a
  **classifier+locator** (the cloned pattern, what the council converged on) or a
  **meaning-explainer** (a stored free-text gloss — a different, riskier prompt
  that sits in tension with the project's verbatim-truth + anti-AI-prose ethos).
  *Ruling: proceed with classifier+locator as the bounded build; record the gloss
  question as an open values call for the project owner.*
- **No stored chapter column exists** (`events`: `arc_key`+`arc_index`+
  `section_id`; no chapter). The "fixed" chapter-in-key premise has no schema
  backing — it must be a **new column on the `meaning` table**, sourced from the
  `chapters` fact (`timeaxis.chapter_arc_index`, `timeaxis.py:183`), NULL for the
  unverified 2/3. (Reviewer 4)
- **The "7,548/48,572 (87%)" stat is wrong** (A): 7,548 is a corpus-wide *ref
  count* (not in `facts.db`/reports) and 7,548/48,572 = 15.5%, not 87%; E's
  12.8%/24% are mis-scoped (Shibuya-Incident-page, pre-Ref-backfill). The honest
  numbers are the 99-node `chapters`-fact count + the 338/7,601
  `section_arc_index`. (Reviewer 4)
- **Double-written field, no authoritative table.** Event-class lines would live
  in *both* `events` and R1; a `PROMPT_VERSION` bump rebuilds one not the other →
  divergence after every re-extract, on top of the live 112-split. Need a
  **duplicated-vs-pointer** decision + one authoritative source. (Reviewer 1)
- **Invalidation coupling.** Inheriting `events`' page-level resume (`revid` +
  `PROMPT_VERSION`, `events.py:1160-1179`), but a whole-corpus per-line index
  needs **per-line content-hash invalidation** (C's `(section_id,
  sentence_ordinal)` key has no line-text hash); and if R1 inherits from / shares
  a pass with `events`, the key must track `events`' `PROMPT_VERSION` too.
  (Reviewers 3, 5)
- **Pass circularity.** "Match the label" is undefined on the 107 (a
  *disagreement* corpus — no ground truth) and the 154 (NULL by definition); only
  harvested *script* lines carry labels, and no one authors them. (Reviewer 4)
- **Input identity / the door itself.** All five designed only the *extraction*
  side; none says how a writer-typed line resolves to a stored row. The "no third
  corpse" rule means the table ships with the door, but the door's input is
  either a wiki line (a `(section_id, ordinal)` lookup — trivial) or a
  **writer-typed line** (needs text matching / FTS5 over the verbatim `quote`).
  (Reviewers 2, 3, 4; D.)

**The one thing to do first (Monday, no GPU):**
Decide the two rulings that change the schema — (1) **classifier+locator now,
gloss later** (record the open values call), and (2) **bound R1 to the unverified
complement + a bounded harvest, R4's 154 stays separate** — then write
`ensure_meaning()` + the `meaning` table DDL in `stores/facts.py` (FK-keyed
sentence rows: `section_id`, `sentence_ordinal`, `content_hash`, `class`,
`is_event`, `participants` [FK-resolved + `unresolved`], `arc_index` NULLable,
**`chapter` NULLable (new column, from the `chapters` fact)**, `revid`,
`prompt_version`), plus a pure-SQL backfill that (i) demonstrates the
events-key lookup **splits the 112 live triples today** (a lookup, not proof of
the meaning key — the meaning PK is unique by construction), and (ii) prints the
unverified-complement size + the `chapters`-fact coverage so the batch is bounded
and priced. This demonstrates the key lookup and bounds the price before any GPU
window.

## Open (recorded, not acted on)

- The **meaning-gloss values call** (classifier+locator vs meaning-explainer) —
  the project owner decides; the build proceeds on classifier+locator.
- **Door input identity:** wiki-line `(section_id, ordinal)` lookup vs
  writer-typed-line FTS5 match — spec the contract before the endpoint.
- **Authoritative-source ruling** for the double-written event fields (pointer vs
  duplicate between `events` and `meaning`).
- **Frozen-set labels:** who authors them + a class-stratified (not event-biased)
  pass criterion.
- **Invalidation coupling:** track both `meaning.prompt_version` and
  `events.prompt_version` where R1 reads events.