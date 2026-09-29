# RESUME PROMPT — JJK VERIFY-7000 INLINE WORKFLOW

Paste everything below into a new opencode session. It is fully self-contained.

---

## 1. What you are doing

Manual, inline verification of **every** JJK training window — **one at a time**.
No background LLM calls, no auto-verifiers, no batch scripts. You read the
passage, fetch every related wiki page, confirm every fact under strict rules,
save one validated line, then move to the next.

This method produced `gold600.jsonl`. It is correct for quality, slower for
wall-clock, and exactly what the owner ordered.

**Order:**
- Phase 1: pool A — ~1,500 opencode-session windows (3×500 main + 5×31 pilots)
- Phase 2: pool B — ~1,000 Qwen windows (already partially done)
- Phase 3: rest of v1/train.jsonl
- Phase 4: the 2,265 `empty` windows (re-read for false negatives)

Currently in **Phase 1**, starting with mimoP1 pilot batch.
**Progress: n=0 through n=344 are empty/verified. n=345 just completed (2 rows pass).**
Next window: **n=346** in `series/jjk/training/opencode/mimoP1_windows.jsonl`.

Write results to `series/jjk/training/opencode/mimoP1_out.jsonl` (append-only, overwrite lines as you go).

---

## 2. The model (already up — DO NOT restart it)

```
Qwen3.6-35B-A3B groupwise-int, NInfer on http://127.0.0.1:18081/v1
Model ID: qwen3.6-35b-a3b-ninfer   (with "-ninfer" suffix)
Context: 262,144   KV pool: 524,288 tokens int8   MTP3 drafting
Server PID: 530718   Watchdog PID: 531020
```

Verify before start:
```bash
curl -sf -m 10 http://127.0.0.1:18081/health
```
Expect: `{"status":"ok"}`

If down: relaunch `tools/train/ops/serve_35b.sh`.

**CRITICAL:** The model name is set by `--model-id` in `serve_35b.sh`. Do NOT change it.
Every config surface (both opencode.json files, `.env`, four training tools) uses
this exact name. If you see `model_not_found`, the server name does not match your request.

---

## 2.1. Live progress monitor (optional but recommended)

Run `tools/train/verify_monitor.py` in a **separate terminal or backgrounded**:
```bash
python3 tools/train/verify_monitor.py --port 8950
```

Then open `http://127.0.0.1:8950` in any browser (Brave). It auto-refreshes every
2 seconds, showing per-pool progress bars, overall %, v1 tier breakdowns, and
server health. This lets you watch verification progress in real time without
switching from your work session. Stop it with Ctrl+C when done.

---

## 3. One-window process (do this for EVERY window)

```
WINDOW N = 346  ← update for each step
WFILE = series/jjk/training/opencode/mimoP1_windows.jsonl
OFILE = series/jjk/training/opencode/mimoP1_out.jsonl
```

**Step 1: Load the window.** Read line from WFILE matching the current `n`.

**Step 2: If there are draft events** in OFILE matching this `n`:
  - For EACH row, run the wiki card lookup:
    ```bash
    scriptengine/.venv/bin/python tools/train/wiki_card.py "Subject" "verb" "Object"
    ```
    (For `awakened`, pass `""` as object.)
  - Run `wiki_card.py` for subject AND object of every row. Capture the first two
    lines of output (resolution info).

**Step 3: Verify each row under strict rules.** Ask yourself these questions in order:
  1. Does the passage STATE the event happened? (Not plan, attempt, hypothetical, claim that turns out false, negation.)
  2. Is the verb right under the guideline table including its "no" column?
  3. Is direction right? Subject is the doer. Passive voice: doer follows "by".
     "Y lost to X" → X defeated Y.
  4. Are both ends named entities the guideline allows? Never species, class, technique, domain, item, groups/institutions. Named shikigami exception: Nue, Mahoraga, Max Elephant, Rika, Moon Dregs. Pronouns only if unambiguous.
  5. Not a duplicate: `fought` and `met` are symmetric — one row per pair.

**Step 4: Missed-event pass.** Re-read the whole passage once more, looking ONLY for
events the drafts did NOT list. Add them (with Steps 2–3 applied).

**Step 5: Write the line.** Append/overwrite to OFILE:
```json
{"n": 346, "id": "...", "page": "...", "section": "...",
 "passage": "...",
 "events": [
   {"quote": "...", "subject": "...", "verb": "...", "object": "... or null",
    "wiki": "from wiki_card.py output",
    "verdict": "yes" or "no",
    "rule": "one short sentence naming the rule that decided"}]}}
```
A window with no events: `{"n": 346, "id": "...", "page": "...", "section": "...",
 "passage": "...", "events": []}`

**Step 6: Save and advance.** Confirm the write went through, increment `n`, repeat.

---

## 4. The rules — base law

`plan/EVENT_ANNOTATION_GUIDELINE.md` sections A–E. Read it NOW:
```bash
cat plan/EVENT_ANNOTATION_GUIDELINE.md
```

### §5a precedents (handoff `plan/JJK_OPENCODE_HANDOFF_2026-09-29.md`)
**READ THESE BEFORE ADJUDICATING.** Six precedents confirmed against built gold:

