# HANDOFF — review the 14k single-pass 35B labels, then train the 9B

Written 2026-10-07 ~01:10 by the Claude session that set this up (its budget
could not hold a full careful review: ~1,500 tokens per dense window x 12k).
The owner chose: **every window is reviewed by Claude in fresh sessions,
from the saved cursor, until the 12,000-window set is hand-checked**
("this 12000 dataset will also be flawless"). Read this file fully first.

## 0. Owner decisions (2026-10-06/07), binding

1. The student is **Qwen3.5-9B** (official), not the 4B (4B training cancelled).
2. New training data: ~12,000 NEW Marvel/MCU windows from the biggest unused
   pages, labeled by the **ninfer 35B in ONE pass per window** reading
   `plan/EXTRACTION_PROCEDURE.md` (no multi-pass draft_v2 pipeline).
3. **Claude reviews EVERY window** as it lands (35B keeps labeling); review
   continues across sessions from the cursor below.
4. Empty share of the 12k: **30%** (Claude's call per the council: the old
   57% + the loss bug taught "answer empty"). Hard empties (event wording,
   no event) preferred, ~75% of the empties.
5. All council fixes (2026-10-06) apply to training: step-level loss
   normalisation, no JJK earned empties, select on non-JJK dev, lower LoRA
   scale, cosine to zero without early stop, 2 seeds, CIs vs the teacher.
6. GPU-only; kill by exact PID only (never pkill/pgrep-cmdline loops);
   switchpoint entry in plan/SWITCHPOINT.md before any model switch; commit
   with explicit pathspecs only; never commit the owner's files
   (plan/JJK_VERIFY_7000_*.md, tools/train/verify_monitor.py, owner hunks in
   verify_row_wiki.py / qwen_worker.py, tools/train/infer.py, the
   `D series/{berserk,bleach,db,hxh,onepiece}/overrides.yaml` deletions).

## 0b. UPDATE 2026-10-07 ~04:50 (read first)

Labeling runner is now PID 512679 running `--hints --repair` (35B + review-derived reminders + one
repair turn; F1 .535 -> .629 on 96 reviewed windows). Its code, the review tools (big_flags.py,
big_mkfix.py, big_consistency.py, eval_hints.py, label_hints.py) and the pattern catalog live on
branch `big-review-flags` (worktree .claude/worktrees/big-review-flags): see
plan/BIG_REVIEW_PATTERNS.md sections E and F for the review loop and the runner resume command.
Review cursor: series/universal/training/big/review_cursor.txt. Rulings R9-R25 were added to the
main checkout's copy of this file (uncommitted there) and are mirrored in BIG_REVIEW_PATTERNS.md.

## 1. State at handoff

| what | where / value |
|---|---|
| windows selected (14,000) | `series/{marvel,mcu}/training/labels/big_in.jsonl` (+ `series/mcu/training/labels/big_receipt.json`); marvel 7,700 / 168 pages, mcu 6,300 / 140 pages; no pool/test/holdout/universal page; list/index/members pages excluded |
| 35B labels (append-only, shuffled order) | `series/universal/training/big/labels.jsonl`; status line in `labels.jsonl.status` |
| labeling runner | `tools/train/label_single.py` PID **471097** (8 workers, `--shuffle`, resumable) |
| ninfer 35B server | PID **470864**, `tools/train/ops/serve_35b_64k.sh`, :18081, model `qwen3.6-35b-a3b-ninfer`, **max 8 lanes (ninfer refuses >8)** |
| labeling rate | ~14-22 windows/min; ETA ~11:00 2026-10-07 |
| review cursor | `series/universal/training/big/review_cursor.txt` = **6** (b1-b6 reviewed; b2-b6 corrected) |
| corrections log | `series/universal/training/big/big_audit.jsonl` ({id, before, after, why}) |
| the 9B base | `/mnt/PROJECTS/hf_home/hub/models--Qwen--Qwen3.5-9B/snapshots/c202236235762e1c871ad0ccb60c8ee5ba337b9a` |
| pre-fix 9B baseline | `/mnt/PROJECTS/student_runs_9b/9B-lr1e-4-r16/best` (old recipe, epoch 3, dev F1 .539) |

