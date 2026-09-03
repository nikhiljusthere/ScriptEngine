# Episode Prose Template — JJK (59 pages)

Prepared for the **episodes** wave of the prose pass (second after the 146
characters). Study of all 59 episode pages in `series/jjk/wikitext/`
(`Episode 1.json` … `Episode 59.json`; spot-read Ep 1/20/39/47/53/59 in
depth, full-corpus scan for the rest, 2026-08-27).

## Page anatomy (uniform across 59/59)

- `page_type = episode`, infobox `episode infobox` (Ep 59 capitalizes it — the
  discovery is structural, casing is not an issue).
- **Infobox facts (structured gold, not prose):** 15 keys — `season number`,
  `ep number`, `ep title`, `kanji`, `romaji`, `jp air date`, `us air date`,
  `adapted from`, `arc`, `opening song`, `previous`, `next` (58), `ending song`
  (58), `new character` (39). Air-date / numbering questions are answered from
  these, not from prose.

### Section layout and presence (of 59)

| section | presence | body size | role in the pass |
|---|---:|---|---|
| Summary | 59 | 103–650 ch, 1–3 sent | 1–2 factual entries |
| Plot Details | 59 (52 non-empty) | 3,573–17,876 ch, up to ~111 sent | **the prose mass** (402 KB total) |
| Characters in Order of Appearance | 59 | short list | declared roster — roster path, not prose |
| Locations | 59 | very short | 0–1 entry |
| Battles & Events | 56 | 1–3 sent | 1–2 entries |
| Jujutsu | 59 | 135–489 ch | technique list → roster-ish / "which technique did X use" |
| Music | 59 | 700–1,500 ch | skip (opening/ending credits) |
| Anime & Manga Differences | 49 | up to 1,272 ch / 11 sent | comparative entries |
| Clips / Videos | 34 / 1 | empty | skip |
| Trivia | 49 (24 non-empty) | 48–809 ch | bullet entries |
| Navigation | 59 | navbox | skip |
| `Juju Stroll` (lvl-3 scene head) | 20 | part of Plot Details | chunk with its scene |
| `Post-Credit Scene` (lvl-3) | 1 | part of Plot Details | chunk with its scene |
| References | 4 | | the only `{{Ref}}`-carrying sections |

## Sourcing: route two (title-locators)

- **16 `{{Ref}}` marks across all 59 pages** — the wiki writes episode prose
  without footnotes. This is the wiki's shape, not a pipeline bug (same class
  as Berserk's 0% chapter-sourcing; `audit` tells you which series is which).
- `citations.py:191` `locator_from_title` is the route-two path (the One Piece
  case: 1,172 episode pages, near-zero `<ref>`s): the page's own title
  `Episode N` **is** the locator. Every sentence of episode prose sources as
  `Episode N` — the `sourced:` header of any script line quoting episode prose
  renders the episode number, no `{{Ref}}` needed.
- Cross-link: infobox `adapted from` = the manga chapter; the graph edge
  `Chapter N -anime episode-> Episode M` (`EpisodeIndex`, `citations.py:104`)
  joins the two when a script wants chapter-level context.
- `cli audit` on episode pages: expect `sentences w/ chapter ≈ 0` and
  `sentences w/ episode` high. Do not "fix" that.

## What to author, per section

1. **Plot Details** — one fact-like entry per scene beat: who does what, which
   technique is used, who wins, what happens next. Answer must be a verbatim
   substring of the section. The long pages (Ep 39 ~111 sent; max 17,876 ch)
   need scene-scoped questions, not one "what happens" question.
2. **Summary** — 1–2 entries; avoid questions whose answer is the question
   (authoring lint: reject answers contained in the question).
3. **Anime & Manga Differences** — comparative entries ("How does Ep N differ
   from the manga?").
4. **Trivia** (24 pages) — bullet entries naming the bullet's subject.
   **Known open chunking gap:** a generic question does not serve a Trivia
   bullet (HANDOFF open gaps) — author questions that name the bullet's
   subject, and if a miss appears, diagnose the gap, don't rephrase.
5. **Battles & Events** — 1–2 entries (who fought whom, outcome).
   **Display-form gold rule (learned on Episode 1, applies to all 59):** the
   section renders the wikilink **display text**, not the battle page title
   (the link's target). E.g. the page shows `Battles & Events: Yuji & Megumi
   vs. Cursed Spirits`; the battle page title is `Yuji Itadori & Megumi
   Fushiguro vs. Cursed Spirits`, which is only in the link's `target` field and
   is NOT in the served bundle. Author the gold item from the display text the
   page actually shows. Using the full page title misses (Episode 1 first run
   went 28/29 for exactly this → 29/29 after the gold fix).
6. **Jujutsu** — "Which technique did X use in Episode N?"-class; the section
   lists techniques, so answers are short verbatim name strings.
7. **Characters in Order of Appearance** — declared roster; go through the
   roster path (enumeration), not prose Q&A.

## Special cases

- **Episodes 53–59 (Culling Game season): Plot Details is EMPTY** (the wiki
  has not written plot prose for the late season). Author only from Summary +
  Battles & Events + Jujutsu + Characters OOA; expect 3–6 entries instead of
  the 12–25 a plot-heavy episode yields. Do not fabricate plot prose to fill
  the gap.
- **Episode 1** has `Videos` + lvl-3 `Episode`/`Clips` heads; later episodes
  use `Clips`. Cosmetic; chunking handles both.
- **Never ask "in which episode does X happen?" on the episode page** — that
  gold belongs on the character/battle page and resolves through the graph;
  on the episode page it is circular.
- **Counterfactuals about episode events** ("What would have happened if X had
  not … in Episode N?") route to `qa` after the R5 G9b fix — but the answer
  must still be verbatim on the page. If the page states no hypothetical
  outcome, RETIRE the question with the standard "not stated on the page"
  reason; do not invent the counterfactual resolution.

## Batch shape and loop

- One batch per episode: `questions/_jjk_page_episode_<N>.json` (slug matches
  the page title), same schema as the character batches (`questions[]`,
  `retired[]`, `note`).
- Per-episode FAST loop (same as characters): dump → author verbatim triples
  → bulk-add → `page-run` → faithful triage (diagnose the gap; never rephrase
  the question to dodge it).
- R5 volume additions, per episode: (1) inline adversarial forms — at least
  one yes/no, one comparative, one counterfactual against the episode's own
  page facts; (2) authoring lint before `page-run` — reject answers contained
  in the question, reject leading wh-words, require numeric answers to
  "how many".
- Ordering: air-date order 1 → 59 (the wiki's own order; matches the
  `previous`/`next` infobox chain).

## Numbers to expect

| page class | count | entries/ep (typical) |
|---|---:|---|
| plot-heavy (S1–S2, Plot Details 3.5–18 KB) | ~45 | 12–25 |
| plot-light (short Plot Details) | ~7 | 6–12 |
| empty Plot Details (53–59) | 7 | 3–6 |

Rough total: ~500–700 prose entries for the wave, plus the structured
infobox-fact questions the facts layer already carries.