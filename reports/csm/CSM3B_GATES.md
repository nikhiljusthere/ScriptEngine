# CSM-3b gate cycle (CSM3B_GATES) — 2026-09-08, Terminal B

## What this wave delivered (five lines — Phase-2 side sessions read receipts alone; R-CSM3B-7)

1. **Scope**: CSM-3b = COUNCIL_csm-3 Rulings 1+7 (roster-door fix + panel-hash
   enforcement) landed and verified, plus the full standing-gate cycle re-run on
   the 1,254 suite (one-copy ordering, CUDA).
2. **R1+R7 landed**: engine `f93d396` (roster-door `served_text` flattens
   members/passages; roster-shaped test) + close-out `bc73795` (panel-hash
   recompute/enforce, tampered pin → exit 1; bare-list held-out load;
   `tools/csm/panel_heldout.py`).
3. **Gates = re-baseline**: pytest 1,254 · eval jjk 31/31 · span-recall jjk
   48,572/48,572 offline + 390/400 live · canon opm 10/16 · 236/236 · 79.0% —
   all exactly the 2026-09-08 15:22–15:26 re-baseline; zero new fails.
4. **Seed bank (39 questions, canon-run shaped — `canon-run --series csm`, no
   eval-harness gold by design)**: 11/19 exact · 138/148 canon = CSM-1b
   post-fix baseline; G-CSM-1 (csm-set-14 recall 0/5) + G-CSM-2 (csm-fact-06
   empty qa bundle) persist, scheduled CSM-4/5.
5. **Open items → §9a preconditions (council CSM-3b, Rulings 2/3)**: F1 the
   ledger sidecar trap (ledger pair shared per series, not per panel — a
   held-out run dropped 168 pinned rows from disk) gets fixed as the zero-GPU
   sequential Wave-2 pre-step, and the Ruling-1 31-member roster line needs a
   live `door=roster` probe — both land before §9a iteration 1 / the Phase-2
   400-probe gate; the orchestrator (never the fixing subagent) grades them.

**Context (one-copy ordering).** Stop `:8000` → in-process gates on CUDA (pytest, eval jjk) →
restart `:8000` on CUDA (pid 103425, started 18:08:01 per its `/health` `started` field) →
HTTP gates (span-recall jjk probe-400, canon opm) + seed bank via `canon-run`. Worker 2
(gates-bank-cuda) executed all gate commands and left the raw logs in `/tmp`; its fork froze
~18:20 (B_NOTE, `reports/csm/interventions.jsonl` @ 12:28:44Z: "fork frozen 333921 B, last
event ~18:20, no live shell"). The orchestrator re-ran the heldout sanity check (5c, ~18:22–18:24)
and this receipt is completed by worker 3 from the raw logs. All numbers below are cited to
log paths + wall time; no gate was re-executed for this receipt.

## 1. pytest full — in-process CUDA, 18:01

`1,254 passed in 188.74s (0:03:08)`, rc=0. Log: `/tmp/pytest_csm3b.log` (mtime 18:01).
Matches the 1,254 suite baseline (1,249 re-baseline + 4 CSM-3 + 1 CSM-3b roster-door test,
`f93d396` + COUNCIL_csm-3 Ruling 1).

**Deviation:** two false-positive monitor kills under the OLD rule-2 — pid 98909 @16 s and
pid 100500 @20 s. Rule-2 checked the bash *wrapper*'s fds (which never hold nvidia fds;
cold CUDA init >15 s looks CPU-like), not the python child. Control A ruled 18:00:06
(`reports/csm/interventions.jsonl`, A_JUDGMENT) and replaced rule-2: kill only provably-CPU
cases; default-device in-process = assumed CUDA, 300 s LONG flag. The 3rd attempt ran to
completion (the 18:01 log above).

## 2. eval --series jjk — in-process CUDA, 18:03

`31/31 (100%)`, rc=0, 46 s. Log: `/tmp/eval_jjk_csm3b.log` (mtime 18:03); the benign
`QdrantClient.__del__` shutdown traceback (`ImportError: sys.meta_path is None, Python is
likely shutting down`) is interpreter-teardown noise, not a failure. Matches the
re-baseline 31/31 (`reports/csm/GATE_REBASELINE_2.md`, 15:22–15:23).

## 3. Seed bank (39 questions) — `canon-run --series csm` (correct runner), 18:15

The task text's `eval --series csm` is a misroute (deviation a below). The measuring runner
is `canon-run`: `scriptengine/eval/canon_gold.py:3` — "The bank lives in
`questions/<series>.json`", loaded via `scriptengine.eval.questions.load_all()`
(`canon_gold.py:42`). The bank: `questions/csm.json` — dict, 7 keys
(`questions`, `retired`, `revid_stamp`, `revids`, `series`, `updated`, `wiki`), 39 active
questions + 1 retired, revid-stamped (fetched 2026-09-08) — the CSM-1 revid-stamped bank.

Results (`/tmp/canon_csm_csm3b.log`, mtime 18:15, 7 s, rc=0):

| metric | value |
|---|---|
| answered exactly right | 11/19 (57.9%) |
| canon items recovered | 138/148 (93.2%) |
| precision, closed sets | 81.4% over 19/21 |
| questions at recall 0 | 2/21 |
| confident and wrong | 0 |
| fact answers present in the bundle | 17/18 |

