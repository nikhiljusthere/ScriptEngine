# RESUME HANDOFF — after the overlap reconciliation (written 2026-10-14)

For a NEW Claude session. Read in this order:
1. `plan/RESUME_REVIEW_HANDOFF_2026-10-10.md` §1: the binding owner rules.
2. `plan/RESUME_REVIEW_HANDOFF_2026-10-13.md`: the v2 forward pass, data locations and commit recipe.
3. `plan/RECONCILE_V2.md`: the reconciliation that this file closes.
4. `plan/BIG_REVIEW_HANDOFF.md` §4: compose and train.
5. `plan/BIG_REVIEW_PATTERNS.md`: the full catalog. Read the end notes in particular.

Branch `big-review-flags`, worktree `/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags`.
The data lives in the MAIN checkout, which is gitignored: `/home/goblin/ScriptEngine/series/universal/training/big/`.
Commits copy the data into the worktree with `git add -f`.

## 1. Owner rules (binding, unchanged)

- Never push.
- Commit with explicit pathspecs only.
- Never stage the owner's uncommitted hunks: `tools/train/label_single.py` (the opencode CACHE_BREAKPOINT hunk) and `plan/FACT_LAYER_PROGRESS.md`.
- "Continue inline, no subagents."
- Only Claude edits `plan/BIG_REVIEW_PATTERNS.md` and `tools/train/big_flags.py`.
  Measure every new rule or flag on approved windows before adding it, and note it in the catalog.
- A106 applies to ordinary sleep only. Write "Avengers, Inc." as "Avengers Inc." in ends.
- GPU-only work. Kill processes by exact PID only. Before any model switch, add a switchpoint entry to `plan/SWITCHPOINT.md`.
- If you are near the session limit: stop, wait for the reset, then continue.
- Model target for training (owner, 2026-10-13): **events + facts + tags** ("events + facts + tags, start with the consistency check").

## 2. State at handoff

- **All 14,000 windows are reviewed** in the v2 pass (events, facts and tags).
  Audit file: `big_audit_v2.jsonl` (append-only; the latest record per id wins).
- **The overlap reconciliation is DONE.** The owner's goal was "Option 2 ... I want clean flawless data".
  - Starting point: 1,024 overlap pairs, of which 960 were inconsistent, grouped into 838 components.
  - Split: 419 components went to the app session (`recon/done_app.txt`) and 419 to the terminal session (`recon/done_term.txt`). All 838 are done.
  - Final `bash plan/review_tools/recon/recon.sh check all`: 115 components still differ, and **all 115 are logged** in `recon/exceptions.txt` (116 entries). None is unlogged.
  - Allowed exception kinds:
    - A4 name: one window's text gives only a shorter or other name.
    - Pronoun-only window: the person is never named in it.
    - A2 member basis: an object or member is named in only one of the two windows.
- **Last commit:** `13c42d70` ("Recon term C813-C838 reconciled; all 419 term components done").
  The committed `big_audit_v2.jsonl`, `exceptions.txt`, `done_app.txt` and `done_term.txt` match the disk copies byte for byte.
  The worktree has no other changes except the two owner files. Nothing is pushed.
- No model is loaded. The GPU is free.

### Tool quirks learned (keep in mind for any further `rv.sh fix`)
- Two `@` blocks for the same window in one fix file: the later block replaces the earlier. Use one block per window.
- An `r Old=>New` rename applies at its position in the block. It can turn alias or transformed_into rows into self-pairs; repair those with `f-` / `f+`.
- `f-` matches regardless of modality.
- The dedupe key ignores the quote. To re-quote a row, use `f-` then `f+`.
- A REFUSED block stores nothing. Race ends are refused, so use crowd_end tags for them.
- Writing an arrival as a fact (`f+ X|arrived|Y`) is refused, and the whole block is lost. Arrivals are events (`+`).
- `met` seems to be deduplicated regardless of direction. To change the direction, remove both rows and re-add them.

### Conventions settled during reconciliation (both sessions applied them)
- Speech acts are actual, with no asserted_by.
- Beliefs and assumptions → `suspected|-`. Realising → `learned|-`. Physically finding something stays a literal other_verb.
- Orders: `X|ordered|Y` is actual, plus `Y|other_verb|verb|ordered|stated|X`. The 576 older rows are not yet normalised (see §3.1).
- Wounds: `attacker|wounded|victim`, or `victim|wounded|-` when no doer is named.
- A145: a confrontation that becomes the fight gets no met. fought is dropped when defeated, killed or sealed covers the same pair.
- Mind control and possession (A116): rows go to the controller or inhabitant. The controlled body gets no fight.
- Universes are not places (A78). Indefinite or descriptive places are dropped.
- Races and unnamed groups → crowd_end tags. Named teams can be doers.
- Aliases: `Alias|alias_of|Real`. Roles and titles are not `became`. Rulers → `leader_of`.

## 3. Next steps (owner has not yet assigned who does which)

The terminal session ("big review flags forward pass") is idle and waiting. Agree the split with it before starting.

1. **Order-modality normalisation.**
   - Of 1,271 approved `X|ordered|Y` facts, 576 carry modality `ordered`, where `actual` is the rule.
   - Owner-approved direction (catalog end notes): a one-shot normalisation plus a gate flag.
   - Measure first, then append audit records.
2. **NBSP verbatim issue.**
   - 24 of 14,000 windows contain U+00A0, and 21 rows were dropped for that reason alone.
   - It is OPEN in the catalog ("a whitespace-tolerant check would change every downstream quote lookup").
   - Note that `exact_quote` already repairs whitespace-only differences. Re-measure before changing anything.
3. **`tools/train/compose_big_set.py` v2.**
   - The current script (132 lines) is events-only and reads `labels.jsonl`.
   - It needs to build events + facts + tags from `big_audit_v2.jsonl` (the latest record per id) over `labels_v2.jsonl`.
   - It must apply the mechanical normalisations at compose time:
     - kinship direction (parent_of/child_of → one direction);
     - married/married_to (both are in the vocabulary and both symmetric).
   - Keep the 30% empty share and the `--short-system` variant.
   - **Open decision for the owner:** the 3,315 gold windows and the dev, dev_pool and test splits are events-only. Either the train/eval mix uses events-only gold, or the gold needs facts and tags too. Ask the owner before composing.
4. **Train Qwen3.5-9B** per `plan/BIG_REVIEW_HANDOFF.md` §4: short prompt first, seeds 1 and 2.
   - Ship bar: ≥ .602 F1 on the Marvel+MCU TEST split, scored once at the end.
   - Fact and tag scoring needs a scorer extension if the target includes them.

## 4. Useful commands

```
cd /home/goblin/ScriptEngine/.claude/worktrees/big-review-flags
bash plan/review_tools/recon/recon.sh check all        # must stay 0 outside exceptions.txt
bash plan/review_tools/recon/recon.sh view C           # one component
bash plan/review_tools/rv.sh fix $PWD/FILE | grep -v ^FIXED   # gated edits (BV2_CURSOR selects the cursor file)
```
