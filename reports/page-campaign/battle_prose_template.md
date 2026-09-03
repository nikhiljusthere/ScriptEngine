# Battle Prose Template — JJK (90 pages)

Prepared for the **battles** wave of the prose pass (third after the 146
characters and 59 episodes). Study of all 90 battle pages in
`series/jjk/wikitext/` (`page_type == battle`; `Jujutsu Sorcerers vs. Sukuna`
read in depth, full-corpus scan of section layout / infobox keys / body sizes
/ `{{Ref}}` counts, 2026-09-02).

## Page anatomy (uniform across 90/90)

- `page_type = battle`, infobox `battle infobox`.
- **Infobox facts (structured gold, NOT prose):** the fight's metadata is
  carried by the structured layer (`page_gen.py::_battle_builder`,
  `own_battle = True`), never re-asked as prose. Keys present across the 90:

  | key | presence | structured question it feeds |
  |---|---:|---|
  | `name` / `outcome` / `side1` / `side2` / `chapters` | 90 | identity, result, participants, manga chapters |
  | `prev` / `arc` / `powers1` / `powers2` | 89 | navigation, arc, **the flat technique lists** |
  | `next` | 88 | navigation |
  | `place` | 87 | location |
  | `episodes` | 74 | "in which episode is X depicted" |
  | `date` | 64 | when |
  | `event` | 36 | which event |
  | `conc` | 25 | concurrent battles |
  | `side3` / `powers3` / `prevevent` / `nextevent` | 1–2 each | rare three-sided fights |

  `side1`/`side2` are the **participant lists**; `powers1`/`powers2` are
  **flat technique lists** (fighter name interleaved with its techniques).
  Both are the G23 over-match class: ask them only through the roster/
  structured path, never as prose.

- **The prose lives in exactly three level-2 sections — `Prologue`,
  `Battle`, `Aftermath` (90/90).** `References` holds the chapter `{{Ref}}`
  marks (`{{Scroll box|<references/>}}`); `Navigation` is a navbox +
  categories. Neither is prose.

### Section layout and presence (of 90)

| section | presence | body size | role in the pass |
|---|---:|---|---|
| Prologue | 90 | 311–7,536 ch, med 1,221 | 1–3 setup / strategy entries |
| Battle | 90 | 397–35,279 ch, med 3,364 | **the prose mass** (scene-scoped beats) |
| Aftermath | 90 | 207–7,027 ch, med 739 | 1–3 consequence entries |
| Trivia | 2 | short bullets | bullet entries (only those 2 pages) |
| Adaptation Differences | 1 | short | comparative entries (only that 1 page) |
| References | 90 | `{{Scroll box|<references/>}}` | chapter `{{Ref}}` marks only — sourcing, no prose |
| Navigation | 90 | navbox + categories | skip |

87 pages are exactly the five core sections; 3 carry a sixth (`Trivia` ×2 on
`Satoru Gojo vs. Sukuna: First Fight` and `Sukuna vs. Mahoraga`;
`Adaptation Differences` ×1 on `Maki Zenin, Toge Inumaki & Panda vs. Suguru
Geto`).

## Sourcing: route one (chapter `{{Ref}}`)

- Unlike episodes (route two, title-locators), battle pages cite the manga
  **inline**: `{{Ref|chap=N|page=P}}` sits inside Prologue / Battle /
  Aftermath, and `{{Scroll box|<references/>}}` collects the footnotes in the
  References section.
- Every battle page carries at least one `{{Ref}}` (min 3, median 5, max 65;
  **zero** pages with none), so every prose beat sources to a chapter through
  `citations.py`. `cli audit` on battle pages: expect **high** chapter
  coverage — the JJK norm, not the Berserk-0% / episode-route-two case. Do
  not "fix" it.
- Cross-link: infobox `chapters` (manga) and `episodes` (anime) join to the
  prose through the graph (`EpisodeIndex`, `citations.py`); a script line
  quoting battle prose renders its chapter, not the episode.

## What to author, per section

1. **Battle** — the prose mass. One fact-like entry per narrative beat: who
   uses which technique, who is injured or killed, the turning point, the
   sequence. The long pages (`Jujutsu Sorcerers vs. Sukuna`, 35,279 ch) need
   **scene-scoped** questions, not one "what happens" question. Answer must
   be a verbatim substring of the section.
2. **Prologue** — 1–3 entries: the setup, the plan/strategy, who agreed to
   what, what was learned beforehand.
3. **Aftermath** — 1–3 entries: who survived / died and how, the fallout,
   who is blamed, who returns.
4. **Trivia** (2 pages) / **Adaptation Differences** (1 page) — bullet /
   comparative entries that name the bullet's subject.
5. **Never re-ask the structured half** (the R6 181-finding guard, and the
   G23 over-match guard): do NOT author a prose question whose answer is an
   infobox field — `outcome`, `place`, `event`, `date`, `arc`, `chapters`,
   `episodes`, `prev`/`conc`/`next`, the participant list (`side1`/`side2`),
   or a flat technique list (`powers1`/`powers2`). Those route to the
   structured / roster path and **fail the prose containment scorer**.
   Technique usage may appear *inside* a verbatim beat answer ("Sukuna
   injured Choso first by punching through him"), but never as a
   "which techniques did X use?" enumeration — that is exactly the G23
   class (the per-fighter technique question belongs on the fighter's own
   page, where `page_gen` already emits it).

## Special cases

- **Thin fights:** the shortest Battle section is 397 ch (a couple of minor
  Culling-Game skirmishes). Expect 2–4 entries instead of the 15–30 a big
  battle yields. Do not fabricate beats to fill the gap.
- **Sixth section on 3 pages** (Trivia ×2, Adaptation Differences ×1) —
  author from it only on those pages.
- **Counterfactuals about a battle** ("What if Sukuna had won?") route to
  `qa`; the answer must still be verbatim on the page. If the page states no
  hypothetical outcome, RETIRE the question with the standard "not stated on
  the page" reason; do not invent the resolution.
- **"In which chapter / episode is X depicted?"** is the infobox
  `chapters` / `episodes` field (structured) — do not author it as prose.

## Batch shape and loop

- One batch per battle: `questions/_jjk_page_<battle-slug>.json` (slug = page
  title with spaces → underscores), same schema as the character / episode
  batches (`questions[]`, `retired[]`, `note`).
- Per-battle FAST loop (same as characters / episodes): dump the page →
  author verbatim triples → bulk-add → `page-run --series jjk --batch
  <slug>` → faithful triage (diagnose the gap; **never rephrase the question
  to dodge it**).
- R5 volume additions, per battle: (1) inline adversarial forms — at least
  one yes/no, one comparative, one counterfactual against the battle's own
  page facts; (2) authoring lint before `page-run` — reject answers contained
  in the question, reject leading wh-words, require numeric answers to
  "how many".
- **Ordering:** story order — sort by the infobox `chapters` value (the manga
  chapter the battle begins in), ties broken by the `prev`/`next` chain. The
  90-page order file (`reports/page-campaign/jjk_battles_order.json`) is
  derived from the infobox links in the next step.

## Numbers to expect

| page class | count | entries/battle (typical) |
|---|---:|---|
| Battle-heavy (Battle section up to ~35 KB) | ~10 | 15–30 |
| Battle-mid (median ~3.4 KB) | ~55 | 6–12 |
| Battle-light (down to ~400 ch) | ~25 | 2–5 |

Rough total: ~600–900 prose entries for the wave, plus the structured
infobox-fact questions the facts layer already carries.