# Peer review 3/5 — CSM unit-3 sweep device fork (council 2026-09-09)

Reviewer weighting: failure mode "the option conflicts with the 2-phase plan or the
JJK-100% invariant and the council did not notice." Zero-GPU, read-only; every
shell < 15 s.

**Letter mapping (state for the chairman).** The task pointed at `adv_A.md`…`adv_E.md`,
which do not exist on disk; the five responses are the role-named files. Mapping
inferred from deployment order (file mtimes 03:48→03:58) and confirmed by the
executor file's own header `# Executor (adv_D)`:

| letter | file | self-label |
|---|---|---|
| A | `adv_first-principles.md` (03:48) | — |
| B | `adv_contrarian.md` (03:50) | — |
| C | `adv_outsider.md` (03:53) | — |
| D | `adv_executor.md` (03:56) | `adv_D` (in header) |
| E | `adv_expansionist.md` (03:58) | — |

Letters below are only reliable if the council's lettering followed deployment
order; role names are unambiguous either way.

## The three answers (word-budgeted)

**1. Strongest: D (Executor).** Only plan-faithful and executable response: option C as
the plan's own path (sweep is HTTP-only; not doable on CUDA at 150k), 1 switch
instead of 3, concrete first step + verification (39/60 not 49/60; 172-row
ledger), explicit change-of-mind (thin queue → option A for pre-extraction
baseline). B (Contrarian) is the sharpest plan-fidelity critic but under-costs
the gate burden.

**2. Biggest blind spot: C (Outsider).** Its first choice (400-probe gate in a
150k in-process CUDA one-copy window) is infeasible: `span_recall.py:44`
hardcodes the HTTP `:8000` base, and at 150k the service is CPU-only — no
in-process CUDA path exists for the gate; making one = engine change (council
+ four gates) that C missed.

**3. What ALL five missed:** the JJK-100% invariant cost of the closure loop —
per `red_list_csm.md`, R-1..R-5 are 4–5 **engine** changes → 4–5 × (council +
four gates); at 150k those gates cannot run "on CUDA, one-copy ordering"
(RESUME §4): the 400-probe is HTTP-only → CPU `:8000` (the "up for HTTP gates"
relief is cited by none). Also unconsidered: **A′** — one 100k switch, no
switch-back: `PHASE_A_COMPLETE` becomes a no-op and "gates on CUDA" is truly
satisfied (1 switch, not 3).

## Verified on disk (evidence for the chairman)

- **Census 39/60, 21 red — the 49/60 on record is a digit transposition.**
  `reports/csm/census_dimensions_csm_results.jsonl` (raw, mtime 03-09 03:39)
  parses to MECH_GREEN 39 / MECH_RED 21 (python count). `work_log.md` 03:43
  line says "49/60 mech-green" while its *own* per-dim list (arc 2/10, abl 4/10,
  state 5/10 green + caus 9/10 + appr 9/10) sums to 39 green / 21 red. The
  brief's reds list (11) omits the appearance/causality reds (1+1) — the 5.4
  extraction gate is more LIVE than the question text says. B/C/D/E caught it;
  A (first-principles) repeats 49/60.
- **The 168-probe datapoint is CUDA@100k, not CPU.**
  `CSM3B_PRESTEP.md` §3: "168-row re-probe on CUDA `:8000` (pid 103425,
  device cuda)", all rows stamped `device=cuda`; the 168 CPU rows (the "1200-s
  incident") were dropped for provenance. The pre-step ran 09-08 18:22, after
  the 150k dial at 17:00 (`work_log.md` L18, free 5,182 MiB → `:8000` CPU);
  the log's 100k state at 23:00 (L43) shows the plan's "even smaller context"
  dial-down (L38) had been applied, so the 18:22 CUDA `:8000` re-probe ran
  under 100k. So the brief's fact #3 misattributes the rate: the CPU rate
  (168/1200 s) comes only from the dropped incident; the CUDA rate is "well
  under the 15-min cap" (duration unrecorded). B (Contrarian) caught this; the
  "35–40 min CPU 400-probe" figure is a projection, never measured on CPU.
