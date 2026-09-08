# COUNCIL_unit3_sweep — unit-3 device-path fork verdict (2026-09-09)

§3 council trigger (RESUME §3 "at every big decision"): the unit-3 spec says the
§9a batch sweep is "the Wave-1 pinned panel + the 400-probe standing gate, on
CUDA, one-copy ordering" — but at 150k (current Qwen mode) the `:8000` service
must stay CPU (headroom 5,381 MiB < 6 GiB), so "panel on CUDA" requires the
150k→100k switch that the 2-phase plan reserves for Phase 2 ("NOT used in Phase
1", `plan/CSM_2PHASE_PLAN.md` L19-20, L122). B convened the full council (owner
rule 2026-09-08: sequential, one agent at a time) before touching the dial.

## Deployment (all zero-GPU, read-only, fresh context)

5 advisors (First Principles / Contrarian / Outsider / Executor / Expansionist)
→ 5 peer reviewers (weighted failure modes) → chairman. Sequential via one
workflow; every member read disk only. Raw receipts:
`reports/csm/receipts/council_unit3_sweep/` (adv_first-principles/contrarian/
outsider/executor/expansionist, review_1..5, chairman).

## Verdict (chairman; unanimous on the core)

**Option C — C-deferred-panel — 5/5 independent agreement.** Stay at 150k for
all of §9a iteration 1; **no mid-phase dial switch**.

1. **400-probe gate now** (R1): `span-recall --series csm --panel
   reports/csm/panel_csm.json --door qa --sanity 400` — one bounded run against
   the **live CPU `:8000` service** (rows 173–572 of the pinned panel, resuming
   the 172-row `e3d73720` ledger), LONG-flagged to A (>300 s at either on-disk
   CPU rate). Not the in-process CUDA driver (does not exist — `span_recall.py`
   is HTTP-only; pre-registered as a `tools/` upgrade, no council trigger, only
   if A flags the CPU path as unacceptably slow).
2. **Pre-triaged miss queue** (R2): `reports/csm/miss_queue_csm_iter1.jsonl`
   from the five frozen sources — twenty-failures 20 (bank 8 / door 5 / d5 7),
   red-list 5 (R-1..R-5), dimension-census reds **21 frozen from the raw
   39/60 file**, narrative-door misses 3 (Introduction, Bomb Girl, International
   Assassins), + the gate's new misses (~16 at the ≈4% per-probe rate). Every
   row stamped with fix class (R-1..R-5 or new R-6+) + floor/fixable ruling.
   **The halt meter = this frozen queue** (class-targeted subset-panel
   re-sweeps; "two no-reduction iterations" counted over queue miss counts;
   the 400-gate new-miss rate is trend-only, never a halt trigger).
