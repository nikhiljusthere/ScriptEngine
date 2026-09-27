# S5 delta re-gate receipt — 2026-09-27 (Phase C entry)

Session `ses_f24716355ffer6xL219hi91Hsn` · branch `character-scoped-questions` ·
runbook `reports/marvel/receipts/f3_f5_prevalidation_2026-09-27.md` §S5 (8 steps) ·
**S3 executed DELTA-ONLY per owner permanent rule 2026-09-27** (full `allpages`
re-enum prohibited unless the owner explicitly asks; plan S3 addendum recorded).

## Verdict
**S5 delta re-gate = PASS** (all 8 steps complete; marvel final G6 landed 236,720 / 3,796,438 / 0)
→ **Phase C entry (C1)** is authorized.

## Step 1 — egress receipt checks (all PASS)
- **F1 marvel** `revid_backfill_marvel_complete_2026-09-26.json`: 236,625/236,628 stamped,
  0 unreadable; **3 `missing_live`** (wiki-side): `Elizabeth Tyne (Earth-33263)`,
  `Enok (Hyboria) (Earth-616)`, `Realm of Nothingness (Forbidden Dimension)` → dispositions
  below (step 6).
- **F1 mcu** `revid_backfill_mcu_complete_2026-09-26.json`: 35,209/35,209 (100%), 0 missing.
- **F3 recrawl** `fixlist_f3_recrawl_2026-09-26.json`: 4/4 written, `--disambiguate` pageid
  suffixes (410610 / 1173315 volumes · 27821 / 1173308 comics) — the 4-title fold is resolved.
- **F5 top-up** `fixlist_mcu_topup_f5_2026-09-26.json`: **1/33 written**
  (`Avengers: Endgame (episode)`), 32 skipped by design (31 `Articles with No Applicable
  Images` + 1 `Article stubs`), `bad_rows=0`. Deviation from the 33-written projection is
  by the engine's standing low-value-page exclusion, not a fetch failure.
