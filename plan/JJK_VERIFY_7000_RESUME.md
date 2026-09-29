# RESUME PROMPT — JJK VERIFY-7000, phase 1

Paste everything below into a new opencode session. It is self-contained: a
fresh agent that has never seen this conversation can run the campaign from it.

---

## 1. What you are doing

Verify **every** JJK training window under **stricter** rules, using the new
Qwen3.6-35B-A3B as the verification engine. The plan of record is
`plan/JJK_VERIFY_7000.md` — read it, but this prompt is the brief and it wins
where they differ.

**Order (the owner set this):**

1. **Phase 1 — the 1,500 opencode-session windows.** Do these first. They are the
   least-examined data in the repo: drafted by free sessions
   (`spacebunny`, `mimo`, `nemotron`), never adjudicated, and the most
   event-dense of any pool (spacebunny 842 events / 500 windows), so they are the
   most likely to over-generate.
2. **Phase 2 — the ~1,000 Qwen windows** (`gold/cand_q6_pilot400.jsonl` 400 +
   `gold/cand_q6_train.jsonl` 600). `gold600/` already holds 333 adjudicated;
   continue from index 333 **and re-verify the 333 already done** under the
   stricter rules rather than trusting the earlier pass.
3. **Phase 3 — import the rest of `v1/train.jsonl`.** These are the windows pools 1
   and 2 never covered. Check whether `stage2_extra.jsonl` / `stage1_extra.jsonl`
   already cover part of this before re-extracting.
4. **Phase 4 — the 2,265 `empty` windows.** Re-read for false negatives. A
   separate pass, because an empty list looks finished and is never audited.

**The count is 4,375 windows, not 7,000.** The pools overlap: 2,455 of the 2,500
drafted windows are already inside `v1/train.jsonl`. The owner was told this and
has not objected. If they insist on 7,000, build the manifest to their spec — but
do not pad a manifest to hit a number on your own.

**Only 343 of 4,375 (7.8%) are `confirmed`.** Everything else is `contested`
(1,534 / 7,274 events), `empty` (2,265) or `unverified` (233). This is why the
campaign exists.

## 2. The model (already up — do not restart it)

```
Qwen3.6-35B-A3B groupwise-int, NInfer, http://127.0.0.1:18081/v1
served model id : qwen3.6-35b-a3b-ninfer
context         : 262,144      KV pool: 524,288 tokens, int8
serve script    : tools/train/ops/serve_35b.sh
watchdog        : tools/train/ops/ninfer35_watchdog.sh
```

Check it before you start: `curl -sf -m 10 http://127.0.0.1:18081/health`
(expect `{"status":"ok"}`). If it is down the watchdog restarts it; otherwise
relaunch `serve_35b.sh`.

**Measured, for planning your throughput:** 954 tok/s aggregate decode and
7,219 tok/s aggregate prefill at 2 lanes. 20.6 GiB of weights load in ~27 s.

**One name, four places.** The model name is set by `--model-id` in
`serve_35b.sh` and must be **copied, never retyped**, into: both
`opencode.json` files, `.env` (`SCRIPTENGINE_LLM_MODEL`,
`SCRIPTENGINE_WRITER_MODEL`), and the `--model` default in the four tools under
`tools/train/`. NInfer serves exactly one name; a mismatch is an instant
`model_not_found`. This already cost one restart.

## 3. The method — this was decided, do not re-litigate

**Direct LLM calls for the row verdicts. Inline judgment for the missed-event
pass and for genuinely ambiguous rows. A 5% blind audit before the full run.**

Why: `verify_row_wiki.py` already calls the model **once per row**, each with a
fresh context holding only the passage, that row, its siblings, and a wiki card
read straight from SQLite. That structure is the quality argument — it makes
rule drift at row 6,000 and "this looks like the row I approved earlier"
structurally impossible, and an inline session carries exactly that accumulated
state as noise. The tooling is also already built and has run over 1,000+
windows. Pool 1 is only ~1,764 rows total: under 2 hours at this speed, versus
6,000+ judgment cycles that would not fit in any one context.

Where inline genuinely wins, and where you should spend your own attention:

- **The missed-event pass.** Under-detection leaves no bad row for the mechanical
  gate to catch. This needs a fresh reading of the passage.
- **Ambiguous rows** — where the guideline and §5/§5a do not settle it.

**Run the tools with `--workers 2`.** That matches `--max-concurrency 2`; a third
worker only queues.

```bash
G=series/jjk/training/gold; T=series/jjk/training/v1/train.jsonl
PY=scriptengine/.venv/bin/python
$PY tools/train/verify_row_wiki.py --series jjk --data $T \
  --cand $G/cand_q6_train.jsonl --out <out>.jsonl --workers 2
```

Defaults are already correct (`:18081`, `qwen3.6-35b-a3b-ninfer`). It resumes by
itself: a window counts as done only when its line has `ok: true`.

## 4. The rules

The base law is unchanged and still binding:

- `plan/EVENT_ANNOTATION_GUIDELINE.md` sections A–E
- `plan/JJK_OPENCODE_HANDOFF_2026-09-29.md` **§5 and §5a**

**§5a holds six precedents confirmed against the built gold — read it before
adjudicating anything.** They are not in §5 and they are not obvious: a landing
on an opponent is `met` only when it *starts* the encounter; "restrained X and
forced them to release" is `captured`; "returned to X" is `arrived`; a school is a
named place; in-person "told X" is `met`; and one `met` per pair per meeting even
across different windows.

