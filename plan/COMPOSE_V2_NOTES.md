# COMPOSE V2 NOTES: stage 8b, events + facts + tags student set (dry run 2026-11-03)

This was a dry run on a frozen snapshot, CPU only (tokenizer only, no weights, no GPU, no model server).
The final composition has NOT been run. It waits for the gold review to finish (§7).
Read with `plan/RESUME_HANDOFF_2026-10-28.md` (state), `plan/RESUME_HANDOFF_2026-10-14b.md` §5 and
`plan/BIG_REVIEW_HANDOFF.md` §4 (compose + train).

## 1. Files

| file | state | what |
|---|---|---|
| `tools/train/compose_big_set_v2.py` | rewritten (draft was cce9e736) | the v2 composer |
| `tools/train/check_v2_set.py` | new | independent checker of a composed dir: schema, verbatim, leaks, empty share, token lengths |
| `tools/train/score_layers_v2.py` | fixed + extended (draft was 6e3af649) | events / facts / tags F1 with CIs |
| `tools/train/eval_base_v2.py` | new, **GPU path not run** | v2 test predictions (full raw, all three layers, `--max-new 4096`) |
| `tests/test_compose_score_v2.py` | new | 10 tests, CPU, tiny fixture: `10 passed in 0.04s` |
| `tools/train/compose_big_set.py`, `eval_base.py`, `score_subsets.py`, `sft_qwen.py` | untouched | |

Data (main checkout, gitignored): `series/universal/training/student_v2_draft/` (483 MB). It holds
`snapshot/` (the frozen inputs), `run1/`, `run2/` and `runA/` (the three dry-run compositions, byte-identical),
`run*.log` (composer receipts on stdout) and `run1.check.json` (the checker output).

## 2. What the composer does

- **Source of every row.** Each row is the latest audit record of its window, using `big_review_v2.audit2()`'s
  rule: latest wins, and a `{"id","void":true}` line withdraws the record before it. That covers the 29 b501–b540
  voids. The draft's plain "last line wins" agreed with this rule only because every void is followed by a
  later record.
  - big: `big/big_audit_v2.jsonl`, all 14,000 windows.
  - gold: `big/gold_v2/gold_audit_v2.jsonl`. A gold window with no record fails the run unless
    `--allow-unreviewed-gold` is passed.
- **Splits** come from `gold_v2/gold_in.jsonl` `splits`, which match `student_clean` exactly: train 3,315,
  dev 215, dev_pool 151 (inside dev, non-JJK), test 292. Gold train holds 0 JJK earned empties: the 682
  earned-empty ids from `student/` are checked and none appear.
- **Answer shape** follows `EXTRACTION_PROCEDURE_V2.md`'s shape and key order:
  - events `{quote, subject, verb, object}`;
  - facts `{quote, subject, relation, object, modality, certainty, asserted_by, canon}`, all 8 keys every time,
    `canon` null when unset;
  - tags `{quote, tag}`. The audit files store `{tag, quote}`; the procedure puts the quote first.
  - Serialised with `json.dumps(ensure_ascii=False)`, as v1, so the event text is unchanged.
- **System prompt.** `SHORT_SYSTEM` is rewritten for the three layers: 1,977 chars, **487 tokens**. It lists
  the 12 verbs, the gate-legal relations (fact_gate minus the 6 retired), modality, certainty, canon and the
  12 tags, plus the event-vs-fact partition rule, verbatim one-sentence quotes, and one name per person with
  no crowd, species or pronoun ends. `--short-system` is the default (the flag is still accepted);
  `--system-file` swaps the prompt for another arm.
- **Empty share.** `--empty-def all` (the stage-8b spec) counts a window as empty only when events, facts and
  tags are all empty. The cap is `--empty-share 0.30` over the big windows. Hard empties (big_in
  `kind == trigger`) are taken first, up to `--hard-share 0.75`.