- **Panel = 17,181 sweep + 200 held-out** (`panel_csm.json`: `panel` len 17,181,
  `held_out` len 200, seed 42, hash `e3d73720…`, verified). The brief's
  "17,381-row panel" double-counts held-out rows that live in the separate
  `sweep_qa_ec15e0d8` ledger (C/Outsider caught; others did not).
- **Ledger 172 rows = 165 HIT / 3 MISS_DOC / 4 MISS_SPAN** (`sweep_qa_e3d73720.jsonl`);
  17,009 remain. No roster/narrative door ledgers exist yet (`ls
  reports/span-recall/csm/`).
- **R-1..R-5 are engine changes** (`red_list_csm.md`, "Notes for the §9a
  executor"): "R-1/R-2/R-3/R-5 are **engine** changes (they trigger the §3
  council + the JJK-100% four-gate re-run); R-4 is engine too, though a
  per-wiki override … is the *preferred* first attempt." So the unit-3 loop is
  4–5 engine changes, each = council + four-gate re-run. D's "per-wiki override
  first" only holds for R-4.
- **span-recall is HTTP-only** (`scriptengine/eval/span_recall.py:44`:
  `BASE = "http://127.0.0.1:8000"`, no override, no in-process mode;
  `CSM3B_PRESTEP.md` §6: "all probes … bounded HTTP clients against that one
  server process"). In-process CUDA one-copy (the census pattern,
  `work_log.md` L55) is available to `tools/csm/*` census tools and pytest/eval
  model loads — not to the 400-probe gate or the panel sweep.
- **The 150k device regime** (`CSM_2PHASE_PLAN.md` L12-13, L34-40;
  `CSM_WAVE2_RESUME.md` §2 L28-30): no CPU shell > 15 s; `:8000` stays CPU
  *service role* only; job model loads in-process CUDA one-copy, "server down
  for pytest/eval, **up for HTTP gates**"; LONG > 300 s runs flagged for A's
  judgment (`work_log.md` L52; job-spec bootstrap B line). The sweep/gate at
  150k therefore has exactly two device paths: CPU `:8000` (A-flagged, 35–40 min
  projected) or a 100k switch.
- **Invariant wording** (`CSM_WAVE2_RESUME.md` §4): "After **every engine
  change** re-run all four (on CUDA, one-copy ordering)" — at 150k the JJK
  400-probe leg cannot run "on CUDA" (HTTP-only → CPU service); the plan's
  only relief is §2's "up for HTTP gates." Unexamined by all five responses.
- **Phase 2 already anticipates everything** (`CSM_2PHASE_PLAN.md` Phase-2
  §1-3): CSM-4 = D5 exhaustive tier-1 × 3 doors (~51 GPU-h) + D6 extraction
  "only on red census" → option C's deferral of the panel is plan-consistent;
  advisor E's (Expansionist) pre-extraction-baseline promotion is compatible
  (CSM-4 resumes the keyed ledger, R-CSM3B-2).
- **`phase_status.txt` is empty** — no `PHASE_A_COMPLETE` yet; the 100k switch
  has not started. 150k confirmed live (`work_log.md` L51: qwen 150k pid 4348,
  free 5,381 MiB; `:8000` = CPU service pid 4510).

## Recommended ruling shape (for the chairman, not a vote)

Pick option C's deferral (all five converge on it) **plus** two plan-fidelity
rulings the council has not yet made: (1) explicitly adopt the RESUME §2 "up
for HTTP gates" relief so the JJK 400-probe leg of the four gates runs on the
CPU service at 150k under A's flag — otherwise the invariant's "on CUDA"
wording forces 100k windows per engine change, which *is* the reserved
switching pattern; (2) price the loop: 4–5 × (council + four gates) with :8000
stop/restart cycles — this, not the sweep's 5–10 h, is unit 3's wall-clock
dominant cost. Keep A′ (one 100k switch, no switch-back) on the table as the
change-of-mind target if the miss queue comes back thin (advisor D's own
trigger).