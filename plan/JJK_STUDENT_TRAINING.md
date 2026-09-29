# Student model — how the event extractor gets distilled (prep, 2026-09-29)

Status: **PREPARATION ONLY.** Nothing here trains until P5 (council) has
declared the labels. This file fixes the method *before* the data exists, so the
data is built to fit it and the result cannot be tuned after the fact.

Governing plan: `plan/JJK_100_PLAN.md` (P6). Verification that feeds it:
`reports/jjk/VERIFY_2026-09-29.md`.

## 0. Where the labels stand (measured 2026-09-29, judge A only)

| label source | precision | share of rows |
|---|---|---|
| JJK `.9` corpus, all rows | 77.3% ± 6.7 (n=150) | 8,491 rows |
| JJK `.9`, `verified = 1` tier | 93.0% (n=71) | 3,830 rows (45%) |
| JJK `.9`, `verified = 0` | 62.8% (n=78) | the rest |

So the teacher is a ~77% labeler on JJK, and the verifier's "yes" tier is a
~93% labeler that covers 57% of the true rows. A student trained on all rows
converges on the 77% labeler. That's the reason §2 filters per window. Every
production run from now on carries the trace (`series/jjk/events_trace_2026-09-29.9.jsonl`
holds JJK's), so the export in §9 has its inputs. These numbers are one
judge's; §6 still requires the second judge before anything trains.

## 1. What the student learns

One task, exactly the teacher's call: *(system prompt with this wiki's verb
definitions, page title, section title, one ≤4,000-char window) →
`{"events": [{"quote","subject","verb","object"}, …]}`*.

- **Input = the exact window the teacher read**, not the section. The extractor
  splits sections into 4,000-char windows with 300-char overlap
  (`abilities._windows`) or packs a small page into one call, and the store
  keeps neither. The input is recorded by the teacher trace
  (`SCRIPTENGINE_EVENTS_TRACE=<jsonl>`, added 2026-09-29): one line per model
  call, holding the window, the holders (section ids / passage labels), and the
  raw answer. **Every production extraction from now on runs with the trace
  on.** Without it there are no exact inputs, and no negatives.
- **Negatives are first-class.** A window whose answer is `{"events": []}`
  stores no row, so only the trace knows it was read. A student trained only on
  windows that produced rows learns that every window has events and
  hallucinates on descriptive prose (JJK: technique pages, Trivia-like prose).
  Keep the teacher's natural empty rate. Do not rebalance it.
- **Thinking off**, as the teacher ran. Granite-4.2 ships native `<think>`, so
  train with an empty think block and serve with thinking disabled. Otherwise
  student and teacher differ in two ways at once and a delta can't be attributed.

## 2. Labels — what counts as a target

The label is the **whole event list for a window**, so filtering is done
**per window, never per row**. Dropping one bad row from a window's target
teaches the student to *omit* that event: a precision fix that silently becomes
a recall bug. The verifier makes this acute: it rejects about half of the true
rows (`events.py`, verification-pass note). Filtering rows by
`verified = 1` would cut recall to about half and teach the student to stay
silent.

A window is **eligible** when:

1. every row the teacher proposed for it survives G1 (verbatim), G2 (legal
   verb), G3 (self-object), G4 (movement object is a place/group), and the
   resolver resolved both ends (no `unknown_participant` drops in that window —
   a dropped proposal means the target would be missing an event the model
   *did* see);
2. no row in it has `verified = 0`. `verified = NULL` is allowed (unanswered is
   not a no);
3. the page is not in a held-out split (§4).

This is a strict filter and it biases toward easy windows. Report the eligible
fraction by page type. If it falls below about 40% of windows, that bias is the
headline finding, and the fix is better labels (adjudication, a better
resolver), not a looser filter.

**Target text = the teacher's raw answer for the window, re-serialised from the
surviving parsed entries**, with names as the *mentions* the model wrote, not
the resolved canonical names. The student learns to read. Resolution stays in
the engine, where it is per-wiki and testable.

## 3. How big it has to be

| source | windows (est.) | note |
|---|---|---|
| JJK `all` scope | ~1,600 | 5.53M chars / ~3.7k per window |
| MCU full run | tens of thousands | shard 1 alone: 6,593 passages / 1,000 pages |
| Marvel full run | largest | 179,276-page `all` queue |

