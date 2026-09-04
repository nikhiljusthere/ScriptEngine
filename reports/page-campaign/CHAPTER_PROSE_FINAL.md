# JJK Chapter Prose — Campaign Final Report

Status: **COMPLETE.** All 6 waves committed; every batch page-run 100% against
the live API; standing gates at pre-campaign baselines. This report closes the
chapters wave of the JJK prose pass (see `chapter_prose_template.md` for the
plan and `HANDOFF_PROSE_PASS.md` for the campaign's method).

## Per-wave results

| Wave | Pages | Batches | Prose Qs | Page-run | Commit |
|---|---|---|---|---|---|
| 1 | `Chapter 0-1`–`Chapter 0-4`, `Chapter 1`–`Chapter 46` | 55 | 166 | 100% | `4ca946f` |
| 2 | `Chapter 52`–`Chapter 106` | 55 | 169 | 100% | `78c182e` |
| 3 | `Chapter 107`–`Chapter 161` | 55 | 168 | 100% | `3176064` |
| 4 | `Chapter 162`–`Chapter 216` | 55 | 171 | 100% | `18d127c` |
| 5 | `Chapter 217`–`Chapter 271` | 55 | 171 | 100% | `eb7536f` |
| 6 | `Modulo Chapter 1`–`25` + `Bonus Manga`, `Five-Page Special Bonus Chapter`, `Special Bonus Chapter`, `Epilogue` | 29 | 96 | 100% | `c533620` |
| **Total** | **304** | **304** | **941** | **100%** | — |

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
`CHAPTER_PROSE_TRIAGE.md`):

- **w6 · Epilogue · Summary** — “Whom do the four short epilogue stories
  feature, per Epilogue?” routed narrative, whose bundle omits the page's own
  `Summary` chunk, so the verbatim gold was unserved. Fixed in-lane per the
  Kinji-079 / Yuki-083 precedent: re-anchored to “Which four characters get
  short epilogue stories in the Epilogue, per Epilogue?” (qa route, gold
  unchanged, probed live), batch re-run 3/3. No engine fix was required for
  the wave to pass.
- Open engine observation carried forward to the engine pass (non-blocking):
  a chapter page's narrative bundle should include its `Summary` chunk as a
  beat, so Summary-only facts are served on the default narrative read.

## Standing gates (final, post wave 6)

| Gate | Result | Pre-campaign baseline |
|---|---|---|
| `pytest tests/ -q` | **1133 passed** | 1,133 |
| `eval --series jjk` | **24/24 (100%)** | 24/24 |
| `canon-run --series opm` | **10/16 exact · 236/236 canon · 79.0% precision** | 10/16 · 236/236 · 79.0% |
| `span-recall --series jjk` | **exit 2 — 2 unreachable lines, both the known `Chapter 239 / References` misses** | 48,570/48,572, exit 2 |

No gate regressed against baseline.

## State left behind

- 304 batch files in `questions/` (`_jjk_page_*.json`, `_`-prefixed so they
  stay out of the official gold bank), all 100%.
- Reports: per-wave reports + this file + `CHAPTER_PROSE_TRIAGE.md` in
  `reports/page-campaign/`.
- The `:8000` API is stopped; at final-gate time ninfer-serve held the GPU,
  so the canon gate ran with the server on `SCRIPTENGINE_DEVICE=cpu`.
- Next up per `HANDOFF_PROSE_PASS.md`: the episodes (59) and battles (90)
  page batches, then techniques (149) and the remaining page types — same
  method, same gates.