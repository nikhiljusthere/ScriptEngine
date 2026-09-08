# Peer Review 5 — CSM Unit-3 sweep fork (council 2026-09-09)

Reviewer weighting: **the council misses the upside — Phase-B data reuse, the
extraction-gate interaction, the infobox-key gap.** Fresh-context subagent;
zero-GPU, read-only; every shell < 15 s.

**Response-file mapping.** The task pointed at `adv_A.md`…`adv_E.md`; those do
not exist in `reports/csm/receipts/council_unit3_sweep/`. The five responses
carry persona filenames. Mapping (same as reviews 1–4: deployment order by
mtime 03:48→03:58 + the executor file's own `adv_D` header):

A = `adv_first-principles` · B = `adv_contrarian` · C = `adv_outsider` ·
D = `adv_executor` · E = `adv_expansionist`.

## Verified on disk (this review's own checks)

| Claim | Verdict | Evidence |
|---|---|---|
| Census 39/60 green / 21 red (not 49/60) | ✓ re-verified | python `Counter` over `reports/csm/census_dimensions_csm_results.jsonl` → MECH_GREEN 39 / MECH_RED 21 |
| qa ledger 172 rows; held-out ledger 13 rows (of 200) | ✓ re-verified | `reports/span-recall/csm/sweep_qa_e3d73720.jsonl` (172), `reports/span-recall/csm/sweep_qa_ec15e0d8.jsonl` (13) |
| 62-key infobox gap, pre-registered two-lever fork | ✓ | `reports/csm/T0_PILOT_CSM.md` L48-50: "62 keys, four near-miss spellings … the council chooses between widening `IDENTITY_FIELDS` (engine) and a CSM per-wiki key map (`series/csm/overrides.yaml`)"; also `reports/csm/receipts/waveB_csm6_instrument.md` L13 |
| Engine-side `IDENTITY_FIELDS` exists (widening = engine change) | ✓ | `scriptengine/retrieve/roster.py:3317` `_IDENTITY_FIELDS`; `scriptengine/eval/page_gen.py:49` |
| **Plan's Phase-2 ordering: CSM-4 sweep (item 2) BEFORE D6 extraction (item 3, only on red census)** | ✓ | `plan/CSM_2PHASE_PLAN.md` L102-108 |
| 8-verb gap: 24/100 held, 76% of the chapter/episode Summary slice not held by the live 9-verb set; "decides widen-set-before-extract" | ✓ | `reports/csm/eight_verb_sample_csm.md`; `reports/csm/dimension_map_csm.md` L13-14, 28-33 |
| Cross-page census 10,889/11,261 edges (96.7% cross-document); events/meaning 0 rows by Phase-2 design | ✓ | `reports/csm/crosspage_census_csm.md` L9 |
| 5.4 gate is conditional: extraction proceeds *only if* the dimension census is red on a structural dimension | ✓ | `reports/csm/door_precheck_csm.md` ("extraction proceeds **only if** …") |
| One-copy census window 34 s (re-adjudication cost at phase close) | ✓ (cited) | `reports/master-work/work_log.md` 03:43 line (census_dimensions 34 s + census_doors 18 s, Qwen 150k alive) — as cited by reviews 1/3 and brief fact 4 |

## The three answers (budgeted, < 200 words total)

**1. Strongest: E (expansionist).** Only response treating "stale" as an
asset: the pre-extraction baseline in the *planned* 100k window is the
control arm of the extraction experiment (delta proves comprehension, not
churn); the miss population writes the D6 spec. Caveat: descope → switch A is
plan-forbidden; Phase-B cost unquantified.

**2. Biggest blind spot: A (first-principles).** Its step (5) schedules the
panel "post-extraction" — but the plan's Phase-2 ordering
(`CSM_2PHASE_PLAN.md` L102-108) puts the CSM-4 sweep *before* D6 extraction.
A forfeits the plan's control arm, repeats 49/60, leaves
causality/appearance reds (2 of 21) unowned.

**3. What all five missed:** (a) **Reuse:** the commit-stamped (R-CSM3B-2)
ledger makes Phase-1 fix-grade rows a resumable prefix of CSM-4's sweep —
per-fix diffs preserved, Phase-B probe budget shrinks by what Phase 1 graded; the 200-row holdout checks post-extraction gain out-of-sample. (b) **Gate
interplay:** no re-adjudication of 5.4 at phase close (34 s re-run;
reds green → extraction descoped), no pre-registered pass test for extraction
(400-gate + 21 reds green post-extraction). (c) **Infobox keys:**
`T0_PILOT_CSM.md` pre-registers a per-wiki key map
(`series/csm/overrides.yaml`) vs
engine `IDENTITY_FIELDS` — mapping the 62 keys in Phase 1 closes census reds,
shrinks D6 scope; even E treats it as Phase-2-only.

## Note to the chairman

The council's default synthesis (D's plan + C's deferral) is sound, but three
upside rulings should attach so the deferral doesn't silently discard value:

1. **Ordering ruling (free upside).** Phase B runs CSM-4's panel sweep
   *before* D6 extraction — that is the plan's own item order
   (`CSM_2PHASE_PLAN.md` L102-108). State it in the ruling: the pre-extraction
   full-panel baseline is the control arm; "staleness" is the experiment, not
   waste. A's "post-extraction" step is the only response that inverts it.
2. **Gate re-adjudication + acceptance test.** Rule a 34 s one-copy census
   re-run at phase close (re-adjudicates 5.4 class-by-class: reds Phase-1
   fixes close → extraction de-scoped, per the plan's "only on red census"),
   and pre-register the extraction's pass criterion: the same 400-row gate +
   the red dimension classes turn green post-extraction; the 200-row held-out
   ledger (13/200 today) is the out-of-sample leg.
3. **Pull the infobox-key lever forward.** The 62-key gap (four near-miss
   families, `T0_PILOT_CSM.md`) is bounded and enumerable — a per-wiki key map
   is the pre-registered no-council lever (engine `IDENTITY_FIELDS` widening is
   the alternative, which *is* council + four gates). Scheduling it in Phase 1
   closes census reds and MISS_DOC rows that otherwise ride into D6, shrinking
   the extraction build. The 8-verb gap (24/100 held) is the sibling decision
   ("widen-set-before-extract", `dimension_map_csm.md` L14) — the council should
   rule verb-set scope in the same breath, since both gate the extraction's
   input surface.

Residual risk: findings (a)-(c) are document/council-record based (the ledger
resume + holdout paths are verified in code by review_4; the T0 two-lever fork
is a pre-registration, not yet a built hook — the per-wiki key map needs a
small override support check before Phase 1 schedules it).