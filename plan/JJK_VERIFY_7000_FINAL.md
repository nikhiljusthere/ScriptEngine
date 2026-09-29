# RESUME PROMPT — JJK VERIFY-7000 INLINE WORKFLOW (FINAL)

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
- Phase 0: Blind audit sample (10 random windows across pools)
- Phase 1: pool A — ~1,500 opencode-session windows (3×500 main + 5×31 pilots)
- Phase 2: pool B — ~1,000 Qwen windows (already partially done, re-verify under stricter rules)
- Phase 3: rest of v1/train.jsonl (~4,375 total unique)
- Phase 4: the 2,265 `empty` windows (re-read for false negatives)

### Phase 0: Blind audit sample (RUN BEFORE PHASE 1)

Pick **10 random windows** across different pools. Mix of empty/dense, known-good/known-empty. Verify each inline under strict rules. Confirm:
- Model correctly rejects false positives under stricter rules
- It catches missed events on dense passages
- Output JSON format is consistent
- No empty-content failures

If >2 out of 10 fail under strict rules, fix the rules/budget/prompt before touching production data. This costs ~10 minutes and prevents cascading uniform errors.

---

## 2. The model (already up — DO NOT restart it)

```
Qwen3.6-35B-A3B groupwise-int, NInfer on http://127.0.0.1:18081/v1
Model ID: qwen3.6-35b-a3b-ninfer   (with "-ninfer" suffix)
Context: 262,144   KV pool: 524,288 tokens int8   MTP3 drafting
```

Verify before start:
```bash
curl -sf -m 10 http://127.0.0.1:18081/health
```
Expect: `{"status":"ok"}`

If down: relaunch `tools/train/ops/serve_35b.sh`.

**CRITICAL:** The model name is set by `--model-id` in `serve_35b.sh`. Do NOT change it. If you see `model_not_found`, the server name does not match your request.

---

## 2.1. Live progress monitor

Run `tools/train/verify_monitor.py` in a separate terminal or backgrounded:
```bash
python3 tools/train/verify_monitor.py --port 8950
```

Open `http://127.0.0.1:8950` in Brave. It shows per-pool progress bars, overall %,
v1 tier breakdowns, server health, and **EWMA alert indicator** (see §6). Auto-refreshes every 2 seconds.

---

## 3. One-window process (do this for EVERY window)

```
WINDOW N = __UPDATE__
WFILE = series/jjk/training/opencode/mimoP1_windows.jsonl  ← update per pool
OFILE = series/jjk/training/opencode/mimoP1_out.jsonl     ← update per pool
DONE_LOG = series/jjk/training/opencode/.mimoP1_done      ← update per pool
IS_PROBE = false   ← set true for golden probe inserts
```

### Step 1: Check if this is a golden probe

Before processing, check: did the previous window set `IS_PROBE=true`? If so, load 2 golden probes from `series/jjk/training/golden_probes.jsonl` instead of the regular WFILE. Golden probes use the same format as production windows but carry `"__is_probe": true` in their output.

### Step 2: Load the window

Read the window from WFILE (or golden_probes.jsonl for probes). Extract n, id, page, section, passage.

### Step 3: Wiki card lookup (if draft events exist)

For EACH row in existing drafts:
```bash
scriptengine/.venv/bin/python tools/train/wiki_card.py "Subject" "verb" "Object"
```
(For `awakened`, pass `""` as object.) Run for subject AND object. Capture resolution info.

### Step 4: Verify each row under strict rules

Ask these questions in order:
1. Does the passage STATE the event happened? (Not plan, attempt, hypothetical, false claim, negation.)
2. Is the verb right under the guideline table including its "no" column?
3. Is direction right? Subject is the doer. Passive voice: doer follows "by". "Y lost to X" → X defeated Y.
4. Are both ends named entities the guideline allows? Never species, class, technique, domain, item, groups/institutions. Named shikigami exception: Nue, Mahoraga, Max Elephant, Rika, Moon Dregs. Pronouns only if unambiguous.
5. Not a duplicate: `fought` and `met` are symmetric — one row per pair.

