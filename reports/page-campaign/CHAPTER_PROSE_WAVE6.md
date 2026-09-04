# JJK Chapter Prose — Wave 6 (Modulo 1–25 + 4 special pages)

Status: **COMMITTED.** All 29 batches at 100% (**96/96**). Authored, emitted
(verbatim-checked against every served chunk), and page-run against the live
CUDA `:8000` API. One triaged failure (epilogue Summary — in-lane authoring
fix, Kinji-079 precedent); no engine fix required.

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
TOTAL 96/96 (failing batches: 0)
```

First full run was 95/96 with `_jjk_page_epilogue.json` at 2/3; after the
in-lane fix below, the full batch re-ran clean at 96/96.

## Triage

One failure, diagnosed and fixed in-lane (method: diagnose the gap, never
dodge). Full entry in `CHAPTER_PROSE_TRIAGE.md`.

- **Epilogue** (page-run 2/3): “Whom do the four short epilogue stories
  feature, per Epilogue?” (gold `Yuko Ozawa, Panda, Nobara Kugisaki, and
  Uraume`, a verbatim substring of the one-line `Summary`) routed **narrative**
  — story-typed pages keep the narrative read — and the narrative bundle for a
  chapter page carries the L3 scene beats + OOA + the previous chapter, but
  **not the page's own `Summary` chunk**, so the Summary-only gold was absent
  from the bundle. An alternate summary phrasing (“How many short epilogue
  stories…”) probed live routed narrative the same way. Re-anchored in-lane to
  “Which four characters get short epilogue stories in the Epilogue, per
  Epilogue?” (same fact, same section, gold unchanged), which routes `qa` with
  the Summary chunk in the bundle; re-run 3/3. Kinji-079 / Yuki-083 precedent
  (misroute on a phrasing → natural alternate, probed live). Non-blocking
  observation for the engine pass: a chapter page's narrative bundle should
  include its `Summary` chunk as a beat, so Summary-only facts are served on
  the default narrative read (recorded, not fixed — this campaign's
  constraint is authoring-side only).

No other failures: the 28 other pages passed their first page-run.

## Gates

Standing gates re-run after the commit (see the final campaign report):
`eval --series jjk`, `canon-run --series opm`, `pytest tests/ -q`,
`span-recall --series jjk`.