JJK alone is **too small to train a student, and is the right size to test
one**. The plan's own reference: STAGE (Qwen3-4B, 18K grounded examples,
31.4 → 74.3% EM). This citation is taken from the plan and has **not been
verified here**. Below about 10K eligible windows a fine-tune is not worth the
GPU time. So the training set is Marvel + MCU `.7` windows. JJK is the
**held-out generalisation test**: a different wiki, different prose, a
different verb inventory. If a student trained on Marvel/MCU extracts JJK as
well as the teacher does, "universal" has been measured rather than asserted.

## 4. Splits (by page, never by row)

- **Train/dev** by page within Marvel+MCU, 95/5, seeded. Never split a page
  across splits: overlapping windows would leak.
- **Test A (in-domain):** 200 held-out Marvel+MCU pages.
- **Test B (cross-wiki):** all of JJK's eligible windows. JJK is never trained on.
- **Test C (cross-wiki, second):** CSM, once CSM has `.7` rows.
- Gold for each test is the **adjudicated judged set** (§6), not teacher output.
  Scoring a student against its teacher measures imitation, not correctness.

## 5. Candidates

| | Granite-4.2-3B | Qwen3.5-9B |
|---|---|---|
| licence | Apache-2.0 | Apache-2.0 |
| on disk | no (download ~6–7 GB) | yes, `/mnt/PROJECTS/hf_home` @ `c2022362`, 19 GB |
| fits a full fine-tune on the 5090 | LoRA certain; full FT is tight at bf16 + 8-bit Adam | LoRA/QLoRA only |
| serve speed | much faster; the reason to want it | ~3× the 3B's cost |
| risk | label noise imitated more faithfully | **shares weights with Open-Jev's base** |

The brief treats "Open-Jev's base is also the future student" as a convenience.
**It is a risk.** If the verifier and the student share a base model, their
errors correlate: the verifier is weakest exactly where the student is
wrong, and the confidence tier stops meaning anything for student-extracted
rows. Either keep the verifier on a different base (the 27B yes/no verifier
already is), or don't use Open-Jev to verify a Qwen3.5-9B student's output.

Recommended order: **Granite-4.2-3B first.** It is cheap to train, and its
failure is informative: if a 3B can't reach the bar with clean labels, the
9B pilot is justified. The 9B second, only if the 3B misses.

## 6. Measurement — the binding constraint

Nothing above is decidable on 30 or 60 judged rows. The 27B's 87% (52/60)
against a 57% alternative is a real gap, but 90% vs 80% on 30 rows is three rows.
Before any student is trained:

- **Precision set:** ≥300 rows, stratified by verb and page type, from the `.7`
  JJK + Marvel + MCU stores. Two independent judges (the owner or a second
  model family, plus Claude), then adjudication of disagreements. Report
  inter-judge agreement (κ). If κ < 0.7 the guideline is the problem. Fix the
  guideline before scoring anything.
- **Recall set:** ≥40 windows (not rows) where a judge lists *every* event the
  window states, blind to the model's output. Precision alone rewards a model
  that says nothing.
- **Scored per row** on (subject mention → node, verb, object mention → node)
  with the quote required to overlap the gold quote. Verb confusions are
  reported as a matrix: `fought` vs `defeated` is the one that matters for
  match-ups.

## 7. Pre-registered decision rule

A student replaces the teacher for a wiki only if, on Test B (JJK) **and** Test A:

1. F1 ≥ teacher F1 − 3 points, on the adjudicated sets;
2. G3 + G4 violation rate ≤ the teacher's;
3. JSON validity ≥ 99.5% *without* constrained decoding (with it, 100% by
   construction, which is why it is reported off);
4. throughput ≥ 3× the teacher's windows/s on the same card.

Missing any one of these means no swap: the student stays a research artifact
and the teacher stays in production. Written down now so it can't move later.

## 8. Tooling (not installed; install when P6 opens)

