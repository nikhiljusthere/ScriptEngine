# Handoff to opencode: JJK verified event dataset → Granite student (2026-09-29, 23:10 IST)

Written by the Claude Code session that ran this work. It continues in opencode.
Read this whole file before touching anything. Background:

- `plan/JJK_STUDENT_TRAINING.md` §10 (runs table, learning curve, post-filter);
- `reports/jjk/COUNCIL_student_training_2026-09-29.md` (the council verdict this plan follows);
- `plan/EVENT_ANNOTATION_GUIDELINE.md` (the labeling law).

---

## 1. What we are doing and why

**Goal.** Train **Granite-4.2-3B** (LoRA) into a near-100%-precision **event extractor**. It will later run over **300k+ Marvel/MCU wiki pages**, where a 27B model is too slow.

An "event" is a row:

```
{quote, subject, verb, object}
```

- `verb` is one of 12: `fought, defeated, killed, met, saved, captured, escaped, betrayed, sealed, awakened, arrived, departed`.
- `quote` is copied verbatim from the passage.

**The owner's rule (non-negotiable).**

> "I want the data it trains on to be 100% correct and verified first … verify using reading wiki pages … Then only give the data to granite for training."

So every training window must be:

1. drafted by a model;
2. flagged row by row by the big Qwen checker, against the passage and the wiki's own data;
3. adjudicated passage-first by a reviewer (until now, Claude).

Only windows that pass all three become training data.

**Why this way.** The measured numbers:

| System | Test | Recall | Precision | Notes |
|---|---|---|---|---|
| Old teacher labels | v3 | 62.8% | 73.0% | too noisy to train on |
| Qwen 27B Q6 (extract, thinking on) | v3 | 77.2% | 77.1% | |
| Qwen 27B Q6 (extract, thinking on) | v4 | 81.5% | 92.1% | biased, see below |
| Granite, 400 gold windows (run D) | v4 | 54.9% | 57.9% | |
| Granite, 205 gold windows (run A) | v4 | 48.6% | 56.2% | |

- The v4 Q6 figure is biased: Q6 was v4's second annotator.
- Granite gained +7.8 recall from 205 → 400 windows. It is data-hungry, and ~80% recall is the realistic ceiling.
- Granite's errors are meaning errors. The deterministic post-filter (`tools/train/postfilter.py`) wrongly rejects 0 of 963 gold rows, but barely changes Granite's precision.
- The fix is more **verified** windows (target ~3,000), not filtering.

**Council design (adopted; do not redesign without the owner):**

1. Two independent drafts per window.
2. The Qwen row-by-row + wiki check (`verify_row_wiki.py`) acts as a **flagger only**. The wiki card may flag a row. It never adds or confirms one.
3. The reviewer adjudicates every window **passage-first**, and settles disputes from the passage alone.
4. A 5% blind re-check of finished windows.
5. Training:
   - LoRA r=64, lr 1e-4 cosine, effective batch 8, 3 epochs;
   - empty windows at their natural share (~43%);
   - rare-verb windows ×3 (`build_trainset.py` does this);
   - checkpoints at 1k / 2k / 3k windows, with a stop rule when a checkpoint stops improving.
6. Ship:
   - deterministic post-filter;
   - 2-of-3 self-consistency;
   - per-verb precision gates on a Marvel test set: ≥95% for killed/betrayed/captured, ≥90% for the others.

---

## 2. Model / GPU state right now: **switching to Q8**

| Item | State |
|---|---|
| Q6 GGUF (the old checker on `:8090`) | **deleted** (owner, to free space) |
| Uncensored NVFP4 / dspark models | **deleted** (owner). `ninfer-work/serve_uncensored_*.sh` and CLAUDE.md mentions of them are now stale. |
| **ninfer (base Qwen3.8-27B NVFP4)** | **running now** on `:18080`, 262k profile (`~/ninfer-work/qwen-switch.sh 262k`). This is what opencode talks to right now. |
| **Qwen3.8-27B Q8_0 GGUF** | **downloading** into `/mnt/PROJECTS/models/qwen3.8-27b-q8/` (29.05 GB; ~19 GB done at 23:08, ~30 MB/s). |

