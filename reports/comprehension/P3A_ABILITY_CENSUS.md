# P3.A — the ability-dimension census + the 3B fork decision

Date 2026-09-07. Resume step **X1.g → P3.A** after the X1 close
(`reports/comprehension/COUNCIL_X1.md`). P3.A builds the ability pool, runs the
census, and takes the 3B fork (`plan/flow.md:244-247`). The census harness,
pool builder, and this report all live under `tools/` + here; the pool is data
(`tools/census_ability_pairs.json`), regenerable after any re-crawl.

## The pool — 315 pairs, leaf-based (correcting the council's 300)

The council closed X1 on the figure **300** (dimension, page) rows, a count
taken by *exact-breadcrumb* match on the five ability titles. That count is
**incomplete**: on most character pages the ability sections are a **nested
tree** — a level-2 `Abilities and Powers` parent with level-3 children such as
`Abilities and Powers / Cursed Technique`. An exact-breadcrumb match on
`cursed technique` sees only the flat top-level sections and **silently misses
every nested child**, so 300 under-counts.

The pool is therefore built **leaf-based**: take the last ` / ` component of each
section breadcrumb and fold it into one of the five plan ability dimensions
(`plan/Plan_to_perfection.md:901-915`), so both the flat and the nested form are
caught. Verified against `series/jjk/facts.db` (`sections ⋈ documents`,
`page_type IN ('character','character_synopsis')`):

| dimension (plan §P3) | leaf title(s) | pairs |
|---|---|---:|
| Cursed Technique | `cursed technique`, `cursed techniques` | 88 |
| Cursed Energy | `cursed energy` | 36 |
| Physical Prowess | `physical prowess` | 37 |
| Intelligence | `intelligence`, `great intellect` | 33 |
| Abilities and Powers | `abilities and powers`, `powers & abilities`, `abilities` | 121 |
| **total** | | **315** (across 121 pages) |

- **Not disjoint.** `Abilities and Powers` (level 2) is the *parent* of the other
  four on nested pages, so a page carries the parent **and** its children; a
  character like Gojo yields up to 5 pairs. Read per-page, never per-dimension
  (council blind-spot, verified).
- **One-off sub-leaves left out on purpose.** Sections like `… / Flight`,
  `… / Intangible`, `… / Immense Strength` are specific sub-abilities, not one of
  the five plan dims; the builder (`tools/build_ability_pairs.py`) maps only the
  five and drops the rest, so the pool stays the plan's dimension set, not an
  open-ended section list.
- **Title variants fold in** (`cursed techniques`→Cursed Technique,
  `powers & abilities`→Abilities and Powers, `great intellect`→Intelligence) —
  recorded here and in the builder, so the fold is explicit, not the "sloppy
  ~313" the council flagged.

## The 3B fork decision rule (council step 5 — the previously-undefined piece)

`plan/flow.md:244-247` defines the three moves but no trigger: **3A** widen
`abilities` to all 146 characters (explicit "no abilities" where genuine),
**3B** extract mechanics not just names, **3C** gate (oracle, then Phase 4).
The council flagged that "no branch maps a census % to a decision." The rule:

The census emits, per (dimension, tier) and per dimension, three signals:

- **reach** = fraction of the dim's pairs that are `reached` or
  `reached-uncited` (a beat from the section is in the 6000-token bundle);
  **miss** = 1 − reach (the section is present but no beat reached it).
- **thin** = fraction of the dim's *reached* pairs whose longest reached beat is
  under `THIN_CHARS` (120 chars): the bundle carries a **name**, not the
  **mechanics** (`tools/census_545.py`).
- **oracle A-rate** = the 3C held-out A/F re-run (council: *the sufficiency
  instrument is the oracle, not the reachability %*).

Fork per dimension (a dim can be CT-thin while PP is fine — the fork is
per-dim, not global):

| per-dim signals | branch | why |
|---|---|---|
| **miss high** (miss > 10%) | **3A / retrieval-widen** | the bundle never reaches the section; widen retrieval (and the `abilities` table to 146) *before* any extraction. |
| **thin high** (thin > 30% of reached) | **3B** | the section is reached but the bundle carries names only — extract mechanics per named technique (the schema half already landed 594 names). |
| **reach high, thin low, oracle A ≥ bar** | **3C — gate** | retrieval already delivers mechanics; run the 3C oracle, on green continue to Phase 4. |
| reach high, thin low, **oracle A < bar** | **3B** (oracle-driven) | reached but the writer still cannot answer — the prose/mechanics are not in the bundle; extract. |

Thresholds (10% miss / 30% thin / oracle bar) are campaign-scoping judgments set
**with the census data in hand** and recorded here when set; the *structure* of
the rule is fixed now. The oracle is the gate; reach/thin only decide
**which** of the non-gate branches (3A vs 3B) applies.

## Results (filled on completion)

- **545 re-run (council "one thing first")**: _pending —_ re-run on current code
  (post-`a5e93c3`), commit per-pair results, record the corrected global
  (not-reached 7 → 5, 99.08%) and confirm the two fixed Trivia faults now reach.
- **ability census (315 pairs)**: final clean GPU pass, 2026-09-07. Raw results
  in `reports/comprehension/raw/census_ability_results.json` (315 records).

  **Overall.** reached **264/315 (83.8%)**, reached-uncited **49/315 (15.6%)**,
  not-reached **2/315 (0.6%)**, reached-at-all **313/315 (99.4%)**.

  **Per dimension.**

  | Dimension | n | reached | reached-uncited | not-reached | miss % | thin n | thin % |
  |---|---|---|---|---|---|---|---|
  | Abilities and Powers | 121 | 103 | 17 | 1 | 0.8 | 1 | 0.8 |
  | Cursed Energy | 36 | 31 | 5 | 0 | 0.0 | 0 | 0.0 |
  | Cursed Technique | 88 | 76 | 11 | 1 | 1.1 | 0 | 0.0 |
  | Intelligence | 33 | 23 | 10 | 0 | 0.0 | 0 | 0.0 |
  | Physical Prowess | 37 | 31 | 6 | 0 | 0.0 | 0 | 0.0 |

  **The 2 not-reached residuals.**
  - [Abilities and Powers] Kensuke Nagino — wrong-section (top section "Kensuke Nagino").
  - [Cursed Technique] Ui Ui — cross-page (top section "Synopsis / Entering the Station").

### Fork decision (3B rule)

- No ability dim hits the fork thresholds (miss > 10% or thin > 30%): max miss
  is 1.1% (Cursed Technique), max thin is 1% (Abilities and Powers). Reach is
  high and thin is low across all five dims.
- The 3C held-out oracle (`reports/comprehension/raw/oracle_2c/oracle_2c_summary.json`)
  passed **16/18 = 88.9%**, sha256
  `a788fa29652a58152edf0f2ce16caea626db35d7e4463ec66176b5635a15935e`, which is
  above the 80% bar (>=15/18). Note for transparency: the outcome-category
  sub-rate is 3/4 (75%); 5 oracle rows were surprises (expected-fail -> PASS:
  A1-A3, B1-B2).
- Verdict: **3C-GREEN for all five ability dims** — retrieval suffices, no
  3A-widen or 3B-extract is owed. Proceed to Phase 4 (state over time) on the
  gate.