- **Fails, and writes nothing, on:**
  - a non-verbatim quote, or an empty subject;
  - a verb, relation, tag, modality, certainty or canon outside the vocabulary;
  - a retired relation (child_of and married_to are normalised as lint M5 did);
  - an actual fact with an asserter, or a non-actual fact without one (except `hypothetical`, allowed by B.4);
  - a gold window with no audit record;
  - an earned empty;
  - an id, exact page or passage shared by train, dev and test;
  - dev_pool not inside dev;
  - a big window on a gold page.
- **Always left out:** a big window that repeats a dev/test sentence of 40+ characters word for word. The dry
  run found 1, b12950 "Iron Man/A.I.M. Operative Controller", which repeats a test sentence from "Iron
  Monger/A.I.M. Operative Controller".
- **Reported, not fatal:** base-page shares (`Denji` vs `Denji/History`); see §6.

## 3. Dry run: commands and outputs

The snapshot was taken 2026-11-03, copied read-only from the live files. Hashes are in `run1/receipt.json` `inputs`:

| file | lines | sha256 (prefix) |
|---|---|---|
| big_audit_v2.jsonl | 19,911 (14,000 windows) | c9e04b93 |
| gold_audit_v2.jsonl | 3,868 (**3,822 / 3,822 windows have a record**) | 1e4b6223 |
| gold_in.jsonl | 3,822 | d4e8eceb |

```
cd /home/goblin/ScriptEngine/.claude/worktrees/big-review-flags
P=/home/goblin/ScriptEngine/scriptengine/.venv/bin/python
D=/home/goblin/ScriptEngine/series/universal/training/student_v2_draft
$P tools/train/compose_big_set_v2.py --snapshot $D/snapshot --out-dir $D/run1 > $D/run1.log   # rc 0, ~2 s
$P tools/train/compose_big_set_v2.py --snapshot $D/snapshot --out-dir $D/run2 > $D/run2.log   # rc 0
PYTHONHASHSEED=987 $P tools/train/compose_big_set_v2.py --snapshot $D/snapshot --out-dir $D/runA
CUDA_VISIBLE_DEVICES= $P tools/train/check_v2_set.py $D/run1 > $D/run1.check.json                # rc 0, errors 0
$P -m pytest tests/test_compose_score_v2.py -q                                                    # 10 passed
```

## 4. Validation numbers (run1 = run2 = runA)

- **Determinism:** run1, run2 and runA (`PYTHONHASHSEED=987`) are byte-identical, receipts included. sha256:
  train 82f0ddd3…, dev ce581226…, dev_pool 1d9240d2…, test 258207ba….
- **Rows per split:** train **17,314** (gold 3,315 + big 13,999), dev 215, dev_pool 151, test 292.
  - train by series: marvel 8,205 · mcu 6,808 · jjk 761 · csm 265 · bleach 256 · db 256 · opm 255 ·
    berserk 254 · onepiece 254.
  - train layer rows: events 33,923 · facts 84,694 · tags 35,496.
