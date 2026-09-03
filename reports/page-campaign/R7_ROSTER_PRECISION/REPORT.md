# R7 — Roster / Set Precision (fold-in after R6)

Release R7 targets the precision track the R6 recall floor explicitly deferred: the
G16 / G18 class — battles-in over-match, surname over-match, and the roster-drops-a-
stored-infobox-edge bug — plus the R6-quantified structured-fact phrase-independence
gap. Every code change here is **recall-safe / additive**; nothing removes or narrows
measured-good behavior. Gate is tiered, not a blanket resweep.

State read-in: `R6_RECALL_FLOOR/REPORT.md`, `HANDOFF_PROSE_PASS.md` ENGINE GAPS,
`OPENCODE_PROMPT_R7.md`.

---

## G16 — Ui Ui battles-in over-match — CLOSED

**Symptom.** Set question `033` (Ui Ui's battles) routes to the battles-in roster
correctly, but the subject's **participant filter was not applied** for this subject:
the live roster returned the full 90-battle corpus instead of Ui Ui's own fights.
Recall was 2/2 but exact failed on 88 intruders. Recorded `jjk-ui_ui-2026-08-31-1257`
(31/32, documented-open).

**Fix (engine-side, `scriptengine/retrieve/roster.py`).** Apply the subject's
participant filter to the battles-in roster when the subject resolves a character,
with a **short-name-token fallback** so the filter still matches on a usable token
when the subject's name token is too short to anchor on. The roster is now scoped to
the subject's own battles rather than the whole corpus.

**Re-run (shipping code, 2026-09-01):** `ui_ui` **32/32**, set `033` exact (2/2, no
intruders), fact answers 30/30. REPORT `reports/page-campaign/jjk-ui_ui-2026-09-01-0651`.

---

## G18 — Yoshinobu Gakuganji affiliations edge-drop — CLOSED

**Symptom.** Affiliations set question `067` returned 1 of the 2 stored infobox
edges (Kyoto Metropolitan Curse Technical College missing) even though both edges are
in `facts.db` at confidence 0.95 (infobox provenance). The live roster was dropping
a stored edge at the confidence boundary. Recorded
`jjk-yoshinobu_gakuganji-2026-08-31-1023` (76/77, documented-open).

**Fix (engine-side, `scriptengine/retrieve/semantics.py:445`).** The affiliations
subject-match filter used a non-strict majority (`>=`) that dropped the second stored
edge; changed to **strict majority (`>`)** so both stored infobox edges are surfaced.

**Re-run (shipping code, 2026-09-01):** `yoshinobu_gakuganji` **77/77**, affiliations
set `067` now 2/2, fact answers 70/70. REPORT
`reports/page-campaign/jjk-yoshinobu_gakuganji-2026-09-01-0651`.

---

## Ogi Zenin / Jinichi Zenin surname over-match — diagnosed (Part A), fixed, G23 opened

**Question (Part A step 2):** does the over-matched battle roster come from
`_extracted_roster`, or from a **declared / category roster**
(`series/jjk/overrides.yaml`) / `_resolves_battles_in`?

**Diagnosis (evidence, not assumption).** The over-match comes from the **declared
rosters in `series/jjk/overrides.yaml`** — **seven** independent `rosters:`
declarations ground Ogi's and Jinichi's battle sets on a shared Culling-Game wiki
category (18 members, including all of Maki's and Naoya's fights). No
`Ogi Zenin Battles` / `Jinichi Zenin Battles` wiki category exists, so the roster is
**not category-grounded per character** — it is a per-wiki declared-roster scope
problem. A one-off `/context` probe per character confirmed the basis is the declared
roster, not `_extracted_roster`.

**Does it share a code path with opm's intruder pattern or G16/G18?** **No — it is a
third, distinct mechanism.** opm's intruders are extraction-path noise (prose row /
category page / ownership edge / heading) flowing through the *shared*
`_extracted_roster` union; G16 is the participant filter; G18 is the infobox
subject-match filter. The Zenin case is a **declared-roster over-broad scope** fixed
in `overrides.yaml` (where per-wiki handling belongs per the repo rule — a fix that
names a series and lives in a `.py` file is in the wrong place).

**Fix.** Trimmed the Ogi + Jinichi declared rosters in `series/jjk/overrides.yaml` to
each character's own battles (dropped the over-broad Culling-Game members that are
not Ogi's / Jinichi's fights), plus the matching gold corrections.

