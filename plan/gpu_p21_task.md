# C task brief — gpu-p21 (P2.1 sweep: R-8 gate window + pre-baked runner)

You are C — the GPU-step agent for CSM Phase 2, P2.1 (the cross-session
handoff, docs/ops/PC_GPU_HANDOFF.md tier 2). The design is CLOSED:
council #30 returned SHIP-WITH-CHANGES and every amendment (A1–A6)
landed at `22d3ac2`. This brief is a runbook, not a design doc — do not
re-litigate; anything not covered here gets a question appended to
`reports/master-work/work_log.md` for A, not an improvisation.

Work from /home/goblin/ScriptEngine with `scriptengine/.venv/bin/python`.

## Runbook (in order; full text: reports/csm/GATE.md "Launch order
(the undischarged gate window, council #30 A2)")

1. **W1 — in-process, whole card:** `~/ninfer-work/ninfer-stop.sh`,
   verify `mode=off` + `:18080` free (a bare kill lets the
   `ninfer_restart.sh` poller resurrect Qwen — always the stop
   script) → `pytest tests/ -q` (expect **1,331** collected, 3 known
   env-mc failures: `tests/test_mcp_server.py:20,35,46`) +
   `eval --series jjk` (expect 31/31).
2. **Service:** start `:8000` on CUDA, setsid-detached:
   `setsid nohup scriptengine/.venv/bin/python -m scriptengine.api.main > /tmp/scriptengine_api_p21.log 2>&1 < /dev/null &`
   — poll `/health` (bounded loop, ~15 s status lines) until 200 and
   confirm `device=cuda`.
3. **W2 — gates against that one service:** `cli span-recall
   --series jjk` (offline rc=0, then `--probe 400` ≥ 390/400) +
   `cli canon-run --series opm --skip-eval` (236/236, 79.0%).
4. **Ledger + re-stamp:** move `reports/csm/GATE_LEDGER.json`
   `last_green` to the R-8 commit (`aada154`, pin 1,331), then
   re-stamp `reports/master-work/phase_status.txt:4` `ledger_sha256`
   (a literal executor otherwise reads the :9 pin as false drift and
   re-runs the window).
5. **Canary:** ~10 min after the launch, the HIT counts in the 4
   wiped sanity ledgers (qa 95 / narrative 35 / roster 2 / auto 37
   per 100) must sit near the qa floor (~90+). A large deficit = a
   quietly-wrong `:8000` (a MISS_DOC flood sails under the 10/50
   ERROR bound) → kill the service, diagnose, redo steps 2–3.
6. **Launch the runner** against the same service (no restart):
   `setsid nohup bash tools/csm/p21_sweep.sh > /dev/null 2>&1 < /dev/null &`
   Pre-checks (exit 10/11/12) enforce the frozen A26 panel/heldout
   hashes + row counts, `device=cuda`, Qwen down; A18 wipes
   stale-stamp ledgers; 30 s per-door watchdog; ≈ 3.7 h wall +
   ~4 min heldout. **No mid-sweep commits** (A18 wipes all 5 ledgers
   on a commit move; a restart costs ~3.7 h).

**In parallel with the sweep wall (model-free, no `:8000` needed):**
author the Q1/Q2 widened census bank — 5 in-scope page types, 376-row
ability pool, verbatim-verified expect terms — per
`reports/csm/CLOSE_COUNCIL_RULINGS_Q1_Q4.md:11-22` into
`reports/csm/`. It gates P2.3, not the sweep (chairman #30 item 4:
the bank rides the GPU session in parallel at zero marginal cost).

## Runner halts (exit code → action)

| exit | meaning | action |
|------|---------|--------|
| 0 | done | read `p21_sweep_<stamp>_RECEIPT.md`; write the sweep report + a work_log line; `~/ninfer-work/qwen-switch.sh 100k` (A19 — NOT the 262k default); P2.2 re-grade only on dimension shift (chairman A7) + A14 comprehension check before `PHASE_B_COMPLETE`. |
| 4 | `:8000` health fail ×2 | restart `:8000` on CUDA, re-launch the runner (A18 resumes from the stamped ledgers). |
| 5 | ERROR > 10 of the last 50 rows THIS RUN wrote | a real defect — keep run.log + receipt, stop, escalate to A with the receipt path. |
| 10 | frozen panel/heldout hash or row count moved | the frozen inputs were touched — restore them from git, re-launch. |
| 11 | `/health` down or device ≠ cuda | redo runbook steps 2–3, re-launch. |
| 12 | Qwen `:18080` is UP | `~/ninfer-work/ninfer-stop.sh`, verify `mode=off`, re-launch. |
| 21 | door CLI crash | inspect the per-door log (named in run.log), fix the cause, re-launch. |
| 22 | ledger corrupt / tier-0 miss | wipe that door's ledger + `.new` sidecar, re-launch. |
| 23 | dead-door (the sanity subset found 0 HITs) | routing/service defect — stop, escalate to A with the door log. |
| 30 | row-count integrity | corrupt resume state — wipe that door's ledger + sidecar, re-launch. |

Every launch leaves `reports/master-work/p21_sweep_<stamp>_RECEIPT.md`
+ `_run.log` + per-door logs; append one line per launch/halt to
`reports/master-work/work_log.md`.

## Standing rules

- `:8000` on CUDA, whole card, for the entire sweep; Qwen DOWN for the
  whole run (the pre-check enforces it, exit 12). The A17 floors and
  the wall estimate are CUDA numbers — never run the sweep on CPU.
- W2 is the JJK non-regression proof (JJK stays 100%); do not touch
  JJK files.
- `work_log.md` is B-only: append at EOF, never rewrite.
- The design is closed (council #30, SHIP-WITH-CHANGES). Do not
  re-open the launch order, the halt bounds, the A18 wipe policy, or
  the 100k post-sweep switch.