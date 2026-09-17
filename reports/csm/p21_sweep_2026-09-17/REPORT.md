# CSM P2.1 sweep: the full panel, post-R-8 (2026-09-17)

The full 17,181-line panel through all four doors (qa, narrative, roster,
auto), plus the 200-line held-out set through auto: the A17 measurement R-8
was waiting for. The runner exited 0; nothing halted.

## Provenance

| | |
|---|---|
| runner | `tools/csm/p21_sweep.sh`, launched 07:24:42 IST, exit 0 at 09:16:28 (1 h 52 min; the estimate was ≈ 3.7 h) |
| tree | HEAD `4b60043` (R-8 fixes `aada154`; gate window green on this tree, `receipts/r8_gate_window.md`) |
| service | one `:8000`, pid 178118, CUDA, whole card, never restarted; Qwen down throughout (`mode=off`) |
| inputs | panel sha256 `cf72135f…`, heldout `604dc8ca…` (A26 frozen, pre-check verified), 17,181 / 200 rows |
| A18 | all 4 pre-R-8 sanity ledgers wiped at start; every one of the 68,924 rows is stamped `4b60043`, device `cuda` |
| canary | +10 min: qa 2,126/2,149 HIT (98.93 %), 0 ERROR; sanity pre-passes identical per row to the pre-wipe ledgers (400/400) |
| receipt | `reports/master-work/p21_sweep_20260917_072442_RECEIPT.md` (committed); `_run.log` + per-door/sanity logs beside it are local only (`*.log` is gitignored) |
| ledgers | `reports/span-recall/csm/sweep_{qa,narrative,roster,auto}_e3d73720.jsonl`, `sweep_auto_ec15e0d8.jsonl` (heldout) |

## Results

| door | HIT | MISS_DOC | MISS_SPAN | TRUNCATED | ERROR | hit rate | sanity-100 | wall | s/probe |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qa | 16,920 | 160 | 101 | 0 | 0 | **98.48 %** | 95 % | 79 m | 0.28 |
| narrative | 1,846 | 9,342 | 105 | 5,888 | 0 | 10.74 % | 35 % | 6 m | 0.023 |
| roster | 133 | 12,542 | 264 | 4,242 | 0 | 0.77 % | 2 % | 10 m | 0.035 |
| **auto** | 2,651 | 8,893 | 124 | 5,513 | 0 | **15.43 %** | 37 % | 15 m | 0.052 |
| auto heldout | 28 | 107 | 0 | 65 | 0 | **14.00 %** | – | 0.5 m | – |

Hit rate is over the full panel (§2a trap 3). **The first 100 panel lines were
not representative of the weak doors:** every sanity-100 number overstated its
door (narrative 35 → 10.7, roster 2 → 0.8, auto 37 → 15.4), while qa's sample
understated it (95 → 98.5).

## A17 grading

- **qa (the regression target): rate PASSES** — 98.48 % ≥ the 97.5 % bar. The
  sanity 95 % was the sample, not the corpus. Closure for qa is "miss file
  empty", and the file holds **261 rows** (below) — the bar is met, the class
  is not closed.
- **narrative / roster (documented floors):** 10.74 % and 0.77 %, re-measured
  far under the sanity figures A17 recorded. Mechanical residual tables by page
  type and section are in `residuals_by_type.json`; the per-residual class +
  reason triage A17 asks for is not done here.
- **auto (the product number): FAILS** — 15.43 % against the 97.5 % bar,
  and the held-out 14.00 % agrees, so this is not a memorised panel.
- **R-8 did not move it.** On the 100 sanity lines, auto's routing changed on
  **0 of 100** rows versus the pre-R-8 run (`2f67222`), and the verdicts are
  identical per row. R-8 fixed the "story in order" over-selection of roster;
  this is the other misroute.

## The routing leak (the second misroute, now sized)

| router picked | lines | share | HIT | hit rate |
|---|---:|---:|---:|---:|
| narrative | 15,302 | **89.1 %** | 1,621 | 10.6 % |
| qa | 1,030 | 6.0 % | 1,007 | **97.8 %** |
| roster | 815 | 4.7 % | 22 | 2.7 % |
| relations | 34 | 0.2 % | 1 | 2.9 % |

Heldout: narrative 178/200 (89.0 %, 10.1 % hit), qa 10/10 hit, roster 0/11.

