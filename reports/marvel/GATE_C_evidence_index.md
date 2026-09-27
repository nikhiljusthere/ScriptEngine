# GATE C — evidence index (council checkpoint; plan §5 lines 788–794)

GATE C = the D1/D2/D3 pre-checks plus the C-gate evidence list, all on the
post-reindex tree. Filled as evidence lands; the council convenes when the
marvel-side items (post-sweep chain, `tools/marvel/post_sweep_chain.sh`)
close. Zero-egress campaign: every receipt below is produced from on-disk
state.

## D-items (pre-checks) — CLOSED, committed
- **D1 — every page covered or excluded in writing** (commit `113090f3`):
  `receipts/d1_reconciliation_2026-09-27.md` + per-title exclusion files
  `receipts/exclusions_marvel_2026-09-27.jsonl` (42,506) +
  `receipts/exclusions_mcu_2026-09-27.jsonl` (12,868). Zero-egress set
  arithmetic: marvel 279,223 − 42,506 = 236,717 (+ 3 retained F1 orphans =
  236,720 on disk); mcu 48,102 − 12,868 = 35,234 on disk. Every excluded
  title carries a named one-line cause.
- **D2 — archetype depth floors vs populated in-scope sections** (commit
  `a47c5c77`): `receipts/d2_depth_floors_2026-09-27.{md,jsonl}`. Pre-
  registered uniform floor (≥50% of an archetype's pages deep AND median
  infobox-fact count ≥1): every archetype in both wikis PASSES (100% deep).
  Recorded finding (not hidden): marvel is infobox-led for
  character/comic/episode (prose on 5.8%/4.6%/1.0% of pages; disk-verified
  pure-infobox corpus fact, zero parser gaps); mcu is prose+infobox.
- **D3 — zero unfiled engine gaps; red list not empty** (commit
  `6eba2dda`): `receipts/d3_red_list_2026-09-27.{md,jsonl}` — 15 entries:
  the 9 `known_diffs` ledger sections (each cause + disposition named) plus
  live reconciliation (unknown-type residue, disambig_unresolved 742 rows /
  677 distinct recorded-not-dropped, F3 collision files closed on disk, C6
  residue, OOS pre). A live regression the ledger does not name fails the
  gate.

## C-gate evidence
1. **Census baseline + OOS pre-score**
   - MCU — DONE 2026-09-26: bank **32,094 rows / 4,803 pages, complete=True**
     (identity 30,511 · affiliation 1,567 · alias 16; 6 residue rows
     ledgered, all from one thin page) · `oos-freeze` 200 rows (seed-frozen,
     disjoint from the census draw) · census GREEN
     (`reports/mcu/census_c6_results_mcu.jsonl`) · **OOS pre-score 196/200
     (98%)** — floor per CSM annex: post ≥ pre − 2 (= 194).
   - MCU re-score post judge/door fix (`3fb213d9`) + post-reindex: DONE —
     **196/200 MECH_GREEN (98%), 0 errors**
     (`reports/mcu/census_c6_oos_pre_mcu.jsonl`,
     `/tmp/opencode/oos_rescore_census_c6_mcu.log`). The 4 pre-reds are
     stable across the fix; the new pre baseline (196) equals the
     2026-09-26 one — floor post ≥ pre − 2 = 194.
   - Marvel — PENDING the post-sweep chain (bank → oos-freeze → census →
     oos-score pre; steps 3–6 of `tools/marvel/post_sweep_chain.sh`).
2. **`unknown`-type residue report** — DONE:
   `receipts/unknown_residue_2026-09-27.{md,jsonl}` (marvel 529/236,720 =
   0.223%; mcu 616/35,234 = 1.748%; cause: absent infobox template in
   528/616 of them + 1 named marvel `Infobox Episode` edge).
3. **Four standing gates** — DONE 2026-09-27 13:27–13:35, chain exit=0
   (`/tmp/opencode/gateC_4gates.log`): pytest **1,367 pin** (1,362 passed +
   2 xpassed + the 3 documented `:8000`-down env trio) · eval jjk 31/31 ·
   span-recall jjk 48,572/48,572 · canon opm 10/16 exact · 236/236 ·
   79.0%.
4. **`chunk-containment` (tier 0), 0 unreachable, both wikis**
   - MCU — DONE post-reindex (with the `content_sections` promotion,
     commit `0720df76`): **coverage 100.0000%**, 430 boilerplate sentences
     excluded per policy (`/tmp/opencode/containment_mcu_post_reindex.log`).
   - Marvel — PENDING post-sweep chain step 2 (re-index step 1 first, since
     the promotion changes what the chunker indexes).

## D1 (phase D) standing-gate marvel set — tracked to the chain
- `eval --series marvel` + `eval --series mcu`: chain steps 7–8 (GPU,
  serialized after C6).
- `chunk-containment --series marvel`: chain step 2.
- census OOS re-score floor: chain step 6 (post ≥ pre − 2; a drop of 3+
  voids — CSM annex).
- CC mapping-gate SQL (§B gate 3): N/A this gate — `cc.db` unchanged since
  the B0/B1 seed (6 episodes); it runs after any cc.db change.
- Standing guards: 0 green→red counter-flips (any flip rolls back its
  mechanism alone); blind-set accuracy must not trail bank movement — the
  D2 blind-fresh set scores against the frozen build (Phase D). Protocol
  tooling ready: `tools/marvel/blind_panel.py` (sealed hash-pinned panel →
  corpus-blind authoring → `validate` freezes the corpus-verified set to
  `reports/marvel/blind_fresh.jsonl` → `score`). The panel seals after the
  chain's `bank` step (complete bank only); the questions are authored by a
  NON-executing party (Plan_to_perfection D4).

## Tree stamps at GATE C
- Re-index: MCU done (events/meaning empty → no `--force`; emphasis
  re-derived deterministically, reindex lossless — `build.py:201-206`).
  Marvel pending chain step 1.
- Parser-evolution re-emit (F7 + current parser): MCU 16,706/35,209 ·
  marvel 7,929/236,628 files rewritten; `preserved_key_violations: []`.
- `roster_route_words` guard fix (commit `37a799ca`): the JJK-era arc/saga
  roster-guard false positive on marvel/mcu (6/99,591 tier-a titles; the
  sweep hard-errored the 4 `Arc*` pages it had reached — re-swept clean on
  resume, report 13,589 pages / 0 errors at chain-launch time).