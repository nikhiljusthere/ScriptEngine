# Advisor A — measurement validity

**Verdict: SOUND-WITH-CAVEATS as a test of "does the content exist in the
corpus". UNSOUND as support for its own load-bearing conclusion ("the remaining
19 are a bounded, cheap engine-side routing fix").**

## What checks out

1. **Same pass/fail rule.** `tools/census_v2_triage.py:26` and
   `tools/census_dimensions_csm_v2_grade.py:29` import `judge` from
   `tools/census_dimensions.py:72`; same `>=2/3 expect verbatim`, same
   `served_text(bundle)`. No threshold drift, no per-row re-grading.
2. **Provenance clean.** The 21 triage ids are exactly the MECH_REDs of the
   frozen `reports/csm/census_dimensions_csm_results.jsonl` (60 rows, all
   `anchored=false`). Verified set-equal.
3. **No weak-term scraping.** I read `best_hits` for all 21 v1 + 42 v2 rows.
   The expect terms are long verbatim clauses ("reveals himself by declaring
   that he will stop her in the name of justice", "hunt and kill a sixteen-year
   old boy"). Recovery is genuine text presence, not keyword luck. Only mild
   case is `csm-dim-state-02` ('Haruka'), and it hit 3/3 anyway.
4. **The docstring-vs-code contradiction is real.** `census_dimensions.py:5-6`
   claims auto-routing; line 100 passes `mode="qa"`. `build_context` has no
   auto door — `context.py:60` `MODES = {qa,narrative,roster,relations}`, and
   `context.py:149` raises `ValueError: Unknown mode 'auto'` (I ran it).
   Routing lives only in `api/main.py:207-208`, `cli.py:1691`,
   `script/writer.py:487`. So `mode="qa"` cannot route internally. Claim #4 holds.

## What it manufactures

5. **Best-of-3 over doors the router would never pick.** `census_v2_triage.py:37`
   tries only `qa+anchor / narrative / narrative+anchor`. It never tries
   **roster** — which is what `route()` actually chooses for **13 of the 21**
   floor rows. The "recovered by" label predicts nothing about the served path.
6. **I ran the claim's own recommended instrument** (route → build_context with
   the router's subject → main.py's roster/relations fallbacks), CUDA, 18 s:
   **8/21 MECH_GREEN, not 17.** Receipt:
   `reports/csm/receipts/council_floor_remeasure/adv_A_auto_door_21rows.json`.
   Eleven rows the triage called ROUTING stay red under auto: `csm-dim-arcn-01,
   -02, -03, -04, -06, -07, -08, -10, csm-dim-state-02, -03, -08` — i.e. the
   entire arc-narrative class the doc reports as **8/8 routing**.
7. **Anchored recovery is partly unreachable.** `main.py:215` lets auto supply
   `routed.signals["subject"]`, but the router's inferred subject *differs* from
   the census subject on `csm-dim-arcn-02` (Eternity Devil vs Hirokazu Arai),
   `-04` (Justice Devil vs Yuko), `state-03` (Aging Devil vs Nail Fiend),
   `caus-03` (Denji vs Asa Mitaka). Three of the 14 `qa+anchor` recoveries are
   therefore not obtainable by any unanchored caller. Passing the census's own
   `subject` is a real serving path, but it is the *oracle* path: it proves
   content presence, not serviceability.
8. **"CONTENT 0" overstates.** The triage's CONTENT bucket requires *zero* hits
   across all attempts (`census_v2_triage.py:69-70`). PARTIAL rows scored 1/3 —
   `csm-dim-arcb-02` recovered only "a devil kidnapped her cat" and missed both
   other clauses; `csm-dim-abl-02`, `-abl-09` likewise. Under the census's own
   ≥2/3 bar those are content misses. Honest phrasing: "0 rows with *nothing*
   recoverable", not "0 content gaps".
9. **Recommendation 1 is uncallable as written.** "run it at `mode='auto'`"
   crashes (`context.py:149`); the fix must call `route()` first.

## Bottom line

The instrument defect is real and the floor number 21 is not trustworthy. But
the replacement number is not 2 either: measured on the door the claim itself
proposes, the floor is **13 open rows**, of which 2 have no recoverable content
and 11 are unproven — arc-narrative/state-over-time content that *exists* but
that no natural, unanchored question reaches. Do not let "17 of 21 recover"
enter a gate. Correct finding, correct halt on P2.3; the sizing (~2 genuine,
~19 cheap) is not supported by the evidence filed.