### Step 5: Missed-event pass

Re-read the whole passage once more, looking ONLY for events the drafts did NOT list. Add them with Steps 3–4 applied.

### Step 6: Write with atomic save + logging

```bash
# 1. Write to .tmp first
echo '<complete json>' > /tmp/jjk100/mimoP1_out.jsonl.tmp

# 2. Validate parses
python3 -c "import json; json.loads(open('/tmp/jjk100/mimoP1_out.jsonl.tmp').read())" && echo OK || echo INVALID

# 3. If valid, atomic rename overwrites the real file
mv /tmp/jjk100/mimoP1_out.jsonl.tmp series/jjk/training/opencode/mimoP1_out.jsonl

# 4. Log completion for crash recovery
echo "$N $ID" >> series/jjk/training/opencode/.mimoP1_done

# 5. Log rule citation for drift monitoring
LAST_RULE=$(python3 -c "import json; d=json.loads(open('series/jjk/training/opencode/mimoP1_out.jsonl').read()); print([r.get('rule','') for r in d.get('events',[])])")
echo "$N $LAST_RULE" >> series/jjk/training/opencode/.mimoP1_rules_log
```

The `.done` log is your post-crash recovery mechanism. After a watchdog restart, read the last line and start from the next window. The `.rules_log` feeds drift detection (Guard 5).

### Step 7: Increment counter

If regular window: increment `n` and go to next WFILE line. If golden probe (after 2 probes processed): reset IS_PROBE=false, load next production window.

---

## 4. The rules — base law

Read NOW:
```bash
cat plan/EVENT_ANNOTATION_GUIDELINE.md
```

### §5a precedents (handoff `plan/JJK_OPENCODE_HANDOFF_2026-09-29.md`)

Six precedents confirmed against built gold:
1. Landing on opponent = `met` ONLY when landing STARTS encounter.
2. "Restrained X and forced them to release" = `captured`.
3. "Returned to X" = `arrived` when X is a named place.
4. A school = named place for `arrived`.
5. In-person "told X" = `met`. Phone/device call stays not-met.
6. One `met` per pair per meeting, even across different windows.

When two verbs fit, take the MORE SPECIFIC (`killed` > `defeated` > `fought`).

---

## 5. Stricter rules

1. **Default `no`.** Affirmatively proven by passage text.
2. **Quote ≥ 12 characters, verbatim.** Never repair spelling.
3. **Both ends resolve to correct wiki entity** (use `wiki_card.py`).
4. **`killed` needs stated death**; wiki Alive status confirms unless passage itself states death.
5. **No class/species/technique/domain/item as end.** Shikigami exceptions only.
6. **One row per pair for `fought` and `met`.** Symmetric.
7. **Ambiguity → `no` or the more specific verb.**
8. **Keep every rejected row with one-sentence `rule`.** Audit trail sacred.
9. **Missed-event pass on EVERY window.** Catch under-generation.
10. **`[]` verdict must be earned.** Name why in `rule` field.

**Constraint that matters most: wiki card NEVER decides.** It catches errors; passage creates truth.

---

## 6. Full drift prevention system

Applied from Drift-prevention council (9cf30cc3). Five guards working together:

### Guard 1: Disguised golden probes (every 200 windows)

After every 100 completed windows, load 2 probes from `golden_probes.jsonl` next. They arrive identically to production windows. Mark `"__is_probe": true` in output. Any probe failure triggers **immediate action**:

**Remediation protocol:** (a) Trigger Ruling Card refresh (§6.5), (b) Reload last 20 verified windows from `.done` checkpoint, (c) Re-verify those 20 inline with fresh context, (d) If ≥1 still disagrees → flush and restart the block from checkpoint.

