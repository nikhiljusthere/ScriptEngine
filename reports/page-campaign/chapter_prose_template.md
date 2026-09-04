# Chapter Prose Template — JJK (304 pages)

Prepared for the **chapters** wave of the prose pass — the narrative remainder
after the chapter-tranche roster build (commit 7). Study of all 304 chapter
pages in `series/jjk/wikitext/` + `series/jjk/facts.db` (275 numbered
`Chapter N` / `Chapter 0-N` + 29 non-numbered: `Modulo Chapter 1–25`,
`Bonus Manga`, `Epilogue`, `Five-Page Special Bonus Chapter`, `Special Bonus
Chapter`; full-corpus scan, 2026-09-04). Format mirrors
`episode_prose_template.md`.

## Page anatomy (uniform across 304/304)

- `page_type = chapter`, infobox `chapter infobox` (casing variants exist — the
  discovery is structural, casing is not an issue).
- Lead: one line — "«X» is the Nth chapter of Gege Akutami's Jujutsu Kaisen."
  (structured, not a prose target.)
- **Infobox facts (structured gold, not prose):** 14 keys (count of 304) —
  `japanese` (304), `romaji` (304), `pages` (304), `date` (304), `issue` (303),
  `previous` (302), `next` (302), `volume` (292), `cover` (290), `chapter
  title` (278), `arc` (275), `anime episode` (185), `new character` (72),
  `name` (3). Air-date / volume / issue / page-count / "which episode adapted
  it" questions are answered from these, not from prose.

### Section layout and presence (of 304; body size = served text, `facts.db`)

| section | pages | non-empty | body size (max ch / max w / max sent) | role in the pass |
|---|---:|---:|---|---|
| **Summary** | 304 | 304 | 865 / 139 / 9 | **in scope** — 1–2 entries |
| **Plot Details** | 304 | 304 | 15,316 / 2,530 / 129 | **in scope — the prose mass** |
| L3 scene heads under Plot Details | 2 | 8 heads | 1,428 / 248 / 15 | chunk with its scene |
| `Author's Comment` | 247 | 0 served | `{{Comment}}` ×237 + `{{Comment 2}}` ×13, dropped by parser | **out of scope + content gap (TODO 8)** |
| `Trivia` | 22 | 22 | 2,416 / 393 / 16 | **in scope** — bullet entries |
| `4-Koma Bonus` | 6 | 6 | 1,006 / 172 / 10 | **in scope** — Modulo-only |
| `Character(s) in Order of Appearance(s)` (4 variants) | 304 | 304 | declared roster (commit 7) | roster path, not prose |
| `Battles & Events` / `Battles and Events` (2 forms) | 254 | 254 | declared roster (commit 7) | roster path, not prose |
| `Locations` / `Location` | 294 | 294 | waived (State 122) | out of scope |
| `Jujutsu` | 277 | 277 | waived (State 122) | out of scope |
| `Color Spread` | 3 | 0 | empty (image spread) | skip |
| `Video` | 5 | 0 | media | skip |
| `References` | 2 | 1 (`Ch 244`) | 430 / 69 / 2 | the only `{{Ref}}`-carrying section |
| `Navigation` | 304 | 17 | navbox | skip |

## Sourcing: route two (title-locators)

- **Only 1/304 chapter page carries `{{Ref}}` (Chapter 244, one mark:
  `{{Ref|chap=134|page=7-9}}`); the
  other 303 have zero.** The wiki writes chapter prose without footnotes — the
  same shape as the episode pages (route two). `citations.py:191
  locator_from_title` is the route-two path: the page's own title (`Chapter N`,
  `Modulo Chapter N`, `Bonus Manga`, …) **is** the locator. Every sentence of
  chapter prose sources as the chapter title — the `sourced:` header of any
  script line quoting chapter prose renders the chapter title, no `{{Ref}}`
  needed.
- Cross-link: infobox `anime episode` (185 chapters) + the graph edge `Chapter
  N -anime episode-> Episode M` (`citations.py:103 EpisodeIndex`) join chapter
  and episode context; `citations.py:154` completes a bare chapter locator with
  its episode when the anime has reached it.
