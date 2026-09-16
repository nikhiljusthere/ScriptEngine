# COMPACTION PROOF — CSM Phase-1 session (opencode, 2026-09-12)

Every compaction MUST read this file first. It carries the small owner
instructions that a summary tends to drop. Newest note at the bottom.

## Owner instructions 2026-09-12 (this session, in order)

1. **Ponytail always on** (owner directive, also in memory.md): ladder
   (exist? reuse? stdlib? native? installed dep? one line? minimum), code-first,
   ≤3-line explanations, no unrequested abstractions.
2. **All tests on GPU/CUDA — never CPU.** Phase 1 needs no reranker, so the
   ~7 GB GPU headroom (Qwen 120k pre-reserves its int8 KV pool) is genuinely
   free; co-locate the test models / :8000 on CUDA. (Supersedes the old
   "CPU fallback for jobs" rule for this campaign.)
3. **Subagents: start with 2 at a time, check if it's better** — the 120k
   context fills up fast. (Refines an earlier "no limit" steer: batches of 2,
   evaluate wall-clock + GPU health + result quality before scaling up.)
   **REFINED later this session (owner): "council's all 5 at a time, the 2
   limit is only for other tasks"** — councils may deploy all members in
   parallel (the R-7 council ran 4 advisors in parallel, then chairman); the
   2-at-a-time limit still applies to *working* subagents.
4. **llm-council as an intermediate step after every major step / 2–3 todos
   completed**, to ensure nothing was left behind. (Already partially in the
   plan as S1–S5 triggers + P1.4 close council; this REINFORCES the cadence —
   run a slim 4-member light-form council at each S1/S2 event, serial.)
5. **This file (plan/COMPACTION_PROOF.md)**: every compaction cites and reads
   it; keep it updated as new small instructions arrive.

## Hard constraints (standing, easy to drop in a compaction)

- `git add .` BANNED — path-limited commits only (name every path).
- `rm *` is denied by project permissions (leave /tmp scratch alone).
- `reports/master-work/work_log.md` = B-only, APPEND at EOF, never rewrite.
- `reports/csm/GATE_LEDGER.json` = ledger of record: gates stand only if
  HEAD == last_green.commit AND no gate-relevant files changed since
  (scriptengine/, series/csm/overrides.yaml, tests). After any such change:
  re-run all 4 standing gates.
- Never kill Qwen (pid 7759). Never run the :8000 API on CPU while Qwen
  owns the card — CUDA co-location in quiet/short windows is the sanctioned
  pattern (verified again in the R-7 gate window: 31,083/32,607 MiB, Qwen
  survived).
- Server launches: `setsid nohup … < /dev/null &` (bare nohup dies on tool
  abort); poll with bounded status-printing loops, never a bare `sleep N`.
- JJK stays at 100% baseline — the 4 gates are the non-regression proof;
  CSM changes must not touch JJK files.
- Councils: serial in 262k/100k-era KV-pool history; at 120k with the owner's
  new 2-at-a-time steer, try 2 small members at a time and check Qwen health
  (full_reset rate / memory) between pairs; fall back to serial if it thrashes.

## Live system state (2026-09-12 ~12:10 +0530)

- Qwen 27B (ninfer) pid **7759**, 120k dial: ctx=kv=**122880**, GPU 25,576 MiB
  (~7 GB free headroom, util 3% idle at the stop). Healthy (`kill -0` alive).
- `:8000` API **STOPPED** again (the P2.1 step-0 warm-up window, started
  ~11:58 on CUDA, was stopped ~12:10 at the owner's direction so the Claude
  session that runs Phase 2 can own all the VRAM). The next session restarts
  it on **CUDA in a Qwen quiet window** before the probes (short, co-located —
  verified twice: R-7 and P1.4 windows, Qwen survived at 31,083/32,607 MiB).
  Log convention `/tmp/scriptengine_api_*.log` (the stopped one:
  `/tmp/scriptengine_api_p21.log`).
- `opencode.json` limit.context = **122880** (synced by the pi switch session;
  `qwen-switch.sh` now auto-syncs BOTH pi `models.json` and opencode.json on
  every dial switch — no more stale context).