- **S3 delta top-ups** (egress FI #216 `187.40.62.123`, ipify-verified pre-call):
  - marvel chunk1 `fixlist_s3_delta_topup_marvel_2026-09-27.json`: 49/50 written, 1 skipped by design
  - marvel chunk2 `fixlist_s3_delta_topup_marvel_chunk2_2026-09-27.json`: 41 written, 2 skipped by
    design, 1 `missing-or-failed` = `Valusian Guard` → wiki rename to `Red Slayers (Earth-616)`
    (base title, on disk, live) — target kept in the gate list, old spelling dropped
  - mcu `fixlist_s3_delta_topup_mcu_2026-09-27.json`: 25 written, 19 skipped by design,
    5 `missing-or-failed` = wiki-side old spellings of in-window renames/deletes
  - mcu2 `fixlist_s3_delta_topup_mcu2_2026-09-27.json`: 2 canonical `…Universe` rename targets
    fetched → both skipped by design (`Article stubs`) — no on-disk gap
  - 1 rc false-positive: `Voice Synthesizer` already on disk (base overlap) → its "write" is a
    legitimate refresh; **net-new MCU files = 24, not 25**
- **Final on-disk totals: marvel 236,720 · mcu 35,234** (reconciled: marvel
  236,628 base − 2 retired F3-folded + 4 F3-new + 90 top-up · mcu 35,209 + 1 F5 + 24 top-up).

## Step 2 — G4-style diff on changed/added files (PASS)
- F3: 2 new-content pages (27821, 410610) + 2 re-extracts identical modulo metadata.
- F5: `Avengers: Endgame (episode)` faithful (pid 443230).
- **`preserved_key_violations: []`** — title/url/pageid/revid/wikitext/fetched_at/categories/
  templates/redirects untouched across the mutation set.

## Step 3 — F3 quarantine (owner-ratified, executed)
- The 2 folded pre-disambiguation `What If` files retired to
  `reports/marvel/receipts/f3_quarantine_2026-09-27/` (reversible).
- 4 pageid-suffixed files on disk, no last-write-wins (verified in step 6 F3 audit).

## Step 4 — G5 local sheet (PASS, zero-egress)
- F3 4-way disambiguation clean (4 distinct pageids, no collision).
- F5 written page faithful: 5 facts, 0 warnings.

## Step 5 — G6 full dry-run on the mutated corpus (official `load_extracted` path)
- **mcu: PASS** — `parse_diff_mcu_final_2026-09-27.jsonl`: **35,234 pages / 126,195 facts /
  0 exceptions** (97.0 s).
- **marvel: PASS** — `parse_diff_marvel_final_2026-09-27.jsonl`: **236,720 pages / 3,796,438 facts /
  0 exceptions** (1421.6 s, 167 pages/s).
  Expectation vs pre-top-up run: 236,632 → 236,720 pages (+88 = 90 top-up − 2 retired).
- Stale pre-chunk2 run was SIGTERM'd before writing its output — nothing lost.

## Step 6 — S3 delta re-enum + drift audits (zero-egress)
- **Delta walk** `recentchanges_delta_{marvel,mcu}_2026-09-27.json` (Fandom `recentchanges`,
  client-side rctype filter, `rccontinue` paging): marvel **93 new / 0 del / 0 move** (3 API
  calls, window 09-25 18:34 → 09-27 02:37) · mcu **48 new / 0 del / 0 move** (4 calls).
- **Liveness of the 3 F1 `missing_live`:** `Elizabeth Tyne (Earth-33263)` + `Enok (Hyboria)
  (Earth-616)` = still missing (wiki-side deletions; on-disk files retained + documented).
  `Realm of Nothingness (Forbidden Dimension)` = **false positive** — now a live redirect to
  `Oblivion Void` (pid 1876536, last rev 09-26 12:17) → revid stamp corrected 0 → 11197247.
- **Gate-day accounting lists (re-archived; 09-25 archives preserved):**
  `marvel_all_pages_gate_2026-09-27.jsonl` = **279,223** (base 279,133 + rc 93 − 3) ·
  `mcu_all_pages_gate_2026-09-27.jsonl` = **48,102** (base 48,059 + rc 48 − 5 stale spellings).
  Operation-level verified (per-op membership; the 2 canonical `…Universe` targets are in rc-new).
- **Drift audits vs the gate lists** (`title_drift_audit_…_gate_2026-09-27.json`):
  - marvel: F2 = exactly the 3 documented `missing_live` orphans · F3 = the 2 What-If-Thor
    groups (pageid disambiguation working, 4 files) · **F7 = 181 occ / 149 files**
  - mcu: F2 = 0 · F3 = 0 · **F7 = 2 occ / 2 files** (known post-re-emit residuals
    `Arlene.json` + `Assassination of Abraham Erskine.json`, unchanged)
- **F7 +5 classification (zero parser regression):** the 5 new stray files are all S3-top-up
  Big Hero 6 Earth-TRN1974 pages (Frederick Frederickson IV / Go Go Tomago / Hiro Hamada /
  Honey Lemon / Wasabi-No Ginger), all `Name ' s` space-apostrophe possessives = the
  documented source-quality family (same class as the 144 pre-existing residual files).
  MCU top-ups: 0 new strays. Counts re-derived with the audit tool's own logic: MATCH.

## Step 7 — standing gates
- Cited, not re-run: since `bc559901` only `plan/` + `tools/marvel/` (campaign tooling)
  changed — **zero engine (`scriptengine/`) or test changes** → the `bc559901` 4-green
  receipt stands (eval 31/31 · span-recall 48,572/48,572 + probe 398/400 ·
  canon 10/16·236/236·79.0% · pytest 3 failed/1,345 passed, CUDA).

## Deferred / owner-decision items (recorded, not blocking C1)
1. **G6 parallel-variant candidate** (owner: let the single-core gate stand): chunked
   multiprocessing of the extract + one-time equivalence diff vs the official sequential
   output; if 0-diff, adopt for future S5 re-gates (~24 min → ~3–4 min).
2. **GATE B1 decision** (Phase B): accept B1-text + B2-diarization attribution vs require a
   fully-labeled CC source first (pilot label density 0–8% on HI files).
3. MCU F7 2-file residual: stays in `known_diffs` (source quality; bounded).

**Next: Phase C — C1 (T0 structured generation on marvel + mcu facts.db).**