# Receipt — P1.4 5.4 re-adjudication (34 s one-copy, council R6)

Timestamp: 2026-09-12 03:5x IST (run finished 03:55±2). HEAD `af382ee`.

Council R6 (council_unit3_sweep/chairman.md L280-286) + plan P1.4 (L186-188):
at phase close, a 34 s one-copy census re-run re-adjudicates the 5.4 gate
class-by-class — a red class closed by a Phase-1 fix de-scopes the extraction
("only on red census").

## Run

- Tool: `tools/census_dimensions.py --series csm` (v1 bank
  `reports/csm/census_dimensions_csm.json`, 60 items = 6 classes x 10,
  36 distinct character subjects).
- Device: CUDA one-copy, in-process (`CENSUS_DEVICE=cuda`), co-located with
  Qwen 27B (pid 7759, 25.5 GB pre-reserved). `:8000` stopped first (its
  5.3 GB model would OOM the co-location). Qwen survived: alive post-run,
  footprint unchanged (25,808 MiB used of 32,607), util returned to idle.
  The proven 34 s window, re-proven (this run: **33 s**, RC=0).
- Results written in place to `reports/csm/census_dimensions_csm_results.jsonl`
  (the 2026-09-09 run is recoverable from git at `af382ee`).

## Result — 21 RED / 39 GREEN (denominator: 60 questions, 6 classes x 10)

| class | mech-green | reds (ids) |
|---|---|---|
| arc-narrative | 2/10 | arcn-01,02,03,04,06,07,08,10 (8) |
| state-over-time | 5/10 | state-01,02,03,08,09 (5) |
| abilities | 4/10 | abl-01,02,04,05,06,09 (6) |
| appearance | 9/10 | appr-06 (1) |
| causality | 9/10 | caus-03 (1) |
| personality | 10/10 | — (0) |

## Re-adjudication (class-by-class, vs the 09-09 run from git)

- Old reds 21; new reds 21; **the red ID sets are identical** (per-item
  verdict diff: no item changed verdict).
- **CLOSED (de-scoped): NONE.** No Phase-1 fix (R-1…R-7) flipped a red class
  green.
- **NEW REGRESSIONS: NONE.** No green item went red.

## Verdict

- 0 closed reds => **no de-scoping**: the 22-row extraction-gated floor
  (21 `csm-dim-*` census reds, 1:1 with the red ids above, + `csm-char-04`
  R-7x, the PM-contract ability row) stands in full. All 22 remain open,
  `ruling=floor` in `miss_queue_csm_iter1.jsonl`.
- The 5.4 gate stays **LIVE** (the census is red on structural dimensions —
  arc-narrative 8, abilities 6, state-over-time 5, appearance 1, causality 1).
  P2.3 (the D6 extraction) is in scope; the A22 null branch did NOT fire.
- **Pre-registered extraction-pass test (shape; plan P2.3 L363-364 + council
  R6):** post-extraction, (1) the same 400-gate per door
  (`span-recall --series csm --panel reports/csm/panel_csm.json --door qa
  --sanity 400`, roster/narrative at their documented floors), (2) the red
  dimension classes turn green (21/21 `csm-dim-*` rows MECH_GREEN on a
  re-run of this same 60-item census; `csm-char-04` closes), (3) the 200-row
  held-out (`panel_csm.json.heldout.json`) is the out-of-sample leg — a
  memorised panel looks green, the held-out must not.

## Denominator note (owner rule: state the denominator, not just the score)

This re-adjudication recounts the **character-only 60-item census** (36
subjects of 537 pages; 0/537 page coverage per `tools/coverage_report.py`).
It does not widen the denominator: the 5-class 50-item non-character census
(`census_dimensions_csm_v2.json`: chapter_box 232 / episode 12 / volume_box 26 /
story_arcs_box 14 / organization 11) is a separate authoring artifact, and the
coverage-denominator question is pre-registered for the close council in
`CLOSE_COUNCIL_PREREGISTERED.md` (questions 1-4 must be answered on disk
before any Phase-2 GPU-day is committed).