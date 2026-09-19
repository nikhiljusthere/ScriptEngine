# D7 window pre-stage record (council #36, D7 re-score)

Pre-staged `2026-09-18 17:32 IST`. One-subagent task: pre-stage everything on
disk, then issue the detached kill-window chain as the final act. Baseline git
HEAD for this window = `20d6da4e` ("CSM D7: derivation leg …"), the
pre-governance-commit tree. After the governance commit below, locate it with
`git log --grep 'council #36 (D7 re-score)'`.

## Verdicts on the pre-checks (chairman.md lines 120–130)

1. **D59 receipts gate** — no contradiction; the on-disk gate receipts are
   green. Proceed.
2. **469-era arithmetic** — verified, with one correction (below): the
   spec's "194/200 ⇒ 6 reds" OOS number anchors to the **git-HEAD census**,
   not the worktree census.
3. **OOS floor** = `d6_flip.py` exit 2 (any green30 flip, or oos200 drop
   ≥ 3 vs the frozen `D6_OOS_PRE.jsonl` = oos200 168G/32R + green30 30/30).
4. **TIERED flag-off inertness** — confirmed by read: flag OFF ⇒ `tier2=[]`
   ⇒ `ordered` is byte-identical to the committed tree (JJK no-op). Folded
   into the flag-off gate run, not proven separately.
5. **argv capture** — done fresh (not a stale pid). See below.

## Corrected census arithmetic (HEAD ≠ worktree)

Both the git-HEAD census and the pre-window worktree census are 486 rows /
469 green, but they are **different compositions**:

| | git HEAD `20d6da4e` (469-era) | worktree (pre-window, floating) |
|---|---|---|
| pool-140 / pool-358 | RED | GREEN |
| pool-149 / pool-252 | GREEN | RED |
| oos200 | 194/200 (6 red) | 195/200 (5 red) |

- **git-HEAD 17 reds** (the D60 canonical list: org-03 D7 + pool-140/358 D7
  + 14 floor) = `abl-pool-140, abl-pool-358, dim-abl-01/02/09,
  dim-arcn-02/03/04/06/08/10, dim-caus-03, dim-org-03, dim-state-02/03/08/09`.
  Its 6 oos200 reds = `state-08, arcn-10, caus-03, pool-358, arcn-02, org-03`
  (pool-358 is in **both** banks; pool-140 is p23-owned, not among the 6 oos
  reds).
- **Counter-flip baseline for every leg = the git-HEAD census** (C6 + pre-check
  #2: "confirm HEAD's census is the 469-era baseline that d6_flip diffs
  against"). Captured to `snapshots/census_head_469.jsonl` via
  `git show HEAD:…` — verified byte-identical to `git show HEAD:…` (469 greens,
  pool-140/358 red, pool-149/252 green). It is stable across the governance
  commit (that commit does not touch the census) and is the same reference
  `d6_flip.py` uses for its "pre".

`d6_flip` dry-run (pre==post==worktree, offline): rc 0; r2g={pool-140,
pool-358}, g2r={pool-149, pool-252}, oos200 168→195 (Δ+27), green30 flips 0.
All 230 OOS ids (200 oos200 + 30 green30) resolve in the census ⇒ no
KeyError risk in `d6_flip`'s `post[rid]` lookup.

## Q2 flag fix (uncommitted, MUST NOT be staged)

`scriptengine/api/context.py` now carries the full uncommitted TIERED+ABILWIDTH
experiment **plus** the 3-line flag gate (Q2): new `_abilwidth_enabled()`
(mirrors `_tiered_enabled`; env `SCRIPTENGINE_ABILWIDTH_RECALL`, default "0",
read on every call) and the ABILWIDTH guard short-circuits on it. Both flags
OFF ⇒ the ABILWIDTH hunk never opens the store and the TIERED hunk yields
`tier2=[]` ⇒ behavior byte-identical to committed `20d6da4e`. `py_compile`
clean. The gate run (flags OFF, deviation (c)) proves the JJK no-op.

## argv capture (fresh) + guards

- pid `1137321` (the live 135k owner-manual Qwen; `ninfer-serve` on
  `--port 18080`, `--max-context 135168 --kv-capacity 143360`), cwd
  `/home/goblin/ninfer-work`. Written to `/tmp/d7_qwen_pid.txt`,
  `/tmp/d7_qwen_argv.txt` (full argv, one line), `/tmp/d7_qwen_cwd.txt`.
- `test -x` on the resolved binary: **OK**. `test -e` on the model path:
  **OK**. (Had either failed: record + STOP, no chain.)

## The three disclosed chain deviations

Verbatim chain body (chairman.md 68–116) + exactly:
- **(a)** bare `python` → `$S/scriptengine/.venv/bin/python` (`$PY`).
- **(b)** bounded liveness guard after the Qwen `kill`: 6×5s SIGTERM window →
  one SIGKILL → 3×5s → else `RECEIPT_KILLFAIL` + `exit 1`.
- **(c)** `unset SCRIPTENGINE_TIERED_RECALL SCRIPTENGINE_ABILWIDTH_RECALL`
  before the four standing gates (the leg loop `export`s them; gates must
  measure committed-tree behavior).

`bash -n` clean. `check_targets.py` `py_compile` clean; smoke run produces the
`PASS/RED <leg>` + `FLOOR <leg>` line contract (the chain greps `^RED`).

## Pass bar + stop conditions (Q4)

- **Leg A** (TIERED=1, ABILWIDTH=0): W ≥ 469, flips ⊇ {arcn-02, arcn-10,
  org-03, state-08}; 0 counter-flips; blind 19/19; d6_flip rc 0.
- **Leg B** (TIERED=0, ABILWIDTH=1): W ≥ 469, flips ⊇ {pool-140, pool-358};
  0 counter-flips; blind 19/19; d6_flip rc 0.
- **Leg C** (both on): W ≥ 469, flips ⊇ union; 0 counter-flips; blind 19/19;
  d6_flip rc 0.
- Floor re-count per leg: which of the 16 Phase-2 floor rows flip (C5 record
  line, printed by `check_targets`).
- Standing gates (flags OFF): pytest **1,331** pin; eval jjk **31/31**;
  span-recall jjk **48,572** offline rc 0 + 400 probes ≥ prior baseline;
  canon opm ≥ **10/16 · 236/236 · 79.0%**.
- **Any leg RED** (missing flip / counter-flip / OOS drop ≥ 3 / green30 flip /
  grader rc≠0) → halt remaining legs; gates still run for the record; restore
  Qwen; receipt = RED + that leg's kill clause (revert hunk / unset flag; no
  post-hoc re-tuning per D59). OOM/restore fail → receipts, owner relaunches.
  Engine code is **never** committed without the owner's word.

## Owner resume path

The chain kills the live 135k this session runs on; the final message may not
be delivered. Resume on `reports/csm/receipts/d7_window/RECEIPT_DONE` +
`/tmp/d7_gpu_chain.log`. If no sentinel within an hour, relaunch the 135k by
hand from `/tmp/d7_qwen_argv.txt` in `/tmp/d7_qwen_cwd.txt`. After issuing the
chain: no poll, no wait, no further action.

## Commit locator

Governance commit `c60f858b` (branch `character-scoped-questions`), message
`council #36 (D7 re-score) record + D7 window chain pre-stage` (16 files).
Find it: `git log --oneline --grep 'council #36 (D7 re-score)'`. This locator
line is appended after the commit (no amend), so it is intentionally
dirty-unstaged; the chain's own receipts stay uncommitted until the owner
decides.