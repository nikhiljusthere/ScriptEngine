# JJK Chapter Prose — Wave 6 (Modulo 1–25 + 4 special pages)

Status: **COMMITTED.** Authored, emitted (verbatim-checked against every
served chunk), and page-run against the live CUDA `:8000` API. 28/29 batches
passed 100%; the `Epilogue` batch stands at 2/3 — its `Summary` gold was
filed as **G30** (engine gap: the narrative bundle omits the page's own
`Summary` beat; fix proposed, not applied) and left failing. Wave total:
**95/96**.

## Scope

- **Pages (29):** `Modulo Chapter 1 … Modulo Chapter 25` (the Jujutsu Kaisen
  Modulo spin-off, in the wiki's own reading order after `Chapter 271`), then
  the remaining non-numbered chapter pages: `Bonus Manga`, `Five-Page
  Special Bonus Chapter`, `Special Bonus Chapter`, `Epilogue`. This is wave 6
  of the 6-wave plan in `chapter_prose_template.md` and closes the 304-page
  chapters wave.
- **Questions: 96** (prose-only, hand-authored).
  - Modulo 1–25: 1 `Summary` + 2 `Plot Details` per page, +1 `4-Koma Bonus`
    on the 6 pages that carry one (`Modulo 9, 14, 17, 20, 23, 24`) →
    19 × 3 + 6 × 4 = **81**.
  - `Bonus Manga` (Summary + Plot Details + Plot Details + Trivia) = 4.
  - `Five-Page Special Bonus Chapter` (Summary + `Plot Details` + L3 scene
    `Plot Details / Taste Test` + Trivia) = 4.
  - `Special Bonus Chapter` (Summary + 2 × Plot Details + Trivia) = 4.
  - `Epilogue` (Summary + L3 scenes `Plot Details / Yuko Ozawa` +
    `Plot Details / Panda`) = 3.
- **Per-section density:** `Summary` 29 (1/page) · `Plot Details` (incl. L3
  scene-scoped) 58 · `Trivia` 3 · `4-Koma Bonus` 6 → **96**.
- **Out of scope (by template):** `Character(s) in Order of Appearance(s)` +
  `Battles & Events` (declared rosters, commit 7 — roster path, not prose);
  `Locations` / `Jujutsu` (waived); `Author's Comment` (content gap, TODO 8);
  `Color Spread` / `Video` / `Navigation` (furniture).
- **L3 scene heads:** the template's 8 scene heads live on 2 pages —
  `Five-Page Special Bonus Chapter` (4 heads: `The Miracle Generation`, `Pan`,
  `Mei`, `Taste Test`) and `Epilogue` (4 heads: `Yuko Ozawa`, `Panda`,
  `Nobara Kugisaki`, `Uraume`). The pass scoped one question to a scene per
  L3 page (Taste Test; Yuko + Panda); the other scenes' facts stay
  reachable through the same pages' other questions and the roster path.

## Results

Full-batch page-run (29 slugs, one `page-run` per page):

```
TOTAL 95/96 (failing batches: 1 — `_jjk_page_epilogue` 2/3, G30 open)
```

First full run was 95/96 with `_jjk_page_epilogue.json` at 2/3. An in-lane
fix was probed and committed in `c533620` (re-run 96/96); the same-day
phrasing probe (5 forms, see `CHAPTER_PROSE_TRIAGE.md`) showed the fact is
**not broadly reachable** — 3 of 4 natural phrasings fail — so the fix was
reversed and the question restored to its original wording, left failing as
the G30 regression case. The wave therefore stands at **95/96**.

## Triage

One failure, diagnosed and **filed as G30** (method: diagnose the gap, never
dodge). Full entry in `CHAPTER_PROSE_TRIAGE.md`; the fix proposal and gate
live in `CHECKPOINT_ROSTER_BUILD.md`.

- **Epilogue** (page-run 2/3): “Whom do the four short epilogue stories
  feature, per Epilogue?” (gold `Yuko Ozawa, Panda, Nobara Kugisaki, and
  Uraume`, a verbatim substring of the one-line `Summary`) routed **narrative**
  — story-typed pages keep the narrative read — and the narrative path's
  own-page beat builder drops sections under the G15 20-word floor (the
  `Summary` is 12 words), so the page's `Summary` never becomes a beat and no
  narrative bundle for the page carries the gold. **Phrasing probe (5
  forms):** the original and “How many short epilogue stories are there…” and
  “What are the four short epilogue stories about…” all route narrative and
  fail; “Who appears in…” and “Which four characters get short epilogue
  stories in the Epilogue…” reach qa and pass. 3 of 4 natural phrasings fail
  → the fact is **not broadly reachable** → engine gap, not authoring-side.
  A wave-6 in-lane re-anchoring (Kinji-079 precedent) was committed in
  `c533620` and reversed the same day; the question is restored to its
  original wording and **left failing (2/3)** as the G30 regression case.
  Fix proposed (exempt a page's own short `Summary` / `Plot` sections from
  the floor in `_beats_from_page`), not applied — execution tier.

No other failures: the 28 other pages passed their first page-run.

## Gates

Standing gates re-run after the commit (see the final campaign report):
`eval --series jjk`, `canon-run --series opm`, `pytest tests/ -q`,
`span-recall --series jjk`.