- pi pid 7914 (session 01a0924e) was idle since 02:49; treat as the switch
  session's owner pane — do not type into it.

## Campaign position (CSM Phase 1, §9a closure loop)

- **R-7 gate window GREEN** (receipt `reports/csm/receipts/r7_gate_window.md`,
  run at HEAD `81df799`): pytest **1,321 collected** (new gate-1 pin; 1,316
  passed, 3 failed = the documented env-mcp trio with :8000 down, 2 xpassed);
  eval jjk **31/31**; span-recall jjk offline **48,572 rc=0** + 400-probe
  **398/400 (99.5%)**; canon opm **236/236, 10/16 exact, 79.0%**.
- R-7 code itself was committed earlier at `60e568f` (WIP power-loss commit:
  `config.identity_fields` + `eval/page_gen.py` merge + `series/csm/
  overrides.yaml` +66 + 2 test files, 41 model-free tests passing).
- **R-7 CLOSED (class-targeted re-sweep GREEN; council SHIP-AMENDED A1–A7).**
  Re-sweep: `csm-char-04` = the **22nd extraction-gated floor row** (the
  PM-contract ability name sits in section prose, the corpus never names it as
  an ability, the R-7 hunk is generation-only → retrieval shape bit-identical;
  close lever = Phase-2 extraction track / 5.4 re-adjudication); r1blast-tokyo
  re-probed live (qa→roster, 5/5, 0 new misses); r1blast-blizzard/marines
  held by gate-4 baseline-identity (direct re-probes skipped by council).
  Council (owner 2026-09-12: all 5 in parallel): 4 slim advisors + chairman,
  `reports/csm/receipts/r7_council/`, COUNCIL_HISTORY #28. Close commits:
  **`4f5d075`** (21-file path-limited close) + **`68d55c8`** (doc-only ledger
  fill). Stamps: queue r1blast ×3, red_list addendum "re-probe after R-7"
  done, GATE_LEDGER last_green → R-7, GATE.md live state → R-7 + pin 1,321,
  CLAUDE.md pin 1,321, drift D22, work_log 2 lines.
- **P1.4 CLOSED (council #29, CONDITIONAL APPROVE; PHASE A COMPLETE AT FLOOR,
  marker 2026-09-12T11:51:10+05:30).** Four-gate copy ALL GREEN @`407c016`
  (pytest **1,321** / eval jjk **31/31** / span-recall **48,572 rc=0 +
  398/400 (99.5%)** / canon opm **236/236 · 10/16 · 79.0%**, run dir
  `reports/2026-09-11-2218/`, ledger `p14_close_copy`); 5.4 re-adjudication
  of the 22-row floor (21R/39G of 60, 0 closed / 0 new, red-ID set identical
  to 09-09); P2.2 bar-audit pull-in (26 cases / 78 expect terms, model-free).
  Close council: 10 members **in parallel** (owner directive), finals
  restored verbatim from opencode.db (`/tmp/opencode/council_close/`),
  chairman single subagent — records `reports/csm/COUNCIL_csm_p14_close.md`
  + `reports/csm/receipts/council_p14_close/`, COUNCIL_HISTORY #29, drift D25.
  Marker: `reports/master-work/phase_status.txt` (substance: head `407c016` +
  receipts + ledger sha256 `c61b0a3f…` + floor 22 + rulings + caveat +
  env-mc known open). Rulings Q1–Q5 on disk: `CLOSE_COUNCIL_RULINGS_Q1_Q4.md`
  (Q1 No / Q2 No / Q3 Yes / Q4 Yes alongside P2.1 / Q5 out-of-gate). env-mc
  deferred to P1.5 (test-side fix, pin 1,321 unchanged). Denominator caveat:
"100%" = 33/33 fixable at the extraction-gated floor, not 100% of pages —
   CSM 175/537 (32.6%), 1,260 q, remainder 52.
