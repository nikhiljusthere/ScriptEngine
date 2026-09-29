# JJK VERIFY-7000 — the full-corpus strict verification campaign

**Owner directive (2026-09-30):** use the new Qwen3.6-35B-A3B to verify **every**
JJK window from the beginning, not just the 600 already adjudicated. The model is
fast enough that the whole corpus is affordable. Verdict rules get **stricter**,
not looser. Order: the ~1,500 opencode-session windows first, then the ~600–700
Qwen Q4/Q6/Q8 windows, then import the remaining JJK windows so all ~7,000 are
verified.

## 0. Why the 35B-A3B, and what changed

The verification step is the expensive one: for each candidate row it pulls the
wiki card for the subject and the object and conforms them against what the
passage states. That is a large-prompt, many-small-outputs workload, which is
exactly what this model is good at.

| | llama.cpp Q8 (old) | Qwen3.6-35B-A3B (new) |
|---|---|---|
| decode, 1 lane | 92 tok/s | 750–780 tok/s measured here; 906 on structured output upstream |
| decode, 2 lanes | — | **954 tok/s aggregate, measured** |
| prefill | 3,211 tok/s | **7,219 tok/s aggregate, measured** (17,705 upstream @ 7.7k) |
| context | 65,536 | **262,144** |
| lanes | 2 | 2 |
| load time | ~90 s | **31.8 s** |

Upstream (`docs/performance/qwen3.6-35b-a3b.md`, measured 2026-09-07 @ rev
`487f897`) reports acceptance 83.5% and 3.50 spec tokens/round for MTP3 on long
reasoning. Serve script: `tools/train/ops/serve_35b.sh` (durable).
Watchdog: `tools/train/ops/ninfer35_watchdog.sh`.

**Two build traps, both already hit and solved — do not repeat them:**

1. The artifact `qwen3_6_35b_a3b.ninfer` is **NInfer format v3**
   (magic `NINFER\0\x03`). The older `build/` binary (Sep 2) only accepts v2 and
   exits with `artifact magic is not NInfer v2`. **`build35/` is the binary to
   use.** The old `qwen3_8_27b_nvfp4.ninfer` is v2 and needs `build/`.
2. `build35/` is the only build with the current flag set. The Sep-2 build lacks
   `--device-state-slots`, `--host-state-slots`, `--host-kv-mib`, and caps
   `--kv-dtype` at `bf16|int8`.

## 1. The pools, counted exactly (2026-09-30)

Counted by unique window id, so these are not double-counted.

| Pool | Windows | File(s) | State |
|---|---:|---|---|
| **A. opencode sessions** | **1,500** | `opencode/{mimo,nemotron,spacebunny}_out.jsonl` (500 each) | drafted by 3 free-session models, **never human-adjudicated** |
| **B. Qwen Q4/Q6/Q8** | **1,000** | `gold/cand_q6_pilot400.jsonl` (400) + `gold/cand_q6_train.jsonl` (600) | 333 of the 600 adjudicated in `gold600/` |
| **A ∩ B** | 45 | | counted once |
| **C. full v1 corpus** | **4,375** | `v1/train.jsonl` | see the tier split below |
| **Union A ∪ B ∪ C** | **4,375** | | C is a superset: 2,455 of A∪B are already inside it |

**So the real total is 4,375 windows, not 7,000.** The pools overlap heavily and
the v1 corpus already contains most of A and B. Importing "all 4,000 JJK
windows" adds no new windows — it adds the 4,375 − 1,455 = 2,920 windows that
pools A and B never covered. The 7,000 figure double-counts. I am flagging this
rather than silently building a 7,000-row manifest; the owner can confirm.

### Tier split of the v1 corpus — this is why verification matters

| Tier | Windows | Events | What it means |
|---|---:|---:|---|
| `contested` | 1,534 | 7,274 | drafted, **disputed** — most need the most work |
| `empty` | 2,265 | 0 | claimed "no events" — must be re-checked for **false negatives** |
| `confirmed` | 343 | 661 | wiki-checker agreed |
| `unverified` | 233 | 594 | never checked |

Only 343 of 4,375 (7.8%) are `confirmed`. The 2,265 `empty` windows are the
silent risk: an empty list looks finished and is never audited, so a passage
whose events were all dropped is invisible. Under stricter rules these get a
full re-read, not a spot check.

## 2. Execution order

Owner directive (2026-09-30): **one window at a time, inline, no background
LLM calls, no auto-verifiers.** For each window I do the full pipeline — read the
passage, fetch every related wiki page, confirm every fact, write one row at a
time under the stricter rules, save it — then move to the next. This was the
method used to produce `gold600.jsonl`; it is correct for quality, slower for
wall-clock, and exactly what the owner ordered.

Order is still Phase 1 → 4 below, but each phase is driven by me, not by tools.

### Phase 1 — pool A, the 1,500 opencode windows

3 × 500, in `n` order, one window per line. These are the least-examined data
in the repo: drafted by free sessions, never adjudicated by a human, and the most
event-dense (spacebunny 842 / 500). Start here.

### Phase 2 — pool B, the 1,000 Qwen windows

Re-verify the 333 already-adjudicated under the stricter rules rather than
trusting the earlier pass. Continue the remaining 267.

### Phase 3 — import the rest of v1

Check whether `stage2_extra.jsonl` / `stage1_extra.jsonl` already cover part of
this before re-extracting. Then verify those windows.

### Phase 4 — the 2,265 `empty` windows

A separate pass: a window that produced `[]` and is wrong is worse than one that
produced a bad row, because nothing downstream notices it. Every empty window
gets its own reading.