Stricter, on top of that:

1. **A row must be affirmatively proven.** Default `no`. "Not ruled out" is not
   evidence.
2. **Quote ≥ 12 characters, copied character for character, wiki typos kept.**
   Never repair spelling.
3. **Both ends must resolve to the right wiki entity**, checked per row. Not
   inferred from the passage alone.
4. **A `killed` row needs a stated death**, and the wiki must not contradict it
   (an object listed Alive is wrong unless the passage states the death).
5. **No class, species, technique, domain or item as an end.** Named shikigami
   (Nue, Mahoraga, Max Elephant, Rika, Moon Dregs) are the exception. Groups and
   institutions are never ends.
6. **One row per pair for `fought` and `met`** — they are symmetric. Never both
   directions.
7. **Ambiguity resolves to `no`, or to the more specific verb**
   (`killed` > `defeated` > `fought`). If the passage also states the fight, both
   `fought` and `killed` are correct.
8. **Keep every "no" row, with a one-sentence `rule`** naming the check that
   decided it. Rejected rows are the audit trail.
9. **Missed-event pass on every window.** Re-read once more for events not
   listed. This is the step most often skipped and the one that catches
   under-generation.
10. **A `[]` verdict must be earned**, and must say why in `rule`.

**The constraint that matters most: the wiki card flags, it never decides.** It
can catch that an end is a technique page or that a `killed` object is listed
Alive, but it can never make a row correct. **The passage decides.** Never let a
wiki card add or confirm a row (handoff §6).

## 5. Traps — each of these has already bitten, once

- **Empty content is not a verdict.** This model reasons by default and will
  spend a small budget entirely on reasoning and return empty content with
  `finish_reason: length`. Measured: a one-sentence question came back empty at
  2,048 tokens (1,142 spent on reasoning) and correct at 20,480. In the
  verifiers an empty reply leaves the row `None` ("unanswered"), a genuine third
  state that `build_trainset.py` refuses to train on — so it is already safe.
  **But any wrapper you write must treat empty as retry-at-higher-budget, never
  as "no events".** A wrapper that reads empty as an empty event list
  manufactures thousands of false negatives.
- **`.env` now loads into the process environment** (`load_dotenv` in
  `scriptengine/config.py`). It did not before, so the three `_answer_budget`
  helpers were silently using their hardcoded defaults. `SCRIPTENGINE_ANSWER_TOKENS`
  is 20,480. If you ever see 8,192, that is the bug returning.
- **`pgrep -f` / `pkill -f` will match your own shell.** The pattern text appears
  in your `/bin/bash -c` command line, so `kill -9` on the result kills the
  controlling shell — it happened twice this session. Use
  `ps -eo pid,comm,args` and match on `comm` plus an anchored args prefix, and
  kill by **exact PID**.
- **To switch models away from the 35B:** kill the **watchdog first**, then the
  server by exact PID. Otherwise the watchdog restarts the server and it collides
  with the new load.
- **Never run ninfer and another model on the card together.** One resident model
  per Engine; 32 GB is not enough for two.
- **Do not train on test-v4 ids** (`recall_gold_v3/gold_test_v4.json`), and do not
  train on anything not adjudicated.
- **The artifact is NInfer format v3** (magic `NINFER\0\x03`). Only
  `ninfer/build35/` loads it; `ninfer/build/` rejects it. Do not "fix" a load
  failure by pointing at the old binary.
- **`git status` shows five `D series/*/overrides.yaml`.** They are a symlink
  artefact (those series dirs point at the offload volume), all byte-identical to
  HEAD. Never commit those deletions.

## 6. The stop rule

**Run the 5% blind audit before the full run.** Take 75 windows at random, judge
them yourself without looking at the tool's answers, then compare.

- **Disagreement ≤ ~3%** → proceed with the full pool.
- **Above that** → fix the *rules or the prompt*, not the window count. Report to
  the owner rather than grinding.

One caveat to carry honestly: this is a 3B-active MoE, so on pure judgment it may
be weaker than the 27B-Q6 that produced `gold600.jsonl`. The speed is proven; the
judgment quality is not. The blind audit is what turns "I think it's fine" into a
number — that is why it goes first.

## 7. First actions, in order

1. `curl -sf -m 10 http://127.0.0.1:18081/health`
2. Read `plan/JJK_VERIFY_7000.md` §3 (the ten rules) and
   `plan/JJK_OPENCODE_HANDOFF_2026-09-29.md` **§5a**.
3. Build the Phase-1 id list: the union of
   `series/jjk/training/opencode/{mimo,nemotron,spacebunny}_out.jsonl` (1,500
   unique ids; dedupe — 45 overlap the Qwen pool).
4. Run `verify_row_wiki.py` on ~75 of them (`--workers 2`) as the blind-audit
   sample.
5. Judge those 75 yourself, blind. **Report the disagreement rate to the owner
   before going further.**

Prior state, so you know what is not lost: `gold600/` = 333 of 600
(`gold_000`–`gold_019` + `gold600.jsonl`, 333 windows / 1,298 events), and
`gold600/gold_020.PARTIAL.md` holds four settled decisions for G333–G344.
Commits: `a83a90e8` (model name + endpoints), `2b5124a7` (serve + campaign plan),
`fb27347a` (answer-budget trap), `9fe709d7` (events v2).