Per line, auto against forced qa (`auto_routing.json`): **14,293 lines miss on
auto and hit on forced qa**; 24 hit on auto and miss on qa; 2,627 hit on both;
237 miss on both. Door choice accounts for essentially the whole gap: forced
qa alone serves 98.48 %.

GATE.md recorded this at 81/100 as "recorded, not yet labelled". The full panel
sizes it at 89 %. **Scope, as in the step-0 addendum:** these are verbatim
line-lookup probes, not writer questions; the claim is bounded to that shape.
Whether narrative *should* take them — or whether the panel's shape is what a
writer asks — is the labelling question, not answered here.

## qa miss file — 261 rows, mechanically pre-sorted

`misses_qa.jsonl`, one row per miss with a **mechanical** shape class
(`tools/csm/p21_sweep_report.py` docstring). It groups the rows for the
row-by-row reading; it does not assign reasons.

| pre-triage class | rows | what it means |
|---|---:|---|
| rank-miss | 120 | MISS_DOC, no nearer explanation — ranking |
| span-miss | 88 | page reached, the line not among its beats |
| corpus-duplicate | 17 | the line is verbatim on another page too — an ambiguous query |
| near-page | 16 | MISS_DOC but the subject's sibling page came back (`Denji` for `Denji/History`) |
| table-row | 13 | the probe line is a pipe-delimited table row, not prose |
| short | 7 | under 10 words |

By page type: character_history 104, character 101, `unknown` 20, chapter_box 14,
organization 10, music 4, story_arcs_box 3, saga_box 3, episode 1, establishment 1.
By top section: Synopsis 107, Plot 64, Abilities 22, Summary 15, Trivia 10,
popularity-poll sections 12.

## A7 — do the misses shift a D6 dimension?

The 26 bar-audit cases (`bar_audit_p14_preregistered.json`) each anchor one
panel line; `a7_dimension_check.json` looks each up in every door's ledger.

- **qa: 25/26 HIT.** The one miss is `csm-bar-pers-04` (Fami, Personality,
  MISS_SPAN — narrative serves it).
- **auto:** arc-narrative 1/5, state-over-time 1/4, causality 0/5, abilities 3/4,
  appearance 4/4, personality 2/4.

**What stops a clean A7 call:** the bar audit was **pre-registered in P1.4 but
never graded** — no results file exists (`PHASE_A_COMPLETE_AT_FLOOR.md` §3 is
the authoring pull-in only). "Re-grade only if the misses shift a dimension"
has no graded baseline to shift from. On the qa door the anchored lines barely
move (one personality miss); on the auto door three of six classes are mostly
unserved. Which door P2.2 grades against, and whether that grading is now owed
outright, is A's call.

## Owed / for A

1. **The second misroute decision** (receipt's A17 input): 89 % of line lookups
   go to narrative and 10.6 % of those are served. The data to size a guard is
   here. The design is closed only for the sweep; a router change owes the four
   gates + `eval --series jjk` again.
2. **qa miss file**: 261 rows to triage row by row (A17 "miss file empty").
3. **narrative / roster residual triage** (class + reason) per A17. The
   mechanical tables are the starting point.
4. **P2.2 bar audit**: never graded, so A7 cannot be settled (above).
5. **A14 / P2.3**: the widened census bank is on disk (`census_widened_csm.json`,
   486 items, `receipts/census_widened_author.md`), and it needs a grader pointed
   at it. The A14 comprehension step must fire before `PHASE_B_COMPLETE`.
6. **Stale docs**: `GATE.md` "Gate debt (undischarged)" and the CLAUDE.md
   gate-1 pin (1,321) predate the R-8 window. The ledger (`GATE_LEDGER.json`)
   is current.

## Files in this directory

| file | contents |
|---|---|
| `REPORT.md` | this report |
| `door_verdicts.json` | per-door verdict counts, hit rate, commit + device stamps |
| `auto_routing.json` | auto full + heldout: router choice × verdict; auto vs forced-qa per line |
| `misses_qa.jsonl` | the 261 qa misses, mechanically pre-sorted |
| `residuals_by_type.json` | narrative / roster / auto verdicts by page type and top section |
| `a7_dimension_check.json` | the 26 bar-audit anchored lines × door verdict |

Regenerate: `python tools/csm/p21_sweep_report.py --out reports/csm/p21_sweep_2026-09-17`
(model-free, < 1 s).
