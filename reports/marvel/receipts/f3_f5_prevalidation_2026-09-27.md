# F3/F5 pre-validation + delta re-gate runbook (2026-09-27, zero egress)

Campaign receipt (untracked, per the `reports/marvel/receipts/` convention).
All checks below ran **zero-egress** at 2026-09-27 ~00:3x while the F1-MARVEL
backfill was mid-run (batch 2374 = 118,700/236,628 stamped, missing=2 tracked,
0 rate-limits; egress FI #214 `187.40.62.58` stable; watchdog pid 47870 healthy).
Nothing in this file touched the running batch or the network.

## 1. F3 pre-validation (plan: "zero-egress inspection of the 2 folded collision files + 1 orphan, then re-crawl")

**Collision map (precomputed locally via `sanitise_filename`):**

| list title | sanitised stem |
|---|---|
| `What If: Thor Vol 1` | `What If_ Thor Vol 1` |
| `What If? Thor Vol 1` | `What If_ Thor Vol 1` |
| `What If: Thor Vol 1 1` | `What If_ Thor Vol 1 1` |
| `What If? Thor Vol 1 1` | `What If_ Thor Vol 1 1` |

Both stems are in the `--disambiguate` colliding set (each appears twice in the
list), so **all 4 titles get a `(pageid)` suffix at runtime → 4 owner files**.
The mode is sequential (fetch one, write + rename, next), so a collision can
never last-write-win. If a live title has been *renamed* on the wiki (e.g. to
the `What If...?` spelling), its live stem is not in the colliding set and the
file is written under the plain stem — that can only update a same-page file
(legitimate refresh + native revid stamp), never fold two titles.

**Folded files on disk (the 2 being retired post-batch):**
- `What If_ Thor Vol 1.json` — pageid 1173315, stored title `What If? Thor Vol 1`, revid 0
- `What If_ Thor Vol 1 1.json` — pageid 1173308, stored title `What If? Thor Vol 1 1`, revid 0
- Both still in the running F1 backfill's path (`W` range in sorted order,
  not yet reached) → **do not move them before the marvel stage completes.**

**Orphan (`Elizabeth Tyne (Earth-33263)`):**
- On disk: `series/marvel/wikitext/Elizabeth Tyne (Earth-33263).json`,
  pageid 1866601, revid 0, 7,386 bytes, content valid.
- In the 15:21 enum (`marvel_all_pages.jsonl`, 279,112 lines): YES (the 2
  Tyne variants are present). Dropped by the 18:58 enum (279,133;
  `E_old − E_new` = exactly the 2 Tyne variants — the F2 record in
  `known_diffs_2026-09-25.md`). Not in the 42,504-line skipped list.
- `title_drift_audit_marvel_2026-09-25.json`: `drift = ["Elizabeth Tyne (Earth-33263)"]` exactly.
- Disposition (per F2 consequence 2): **stays on disk**; the post-batch revid
  spot-check re-enumerates live and it surfaces as a wiki-side deletion, not a
  content change.

## 2. F5 pre-validation

`mcu_topup_f5_2026-09-26.jsonl` (33 titles; fresh enum 48,059 − manifest
48,026 = net-new 33): **0 of the 33 have an on-disk MCU file** (sanitised-name
check) → the list is fresh; every F5 write is a true top-up, none overwrites.

## 3. F1 write-path rationale (feeds the re-gate's diff step)

`revid_backfill.py::stamp_revid` rewrites **only the `"revid"` line** (regex
sub, count=1) and then re-parses before/after, asserting the dicts are
identical apart from the new revid value. Any anomaly is printed
(`ANOMALY … revid line not found/unique; skipped`) and counted. So for the
~236k + ~35k F1-mutated files, "the only delta is the revid line" holds by
construction AND is verified per file inside the tool — the G4-style diff on
F1-mutated files reduces to: receipt `stop_reason=complete` + anomaly count 0.

## 4. DELTA RE-GATE (S5) runbook — run after the watchdog logs "EGRESS BATCH COMPLETE"