3. **Documented floor over the extraction-gated reds** (R3): the 21 census reds
   sit on the Phase-2 extraction track (5.4 gate LIVE); their structural
   closure is the extraction build. The halt rule counts only Phase-1-fixable
   classes (plan Phase-1 done-criterion: "the closure loop at a no-reduction
   halt or a documented floor", 2PHASE L92-98).
4. **Exhaustive panel → Phase B, first act, PRE-extraction** (R4): plan item
   order (CSM-4 sweep item 2 precedes D6 extraction item 3, 2PHASE L102-108);
   the pre-extraction baseline is the control arm of the extraction experiment;
   commit-stamped Phase-1 rows resume forward (CSM-4's probe budget shrinks by
   what Phase 1 graded). One switch total: the planned `PHASE_A_COMPLETE` → 100k
   (`phase_status.txt` does not exist yet).
5. **Dead-door ruling** (R5): exit-3 sanity checks *merged* counts (warm qa
   ledger ⇒ 165 HITs ⇒ the floor can never fire) — so any post-fix class
   re-sweep must show **≥1 HIT in its own new rows or halt to council** (the
   one-line engine fix is deferred: council + four gates).
6. **Phase close** (R6): 34 s one-copy census re-adjudication of 5.4
   class-by-class (a red class closed by a Phase-1 fix de-scopes the
   extraction, "only on red census"); pre-register the extraction pass test
   (same 400-gate + red dimension classes green post-extraction; 200-row
   held-out as the out-of-sample leg).
7. **Infobox lever** (R7): the 62-key gap's per-wiki key map
   (`series/csm/overrides.yaml`) is the pre-registered **no-council** fix
   lever (T0_PILOT_CSM.md L48-50; engine `IDENTITY_FIELDS` widening = council +
   four gates). Phase-1 fix candidate after a small override-support check.

Why not A (mid-phase 100k switch): plan violation + staleness (the 5.4 gate is
LIVE ⇒ a pre-extraction 17k sweep measures a state the extraction changes;
CSM-4 re-sweeps at 100k anyway) + 3 reload windows vs 1. Why not B (stay 150k,
bounded CPU series for the full panel): ≈7.6–33.7 h of service load behind
~100–135 A-flagged runs for the same stale artifact.

**Change-of-mind condition (chairman):** if the baseline gate + frozen queue
comes back thin/empty (twenty-failures all HIT, no new miss class, every red
a floor), iteration 1 collapses to the plan's documented-floor close; the
device path is unchanged (150k until phase close, no mid-phase switch).

## Corrections this council forced into the record (B verified raw)

| On record | Raw truth | Evidence |
|---|---|---|
| work_log 03:43: "49/60 mech-green; reds arc-narrative 2/10, state-over-time 5/10, abilities 4/10" (13 reds implied) | **39/60 MECH_GREEN / 21 MECH_RED** — per-class: arc-narrative 2/10, state-over-time 5/10, abilities 4/10, personality 10/10, **appearance 9/10, causality 9/10** (the greens list summed to 39, not 49; 8 reds arc-narrative, 6 abilities, 5 state, 1 appearance, 1 causality) | `reports/csm/census_dimensions_csm_results.jsonl` (Counter over `verdict`, B re-counted this session) |
| Brief fact "CPU ≈ 168 probes/bounded run" | The 168-probe datapoint is **CUDA** `:8000` (`CSM3B_PRESTEP.md` §3, pid 103425 device=cuda); the only CPU rate points are ≈1–2 s/probe (work_log L26-27) and the dropped 1200-s incident sidecar (7.1 s/row). "0.9%" is completion-weighted (161/17,181); per-probe miss ≈ 4% (7/168) | `reports/csm/CSM3B_PRESTEP.md` §2–3 |
| "17,381-row panel" | Panel = **17,181** sweep rows + 200 held-out (separate keyed ledger `sweep_qa_ec15e0d8`, 13/200) | `reports/csm/panel_csm.json` |
| qa ledger state | 172 rows = 165 HIT / 3 MISS_DOC / 4 MISS_SPAN; 17,009 remain | `reports/span-recall/csm/sweep_qa_e3d73720.jsonl` |

## Side effects (per the chairman)

- **ESC:** only the one-copy census windows (stop `:8000` → 34 s + 18 s CUDA
  one-copy → restart CPU). **No `:8000` stop for the 400-gate or class
  re-sweeps** (they probe the live CPU service).
- **Switchpoint:** none in iteration 1 (reserved for Phase 2).
- **A approvals:** the one LONG flag for the gate run. Per **engine** fix:
  §3 council trigger + four-gate re-run (≈40–60 min each at 150k: pytest +
  eval jjk + canon opm in-process CUDA one-copy with the server down, span-
  recall 48,572 offline + 400-probe leg on the CPU service). Per-wiki
  overrides need no council. This cost stack (~2.5–5 h overhead × up to 5
  fixes), not the sweep, is unit-3's wall-clock driver.
- **JJK-100% invariant:** CSM work in CSM-centric files only; four gates
  re-baselined 2026-09-08 15:22 (1,254 / 31-31 / 48,572+400 / 236-236·79.0%)
  stand as the bar.

## First executable step (executed by B next)

1. ESC to A: LONG-flag approval for the baseline 400-gate run.
2. `span-recall --series csm --panel reports/csm/panel_csm.json --door qa
   --sanity 400` (bounded, CPU `:8000`; records the first on-disk CPU rate at
   the 150k service).
3. In the same model-free window: write `reports/csm/miss_queue_csm_iter1.jsonl`
   from the five frozen sources, every row stamped class + floor/fixable.