No venv on this machine has `peft`, `trl` or `bitsandbytes` (checked
2026-09-29). Training gets its own venv (`~/train-env`, torch cu130 for the
5090) and **never** touches `scriptengine/.venv`: a training dependency has no
caller in the engine. Minimal stack: `transformers`, `peft`, `trl` (SFT on
chat-formatted pairs, loss on the assistant turn only), `datasets`. LoRA r=16–32
on all linear layers, seq len 4,096 (window ≤4k chars ≈1k tokens + ~1k system
prompt + answer), lr 1e-4–2e-4, 2–3 epochs, early stop on dev F1, not dev loss.
Serve the student through the same SGLang path with `response_format`
json_schema (verb enum). Constrained decoding helps a 3B much more than it
helps the 27B.

## 9. The export (to write when P5 closes)

`tools/export_training.py`: trace JSONL + gated store → `{train,dev,testA,testB}.jsonl`,
one chat record per eligible window, plus a receipt of the eligible fraction by
page type and by drop cause. Deterministic, seeded, re-runnable. It reads the
trace and the store and writes nothing back to either.

## 10. Progress log (2026-09-29, evening)

**Pilot gold done: 400 train windows, 966 events** (`series/jjk/training/gold/`
`gold_000..021.json` → `gold_pilot_all.jsonl`; 173/400 windows correctly empty).
Method: Q6 worker candidates (thinking, `--effort medium`) ∪ teacher targets,
every label adjudicated by Claude under `plan/EVENT_ANNOTATION_GUIDELINE.md`;
missed events written by hand; every quote verified verbatim by `build`.
Verb mix: fought 400, met 224, defeated 97, saved 65, killed 59, arrived 49,
awakened 20, escaped 19, sealed 18, captured 9, departed 4, betrayed 2.

**Label sources scored against that gold (400 windows):**

| source | recall | precision |
|---|---|---|
| Q6 worker (medium) | 87.0% | 92.5% |
| teacher target (current silver) | 62.5% | 67.5% |

The Q6 figure is anchored (the gold was adjudicated from its candidates); on
the independent 40-window test gold it scored 69.2% / 85.0%. Either way the
teacher silver is the weakest link, so the warm-up set is rebuilt from Q6:
**silver v2** = Q6 labels on the 3,975 non-gold train windows + the 400 gold
windows (`gold_tools.py silver`; a window whose rows cannot all be validated is
dropped whole — 3/400 on the pilot).

**Runs** (test = 40-window hand gold, `tools/eval_extraction.py`):

| run | data | recall | precision |
|---|---|---|---|
| zero-shot Granite-4.2-3B | — | 8.4% | 37.0% |
| A | gold 205, 4 ep | 44.9% | 57.3% (overfit, loss 0.02) |
| B1 | teacher silver (205 gold swapped in), 2 ep | pending | |
| B2 | B1 → gold 400, 2 ep | pending | |
| C1 | silver v2 (Q6 + gold), 2 ep | pending | |
| C2 | C1 → gold 400, 2 ep | pending | |

Chain: `/tmp/jjk100/runB.sh` then `/tmp/jjk100/chainC.sh` (status files
`/tmp/jjk100/runB_status`, `/tmp/jjk100/chainC_status`). The 40-window test
gold is small (107 core events, ±~9 points): a winner there is confirmed on a
larger test set before any swap (§7 still binds).

**Test gold v3 (100 windows, 180 core events)** — `series/jjk/training/recall_gold_v3/`:
the 40 v2 windows + 60 more held-out test windows annotated blind (passage
only, no model output), so the test stays independent of the Q6 labels run C
trains on. `eval_extraction.py --gold-dir series/jjk/training/recall_gold_v3`.
Teacher target on v3: 62.8% recall / 73.0% precision (agrees with the pilot's
62.5 / 67.5; the 40-window set alone read 47.7% recall). Q6 and every Granite
adapter are scored on v3 by `/tmp/jjk100/post_v3.sh` after the chain.

### Owner directive 2026-09-29 18:10 — Granite trains on verified data only
Runs B and C (teacher silver / unverified Q6 silver) were **stopped**; nothing
has been trained on unverified labels. Pipeline now: Q6 extracts (thinking on,
guideline) → verifier pass → Claude adjudicates every window → Granite.

