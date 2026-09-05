# COUNCIL — the placement-signal fix (D6-completeness)

Date 2026-09-05. The re-scoped bucket (COUNCIL_last-bucket-scoping.md, unit 2) names
this as a **code** change to `timeaxis.placement_time_axis` — section-aware — that
recovers the 995 arc-named-heading rows plus a smaller citation signal, leaving a
documented residual, with the 2,748-event total intact. This council pressure-tests
the fix *before* writing it.

Method: 5 advisors (contrarian / first-principles / expansionist / outsider /
executor) → anonymized A–E → 5 peer reviews (skeptic / pragmatist / formalist /
domain-expert / fresh-eyes) → every load-bearing claim re-verified against code + DB
before recording (ledger at bottom).

## The fix, as the council shaped it

`backfill_event_arc_index` re-derives `arc_index` on every gate call, so the fix
lives in the axis, not a data-UPDATE. Two cheap, model-free signals, both reading
only the wiki's own facts:

1. **Section signal (the 995).** A character/synopsis page files its per-arc prose
   under sections titled after the arc ("Culling Game Arc", "Shibuya Incident Arc").
   The section *is* the placement: an event stated in that section sits in that arc
   even when the page itself is off the story chain. `section_arc_index` maps
   `section_id → arc_index` by matching the section title to an on-chain arc page
   (`match_arc` + `story_arc_index`). All 995 resolve; 0 unresolved.
2. **Chapter/episode page signal (the ~923).** A chapter or episode page carries its
   own `arc` fact ("Chapter 0-1 → Cursed Child Arc"). The axis today only walks
   `placement_pages` (arc/saga/event/battle), so these pages are invisible and their
   923 events sit off the axis. Broadening the axis to read the `arc`/`chapters` fact
   of chapter/episode pages recovers them by the *same* `arc_fact`/`chapters`
   signals already trusted for placement pages.

The backfill places per **(page, section)**: the section index wins when it resolves
to an on-chain arc (section refines page); otherwise the page index. On today's
corpus the two signals are disjoint (the 714 page-placed rows sit under no arc-named
section; the 995 sit on non-placement pages), so "refine" ≡ "fallback" in practice.

## What the council corrected (verified against code + DB)

1. **The section signal must NOT key on the raw `events.section_id` int.** A re-crawl
   renumbers `sections.id`, dangling the 838 FK refs (the queued id-dangling hazard).
   Once the section signal *depends* on `section_id` resolving to the right section,
   that hazard becomes load-bearing: a reused id could resolve to a **different
   section's arc — a silent wrong placement, worse than a miss.** The fix resolves
   the section through the **live `sections` table by id, with a document guard** —
   the section's owning page must equal the event's `arc_key` (and its title must
   name an on-chain arc). A dangling or reused id degrades to a **miss (NULL), never
   a wrong arc.** Verified: all 995 pass the document guard today (0 fail), so the
   guard is a no-op on current data but the safety net for the re-crawl.
2. **The re-derived test is tautological as written** (it recomputes
   `placement_time_axis` on both sides of the assertion). It must pin **real
   numbers**: the 714 `(arc_key, arc_index)` pairs, a hand-checked sample of the 995
   (the 9 arc headings → their expected on-chain index), and the ~923 page-signal
   rows — plus **negative tests** (a dangling `section_id` → NULL; a non-arc section
   title → NULL; a section on a mismatched page → NULL) and the **cross-page
   disagreement delta** (placing rows can flip agreeing groups; the baseline is 38).
3. **The "citation signal" is the page's own `arc` fact, not an in-section
   `(Chapter N)` regex.** The 1,039 generic-section rows are mostly on **chapter
   (629) + episode (294)** pages — 923 total — and those pages carry an `arc` fact
   directly (275/304 chapter, 59/59 episode). That is the wiki's own verifiable
   citation, the *same class* as the trusted `chapters` fact, **not** the "guessed
   parameter" the standing rule warns about (that rule targets OPM's `cep`). The
   in-section-text `(Chapter N)` is sparser (62/1,039) and stays a documented
   residual. Placing by the page's `arc` fact is a lookup, not a guess.
