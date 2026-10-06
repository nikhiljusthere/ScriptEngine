# THE method to make and verify event windows (canonical, owner 2026-10-07)

This is the ONLY sanctioned way to produce and verify event-labeled windows for training.
Every earlier method is retired (see the end). If a doc or script disagrees with this file,
this file wins.

## Ownership rule (owner, 2026-10-07) — binding

- **Only Claude may add new rules** (review rulings, pattern-catalog entries, labeler hints).
- **Only Claude may update the two files** `tools/train/big_flags.py` (the flagger) and
  `plan/BIG_REVIEW_PATTERNS.md` (the pattern catalog). No other agent, model, or script
  edits them; the 35B only *reads* their distilled form (label_hints.py + big_flags.check).
- `tools/train/label_hints.py` (the 35B's reminders) is derived from the catalog and is
  likewise edited only by Claude, and only to mirror catalog entries.

## Step 1 — make: 35B single pass, with hints and one repair turn

`tools/train/label_single.py` (hints and repair are ON by default):

1. System prompt = `plan/EXTRACTION_PROCEDURE.md` (the procedure the gold follows; cached prefix).
2. User turn = the window + at most 5 one-line reminders whose trigger words occur in THIS
   window (`label_hints.hints`, distilled from `plan/BIG_REVIEW_PATTERNS.md`).
3. The answer is gated mechanically (`label_single.gate`: verbatim quote, the 12 verbs, shape,
   no class/species/item ends, places only for arrived/departed/escaped).
4. `big_flags.check` runs on the gated rows; only if a flag fires, ONE follow-up turn lists the
   flags (max 8) and asks for the complete corrected JSON, which is gated again.

Measured on 96 hand-reviewed windows (`tools/train/eval_hints.py`, gold = Claude-reviewed rows):

| recipe | P | R | F1 | exact windows |
|---|---|---|---|---|
| single pass, procedure only (retired) | .694 | .436 | .535 | 38/96 |
| + hints | .707 | .503 | .588 | 37/96 |
| **+ hints + repair (this method)** | **.769** | **.532** | **.629** | **44/96** |

(`--baseline` turns hints and repair off; it exists ONLY to re-measure this table.)

## Step 2 — verify: Claude reviews every window

1. `tools/train/big_flags.py N` shows the next windows from the cursor with DUP/OVERLAP of
   reviewed windows, row FLAGs, MISS? cues, OK marks. Flags are prompts, never verdicts:
   every window is read in full.
2. Claude decides every window against `plan/EXTRACTION_PROCEDURE.md` + the rulings
   (`plan/BIG_REVIEW_HANDOFF.md` R1-R25) + the catalog (`plan/BIG_REVIEW_PATTERNS.md`).
3. Corrections: compact edits -> `tools/train/big_mkfix.py` -> `tools/train/big_review.py --fix`
   (same gate as the labeler; refused windows are fixed and resubmitted) -> `--mark N`.
4. Every new error class found is added to the catalog (and, where it can be matched, to the
   flagger and the hints) by Claude, and committed.
5. Before composing a training set: `tools/train/big_consistency.py` (overlapping windows must
   carry the same rows), then `tools/train/compose_big_set.py --reviewed`.

## Retired methods (do not use to make windows)

- The multi-pass drafter `tools/train/draft_v2.py` (example-bank retrieval, sentence and
  missed-event passes, 3-vote verifier; `plan/FLAWLESS_LABELING_PLAN.md`). Its module stays only
  because the gate reuses `draft_v2.check_rows`.
- The plain single pass without hints/repair (the first 5,206 rows of
  `series/universal/training/big/labels.jsonl`; still reviewed, never used unreviewed).
- Any other labeler, prompt, or unreviewed model output.
