# SWITCHPOINT — the resume file for Qwen mode switches

pi's model is the Qwen server: while the server is reloading the agent has no
model, and after reopening pi the *transcript* may be discarded (small
contexts compact fast). So everything needed to continue must live here, on
disk, **before** `qwen-switch.sh` runs. Fill the hand-written section before
every switch; `qwen-switch.sh` appends machine lines to the switch log — never
edit those.

## Current position (hand-written — fill BEFORE every switch)

- mode: **262k + `--vision` (this session started under it, 2026-09-08; the
  old stuck 100k CSM session 01a07cab is retired/trashed — everything it held
  is on disk)** → CSM campaign RESUMED. Items 1–2 are zero-GPU disk work,
  fine under 262k. Item 4 (D5 exhaustive sweep, ~51 GPU-h) goes through the
  gpu-handoff chain (`docs/ops/PC_GPU_HANDOFF.md` + `tools/master-work/
gpu-handoff.sh`) in a 100k-mode side session — never block this session on
  the GPU, never `--api` on a chain switch.
- git: `064093e` (csm: CSM-1 — revid-stamp the seed bank + inventory) on the
  campaign trail `281fe2e` (wave-0) → `4e7c304` → `8f8ffdb` (council verdict)
  → `6a87479` (overflow-handoff checkpoint) → `064093e`. Untracked
  (master-work, not CSM area): `plan/AB_DEPLOYMENT.md`,
  `reports/master-work/{GPU_LIVE1_REPORT.md,STOP,gpu_handoff_state/}`;
  modified by the master-work process (do not commit from the CSM session):
  `plan/decisions.md`, `plan/state.md`, `reports/master-work/a_wake_log.md`.
- trunk/excursion address (drift_log §4): **X2 CLOSED** (JJK D6 done, D11) ·
  trunk P6 not-started by owner directive (JJK-only halt). **Active: the CSM
  (Chainsaw Man) campaign** (owner-authorized 2026-09-07): the 8-item plan in
  `reports/csm/COUNCIL_csm-campaign.md` is the campaign plan; CSM-1 DONE (this
  checkpoint); **CSM-2 is next**.
- work explanation (what's done, what's in flight, the exact next step):
  - **CSM-1 DONE (`064093e`)** — inventory + revid-stamp, zero new
    questions: `questions/csm.json` 39/39 active + `questions/
    _csm_relations.json` 11/11 stamped `source_revid` (18 distinct wiki
    source pages pinned, 0 unpinnable; the 1 retired entry has no `sources`
    key → null, documented; `csm-set-02`'s cbr.com source unpinnable);
    `reports/csm/CSM1_INVENTORY.md` committed (counts, revid table, the 20
    declared rosters, verification output, incident receipt). Raw receipts
    only. The tool's first run wiped the questions lists (tuple-unpack swap)
    — restored from git, fixed, recorded in the inventory's Incident section;
    same fix batch: Fandom-403 UA + CRLF/indent whole-file churn.
  - Standing four gates NOT re-run for CSM-1: no engine/store change (question
    files + a CSM-only tool in `tools/csm/`); JJK baseline untouched.
  - **Next: CSM-2** (council item 2): classify all 537 CSM pages / 12 page
    types (incl. the 14 `unknown`s) in `series/csm/overrides.yaml` —
    in-scope / excluded-in-writing + archetype (one reusable schema); that
    list IS 5.1's scope list + §6's archetype mapping. `tools/
    coverage_report.py` reads scope from overrides (the JJK-hardcoded
    `IN_SCOPE_TYPES` retired), exits non-zero on an unclassified `page_type`.
    Done-criteria: csm denominator 537 / 0 unclassified / 0 unknown; `--series
    jjk` output byte-identical; non-zero-exit path + a CSM scope test in
    `tests/`; pytest green. No series name in any `.py`.
  - Council cadence: fires after CSM-2 (2 completed todos) → `reports/csm/
    COUNCIL_csm-1-2.md` (5 advisors in parallel, then 5 peers; raw receipts).
- open questions / risks:
  - GPU at check time: Qwen 262k owns the card (util 100%), `:8000` on CPU
    (headroom 1,604 MiB < 6 GiB → CPU is correct; do not co-locate). CSM-2 is
    zero-GPU, so no action needed.
  - The master-work A/B deploy is in flight on this box (the untracked /
    modified files above); CSM commits stay CSM-area paths only, and the
    master-work files are managed by that process.
- first action on resume: **start CSM-2** from its council item 2 scope +
  done-criteria (`reports/csm/COUNCIL_csm-campaign.md`); read-first records:
  `reports/csm/CSM1_INVENTORY.md` (stamped bank), `reports/csm/
  CSM1B_BANK_VALIDATION.md` (CSM-1b state: gold fixes, gaps G-CSM-1..4),
  `reports/csm/GATE_REBASELINE.md` (current gate numbers). Todos CSM-1..8 are
  recreated from the council plan if the panel was lost (CSM-1 + CSM-1b =
  done; CSM-2 next).
- done this turn (2026-09-08, gpu-live2 RESUME): read C's report (all 4 gates
  PASS on CUDA), `:8000` verified on CPU, chain state clean (no STALLED, one
  typed resume), C transcript trashed, CLAUDE.md + gates-skill baselines
  re-baselined with run timestamps + committed. **Next: CSM-2** (page-type
  classification + scoreboard generalization, council item 2 — grounding data
  in the CSM-1b todo note + `reports/csm/`).