**Q6 on the blind 100-window test gold v3: 77.2% recall / 77.1% precision**
(teacher target 62.8 / 73.0). Better than the teacher, still wrong on ~1 row
in 4, so no Q6 row trains the student unverified.

**Verifier candidates, measured on the 400 adjudicated pilot windows** (correct
rows = kept in gold; wrong rows = rejected and not a redundant duplicate):

| verifier | AUC | wrong rows passed @0.5 | correct rows passed @0.5 |
|---|---|---|---|
| Open-Jev-9B (ZefanCai, LoRA on Qwen3.5-9B, `:8791`, CUDA), plain question | 0.47 | 89% | 85.5% |
| Open-Jev-9B, guideline rules in the question | **0.671** | 67% | 87.5% |
| Q6 verifier (`tools/train/verify_rows.py`, thinking on) | pending | | |

Open-Jev-9B runs here (needed `C_INCLUDE_PATH` to `~/vllm-env-extra/usr/include`
for Triton's `Python.h`; ~18.9 GB VRAM, 0.06 s/row), but as a one-step decision
model it cannot do the guideline-level reading (attempt vs act, class vs name,
who did it). decider-0.8b was not scored (stopped on owner instruction).

### Learning curve on the blind v3 test (100 windows, 180 core events), 2026-09-29 19:06

| model | training data | recall | precision |
|---|---|---|---|
| Granite A | 205 verified windows, 4 ep | 46.1% | 53.9% |
| Granite D | 400 verified windows, 3 ep | 53.9% | 56.7% |
| teacher target | — | 62.8% | 73.0% |
| Q6 worker | — | 77.2% | 77.1% |

Doubling the verified data bought +7.8 recall, +2.8 precision: the student is
still data-hungry and well below its labeller. Extrapolating the per-doubling
gain, ~1,000 windows lands near ~60–64% recall — below Q6 and near the teacher —
so the owner's smaller set (1,000 windows: `gold/ids_1000.json`, 400 pilot +
`select_600.json`) is a checkpoint, not the finish line: it is trained and
measured, and the Q6 extraction + wiki check continue on the remaining windows
(nothing done for the 1,000 is wasted — it is a subset of the full set).

### Council 2026-09-29 (owner-requested) — adopted design
Full record: `reports/jjk/COUNCIL_student_training_2026-09-29.md`. Adopted:
- **Loop:** two independent drafts per window (Q6 extraction + stored teacher rows
  for the 1,000; opencode model + Q6 corrector for the 1,500; teacher rows + Q6
  corrector for the 500) → Q6 row-by-row wiki check as a FLAGGER → Claude reviews
  every window, passage first → disputes settled from the passage alone (the wiki
  card may flag, never add or confirm) → a blind re-annotation of a random 5% of
  finished windows measures the training set's own error.
- **Training:** Granite-4.2-3B, LoRA r=64 all-linear, lr 1e-4 cosine, batch 8,
  3 epochs, verified windows only, natural ~43% empty windows, rare verbs ×3,
  teacher rows excluded; checkpoints at 1k/2k/3k (stop rule: <3 recall points
  2k→3k → targeted rare-verb mining instead of random windows).
- **Ship:** deterministic post-filter + 2-of-3 self-consistency (if affordable)
  + per-verb gates on a Marvel test set (≥95% killed/betrayed/captured, ≥90% rest).

**Test gold v4** (`recall_gold_v3/gold_test_v4.json`, 173 core + 97 optional):
second, independent annotation = Q6 blind (thinking, no draft) on all 100 windows;
34 windows disagreed, each settled passage-only. On v4: Q6 81.5/92.1 (biased up —
Q6 was the second annotator, its borderline rows became optional), teacher
64.7/74.8, Granite D (400) 54.9/57.9, Granite A (205) 48.6/56.2.

**Post-filter** (`tools/train/postfilter.py`): wrongly rejects 0 of 963 verified
rows once self-directed rows are allowed (the 2 duplicate rejects were real
duplicate pairs in the gold). On Granite D it barely moves precision (57.9 → 56.0):
its 95 false rows are meaning errors, not format errors — as the council predicted.
The levers are verified data and self-consistency, not filters.