- **P2.1 step-0 STARTED then HANDOFF (owner stop ~12:10; the Claude session
  owns Phase 2 + the VRAM).** Done in the directing session: quiet-window
  check (Qwen idle 3–5% between bursts, no extraction batch, ~7 GB headroom)
  → `:8000` up on CUDA (`/tmp/scriptengine_api_p21.log`, pid was 89782) →
  **warm-up 1-probe (qa door): 1/1 HIT, 17.0 s wall, cuda,
  `reports/span-recall/csm/recall_verbatim.jsonl` written** (committed).
  NOT done: the per-door sanity-100 + the on-disk s/probe re-estimate + the
  A17 per-door floor policy in `reports/csm/GATE.md` + the go/no-go.
  **Next session's pre-flight (A18, the plan's "start from zero"): the
  tracked qa ledger `reports/span-recall/csm/sweep_qa_e3d73720.jsonl` holds
  572 Phase-1 rows stamped `commit 5c424f3` (pre-fix, f81a1af window) —
  WIPE it before the sanity-100/full sweep so probes start at panel row 1
  (the warm-up probe did not touch the panel ledger). Narrative/roster have
  no ledgers yet. Then: restart `:8000` (CUDA, quiet window) → `--sanity 100`
  qa → narrative → roster (plan order; `--sanity` first-run-only) → measure
  per-door s/probe → re-estimate 17,181 × s/probe per door into GATE.md
  (record A17 floor policy pre-sweep + the A26 panel/heldout hashes) →
  go/no-go vs the 2-GPU-day budget (re-estimate > 2 GPU-days ⇒
  abort/shrink/council) → then the 200-row held-out leg + P2.3 extraction.