1. **Landing on opponent = `met` ONLY when landing STARTS encounter.** Landing mid-battle is re-encounter → not `met`.
2. **"Restrained X and forced them to release" = `captured`.**
3. **"Returned to X" = `arrived`** when X is a named place.
4. **A school = named place** for `arrived`.
5. **In-person "told X" = `met`.** Phone/device call stays not-met.
6. **One `met` per pair per meeting,** even across different windows.

When two verbs fit, take the MORE SPECIFIC (`killed` > `defeated` > `fought`).
If passage also states the fight, BOTH are correct.

---

## 5. Stricter rules (on top of base law)

1. **Default `no`.** A row must be affirmatively proven, not merely unrefuted.
2. **Quote ≥ 12 characters, verbatim, wiki typos kept.** Never repair spelling.
3. **Both ends resolve to correct wiki entity** (use `wiki_card.py`).
4. **`killed` needs stated death**; wiki Alive status confirms unless passage itself states death.
5. **No class/species/technique/domain/item as end.** Exceptions: named shikigami (Nue, Mahoraga, Max Elephant, Rika, Moon Dregs).
6. **One row per pair for `fought` and `met`.** Symmetric — never both directions.
7. **Ambiguity → `no` or the more specific verb.**
8. **Keep every rejected row with one-sentence `rule`.** Audit trail is sacred.
9. **Missed-event pass on EVERY window.** Catch under-generation.
10. **`[]` verdict must be earned.** Name why in `rule`.

**The constraint that matters most: wiki card flags, it NEVER decides.** It catches errors; the passage creates the truth. Never let wiki evidence create or confirm a row.

---

## 6. Answer budget trap

This model reasons by default and spends small budgets entirely on reasoning, returning **empty content with `finish_reason: length`**. Measured: a one-sentence question returned empty at 2,048 tokens (1,142 spent on reasoning) and correct at 20,480.

**Any wrapper must treat empty as retry-at-higher-budget, never as verdict.** In the verifiers, retries escalate budget automatically. If writing new code, use 20,480 min. **Raise it, never lower it.**

---

## 7. Operational traps (read carefully)

- **pgrep/pkill kills my shell twice.** The pattern text appears in my own `/bin/bash -c` command line. Kill by EXACT PID only, using `ps -eo pid,comm,args --no-headers | awk` with comm + anchored args match.
- **To switch models away from 35B: kill watchdog FIRST, then server by exact PID.** Otherwise the watchdog restarts and collides.
- **Do NOT train on test-v4 ids** (`recall_gold_v3/gold_test_v4.json`) or anything not adjudicated.
- **Five `D series/*/overrides.yaml` in git status are SYMLINK ARTIFACTS.** Those series dirs point at the offload volume — byte-identical to HEAD. Never commit those deletions.
- **Artifact is NInfer v3** (`build35/` binary only). Old `build/` rejects it.
- **Don't run multiple models on card together.** 32 GB limits to one resident model per Engine.
- **Empty reply ≠ rejection** in verifiers — parse raises, row stays `None` ("unanswered"), third state downstream that `build_trainset.py` refuses to train on.
- **`.env` loads into process environment** (`config.py` calls `load_dotenv`). `SCRIPTENGINE_ANSWER_TOKENS=20480` works. Explicit env overrides `.env`.

---

## 8. Where the data lives

| File | Purpose |
|------|---------|
| `series/jjk/training/opencode/mimoP*_windows.jsonl` | Input passages (one line/window, 500 each) |
| `series/jjk/training/opencode/mimoP*_out.jsonl` | Output (append-only, overwrite as you go) |
| `series/jjk/training/opencode/NEMOTRON_OUT.jsonl` | nemotron version |
| `series/jjk/training/opencode/SPACEBUNNY_OUT.jsonl` | spacebunny version |
| `series/jjk/training/gold/cand_q6_train.jsonl` | Qwen pool (next phase) |
| `series/jjk/training/v1/train.jsonl` | Full corpus (phase 3+) |

Pilot batches (5×31): `mimoP1` through `mimoP5` — already processed.  
Main batch (500 each): `mimo_out.jsonl` → `nemotron_out.jsonl` → `spacebunny_out.jsonl`

Progress tracking:
- Pilot done: n=0..344 (345 windows, mostly empty)
- Currently processing: `mimoP1` pilot at **n=346**
- After pilot completes, continue main mimo batch from highest `n` found in existing output

---

## 9. Start now

1. **Read** `plan/EVENT_ANNOTATION_GUIDELINE.md` sections A–E
2. **Read** handoff `plan/JJK_OPENCODE_HANDOFF_2026-09-29.md` section §5a (precedents)
3. **Confirm** health: `curl -sf -m 10 http://127.0.0.1:18081/health` → `{"status":"ok"}`
4. **Start** with Window n=346 in `mimoP1` (or whichever window comes after the last completed one). Process inline, one-at-a-time, following Steps 1–6 above. Save result. Advance.

Current saved git commits for context (these capture the full chain of ops):
- `a83a90e8` — model name alignment across all surfaces
- `80520b64` — resume prompt doc
- `fb27347a` — answer-budget trap
- `2b5124a7` — serve + campaign plan
