# CSM P2.1 runner council — framed question (council #30)

- Deployed: 2026-09-16 23:32–00:21 IST (advisors 23:32–23:51, reviewers 23:58–00:21),
  5 advisors in parallel + 5 reviewers in parallel + 1 chairman (owner directive
  2026-09-12: all 5 council members at a time; supersedes the 2026-09-08 one-at-a-time
  rule for council work).
- Provenance: this framed question is the orchestrator's reconstruction of the common
  SITUATION block all ten members received (the per-member prompt was not persisted to
  disk). Every numbered item below was disk-verified by the orchestrator on
  2026-09-16/17. If you doubt a number, read the cited file before judging.

## QUESTION

**SHIP-OR-AMEND the R-8 close + P2.1 runner state before the GPU session.**
Does `tools/csm/p21_sweep.sh` @ `d1c1ff8` ship as-is (docs-only residual), or does it
take a code patch? Which of the two proposed pre-expansions (if any) run before the
GPU day? Five lenses: (1) runner code, (2) R-8 close + gate-window docs (launch order,
halt codes, sha re-stamp), (3) pre-expansions, (4) executor traps, (5) wall-time/VRAM
arithmetic.

## SITUATION (state on disk)

1. **Runner, post-fix.** `tools/csm/p21_sweep.sh` @ `d1c1ff8` (branch
   `character-scoped-questions`, parent `b8b0ed5`). The runner's first council-1 audit
   found two material defects (held-out leg 422 on the wrong api-door; exit-5
   unreachable + A18 sidecar-blind); both closed in the fix-up commit: label/api-door
   split (`p21_sweep.sh:140-145, 239-242`), sidecar-aware watchdog (:169-186), A18 wipe
   of all five ledgers (:114-136). 14-assertion dry-run harness green at
   `/tmp/p21test2/` (fake VENV + stand-in server); `bash -n` clean.
2. **R-8 gate window undischarged.** `reports/csm/GATE_LEDGER.json` `last_green` = R-7
   `60e568f` (pin 1,321). Owed before panel spend: the four standing gates +
   `eval --series jjk` 31/31 at post-R-8 pin **1,331** (collect-only-confirmed), then
   move `last_green` to the R-8 commit. The env-mc trio
   (`tests/test_mcp_server.py:20,35,46`) fails with `:8000` down → W-state pin:
   W1 (`:8000` down) = 1,331 + 3 env-mc fails; W2 (`:8000` up) = 1,334/0. GATE.md is
   silent on the W-state split.
3. **Live GPU state.** Qwen pid 5625 @122880 (120k dial;
   `~/ninfer-work/qwen_mode.txt mode=122880`), ~6.17 GB free; `:8000` down. The plan's
   Phase-2 dial is 100k (A19, `plan/CSM_2PHASE_PLAN.md`).
4. **Sha pin trap.** `reports/master-work/phase_status.txt:4` pins
   `ledger_sha256 c61b0a3f…`; :9 says "verify before any panel spend". Moving
   `GATE_LEDGER.json` `last_green` to R-8 changes the sha → the pin is unsatisfiable
   until re-stamped (a literal executor reads it as ledger drift and re-runs the gate
   window: 1–2 GPU-h).
5. **GATE.md doc defects (first-audit findings).**
   - Launch-order bullet :342-349 + Order note :16-19: self-contradictory — step (1)
     "discharge the gate window" includes gate-3's live probe and gate-4, which need
     `:8000` *up*, but the first explicit ":8000 up" is step (2). The W1/W2 split is
     not in the bullet.
   - :345 names `ninfer-work/qwen-switch.sh` as the Qwen stop tool — wrong script (dial
     switcher only, no stop mode, `~/ninfer-work/` is non-repo-relative). The real stop
     is `~/ninfer-work/ninfer-stop.sh` (unloads Qwen, writes `qwen_mode.txt mode=off`,
     which blocks the `ninfer_restart.sh` poller; a bare `kill` leaves the poller able
     to resurrect Qwen mid-sweep).
   - Halt line :306-309 omits rc 3 (dead-door) — `cli.py:2097` / `:2198`; rc mapping
     2 tamper / 3 dead / 1 crash at `cli.py:2093-2199`. The runner header
     (`p21_sweep.sh:21-22`) is right; the doc table is not.
   - :312 "≈ 2.7 h panel + ~4 min heldout" sums only qa/narrative/roster; the auto
     full-panel door was measured 0.192 s/probe (:137 addendum) → ≈ 3.7 h.
6. **Runner code gaps (post-fix audit).**
   - No `--sanity 100` pre-pass on the door call (`p21_sweep.sh:154` vs
     `PHASE2_JOB.md:66-67` — sanity-100 is first-run-only, zero panel spend). A dead
     door (HTTP 200, empty bundle → MISS verdicts, not ERROR) trips neither exit 5 nor
     exit 4.
   - No pre-check records `/health`'s `device` (the receipt records VRAM only,
     `p21_sweep.sh:71`; `api/main.py:161` serves it). A CPU `:8000` passes all
     pre-checks (`:83-88`) and crawls for hours.
   - Resume-boundary straddle (R5, HIGH): the ERROR window
     (`p21_sweep.sh:177`) counts the last 50 rows of main+sidecar, but the sidecar is
     never reset on resume — `span_recall.py:408-411` reads the stale `.new` into
     `prior` and :469 appends fresh rows *after* the old ERROR burst. After an exit-5
     halt + the documented resume (:224-230), a stale burst can still sit in the window
     → false exit 5 at every resume after an ERROR burst.
   - Pre-wipe sanity ledgers (the canary floors): 4×100-row `e3d73720` ledgers —
     qa/narrative/roster stamped `f2a611d`, auto stamped `2f67222`; HIT 95/35/2/37.
     A18 wipes them at launch.
7. **Proposed pre-GPU expansions (C, ranked).**
   1. Offline `route()` bucketing (~30 min, model-free): `route()` is regex +
      overrides YAML + SQLite; the R-8 guard `wants_chronology_set`
      (`chronology.py:597/616`, called from `router.py:632`) is pure regex.
      `api/main.py:208` is `route(..., subject=None)` — the sweep sends no subject, so
      a local `route()` mirrors the server's auto door exactly. Yields the auto leg's
      per-sub-door load, the expected auto hit-rate as a weighted mix of the four
      forced-door sanity rates, and a calibration diff against the 100 `mode_routed`
      sanity rows.
   2. Q1/Q2 widened census bank (`reports/csm/CLOSE_COUNCIL_RULINGS_Q1_Q4.md:11-22`;
      Q2 sizes the pool to the 376 ability rows) — a P2.1 entry condition.
   R3's pricing: SKIP both pre-sweep — the sanity pre-pass catches dead doors in ~10
   min (route() becomes post-hoc triage), and the bank gates P2.3, not the sweep, so it
   rides the GPU session in parallel with the detached run.