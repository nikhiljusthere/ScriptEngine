# JJK Chapter Prose — Campaign Final Report

Status: **COMPLETE.** All 6 waves committed; 941/941 questions page-run
(100%). The one open gap (G30) was closed by `ee9fa2e` on 2026-09-04; standing
gates at pre-campaign baselines. This report closes the
chapters wave of the JJK prose pass (see `chapter_prose_template.md` for the
plan and `HANDOFF_PROSE_PASS.md` for the campaign's method).

## Per-wave results

| Wave | Pages | Batches | Prose Qs | Page-run | Commit |
|---|---|---|---|---|---|
| 1 | `Chapter 0-1`–`Chapter 0-4`, `Chapter 1`–`Chapter 51` | 55 | 166 | 100% | `4ca946f` |
| 2 | `Chapter 52`–`Chapter 106` | 55 | 169 | 100% | `78c182e` |
| 3 | `Chapter 107`–`Chapter 161` | 55 | 168 | 100% | `3176064` |
| 4 | `Chapter 162`–`Chapter 216` | 55 | 171 | 100% | `18d127c` |
| 5 | `Chapter 217`–`Chapter 271` | 55 | 171 | 100% | `eb7536f` |
| 6 | `Modulo Chapter 1`–`25` + `Bonus Manga`, `Five-Page Special Bonus Chapter`, `Special Bonus Chapter`, `Epilogue` | 29 | 96 | **96/96 (100%)** | `c533620` |
| **Total** | **304** | **304** | **941** | **941/941 (100%)** | — |

- 941 questions landed against the template's 600–900 band (planned ≈810):
  the overage is density on the special/bonus pages (`4-Koma Bonus`,
  `Trivia`, L3 scene-scoped `Plot Details`), not a deviation in method.
- Each wave was authored from a live `chprose.py dump` of that range's
  sections, golds verbatim-checked against every served chunk at emit, and
  page-run slug-by-slug on the `:8000` API (CUDA for waves 1–5 and 6's first
  run; CPU for the final canon gate).
- Per-wave detail: `CHAPTER_PROSE_WAVE1.md` … `CHAPTER_PROSE_WAVE6.md`.

## Triage

One triaged failure across the whole campaign (full entry in
`CHAPTER_PROSE_TRIAGE.md`), **now closed**:

- **w6 · Epilogue · Summary** — “Whom do the four short epilogue stories
  feature, per Epilogue?” routed narrative, whose bundle omits the page's own
  `Summary` beat (the narrative beat builder drops sections under the G15
  20-word floor; the Epilogue's `Summary` is 12 words), so the verbatim gold
  was unserved. A phrasing probe (5 forms) showed 3 of 4 natural phrasings
  fail → the fact is **not broadly reachable** → engine gap, not an authoring
  issue: the in-lane rephrase (Kinji-079 precedent) committed in `c533620`
  was reversed the same day, the question is restored to its original wording
  and left failing (2/3) as the regression case. Filed as **G30** in
  `CHECKPOINT_ROSTER_BUILD.md`, then **CLOSED by `ee9fa2e` (2026-09-04)**:
  the short-prose-section floor was lifted (title-scoped to `Summary`/
  `Synopsis`), the regression case now passes 3/3, and `sourcing-01` held at
  37/40.

## Standing gates (final, post G30)

| Gate | Result | Pre-campaign baseline |
|---|---|---|
| `pytest tests/ -q` | **1137 passed** | 1,133 |
| `eval --series jjk` | **24/24 (100%)** | 24/24 |
| `canon-run --series opm` | **10/16 exact · 236/236 canon · 79.0% precision** | 10/16 · 236/236 · 79.0% |
| `span-recall --series jjk` | **exit 2 — 2 unreachable lines, both the known `Chapter 239 / References` misses** | 48,570/48,572, exit 2 |

No gate regressed against baseline.

## State left behind

- 304 batch files in `questions/` (`_jjk_page_*.json`, `_`-prefixed so they
  stay out of the official gold bank); 941/941 questions page-run clean (the
  single open gap, G30, was closed by `ee9fa2e` on 2026-09-04).
- Reports: per-wave reports + this file + `CHAPTER_PROSE_TRIAGE.md` in
  `reports/page-campaign/`.
- The `:8000` API is stopped; at final-gate time ninfer-serve held the GPU,
  so the canon gate ran with the server on `SCRIPTENGINE_DEVICE=cpu`.
- Next up per `HANDOFF_PROSE_PASS.md`: the episodes (59) and battles (90)
  page batches, then techniques (149) and the remaining page types — same
  method, same gates.