## 3. The stricter rules

The base law is unchanged and still binding:
`plan/EVENT_ANNOTATION_GUIDELINE.md` (sections A–E) plus
`plan/JJK_OPENCODE_HANDOFF_2026-09-29.md` §5 and **§5a**. §5a holds six
precedents confirmed against the built gold — read it before adjudicating.

Stricter means, concretely:

1. **A row must be affirmatively proven, not merely unrefuted.** Default `no`.
   "The passage does not rule it out" is not evidence.
2. **Quote ≥ 12 characters, copied character for character, wiki typos kept.**
   Never repair spelling. The builder's `problems: 0` is the floor, not the goal.
3. **Both ends must resolve to the right wiki entity**, checked per row with
   `tools/train/wiki_card.py`, not inferred from the passage alone.
4. **A `killed` row needs a stated death**, and the object's wiki status must not
   contradict it. A "seemingly exorcised" curse that survives is not killed.
5. **No class, species, technique, domain or item as an end.** Named shikigami
   (Nue, Mahoraga, Max Elephant, Rika, Moon Dregs) are the exception.
   Groups and institutions are never ends.
6. **One row per pair for `fought` and `met`** — they are symmetric. Never both
   directions. The builder drops twins mechanically; do not rely on it.
7. **Ambiguity resolves to `no`, or to the more specific verb.** When two verbs
   fit, take the more specific (`killed` > `defeated` > `fought`); if the
   passage also states the fight, both `fought` and `killed` are correct.
8. **Every "no" row is kept and carries a one-sentence `rule`** naming the check
   that decided it. Rejected rows are the audit trail; deleting them destroys it.
9. **A missed-event pass on every window**: re-read once more for events not
   listed. This is the step that catches under-generation, and it is the one
   most often skipped.
10. **A `[]` verdict must be earned**, per Phase 4. Name in the `rule` field why
    the passage has no event.

**Never let the wiki card create or confirm a row.** It flags only. The passage
decides. This is handoff §6 and it is the single most important constraint in
this campaign: the wiki is evidence about entities, never evidence that an event
happened.

## 4. Doing it at this speed

- **Concurrency: 2 client workers**, matching `--max-concurrency 2`. Measured
  954 tok/s aggregate at C=2 (vs 650 upstream at C=1). A third worker only
  queues.
- **Set `SCRIPTENGINE_ANSWER_TOKENS=20480`** to match the server's
  `--default-max-tokens`. This is not a formality on this model: it reasons by
  default and will spend a small budget entirely on reasoning and return **empty
  content with `finish_reason: length`**. Measured — a one-sentence question
  returned empty at 2,048 tokens (1,142 spent on reasoning) and
  `Megumi Fushiguro` in 1.9 s at 20,480. **Any empty answer must be retried at a
  higher budget, never accepted and never treated as "no events".** A wrapper
  that reads empty content as an empty event list will silently manufacture
  thousands of false negatives across this corpus.
- **Retries:** all batch tools resume by themselves — a window counts as done
  only when its line has `ok: true`.
- **Per-batch acceptance:** rebuild after each batch; it must print
  `problems: 0`.
- **Stop and report** rather than grinding if a phase's disagreement rate runs
  high. The handoff's 5% blind re-check (step 6) is the calibration for this: if
  blind re-adjudication disagrees above ~3%, the rules or the model need work
  before more windows are drawn, not more windows.
- **Do not train on test-v4 ids** (`recall_gold_v3/gold_test_v4.json`), and do not
  train on anything not adjudicated — `build_trainset.py` refuses non-gold
  tiers; keep it refusing.

## 5. Drift prevention (new, addresses owner concern)

Over 7,000 windows a single model can silently drift — accepting rows it would have
rejected earlier, missing events it previously caught, or degrading output format.
Three safeguards are built into the workflow:

### Guard 1: Ruling Card refresh every 50 windows

A compact "rules anchor" that gets re-pasted into context at each batch boundary to
reset attention before repetition fatigue sets in. (§6.5 of inline resume prompt).

### Guard 2: Duplicate check every 200 windows

Re-verify 10 past results from the `.done` log. If >2 disagree with original verdicts,
re-read ALL guidelines and precedents. Catches model slipping on rule interpretation.

### Guard 3: Cross-pool consistency after each pool completes

Compare acceptance rate of just-completed pool against the baseline from earlier pools.
>15 pp delta triggers audit. Catches systematic shift in model behavior.

### Additional measures for long campaigns

- **Output schema validation:** Every atomic save validates JSON before mv. Corrupted
  or malformed output never enters the pipeline.
- **Atomic write pattern:** Write to `.tmp`, validate, then rename. Prevents corruption
  from watchdog restarts, OOM spikes, or any mid-write failure.
- **Retry cap:** Max 3 attempts per window (10k → 20k → 20k tokens). No unbounded retries.
  After 3, mark as SKIP with metadata marker — known gaps return later.

## 6. State at the time of writing

- Model: **loaded and healthy** on `:18081`, pid recorded in
  `~/ninfer-work/qwen_mode.txt`. `opencode.json` (repo) and
  `~/.config/opencode/opencode.jsonc` (global) both set to
  `ninfer-35b/qwen3.6-35b-a3b-ninfer`.
- **No window of this campaign has been verified yet.** Phase 1 has not started.
- The previous campaign's state is intact and resumable: `gold600/` = 333 of 600
  (`gold_000`–`gold_019` + `gold600.jsonl`, 1,298 events), and
  `gold600/gold_020.PARTIAL.md` holds the partial decisions for G333–G344.