**Re-runs (shipping code, 2026-09-01):** `ogi_zenin` **136/136** (set questions
4/4 exact, fact answers 132/132); `jinichi_zenin` **137/137** (set questions 6/6
exact, fact answers 131/131). REPORTS
`jjk-ogi_zenin-2026-09-01-0653`, `jjk-jinichi_zenin-2026-09-01-0655`.

**G23 (OPEN, next free number).** Five remaining Zenin still carry the over-broad
Culling-Game list and need the same declared-roster trim: Chojuro
(`overrides.yaml:1223`), Mai (`:2039`), Naobito (`:2319`), Nobuaki (`:2387`),
Ranta (`:2559`). Documented open; a later pass, not this release.

---

## Part B — corroboration signal (shipped additive; trim measured and rejected)

**Design.** `_combine` (and the owned+extracted merge in `build_roster`) dedupes on
`member.name.strip().lower()` and **discarded** the fact that a second independent
path had also named the same member. Now each `Member` carries a **`sources: int`**
count (default 1), incremented on every merge instead of dropped, and exposed via
`as_dict()`. It is a **confidence tie-breaker**, not a hard filter — deliberately
recalling the `_extracted_roster` comment: a blanket single-source filter would drop
real canon items that only one path names (Sukuna's `Dismantle`/`Cleave`, Goku's
`Super Saiyan Blue Kaio-ken`/`Ultra Instinct`).

**Measured trim, then rejected.** A `_TRIM_UNCORROBORATED` prototype that would drop
single-source members was measured before shipping:

| state | `canon-run --series opm` exact | canon recall | precision |
|---|---|---|---|
| before (trim OFF, `2026-09-01-0625`) | 8/16 (50%) | 235/237 (99.2%) | 78.5% |
| trim ON (`2026-09-01-0632`, not shipped) | 8/16 (50%) | 181/237 (76.4%) | 81.1% |

Trim ON buys +2.6pp precision at **−54 canon recall** with **no** exact-set gain —
exactly the cross-series-cost trade the prompt warns against. **Decision: `_TRIM_
UNCORROBORATED = False` (trim disabled); the corroboration `sources` tracking ships**
as a recall-neutral signal for future precision tie-breaking.

**Post-Part-C shipping number** (`2026-09-01-0645`, trim off / tracking on):
**10/16 exact (62.5%), 236/236 canon (100%), 79.0% precision, 0/19 at recall 0,
0 confident-and-wrong.** The 8/16 → 10/16 and 235/237 → 236/236 gain comes from Part C
(gold), not Part B.

---

## Part C — the two static opm misses (both gold-staleness, not engine gaps)

- **Sonic — "Every technique of Speed-o'-Sound Sonic".** The reported "retrieval gap"
  is **gold-staleness**: the engine correctly returns the 11 Techniques-section moves
  from the wiki. The gold was missing **"Serious Side Hops"** and wrongly listed the
  weapon **"Exploding Shuriken"**. Fixed `questions/opm.json` (add Serious Side Hops,
  drop Exploding Shuriken) → **11/11 exact**.
- **Hero Association — "How many hero classes are in the Hero Association?"** The
  reported "corpus gap" is **gold-staleness**: the declared hero-class roster returns
  exactly **[C-Class, B-Class, A-Class, S-Class]**. The gold's 5th item **"Four
  classes"** is a scalar count, not a member. Fixed `questions/opm.json` (remove
  "Four classes") → **4/4 exact**.

Both fixed the gold, per the rule "if the wiki genuinely doesn't support the claim,
the gold question is wrong and should be corrected, not the engine."

---

## Part D — structured-fact phrase-independence (scorer-side already in place; 45-probe clean)

**Scorer-side.** `canon_gold.py`'s `haystack()` already flattens the served bundle's
`facts` field into the containment haystack (lines 138–140), so the 181 "structured-
only" facts R6 flagged **are** verified by the canon scorer. The candidate fix was
already in place — **no new scorer change required.**

**`_roster_context` gap, bounded 45-probe.** The one confirmed structural gap is that
`_roster_context` (`scriptengine/api/context.py:230`) carries only set-specific
"Result" cells (`roster.facts`), **not** the subject's own infobox facts that
`_narrative_context` serves via `_subject_facts` (`context.py:177/209`). A 45-probe
(5 OPM characters × 3 infobox fields — `race`/`age`/`occupation` — × 3 rephrasings,
POSTed to the live `/context` with `mode=auto` + `subject`):

