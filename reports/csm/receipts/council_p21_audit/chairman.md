# Council #30 — CSM P2.1 runner: chairman's record (2026-09-17)

Chairman: fresh-context, zero-GPU, read-only, 2026-09-17. Inputs: `framed_question.md`, `advisors.md` (A–E), `reviews.md` (R1–R5). Every verdict-affecting claim re-verified against disk (runner @ `d1c1ff8`, `span_recall.py`, `cli.py:2093-2202`, `api/main.py`, `GATE.md`, `GATE_LEDGER.json`, `phase_status.txt`, `~/ninfer-work/`, `reports/span-recall/csm/`, `qwen_mode.txt`; fresh `pytest --collect-only` = 1,331).

## VERDICT

**SHIP-WITH-CHANGES.** The runner's council-1 fixes are closed on disk and its pre-checks/freeze inputs sound, but one verified resume-boundary defect (R5) plus two missing pre-pass/receipt lines and a self-contradictory `GATE.md` launch order mean the GPU session must not start until a ~1 h zero-GPU patch + doc re-stamp lands.

## Amendments

**A1 — runner patch, `tools/csm/p21_sweep.sh` (MUST before GPU session; resolves R5, A, R2, R4-4).**
1. Resume baseline (R5): `run_door` (~:152) records `base_main`/`base_side` (the `wc -l` of ledger/sidecar, `|| echo 0`, extend the `local` list at :150) before the `nohup` launch; the watchdog (:177) then counts ERROR only over this run's rows: `main_new=$((main_l-base_main)); side_new=$((side_l-base_side)); err=$({ [ "$main_new" -gt 0 ] && tail -n +$((base_main+1)) "$ledger" | tail -n "$ERROR_WINDOW"; [ "$side_new" -gt 0 ] && tail -n +$((base_side+1)) "$side" | tail -n "$ERROR_WINDOW"; } | tail -n "$ERROR_WINDOW" | grep -c '"verdict": "ERROR"' || true)` — same shape as the existing :177 line. Verified defect: on resume, `span_recall.py:408-411` reads the stale `.new` into `prior` and :469 appends after it → a pre-halt ERROR burst can sit in the 50-row window → false exit 5 after any burst-halt + resume.
2. After `local pid=$!` (:154): `trap 'kill "$pid" 2>/dev/null' EXIT` (R4: a non-reboot runner death orphans the CLI into a second sweep on the same sidecar).
3. Standalone sanity pre-pass after the A18 block (:138), per door whose ledger is 0 rows post-wipe: a `--sanity 100` CLI call (PHASE2_JOB.md:66-67: first-run-only, zero panel spend; rc 3 = dead door → halt). Fresh-start only — resumed doors skip it, since a capped resume trips exit 30 at :194-197 (R2's correction of A).
4. Receipt (:71) + pre-check: record `:8000 device` from `/health` (`main.py:161`); non-cuda → exit 11 (a CPU `:8000` passes all pre-checks today).
Re-verify: the 14-assert dry-run `/tmp/p21test2/` + 1 new assert (resume after a sidecar ERROR burst → no false exit 5). No CLI change.

**A2 — launch-order rewrite, `GATE.md:342-349` (MUST; B's drop-in, corrected by R2/R4).**
> 1. **W1 — in-process, whole card:** stop Qwen FIRST via `~/ninfer-work/ninfer-stop.sh` (writes `mode=off`; blocks the `ninfer_restart.sh` poller — a bare kill lets it resurrect Qwen mid-sweep; `qwen-switch.sh` has no stop mode, GATE.md:345 mislabels it). Verify `mode=off` + :18080 free. Then `pytest tests/ -q` (W1 expectation, A5) + `eval --series jjk` 31/31.
> 2. **Service:** `:8000` up on CUDA from the current tree (setsid-detached); record HEAD; confirm `/health` `device=cuda` (models load lazily).
> 3. **W2 — gates against that one service:** `span-recall --series jjk` (offline rc=0 + 400-probe ≥ 390/400) + `canon-run --series opm --skip-eval` (236/236, 79.0%).
> 4. **Ledger + re-stamp:** move `GATE_LEDGER.json` `last_green` to the R-8 commit, then re-stamp `phase_status.txt:4`'s `ledger_sha256` (the :9 pin is otherwise unsatisfiable; a literal executor reads the drift as ledger drift and re-runs the window — 1–2 GPU-h).
> 5. **Canary:** count HITs in the 4 pre-wipe sanity ledgers (qa 95 / narrative 35 / roster 2 / auto 37 per 100; A18 wipes at launch). At ~10 min in, HIT% must sit near the qa floor (~90+); a large deficit = a quietly-wrong `:8000` (MISS_DOC floods the 10/50 bound can't catch) → kill + diagnose.
> 6. **Launch the runner** against the same service (no restart; exit 12 enforces Qwen-down). **No mid-sweep commits** (A18 wipes all 5 ledgers; ~3.7 h restart).
> Post-sweep: restart Qwen via `qwen-switch.sh 100k` (plan A19), not the 262k default `ninfer-stop.sh` restarts.

**A3 — Order note, `GATE.md:16-19` (MUST):**
> **Order (council #30): stop Qwen (`ninfer-stop.sh`, verify `mode=off`) → W1 in-process, whole card → `:8000` up on CUDA → W2 gates → move `GATE_LEDGER` + re-stamp `phase_status` sha → launch the runner against the same service. The runner's pre-checks (exit 11/12) see service state only, not the gates.**

**A4 — halt-table rc-3 row, `GATE.md:306-309` (MUST; D):** add "…, **3 dead-door** (`--sanity` found 0 hits on the door's 100 probes; `cli.py:2196-2202`), 1 crash" — the runner header (`p21_sweep.sh:21-22`) already carries it; the doc table omits it.

**A5 — W-state pin, `GATE.md` R-8 section (~:280) (MUST; R4-2, number corrected):** "W1 (`:8000` down) = 1,331 collected with the 3 known env-mc failures (`tests/test_mcp_server.py:20,35,46`); W2 (`:8000` up) = 1,331/0. (SITUATION/R4's 1,334/0 is a +3 arithmetic drift — verified collect-only = 1,331.)"

**A6 — wall estimate, `GATE.md:312` (SHOULD; R4-3):** "≈ 3.7 h panel (2.73 h + 17,181 × 0.192 s auto ≈ 0.9 h, :137 addendum) + ~4 min heldout" — the 2.7 h sum omits the auto full-panel door.

**A7 — post-sweep steps (post-sweep; R4-5):** P2.2 re-grades only if misses shift a dimension; the A14 comprehension step must fire (P2.3b if null) before `PHASE_B_COMPLETE`.

## CONFLICT RESOLUTIONS

1. **B vs R2 (co-location):** R2 stands — the live dial is 120k (`qwen_mode.txt mode=122880`, pid 5625, free 6,279 MiB), not 100k; a 5.3 GB W1 load leaves ~0.9 GB margin against R-5's OOM at 66 MiB free (work_log R-5 entry) → E's order, stop Qwen before W1.
2. **A's pre-pass form (per R2):** stands as a standalone fresh-start-only call before the loop; a capped run inside `run_door` trips exit 30 (:194-197).
3. **R5 vs doc-only consensus:** R5 stands — the resume-boundary defect is verified on disk (`span_recall.py:408-411,469,489`; `p21_sweep.sh:177`) → a code patch, not doc-only.
4. **R3's SKIP of C's expansions:** the pricing stands — `route()` bucketing SKIPs pre-sweep (subsumed by the pre-pass; post-hoc triage if the auto leg is short); the Q1/Q2 census bank gates P2.3, not the sweep — it runs parallel in the GPU session at zero marginal cost.
5. **262k vs 100k restart:** R4 stands — `ninfer-stop.sh`'s 262k line is the exploratory default; plan A19 sanctions 100k for Phase 2 → `qwen-switch.sh 100k`.

## Verify before launch (on-card)

1. `nvidia-smi`: Qwen (pid 5625) down, ~31 GB free; :18080 free; `qwen_mode.txt` = `mode=off`.
2. `/health`: 200, `device=cuda`, `started` ts newer than the last engine commit (stale guard, `main.py:171`).
3. HEAD = the post-patch commit; A18 wipes the 4 stale ledgers (f2a611d ×3 / 2f67222); panel shas `cf72135f…`/`604dc8ca…`, 17,181/200 rows.
4. W1: 1,331 collected, 3 env-mc failures; W2: 1,331/0; `eval --series jjk` 31/31.
5. `/tmp/p21test2/run.sh` green post-patch (14 + 1 new assert).
6. `GATE_LEDGER.json` `last_green` = the R-8 commit + `phase_status.txt` sha re-stamped, before the launch line.