Cost: ~2 API calls per 200 windows (~1% overhead).

### Guard 2: EWMA acceptance-rate chart

Track per-100-window acceptance rate on a rolling 200-window EWMA (alpha=0.1). When EWMA drops >2pp from the initial baseline, trigger an alert on the monitor dashboard. The monitor already counts done lines; add acceptance-rate tracking to the HTML generation.

Baseline is established after the first 100 windows. Set SCRIPTENGINE_ANSWER_TOKENS=20480 to match the server's budget.

### Guard 3: Ruling Card refresh every 50 windows

Paste the anchor block below into your context at each batch boundary. Resets attention before repetition fatigue.

### Guard 4: Duplicate check every 200 windows

Take the last 10 verified results from `.done` log, fetch them again from input files, verify inline. Compare: same verdict? Same reasoning? If >2 disagree → re-read ALL guidelines and precedents before continuing.

### Guard 5: Rule-citation distribution monitoring

Every window logs which guideline concepts appear in the `rule:` field (via `.rules_log`). Over time, plot a histogram of citations. If citations shift away from stricter sub-rules, the model is relaxing standards even if acceptance rate looks stable. Simple Python script reads `.rules_log` and plots — run weekly.

### Guard 6: Thematic consistency gate

Group accepted events by narrative domain (Shibuya Incident, Culling Game, character relationships, etc.). Track acceptance rate per domain. Sudden collapse in one domain = corpus-region issue, not global drift. Cheaper fix: expand entity set for that domain rather than re-running the whole pipeline.

### Answer budget trap + retry protocol

Max **3 attempts per window**:
- Attempt 1: 10,000 tokens
- Attempt 2: 20,480 tokens  
- Attempt 3: 20,480 tokens
- Attempt 4: **SKIP** — mark `"verdict": "none", "rule": "skip: max_retries_exceeded"`. Add ID to `.skipped` log.

Unbounded retries drain the concurrency queue. Even 5% stubborn rate = 200 zombie sessions.

---

## 6.5. ANCHOR — Ruling Card (paste every 50 windows)

```
=== VERIFICATION RULES — REFRESH ===
Base law: EVENT_ANNOTATION_GUIDELINE.md sections A-E. Stricter rules 1-10.
§5a precedents 1-6 (handoff doc).
KEY CONSTRAINTS:
- Default NO. Row must be affirmatively proven by passage text.
- Wiki card NEVER creates/confirms rows. Only catches errors.
- If passage also states fight AND specific verb → BOTH correct.
- No class/species/item as end (shikigami exceptions only).
- Keep ALL rejected rows with one-sentence rule reason.
- Missed-event pass on EVERY window mandatory.
- Empty list [] verdict must be earned, name why in rule field.
- Quote >= 12 chars, verbatim, wiki typos kept.
- fights/met are SYMMETRIC — one row per pair.
=== END RULES ===
```

---

## 7. Setup required before starting

### 7.1 Create golden probes file

Extract 20–30 pre-adjudicated windows from `gold600.jsonl` covering:
- Easy: clear-cut battles, obvious captures
- Medium: ambiguous directions, subtle verb distinctions
- Hard: implied events, indirect descriptions, passive constructions
- Edge cases: from the six §5a precedents

Format identical to production windows (one JSON line each). File: `series/jjk/training/golden_probes.jsonl`.

Example line:
```json
{"n": 0, "id": "4162d0150e7268c4", "page": "Satoru Gojo vs. Sukuna", "section": "", "passage": "..."}
```

### 7.2 Update monitor dashboard (optional but recommended)

Edit `tools/train/verify_monitor.py` to compute rolling EWMA of per-window acceptance rate and display an alert indicator. Basic approach: read the last 200 `out.jsonl` entries, count accepted rows, plot rolling average with baseline band.

### 7.3 Rule-citation monitoring script (post-first-pool)