- done this turn (2026-09-08, CSM-1, fresh 262k+vision session): CSM-1
  DONE + committed `064093e` (stamped bank + inventory artifact, CSM-area
  paths only). Tool fixes committed with it: Fandom-403 UA, tuple-swap
  data-loss (restored from git, then fixed), CRLF/indent churn. Coverage
  regenerated (JJK 893/987, in-scope remainder 0 — date-line only change).
  Standing gates not re-run: CSM-1 made no engine/store change. Next: CSM-2
  (page-type classification + scoreboard generalization, council item 2);
  council fires after CSM-2 (cadence: every 2–3 todos).
- done this turn (2026-09-07 23:3x, CSM Wave-0 + campaign start): CSM
  grounded (537 pages, 5,081 facts, 11 types, audit 5/5 PASS, span-recall
  rc=2 with 439 unreachable) → diagnosed (pre-G15 index + Notes/References
  divergence) → fixed (re-index + `content_sections`) → verified (0
  unreachable, 100.0000%; all standing gates green on CUDA, 1,242 pytest).
  Two new owner rules persisted in CLAUDE.md (GPU >15 min; 10–15 s polling
  + explicit timeout). CSM campaign todos created (#11–#15). Council on
  the CSM plan launched. Committed `281fe2e`.

## gpu-live2 handoff (2026-09-08 — A=01a07ff0 → chain → C on 100k → A resume)

**DONE 13:57 local — chain complete (state=done, no STALLED; C transcript
trashed after the report was read; `:8000` back on CPU, pid 62983).** All 4
gates PASS on CUDA (receipts `reports/csm/GATE_REBASELINE.md`):
pytest **1,242/1,242** (the 6 OOM cases pass on GPU) · eval jjk **31/31** ·
span-recall jjk **48,572/48,572** offline + **390/400 (97.5%)** probe ·
canon opm **10/16 exact, 236/236, 79.0%**. CLAUDE.md + the gates skill
baseline updated with these numbers + run timestamps (the 1,239-vs-1,242
stale pair is resolved: the suite is 1,242).

Second live run of the gpu-handoff chain (docs/ops/PC_GPU_HANDOFF.md):
`gpu-handoff.sh --tier2 plan/gpu_live2.spec` flips 262k→100k, opens C
(visible terminal `GPU-gpu_live2`, fresh 100k pi) which runs the
**standing-gates re-baseline** per `plan/gpu_live2_task.md` (pytest full on
CUDA incl. the 6 OOM cases, eval jjk, span-recall jjk offline + --probe 400
on a CUDA :8000, canon opm --skip-eval) → `reports/csm/GATE_REBASELINE.md`,
flips back 262k, and the gated typer types the resume line into A's window
(51768426). A sits idle at its prompt meanwhile (frozen context, zero cost).
Context: CSM-1b (owner directive 2026-09-08) is DONE + committed — bank
validation + 4 in-place gold fixes + relations runner + 4 numbered engine
gaps (G-CSM-1..4); the gate re-baseline moved to this side session (owner
correction: 262k holds the card → 100k+CUDA, never CPU fallback).

**On resume (the typed RESUME line is my next user message):**
1. Read `reports/csm/GATE_REBASELINE.md` (C's re-baseline).
2. Restore `:8000` to CPU (C left it on CUDA; 262k co-location rule —
   headroom 1,604 MiB < 6 GiB).
3. Check chain state: `reports/master-work/gpu_handoff_state/gpu_live2.{log,stalled,typed}`
   + `/tmp/gpu_live2_chain.log`. A `STALLED` flag = inspect, then replay:
   `setsid nohup bash tools/master-work/gpu-handoff.sh --tier2 plan/gpu_live2.spec >/dev/null 2>&1 &`
   (gates are idempotent).
4. Trash C's transcript (`reports/master-work/gpu_handoff_state/c_session`)
   — only AFTER reading the report (deleting it earlier poisons the
   switch-back fit guard).
5. Update CLAUDE.md's stale gate values with the re-baselined numbers + run
   timestamps (the 1,239 vs 1,242 self-contradiction), commit, then resume
   **CSM-2** (scoreboard/classification, council item 2 — its grounding data
   is in `plan/SWITCHPOINT.md`'s CSM-1b todo note / `reports/csm/`).

## gpu-live1 handoff (2026-09-08 — A=01a07f33 → chain → C on 100k → A resume)

First LIVE run of the gpu-handoff chain (docs/ops/PC_GPU_HANDOFF.md):
`gpu-handoff.sh --tier2 plan/gpu_live1.spec` flips 262k→100k, opens C
(visible terminal `GPU-gpu_live1`, fresh 100k pi) which runs the JJK gate
baseline per `plan/gpu_live1_task.md` (→ `reports/master-work/GPU_LIVE1_REPORT.md`),
flips back 262k, and a gated plain-shell typer types the resume line into A's
window (50331658). A sits idle at its prompt meanwhile (frozen context, zero
cost). Engine was untouched by today's MASTER_WORK deploy, so the baseline
should hold (eval 31/31, span-recall 100%); a deviation is a real signal.

**On resume (the typed RESUME line is my next user message):**
1. Read `reports/master-work/GPU_LIVE1_REPORT.md` (C's baseline).
2. Restore `:8000` to CPU (C left it on CUDA; 262k co-location rule —
   headroom 3.5 GiB < 6 GiB).
3. Check chain state: `reports/master-work/gpu_handoff_state/gpu_live1.{log,stalled,typed}`
   + `/tmp/gpu_live1_chain.log`. A `STALLED` flag = inspect, then replay:
   `setsid nohup bash tools/master-work/gpu-handoff.sh --tier2 plan/gpu_live1.spec >/dev/null 2>&1 &`
   (gates are idempotent).
4. Trash C's transcript (`reports/master-work/gpu_handoff_state/c_session`)
   — only AFTER reading the report (deleting it earlier poisons the
   switch-back fit guard).
5. CSM resume remains on hold (owner-paused; the stuck session 01a07cab
   resumption is a separate, later flip).

## Switch log (machine-appended by qwen-switch.sh)

- (none yet)- 2026-09-07T22:05:09+05:30 qwen-switch: ctx=102400 (mode 100k), api=off, free=8988MiB
- 2026-09-07T22:17:58+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=8986MiB
- 2026-09-07T22:19:34+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=8986MiB
- 2026-09-07T22:53:45+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=3513MiB
- 2026-09-07T23:32:51+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=9002MiB
- 2026-09-08T10:14:37+05:30 qwen-switch: ctx=135168 (owner manual +--vision; profile = serve_ctx_135168.sh), api=cpu, free=5575MiB
- 2026-09-08T12:51:22+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=7072MiB
- 2026-09-08T12:56:08+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1604MiB
- 2026-09-08T13:47:15+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=6932MiB
- 2026-09-08T13:56:00+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1488MiB
