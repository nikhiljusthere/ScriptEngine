# P2.3 + P2.2 red triage (69 widened + 15 bar-audit reds) — 2026-09-17

Grader: `tools/csm/p23_grader.py`, model-unloaded run `p23_grader_20260917-103148`
(receipt in `reports/master-work/`, results committed `3d43a21`). Judge:
≥2 of 3 expect terms substring-matched in the served bundle (MECH_GREEN).
0/538 probe errors; **0 reds flip GREEN under apostrophe/whitespace
normalization** (checked) — no judge artifact class.

## Widened census (qa door): 417/486 = 85.8%, 69 reds

| class | green | reds | red nature |
|---|---|---|---|
| ability-pool | 370/376 | 6 | specific ability subsection absent from the bundle (width), e.g. Falling Devil "Body Control" → served Traumatic Anti-Gravity |
| personality | 10/10 | 0 | — |
| appearance | 9/10 | 1 | width (Appearance section thinnest) |
| causality | 9/10 | 1 | width |
| organization | 5/10 | 5 | mixed: width (members/enumerations) + one content-thin |
| state-over-time | 5/10 | 5 | **content: no interval facts** — bundle serves the character infobox (current state); the during-an-arc state is not in the corpus (JJK precedent: `extra_facts` in overrides.yaml; CSM has none) |
| arc-narrative | 2/10 | 8 | "in order" questions need long event runs; bundle width + narrative door floor (10.74% of line probes) |
| abilities | 4/10 | 6 | enumeration "Every ability of X": ability subsections missed by the bundle; **roster door serves these 4/4 on the bar audit** |
| chapter_box | 1/10 | 9 | **wrong-page ranking**: "Chapter 1" → served "Chapter 124"; numeric-title collisions |
| episode | 1/10 | 9 | **wrong-page ranking**: "Episode 2" → infobox header only, no episode content |
| volume_box | 1/10 | 9 | **wrong-page ranking**: "Volume 13" → "Chapter 13 (Volume 2)" |
| story_arcs_box | 0/10 | 10 | **wrong-page ranking**: "Bat Devil arc" → Bat Devil character page; "Eternity Devil arc" → a *game* page |

Red mass = 37 box-class wrong-page + 27 width/enumeration + 5 state-over-time
content + others.

## Bar audit (26, pre-fix): qa 11/26 (control arm, P-2), auto 14/26 (P-3 supplement)

| class (auto door routed →) | qa | auto | read |
|---|---|---|---|
| appearance (qa) | 4/4 | 4/4 | green both doors |
| causality (qa) | 4/5 | 4/5 | green both doors |
| abilities (roster) | 2/4 | **4/4** | roster door wins 2 — enumeration shape needs the roster door |
| arc-narrative (narrative) | 0/5 | 1/5 | narrative door floor; not a routing fix |
| state-over-time (qa) | 0/4 | 0/4 | **both doors red → content class (interval facts), not routing** |
| personality (qa) | 1/4 | 1/4 | width |

Auto-door wins over the qa control arm: exactly 3 cases (arcn-05, abl-02,
abl-04 — narrative/roster routing).

## Pre-analysis for the P-3 evidence call (R-9 vs the writer bar)

The P-3 firing condition is writer-shaped misroute evidence. What these
numbers say before P2.4:

1. **R-9 (the auto router's 89.1%-to-narrative second misroute, a
   line-probe-axis defect) is not the lever for the writer-question reds.**
   On the 26-case bar, auto already beats forced-qa by only 3 cases; the
   state-over-time class (0/4 both doors) and the 37 box-class wrong-page
   reds are inside-door failures (ranking/content) that a router fix cannot
   reach.
2. **The engine-fix candidate cluster is the 37 box-class wrong-page reds**
   (numeric title collisions Ch/Ep/Vol, arc page vs character/game page) —
   the same family as the sweep triage's 83 defect-rank rows. Per P-3 the
   first route is per-wiki (`series/csm/overrides.yaml`), keeping JJK
   baseline + the four standing gates untouched.
3. **state-over-time (9 reds across both banks) is an extraction-class gap**
   (CSM has no interval facts): Phase-2 extraction campaign territory or a
   per-wiki `extra_facts` declaration (JJK precedent).
4. **P2.4 (writer leg) is the remaining piece of the firing condition** —
   it needs Qwen up. If the writer leg also shows misroute-shaped failures
   (not these ranking/content failures), R-9 fires; if not, the
   writer-bar evidence resolves to "fix the box-ranking + interval-facts
   classes, leave R-9 deferred".