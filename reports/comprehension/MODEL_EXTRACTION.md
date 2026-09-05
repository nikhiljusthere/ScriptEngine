# Phase 2 — Model extraction: events over the placement set

Subject: the whole `jjk` placement set (108 pages: 9 event + 90 battle +
9 story_arcs). The question Phase 1's door test answered for *one* page with
hand-written rows, Phase 2 answers for *all* of them with a model, gated so
nothing unverified reaches the table.

## The data

108 pages, **532 events, 0 failed**. Stored with `model=qwen3.8-27b-ninfer`,
`prompt_version=events-2026-09-05.2`, `revid=0` (the jjk corpus is revid-0, so
the cache key is the prompt version).

The version is `.2`, not `.1`: between the two the participant set tightened
(see the container gate below), so a row read under `.1` is not the row
`.2` would read, and the key must say so or a stale page skips re-extraction.

## How a page becomes rows

`events-extract` walks each placement page's prose sections
(`extractable_sections`, list-sections and extraction-only `Timetable` /
`Interactive Map` excluded) and, per window of each section, asks the model for
`{subject, verb, object, quote}` events. Every candidate row is gated before it
is stored:

- **verb** in the closed `EVENTIVE_VERBS` set — no synonyms, no tenses.
- **both ends resolve** to a real `nodes.id` (name or alias) via
  `known_participants`. A name the wiki has no page for is dropped, not guessed.
- **quote is verbatim** in the section that states it (`_quoted_in`).
- **container gate**: an end whose page is a *container* of events — a battle,
  arc, saga, story_arc, chapter or episode (`NON_PARTICIPANT_TYPES =
  PLACEMENT_TYPES | {chapter, episode}`, 471 nodes on jjk) — is not a
  participant in one. Without this the model, unable to find a character's
  name, fell back to the page it read and produced rows like
  `Jujutsu Sorcerers vs. Dagon fought Dagon`. Those are now rejected at the
  gate; the same passage instead yields the individual characters
  (`Yuji Itadori fought Jiro Awasaka`).

`time_rank` is never the model's: it is looked up from the section's place on
the page's clock axis (`section_time_ranks`, carry-forward — a clock-titled
section takes its heading hour, a non-clock section inherits the last hour
before it, and a page with no clocks falls back to ordinal).

## The thinking-model knob

`qwen3.8-27b-ninfer` is a reasoning model: at full effort it spends ~20k tokens
(a hundred seconds) *thinking* on a passage one pass reads in eight, and a
2k/8k/16k answer budget is consumed by reasoning with no answer at all.
`reasoning_effort: low` brings a window to ~8s and a correct answer. That field
exists only on servers that validate it, so it travels as an opt-out:
`_effort_body()` reads `SCRIPTENGINE_EVENTS_REASONING_EFFORT` (default `low`)
and, when set, is merged into the request as `extra_body` — a new additive
parameter on `LLMClient.complete` / `complete_with_usage` / `_local` that is
`None` by default, so every caller that predates it sends exactly the request
it always sent.

## Verified

- **Zero** stored row has a subject or object that is a container page.
- The Phase-1 door test re-passes on the model's own Shibuya rows: with
  `SCRIPTENGINE_EVENTS_ORDER=1` the `10:01 C Tower` beat moves from position 8
  to 11, behind the `9:22` / `9:27` / `9:40` beats, and every beat's start time
  is non-decreasing. Flag off, the article's own (out-of-order) order is
  untouched.
- Known alias collisions in the *wiki data*, flagged for Phase 5 (not code):
  `gojo` → `Sorcerer Clan`, `ryomen sukuna` → `Volume 1`.

## Standing gates (flag off)

| gate | baseline | phase 2 |
|---|---|---|
| pytest | 1137 passed | 1137 passed |
| eval jjk | 24/24 | 24/24 |
| span-recall jjk | 48,570/48,572 (2 misses, rc=2) | 48,570/48,572 (2 misses, rc=2) |
| canon-run opm | 10/16 · 236/236 · 79.0% | 10/16 · 236/236 · 79.0% |

The events table and its methods are reachable only from the `events` /
`events-extract` commands, the `SCRIPTENGINE_EVENTS_ORDER` flag, or
`seed_phase1_rows`. Nothing on a default path touches them, so the gates are
structurally unaffected and were re-run clean.

## Residuals

- Self-directed `arrived` rows (`Aoi Todo arrived Aoi Todo`) are the allowed
  self-directed case, quote-backed; a minor modelling artifact, not wrong data.
- Arc pages carry no clock, so their rows fall back to ordinal `time_rank`
  (correct, just coarse).

## Commands

```
SCRIPTENGINE_LLM_BASE_URL=http://localhost:18080/v1 \
SCRIPTENGINE_LLM_MODEL=qwen3.8-27b-ninfer \
SCRIPTENGINE_EVENTS_REASONING_EFFORT=low \
python -m scriptengine.cli events-extract --series jjk --workers 4
python -m scriptengine.cli events --series jjk
SCRIPTENGINE_EVENTS_ORDER=1 python -m scriptengine.cli timeline --series jjk "Shibuya Incident" --max-beats 40
```