**About the download:**

- Script: `tools/train/ops/dl_q8.sh`. Log: `/tmp/jjk100/dl_q8.log`.
- It is finished when the log has a line starting with `DONE`, and `Qwen3.8-27B-Q8_0.gguf` exists in that folder.
- If it died, re-run the script: `hf_hub_download` resumes.

**Owner directive:** the Q8 model, with an **f16 KV cache** and a **65k (65536) context window**, replaces Q6 for everything from now on: extraction drafts, the row checker and the corrector.

### 2a. Switch procedure (do this once the download is DONE)

The card cannot hold ninfer and Q8 at the same time.

1. **Stop ninfer:** `~/ninfer-work/ninfer-stop.sh`. Confirm with `nvidia-smi` that only a few hundred MiB are in use.
   - opencode loses its model at this moment. That is why step 3 exists: opencode's model becomes the Q8 server itself.
2. **Start Q8** (llama.cpp, MTP speculative decoding, jinja chat template with thinking):

   ```bash
   NP=6 CTX=65536 setsid nohup /home/goblin/ScriptEngine/tools/train/ops/serve_q8.sh \
     > /tmp/jjk100/q8_server.log 2>&1 < /dev/null &
   ```

   Then poll `curl -s 127.0.0.1:8090/health` in a bounded loop (no bare `sleep`).
   - The server's KV cache is f16 by default. The script passes no `-ctk`/`-ctv`, which is exactly the owner's "f16 KV".
   - **Fit warning (measure it, don't assume).** Q8_0 weights are ~27.7 GiB. f16 KV at 65k is ~4 GiB: 16 full-attention layers × 4 KV heads × 256 head_dim × 2 × 2 bytes ≈ 64 KiB per token. Together that is ~33 GiB, which does not fit the 31.8 GiB card at `NGL=999`.
   - If the log shows a CUDA OOM, relaunch with partial offload: `NGL=60 NP=6 CTX=65536 …serve_q8.sh`. Lower NGL (58, 56 …) until it loads, then measure tok/s.
   - If partial offload is too slow (below ~15 tok/s decode), tell the owner. The alternative is `unsloth` **UD-Q8_K_XL**, which is ~28 GB and may also need offload.
   - **Do not** switch the KV cache to q8 without asking: the owner asked for f16.
   - Record the measured VRAM, NGL and decode tok/s in `plan/JJK_STUDENT_TRAINING.md` §10.
3. **Update `opencode.json` for Q8.** Edit both files:
   - repo `ScriptEngine/opencode.json`;
   - global `~/.config/opencode/opencode.jsonc`.

   Add this provider next to `ninfer-27b` (keep the ninfer entries; they are the fallback). Then set `"model": "llamacpp-q8/qwen3.8-27b-q8"`, and back up first (`cp opencode.json opencode.json.bak-pre-q8`):

   ```jsonc
   "llamacpp-q8": {
     "npm": "@ai-sdk/openai-compatible",
     "name": "llama.cpp Q8 (local :8090)",
     "options": { "baseURL": "http://127.0.0.1:8090/v1", "apiKey": "none" },
     "models": {
       "qwen3.8-27b-q8": {
         "name": "Qwen3.8-27B-Q8_0 (llama.cpp, f16 KV, 65k)",
         "id": "qwen3.8-27b-q8",
         "modalities": { "input": ["text"], "output": ["text"] },
         "limit": { "context": 65536, "output": 16384 }
       }
     }
   }
   ```

   - Restart opencode after the edit so it reads the new config.
   - Note: `qwen-switch.sh` rewrites `limit.context` of the **ninfer** entries only. It will not touch this one, but running it starts ninfer again, which would evict Q8. Don't run `qwen-switch.sh` while Q8 is the working model.
   - **Shared context:** `--kv-unified` means the 65k KV pool is shared by all `-np` slots, and opencode's own agent session is one of those consumers. Keep your agent context lean. Run the batch tools with `--workers 3–4` (not 6) while you are also chatting through the same server.
4. **Restart the watchdog.** The 5090 drives the display, so a long kernel can hit the CUDA "launch timed out" watchdog and kill the server (this happened on 2026-09-29). `-ub 512` in `serve_q8.sh` reduces the risk. The watchdog restarts the server with `NP=6 CTX=65536`.

   ```bash
   setsid nohup /home/goblin/ScriptEngine/tools/train/ops/q6_watchdog.sh \
     > /tmp/jjk100/watchdog.out 2>&1 < /dev/null &
   ```

   If you had to use `NGL=<n>`, add `NGL=<n>` to its relaunch line first.

GPU-only rule (CLAUDE.md): all model work runs on CUDA. Never set `SCRIPTENGINE_DEVICE=cpu` and never run the checker on CPU.

---

## 3. Where the data stands (exact counts, 23:10)

All paths are under `series/jjk/training/`. `v1/train.jsonl` is the window pool (export-shaped: `messages[1].content` holds `Passage:\n…`).

| Set | Windows | State |
|---|---|---|
| Pilot gold `gold/gold_pilot_all.jsonl` (= `gold_pilot.jsonl`) | 400 / 963 events | **DONE**: adjudicated, Q6 wiki-checked (0 failures), plus 14 fixes (`gold_zz_fix1.json`) |
| "600" set: Q6 drafts `gold/cand_q6_train.jsonl` + teacher rows | 600 | **333 / 600 reviewed** → `gold600/gold600.jsonl` (1,298 events, 0 problems). **Resume at index 333** of `gold/review600_order.json`. |
| `gold/verifyrow_600.jsonl` (wiki flags for the 600) | 600 | only **345 ok**. 255 failed in the server crash; **re-run with Q8** (§4 step 1). The review continued without those flags, which is allowed because the flags are advisory. |
| opencode drafts (Space Bunny, MiMo, Nemotron) `opencode/*_out.jsonl` → `gold/draft_{spacebunny,mimo,nemotron}.jsonl` | 3 × 500 | complete. Each set contains 15 hidden calibration windows (ids in `/mnt/PROJECTS/backups/jjk_100_20260929/opencode_calibration_ids.json`). |
| teacher drafts `gold/draft_teacher500.jsonl` | 500 | complete |
| Stage 1 corrector `gold/stage1_extra.jsonl` (`verify_rows.py` over the 2,000) | 2,000 | only **464 ok** (crash); **re-run with Q8** |
| Stage 2 merge `gold/stage2_extra.jsonl` → wiki flags `gold/verifyrow_extra.jsonl` | 464 / 286 ok | rebuild after stage 1 completes |
| Test gold `recall_gold_v4`: `recall_gold_v3/gold_test_v4.json` (100 windows, 173 core / 97 optional) | test only | **never train on these ids** (`recall_gold_v3/ids_100.json`) |

**Target:** 400 pilot + ~600 + ~2,000 extra ≈ **3,000 verified windows**.

---

## 4. Remaining work, in order

Run everything from `/home/goblin/ScriptEngine` with `scriptengine/.venv/bin/python` (`PY`). All batch tools resume by themselves: a window counts as done only when its line has `ok: true`, so failed windows are retried.

```bash
G=series/jjk/training/gold; T=series/jjk/training/v1/train.jsonl; PY=scriptengine/.venv/bin/python
```

1. **Re-run the failed wiki checks on the 600** (Q8 must be up):

   ```bash
   $PY tools/train/verify_row_wiki.py --data $T --cand $G/cand_q6_train.jsonl --ids $G/select_600.json \
     --out $G/verifyrow_600.jsonl --workers 4 > /tmp/jjk100/verifyrow_600.log 2>&1
   ```

   Readers use each id's **last** line. The tool writes JSON verdicts, one line per window, and prints progress every 25 windows.
2. **Re-run the overnight chain for the 2,000 extra windows.** This is stage 1 corrector → merge → wiki check:

   ```bash
   setsid nohup bash tools/train/ops/night_chain.sh > /tmp/jjk100/night_chain.out 2>&1 < /dev/null &
   ```

   - Status goes to `/tmp/jjk100/night_status`. It exits after one round, because the opencode count is already 1,500.
   - Set `--workers` in the script to 3–4 if you are chatting through the same server.
3. **Finish the passage-first review of the 600** (index 333 → 599), 12 windows at a time:

   ```bash
   $PY tools/train/gold_tools.py render --data $T --cand $G/cand_q6_train.jsonl --ids $G/review600_order.json \
     --verify $G/verifyrow_600.jsonl --start 333 --n 12 > /tmp/jjk100/r600_bNN.txt
   ```

   - The render lists each window's passage and its candidate rows `c0..cN`:
     - `[W]` = Q6 draft;
     - `[T]` = teacher;
     - `[WT]` = both;
     - `<<Q6 …>>` = the wiki checker's flag.
   - Write one adjudication file per batch: `series/jjk/training/gold600/gold_020.json`, `gold_021.json`, … (gold_000–019 exist):

     ```json
     {"<window id>": ["c0","c2", ["<verbatim quote>","Subject","verb","Object or null"]], "<id>": []}
     ```

     A string keeps that candidate. A 4-list adds a row the drafts missed. `[]` means the window has no events. Every window of the batch must appear.
   - Rebuild after each batch. It must print `problems: 0`, which checks that each quote is verbatim and the shape is valid:

     ```bash
     $PY tools/train/gold_tools.py build --data $T --cand $G/cand_q6_train.jsonl \
       --gold series/jjk/training/gold600 --glob 'gold_*.json' --out series/jjk/training/gold600/gold600.jsonl
     ```

4. **Review the 2,000 extra windows** the same way, once stage 2 + wiki flags exist:
   - render with `--cand $G/stage2_extra.jsonl --no-teacher --verify $G/verifyrow_extra.jsonl`;
   - write adjudications to a new folder, e.g. `series/jjk/training/gold_extra/`.
5. **Score the opencode models** on their 15 calibration windows each, to know which draft source is weakest:

   ```bash
   $PY tools/train/ops/calib_score.py
   ```

   The last partial check had Space Bunny at 55.6 recall / 62.5 precision on 10 windows.
6. **5% blind re-check.** Pick 5% of finished windows at random and re-adjudicate them without looking at your first answer. Report the disagreement rate. If it is above ~3%, re-review that batch.
7. **Build the train set, verified windows only:**

   ```bash
   $PY tools/train/build_trainset.py --verified $G/gold_pilot_all.jsonl series/jjk/training/gold600/gold600.jsonl \
     [gold_extra.jsonl] --out series/jjk/training/v2/train_verified.jsonl --rare-x 3
   ```

   It prints a receipt. Put that receipt in `JJK_STUDENT_TRAINING.md` §10.
8. **Train Granite.** Stop the Q8 server first so the card is free (restart it afterwards). Use the council recipe:

   ```bash
   M=/mnt/PROJECTS/hf_home/hub/models--ibm-granite--granite-4.2-3b/snapshots/e459acceac81e5fe67c07d9cfc72329a332e7eb1
   $PY tools/train/sft.py --model $M --train series/jjk/training/v2/train_verified.jsonl \
     --out /mnt/PROJECTS/models/granite-runs/E_1k --lr 1e-4 --epochs 3 --rank 64 --batch 4 --accum 2
   ```

   - Do this at ~1k, ~2k and ~3k verified windows (runs `E_1k`, `E_2k`, `E_3k`).
   - `sft.py`'s default lr is 2e-4, so **pass `--lr 1e-4`**. Its scheduler is already cosine.
9. **Evaluate each checkpoint** on test v4:

   ```bash
   $PY tools/train/infer.py --model $M --adapter /mnt/PROJECTS/models/granite-runs/E_1k \
     --data series/jjk/training/v1/test.jsonl --ids series/jjk/training/recall_gold_v3/ids_100.json \
     --out /tmp/jjk100/pred_E_1k.jsonl
   $PY tools/eval_extraction.py --gold-dir series/jjk/training/recall_gold_v3 --pred /tmp/jjk100/pred_E_1k.jsonl
   ```

   - `eval_extraction` picks the newest `gold_test_v*.json`, which is v4.
   - Then score again with the post-filter and with 2-of-3 self-consistency (three sampled runs; keep rows that appear in ≥2).
   - Compare against D_gold400: 54.9 recall / 57.9 precision.
   - **Stop rule:** if 2k → 3k adds less than ~2 points of F1, more data is not the lever. Report that to the owner rather than grinding.
10. **Report to the owner:** per-verb precision/recall, the learning curve (205 / 400 / 1k / 2k / 3k), and whether the ship gates are reachable. The Marvel test set does not exist yet; propose building it.

---

## 5. Adjudication rulings (apply them exactly; they are what gold_000–019 used)

The guideline's sections A–E are the law. These rulings resolve the cases it leaves open.

- **Evidence.**
  - The passage decides.
  - The wiki flag is a hint only.
  - Past events restated in the passage count ("even though Satoru Gojo killed him"; "his fight with Choso").
  - Narrated reports presented as true count ("Ranta informs them Maki has killed Ogi").
  - Claims, opinions and plans don't ("Yuji claims Sukuna saved Nanami"; "Kusakabe affirms Gojo has won"; "heads out to meet X"; "aligned with Kenjaku to seal Gojo").
  - "Anime & Manga Differences" windows: an event described for either medium counts.
- **Quotes** are verbatim, wiki typos included. Never "fix" spelling.
- **Ends.**
  - Named characters and named shikigami (Nue, Max Elephant, Mahoraga, Garuda) are allowed ends.
  - Never an end: groups, units and institutions (Kukuru Unit, Team Zenin, Jujutsu High, "curse users"); unnamed descriptors ("the head of New Shadow Style", "her father"); techniques, domains, items (Prison Realm is an item: its user is the subject).
  - An epithet that clearly names a character in the same passage uses the character's name ("the patch face curse" → Mahito).
  - **Mechamaru = Kokichi Muta**: one entity, keep one row.
  - A double or split-off copy is not the person ("Mahito's double", "the other Mahito").
  - Angel and Hana are kept as the passage names them.
- **fought** is symmetric: one row per pair.
  - A confrontation right before a fight may carry both `met` and `fought`.
  - Not fought: threats, spear into a blackboard, friendly or comedic kicks, force-feeding an unconscious person, breaking free of an attack aimed at someone else.
- **met** needs a stated face-to-face encounter: "meets", "confronts", "encounters", "happen upon", "reunite / regroup with", "X shows up", "arrives to back up" plus a named partner, "during a meeting with".
  - Not met: phone or device calls, orders, plans, conversation lines inside a meeting that began earlier, re-noticing someone mid-fight, "recalls".
  - In-person briefings and named meeting participants count.
- **defeated**: "knocks unconscious", "makes short work of", "eliminates" / "dispatch", "overpowers" at the end of an exchange, "incapacitating", "destroys the body" of a survivor, "leaving him bleeding and wounded" when the victor walks away.
  - Not when the loss is undone (Hakari's replay), when the fight simply continues, or for "throws the fight".
- **killed** needs a stated death: "death", "fatal blow", "killing", "exorcise".
  - A "seemingly exorcised" target that survives is not killed.
  - A shikigami "completely disintegrated" is killed.
- **sealed**: a stated trap inside a domain, projection frame, ice, coffin or Prison Realm. The one who commands the Prison Realm is the subject.
  - Not sealed: a ritual barrier for allies, a domain expansion with no stated trap, sealing a finger inside someone, unsealing.
- **captured**: restrained, pinned, immobilized (blood net on Nue, Mahoraga's arms immobilizing Gojo, "pins Nanami to the wall", "effortlessly restrained"), or held confined in a room.
- **saved**: rescue, freeing from a seal or domain, "healed" from near death, "stops X from killing Y".
  - Not saved: "spared", failed or only intended rescues.
- **escaped**: getting away from pursuers or a trap ("break out of the ice", "escapes into the sewers", "the two have already escaped", "withdraws / walks away from the fight").
  - Not escaped: dodging inside a fight.
- **awakened** (object null): return to life, reborn as a curse, incarnation into the true form, a first awakening of a technique or domain, a new power discovered mid-battle (Dabura's Reversal), a cursed womb evolving into a spirit.
  - Not awakened: waking from sleep, coma, trance or injuries.
- **arrived**: a *named* place with "enters", "arrives", "gets inside", "goes to see a movie at X", "takes Sukuna to Sendai … upon arrival", "reached the Shibuya Tower".
  - Not arrived: "heads to", or an unnamed place ("the station").
- **departed** needs a named place. Leaving a clan is not a place.
- **betrayed**: defecting from Geto's group to jujutsu society is accepted.
- **Duplicates**: when two candidates state the same pair and verb, keep the one with the better quote. The checker already drops symmetric twins mechanically.

### 5a. Addendum — precedents confirmed while adjudicating G333–G344 (2026-09-30)

Each was checked against a row already in `gold600.jsonl`, so it is a fact about
the built gold, not an opinion. Search there first, then rule.

- **Landing on an opponent is `met` ONLY when the landing starts the encounter.**
  Gold has `Yuka =met=> Dabura | "landing directly in front of Dabura"` — valid
  because that landing *marked the start of their battle*. A landing **in the
  middle of** an ongoing fight is the re-encounter case and is **not** `met`
  (this decided G337: Yuji landing on top of Sukuna mid-battle → no `met` row).
- **"restrained X and forced them to release" is `captured`.** Gold already has
  `Megumi =captured=> Kirara | "Megumi restrained Kirara and forced them to
  release"` from another window of the same fight-club scene, so keep the
  corrected row rather than downgrading it to `fought`.
- **"returned to X" is `arrived`** when X is a named place — gold has
  `Momo =arrived=> Kyoto`. The object is the place reached, not the person.
- **A school is a named place for `arrived`** — gold has
  `Noritoshi =arrived=> Tokyo College`.
- **Saying something to a person in person is `met`.** Gold has
  `Nanami =met=> Akari` and `Nanami =met=> Nobara` from a told-X line. A phone
  or device call stays not-`met` (unchanged).
- **One `met` per pair per meeting, even across windows.** Two different
  windows can describe the *same* meeting; when they do, the pair is met once
  (decided G341: `Noritoshi =met=> Yoshinobu Gakuganji`, the same pre-event
  meeting as window `365bed55`, which already carries that row).

---

## 6. Don'ts

- Don't train on anything not adjudicated (`build_trainset.py` refuses non-gold tiers; keep it that way).
- Don't train on test-v4 ids.
- Don't let the wiki card add or confirm rows. It only flags.
- Don't run ninfer and Q8 together. Don't run `qwen-switch.sh` while Q8 is the working model.
- Don't kill processes with broad `pkill -f` patterns: that killed the controlling shell before. Match exact PIDs.
- Don't edit a running bash script. Stop it, edit, relaunch.
- Don't commit unless the owner asks (the branch is `character-scoped-questions`, with lots of untracked work).
- Durable copies of every ops script are in `tools/train/ops/`: `serve_q8.sh`, `q6_watchdog.sh`, `night_chain.sh`, `dl_q8.sh`, `calib_score.py`, `compare_verifiers.py`, `q6verify_score.py`. The `/tmp/jjk100` copies are scratch.

## 7. Open notes for the owner

- CLAUDE.md, `pi.md`, `docs/ops/QWEN_MODES.md` and `~/ninfer-work/serve_uncensored_*.sh` still reference the deleted uncensored NVFP4 production model. They need updating when the Q8 setup is measured.
- The base NVFP4 ninfer model (`/mnt/PROJECTS/ninfer-transfer/models/qwen3_8_27b_nvfp4.ninfer`, 18 GB) was **kept**. It is what serves opencode until the switch.
