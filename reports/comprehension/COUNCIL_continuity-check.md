# COUNCIL — design the continuity-check scaffold

Date 2026-09-05. Standing rule: a council pass before the D6-consumer scaffold.
Method: 5 advisors (contrarian / first-principles / expansionist / outsider /
executor) → anonymized A–E → 5 peer reviews (skeptic / pragmatist / formalist /
domain-expert / fresh-eyes) → every load-bearing claim re-verified against code +
DB before recording (ledger at bottom).

## The question

The placement-signal fix is done (NULL `arc_index` 2,034 → 154; 2,594 placed). The
time axis now orders every placed event by `arc_index`. Design the **continuity-
check** — the D6-consumer, validation-layer scaffold whose stated purpose is
"ask what a character knew at a given moment, and reject a script line referencing
an event three arcs early; deterministically testable." Constraints from the
scoping council: scaffold-only (no production wiring), model-free (no LLM in the
check), a lookup/subtraction not a guess; and the plan's hard rule — *write twenty
real failing script lines before any D6 GPU-week, or the event graph is not yet
the highest-value work.*

## Verdict

**Build a gap *detector*, not a rejector — and seed the gold set from the
triaged 107, not the raw 107.** The council's one-line answer to the five
decisions:

| Decision | Verdict |
|---|---|
| 1. what it checks | **the gap, as a flag**: `gap = claimed_arc − actual_arc`. (a) is the atomic per-beat subtraction; (b) is (a) composed over a beat walk and ships *with a flashback/recap exemption class*, not a hard reject. The "three arcs early" number is a **policy knob**, not the check. |
| 2. input shape | a **structured beat** `{line, source (chapter/episode), subject, verb, object}` — not a bare event id (an id can't fail; it just echoes the axis). No verb/participant *parsing* (that is LLM work); the scaffold takes structured beats, the consumer parses prose. |
| 3. where it lives | `scriptengine/ingest/continuity.py`, sibling of `gate.py`; pure functions over `FactStore`, no model; a `continuity` CLI door mirroring `time-axis`. Scaffold-only: no `api/` import, no `verify` hook. The consumer (the D6 write-layer, named at `GATE.md` "Owner of the 116") is where this gets wired. |
| 4. is the 107 the gold set | **No — the *triaged* 107 is.** The raw 107 is a mixed population (26 boundary straddles + 50 state-verb artifacts + 31 interaction-verb anachronisms). Seed the gold set from the **31 interaction-verb, gap≥2** filings only. The **either-direction continuity detector** (out-of-order, premature *or* delayed) has **31 ≥ 20 → its bouncer passes now.** The **premature-only** subset (the plan's literal "three arcs early") is **9 < 20** — that is the honest "what-X-knew" signal, reported, not hidden. The "correct arc" is the **cross-page majority filing**, a corpus truth independent of the axis under test, so the set is **not circular**. |
| 5. minimal scaffold | `triage_filings()` (class split + gap histogram = the residual disposition) → a frozen `gold_continuity.json` (20-draw of the 31) → `beat_gap` / `walk_monotonicity` / `knowledge_frontier` → the `continuity --gold / --triage / --frontier` door + a coverage line. Cut: `--line`/`--beats` parsing, hard-reject, 8-corpora claims. Half a day, zero GPU. |

## What the council corrected (verified against code + DB)

1. **The 107 is not a violations set — it is three classes, and two are
   legitimate.** Triage (measured): 26 are *adjacent* (`arc_span==1`, an event
   straddling an arc boundary — legitimate); 50 are *state-verb* filings
(`arrived` 30, `departed` 20) — a character genuinely arriving/departing in
    many arcs, the coarse-key artifact ("Gojo arrived" is true in six arcs, not an
    error); **31 are interaction-verb, gap≥2** (`fought` 12, `saved` 10, `killed` 5,
    `awakened` 4) — the true anachronism core. **Direction matters, and it was
    checked, not assumed**: of the 31, **9 are premature** (a filing at least two
    arcs *early* of the adjudicated truth — the plan's literal "three arcs early")
    and **22 are delayed** (a filing at least two arcs *late*). Seeding the gold
    set from the raw 107 (A/D/E's "20 of the 107") bakes the 50 state-verb
    artifacts into the acceptance set. **VERIFIED** (the 107's class triage +
    direction split, below).
2. **The "correct arc" is the cross-page majority, so the gold set is not
   circular.** For a disputed filing the *actual* arc is the arc the **majority**
   of independent pages file it under — a corpus truth, not the single `arc_index`
   position the check is validating, and not an LLM adjudication. The *claimed*
   arc is the beat's sourced chapter via `chapter_arc_index`, which reads the
   `facts` table (battle-page `arc`+`chapters`), **not** `events.arc_index` — so
   both sides of `gap = claimed − actual` are independent of the axis under test.
   **VERIFIED** (`cross_page_agreement` `majority_share`; `chapter_arc_index`
   reads `facts`, timeaxis.py:183).
3. **"What X knew" is a subject-scoped prefix read, not a belief-state oracle.**
   A belief-state check ("did A know the reveal yet?") is unanswerable from placed
   event data without an LLM (breaks the model-free rule). What the axis actually
   gives, for free, is the **knowledge frontier**: every event a subject
   participated in (as actor *or* object) up to arc *n* — a plain
   `SELECT … WHERE arc_index <= ? AND (subject=? OR object=?)`. **VERIFIED**
   (frontier query: Yuji Itadori → 386 events ≤ arc 7, 298 ≤ arc 6, 447 total).
4. **Monotonicity (b) must carry a flashback/recap class, not a hard reject.**
   JJK re-tells the past (recap episodes, the Culling Game's Heian-era
   intra-arc flashbacks), so a backward `arc_index` jump is legitimate structure,
   not an anachronism. The check *flags* the jump; an explicit exemption class
   marks the legitimate ones. A threshold without the class false-positives.
   (Domain-grounded, not DB-verifiable.)
5. **The "no named consumer" premise is partly moot.** `GATE.md` already names
   one — "Owner of the 116: the continuity-check consumer" — the D6 write-layer
   that will consume the 116 arcless rows. The scaffold is scaffold-only because
   that consumer is *not built yet*, not because it is *unnamed*. The hand-off
   contract is written into the module docstring.

## What the council left open (deferred to the consumer)

- **The twenty *real script* failures do not exist yet.** `scripts output/` holds
  one early script with no per-beat `sourced:` headers, so the plan's strongest
  form — "a line that came out wrong" — cannot be harvested now. The gold set is
  therefore **corpus-derived** (the 31 interaction-verb filings, each a line
  claiming an out-of-order arc, correct answer = the majority/adjudicated arc). It
  satisfies the bouncer's *count* (31 ≥ 20); the strongest *form* (harvested real
  D6 failures) arrives with the named consumer.
- **The "what-X-knew" subset is thin and that is the honest finding.** Of the 31,
  only **9 are premature** (a filing ≥2 arcs *early* of the adjudicated arc) — and
  a *delayed* reference (an event from an earlier arc, 22 of them) is not a
  knowledge error, since past events are already known. So the knowledge-frontier
  purpose rests on 9 corpus cases, below the bouncer's 20: if the consumer's job
  were *only* "what did X know," the D6 week would not fire on count. The
  either-direction continuity detector (31) is what passes. Both numbers ship in
  the triage line; neither is rounded away.
- **The threshold is a knob, not a constant.** The data shows gap≥2 is the common
  regime (17 at span 2); "three arcs early" is the plan's number. Expose it, do
  not assert it.
- **Sub-arc precision is out of scope.** The axis carries `(arc_index,
  time_rank, section ordinal)`; the check is at the 9-bucket `arc_index`. A
  same-arc anachronism (wrong beat within an arc) is invisible here by design —
  it is the consumer's finer problem.
- **8-corpora inheritance is a claim, not a fact.** The axis reads the wiki's own
  `chronology.chains`, so it *should* be series-agnostic; JJK's 2,594/2,748
  placement rate does not transfer. Unverified on the other seven; do not ship
  the claim.

## Minimal runnable path (executor)

1. `triage_filings()` → the 26 / 50 / 31 class split + the span histogram (this
   is the "residual disposition" line). Measured now.
2. The 31 interaction-verb, gap≥2 filings (9 premature + 22 delayed) → freeze a
    20-draw (largest gap, lowest majority share = the cleanest) as
    `scriptengine/eval/gold_continuity.json`. Each case:
    `{verb, participants, claimed_arc_index (out-of-order filing), actual_arc_index
    (majority), gap, direction}`. The 9 premature ones double as the
    "what-X-knew" subset.
3. `continuity.py` (~120 lines, reuses the timeaxis lookups): `beat_gap(store,
   beat)`, `walk_monotonicity(store, beats, flashback_class=…)`,
   `knowledge_frontier(store, subject, upto)`. Pure, no model, no api.
4. `continuity` CLI door (`--gold` exit 0/1, `--triage`, `--frontier --subject --upto`)
   + a coverage line (`placed 2,594 / placeable 2,594 = 94.4%; 154 correctly
   unplaceable → standing states`).
5. `tests/test_continuity.py` mirroring `test_gate.py`. Cut `--line`/`--beats`,
   hard-reject, 8-corpora.

## Verified-claims ledger (checked against code/DB before recording)

- The 107 = 26 adjacent + 50 state-verb + 31 interaction-verb(gap≥2); 62
  `modeling_problem` — **VERIFIED** (triage query: `arrived` 36 / `departed` 24
  overall, `fought` 20 / `saved` 12 / `killed` 9; large-gap `arrived` 30 +
  `departed` 20 = 50, interaction 12+10+5+4 = 31).
- The either-direction continuity detector has 31 ≥ 20 → its bouncer passes on
  count — **VERIFIED** (31 = 9 premature + 22 delayed, measured by direction).
- The premature-only "what-X-knew" subset is 9 < 20, the honest thin signal —
  **VERIFIED** (direction split, measured).
- `chapter_arc_index` reads `facts` (battle `arc`+`chapters`), independent of
  `events.arc_index` — **VERIFIED** (timeaxis.py:183–203).
- The adjudicated "actual" arc is the cross-page majority, a corpus truth —
  **VERIFIED** (`cross_page_agreement` `majority_share`, gate.py:133).
- The knowledge frontier is a free, correct SELECT (subject OR object,
  `arc_index <= n`) — **VERIFIED** (Yuji: 386 ≤ 7, 298 ≤ 6, 447 total).
- `GATE.md` names the consumer ("Owner of the 116") — **VERIFIED** (GATE.md:217).
- `scripts output/` has no per-beat `sourced:` headers to harvest yet — **VERIFIED**
  (one early script, no `sourced:` lines).

## One next step

Implement the scaffold exactly as the minimal path: `triage_filings()` +
frozen `gold_continuity.json` (20 of the 31) + `continuity.py` (three pure
functions) + the `continuity` CLI door + `tests/test_continuity.py`. The triage is
already measured (26/50/31) and the frontier query verified, so the code is
mechanical; the one judgment call left is the 20-draw, which is "largest gap,
lowest majority share" — a fixed, defensible rule, not a taste.