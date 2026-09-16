# CSM P2.1 runner council — advisor finals (council #30)

- Date: 2026-09-16, 23:32–23:51 IST
- Method: 5 advisors deployed in parallel (owner directive 2026-09-12: "council's all 5 at a
  time"), each fresh-context, zero-GPU, read-only; post-fix re-audit of the R-8 close + P2.1
  runner at `d1c1ff8`.
- Framed question: `framed_question.md` (this directory).
- Provenance: finals transcribed **verbatim** from the session database
  (`~/.local/share/opencode/opencode.db`, message table) — the task results were never
  persisted by the orchestrator, so the DB restore is the record.
- Lettering (reviewers reference only these letters):
  A = Contrarian, B = First-Principles, C = Expansionist, D = Outsider, E = Executor.
- Letter↔session map: A = `ses_f549de3fdffetDMq79u6gpPveu`, B = `ses_f549de3e7ffez65CATawitaKOZ`,
  C = `ses_f549de3dbffePl2KDuk6yKK5EN`, D = `ses_f549de3d2ffeadgVm4kb5EVCyX`,
  E = `ses_f549de3b8ffe22Z6JhSr5VUHmg`.
- Post-hoc on-disk verification (parent session, 2026-09-16/17): the stop-tool misnaming
  (A/D/E) confirmed — `~/ninfer-work/ninfer-stop.sh` exists and writes `qwen_mode.txt
  mode=off`; `qwen-switch.sh` is dial-only. rc-3 dead-door at `cli.py:2097/:2198`
  confirmed. The `--sanity` absence at `p21_sweep.sh:154` confirmed (PHASE2_JOB.md:66-67:
  sanity-100 first-run-only). Sanity HIT floors 95/35/2/37 confirmed in the four
  `e3d73720` ledgers. `phase_status.txt:4/:9` sha pin confirmed.

## A — Contrarian

Session `ses_f549de3fdffetDMq79u6gpPveu`

**SHIP-WITH-CHANGES.** All four council-1 fixes are closed on disk: (a) the heldout leg runs api-door `auto` under label `auto-heldout` (`tools/csm/p21_sweep.sh:140-145, 239-242`); I verified the runner's own `_panel_hash` import (`p21_sweep.sh:96`) against the real venv — it works in 0.1s and returns the expected `ec15e0d8`, so the heldout ledger name resolves. (b) The A18 wipe spans all five ledgers + sidecars (`p21_sweep.sh:133-136`); the watchdog counts main + sidecar and tails the sidecar for the ERROR bound (`p21_sweep.sh:169-186`). (c) The auto-sanity stamp `2f67222` correction is on disk (`GATE.md:337-340`; work_log 2026-09-16T23:30 entry, line 125). (d) Launch order + do-not-commit-mid-sweep warning (`GATE.md:342-349`; receipt `p21_sweep.sh:228-230`). Kill/resume is self-healing: per-row-flushed sidecar (`span_recall.py:469-471`) leaves a clean SIGTERM boundary, the strict ledger reader rejects a torn row (`span_recall.py:334-349`, rc 2), and a kill mid-merge re-merges idempotently on resume.

What the 14-assertion dry-run (fake VENV + stand-in server) cannot catch, and the most likely mid-sweep GPU failure: the runner never runs the spec's per-door `--sanity 100` pre-pass (`p21_sweep.sh:153` vs `PHASE2_JOB.md:66-67`). A dead door (HTTP 200, empty bundle → MISS verdicts, not ERROR) trips neither exit 5 nor exit 4, burns ~2.7 h per door, and defers the pre-consumption go/no-go (`PHASE2_JOB.md:60-64`). Second: no precheck records the :8000 device (`p21_sweep.sh:12-13` asserts service state only) — a CPU :8000 passes everything and crawls for hours.

Actions: (1) Add the per-door `--sanity 100` pre-pass, fresh-start only — drop it on resume (the CLI's limit applies to un-probed rows, so capping a resumed run at 100 trips exit 30). (2) Record /health's `device` in the receipt pre-check section (one line; `_sweep_stamps` already reads it, `cli.py:2019-2020`).

## B — First-Principles

Session `ses_f549de3e7ffez65CATawitaKOZ`

Verdict delivered; the two actions are doc-only and belong to the coding side (my mandate is read-only, so I don't apply them). The one remaining next step I can take is turning them into paste-ready text — here are the drop-in replacements for the two GATE.md defects:

**GATE.md:342-349 ("Launch order" bullet) — replace with:**

> **Launch order (the undischarged gate window, revised 2026-09-16 — the original wording scheduled all four gates before `:8000` was up, but gate-3's live probe and gate-4 need it; one service state must certify both the gates and the sweep):**
>
> 1. **W1 — in-process gates, `:8000` down:** `pytest tests/ -q` = 1,331 (pin) + `eval --series jjk` 31/31, in-process CUDA (the one-copy embedder+reranker ~5.3 GB co-locates with Qwen 100k; if Qwen is on a heavier dial, stop it first).
> 2. **Service state:** stop Qwen (`ninfer-work/qwen-switch.sh`, `docs/ops/PC_GPU_HANDOFF.md`) and bring `:8000` up on CUDA with the whole card, **started from the current tree** (record HEAD in the receipt).
> 3. **W2 — gates against that one service:** gate-3 `span-recall --series jjk` (offline rc=0 + 400-probe ≥ 390/400) + gate-4 `canon-run --series opm --skip-eval` (236/236, 79.0%). Then move `GATE_LEDGER.json` `last_green` to the R-8 commit (receipts_commit in the doc-only ledger-fill commit, R-7 pattern).
> 4. **Canary:** before launching the runner, count the HITs in the five pre-wipe sanity ledgers (floors: qa 95, narrative 35, roster 2, auto 37 /100 — A18 wipes them at launch). At ~10 min into the sweep (first 100 rows of the qa door) the HIT% must sit near the qa floor (~90+); a large deficit means quietly-wrong (stale `:8000` code or vectors → MISS_DOC floods, which the 10/50 ERROR bound cannot catch): kill and diagnose, don't wait the 2.7 h.
> 5. **Launch the runner against the same service** (no restart; exit 12 enforces Qwen-down).
>
> **Do not commit while the sweep runs**: a HEAD move makes every ledger's stamp stale and the next launch wipes all five ledgers (A18) — full restart.

**GATE.md:16-19 (the "Order" note in the gate-1 block) — replace with:**

> **Order (2026-09-16 runner fix-up, revised): W1 in-process gates (`:8000` down) → stop Qwen + bring `:8000` up on the whole card (current tree) → W2 gates against it → move GATE_LEDGER → launch the runner against the same service (full sequence under "Launch order" below). The runner's pre-checks (exit 11/12) enforce the service state only; they cannot see the gates.**

Nothing else is owed from my side: no code-level residual defects remain — runner, CLI stamps, ledger state, and the A26/A18 enforcement are all sound. The GPU hand-off is ready pending those two doc re-stamps.

## C — Expansionist

Session `ses_f549de3dbffePl2KDuk6yKK5EN`

**SHIP.** The coding side is ready for the GPU handoff. Verified on disk this session: frozen panel sha `cf72135f…` / heldout `604dc8ca…` intact (17,181/200 rows; h8 `e3d73720`/`ec15e0d8` match all five ledger names); the runner's pre-check one-liner runs clean in 0.1s; ledger rows carry the exact `"commit": "f2a611d"` stamp format the runner's grep expects; CLI rc semantics (2 tamper / 3 dead-door / 1 crash) match the 20+rc mapping (cli.py:2093–2199). Council-1 defects are closed: heldout now runs api-door `auto` (p21_sweep.sh:140–151, 241–242; main.py:79 accepts "auto", so no 422) and watchdog + A18 wipe are sidecar-aware (:111–130, 172–177). The owed gate window is explicitly the GPU session's job (GATE.md:277–282), not a runner defect.

Ranked zero-GPU expansions (value × cost):

1. **Offline `route()` bucketing — top pick.** `route()` is model-free (regex + overrides YAML + SQLite; the R-8 guard is pure regex, `wants_chronology_set`, chronology.py:616), and the sweep sends the bare panel sentence with no subject (span_recall.py:207–219), so `route(series_paths("csm"), sentence)` mirrors the server's auto door exactly. A ~30-min throwaway script yields: (a) the auto leg's per-sub-door load, (b) the expected auto hit-rate as a weighted mix of the four forced-door sanity rates against the 97.5% bar — a pre-registered A17 input, and (c) a calibration diff: the current router must reproduce the 100 `mode_routed` rows in the sanity auto ledger. This is the one expansion that can catch a routing regression before 2.7h of panel spend.

2. **Q1/Q2 widened census bank — second.** P2.1 entry condition, to run inside the sanity window (CLOSE_COUNCIL_RULINGS_Q1_Q4.md:11–22); Q2 sizes the pool to the 376 ability rows. Without it, the GPU session authors on-card or the P2.3 null-branch re-gate slips. All-or-nothing: an unverified expect-term bank poisons P2.3.

Traps: pre-baking extraction prompts (PHASE2_JOB.md:140–145 — targets may depend on census output), a 5th held-out leg (marginal per A24(a)), and an estimate-mode flag (watchdog + per-100 progress lines already report the rate; the 2.7h estimate is on disk). The stale 13-row `sweep_qa_ec15e0d8.jsonl` (Sep 8) is inert — one `rm` on the GPU side.

**Actions:** (1) run the route() bucketing now; land histogram + expected auto rate in GATE.md before panel spend. (2) Author the Q1/Q2 bank (5 page types, 376-row pool, verbatim-verified) into `reports/csm/` before the sanity window.

## D — Outsider

Session `ses_f549de3d2ffeadgVm4kb5EVCyX`

SHIP-WITH-CHANGES — one-line doc fix; no code changes.

(a)–(d) verified closed against code and disk: (a) `run_door` splits label/api-door (tools/csm/p21_sweep.sh:140-145, 239-242); api/main.py:79 accepts only the five modes, and the heldout ledger name `sweep_auto_ec15e0d8.jsonl` matches the CLI's recomputed hash (span_recall.py:287; both verified on disk). (b) the watchdog counts main + sidecar and tails the sidecar for the ERROR window (p21_sweep.sh:172-177); A18 wipes main + sidecar across all five ledgers (p21_sweep.sh:114-136); the CLI re-probes ERROR rows on resume (span_recall.py:419) and the sidecar survives a kill (span_recall.py:469-489). (c) GATE.md:337-340 matches on-disk stamps (auto=2f67222, others=f2a611d). (d) launch order at GATE.md:342-349. Frozen inputs verified (p21_sweep.sh:40-41 vs on-disk shas; 17,181/200 rows).

The one pre-handoff fix (doc, not code): GATE.md:345 says stop Qwen via `ninfer-work/qwen-switch.sh` — wrong script (it only switches the context dial) and a non-repo path (it lives at `~/ninfer-work`); the real tool is `~/ninfer-work/ninfer-stop.sh`, which also writes `qwen_mode.txt mode=off` so the master-work poller (ninfer_restart.sh, docs/ops/PC_GPU_HANDOFF.md:106) can't resurrect Qwen mid-sweep. A hand-rolled pkill → poller resurrection → card stolen → exit 4.

Top-3 traps for a first-time executor:
1. GATE.md:345 misnames the stop tool; `ninfer-work/` isn't repo-relative. Fix: one line → `~/ninfer-work/ninfer-stop.sh`.
2. Launch step (1) needs `:8000` up for the gates' HTTP legs (probe + canon), but the first explicit ":8000 up" is step (2); the in-gate co-location pattern is only in reports/master-work/work_log.md:118. Fix: one line in GATE.md:342-343.
3. GATE.md:308's halt table omits rc 3 (dead-door) — the runner header is right (p21_sweep.sh:21-22); and "re-run the same launch line" resume only works if no commit happened meanwhile (A18 wipes all five ledgers, GATE.md:347-349). Fix: add "3 dead-door".

## E — Executor

Session `ses_f549de3b8ffe22Z6JhSr5VUHmg`

**SHIP-WITH-CHANGES.** The runner is sound; the hand-off *instructions* carry three doc-level defects. Verified on disk: panel/holdout sha256 == the A26 frozen constants (pre-checks will pass); all four e3d73720 ledgers stale-stamped (f2a611d/2f67222) so A18 wipes all four; no `.new` sidecars; `sweep_auto_ec15e0d8.jsonl` absent (held-out fresh); the orphan `sweep_qa_ec15e0d8.jsonl` is inert (not in the managed five, p21_sweep.sh:133-136). Findings (a)-(d) are closed: label/api-door split (p21_sweep.sh:140-145, 242), sidecar-aware watchdog (169-186) + A18 over all five ledgers (114-130), auto-stamp doc fix (GATE.md:338-340), launch order stated (GATE.md:342-349).

But GATE.md:342-349, read by the executor, has:
1. **Self-contradictory order.** Step (1) "discharge the gate window" includes gates 3/4 (span-recall live probe, canon opm), which need :8000 *up*; step (2) says "then bring :8000 up." The W1/W2 split (W1 in-process with :8000 down, W2 with it up — the pattern from work_log R-5/R-6/R-7/P1.4) is not in the bullet.
2. **"Stop Qwen (`ninfer-work/qwen-switch.sh`)" is doubly wrong**: from the repo root the path doesn't exist (it's `~/ninfer-work/`), and the script has **no stop mode** (`usage: qwen-switch.sh <262k|100k|<tokens>>`; no-ops when the dial is unchanged). Stopping = `kill` the ninfer-serve pid (currently 5625, @122880) and confirm `:18080` free. Bounded cost: runner pre-check exit 12 (p21_sweep.sh:89-92) is the safety net.
3. **`phase_status.txt:9` "verify ledger_sha256 (c61b0a3f) before any panel spend"** becomes unsatisfiable once the launch order's step (1) does its job (moving `GATE_LEDGER.json` `last_green` to R-8 changes the sha). A literal executor may conclude ledger drift and re-run the whole gate window — 1-2 GPU-hours.

Also: W1 in-process with Qwen@120k resident leaves only ~0.9 GB margin (6.2 GB free vs ~5.3 GB model load; R-5 OOM'd at 0.07 GB, work_log:94). Stopping Qwen *before* W1 removes it — and Qwen must be down for the sweep anyway.

**Actions:** (1) Rewrite GATE.md:342-349 as an explicit six-step sequence with per-step device state: stop Qwen (kill, not qwen-switch) → W1 full-card `pytest tests/ -q` (1,331, 3 env-mc expected) + `eval --series jjk` (31/31) → bring :8000 up on CUDA (confirm `device=cuda` in the log, not nvidia-smi — models load lazily) → W2 span-recall jjk + canon opm → GATE_LEDGER → aada154/1,331 **plus re-record the marker sha** → launch runner; restate no-commit-mid-sweep (A18 wipes all five ledgers, ~2.7 h restart, p21_sweep.sh:99-107). (2) The hand-off prompt must carry the exact :8000 line (`setsid nohup scriptengine/.venv/bin/python -m scriptengine.api.main > /tmp/scriptengine_api.log 2>&1 < /dev/null &`) and the poll recipe: `reports/master-work/p21_sweep_<stamp>_run.log` for `door X: done` / `HALT` (30 s cadence, ~2.7 h + 4 min wall per GATE.md:312; per-door `_door_<label>.log` for progress), then exit-code table: 4 = restart :8000 + relaunch (ledgers resume forward, no row loss, p21_sweep.sh:224-230), 5 = read the `.new` sidecar tail — connection errors = restart, 500/OOM = council, 20-23/30 = coding defect, hand back. On exit 0: A17-grade from the receipt (auto ≥ 97.5 %, qa miss file, narrative/roster floors, held-out OOS, p21_sweep.sh:252-258), then P2.3 widened census + D6 extraction (Qwen back on the card, :8000 down; answer PHASE2_JOB.md:140-145's open question before pre-baking the extraction batch).
