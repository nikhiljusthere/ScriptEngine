# Peer Review 4 — CSM unit-3 sweep fork (council 2026-09-09)

Reviewer weighting: **the option is not actually executable with the on-disk tooling
(panel ledger, resume, sanity gates).** Fresh-context subagent; zero-GPU, read-only,
every shell < 15 s. No file edits.

**Letter mapping** (same as reviews 1–3; the task's `adv_A.md`…`adv_E.md` do not
exist on disk). By deployment order (mtimes 03:48→03:58) + the executor's own header
label `adv_D`:

| letter | file | mtime |
|---|---|---|
| A | `adv_first-principles.md` | 03:48 |
| B | `adv_contrarian.md` | 03:50 |
| C | `adv_outsider.md` | 03:53 |
| D | `adv_executor.md` | 03:56 (self-labels `adv_D`) |
| E | `adv_expansionist.md` | 03:58 |

## The three answers (~195 words, budgeted)

**1. Strongest: D (Executor).** Only one executable against the on-disk tooling:
correct fork (sweep is an HTTP client; 150k ⇒ CPU service ⇒ CUDA sweep
needs the Phase-2-reserved switch), deepest spot-checks (panel 17,181+200, ledger 172,
census 39/60 vs three responses' 49/60), plan-faithful timeline, falsifiable
change-of-mind. Caveat: its `--sanity 472` probes 472 rows, not its stated 300.

**2. Biggest blind spot: D.** First step mis-specified — `--sanity N` probes the first
N *unprobed* rows, so it probes 472, not 300; "4 hours" under-budgets five
engine-class items (each = council + four gates); its change-of-mind target (option
A's mid-phase switch) is plan-forbidden, no plan-faithful alternative (fold into the
planned 100k switch).

**3. What ALL five missed** (code-verified): (a) the exit-3 sanity halt
checks the *merged* count; qa already holds 165 HITs, so a resumed sanity run can
never be zero-hit → the floor cannot catch a door a fix kills. (b) B's pinned 400-row
meter has no CLI mechanism — resume is one-way; re-probing the same 400 needs ledger
deletion or an engine flag (council + four gates). (c) "400-probe gate" is ambiguous
— legacy `--probe 400` (router-mode, no `--door`, never run on CSM) ≠ the qa-door 400.

## Why D, and why its step mis-specified (evidence)

- CLI `span-recall` (scriptengine/cli.py L2028–2250): `--panel` recomputes the panel
  hash from the loaded rows, cross-checks the pin's stored hash (mismatch → exit 1),
  keys the ledger `sweep_<door>_<hash8>.jsonl`; `--sanity N` passes `limit=N` to
  `impl.recall`, whose help says "probe only the first N **unprobed** panel entries"
  (L2059–2063). In `span_recall.py`, resume builds `prior` from the ledger by
  `(title, sentence)`, then `to_run = [p for p in probes if (p[0], p[2]) not in
  prior]`; `if limit: to_run = to_run[:limit]`. With the 172-row qa ledger,
  `--sanity 472` → **472 new probes** (panel rows 173–644), not D's "rows 173–472"
  (300 rows / ~35 min at the ~7.1 s/probe CPU rate; actually ≈ 56 min). B's
  `--sanity 400` (= 400 new probes, "400-row sample") is stated correctly.
- D's "4 hours: serial fix closure over R-1..R-5" contradicts
  `reports/csm/red_list_csm.md` (R-1..R-5 all engine-class; R-4's per-wiki override
  is only the *preferred first attempt*) — each engine change = §3 council trigger +
  four standing gates (JJK-100% invariant, `plan/CSM_WAVE2_RESUME.md` §4). Also
  flagged in reviews 1–3, but D's own timeline still budgets 4 h.

## What all five missed (evidence for the chairman)

**(a) The exit-3 dead-door sanity halt is void on any warm ledger.**
`span_recall.py` pinned branch: after resume-merge, `counts` is recomputed from the
*merged* row set (prior ledger rows + this run's sidecar) and that is what the CLI
returns and checks: `if sanity and run["counts"]["HIT"] == 0: exit 3` (cli.py
L2187–2193). The qa ledger already holds 165 HITs (verified: 172 rows = 165 HIT /
4 MISS_SPAN / 3 MISS_DOC, `reports/span-recall/csm/sweep_qa_e3d73720.jsonl`), so on
any resumed qa sanity run `HIT == 0` is unreachable. Consequence: the council
addendum's "per-door sanity floor" (a dead door must not burn the exhaustive sweep)
only protects *cold* ledgers (roster/narrative first runs). Once a serial fix kills
a door — the exact scenario option C's per-fix graded re-sweeps create — the sanity
gate will not halt; a full 17k sweep against a dead door is possible. A one-line fix
(check this-run counts, not merged) is an engine change → council + four gates;
cheaper: rule that a post-fix re-sweep must confirm ≥1 HIT in its *new* rows.

**(b) B's pinned 400-row halt meter (review_2's "fix the meter") has no on-disk
mechanism.** Resume is one-way: `to_run` skips every row already in the ledger
(only ERROR rows re-probe). So "re-probe the fixed 400-row subset after each fix"
cannot be expressed in the CLI: a second `--sanity 400` probes rows 573–972, not the
same 400. Options: (i) delete/truncate the ledger and re-run `--sanity 400` (re-probes
panel rows 1–400 each time; cumulative state recoverable from git, the error path says
"restore the ledger from git"); or (ii) add a `--reprobe` flag (engine change →
council + four gates). The council should rule which, or B's meter is unexecutable as
written. Side note: a cumulative ledger also mixes commit vintages (rows stamped
`device=cuda, commit=5c424f3` today; a CPU re-run stamps `device=cpu` + new commit —
by design per R-CSM3B-2, but "miss-count regression" then measures against a
mixed-vintage baseline).

**(c) "The 400-probe standing gate" is ambiguous in the tooling and the options text.**
Legacy `--probe 400` (the standing JJK gate) is a seed-7 sample of the *current*
corpus, router-mode only (no `--door` parameter on that path), appends to
`recall_verbatim.jsonl` without dedupe or resume, and `--probe` is ignored whenever
`--panel` is given. No `recall_*.jsonl` exists under `reports/span-recall/csm/` —
the CSM 400-probe gate has never run. The qa-door "400" (`--panel --sanity 400`) is a
different probeset (400 *panel* rows, door-forced, keyed ledger). Job spec unit 3
says "Wave-1 pinned panel + the 400-probe standing gate" — that is two probesets;
none of the five responses (nor the brief) pins which "400-probe gate" iteration 1
delivers. B implicitly chose the panel reading; the executor D and the brief's rates
("35–40 min CPU") conflate them.

## Verified on disk (this review's own checks)

| Claim | Verdict | Evidence |
|---|---|---|
| Panel 17,181 sweep + 200 held-out, seed 42, hash `e3d737205cd0…` | ✓ | `reports/csm/panel_csm.json` (python count) |
| qa ledger 172 rows = 165 HIT / 4 MISS_SPAN / 3 MISS_DOC; rows carry `panel_hash` + `device` + `commit` (R-CSM3B-2 stamps; first row: `device=cuda, commit=5c424f3`); 17,009 remain | ✓ | `reports/span-recall/csm/sweep_qa_e3d73720.jsonl` (172 lines; head + Counter) |
| Held-out ledger exists, 13 rows (outsider's "never swept" is overstrong, as review_1 noted) | ✓ | `reports/span-recall/csm/sweep_qa_ec15e0d8.jsonl` |
| CSM tier-0 clean → no exit-2 trap on sweep runs | ✓ (checked; not a finding) | `reports/span-recall/csm/index_misses.jsonl` = 0 lines |
| Census 39/60 MECH_GREEN / 21 MECH_RED (work_log's "49/60" is a digit error; three responses repeated it) | ✓ | `reports/csm/census_dimensions_csm_results.jsonl` (Counter) |
| `--sanity` = first N *unprobed* rows; resume/merge/limit as described; merged-count return | ✓ | `scriptengine/eval/span_recall.py` (pinned branch), `scriptengine/cli.py` L2059–2063, L2177–2193 |
| `--probe` ignored with `--panel`; legacy path router-mode, append, no resume/door | ✓ | `scriptengine/cli.py` (L2044–2054 help; probe branch L2205–2235) |
| Stamps = service `/health` device + git short commit, "unknown" fallback | ✓ | `scriptengine/cli.py` `_sweep_stamps()` L1998–2025 |
| Unit-3 spec: "Batch sweep (Wave-1 pinned panel + the 400-probe standing gate, on CUDA, one-copy ordering) … Halt: miss-count regression or two no-reduction iterations → council" | ✓ | `reports/master-work/CSM_WAVE2_JOB.md` L30–36 |
| R-CSM3B-2 = re-key ledger by 8-char panel hash + device/commit stamps | ✓ | `reports/csm/COUNCIL_csm-3b.md` (ruling 2 + "The One Thing to Do First") |
| `phase_status.txt` / 150k state | not re-checked this review (reviews 1–3 cite `work_log.md` L51: 150k pid 4348, 5,381 MiB free, `:8000` CPU pid 4510; `phase_status.txt` empty) | — |

## Residual risk / note to the chairman

- The letter mapping is inferred (task paths `adv_A.md`…`adv_E.md` absent); it is
  consistent across reviews 1–3 and the executor's self-label, so persona names are
  the safe reference.
- Findings (a) and (b) are code-read conclusions (zero-GPU, no sweep run). They are
  deterministic from the shown code paths; a 5-line throwaway harness could confirm
  the merged-count behavior, but it needs the `:8000` service and is out of this
  review's zero-GPU/read-only budget.
- If the council adopts D's plan as the execution path, attach: corrected first step
  (`--sanity 300` if the intent is 300 new probes; `--sanity 472` if 472), a
  per-fix rule "new rows must show ≥1 HIT or halt", and the ruling on the B-meter
  mechanism (ledger-delete re-probe vs `--reprobe` engine flag).