Check health any time:
```
cat series/universal/training/big/labels.jsonl.status
scriptengine/.venv/bin/python tools/train/big_review.py --status
kill -0 471097 && kill -0 470864 && curl -s -m 3 localhost:18081/v1/models | head -c 80
```
If the runner died: restart it with the SAME command (resumable; it waits
and retries if the server is down, never writes failure rows):
```
setsid nohup scriptengine/.venv/bin/python tools/train/label_single.py \
  --in series/marvel/training/labels/big_in.jsonl --in series/mcu/training/labels/big_in.jsonl \
  --out series/universal/training/big/labels.jsonl --workers 8 --shuffle \
  >> series/universal/training/big/label_run.log 2>&1 < /dev/null &
```
If ninfer died: `setsid nohup bash tools/train/ops/serve_35b_64k.sh > ~/ninfer-work/logs/serve_35b_label14k.log 2>&1 < /dev/null &` (up in ~40 s).

## 2. The review loop (what each session does)

```
scriptengine/.venv/bin/python tools/train/big_review.py --next 10 --chars 4000 > $CLAUDE_JOB_DIR/tmp/rv.txt
# read rv.txt (Read tool), decide every window, write corrections:
scriptengine/.venv/bin/python tools/train/big_review.py --fix $CLAUDE_JOB_DIR/tmp/bfix.json
scriptengine/.venv/bin/python tools/train/big_review.py --mark <last b-number reviewed>
```
- `--next` prints each window in full (use `--chars 4000`: rows often quote
  text past 900 chars), the 35B's rows, and any rows the gates dropped.
- `bfix.json` = `[{"id": "<window id>", "why": "<rule-cited reason>", "events": [ALL final rows]}]`
  — the COMPLETE row list for the window (not a diff). The id is the window
  id (map b-number n -> line n of labels.jsonl). `--fix` runs the same gates
  as the labeler (verbatim quote, 12 verbs, shape, no class/species/item
  ends, places only for arrived/departed/escaped) and REFUSES a window that
  fails; fix and resubmit.
- Only correct what is wrong; a window you accept needs no entry. Then mark.
- Never edit labels.jsonl; corrections live only in big_audit.jsonl.
- Review in label order (the cursor). Empty windows are fast: check that no
  sentence states an event.
- Budget: ~1,000-1,500 tokens per dense window. Stop a session well before
  its budget ends; the cursor + audit log are the whole state.

### What to check in every window (in this order)

The rules are `plan/EXTRACTION_PROCEDURE.md` (the doc the 35B read). Its
measured weak spots on these big Marvel/MCU pages:
1. **Missed events** — go sentence by sentence: thawing/reviving/waking
   (awakened), rescues and life-saving acts (saved), "brought back to
   captivity" (captured), escapes from a named opponent (escaped), arrivals
   at named places, entries that meet everyone present (met), attacks or
   powers used on someone in passing (fought).
2. **Wrong verb** — "confronted" with no attack = met; "turned into stone",
   "trapped inside an armor/dimension" = sealed (not defeated/captured);
   knockout/"overpowered ... pushed off" = defeated; "joined the team" is
   NOT met.
3. **Ends** — one name per person (Captain Marvel = Mar-Vell: the real name
   in every row); groups -> named members when the window names members of
   that group taking part ("the Avengers" + Vision/Iron Man named -> member
   rows), group row only when no member is named; "Luke Cage's team" ->
   Luke Cage; never crowds/species ("Kree and Skrulls", "the Skrull fleet").
4. **Quotes** — the quote must STATE the event (not just the start of the
   sentence before it).

### Rulings made in the first batch (b1-b6), add new ones here

- R1 "City, State" / "City, Country" -> ONE arrived row with the most
  specific named place ("Sugar Land, Texas" -> Sugar Land).
- R2 "briefly confronted by X" (no attack stated) -> met, not fought.
- R3 "turned into stone by X" -> X sealed them; "trapped X inside a
  Hulkbuster Armor" -> sealed.