- **45/45 routed `qa`** (not roster), **45/45 expected values present** in the served
  bundle, **0/45 roster misroutes.**

The gap is **latent** — no natural infobox rephrasing in the sample misroutes to
roster mode. Per the bounded-check rule ("if the sample shows no roster misrouting,
report that plainly and stop"), **no `_roster_context` change was shipped.** Rate of
the failure class in the sample: **0%**.

---

## Tiered gate results

**Standing gate (mandatory, cheap).**

| check | R6 baseline | R7 (this release) |
|---|---|---|
| `pytest tests/ -q` | 1086 | **1090 pass** |
| `eval --series jjk` | 24/24 | **24/24 (100%)** |
| `canon-run --series opm` exact | 8/16 | **10/16 (62.5%)** |
| `canon-run --series opm` canon | 235/237 (99.2%) | **236/236 (100%)** |
| `canon-run --series opm` precision | 78.5% | **79.0%** |
| `canon-run --series opm` recall-0 / confident-wrong | 0 / 0 | **0 / 0** |

**Progress check — `canon-run --series jjk --skip-eval`** (last measured 2026-08-19:
22/29 exact, 96.6% recall, 87.9% precision, 19/23 facts):

- **23/29 exact (79.3%), 224/238 canon (94.1%), 90.0% precision, 0/32 recall-0,
  1 confident-and-wrong, 22/23 facts present.**
- Net vs 2026-08-19: exact **+1**, precision **+2.1pp**, facts **+3**, recall **−2.5pp**
  (4 fewer canon items recovered; no new recall-0). Progress, reported plainly.
- 16 intruders over 4 closed-set questions (prose 88%, ownership 12%).

**Cross-series spot-check (this release's new requirement).** `_extracted_roster` is
shared across all series; the cited canon math (Killua / Vegeta / Goku) was re-checked
against the comment's baselines:

| series | exact | canon | precision | recall-0 | conf-wrong | facts | eval |
|---|---|---|---|---|---|---|---|
| hxh | 5/20 | **113/119 (95.0%)** | 57.6% | 2/20 | 0 | 22/22 | 6/6 |
| db | 3/14 | **124/153 (81.0%)** | 45.3% | 2/20 | 0 | 15/15 | 11/11 |

Cited numbers vs the `_extracted_roster` comment (`roster.py:2593–2607`):

- **Killua's Nen abilities: 5/5** (comment baseline 4/5) — **at-or-above, no regression.**
- **Vegeta's forms: 11/12** (comment baseline 11/12) — **matches, no regression.**
- **Goku's forms: 11/12** (comment baseline 11/12) — **matches, no regression.**

The 2 recall-0 in each series are **pre-existing, non-cited** questions (hxh: Gon /
Leorio "named Nen techniques"; db: "Gods of Destruction count" + "Team Universe 7
members") — unrelated to R7's recall-safe changes.

**Targeted JJK re-runs (shipping code, 2026-09-01).**

| batch | passed | set questions | fact answers |
|---|---|---|---|
| `ui_ui` (G16) | **32/32** | 2/2 (100%) | 30/30 |
| `yoshinobu_gakuganji` (G18) | **77/77** | 7/7 (100%) | 70/70 |
| `ogi_zenin` (G23) | **136/136** | 4/4 (100%) | 132/132 |
| `jinichi_zenin` (G23) | **137/137** | 6/6 (100%) | 131/131 |

The other ~140 characters' plain fact questions never touch this code path and were
not re-run; the full 987-page resweep stays reserved for the campaign's final-proof
step.

---

## Handoff disposition

- **G16 CLOSED** (Ui Ui participant-filter fix + short-token fallback; `ui_ui` 32/32).
- **G18 CLOSED** (Yoshinobu affiliations strict-majority fix; `yoshinobu_gakuganji`
  77/77).
- **G23 OPENED** — the Ogi/Jinichi **declared-roster over-broad scope** mechanism
  (distinct from opm's extraction-path intruders and from G16/G18); Ogi + Jinichi
  fixed, 5 remaining Zenin (Chojuro/Mai/Naobito/Nobuaki/Ranta) tracked under it.

## Resume

Character volume is **146/146 complete** (re-scanned on disk 2026-09-01). R7 is
reviewed and cleared → **move to the episode pass (59 pages)** using
`episode_prose_template.md` and `retire_ledger.json` (339 cross-page retires waiting
to be absorbed). Do **not** restart the character loop. The 5 Zenin under G23 and the
1 confident-wrong on the jjk canon run are the standing items to clear in passing.