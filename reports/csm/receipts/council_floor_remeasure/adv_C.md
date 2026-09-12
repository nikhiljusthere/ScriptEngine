# Advisor C — instrument design: how to fix the census

## 0. A blocking fact the claim doc missed

`mode="auto"` **cannot be passed to `build_context`**: `MODES = {"qa",
"narrative", "roster", "relations"}` (`scriptengine/api/context.py:60`) and
:148 raises `ValueError`. `auto` exists only inside the endpoint
(`scriptengine/api/main.py:207-249`): `route()` → mode → **subject forwarding**
(`main.py:215`, `request.subject or routed.signals["subject"]`) → **roster→
narrative fallback** (:228) → **relations→qa fallback** (:243). So "run the
census at auto" is not a one-word edit, and a census that re-implements those
four steps will drift from `/context` — the exact defect we are fixing.

## 1. I measured what `auto` actually does (model-free, SQLite router)

On the 21 floor rows, `route()` picks **roster for 13, qa for 8, narrative for
0**. `router.py:627` — `wants_chronology()` → `Route("roster", "asks for the
story in order")` — claims every "…during the War Devil arc, **in order**?"
question. Roster returns members (29/31/14/31/14), so the :228 fallback never
fires. Judging the first 8 arc-narrative rows under true auto: **0/8
MECH_GREEN** — all still red, though triage called them ROUTING.

**Therefore: switching to auto is honest, but it is not a recovery.** The
doc's "17 of 21 routing" is a *best-of-4 oracle with gold anchors*
(`tools/census_v2_triage.py:37-40`), an upper bound no caller can reach. The
true floor lies between 2 (oracle) and ~16 (auto). Both numbers currently on
the table are wrong.

## 2. The design

**(a) Extract, don't duplicate.** Move `main.py:207-249` into
`scriptengine/api/context.py` as
`serve_context(paths, query, mode="auto", *, subject=None, …) -> (bundle, trace)`,
where `trace = {"requested", "routed_mode", "why", "routed_subject",
"fallback_from", "final_mode"}`. `/context` becomes a thin caller (behavior
byte-identical); the census calls the same function. One code path, testable.

**(b) Door-aware verdicts, not a door swap.** `tools/census_dimensions.py:99`
gains `--door {qa,auto,all}`, **default `qa`** (old runs reproduce exactly).
`all` runs qa → auto → narrative → roster and stops at first green. Record:

```json
{"id":"csm-dim-arcn-01","verdict":"MECH_RED","primary_door":"auto",
 "doors":[{"door":"qa","verdict":"MECH_RED","hits":0},
          {"door":"auto","routed_mode":"roster","why":"asks for the story in order",
           "routed_subject":"Fake Chainsaw Man","verdict":"MECH_RED","hits":0},
          {"door":"narrative","verdict":"MECH_GREEN","hits":2}],
 "class":"ROUTER_DEFECT"}
```

Classes: `SERVED` (auto green) · `ROUTER_DEFECT` (auto red, some door green) ·
`ANCHOR_ONLY` (green only with gold subject) · `CONTENT` (no door green).
**Only `CONTENT` may size extraction.** `ROUTER_DEFECT` sizes an R-8 router
fix-class — start at `router.py:627` (chronology must not claim a
character-scoped "in order" question with a story-typed subject).

**(c) Anchoring: no.** The primary verdict must never pass the bank's gold
`subject`; auto already infers one, and that inference is the thing under
test — it matches gold on only 16/21 (`arcn-02` infers *Eternity Devil* vs gold
*Hirokazu Arai*; also `arcn-04`, `state-03`, `caus-03`). Keep `--anchored` as a
**diagnostic** producing `ANCHOR_ONLY`, never a headline score.

**(d) Comparability: version, never mutate.** The v1 results file was already
overwritten in place once (`reports/csm/GATE.md:38-39`; prior version only at
`af382ee`). Stamp `instrument_version` in every record and write to
`census_dimensions_<series>_results_v<N>.jsonl` — `v1` = qa-only (frozen,
read-only, the "39/60" / 21-red gate record stands as *a qa-door score*), `v2` =
door-aware. Never compare across versions; `GATE.md` re-labels the old row
"21 qa-door reds", superseded not deleted. Re-run v1 alongside v2 once to
publish both on the same corpus.

## 3. Must not change

`_census_paths()` JJK isolation (`tools/census_dimensions.py:48-57`), the
frozen JJK bank/results bytes, `judge()`'s ≥2-of-3 rule
(:72-81 — changing it invalidates every bank at once), and the `--door qa`
default. JJK's 100% is a qa-door number; it is re-measured only as an added v2
column, never by overwriting `reports/comprehension/census_3b_results.jsonl`.
