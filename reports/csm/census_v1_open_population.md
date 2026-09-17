# CSM Census v1 — Full Open Population (council #34, step 3)

The register `reports/csm/census_v1_floor_triage.jsonl` is extended **22 → 233
rows**: the full open population, not just the census-v1 floor.

**233 = 134 + 42 + 6 + 16 + 22 + 10 + 3.** Every row now carries governance
fields (`bucket`, `root_cause`, `owning_phase`, `closer`, `retest_trigger`,
`extraction_gated`, `lever`) alongside the census fields (`id`, `class`,
`subject`, `q`, `expect`, `triage`, `recovered_by`, `best_hits`).

## Buckets

| bucket | n | class | root cause | owning phase | closer | retest trigger | extr-gated |
|---|---|---|---|---|---|---|---|
| `setrel` | 134 | set-relation-residual | set/relation-completeness (box-ranking / width / state-over-time); #33 "not a router lever" | Phase-2 (D6) | D6 set/relation extraction | re-run D36 page-run after D6 | yes |
| `dim` | 42 | chapter_box 9 · episode 9 · volume_box 9 · story_arcs_box 10 · organization 5 | extraction-gated (D6 set/relation/mechanism completeness) | Phase-2 (D6) | D6 extraction campaign | re-run p23 census after D6 | yes |
| `abl` | 6 | ability-pool | extraction-gated | Phase-2 (D6) | D6 extraction campaign | re-run p23 census after D6 | yes |
| `empty` | 16 | empty-answer | engine returned no candidates at all | Phase-2 (D6) or struck | struck / receipt on file | n/a (struck per #34 R2) | no |
| `floor` | 22 | census-v1 floor (21 `csm-dim-*` 3-item + `csm-char-04` full-set) | extraction-gated (D6 census floor; R-7 close re-sweep 2026-09-10) | Phase-2 (D6) | D6 extraction / 5.4 re-adjudication | re-run D6 extraction + census after Phase-2 | yes |
| `bydesign` | 10 | R-1/R-2/R-3/R-4 (stamped open) | by-design open (documented, not a Phase-1 lever) | n/a (by-design) | n/a (documented) | n/a (revisit at P6) | no |
| `r1blast` | 3 | R-1 (blast-radius stamps) | R-1 blast-radius stamp (council R-1 chairman, 2026-09-09) | n/a | n/a | n/a | no |

## Notes (granularity + derivation)

- **134 `setrel` = page-granularity** — one row per rc=2 page slug in D36
  `receipts/model_window_d36/page_run.tsv` (136 rc=2 = 134 pages + 2 sweep
  artifacts `sweep_a.report`/`sweep_b.report`, tsv lines 442–443). Carries the
  corpus's **424 failing set/relation questions** (inventory §1): affiliations
  109 · named techniques 75 (74 short-subject + 1 `Light of a Star…`) · enemies
  55 · allies 49 · aliases 39 · superiors 27 · subordinates 23 · romantics 10 ·
  families 9 · friends 8 · rivals 6 · notable members 6 · mentors 3 · students
  2 · creators 1 · creations 1 · employees 1 (`tokyo_devil_detention_center`).
  Shape: **set/relation completeness, not fact recall** — D36 "known-class
  residual: box-ranking / width / state-over-time"; council #33: "not a router
  lever; no `router.py` change owed, R-9 absorbed no-fire."
- **16 `empty` = FAIL-line-granularity** — `missing: -`, the engine returned no
  candidates at all; 15 distinct slugs (`eternity_devil` ×2 →
  `empty-eternity_devil-1/-2`). The 15 slugs are a **subset of the 134 pages**,
  but the 16 are question/FAIL-level rows — the 233 total counts both
  granularities (council #34 disjoint arithmetic; the 16 "carry a receipt or are
  struck" per #34 R2).
- **42 `dim` + 6 `abl`** = the p23 bank reds **not** in the census-v1 floor:
  63 dim bank reds − 21 floor `csm-dim-*` = 42; + 6 ability-pool reds
  (`csm-abl-pool-140/149/166/237/252/358`). Fresh-triaed as extraction-gated
  from on-disk p23 receipts (`census_widened_csm_results.jsonl`); `recovered_by`
  reflects per-row `hits` (non-empty → `qa+anchor`/`narrative`, else `none`).
- **22 `floor`** = the census-v1 floor (21 `csm-dim-*` 3-item + `csm-char-04`
  full 8-item `expect` / 7 `best_hits`, Makima abilities); the canonical **N=22**
  (the "21" = the Census-v1 dim subset). GATE.md L73–87 halt residual **35 = 22
  floor + 10 by-design + 3 r1blast** (A20 stamps against the register diff, not
  against 35).
- **10 `bydesign` + 3 `r1blast`** = the 13 non-floor open rows in
  `miss_queue_csm_iter1.jsonl` (ruling = fixable-but-by-design or stamped).
  By-design ids: `csmdoor-01`, `csmd5-01/02/03/05/06`, `gate400-320`, `red-R-4`,
  `csm-char-03`, `csm-set-02` (`csmd5-04/07` are closed, excluded). R1 ids:
  `r1blast-tokyo`, `r1blast-blizzard`, `r1blast-marines`.

## Sources
- Register: `reports/csm/census_v1_floor_triage.jsonl` (233 rows, all unique ids).
- Inventory: `reports/csm/csm100_inventory.md` §1 (page-run / 424 / 16).
- p23 bank: `reports/csm/census_widened_csm_results.jsonl` (486: 417 green / 69 red).
- Halt rule: `reports/csm/GATE.md` L73–87. Miss queue: `miss_queue_csm_iter1.jsonl`.
- Council: `reports/csm/COUNCIL_csm_100p.md` (verdict L267+, step-3 spec L325–326).