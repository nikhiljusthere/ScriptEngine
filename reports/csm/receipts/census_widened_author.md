# Receipt: widened census bank authoring (census_widened_csm.json, council #29 Q1/Q2)

Claude GPU session C, 2026-09-17, in parallel with the P2.1 sweep wall (plan/gpu_p21_task.md; chairman #30 item 4). Model-free: `series/csm/facts.db` opened read-only (`mode=ro`), no model, no `:8000` contact, no Qdrant, no GPU; every command < 2 s. Not graded (P2.3 grades it). Not committed yet: no mid-sweep commits (A18); it lands with the post-sweep commit.

## Outputs

- `reports/csm/census_widened_csm.json` — 486 items, `{meta, items}`, `json.dumps(indent=1, ensure_ascii=False)` (the v1/v2 serialization); sha256 `d3888ed0efe65920dabf68389ce7ad7f5a44d84b591915ab79e96ba3aeb2ce33`.
- `tools/csm/build_census_widened.py` — the deterministic builder (a rebuild is byte-identical; re-run after any re-crawl / re-extraction, JJK `tools/build_ability_pairs.py` precedent: the pool is data).
- This receipt.

## Composition (what each ruling maps to)

| part | items | ruling | how |
|---|---:|---|---|
| v1 character census | 60 | Q3 (widened ⊇ the 60-q census) | carried verbatim from `census_dimensions_csm.json` (sha256 `933b8bbc…`) |
| v2 page-type census | 50 | Q1 (5 in-scope page types) | carried verbatim from `census_dimensions_csm_v2.json` (sha256 `2f480c2a…`): chapter_box / episode / volume_box / story_arcs_box / organization, 10 each |
| ability pool | 376 | Q2 (size the pool to the 376 rows) | built here, one item per `abilities` row (1:1 on rowid, 75 characters; kinds {'trait': 180, 'technique': 147, 'item': 28, 'transformation': 21}) |

Carried items are byte-for-byte the v1+v2 item dicts (checked: `items[:110] == v1.items + v2.items`); ids are unique across all 486.

**Q1 reading (question for A, below):** the ruling names the 5 page types but no per-class size. v2 already widens to exactly those 5 types at 10/class — JJK's census shape (`census_3b_dimensions.json`, 14 classes × 10) — so it is carried rather than regenerated. Q2 is the ruling that names a size (the 376 rows), and only the ability dimension is pool-sized.

## Pool method (Q2)

- **Item shape** = census v1 (`id/class/subject/q/expect/source`), class `ability-pool` (kept apart from v1's 10 roster-shaped `abilities` items so per-class tallies do not blend), ids `csm-abl-pool-001…376`, `source` = `{table, character, name, kind, section, abilities_rowid}`.
- **q**: `What is <character>'s <name>, and how does it work?` (`the` before a `… Devil` / `… Fiend` subject, v1 phrasing).
- **expect**: `[name, mechanics phrase, mechanics phrase]`. The name is verbatim in its own section for all 376 rows (checked case-sensitive). The phrases are contiguous slices (25–80 chars, ≥ 4 words, word-boundary cut, parentheticals/citations excluded) of the sentence in the ability's own section that names it — two windows along that sentence, then the text before the name, then the following sentence **unless it names another of the character's abilities** (that is the next entry, e.g. `Dancing:` after `Driving:`, and would grade this ability on another's mechanics).
- **Why name + mechanics under the ≥ 2-of-3 judge:** a bundle that carries only the name is RED — the "thin" signal JJK's P3.A census measured separately (`reports/comprehension/P3A_ABILITY_CENSUS.md`) is built into the grade.
- **Thin sources: 28 items** carry 2 terms (name + the one verifiable phrase — the section says too little, or the only continuation is another ability's entry). They are emitted, never dropped (Q2 sizes to the rows), and flagged `source.thin_source: true`; with 2 terms the judge needs both.

Sample items:

```
csm-abl-pool-002 | What is the Aging Devil's Immense Healing Factor, and how does it work?
    ['Immense Healing Factor', 'While getting sliced repeatedly by Pochita with his chainsaws, it is shown to']
csm-abl-pool-100 | What is Denji's Chainsaw Retraction, and how does it work?
    ['Chainsaw Retraction', 'If he needs the full use of his arms and legs to do certain tasks while in his', "Hybrid form, Denji's chainsaws can be retracted into his body, allowing him to"]
csm-abl-pool-204 | What is Kishibe's Enhanced Reflexes, and how does it work?
    ['Enhanced Reflexes', 'Kishibe has superhuman reflexes, being able to dodge a spear at point-blank', 'range which was thrust through the door in front of him by surprise and react']
csm-abl-pool-299 | What is Reze's Self-Detonation, and how does it work?
    ['Self-Detonation', 'Besides her ability to release explosions from her body, Reze also has the', 'power to turn parts of her body into bombs']
```

## Verification (model-free)

- **Pool, all 1100 terms** pass, under the judge's own matching (`served_text` is `norm()`ed, judge lowercases): (a) `term == norm(term)`; (b) case-sensitive substring of `norm(source section text)`; (c) case-insensitive substring of `norm(chunk.text)` for a chunk of the character's page (the stored unit `/context` serves — a phrase never straddles a chunk boundary).
- **v1/v2 meta check** (exact substring of `sections.text + facts.value + abilities.name + documents.title`): pool fails 1 — `csm-abl-pool-009` `through the following commands: "Swallow it whole" 丸飲み Marunomi: Akane fully` spans a raw `\n` that `norm()` folds to a space; it passes (a)–(c), so it is gradeable as served.
- **Carried v1+v2 (330 terms):** 5 fail the case-sensitive check, 0 fail case-insensitively — `csm-dim-arcb-02`, `-arcb-08` (×2), `-arcb-09`, `csm-dim-org-08`: sentence-initial `The`/`They` lowered by the v2 author, whose SQLite `LIKE` check is ASCII case-insensitive. The judge is case-insensitive, so they grade as intended; recorded, not edited (carried items stay verbatim).
- **Judge proof** (`tools/census_dimensions.py` `judge()`, imported, no model call): served text = the item's source section → **376/376 MECH_GREEN**; served text = `"<character> has <name>."` → **376/376 MECH_RED**. Every pool item is gradeable, and none is green on the name alone.

## Thin-source items (28)

- `csm-abl-pool-002` Aging Devil — Immense Healing Factor (`Abilities / Devil Powers`)
- `csm-abl-pool-024` Aki Hayakawa — Driving (`Abilities / Antemortem Abilities / Skillset`)
- `csm-abl-pool-028` Aki Hayakawa — Blood Consumption (`Abilities / Postmortem Abilities / Devil Powers`)
- `csm-abl-pool-052` Barem Bridge — Blood Consumption (`Abilities / Hybrid Powers`)
- `csm-abl-pool-065` Class President — Sharp Claws (`Abilities / Devil Contracts`)
- `csm-abl-pool-144` Falling Devil — Enhanced Smell (`Abilities / Physical Prowess`)
- `csm-abl-pool-153` Fire Devil — Fire Dispersement (`Abilities / Devil Powers`)
- `csm-abl-pool-190` Justice Devil — Regeneration (`Abilities / Devil Powers`)
- `csm-abl-pool-199` Katana Man — Marksmanship (`Abilities / Skillset`)
- `csm-abl-pool-206` Kishibe — Claw Devil Contract (`Abilities / Devil Contracts`)
- `csm-abl-pool-207` Kishibe — Knife Devil Contract (`Abilities / Devil Contracts`)
- `csm-abl-pool-208` Kishibe — Needle Devil Contract (`Abilities / Devil Contracts`)
- `csm-abl-pool-212` Kobeni Higashiyama — Enhanced Strength (`Abilities / Physical Prowess`)
- `csm-abl-pool-217` Kobeni Higashiyama — Dancing (`Abilities / Skillset`)
- `csm-abl-pool-233` Miri Sugo — Blades (`Abilities / Hybrid Powers`)
- `csm-abl-pool-234` Miri Sugo — Blood Consumption (`Abilities / Hybrid Powers`)
- `csm-abl-pool-240` Nayuta — Bang! (`Abilities`)
- `csm-abl-pool-267` Power — Blood Scythe (`Abilities / Devil Powers`)
- `csm-abl-pool-269` Power — Blood Axe (`Abilities / Devil Powers`)
- `csm-abl-pool-270` Power — Blood Chainsaw (`Abilities / Devil Powers`)
- `csm-abl-pool-275` Power — Acting Skills (`Abilities / Skillset`)
- `csm-abl-pool-286` Quanxi — Bilingual (`Abilities / Skillset`)
- `csm-abl-pool-288` Quanxi — Archery (`Abilities / Skillset`)
- `csm-abl-pool-305` Reze — Bilingual (`Abilities / Skillset`)
- `csm-abl-pool-319` Spear Hybrid — Hybrid Transformation (`Abilities / Hybrid Powers`)
- `csm-abl-pool-330` Whip Hybrid — Hybrid Transformation (`Abilities / Hybrid Powers`)
- `csm-abl-pool-340` Yoru — Immense Healing Factor (`Abilities / Supernatural Abilities / Physical Prowess`)
- `csm-abl-pool-366` Yoru — Spearmanship (`Abilities / Skillset`)

## Open for A

1. **Q1 sizing:** carried v2 at 10/class (JJK 14×10 shape). If Q1 means pool-sizing the page types as Q2 does the abilities (232 + 12 + 26 + 14 + 11 = 295 pages), that is a builder extension, not an edit — say so and it regenerates.
2. **Grader:** `tools/census_dimensions_csm_v2_grade.py` hardcodes its bank path; P2.3 needs a grader pointed at this bank (same judge, `mode="qa"`, CUDA) — a one-constant copy, left for P2.3 rather than written unasked.