- `cli audit` on chapter pages: expect `sentences w/ chapter ≈ 0` (no
  footnotes in the prose) with sourcing via the title-locator. Do not "fix"
  that.
- The two known `Chapter 239 / References` span-recall exit-2 misses remain
  expected; `Chapter 244` is the lone `{{Ref}}` page.

## What to author, per section

1. **Plot Details** (304, all non-empty) — the prose mass (184–2,530 w, up to
   129 sent). One fact-like entry per scene beat: who does what, which technique
   is used, who wins, what happens next. Answer must be a verbatim substring of
   the section. Long pages (700+ w; up to 2,530 w / 129 sent) need scene-scoped
   questions, not one "what happens" question; when an L3 scene head is present
   (8 heads on 2 pages: `Yuko Ozawa`, `Panda`, `Nobara Kugisaki`, `Uraume`,
   `The Miracle Generation`, `Pan`, `Mei`, `Taste Test`) scope the question to
   that scene.
2. **Summary** (304) — 1–2 entries; the 1–9 sentence overview. Avoid questions
   whose answer is contained in the question (authoring lint).
3. **L3 scene heads** (8, on 2 pages) — chunk with their scene; the head scopes
   the question ("In the <scene> of Chapter N, …").
4. **Trivia** (22) — bullet entries naming the bullet's subject. **Known open
   chunking gap:** a generic question does not serve a Trivia bullet (HANDOFF
   open gaps) — author questions that name the bullet's subject; on a miss,
   diagnose the gap, don't rephrase to dodge it.
5. **4-Koma Bonus** (6, Modulo only) — the bonus 4-koma gag; 1 entry naming the
   gag.
6. **Out of scope (do not author):** `Characters in Order of Appearance` +
   `Battles & Events` (declared rosters, commit 7 — served by the roster path;
   do not re-ask them); `Locations` + `Jujutsu` (waived, State 122 —
   line-level only); `Author's Comment` (content gap, TODO 8 — the `{{Comment}}`
   bodies are not served prose); `Color Spread` / `Video` / `Navigation` (empty
   or furniture).
7. **Display-form gold rule (from the episode template, applies to inline
   battle names in Plot Details):** the section renders the wikilink **display
   text**, not the battle page title. Author the gold item from the display text
   the page actually shows; the full battle-page title is only in the link's
   `target` field and is not in the served bundle.

## Special cases / structural variants

- **OOA — 4 heading variants** (declared rosters, commit 7): `Character in
  Order of Appearances` (153), `Characters in Order of Appearance` (149),
  `Character in Order of Appearance` (1), `Characters in Appearance` (1 — Ch
  74). Roster path — no prose.
- **Battles & Events — 2 forms** (declared rosters, commit 7): `Battles &
  Events` (238 in-tranche) + `Battles and Events` (16) = 254 (corpus-wide 390 +
  18 = 408). Roster path — no prose.
- **`Summary` / `Plot Details` are uniform** — no heading variants (304/304
  each). The variance in this page type is in the closed-set sections, not the
  narrative ones.
- **`Epilogue`** — its Plot Details body lives entirely under 4 L3 scene-heads
  (`Yuko Ozawa`, `Panda`, `Nobara Kugisaki`, `Uraume`; ~4,585 served ch / 785
  w), so it is a normal plot-heavy chapter, not an empty one. The census must
  roll an L3 head's text into its parent section's body (the L2 `Plot Details`
  row alone stores 0 ch). Author from the 4 scenes.
- **29 non-numbered pages** — `Modulo Chapter 1–25` (the Jujutsu Kaisen Modulo
  spin-off; 6 carry `4-Koma Bonus`), `Bonus Manga`, `Five-Page Special Bonus
  Chapter`, `Special Bonus Chapter`, `Epilogue`. Slot them after the numbered
  chapters; the Modulo pages also carry `{{Comment 2}}` author notes (out of
  scope).
- **Never ask "in which chapter does X happen?" on the chapter page** — that
  gold belongs on the character/battle page and resolves through the graph; on
  the chapter page it is circular.
