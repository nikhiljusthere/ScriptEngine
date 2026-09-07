# RESIDUALS_p3-gate — 7-item consumption-path map (3C gate, Condition 1 + 4)

Mechanical file demanded by the 3C council (`COUNCIL_p3-gate.md`, Condition 4). One row
per residual: the authoritative harness `sub` label, the 4A/4B **consumption-path
verdict** (Condition 1), and a disposition. Re-reviewed at the **4C gate**.

**4B's inputs (per `flow.md:260-262`):** state intervals are modelled by 4A
(state, start arc, end arc, source quote) and *populated* by 4B from (a) infobox facts
carrying a "(Former)" marker and (b) **synopsis prose**. So a residual is **ON 4B's
path** only if 4A/4B will consume the line it returns *or the page it points to* —
i.e. only its cross-page/synopsis-bearing items qualify. All 7 have `n_reached=0`
(0-content misses), so none is a confident wrong fact to quarantine — the risk is the
cross-page ones, where the state fact genuinely lives on another page.

| # | dim | page | sub | 4A/4B consumes? | reason | disposition |
|---|---|---|---|---|---|---|
| 2 | Cursed Technique | Ui Ui | cross-page | **YES** | top_doc = *Shibuya Incident Arc* synopsis; Ui Ui's state (sealed as a cursed object during Shibuya) is a P4 state fact and 4B consumes that synopsis prose | **quarantine/verify** before 4B populates Ui Ui's interval |
| 4 | History | Mimiko Hasaba | wrong-section | **YES** | top_doc = *Mimiko Hasaba/Synopsis*; 4B consumes her /Synopsis subpage prose | **verify** before 4B (re-scope the fact to the /Synopsis page) |
| 1 | Abilities and Powers | Kensuke Nagino | wrong-section | NO | static ability; 4B reads infobox "(Former)" + synopsis, not ability prose | log; revisit at 4C if a state fact needs it |
| 3 | History | Chiharu Miyaguni | wrong-section | NO | "History" backstory section ≠ 4B's synopsis prose; alive/dead end-state, if needed, comes from structured infobox Status (not a retrieval miss) | log |
| 5 | History | Nanako Hasaba | cross-page | NO | "History" backstory; no synopsis dependency for 4B | log |
| 6 | Personality | Phantom Cursed Spirit | wrong-section | NO | static trait; 4B does not read personality prose | log |
| 7 | Personality | Sara Kozuki | wrong-section | NO | static trait; 4B does not read personality prose | log |

**ON 4B's path: 2 (Ui Ui, Mimiko Hasaba). OFF: 5.** Both ON-path items are the
cross-page/synopsis-bearing ones, exactly as the reviewers predicted.

## Condition 2 — wrong-section root-cause triage

The 5 wrong-sections span **3 different dims** (Abilities, History×2, Personality×2)
with **different top_secs** (root, root, /Synopsis, Appearance, root). Low likelihood
of a single shared router bug; the root-`top_sec` ones (Kensuke, Chiharu, Nanako, Sara)
read as *section-absent/empty-on-page* content gaps, while Mimiko is a subpage re-scope
and Phantom is a wrong-section pointer (Appearance for a Personality question). Real
RED cost is therefore low — mostly content gaps, not one fixable retriever bug. This
further undercuts the RED case.

## Oracle re-label (Condition 5) — parallel, non-blocking

`oracle_2c_summary.json` (sha `a788fa29…`) scored 16/18 (88.9%) but `surprises` shows
**5** `expect=fail → PASS` (A1,A2,A3,B1,B2); the `RED_floorfirst` variant is 11/18.
Re-run the 18 with honest expected/actual labels, reconcile the 5 surprises against this
residual list and the oracle/census gap, and quote the score with its Wilson 95% CI
(≈[67%,97%] at n=18), not a bare 88.9%.

## Gate status

- Owner: comprehension campaign (3C gate).
- Re-review trigger: **4C gate** (oracle B-group; B1/B2 must move).
- Status: 2 items quarantined (Ui Ui, Mimiko), 5 logged.