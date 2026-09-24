# JEV measurement receipts — council #38 (2026-09-24, amend #38-7)

CPU-side assignment from the P2-scope lock (not a window leg). Per
`plan/CSM_JEV_ACCEL.md` § Measurement protocol: pruner decision logs
(every judgment, trim, error; `hook_error` lines = fail-open) + NInfer
`requests.jsonl` prompt tokens + cache hits, vs the R-5 baseline
(3.76M prompt / 110k output / 6.1% cache hit, the pre-pruner compaction
measurement).

## NInfer cost — council #38 window

Window: 2026-09-24 04:49:26 → 05:34:36 +0530 (framed_question.md →
chairman.md mtime; single server instance `serve-4332`, pid 4332,
:18080). Traffic = the 11 council subagent sessions (5 advisors, 5
reviewers incl. the R4 retry, 1 chairman) + the directing session's own
turns inside the window (the subagents ran strictly sequentially; the
directing session is idle while they run, so no concurrent mix-up of
windows, only interleaved turns).

| metric | council #38 window | R-5 baseline |
|---|---|---|
| requests | 175 | — |
| prompt tokens | 10,464,019 (≈ 10.46M) | 3.76M |
| output tokens | 336,090 (≈ 336k) | 110k |
| prefix-cache hit | 7,090,433 / 10,464,019 = **67.76%** | 6.1% |

Reading: with the context-pruner + NInfer prefix reuse, the per-council
cache-hit rate is ~11× the R-5 baseline (67.76% vs 6.1%). Prompt volume
is ~2.8× the baseline — this council is 11 subagent sessions vs the
smaller R-5 session, so the comparison is directional, not like-for-like;
the cache-hit delta is the JEV win.

## Pruner decision logs

`~/.config/opencode/jev-context-pruner/decisions.jsonl` — 12 lines:
`setup` × 10, `apply` × 2, **`hook_error` × 0** (no fail-open; nothing
left verbatim by error).

`~/.config/opencode/jev-bash-pruner/decisions.jsonl` — 68 lines:
`setup` × 5, `trimmed` × 2, `no_scoring_capacity` × 61, **`hook_error` × 0**.

This session (`ses_f2f7bfe8cffegkgz0l6AQllWeV`):
- context-pruner `apply` 2026-09-24T00:07:30Z: 332,192 chars →
  **6 results dropped, 0 calls dropped**, 40.1 s scoring pass.
- bash-pruner: 61 `no_scoring_capacity` events 2026-09-23T23:05:28Z →
  2026-09-24T00:06:29Z (all this session): the `:8018` fast-lane gateway
  had no scoring capacity for that ~1 h interval, so the bash pruner
  **failed open by design** (no mutation, logged). No trims landed in
  that window; the 2 `trimmed` events are from earlier (pre-window)
  traffic.

## Standing notes

- Fast lane (`:8018` decider-0.8b, CPU) was the scoring path throughout;
  the deep lane (:18080) served the council subagents (its 503-by-design
  quiet-window behavior is unchanged — the deep lane is busy while
  opencode runs, so subagent traffic rode on it in the quiet gaps).
- Cadence: repeat this receipt after every council through the campaign's
  close (amend #38-7).