Cross-checked **identical** to the CSM-1b post-fix baseline (`reports/2026-09-08-0752/REPORT.md`,
0746/0752 runs: 11/19, 138/148, 81.4%, 2/21, 0, 17/18) → **NO NEW FAILS**. The failing
questions are the known recorded engine gaps G-CSM-1 (csm-set-14, recall 0/5) and G-CSM-2
(csm-fact-06, qa bundle empty), documented in `reports/csm/COUNCIL_csm-1b-2.md`; scheduled
CSM-4/CSM-5.

## 4. span-recall --series jjk --probe 400 — HTTP vs CUDA :8000, 18:11

Offline tier-0: 48,572/48,572 sentences present in a chunk, 0 unreachable, coverage 100.0000%,
rc=0 (unchanged). Live probe: 390/400 (97.5%) — 6 page-not-retrieved, 4
page-retrieved-line-absent, 0 truncated, 0 errors; 195 s; rc=0.
Log: `/tmp/spanrec_jjk_csm3b.log` (mtime 18:11). Identical to the re-baseline
(`reports/csm/GATE_REBASELINE_2.md` line 20: 390/400, 6 MISS_DOC / 4 MISS_SPAN / 0 / 0).

## 5. canon-run --series opm --skip-eval — HTTP, 18:13

10/16 (62.5%) exact, 236/236 (100.0%) canon, precision 79.0% over 16/19 closed sets,
0/19 at recall 0, 0 confident-wrong, fact answers 20/20; 11 s; rc=0.
Log: `/tmp/canon_opm_csm3b.log` (mtime 18:13); sidecar report
`reports/2026-09-08-1242/REPORT.md`. Identical to the re-baseline
(`GATE_REBASELINE_2.md` line 21: 10/16, 236/236, 79.0%).

## 6. Heldout live sanity (Ruling-7 delegated tail) — orchestrator re-run ~18:22–18:24

`python -m scriptengine.cli span-recall --series csm --panel reports/csm/panel_csm.json.heldout.json --sanity 4`
→ rc=0; **4/4 HIT this run (8/8 cumulative** in `reports/span-recall/csm/sweep_qa.jsonl`,
including worker 1's earlier 4); 0 not-retrieved / 0 absent / 0 truncated / 0 errors;
panel-hash header `ec15e0d8772b8b54…`; csm tier-0 17,382/17,382, 0 unreachable.
Log: `/tmp/spanrec_csm_heldout_csm3b_final.log` (mtime 18:24). Proves the bare-list heldout
side file loads live → **Ruling-7 green**.

## 7. Service state (left running as instructed)

`:8000` UP, device cuda, pid 103425 (etime 16:32 @18:24; started 18:08:01 per `/health`),
embed `BAAI/bge-large-en-v1.5` + rerank `BAAI/bge-reranker-v2-m3` loaded; Qwen `:18080`
alive (HTTP 200).

## Deviations / notes

**(a) Task-text 3c misroute.** `eval --series csm` fails rc=1 — "No gold set for 'csm'.
Expected `scriptengine/eval/gold_csm.json`" (`/tmp/eval_csm_csm3b.log`, 1 s).
`scriptengine/eval/gold_csm.json` never existed in git
(`git log --oneline -- scriptengine/eval/gold_csm.json` is empty). The bank is not in
eval-gold shape; creating `gold_csm.json` would be an engine design change — deliberately
not created; if the campaign wants an eval-gold-format csm bank, that is a council/CSM-4
item. The bank was measured via the correct runner (`canon-run --series csm`, §3).

**(b) Two false-positive monitor kills + A's 18:00:06 ruling** — see §1.

**(c)** Workflow parent timeout cut worker 2 mid-analysis (~18:20 fork freeze); the
orchestrator completed 5c (heldout sanity) and worker 3 completed this receipt.

**(d) LEDGER SIDECAR TRAP (new finding, for the council — F-CSM-3b-1).** The csm
pinned-panel ledger pair (`reports/span-recall/csm/sweep_qa.jsonl` + `.new`) is shared
*per series*, not per panel. The 18:24 sanity-4 run (heldout panel) read the 168-row
`.new` sidecar (pinned-sweep progress from the 1200-s incident, committed @ `bc73795`)
into `prior`, merged only heldout-panel keys into `sweep_qa.jsonl` (8 rows: 4 prior +
4 new), then unlinked the sidecar per the designed merge contract
(`scriptengine/eval/span_recall.py:383–452`, `sidecar.unlink` @452). Result:
`sweep_qa.jsonl.new` was deleted from disk; the 168 pinned-sweep rows survive only in git
(`bc73795`). Phase-2 pinned-sweep resume must either restore
`git show bc73795:reports/span-recall/csm/sweep_qa.jsonl.new` (restored in this commit's
companion paths) or re-probe those 168 rows; the proper fix (ledger keyed by panel-hash)
is recorded as finding **F-CSM-3b-1** for the CSM-3b council.

## Verdict

All four standing gates identical to the 2026-09-08 15:22–15:26 re-baseline (pytest 1,254;
eval jjk 31/31; span-recall jjk 48,572/48,572 offline + 390/400 live; canon opm 10/16 ·
236/236 · 79.0%). Seed bank: no new FAILs (G-CSM-1/G-CSM-2 persist, scheduled CSM-4/5).
Sanity-4: 4/4 HIT (8/8 cumulative). **CSM-3b gate cycle COMPLETE.**