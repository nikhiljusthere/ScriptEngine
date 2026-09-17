# P23_HANDOFF — P2.3 + P2.2 census grading, model-unloaded batch (council #31 P-2/P-5)

The one remaining GPU step of the P2.1→P2.5 close: fire the pre-baked grader
with Qwen DOWN and the whole 32 GB card free. **No :8000 is needed** — the
grader is in-process, the exact `build_context` path the `/context` endpoint
serves (auto door = router + fallbacks, included).

## Why this batch (pre-registrations, `reports/csm/COUNCIL_p21_post_sweep.md`)

- **P-5 / P2.3:** the A14 comprehension step = a grader over the 486-item
  writer-shaped widened census bank (`reports/csm/census_widened_csm.json`,
  v1 60 + v2 50 + ability-pool 376), qa door, in-process CUDA.
- **P-2 / P2.2:** the 26-line P1.4 bar audit
  (`reports/csm/bar_audit_p14_preregistered.json`), graded **pre-fix**:
  qa control arm (primary verdict) + auto door (the R-9-contingent
  supplement, P-3). The verdict is declared R-9-contingent: any post-fix
  delta is R-9's evidence, not the audit's.

## State this batch assumes (verify, then proceed — the runner pre-checks all of it)

- Qwen may be UP (any dial). The batch **stops it** (`ninfer-stop.sh`) and
  **leaves it DOWN**; the owner restores the dial on return (P2.4 needs Qwen
  up). The stop writes `mode=off` and blocks the restart poller (a bare kill
  lets it resurrect Qwen mid-run — GATE.md launch-order note).
- A CPU `:8000` may be running (hand-restart after the qwen-switch
  same-device defect, `9c9cbe4`). **Leave it** — it holds its models in RAM
  only; the batch never touches it.
- If a *CUDA* `:8000` or another GPU job holds the card, the free-memory
  pre-check trips (exit 11) — stop that job first.

## Launch

From the repo root, fully detached (the job survives the launching session;
the plain-`nohup` variant dies with the process group — setsid rule):

```
setsid nohup bash tools/csm/p23_handoff.sh > /dev/null 2>&1 < /dev/null &
```

Poll with fast, bounded checks (no bare sleeps):
`reports/master-work/p23_grader_*_RECEIPT.md` appearing = done. Wall
estimate 5–10 min (model load + 538 in-process probes; the P2.1 sweep ran
0.506 s/probe *through HTTP* with a separate service — in-process is faster).

## What it produces (all committed on the owner's return — the batch writes, it does not commit)

- `reports/csm/census_widened_csm_results.jsonl` — P2.3/A14, 486 rows
- `reports/csm/bar_audit_p14_results.jsonl` — P2.2, 26 rows × {qa, auto}
  (per row: verdicts + hits/missing per door + the auto door's `routed_mode`
  — the R-9 input on writer-shaped questions)
- `reports/master-work/p23_grader_<stamp>_RECEIPT.md` (+ `_run.log`)

## Halt codes (runner)

| code | meaning |
|---|---|
| 10 | Qwen would not stop (mode file not `off` / :18080 busy) |
| 11 | GPU free < 6 GB after stopping Qwen — owner intervention |
| 12 | venv / banks missing |
| 14 | smoke run failed (mechanics or model load broken) |
| 16 | grader nonzero — exit 3 = ERROR rate > 10% (a quietly-wrong run; do not ship, diagnose), 124 = 45-min watchdog |

## After it lands (owner return, Qwen up)

1. ~~Commit the results + receipt.~~ **DONE 2026-09-17** — run
   `p23_grader_20260917-103148` (155 s, 0/538 errors, Qwen was already
   down): widened 486 (qa) = 417 MECH_GREEN (85.8%); bar audit qa 11/26
   (pre-fix control arm, P-2), auto 14/26 (R-9 supplement). Results +
   receipt committed `3d43a21`; red triage in
   `reports/csm/p23_red_triage.md`.
2. **P2.4 writer leg:** one `script-gen` + `cli verify` on CSM (needs Qwen +
   the CUDA `:8000` research path).
3. **The R-9-vs-writer-bar evidence call** (council or owner, per the trigger
   rules): the P-3 firing condition is writer-shaped misroute evidence from
   P2.4 + the P2.3 verdicts; `bar_audit_p14_results.jsonl` carries the
   `routed_mode` per case. Check `series/csm/overrides.yaml` (per-wiki route,
   no JJK debt) before any series-agnostic `router.py` change.
4. **Residual triage sign-off** (P-4): the logs are already on disk and
   committed — `p21_sweep_2026-09-17/triage/triage_qa_p1.jsonl` (118),
   `triage_qa_p2.jsonl` (143), `floor_sample.jsonl` (289 sampled / 64 cells /
   32,383 residual rows). → **`PHASE_B_COMPLETE`**
   (`plan/CSM_2PHASE_PLAN.md` §P2.5 checklist + P-4 scope).