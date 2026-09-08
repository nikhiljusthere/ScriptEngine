# Wave B · CSM-6 instrument — receipt (sub-1)

Status: DONE (zero-GPU; no model run, no `:8000`, no git; every shell <15 s)

## Deliverables (all on disk, raw receipts inline in CSM6_INSTRUMENT.md)
1. `tools/census_dimensions.py` + `tools/placement_audit.py` + `tools/census_doors.py` parameterized with `--series` (default jjk). JJK default = legacy paths, **byte-identical regeneration proven** (sha of regenerated JJK door sets == frozen files). `placement_audit --series csm` run: bar MET, vacuous (0 events → Phase-2) → `reports/csm/placement_audit_csm.json`.
2. `reports/csm/dimension_map_csm.md` — §12 map regenerated from CSM's own sections (222,761w character prose; Outcomes unmapped: 0 battle pages, no outcome keys).
3. `reports/csm/eight_verb_sample_csm.md` — seed 20260909, 100 sentences of the chapter/episode Summary slice, read-classified, no model: **24/100 covered; 76% cannot be held** by the live 9-verb set (no recurring true gap; JJK's `met` did not transfer).
4. Frozen census sets (stamped, fresh from CSM, never copied from JJK):
   - `census_roster_100_csm.json` = 11 (corpus property, shortfall frozen) + `census_narrative_100_csm.json` = 100;
   - `census_dimensions_csm.json` = 60 Q (6 dimensions × 10), **all 180 expect terms verified verbatim in-store**;
   - `d4_open50_csm.json` verified intact (50, seed 20260909), not edited.
5. T0 pilot: `cli page-sweep --series csm` tier a 175/175 (0 errors, 1,260 structured Qs), tier b 0 (corpus property) → frozen `reports/csm/t0_pilot_csm.json` (843 identity Qs) + `T0_PILOT_CSM.md`. **#1 emergence 843 (vs ~535 expected — richer); #2 survival 843/843 (100%)**. Gap recorded: 62 CSM infobox keys outside the engine vocabulary (near-miss spellings `anime_debut`/`manga_debut`/`japanese voice`/`english voice`) → council at Phase-2 gate.
6. Cross-page census (SQL <15 s) → `reports/csm/crosspage_census_csm.md`: **10,889/11,261 edges cross documents** (mentions 8,586 + grid + infobox relations); events/meaning 0 by Phase-2 design. **Green for Phase 1; no G-CSM-5** (a gap only rides on a red dimension-census result → gate 5.4 → P6).

## JJK-100% invariant
Held. Six JJK baseline files sha-verified unchanged; all JJK code paths branch on `series == "jjk"` for legacy paths/format only.

## Deferred to orchestrator (zero-GPU rule)
- Model-run of the dimension + door censuses on CSM (one-copy CUDA window: stop `:8000` → run → restart). Frozen inputs in place.