- R4 "joined the team" / "teamed up with" -> no met row.
- R5 "Thawing the hero out" (from suspended animation) -> awakened.
- R6 "merged with him to preserve his life" -> saved.
- R7 "X arrived with the defeated Y" after X confronted/battled Y -> X defeated Y.
- R8 A villain's magic/power used to manipulate or control someone -> fought.

## 3. When labeling finishes (~11:00)

1. Confirm `labels.jsonl.status` says done 14000/14000 and the runner exited.
2. Append a switchpoint entry, then stop ninfer by exact PID (470864, or
   look it up: `ps -eo pid,cmd | grep "ninfer-serve models/qwen3_6_35b" | grep -v grep`).
3. Keep reviewing (the review never needs the GPU).

## 4. Compose + train (after >=12,000 reviewed windows, mix reachable)

Compose from REVIEWED windows only (corrections applied), both prompt variants:
```
scriptengine/.venv/bin/python tools/train/compose_big_set.py --reviewed --n 12000 --empty-share 0.30
scriptengine/.venv/bin/python tools/train/compose_big_set.py --reviewed --n 12000 --empty-share 0.30 --short-system
```
-> `series/universal/training/student_big{,_short}/` = 3,315 verified gold
train windows + 12,000 reviewed big windows; dev/dev_pool/test stay gold.
(If fewer than 8,400 reviewed eventful windows exist, compose takes what
exists — check the receipt's big_empty_share before training.)

Train the 9B (GPU free, ninfer stopped), short-prompt arm first (~1.5 h/run):
```
M9=/mnt/PROJECTS/hf_home/hub/models--Qwen--Qwen3.5-9B/snapshots/c202236235762e1c871ad0ccb60c8ee5ba337b9a
D=series/universal/training/student_big_short
for seed in 1 2; do
  PYTHONUNBUFFERED=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True ~/train-env/bin/python \
    tools/train/sft_qwen.py --model $M9 --train $D/train.jsonl --dev $D/dev.jsonl \
    --select-dev $D/dev_pool.jsonl --out /mnt/PROJECTS/student_runs_big/9B-short-a16-lr1e-4-s$seed \
    --lr 1e-4 --rank 16 --alpha 16 --dropout 0.05 --epochs 2 --patience 99 --seed $seed \
    --loss-norm step --micro-batch 2 --accum 8
done
```
(rsLoRA alpha 16 at r16 = update scale 4, half the old 8; `--patience 99` =
no early stop; the best epoch is kept on dev_pool.) A full-prompt arm
(`student_big`) costs ~3 h/epoch; run it only if the short arm disappoints.

Score with intervals against the teacher on the same gold windows:
```
scriptengine/.venv/bin/python tools/train/score_subsets.py --gold series/universal/training/student/dev.jsonl \
  --pred /mnt/PROJECTS/student_runs_big/9B-short-a16-lr1e-4-s1/dev_preds_e2.jsonl --pred .../s2/dev_preds_e2.jsonl --teacher
```
Bars: teacher (frozen multi-pass) .569 pool-dev / .530 Marvel+MCU dev;
single-pass 35B+doc .628 / .574. **Ship bar: >= .602 F1 on the Marvel+MCU
TEST split**, scored once at the end (test preds: `tools/train/eval_base.py
--model $M9 --adapter <best> --in series/universal/training/student_big_short/test.jsonl`,
then score_subsets with `--gold series/universal/training/student/test.jsonl`).
Then the serving benchmark (vLLM/SGLang windows/min) for the Marvel+MCU run.

## 5. Reference

- Council verdict + fixes: commit 8556f07b; memory `project_student_training_state.md`.
- Procedure doc + selector + runner: commits b3b6aaea, d62f51f5.
- Why the 35B errs (3,000 pool windows): row P .751 R .557 — misses in
  windows where it found other events (604), end errors (443 FN + 238 FP),
  empty answers on eventful windows (360 FN), wrong verbs (203).
- Pilot on 151 gold pool-dev windows: 35B single pass + doc F1 .628;
  frozen multi-pass .569; 35B without thinking .398.