- **Counterfactuals** about chapter events ("What would have happened if … in
  Chapter N?") route to `qa`; the answer must still be verbatim on the page. If
  the page states no hypothetical outcome, RETIRE with "not stated on the
  page"; do not invent the resolution.
- **`Author's Comment` content gap (record, don't author — TODO 8):** 247 pages
  hold Gege Akutami's `{{Comment}}` (×237) / `{{Comment 2}}` (×13) notes (250
  templates) that the parser drops (all 247 sections store `text=''`; the
  parser has no prose rule for `comment` templates). Same class as the
  `{{Scroll box|content=}}` gap — ~250 author-commentary bodies are not in the
  corpus. Out of scope for the prose wave; filed as **TODO 8** in
  `CHECKPOINT_ROSTER_BUILD.md` (parser pass; low signal: author meta-commentary,
  not plot).

## Batch shape and loop

- One batch per chapter: `questions/_jjk_page_chapter_<N>.json` (slug matches
  the page title; non-numbered pages slug to their full title, e.g.
  `_jjk_page_modulo_chapter_3.json`), same schema as the character/episode
  batches (`questions[]`, `retired[]`, `note`).
- Per-chapter FAST loop (same as characters/episodes): dump → author verbatim
  triples → bulk-add → `page-run` → faithful triage (diagnose the gap; never
  rephrase the question to dodge it).
- R5 volume additions per chapter: (1) inline adversarial forms — at least one
  yes/no, one comparative, one counterfactual against the chapter's own facts;
  (2) authoring lint before `page-run` — reject answers contained in the
  question, reject leading wh-words, require numeric answers to "how many".
- Ordering: the wiki's own reading order — `Chapter 0-1…0-4`, then `Chapter
  1…` (numbered, ascending), then the 29 non-numbered pages (Modulo 1–25, then
  the specials by title).

## Wave plan (304 pages → 6 waves, budget 600–900)

In-scope sections: **Summary (304) + Plot Details (304) + Trivia (22) +
4-Koma Bonus (6) = 636 sections**. At ~1.0–1.4 entries/section that is
**~636–890 questions** (the 600–900 band; short Summary sections yield 1,
plot-heavy Plot Details yield 1–2 scene-scoped, Trivia/4-Koma ~1 each ≈ 42).

| wave | pages | content | per-wave target |
|---|---:|---|---:|
| 1 | 55 | `Chapter 0-1…0-4` + `Chapter 1…~46` | ~145 |
| 2 | 55 | next 55 numbered | ~145 |
| 3 | 55 | next 55 numbered | ~145 |
| 4 | 55 | next 55 numbered | ~145 |
| 5 | 55 | last 55 numbered (…to `Chapter 271`) | ~145 |
| 6 | 29 | `Modulo 1–25` (+ its 6 `4-Koma`) + `Bonus Manga` / `Five-Page Special` / `Special Bonus` / `Epilogue` | ~85 |

Total ≈ **~810** (upper-mid band). Each wave ends with a `page-run` over its batch
files + the standing gates (`eval --series jjk`, `canon-run --series opm`,
`pytest tests/ -q`, `span-recall --series jjk`) before the next wave starts.

## Numbers to expect

| page class | count | in-scope sections | entries/page (typical) |
|---|---:|---:|---:|
| plot-heavy (Plot Details ≥700 w, up to 129 sent) | 61 | 2 (+Trivia/4-Koma where present) | 2–4 |
| moderate (300–699 w — the 75% bulk; med 528 w) | 231 | 2 | 2–3 |
| plot-light (100–299 w) | 12 | 2 | 1–2 |
| `Trivia` (22 pages) / `4-Koma Bonus` (6 Modulo pages) | — | +1 each | ~1 |

Rough total: **~600–900 prose entries** for the wave (Summary + Plot Details +
Trivia + 4-Koma Bonus), plus the structured infobox-fact questions the facts
layer already carries, and the 558 OOA/B&E roster entries (commit 7) which ride
the separate roster path. `Trivia` (22) + `4-Koma Bonus` (6) are **in scope**
(~42 questions at ~1.5/section; fits the 600–900 band without a separate wave).