# D1 reconciliation — every page covered or excluded in writing (2026-09-27 gate day)

Zero-egress set arithmetic over committed receipts (S5 delta re-gate day).
Denominator annex rule: a number that disagrees with a fresh run wins.

## marvel

- gate-day list: **279223** (base 09-25 enumeration + 09-27 rc delta − wiki-side deletions)
- on disk (G6 final dry-run, 0 exceptions): **236720**
- excluded: **42506** → `exclusions_marvel_2026-09-27.jsonl`
- arithmetic check: gate − excluded = 236717 vs on-disk − retained orphans = 236717 (tie: True)
- retained orphans (F1 `missing_live`, on disk by design, not in gate list): 3
  - Elizabeth Tyne (Earth-33263)
  - Enok (Hyboria) (Earth-616)
  - Realm of Nothingness (Forbidden Dimension)

cause classes:
  - crawl-skip: 42504
  - topup-skipped: 2
  - receipts consulted: skip_receipt=42504 rc_new=93 topup_targets=98

## mcu

- gate-day list: **48102** (base 09-25 enumeration + 09-27 rc delta − wiki-side deletions)
- on disk (G6 final dry-run, 0 exceptions): **35234**
- excluded: **12868** → `exclusions_mcu_2026-09-27.jsonl`
- arithmetic check: gate − excluded = 35234 vs on-disk − retained orphans = 35234 (tie: True)
- retained orphans (F1 `missing_live`, on disk by design, not in gate list): 0

cause classes:
  - crawl-skip-aggregate: 12817
  - topup-skipped: 51
  - residual: 0
  - receipts consulted: skip_receipt=0 rc_new=48 topup_targets=82
