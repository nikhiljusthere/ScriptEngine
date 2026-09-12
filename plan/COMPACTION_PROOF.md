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

## Live system state (2026-09-12 ~11:55 +0530)

- Qwen 27B (ninfer) pid **7759**, 120k dial: ctx=kv=**122880**, GPU ~25.9 GB,
  ~6.2 GB free headroom. `ninfer-work/qwen_mode.txt`: mode=122880 api=cuda.
- `:8000` API **STOPPED** (P1.4 W2 window closed after the canon opm copy).
  Restart on **CUDA in a Qwen quiet window** before the P2.1 probes (short,
  co-located — verified twice: R-7 and P1.4 windows, Qwen survived at
  31,083/32,607 MiB). Log convention `/tmp/scriptengine_api_*.log`.
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
3. **Phase 2, straight in** (owner steer 2026-09-10: no pause):
   (a) restart `:8000` on CUDA in a Qwen quiet window (short co-located run);
   (b) **P2.1 step 0 before any panel hour**: per-door sanity-100 →
   re-estimate 17,181 × measured s/probe per door into `reports/csm/GATE.md`
   + record the A17 per-door floor policy pre-sweep → go/no-go
   (>2 GPU-days ⇒ abort/shrink/council). The plan's 51-GPU-h is double-stale
   (4 s/probe = fiction; on-disk ceiling 8.5 s/probe CPU@150k ≈122 h).
   (c) 200-row held-out leg (`heldout_declaration_csm.md`, A24/A26).
   (d) P2.3 extraction (closes the 22 floor rows; per Q3, re-gate the null
   branch on the widened census — the 5 in-scope page types, not the 60-q
   character census).
   (e) P1.5 (MCP bridge): env-mc test-side fix, live proof 3/3, ledger note.
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