- **Schema and verbatim (checker):** 0 errors over all 17,972 rows. Every row has system, user and
  assistant; the assistant JSON equals the row's own layers; every layer has its exact keys in order; the
  vocabulary passes; every quote is verbatim in the passage; there is one system prompt; and every prompt ends
  in the empty think block (`sft_qwen.render_prompt`'s assertion).
- **Leaks:** 0 shared ids, 0 shared exact pages and 0 shared passages for train–dev, train–test and dev–test.
  dev_pool is inside dev, 0 duplicate ids.
  - Exact sentences of 40+ chars still shared: train–dev 3 and train–test 1, all gold-vs-gold, inherited from
    student_clean.
- **Empty share, train split, by definition:**

  | definition | share |
  |---|---|
  | all three layers empty | 0.06% |
  | events + facts empty | 16.7% |
  | no events | 41.0% |

  On the big windows under `all`: 11 empties available, all 11 taken (6 hard). **The 30% cap does not bind.**
- **Token lengths** (Qwen3.5-9B tokenizer + chat template, `enable_thinking=False`; answer counts include EOS):

  | split | prompt p50 / max | answer p50 / p95 / p99 / max | total p50 / p99 / max | total > 4096 | answer > 2048 | answer > 1024 |
  |---|---|---|---|---|---|---|
  | train | 632 / 2,861 | 386 / 1,207 / 1,783 / 4,805 | 1,022 / 2,683 / 7,140 | **10** | 84 | 1,427 |
  | dev | 608 / 876 | 336 / 1,171 / 1,559 / 2,993 | 954 / 2,281 / 3,869 | 0 | **1** | 14 |
  | test | 596 / 972 | 228 / 1,032 / 1,732 / 2,884 | 839 / 2,476 / 3,856 | 0 | 1 | **15** |

  - Train totals 19.38M tokens per epoch, 8.15M of them supervised. The system prompt is 487 tokens on all
    17,314 rows, about 8.4M tokens or **43% of the epoch**.
  - The 10 rows over 4,096 are the densest windows: gold `"Future" Trunks Saga` (7,140), gold
    `Arthur Pendragon (Earth-616)`, 2× `Steven Rogers (Earth-13122)`, `Earth-616`, `Prime Universe`, ….

## 5. Scorer: what was wrong and what changed

`score_layers_v2.py` scores events with the existing `eval_extraction.score` (the scorer behind the .602 bar, so
event numbers stay comparable). It also scores:
- **facts:** relation and modality must be equal, both ends must match by `ee.same`, symmetric relations match
  either way round, and `other_verb` matches on subject plus a verb prefix. Matching is greedy one-to-one.
- **tags:** same tag, and the quotes overlap by containment.

Fixed and added on 2026-11-03:
1. **Bug:** `load()` read the record's own keys whenever `events` was present. Both `sft_qwen.dev_generate`
   and `eval_base.py` write `{id, events, raw}`, so every fact and tag scored as missed. `load()` now parses the
   full `raw` first and falls back to the record's keys. It also records per-window v2 JSON validity.
2. Refactored into a `score_layers()` function so it can be unit-tested.
3. New output: agreement on matched facts for the fields the match ignores (certainty, asserted_by, canon).
4. The smoke test on the composed test split (perfect predictions taken from the gold answer) gives
   F1 1.000 / 1.000 / 1.000, JSON valid 1.000 and agreement 1.000.

Changes still needed in code this task did not touch (training and GPU code):
- **`eval_base.py` cannot produce v2 predictions.** It parses events only, keeps `raw[-3000:]` (cutting the head
  of the answer) and defaults to `--max-new 1024`, while 15 test answers are longer. Use the new
  `eval_base_v2.py`. Its GPU path has not been run: smoke it on about 8 windows first.
- **`sft_qwen.py:159`:** `max_new = min(max(max_new, 256), 2048)` cuts the longest v2 dev answer. That answer
  is 2,993 tokens, sits in dev_pool too, and its rule asks for 5,213. A cut answer is invalid JSON, so the
  window's events are lost from checkpoint selection. **Raise the cap to 4096.**
- `sft_qwen.dev_scores` selects checkpoints on event F1 only. That is fine for the ship bar; facts and tags are
  scored afterwards with `score_layers_v2.py --pred RUN/dev_preds_eN.jsonl`, which reads the full raw.
- `score_subsets.py --teacher` reads `ROOT/series/...`. Run it from the main checkout: from the worktree it
  silently prints nothing.

**Old teacher re-scored on the revised test** (`draft_frozen`, events, from the main checkout).
Provisional: this is the snapshot gold.

| gold | all (n=292) | marvel+mcu (n=123) | dev_pool (n=151) |
|---|---|---|---|
| old student_clean | .643 | **.602** (reproduces the ship bar) | .569 |
| v2 snapshot | .571 [.484–.659] | **.522 [.415–.639]** | .496 |

The gold events changed in 58 of 292 test, 63 of 215 dev and 785 of 3,315 train windows.

## 6. Open decisions for the owner

1. **Empty definition.** Under the spec's `all` definition the 30% cap is moot: 11 of 14,000 big windows have
   nothing at all, because the coverage rule tags almost every window. The council's concern was "answer
   nothing" on events. Under v1's definition (`--empty-def events`) the cap drops **1,715** big windows
   (train 15,599), many of them fact-only windows, so fact training data is lost. `events+facts` gives 13.9% on
   big and drops nothing. Recommendation: keep `all`, with no drops.
2. **New ship bar.** The teacher scores .522 on the revised Marvel+MCU test, against .602 on the old one.
   Either the student must beat the teacher on the same revised test, or the bar stays .602 on old-gold
   events. Re-score after the final compose.
3. **`--max-len`.** At 4096, sft_qwen drops 10 train rows, the densest windows. At 8192 all of them are kept
   (max 7,140). Memory at that length on the 32 GB card has not been verified.
4. **System prompt cost.** It is 487 tokens, 43% of training tokens. A v1-style instruction of about 70 tokens
   with no vocabulary lists would cut the epoch about 37% (19.4M to about 12.2M tokens); the student would learn
   the vocabulary from the labels.
5. **Base-page overlap.** 166 big train windows sit on the base page of a test page: `Robert Drake (Earth-616)`,
   `Iron Monger`, `Thor` and `2015/Norman Osborn-Mentored Spider-Man`. They share no passage, and only the one
   sentence already dropped. `--drop-base-page-overlap` removes them (train 17,148). The gold-vs-gold base-page
   shares (train–dev 42 windows, train–test 18) are inherited from v1's frozen split.
6. **`other_verb` share** is **56.5%** of train facts (big 54%, gold 68%), against the procedure's under-10%
   aim. The data is consistent, but the fact layer is dominated by the escape hatch. The scorer's `other_verb`
   rule (subject plus verb prefix) is lenient.
7. **Format choices** (cheap to flip before training): tag key order `{quote, tag}` (the procedure's order)
   and `canon` always present.
8. Open rulings from the 2026-11-03 handoff (vehicles not places, page-title ends, the "the king" case and
   others) are not decided. They change labels, not the composer.

## 7. Final re-run (after the gold review finishes; do not run before)

Preconditions:
- the review agents are stopped and every gold window has a record;
- the gold lint is clean (`BV2_SET=gold bash plan/review_tools/lint.sh`, or the `lint_gold*.sh` tools that
  appeared in `plan/review_tools/` during this session; another session wrote them, not this one);
- the open rulings in §6.8 are decided.

```
cd /home/goblin/ScriptEngine/.claude/worktrees/big-review-flags
P=/home/goblin/ScriptEngine/scriptengine/.venv/bin/python
B=/home/goblin/ScriptEngine/series/universal/training/big
OUT=/home/goblin/ScriptEngine/series/universal/training/student_v2_short
mkdir -p $OUT/snapshot && cp $B/big_audit_v2.jsonl $B/gold_v2/gold_audit_v2.jsonl $B/gold_v2/gold_in.jsonl $OUT/snapshot/
$P tools/train/compose_big_set_v2.py --snapshot $OUT/snapshot --out-dir $OUT          # + --empty-def / --drop-base-page-overlap per §6
CUDA_VISIBLE_DEVICES= $P tools/train/check_v2_set.py $OUT > $OUT/check.json; echo rc=$?   # must be 0, "errors": 0
cd /home/goblin/ScriptEngine && scriptengine/.venv/bin/python tools/train/score_subsets.py --gold $OUT/test.jsonl --teacher   # the revised bar
```

The training command is `BIG_REVIEW_HANDOFF.md` §4 with `D=$OUT`, plus `--max-len 8192` per §6.3 and the
`sft_qwen.py:159` cap raised to 4096. Score with:
- `score_subsets.py --gold $OUT/dev.jsonl --pred RUN/dev_preds_eN.jsonl` for events;
- `score_layers_v2.py --gold $OUT/dev.jsonl --pred RUN/dev_preds_eN.jsonl` for all three layers.

Test predictions come from `eval_base_v2.py --in $OUT/test.jsonl --max-new 4096`, scored once at the end.
