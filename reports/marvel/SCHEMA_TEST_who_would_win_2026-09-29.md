# Schema test: can the event rows answer "who would win"? (council step 1, 2026-09-29)

The council's first action (`COUNCIL_extraction_optimization_2026-09-29.md`): write 30 real Marvel/MCU match-up questions and check, for each, whether any row the current verb set can emit supports a grounded answer.

**Current verb set** (`EVENTIVE_VERBS`, events.py): fought, killed, awakened, sealed, betrayed, saved, arrived, departed, met.

**What a grounded match-up answer needs** (RUNBOOK §0, "reasoned" layer): (A) direct outcomes between the two, (B) outcomes against shared or comparable opponents (the transitive chain), (C) feats and powers (fact values: `powers`, `abilities`, `weaknesses`, read by C5 and served as passages), and (D) the reality/version, so a cross-Earth match-up compares the right variants (the resolver's `page_real`). Rows supply A and B. Without an outcome, A and B reduce to "they fought", which is not evidence of who won.

## Measured: how much outcome the corpus states and the schema drops

- Marvel `history` values, a seeded sample of 3,000 (20,230 sentences): **8.7% of sentences state an outcome** (defeated, beat, overpowered, bested, lost to, escaped, fled, captured, subdued, knocked out, vanquished, triumphed). `history` alone is 127,035 values / 106.7M chars, so on the order of 100k+ outcome sentences corpus-wide.
- The chosen-model trial rows (uncensored + MTP, 160 pages): 145 of 483 rows are `fought`; **24 of those quotes state who won** ("Magneto knocked him out", "…ultimately f[ought off]…"), and the row keeps only "fought".
- Only `killed` and `sealed` carry an outcome today, and both are terminal: most Marvel fights end in a defeat, capture or escape, not a death.

## The 30 questions

Scoring: **A/B** = can any row the current schema emits carry the decisive evidence (the outcome of a fight between them or against a shared opponent)? `killed-only` = only a death (rare, terminal) carries a winner.

| # | question | realities | direct history? (architect prior, unverified against the corpus) | A/B with current verbs |
|---|---|---|---|---|
| 1 | Hulk (616) vs Thor (616) | same | many fights | no (fought only) |
| 2 | Thanos (616) vs Thanos (MCU 199999) | cross | never | no (shared-opponent outcomes needed) |
| 3 | MCU Scarlet Witch vs 616 Doctor Strange | cross | never | no |
| 4 | Captain America (616) vs Winter Soldier (616) | same | many | no |
| 5 | Wolverine (616) vs Sabretooth (616) | same | many | killed-only |
| 6 | Spider-Man (616) vs Venom (616) | same | many | no |
| 7 | Sentry (616) vs Hyperion (Earth-712) | cross | yes | no |
| 8 | MCU Iron Man (Mark 85) vs 616 Doctor Doom | cross | never | no |
| 9 | Silver Surfer (616) vs Thor (616) | same | yes | no |
| 10 | Namor (616) vs MCU Namor (Talokan) | cross | never | no |
| 11 | Juggernaut (616) vs Hulk (616) | same | yes | no |
| 12 | Magneto (616) vs Ultron (616) | same | yes | no |
| 13 | Deadpool (616) vs Punisher (616) | same | yes | no |
| 14 | MCU Captain Marvel vs 616 Gladiator (Kallark) | cross | never | no |
| 15 | Ghost Rider (Johnny Blaze) vs Mephisto | same | yes | no |
| 16 | Black Panther (616) vs Killmonger (MCU) | cross | never (616 version has) | no |
| 17 | Doctor Strange (616) vs Dormammu (616) | same | yes | sealed-only (partial) |
| 18 | Apocalypse (616) vs Onslaught (616) | same | yes | no |
| 19 | Moon Knight (616) vs Daredevil (616) | same | yes | no |
| 20 | Ultimate Hulk (1610) vs 616 Wolverine | cross | yes (famous) | killed-only (partial) |
| 21 | Galactus (616) vs Celestials | same | yes | no |
| 22 | MCU Wanda vs Agatha Harkness (MCU) | same | yes | killed-only (partial) |
| 23 | Kang the Conqueror (616) vs MCU He Who Remains | cross | never | no |
| 24 | Storm (616) vs Black Panther (616) (sparring/duels) | same | yes | no |
| 25 | Carnage (616) vs Sentry (616) | same | yes (Sentry won) | killed-only (partial: Carnage "torn apart") |
| 26 | Red Hulk (616) vs Thor (616) | same | yes | no |
| 27 | Gladiator (616) vs Superman-analogue Hyperion (616 variant) | cross | yes | no |
| 28 | MCU Thor (Endgame) vs 616 Hercules | cross | never | no |
| 29 | Absorbing Man (616) vs Thor (616) | same | many | no |
| 30 | Emma Frost (616) vs Jean Grey (616) | same | yes | no |

**Result: 0 of 30 questions can be answered from outcome evidence with the current verbs; 5 have partial support through a terminal `killed`/`sealed` only.** 11 of 30 are cross-reality pairs that never met, which can only be answered by the transitive chain (B), and the chain needs outcome rows against shared opponents.

## Verdict (architect, per council step 1)

The verb set must gain outcome verbs before the full run; tuning throughput first would bake a schema that cannot answer the brain's headline question into 360k passages. Minimal extension, declared per wiki in `overrides.yaml` (generic mechanism, inert default; JJK/CSM untouched):

- `defeated`: the subject beat the object ("X defeated / beat / overpowered / bested / knocked out Y"; "Y lost to X" is written with X as subject).
- `escaped`: the subject got away from the object ("X escaped / fled from Y").
- `captured`: the subject captured / subdued / imprisoned the object.

`fought` stays for a fight the passage gives no outcome for. Proof after the extension: re-score these 30 (the target: every same-reality pair with history gets A-rows; cross-reality pairs get B-chains via shared opponents), plus the judged precision of the new verbs on the 160-page sample.