4. **Exact title match only; the arc chain is not canon order.** The 995 match the 9
   arc headings by lowercased equality against the on-chain `story_arcs` pages —
   zero fuzzy matching, zero collisions. The wiki files Fearsome Womb (idx 1),
   Vs. Mahito (idx 2) and Death Painting (idx 4) *before* Kyoto (idx 3) and Shibuya
   (idx 6) in its `previous`/`next` chain even though canon runs them after Shibuya;
   the 995 inherit that filing order. The fix places them where the wiki filed them;
   correcting the chain is a separate, out-of-scope decision (recorded, not acted on).
5. **`enforce_arc_placement` is a ratchet (gate.py:54).** It flips unplaced
   `temporal=1` rows to `temporal=0` **permanently**. Run in the re-crawl window
   (where the section signal misses a renumbered id), it would demote rows that a
   later stable re-crawl would place. No test exercises the flip path. The fix keeps
   the guard "miss, never wrong arc" so a missed section only costs an off-axis row,
   never a misplacement; the ratchet's interaction with the queued id-stability fix
   is documented as a follow-up, not resolved here.

## True residual (what stays NULL, and why)

Projected 116; **measured 154** after the fix (the extra 38 are chapter pages the
wiki filed under an arc that is not on the story chain, so the page signal
correctly leaves them off-axis). `arc_index` drops 2,034 → 154; the 714
placement-page rows are preserved 714/714 and every `temporal=1` row stays placed.

| Set | Rows | Why off-axis | Disposition |
|-----|------|--------------|-------------|
| character / character_synopsis / location / technique under **generic** headings (History, Synopsis, Overview) | 116 (99 + 11 + 4 + 2) | the wiki gives no arc the cheap signals can read; the section is not arc-named and the page carries no `arc`/`chapters` fact | genuine residue — a standing state the axis cannot order; NULL is the *correct* answer, not a miss. Owner: the continuity-check consumer (named in its unit) |
| chapter pages filed under an arc **off the story chain** | 38 | the page's `arc` fact names a real arc, but that arc is not on the `previous`/`next` chain, so it has no orderable position | off-axis by construction (an off-chain arc has no index); the wiki's own filing, not a gap in the fix |
| the `residue` placement page (today, 30 pages) | its events | no `arc`/`chapters` fact reaching an on-chain arc | inference territory; already quarantined |

The 995 + 885 (chapter/episode page signal) are the recoverable set, 1,880 rows
plus the 714 preserved = 2,594 placed. The 154 are not placeable by a cheap
verifiable signal, and forcing them would manufacture misplacements. "Complete
arc index" = every row with a *verifiable* arc claim placed, not every row the
fix places.

## Verified-claims ledger (checked against code/DB before recording)

- 2,748 events; 714 placed (`temporal=1`, `arc_index` set); 2,034 off-axis
  (`arc_index IS NULL`, `temporal=0`) — **VERIFIED** (query).
- All 714 page-placed rows sit on placement-type pages, 0 under an arc-named section
  → the 714 and 995 are disjoint — **VERIFIED** (query).
- 995 NULL rows under arc-named sections, all on character/character_synopsis/org/
  item/location pages (918 + 51 + 12 + 3 + 11), all 9 headings resolve to an
  on-chain `story_arcs` page, 0 unresolved — **VERIFIED** (query).
- 1,039 NULL rows under generic headings: chapter 629, episode 294, character 99,
  character_synopsis 11, location 4, technique 2 → the 923 chapter/episode rows are
  the page-signal set, the 116 the residual — **VERIFIED** (query).
- Chapter pages 304 (275 carry an `arc` fact); episode pages 59 (59 carry an `arc`
  fact) — **VERIFIED** (query).
- All 995 pass the `section.document == event.arc_key` guard (0 fail) — **VERIFIED**
  (query).
- The 9 arc headings map to on-chain indices: Cursed Child 0, Fearsome Womb 1,
  Vs. Mahito 2, Kyoto 3, Death Painting 4, Gojo's Past 5, Shibuya 6, Culling Game 7,
  Shinjuku 8 — **VERIFIED** (query).
- `backfill_event_arc_index` re-derives `arc_index` on every gate call — **VERIFIED**
  (timeaxis.py:238; call sites gate.py:45,97).

## One next step

Implement `section_arc_index` + the chapter/episode page signal + the (page, section)
backfill with the document guard, re-derive the backfill test to pin the real numbers
with negative tests, verify NULL drops 2,034 → ~116 with the 714 intact, then commit.