- **Open queue: 35 rows = (a) 22 extraction-gated floor** (21 D6-extraction +
  `csm-char-04`) **+ (b) 13 invariant floor/residual, stamped by-design open**
  (csmdoor-01 31/88; D5 residuals csmd5-01/02/03/05/06 + gate400-320 +
  red-R-4; closed-class residuals csm-char-03 + csm-set-02 (R-3) + r1blast-
  tokyo/blizzard/marines (R-1) — the DRAFT's residual-stamp gap closed by the
  council's A2) **+ (c) 0 fixable**. Final meter:
  `reports/csm/HALT_METER_P13.md` (re-issued from the DRAFT at the close;
  DRAFT + final both committed; halt residual 35, superseding the DRAFT's 34).
  Env-mcp caveat (chairman A4): the 3-trio live proof was DISCHARGED at the
  P1.4 four-gate copy (:8000 up) — 2/3 pass, 1 REAL finding (bare "Maki
  Zenin" → `qa` vs test's narrative expectation; pre-existing since
  `8d07487`). Deferred to P1.5 (test-side fix, pin 1,321 unchanged; see
  `GATE_LEDGER.json` `p14_close_copy.env_mc_live_proof`).

## Next steps (in order)

1. ~~R-7 class re-sweep + stamp/commit + council~~ **DONE** (`4f5d075` +
   `68d55c8`; records above).
2. ~~**P1.3 finalize** (halt-meter convergence) + **P1.4 close** (four-gate
   copy + 5.4 re-adjudication + bar-audit + close council + marker)~~ **DONE
   (2026-09-12)** — council #29 CONDITIONAL APPROVE, all 3 on-disk conditions
   landed in the close commit; `PHASE_A_COMPLETE 2026-09-12T11:51:10+05:30`
   marker in `reports/master-work/phase_status.txt`;
   `reports/csm/PHASE_A_COMPLETE_AT_FLOOR.md`; drift D25.
3. **Phase 2 — now owned by the Claude session (owner stop 2026-09-12 ~12:10;
   it frees all the VRAM). Straight in** (owner steer 2026-09-10: no pause):
   (a) wipe the tracked qa ledger (572 pre-fix rows, A18 "start from zero");
   (b) restart `:8000` on CUDA in a Qwen quiet window (short co-located run;
   warm-up probe already done in the directing session, 17 s wall);
   (c) **P2.1 step 0 before any panel hour**: per-door sanity-100 (qa →
   narrative → roster) → re-estimate 17,181 × measured s/probe per door into
   `reports/csm/GATE.md` + record the A17 per-door floor policy pre-sweep +
   the A26 panel/heldout hashes → go/no-go (>2 GPU-days ⇒
   abort/shrink/council). The plan's 51-GPU-h is double-stale (4 s/probe =
   fiction; on-disk ceiling 8.5 s/probe CPU@150k ≈122 h).
   (d) 200-row held-out leg (`heldout_declaration_csm.md`, A24/A26).
   (e) P2.3 extraction (closes the 22 floor rows; per Q3, re-gate the null
   branch on the widened census — the 5 in-scope page types, not the 60-q
   character census).
   (f) P1.5 (MCP bridge): env-mc test-side fix, live proof 3/3, ledger note.
4. Keep this file current at each step (append a dated note at the bottom).

## Dated notes

- 2026-09-12 ~03:40: R-7 gate window 4/4 GREEN (receipt on disk, HEAD 81df799);
  halt-meter draft done (21/13/1 buckets); both 2-at-a-time subagents
  verified working (wall-clock good, no GPU anomaly, compact outputs).
- 2026-09-12 ~04:00: **R-7 class CLOSED.** Re-sweep GREEN (csm-char-04 =
  22nd floor row; r1blast-tokyo live 0-new-miss; blizzard/marines held by
  baseline-identity); council 4-advisor parallel + chairman per the new owner
  directive ("all 5 at a time, 2-limit is other tasks only") → SHIP-AMENDED
  A1–A7, all executed. Close commit `4f5d075` (21 files, path-limited) +
  doc-only ledger fill `68d55c8`. HALT_METER_P13.md re-issued FINAL at
  (a)=22/(b)=13/(c)=0, halt residual 35. Queue 35/23/58 (zero rows closed by
  design, by design). NEXT: P1.3 finalize (mechanical convergence check on
  the final meter) → P1.4 close council (four-gate copy with :8000 up — the
  env-mcp trio's live proof — + 5.4 re-adjudication of the 22-row floor +
  bar-audit + close conditions (a)–(e)) → `PHASE_A_COMPLETE_AT_FLOOR.md` →
  Phase 2 P2.1 step 0.- 2026-09-12 ~11:52: **PHASE A COMPLETE AT FLOOR (P1.4 closed).** Council
  #29 (10 parallel members + chairman; finals restored from opencode.db)
  ruled CONDITIONAL APPROVE; all 3 on-disk conditions landed in the close
  commit: `CLOSE_COUNCIL_RULINGS_Q1_Q4.md` (Q1 No / Q2 No / Q3 Yes /
  Q4 Yes alongside P2.1 / Q5 out-of-gate D-only) + the substantive
  `PHASE_A_COMPLETE 2026-09-12T11:51:10+05:30` marker in
  `reports/master-work/phase_status.txt` (ledger sha256 `c61b0a3f…`, floor 22,
  head `407c016`, denominator caveat, env-mc known open) +
  `reports/csm/PHASE_A_COMPLETE_AT_FLOOR.md`. Stamps: GATE_LEDGER +p14_close,
  COUNCIL_HISTORY #29, drift D25, work_log ACT. env-mc → P1.5 (test-side, no
  re-pin, pin stays 1,321). 51-GPU-h double-stale → P2.1 step-0 owes the
  on-disk re-estimate before any panel hour. NEXT: Phase 2 as above.
- 2026-09-12 ~12:10: **P2.1 step-0 started, then owner-directed handoff.**
  Quiet window verified (Qwen idle 3–5%, no extraction batch) → `:8000` up
  on CUDA (pid 89782, `/tmp/scriptengine_api_p21.log`) → warm-up 1-probe on
  the qa door: 1/1 HIT, 17.0 s wall (model load included), cuda, wrote
  `reports/span-recall/csm/recall_verbatim.jsonl` (committed). Owner stop:
  Phase 2 goes to the Claude session, which owns all the VRAM. Steady state
  restored: `:8000` down (killed 89782), Qwen 7759 alive (25,576 MiB, 3%
util, idle). Next session pre-flight: wipe the 572-row pre-fix qa ledger
   (`sweep_qa_e3d73720.jsonl`, stamped 5c424f3; A18 start-from-zero), restart
   `:8000`, per-door sanity-100 + on-disk re-estimate + A17 floor policy +
   A26 hashes → go/no-go → held-out leg → P2.3.
