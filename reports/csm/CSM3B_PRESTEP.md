# Wave-2 pre-step (CSM3B_PRESTEP) — 2026-09-08, Terminal B

Council CSM-3b ruled F1 (the ledger sidecar trap) the §9a precondition and the
Ruling-1 31-member roster line a live-probe prerequisite — this pre-step
executes both rulings (R-CSM3B-2 + R-CSM3B-3) as the zero-GPU sequential step
before the 2-parallel Wave-2 subs.

## What this pre-step delivered (five lines — orchestrator side sessions read
receipts alone; R-CSM3B-7 style)

1. **F1 fixed (R-CSM3B-2)**: the pinned-panel sweep ledger pair is now keyed by
   the 8-char panel hash (`sweep_<door>_<hash8>.jsonl` + `.new`,
   `span_recall.sweep_ledger_path`), every ledger row carries
   `panel_hash` + `device` + `commit` stamps, and a row without this panel's
   hash stamp (or an unparseable ledger line) refuses the resume — CLI exits 2
   with a stderr message (Ruling-7 tamper behavior).
2. **Ledger pair migrated + CPU rows dropped**: the 8 CUDA-provenance heldout
   rows moved to `sweep_qa_ec15e0d8.jsonl` (stamped `device=cuda`,
   `commit=78b5cf3`, full heldout panel hash); the 168 CPU-provenance pinned
   rows (the 1200-s incident sidecar) were dropped for provenance purity and
   the unkeyed `sweep_qa.jsonl` / `.new` pair deleted.
3. **168 pinned rows re-probed on CUDA**: `sweep_qa_e3d73720.jsonl` holds 168
   rows, all stamped `device=cuda` / `commit=5c424f3` / pinned panel hash
   `e3d73720…` — 161 HIT · 3 MISS_DOC · 4 MISS_SPAN · 0 ERROR (hit rate 0.9%
   over the full 17,181-row panel; 17,013 probes remain for resume).
4. **Roster door live-probed (R-CSM3B-3)**: the 31-member line (Devils roster,
   `Akane Sawatari | Abilities / Devil Contract`) at `door=roster` serves
   31 of 88 members with **16,231 chars** (pre-fix: 31 members / 0 chars) —
   the Ruling-1 verification spec (31 members / 0 chars → must serve chars) is
   met; yield matches GATE.md:757's recorded 14–16k re-probe, so the N=100
   roster-sanity escalation (CSM-3 Ruling 3) is not triggered.
5. **Not graded here (§9a)**: the interleaved two-panel survival grade (pinned
   sanity → heldout sanity live → assert both keyed ledgers survive) is the
   orchestrator's step — this worker ran the named unit test
   (`test_two_panel_ledgers_survive_interleaved_runs`, 14/14 in
   `tests/test_span_recall.py`), not the live grade. No commits made; the
   orchestrator commits this pre-step.

## 1. F1 fix — what changed (no JJK baseline touched)

