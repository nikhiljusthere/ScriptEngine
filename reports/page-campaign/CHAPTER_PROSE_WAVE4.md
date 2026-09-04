# JJK Chapter Prose — Wave 4 (Chapters 162–216)

Status: **COMMITTED.** All 55 batches at 100% (**171/171**). Five sub-batches,
each authored, emitted (verbatim-checked against every served chunk), and
page-run against the live CUDA `:8000` API. Zero engine gaps — every failure
during authoring or page-run was a gold/wording error, caught by the verbatim
gate or the page-run and fixed inline, not triaged.

## Scope

- **Pages (55):** `Chapter 162 … Chapter 216`, the wiki's reading order, wave 4
  of the 6-wave plan in `chapter_prose_template.md`.
- **Questions: 171** (prose-only, hand-authored). Per chapter: 1 `Summary` +
  2 `Plot Details`, +1 `Trivia` where the page has one, plus a second `Summary`
  question on `Chapter 181` (two separate summary scenes).
- **Per-section density:** `Summary` 56 (1/chapter +1 for `Chapter 181`) ·
  `Plot Details` 110 · `Trivia` 5 (`Chapter 169`, `Chapter 184`,
  `Chapter 201`, `Chapter 211`, `Chapter 212`).
- **Out of scope (by template):** `Characters in Order of Appearance` +
  `Battles & Events` (declared rosters — ride the roster path, not prose);
  `Locations` / `Jujutsu` (waived); `Author's Comment` (content gap);
  `4-Koma Bonus` (Modulo-only, wave 6).

## Sub-batches (all 100%)

| sub-batch | chapters | questions | result |
|---|---|---|---|
| w4_a | 162–172 | 34 | 34/34 |
| w4_b | 173–183 | 34 | 34/34 |
| w4_c | 184–194 | 34 | 34/34 |
| w4_d | 195–205 | 34 | 34/34 |
| w4_e | 206–216 | 35 | 35/35 |
| **total** | **162–216** | **171** | **171/171** |

## Triage

No engine gaps in wave 4. `CHAPTER_PROSE_TRIAGE.md` carries no wave-4 entries.

Authoring-side fixes were made inline and re-verified:

- **Ch 174** (page-run 33/34): the original Summary question missed because its
  phrasing invited a roster read. Reworded to “Who has excelled thus far in the
  Culling Game, per Chapter 174?” with gold `Yuta Okkotsu`; re-run 3/3.
- **Ch 181** (authoring pass): the chapter has two summary scenes. The Hakari /
  aspiring-mangaka beat was corrected to `Summary`, and the Charles Bernard /
  visitor-registration beat was added as a second `Plot Details` question,
  bringing the chapter to 4 Q.
- **Ch 188** (emit gate): the crate question’s gold was corrected to the exact
  `the large crate` before page-run.
- **Ch 192** (emit gate): the Summary gold was corrected to the exact
  `Naoya Zenin wasn't slain using jujutsu` before page-run; the Plot question
  was also tightened to “What begins as Naoya's body implodes, per Chapter
  192?”
- **Ch 195** (page-run 33/34): the Summary question carried a long multi-entity
  answer. Reworded to “What does the sumo enthusiast lack, per Chapter 195?”
  with gold `no one to wrestle`; re-run 3/3.
- **Ch 198** (emit gate): the Maki question’s gold was corrected to the exact
  capitalization `She has no cursed energy` before page-run.
- **Ch 209** (page-run 34/35): “What do each and every soldier ignore…” missed
  with the gold `Kogane`. Reworded to “What do the invading soldiers ignore,
  per Chapter 209?” with the exact gold `the shikigami`; re-run 3/3.
- **Ch 211** (page-run 34/35): “What do all the group's collective points get
  transferred to…” missed with the gold `Megumi`. Replaced with “At what time
  do Maki and Kiyotaka Ijichi bring Tsumiki to the colony, per Chapter 211?”
  with gold `3 P.M.`; re-run 4/4.