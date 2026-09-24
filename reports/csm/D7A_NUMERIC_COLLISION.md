# D7a defect sheet — the numeric-collision family (canonical row chap-01)

2026-09-24, opencode session, model-free (disk + read-only corpus). One of
the D7 holdout legs owed by `plan/CSM_100_CLOSE.md` step D7a ("per
holdout, from committed artifacts + chunk SQL, gold-error triage first …
defect statement with DB-verified locations + fix hypothesis + falsifiable
flip prediction"). The family = the box-class wrong-page ranking class of
`p23_red_triage.md` (37 of the 69 pre-extraction reds), canonical D7
holdout row `csm-dim-chap-01`.

## Gold-error triage (first, per D7a)

- `csm-dim-chap-01` ("What happens in Chapter 1?", subject: Chapter 1):
  all 3 expect terms are verbatim in **`Chapter 1 / Summary`**
  (`csm-red-triage.jsonl`: "kill a Tomato Devil as part of his devil
  hunting job for the Yakuza" / "turning into Chainsaw Man, ripping the
  zombies" / "become her pet, and as a pet she would feed him") — gold
  SUPPORTED. The family verdict is the same: the 2026-09-24 red-triage
  covered all 23 then-red rows, 23/23 gold-supported, zero bank/crawl
  defects. **No row in this sheet is retired as a gold error.**

## Defect statement (DB-verified locations)

The family's failure mode is **numeric-title collision + page-type
confusion at ranking**: the query's numeric or arc title binds to a wrong
page, and the right box page's Summary (where the gold lives, kept +
chunked) loses the ranking.

| canonical | served instead | gold location |
|---|---|---|
| "Chapter 1" | "Chapter 124" | `Chapter 1 / Summary` (3/3 terms) |
| "Episode 2" | infobox header only | `Episode 2 / Summary` |
| "Volume 13" | "Chapter 13 (Volume 2)" | `Volume 13 / …` chapter-enumeration section |
| "Bat Devil arc" | the Bat Devil character page | `Bat Devil arc / Synopsis` |
| "Eternity Devil arc" | a game page | `Eternity Devil arc / Synopsis` |

Family roster (the 37 pre-extraction reds, from
`census_widened_csm_results_hints.jsonl`; **id-pinned, amend #38-6,
council #38** — pulled 2026-09-24 by class filter
`{chapter_box, episode, volume_box, story_arcs_box}`; "What happens in
Chapter N?" / "Which chapters are in Volume N?" / "What happens in the X
arc?" shapes):

- **story_arcs_box (10):** `csm-dim-arcb-01` `csm-dim-arcb-02`
  `csm-dim-arcb-03` `csm-dim-arcb-04` `csm-dim-arcb-05` `csm-dim-arcb-06`
  `csm-dim-arcb-07` `csm-dim-arcb-08` `csm-dim-arcb-09` `csm-dim-arcb-10`
- **chapter_box (9):** `csm-dim-chap-01` `csm-dim-chap-02` `csm-dim-chap-03`
  `csm-dim-chap-04` `csm-dim-chap-05` `csm-dim-chap-07` `csm-dim-chap-08`
  `csm-dim-chap-09` `csm-dim-chap-10`
- **episode (9):** `csm-dim-ep-01` `csm-dim-ep-02` `csm-dim-ep-03`
  `csm-dim-ep-04` `csm-dim-ep-05` `csm-dim-ep-06` `csm-dim-ep-07`
  `csm-dim-ep-09` `csm-dim-ep-10`
- **volume_box (9):** `csm-dim-vol-01` `csm-dim-vol-02` `csm-dim-vol-04`
  `csm-dim-vol-05` `csm-dim-vol-06` `csm-dim-vol-07` `csm-dim-vol-08`
  `csm-dim-vol-09` `csm-dim-vol-10`

## Fix hypothesis + what closed it (on disk)

- **Q1-L1 story-pages floor** (`90206940`, D7 era; council-narrow Q1 WIN):
  the story-pages retry flipped **chap-01 + arcn-07** (the two D7-holdout
  rows of the family's canonical set) with the registered guards holding.
- **Subject routing** (the D6 close, `3c047604` A20: "417→463 gated from
  committed IDs"): closed **all 37 box-class reds** — the product state
  (flag-OFF, 469/486) carries **0 box-class reds** (disk-verified 2026-09-24
  against `d7_window/snapshots/census_head_469.jsonl`).
- **Residual (pre-registered):** under the campaign instrument with
  subject only, chap-01 is one of the 8 rows still red
  (`census_widened_csm_results_hints.jsonl`) and green under the full
  60000/50 campaign arm (`…_hints_campaign.jsonl` 8/8) ⇒ the family's
  product-path residual is WIDTH (top_k=8) on the numeric-collision shape,
  the same lever family as the width class — TIERED tier-2 + the class-
  scoped top_k=30 instrument (`WIDTHCLASS_PREDICT.md`) cover it. No
  separate engine mechanism is owed by the family itself.

## Falsifiable retest (pre-registered; graded in the GPU window)

- **Rows:** the 37 family rows (id-pinned in the roster above, 37 ids;
  re-verify with the class filter
  `{chapter_box, episode, volume_box, story_arcs_box}` against
  `census_widened_csm_results_hints.jsonl` at re-grade time) + the blind
  19 (`blind_fresh_d7.jsonl`).
- **Config:** product (flag-OFF committed tree, p23 endpoint defaults,
  campaign path with subject) — i.e. the post-extraction, post-re-grade
  state of the window, legs (e) of `P2_SCOPE_EXTRACTION.md`.
- **Bar:** 0 box-class reds (the family stays closed) AND blind 19/19.
- **Reopen trigger:** any box-class row red in ANY re-grade ⇒
  "numeric-collision family regression" ⇒ re-diagnosis via the D7a path
  (gold-error triage first), a new pre-registered instrument, and the
  council — **never an ex-post re-tune of a landed leg (D59)**.

## Status

Family CLOSED at the product state (0 reds); this sheet is the D7a
record + the regression trigger that keeps it honest. The canonical row
chap-01 stands: closed by Q1-L1, re-armed by the retest above.