`scriptengine/eval/span_recall.py`:
- `sweep_ledger_path(folder, door, panel_hash)` → `sweep_<door>_<hash8>.jsonl`
  (each panel keeps its own pair; the shared per-series name is what let the
  heldout run drop the pinned sidecar's 168 rows).
- `recall(..., stamps=None)`: pinned-branch ledger rows now carry
  `"panel_hash"` (full hash, the tamper guard) + `**stamps`
  (`device`, `commit`); a prior/sidecar row whose `panel_hash` differs from
  the panel being resumed (or is missing) raises `SpanRecallError`.
- `_read_jsonl` is strict: an unparseable ledger line raises `SpanRecallError`
  (refuse the resume) instead of a raw traceback.

`scriptengine/cli.py` (sweep branch only; the legacy `--probe` path and the
JJK standing-gate call shapes are byte-identical):
- `rows_path = impl.sweep_ledger_path(folder, door, panel_hash)`.
- `_sweep_stamps()`: `device` from `GET /health` (the same `:8000` the probes
  hit), `commit` from `git rev-parse --short HEAD`; both fall back to
  `unknown` rather than blocking the sweep.
- `impl.SpanRecallError` in the sweep branch → stderr message + `Exit(2)`
  (Ruling-7 tamper: corrupted/foreign ledger refuses the resume).

## 2. Ledger migration (offline, integrity-checked before any deletion)

| from (pre-fix, shared name) | to (keyed) | rows | stamps |
|---|---|---|---|
| `sweep_qa.jsonl` (8 heldout rows, CUDA) | `sweep_qa_ec15e0d8.jsonl` | 8 | `panel_hash=ec15e0d8772b8b54…`, `device=cuda`, `commit=78b5cf3` (tree under which the ledger was recorded, ~18:22–18:24 probes) |
| `sweep_qa.jsonl.new` (168 pinned rows, CPU — 1200-s incident) | *dropped* | 168 | — (provenance purity, R-CSM3B-2(d)) |
| — (created by the re-probe) | `sweep_qa_e3d73720.jsonl` | 168 | `panel_hash=e3d737205cd07245…`, `device=cuda`, `commit=5c424f3` (HEAD at probe time; working tree carried the uncommitted F1 edits) |

Integrity checks before deletion: pinned hash recompute `e3d737205cd07245…`
matches the pin's stored hash; heldout 200-row list hash `ec15e0d8772b8b54…`
matches CSM3B_GATES §6; the 168 dropped rows' `(title, sentence)` set equals
exactly the first 168 pinned-panel lines in panel order (so `--sanity 168`
re-probes precisely those rows).

## 3. 168-row re-probe on CUDA `:8000` (pid 103425, device cuda)

Command (single bounded run, well under the 15-min cap; progress printed at
100/168):

```
scriptengine/.venv/bin/python -m scriptengine.cli span-recall \
  --series csm --panel reports/csm/panel_csm.json --door qa --sanity 168
```

- panel hash echoed `e3d737205cd07245…` (matches the pin; no exit-1 mismatch)
- probes done 168 · panel size (denominator) 17,181
- **served the line 161 (0.9%)** · page not retrieved 3 · page retrieved, line
  absent 4 · truncated 0 · errors 0
- rc=0 (no dead-door halt); 17,013 probes remain — resume with the same command
- ledger `reports/span-recall/csm/sweep_qa_e3d73720.jsonl`: 168 rows, every
  row `device=cuda` + `commit=5c424f3` + `panel_hash=e3d73720…` (verified)

## 4. Roster door live probe (R-CSM3B-3) — raw record

Line (the council's 31-member line is not recorded by sentence in the earlier
receipts; the identification property is "a CSM panel line whose `door=roster`
probe returns 31 members"; the 14–16k-chars re-probe in GATE.md:757 matches
this line exactly):

- panel line: `Akane Sawatari | Abilities / Devil Contract` —
  `"Tail" 尻尾 Shippo: Akane is also able to summon the tail of the Snake Devil.`
- routing: subject `Snake Devil`, basis `Devils`, kind `category`
- **members served 31 / available 88 · 16,231 chars served · truncated=true**
- sweep-shape verdict for the line itself: MISS (the line is not inside a
  member's text — expected; the Ruling-1 property is char delivery, not HIT)
- pre-fix (The Outsider's live probe, COUNCIL_csm-3): same line-shape →
  31 members / **0 chars** → every roster probe structurally MISS_DOC.
  Post-fix: 16,231 chars → the structural failure is gone.
- yield check: 16,231 chars ∈ the 14–16k recorded in GATE.md:757 → not
  low-yield; the N=100 roster-sanity escalation (CSM-3 Ruling 3) is not
  triggered. Raw record: `reports/csm/CSM3B_PRESTEP_ROSTER_PROBE.json`.

## 5. Targeted test (unit level; the live interleaved grade is the orchestrator's)

- `tests/test_span_recall.py`: **14 passed** (13 pre-existing + the named
  `test_two_panel_ledgers_survive_interleaved_runs`: keyed paths coexist under
  interleaved A→B→A runs, per-row `panel_hash` stamps, unstamped row and
  corrupt ledger both refuse the resume). Targeted file only, model-free
  (monkeypatched `_ask` + tmp sqlite), 0.7 s.
- End-to-end acceptance of the migrated heldout ledger through the new code:
  `span-recall --series csm --panel …heldout.json --door qa --sanity 1` →
  resume read the 8 migrated rows (no tamper refusal), probed 1 new row
  (HIT), ledger now 9 rows, rc=0. The 9th row is stamped
  `device=cuda` / `commit=5c424f3` (it is a legitimate sweep continuation).

## 6. `:8000` state (unchanged by this pre-step)

- pid 103425, etime 01:00:47 at receipt time, `started 2026-09-08T12:38:01Z`
  (identical before and after every step of this pre-step)
- `/health`: `ok`, `device=cuda`, embed `BAAI/bge-large-en-v1.5`,
  rerank `BAAI/bge-reranker-v2-m3`, 8 series
- all probes in this pre-step were bounded HTTP clients against that one
  server process; no second model copy was ever in VRAM (one-copy rule held)

## 7. Explicit boundaries

- **Not done here, by §9a**: the live interleaved two-panel survival grade
  (pinned `--sanity` → heldout `--sanity` → assert both keyed ledgers survive)
  is the orchestrator's grading step. This worker fixed, migrated, re-probed,
  and unit-tested; it does not grade its own fix.
- **No commits made** — the orchestrator commits this pre-step (engine +
  ledger + this receipt).
- The JJK standing-gate call shapes and the legacy `--probe` path are
  untouched; JJK baseline is untouched.
## 8. Orchestrator grade (live interleaved two-panel survival, §9a — 2026-09-08, Terminal B)

The orchestrator (not the fixing worker) ran the live grade:

1. Pre-state: `sweep_qa_e3d73720.jsonl` = 168 rows, `sweep_qa_ec15e0d8.jsonl` = 9 rows.
2. `span-recall --series csm --panel reports/csm/panel_csm.json --door qa --sanity 4`
   (pinned) → rc=0, 172 rows.
3. `span-recall --series csm --panel reports/csm/panel_csm.json.heldout.json --door qa --sanity 4`
   (heldout — the run that pre-fix fired the F1 trap: rewrote the shared ledger
   with only its own keys, unlinked the shared sidecar, dropped the pinned rows)
   → rc=0, 13 rows.
4. Assertions (all PASS): pinned 172 = 168 pre-grade rows survived + 4 new;
   heldout 13 = 9 pre-grade rows survived + 4 new; every row in both ledgers
   carries `panel_hash` + `device=cuda` + `commit` stamps. F1 is defused live,
   not just unit-tested. Raw log: `/tmp/prestep_grade.log`.
