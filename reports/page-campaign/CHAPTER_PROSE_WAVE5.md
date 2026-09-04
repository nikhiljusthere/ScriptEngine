# JJK Chapter Prose — Wave 5 (Chapters 217–271)

Status: **COMMITTED.** All 55 batches at 100% (**171/171**). Five sub-batches,
each authored, emitted (verbatim-checked against every served chunk), and
page-run against the live CUDA `:8000` API. Zero engine gaps — every failure
during authoring or page-run was a gold/wording error, caught by the verbatim
gate or the page-run and fixed inline, not triaged.

## Scope

- **Pages (55):** `Chapter 217 … Chapter 271`, the wiki's reading order, wave 5
  of the 6-wave plan in `chapter_prose_template.md` (the last numbered-chapter
  wave; `Chapter 271` is the final numbered chapter page).
- **Questions: 171** (prose-only, hand-authored). Per chapter: 1 `Summary` +
  2 `Plot Details`, +1 `Trivia` where the page has one.
- **Per-section density:** `Summary` 55 (1/chapter) · `Plot Details` 110 ·
  `Trivia` 6 (`Chapter 240`, `Chapter 241`, `Chapter 242`, `Chapter 243`,
  `Chapter 244`, `Chapter 262`).
- **Out of scope (by template):** `Characters in Order of Appearance` +
  `Battles & Events` (declared rosters — ride the roster path, not prose);
  `Locations` / `Jujutsu` (waived); `Author's Comment` (content gap);
  `4-Koma Bonus` (Modulo-only, wave 6).

## Sub-batches (all 100%)

| sub-batch | chapters | questions | result |
|---|---|---|---|
| w5_a | 217–227 | 33 | 33/33 |
| w5_b | 228–238 | 33 | 33/33 |
| w5_c | 239–249 | 38 | 38/38 |
| w5_d | 250–260 | 33 | 33/33 |
| w5_e | 261–271 | 34 | 34/34 |
| **total** | **217–271** | **171** | **171/171** |

`w5_c` carries 38 because `Chapter 240–244` all hold `Trivia` (4 Q each);
`w5_e` carries 34 because `Chapter 262` is the wave's only other `Trivia`
page (4 Q).

## Triage

No engine gaps in wave 5. `CHAPTER_PROSE_TRIAGE.md` carries no wave-5 entries.

Authoring-side fixes were made inline and re-verified:

- **Ch 220** (page-run 32/33): a Kogane question phrased generically invited a
  roster read and came back "answer absent". Reworded to “What rule does Kogane
  pass, per Chapter 220?” with gold `rule thirteen`; re-run 3/3.
- **Ch 244** (authoring pass): “What does Yuji's plan ensure…” was mislabelled
  `Plot Details`; the gold `Sukuna answers for his crimes and stands trial
  within Deadly Sentencing` sits in `Summary`. Section corrected; re-run 4/4.
- **Ch 249** (page-run 37/38): “Who takes responsibility by going all out, per
  Chapter 249?” (gold `Yuta`) misrouted to the roster path. Reworded to “What
  does Yuta take responsibility for by going all out, per Chapter 249?” with
  gold `the precarious situation`; re-run 3/3.
- **Ch 253** (page-run 32/33): “What remains to continue the fight when all
  other options seem lost…” (gold `one unexpected grade 1 sorcerer`) misrouted
  to the roster path. Replaced with “Who is the unexpected grade 1 sorcerer
  left to continue the fight, per Chapter 253?” with gold `Kusakabe`; re-run
  3/3.