Plan line: "delta re-gate (S5): after #1–#6 mutate the corpus — G4-style diff
on changed/added files, G5 sample on them, G6 full dry-run on the mutated
corpus, re-archived accounting lists → receipt; Phase C start = after this
receipt." All steps zero-egress except the S3 re-enumeration (trivial, in the
same gate window).

1. **Egress receipt checks** (`reports/marvel/receipts/`):
   - `revid_backfill_marvel_2026-09-26.json` (+ any `_runN`): `stop_reason=complete`, stamped ≈ 236,626 (missing = 2, titles recorded), anomalies 0.
   - `revid_backfill_mcu_2026-09-26.json`: `stop_reason=complete`, stamped ≈ 35,209, anomalies 0.
   - `fixlist_f3_recrawl_2026-09-26.json`: 4 rows, all `status=written`, each revid ≠ 0, filenames carry the `(pageid)` suffix; record the title→pageid→file map.
   - `fixlist_mcu_topup_f5_2026-09-26.json`: 33 rows, all `status=written`, revid ≠ 0.
2. **G4-style diff on changed/added files:**
   - F1-mutated: per §3 (receipt + anomaly count is the diff record; optionally spot-verify 20 files: key-set identical, only revid changed).
   - F3: for each new owner file sharing a pageid with an old folded file, diff the wikitext — expect identity modulo revid/fetched_at (the re-crawl refreshed the same page). Files whose live pageid differs from the folded files' are new content → to the G5 sample.
   - F5: 33 new files — parse OK, required key set, revid > 0, title matches the list.
3. **Retire the 2 folded F3 files (PROPOSED step — owner-ratifiable at the morning gate; reversible, receipted):** move `What If_ Thor Vol 1.json` + `What If_ Thor Vol 1 1.json` (superseded last-write-win files) into `reports/marvel/receipts/f3_quarantine_2026-09-27/`. Do NOT delete. If the owner declines, keep them and record the 6-files-for-4-titles state in the accounting. (Safe only after step 1 confirms the F3 receipt — and the marvel backfill is complete.)
4. **G5 sample on the changed/added set:** disambiguation/fidelity sheet over the 4 F3 titles + a 10-of-33 F5 sample + the 2 marvel missing (expect live 404 / no-longer-resolves) + the orphan (expect wiki-side deletion on re-enum).
5. **G6 full dry-run** on the mutated corpus: `load_extracted` dry-run, marvel + mcu — expect 0 exceptions / 0 quarantined (09-25 baselines: 35,209 MCU ≈ 96 s, 0/0; marvel full-run zero-exception baseline on record).
6. **Re-archived accounting lists (S3 standing):** same-day re-enumeration (Marvel + MCU; the one trivial egress of the gate) → refresh `marvel_all_pages` / `mcu_all_pages_fresh`, re-run `tools/marvel/title_drift_audit.py` → expect: drift = orphan only, collisions = none (F3 resolved). Projected on-disk totals **with** the retirement: marvel 236,628 + 4 − 2 = **236,630**; mcu 35,209 + 33 = **35,242** (without: 236,632).
7. **Standing gates:** re-run ONLY if code changed since `bc559901` (the 4-green receipt there: pytest 1,345+2xp+3f documented, eval jjk 31/31, span-recall 48,572/48,572 + probe 398/400, canon 10/16·236/236·79.0%). The batch is corpus-only → cite, don't re-run. (The queued O\*N\*E fixture commit carries its own gate run.)
8. **Write `reports/marvel/receipts/delta_regate_2026-09-27.md`** (steps 1–7 outcomes + totals) → **Phase C entry** (per plan: "Phase C start = after this receipt").

## 5. Ops notes (2026-09-27)

- Live monitor `tools/marvel/live_monitor.py` (http://127.0.0.1:8471/, LAN
  192.168.1.3:8471): a JS syntax error (two unterminated template literals in
  the inline script) made the page render as an empty skeleton — "no data"
  reports. Fixed (closing backticks + client-side ETA from the rate sample);
  verified with `node --check` on the *served* JS. Server restarted, 200 OK.
- Watchdog `egress_watchdog.sh` is the sole orchestrator; its F3/F5 stage
  definitions were re-verified against this file's pre-computation (correct
  titles files, `--disambiguate` on F3 only, anchored python-pid matching).