# A/B charter — this deployment (2026-09-08, post-transcript-import)

Two long-lived pi sessions on the 100k Qwen dial, one GPU each. Master-work's
PC loop stays **parked** (its `STOP` file on disk); this is A/B without the
loop: A supervises, B works.

## A — tmux session `control` (the GPU supervisor)

Job: **control and monitor every shell that runs on the GPU** — Qwen `:18080`
(`ninfer-work/qwen_mode.txt` is the source of truth for the dial), the `:8000`
service, and any in-process CUDA job B launches (pytest model tests, eval,
span-recall probes, canon-run, one-copy embedder jobs).

Standing rules (CLAUDE.md GPU section + `docs/ops/QWEN_MODES.md`):
- CUDA first / CPU last; no CPU job > 15 min; heavy LLM batches
  (`events-extract`) dedicate the card (stop `:8000` first, never CPU-workaround).
- One copy of the embedder/reranker at a time (stop `:8000` for an in-process
  CUDA job, restart it after).
- `:8000` launches are `setsid`-detached + short `ps`/`curl /health` verify.
- A rules on B's escalations (`plan/state.md`); A's liveness signal =
  timestamped lines in `reports/master-work/decisions.md` (A is the only
  writer; a quiet file = A is dead — see `plan/AB_DEPLOYMENT.md` §6.4).
- A stays thin (short poll bursts, N ≥ 60 s; shared-KV pacing per
  `AB_DEPLOYMENT.md` §7): reads state files, writes decisions, spawns/kills B,
  owns Qwen dial switches **between agent turns**.

Kill/resume for B: `AB_DEPLOYMENT.md` §6 (overflow → fresh respawn, never
`--session` an overflowing transcript; terminal death → resume if it fits,
else respawn; disk is the tiebreaker).

## B — tmux session `work` (the worker)

Job: campaign work. Next authorized campaign: **CSM** (`plan/CSM_2PHASE_PLAN.md`
— Phase 1 fixing process; the JJK campaign closed 2026-09-07, D11). Read it,
sync the campaign todos, then **wait for the owner's directive before
starting work units**.

B discipline:
- Checkpoint per unit: `plan/state.md` position + a `reports/master-work/
  work_log.md` line (with `ETA:` at unit start).
- All model/GPU work on CUDA under the 100k dial; no CPU shell command > 15 s.
- Subagents: ≤ 2 parallel workers per wave; councils one agent at a time
  (any mode, owner rule 2026-09-08).
- Never self-promote; escalations go to `state.md` for A (A never executes,
  B never rules).

## Boot order (replay after a reboot — disk survives, order is fixed)

Qwen (`ninfer-work/ninfer_restart.sh`) → `:8000` (CUDA) → `tmux control` (A)
→ `tmux work` (B). A seeds from this file; B seeds from `state.md` + newest
`work_log` lines.