- 2026-09-16 ~22:50: **R-8 gap window closed (coding-only, opencode; the
  GPU leg is the Claude handoff).** R-8 = `aada154` (the `wants_chronology_set`
  guard in `retrieve/chronology.py` + `retrieve/router.py` that splits
  set-in-order → roster from one-subject-in-order → narrative; 39 diff lines =
  10 collected router tests). It landed on tree `852916e` with its gate window
  **undischarged**: `GATE_LEDGER.json` `last_green` is still P1.2/R-7
  (`60e568f`, pin 1,321) and `git log 407c016..HEAD -- scriptengine/ tests/` =
  `aada154` only. (1) **Pin corrected to 1,331** (1,321 + 10 R-8 tests;
  verified `pytest tests/ --collect-only -q` = 1,331). (2) **env-mc deferral
  discharged (count-neutral)**: the P1.4 live-prove finding (bare "Maki Zenin"
  → `qa`) is the intended router behavior (bare-name→qa rule, `router.py:
  816-820`, landed 8d07487); the stale test now asserts it —
  `tests/test_mcp_server.py::test_research_bare_character_name_is_qa`
  (renamed from `..._is_narrative`). (3) **P2.1 sweep runner pre-baked** at
  `tools/csm/p21_sweep.sh` (sweep needs no Qwen inference → runs with Qwen
  DOWN, whole 32 GB on `:8000`): pre-checks (A26 frozen hashes
  `cf72135f…`/`604dc8ca…`, row counts 17,181/200, `:8000` /health, Qwen
  `:18080` down → exit 10/11/12) + **stamp-based A18 pre-wipe** (ledger rows
  stamped with current `git rev-parse --short HEAD` (7 chars) resume forward;
  any older stamp — the pre-R-8 `f2a611d` sanity rows — wipes and the door
  restarts, so P1 parser fixes are never attributed to P2.3) + sequence qa →
  narrative → roster → auto (full panel) then auto-heldout (200-row
  out-of-sample, the A24(a) number) + 30 s watchdog + halt codes (exit 4 =
  health ×2 rolling, exit 5 = ERROR >10/last-50 rows rolling, exit 20+rc =
  CLI rc, exit 30 = row-count integrity) + receipts
  `reports/master-work/p21_sweep_<stamp>_{RECEIPT.md,_run.log}`. Pre-check +
  wipe/resume logic verified against a scratch copy. **Ledger disk state
  (supersedes the "572 rows" note above):** 4 × 100-row
  `sweep_{qa,narrative,roster,auto}_e3d73720.jsonl` — qa/narrative/roster
  stamped `f2a611d`, auto stamped `2f67222` (pre-R-8, the `ba3a866` wipe +
  sanity-100 recreation; all four stale vs HEAD) → the runner wipes all four
  at run start (stale stamp). **Owed (GPU, Claude session, Qwen
  down): the R-8 four standing gates + `eval --series jjk` 31/31 at pin 1,331,
  then `setsid nohup bash tools/csm/p21_sweep.sh > /dev/null 2>&1 < /dev/null &`
  for P2.1 (receipt → A17 bar ≥ 97.5 % on the post-R-8 auto path), then P2.3
  widened census + D6 extraction.** **R-8 window fix-up (2026-09-16,
  council-1 audit, disk-verified, zero GPU): the runner was hardened — the
  heldout leg ran api-door `auto` under label `auto-heldout` (`auto-heldout`
  as an API mode would 422, `api/main.py:79`), the watchdog now watches main +
  the `.new` live-sidecar (merged on clean exit, `span_recall.py:469-489`) so
  exit 5 is reachable on wiped ledgers, and the A18 wipe manages all five
  ledgers + sidecars (resume iff every row stamped with HEAD); GATE.md's R-8
  section now carries the explicit launch order (gate window FIRST, then Qwen
  down, `:8000` on the whole card, launch; no commits mid-sweep) —
  `work_log.md` + `GATE.md` "Runner fix-up (council-1 findings)" for the
  full record.**
