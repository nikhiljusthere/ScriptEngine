# JJK Chapter Prose — Wave 3 (Chapters 107–161)

Status: **COMMITTED.** All 55 batches at 100% (**168/168**). Five sub-batches,
each authored, emitted (verbatim-checked against every served chunk), and
page-run against the live CUDA `:8000` API. Zero engine gaps — every failure
during authoring or page-run was a gold/authoring error, caught by the verbatim
gate or the page-run and fixed inline, not triaged.

## Scope

- **Pages (55):** `Chapter 107 … Chapter 161`, the wiki's reading order, wave 3
  of the 6-wave plan in `chapter_prose_template.md`.
- **Questions: 168** (prose-only, hand-authored). Per chapter: 1 `Summary` +
  2 `Plot Details`, +1 `Trivia` where the page has one.
- **Per-section density:** `Summary` 55 (1/chapter) · `Plot Details` 110 ·
  `Trivia` 3 (`Chapter 117`, `Chapter 133`, `Chapter 141`).
- **Out of scope (by template):** `Characters in Order of Appearance` +
  `Battles & Events` (declared rosters — ride the roster path, not prose);
  `Locations` / `Jujutsu` (waived); `Author's Comment` (content gap);
  `4-Koma Bonus` (Modulo-only, wave 6).

## Sub-batches (all 100%)

| sub-batch | chapters | questions | result |
|---|---|---|---|
| w3_a | 107–117 | 34 | 34/34 |
| w3_b | 118–128 | 33 | 33/33 |
| w3_c | 129–139 | 34 | 34/34 |
| w3_d | 140–150 | 34 | 34/34 |
| w3_e | 151–161 | 33 | 33/33 |
| **total** | **107–161** | **168** | **168/168** |

## Triage

No engine gaps in wave 3. `CHAPTER_PROSE_TRIAGE.md` carries no wave-3 entries.

Four authoring-side fixes were made inline and re-verified:

- **Ch 114** (page-run 33/34): the first question did not retrieve its gold.
  Reworded to “Which two curse users interrupt the Kusakabe Team, per Chapter
  114?” with the same gold `Manami Suda and Toshihisa Negi`; re-run 3/3.
- **Ch 146** (page-run 33/34): the Kogane question did not retrieve its long
  gold. Reworded to “What is the name of the shikigami each player receives,
  per Chapter 146?” with gold `a Kogane`; re-run 3/3.
- **Ch 159** and **Ch 160** (emit gate): non-verbatim gold phrasings were
  corrected before page-run; neither failure reached a live batch.