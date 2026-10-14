# RESUME HANDOFF b — lint pass + gold v2 + 27B (written 2026-10-14 ~04:30 by the app session)

For the NEW terminal session. Read first: `plan/RESUME_REVIEW_HANDOFF_2026-10-10.md` §1 (binding owner rules),
`plan/RESUME_HANDOFF_2026-10-14.md` (state after the overlap reconciliation, tool quirks, conventions),
`plan/BIG_REVIEW_PATTERNS.md` (whole catalog, end notes), `plan/BIG_REVIEW_HANDOFF.md` §4 (compose + train).
Rules in short: never push; explicit pathspecs; never stage `tools/train/label_single.py`'s owner hunk or
`plan/FACT_LAYER_PROGRESS.md`; only Claude edits the catalog and `big_flags.py`; GPU-only; kill by exact PID;
SWITCHPOINT entry (main checkout `plan/SWITCHPOINT.md`) before any model switch; no Claude subagents.

## 1. Owner decisions this session (verbatim where quoted)

- "If there are any more inconsistencies in the dataset, fix all of them and make the dataset flawless, then only
  move to train the 9B model."
- Gold-set decision (§3.3 of the 14 handoff): **full plan** — bring the gold set to v2: facts+tags added to the
  3,822 unique gold windows (student_clean train 3,315 + dev 215 + dev_pool 151 (⊂ dev) + test 292), AND re-check
  the gold events against the current catalog. Caveat accepted: test events may change, so re-score the old
  teacher on the revised test too, to keep the .602 ship bar meaningful.
- "Use 27B instead with all the big flag files or any directions you need, 27B is smarter it will make fewer
  mistakes. You will have to review their answers anyways." → the reading work below is pre-done by the
  **27B Qwen** (ninfer, :18080, `bash /home/goblin/ninfer-work/qwen-switch.sh <ctx>`), given the catalog,
  `big_flags.py` output and the procedure; Claude reviews every 27B answer before anything is submitted.
- "move the work to the terminal session" → this session (terminal) now owns ALL remaining work.

## 2. Done in the app session

- `plan/review_tools/lint_v2.py` (`lint.sh [--regate] [--show CHECK]`): corpus lint of the final rows.
  Before fixes: all 14,000 windows have an audit record; `--regate` with today's gates: **0 refused** events/facts/
  tags (75 windows' facts would be re-normalised; harmless).
- `plan/review_tools/lint_fix.py` (`lint_fix.sh [--dry]`): rule-decided fixes, gated like `rv fix`, appended as
  `why: "lint M…"` records. **Applied: 908 records** (M1 ordered→actual 418 windows, M5 child_of→parent_of and
  married_to→married 294, M2 A89 event twins 157, M3 asserted_by==subject on actual rows 34, M4 duplicates 33),
  0 refused. Backup: `big/big_audit_v2.jsonl.bak-pre-lint-2026-10-14`.
- `plan/review_tools/lint_work.py` (`lint_work.sh build | show B`): NOT yet run. Builds the reading lists of
  windows that need judgment, groups overlap partners together, writes `big/lint/work_{app,term}.txt`. Since
  you own everything now, just use both files (or change the split code to one file).
- Gold v2 labelling (35B, `--add-only`, gold events fixed): `tools/train/ops/label_gold_v2.sh` → 
  `big/gold_v2/gold_labels_v2.jsonl` (3,423/3,822 at 04:30, ~13 w/min, PIDs: server 672061, labeller 672495).
  Inputs `big/gold_v2/gold_in.jsonl` (with `splits`), `gold_events.jsonl`. Let it finish, then switch to the 27B
  (SWITCHPOINT entry; stop 672061 by exact PID; qwen-switch.sh).

## 3. Lint classes that need reading (counts before the M-fixes; re-run `lint.sh` first)

| class | windows | what to decide |
|---|---|---|
| E_met_and_fight_same_pair | 467 | A145: a confrontation that becomes the fight gets no met; keep met only for a separate meeting. Seen: same-quote met+fought (b5239, b6543, b3814), "appeared and attacked" (b3741), wrong-person met (b8570: quote names Talbot, row says Sunil Bakshi), crowd end "ESU" (b2685) |
| E_A145_same_sentence | (lint_work) | fought + defeated/killed for one pair quoted in the same sentence → drop fought (b2576, b10175). Separately stated fights stay (step 5): most of the 1,028 fought+defeat rows are legit |
| name_short_and_full | ~500 raw, filtered | one name per person (A4): "Coulson"+"Phil Coulson", "Pym"+"Hank Pym"; NOT relatives sharing a surname (Catherine/Geoffrey Wilder, Tony/Howard Stark) or places |
| F_alias_variant_* | ~80 | codename_of/also_known_as/real_name_of → `Alias|alias_of|Real` (directions are mixed!), epithets/renamed places → no alias (A148) |
| F_actual_with_asserter (asserter ≠ subject) | ~30 | claim mis-moded as actual, or drop asserter; several are garbage rows (b239 "Stark Industries missile|other_verb|hit", "home|located_at|Sokovia") |
| F_A134 / F_A125 / F_A115 / F_A146 | 48 / 55 / 42 / 3 | attempt word, copula object, clause object of a knowledge relation, died as other_verb |
| self pairs, symmetric both dirs | 7 / 19 | read |

Method (owner's 27B direction): batch the flagged windows (`rv.sh view 1 --from B-1` text + `lint_work.sh show B`
+ the relevant catalog rows) into 27B prompts asking for edit blocks in the `rv.sh fix` format; Claude reads each
window and each 27B answer, corrects it, then submits via `bash plan/review_tools/rv.sh fix $PWD/FILE | grep -v ^FIXED`.
Never `mark`. Read every flagged window in full (other errors get fixed too; the early facts backfill b1-b1161 is
the weakest part). Overlap partners: edit both sides identically, then `recon.sh check all` must again show only
logged exceptions (it showed 126 inconsistent pairs mid-lint-write; re-run — earlier final state was 115
components, all in `recon/exceptions.txt`).

## 4. Gold v2 review (after §3)

Needs a gold mode for the review tool: `big_review_v2.py` is tied to labels_v2/big_audit_v2/order(). Add env
switches (e.g. `BV2_SET=gold`: V2=`gold_v2/gold_labels_v2.jsonl`, AUDIT2=`gold_v2/gold_audit_v2.jsonl`, order =
gold_in order, passages from gold_in messages, wiki per series — gold has jjk/csm/bleach/db/opm/berserk/onepiece
too, all with `series/<s>/facts.db`). 27B pre-reviews each gold window (events re-checked + facts + tags), Claude
reviews and submits. Then lint the gold set with the same checks.

## 5. Compose + train (after §3 and §4 are clean)

`tools/train/compose_big_set.py` v2: events+facts+tags from the latest audit records (big + gold), output schema
`{"events":[...],"facts":[...],"tags":[...]}`, 30% empty share, `--short-system` (rewrite SHORT_SYSTEM for the
three layers), gold dev/dev_pool/test from the gold audit. Extend the scorer for facts/tags. Train Qwen3.5-9B
short prompt, seeds 1 and 2 (§4 of BIG_REVIEW_HANDOFF); ship bar ≥ .602 events F1 on the Marvel+MCU TEST, scored
once at the end, plus the old teacher re-scored on the revised test.
