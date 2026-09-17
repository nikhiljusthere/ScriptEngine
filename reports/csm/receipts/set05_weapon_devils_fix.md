# csm-set-05 "Every Weapon Devil" fix + closure8 full sweep receipt (CSM Phase 2, 2026-09-17)

- Timestamp: 2026-09-17T21:21:00+05:30 (IST)
- git HEAD (sweep tree): `f49e0d2 tests: CSM scope golden 227 -> 473 (council #32 P-6 re-scope, drift D30)`; `series/csm/overrides.yaml` is a **working-tree change (M, uncommitted)** — the fix below is not yet committed (no commit requested). Last commit that touched overrides.yaml: `58639a3` (D33+D34 floor_section_cap).
- Mode: :8000 on CUDA, Qwen 100k profile (ninfer-serve) co-located on the same card — the sanctioned Phase-1 steady state. Qwen alive at start and after the sweep (`:18080` ok). No CPU restore owed.

## The regression

FAIL8's Weapon Devils union was `7 hybrid page-titles + 3 devil names = 10` members.
csm-set-05 "Every Weapon Devil" is a **closed 7-item set** golded by devil name
(each aliased to the human it fused with). The exact rule is
`found==canon AND members==canon` (`canon_gold.py:199`), so 10 declared members
vs 7 canon read as 3 intruders → **70% precision** (this is FAIL8 Risk #2, line
134–137 of `FAIL8_ROOT_CAUSES.md`, materialized exactly as predicted).

## The fix

`series/csm/overrides.yaml` → `Weapon Devils` roster reduced to the **7 devils**:

```
members: [Katana Devil, Bomb Devil, Bow Devil, Longsword Devil,
          Flamethrower Devil, Whip Devil, Spear Devil]
```

None of the seven has its own article, so the router emits the declared names
anyway; the infobox `members` fact (Katana/Bomb/Bow Devil, `csm-pg-weapon_devils-002`)
is a 3-subset of the seven, so the campaign `weapon_devils` batch stays green.
Rationale comment lives in the YAML (overrides.yaml:239–247). `load_overrides`
(`config.py:301`) is uncached, so the running :8000 picked up the change with no restart.

## Verification — closure8 sweep (live, :8000 CUDA)

Command: `cd /home/goblin/ScriptEngine && PYTHONPATH=/home/goblin/ScriptEngine ./scriptengine/.venv/bin/python /tmp/opencode/closure8.py`
(output: `/tmp/opencode/closure8_result.json`)

**14/14 campaign batches PASS** (8 targets + 6 no-regression):

| kind | batch | score | set exact |
|------|-------|-------|-----------|
| TARGET | death_devil | 14/14 | 8/8 |
| TARGET | fami | 12/12 | 6/6 |
| TARGET | devil_hunter_club | 4/4 | — |
| TARGET | four_horsemen | 3/3 | — |
| TARGET | quanxi_and_the_fiends | 3/3 | — |
| TARGET | tokyo_devil_detention_center | 5/5 | — |
| TARGET | tokyo_special_division_5 | 4/4 | — |
| TARGET | weapon_devils | 4/4 | — |
| NOREG | american_thugs | 3/3 | — |
| NOREG | anti_makima_squad | 2/2 | — |
| NOREG | chainsaw_man_church | 4/4 | — |
| NOREG | family_burger_restaurant | 5/5 | — |
| NOREG | prophecy_of_nostradamus | 3/3 | — |
| NOREG | tokyo_special_division_4 | 4/4 | — |

**The at-risk bank sets (the regression's blast radius) are all GREEN:**
- `csm-set-05` "Every Weapon Devil" → **exact 7/7, 100% recall + 100% precision, declared** (regression fixed)
- `csm-set-04` "Every Four Horsemen" → **exact 4/4**
- `csm-fact-15` (the weapon-devils infobox fact) → **present** (facts 18/18)

**Bank headline: set exact 15/19, fact present 18/18.** The 5 residual
set-partials are all **pre-existing / known floor, not regressions from this fix**
(their subjects are untouched by the 4 overrides edits — establishment→org,
the 4 org rosters, Weapon Devils, Four Horsemen):

| set | kind of gap | status |
|-----|-------------|--------|
| csm-set-01 (Denji forms) | precision (over-inclusion) | pre-existing |
| csm-set-02 (Power abilities) | precision (over-inclusion) | pre-existing |
| csm-char-01 | precision (over-inclusion) | pre-existing |
| csm-char-03 | precision (over-inclusion) | pre-existing |
| csm-char-04 (Makima abilities) | recall — missing "Contract with the Prime Minister of Japan" | documented extraction-gated floor row (D22) |

The closure8 bank line reads FAIL only because its criterion is whole-bank
100% exact; those 5 keep it red. That is the known CSM floor, out of scope for
this closure.

## Verdict

csm-set-05 regression **fixed and verified** (7/7 exact); zero new regressions
across the 14-batch sweep (8 targets + 6 no-regression all PASS) and the
at-risk bank set (set-04, set-05, fact-15) is fully green. The 4 standing
gates (pytest / eval-jjk / span-recall-jjk / canon-run-opm) are unaffected by
a working-tree overrides.yaml edit (no engine hunk); re-run them only if the
fix is promoted to a commit.