After completing first pool, run a simple Python script reading `.rules_log`:
```bash
python3 << 'EOF'
from collections import Counter
counts = Counter()
for line in open("series/jjk/training/opencode/.mimoP1_rules_log"):
    parts = line.strip().split(None, 1)
    if len(parts) == 2:
        # Count keywords in rule text
        for word in ["affirmed", "proven", "unrefuted", "wiki", "class", "species", "ambiguous", "duplicate", "symmetric"]:
            if word in parts[1].lower():
                counts[word] += 1
for k, v in counts.most_common():
    print(f"{k}: {v}")
EOF
```

---

## 8. Operational traps (read carefully)

- **pgrep/pkill kills my shell twice.** Pattern appears in own `/bin/bash -c` command line. Kill by EXACT PID using `ps -eo pid,comm,args --no-headers | awk` with comm + anchored args match.
- **Switch models away from 35B: kill watchdog FIRST, then server by exact PID.** Otherwise watchdog restarts and collides.
- **Do NOT train on test-v4 ids** or anything not adjudicated.
- **Five `D series/*/overrides.yaml` in git status are SYMLINK ARTIFACTS.** Byte-identical to HEAD. Never commit those deletions.
- **Artifact is NInfer v3** (`build35/` binary only). Old `build/` rejects it.
- **Don't run multiple models on card together.** 32 GB limits to one resident model per Engine.
- **Empty reply ≠ rejection** in verifiers — parse raises, row stays "unanswered", third state downstream that `build_trainset.py` refuses.
- **`.env` loads into process environment** (`config.py` calls `load_dotenv`). `SCRIPTENGINE_ANSWER_TOKENS=20480` works. Explicit env overrides `.env`.

---

## 9. Where the data lives

| File | Purpose |
|------|---------|
| `series/jjk/training/opencode/mimoP*_windows.jsonl` | Input passages (one line/window, 500 each) |
| `series/jjk/training/opencode/mimoP*_out.jsonl` | Output (append-only, overwrite as you go) |
| `series/jjk/training/opencode/NEMOTRON_OUT.jsonl` | nemotron version |
| `series/jjk/training/opencode/SPACEBUNNY_OUT.jsonl` | spacebunny version |
| `series/jjk/training/gold/cand_q6_train.jsonl` | Qwen pool (next phase) |
| `series/jjk/training/v1/train.jsonl` | Full corpus (phase 3+) |
| `series/jjk/training/golden_probes.jsonl` | Golden probes (20-30 pre-certified windows) |
| `series/jjk/training/gold600/gold600.jsonl` | Existing gold standard (extract probes from here) |

Pilot batches (5×31): `mimoP1` through `mimoP5` — partially processed.  
Main batch (500 each): `mimo_out.jsonl` → `nemotron_out.jsonl` → `spacebunny_out.jsonl`

---

## 10. Start now

1. **Confirm** health: `curl -sf -m 10 http://127.0.0.1:18081/health` → `{"status":"ok"}`
2. **Read** `plan/EVENT_ANNOTATION_GUIDELINE.md` sections A–E
3. **Read** handoff `plan/JJK_OPENCODE_HANDOFF_2026-09-29.md` section §5a (precedents)
4. **Create** `golden_probes.jsonl` from existing `gold600.jsonl` (step 7.1 above)
5. **Run Phase 0 blind audit:** 10 random windows across pools. If >2 fail strict rules → fix before proceeding.
6. **Start production:** Follow Steps 1–7 above for each window. After every 50 windows, paste the Ruling Card (§6.5). After every 100 windows, insert 2 golden probes. After every 200 windows, re-verify 10 past results.

Current saved git commits for context:
- `9cf30cc3` — drift-prevention council verdict
- `9de61f6c` — council patches applied (atomic save, retry cap, blind audit)
- `fb27347a` — answer-budget trap
- `a83a90e8` — model name alignment
