# Release R5 — Counterfactual Discriminator (G9b) + Possessive Subject Ranking (G12)

2026-08-27 · git `9fbf9f3` · server started `2026-08-27T01:30:32Z` (fresh R5 code,
check_fresh PASS) · all gates measured against the new code.

## Scope

- **R5-a (G9b):** a counterfactual / negated-conditional query ("What happened
  to Ijichi and Ino if they had not been treated by Shoko?") used to walk the
  narrative route and never surface the factual answer. The discriminator is
  the *conditional clause* (past-perfect `if` clause or `would` main clause),
  not the head verb: the hypothetical now reaches `qa`; the past-factual
  account the eval gold row rests on ("What happened to Nanami during the
  Shibuya Incident?") has no clause and stays `narrative`.
- **R5-b (G12):** "Can Suguru Geto cast Curtain over a weaker sorcerer's
  barrier?" resolved the possessive `a weaker sorcerer's` to the organization
  `Jujutsu Sorcerer` and outranked the named agent. A possessive owner buried
  in a prepositional object no longer wins the subject boost; topic
  possessives ("What is Sukuna's Domain Expansion?") are untouched.
- G11 was deliberately NOT touched this release.

## Changes

### `scriptengine/retrieve/router.py`

R5-a (G9b):
- L242–253 — `_COUNTERFACTUAL` regex + the G9b comment block (placed after
  `_YES_NO_STORY`, before `_STORY_TYPES`):
  `r"\bif\b[^.?!]*(?:\bhad\b|\bhadn'?t\b|\bwere\b)|\bwould\b"` (case-insensitive).
- L358–366 — in `route()`, after the `story_verb` computation:
  `counterfactual = bool(_COUNTERFACTUAL.search(query or ""))`;
  `if counterfactual: story_verb = False`. The clause, not the head verb,
  marks the hypothetical; a past-factual account has no marker and keeps its
  route.
- L415 — `"counterfactual": counterfactual` added to the signals dict
  (after `"story_verb"`), so a miss can be attributed to the discriminator.

R5-b (G12):
- L169–200 — after `_POSSESSIVE` (L167): `_OBJECT_PREPS` frozenset
  (`in/on/at/over/under/with/against/during/before/after/within/across/through/
  onto/into/upon/around/about/off/beside/behind/beyond`) and
  `_topic_owners(query)`, which drops a possessive owner when a preposition
  sits within the three preceding words (punctuation-stripped).
- L673–677 — in `_subject`, `owners = _topic_owners(query or "")` replaces the
  raw `_POSSESSIVE.findall` set: only a *topic* possessive names the subject
  outright.

### `tests/test_router.py`

- L274–286 — `test_a_possessive_in_an_object_does_not_outrank_the_agent`
  (R5-b/G12 regression in `TestSubjectPreference`): the G12 query must resolve
  `Suguru Geto`, not `Jujutsu Sorcerer`; asserts `mode == "qa"`.
- L598 — `TestShokoGaps` docstring rewritten (G9b closed in R5-a, no longer
  "deliberately left narrative").
- L614–638 — `test_the_counterfactual_shapes_reach_qa`: the 7 spec shapes
  (G9b + the 6 R3 counterfactuals) must route `qa` with
  `signals["counterfactual"] is True`.
- L640–668 — `test_the_past_factual_forms_stay_narrative`: the Nanami eval
  gold row + a plain past Gojo account must stay `narrative` with
  `counterfactual is False`.
- The old `test_the_negated_conditional_stays_narrative` (which pinned the
  G9b branch in narrative) is replaced by the two tests above.
- `test_a_possessive_names_the_subject` (L258, 7 topic-possessive cases)
  passes unchanged — topic possessives are untouched.

## Route table (in-process probe, bare queries)

Before = the R3 state that motivated R5 (probe_r3 117/126: all 7
counterfactuals walked narrative and failed; shoko_ieiri 33/34 on the G9b
question). After = R5 probe, 2026-08-27.

| # | query | before | after | subject (after) |
|---|---|---|---|---|
| cf1 | What happened to Ijichi and Ino if they had not been treated by Shoko? | narrative (miss) | qa | Kiyotaka Ijichi |
| cf2 | What would Yuji have become if he had not become a sorcerer? | narrative (miss) | qa | Yuji Itadori |
| cf3 | What would have happened if Yuta had not pretended to kill Yuji? | narrative (miss) | qa | Yuji Itadori |
| cf4 | What would have happened to Megumi if Toji had not committed suicide to protect him? | narrative (miss) | qa | Megumi Fushiguro |
| cf5 | What would have happened if Naoya's domain had been able to detect Maki? | narrative (miss) | qa | Naoya Zenin |
| cf6 | What would have happened if Maki had not taken over the battle against Hanami? | narrative (miss) | qa | Hanami |
| cf7 | What would have happened if Shoko had not sutured Gojo's body for Yuta? | narrative (miss) | qa | Satoru Gojo |
| cf8 | What would happen if Maki used her technique against Hanami? (edge: non-past `would`) | not probed | qa | Hanami |
| cf9 | What would have happened if the Angel were to face Sukuna again? (edge: `were`) | not probed | qa | Sukuna |
| ctl1 | What happened to Nanami during the Shibuya Incident? (eval gold row) | narrative | **narrative (kept)** | Kento Nanami |
| ctl2 | What happened to Gojo during the Shibuya Incident? (plain past) | narrative | **narrative (kept)** | Satoru Gojo |

Observation (not a defect, mode is right): cf8 resolves the subject to
`Hanami` (the named opponent) rather than `Maki` (the agent). Acceptable for
a qa counterfactual about their mutual battle; re-verify if a page-run ever
focuses the bundle wrong on a shape like it.

## G12 subject resolution (before → after)

| query | before, no hint | after, no hint | after, hint=`"Suguru Geto"` |
|---|---|---|---|
| Can Suguru Geto cast Curtain over a weaker sorcerer's barrier? | `Jujutsu Sorcerer` (G12) | **`Suguru Geto`** | `Suguru Geto` |
| What is Sukuna's domain? (topic control) | `Sukuna` | `Sukuna` (unchanged) | — |
| What is Sukuna's Domain Expansion? (topic control) | `Sukuna` | `Sukuna` (unchanged) | — |

The suguru_geto batch already scored 94/94 *with* the page hint; R5-b makes
the bare-query (no-hint) path agree with it.

## Gates (all on the R5 code; canon-run on the fresh server)

1. **Gate 1 — pytest** (in-process): `1068 passed in 90.71s`. Baseline was
   1059; +10 new R5 tests, −1 replaced (`test_the_negated_conditional_stays_narrative`).
2. **Gate 2 — eval jjk** (in-process): `24/24 (100%)` — alias 2/2, fact 6/6,
   lexical 3/3, multihop 3/3, narrative 2/2, roster 2/2, semantic 5/5,
   sourcing 1/1. The Nanami narrative gold row passed.
3. **Gate 3 — canon-run opm** (fresh R5 server, report `2026-08-27-0133`):
   **8/16 exact (no change), 235/237 canon (no change), 78.5% closed-set
   precision (no change)**; 0 confident-and-wrong; fact answers present
   20/20. The run's own check_fresh passed (server start 01:30:32Z > newest
   source mtime), so the numbers measure the R5 router.

## Verification re-runs (fresh server, 2026-08-27-0135 chain)

| batch | before (R1/R3) | after (R5) | expectation |
|---|---|---|---|
| shoko_ieiri | 33/34 (G9b miss) | **34/34 COMPLETE** (`jjk-shoko_ieiri-2026-08-27-0135`) | 34/34 ✓ |
| suguru_geto | 94/94 | **94/94** (`jjk-suguru_geto-2026-08-27-0137`) | 94/94 (no change) ✓ |
| probe_r3 | 117/126 (7×G9b + 2×G11) | **123/126** (`jjk-probe_r3-2026-08-27-0141`) | 124/126 — **one short, see G13** |

The 3 remaining probe_r3 failures: 2× **G11** (location-scoped battle
outcome below the top-k beam — Gachinko ring, Fukutoshin station) and 1×
**G13** (new, below). The 7 G9b counterfactuals all pass the *route* — cf6
("What would have happened if Maki had not taken over the battle against
Hanami?", probe `jjk-probe-r3-105`, subject Toge Inumaki) now reaches `qa`,
but the factual outcome sentence "Maki takes over the battle." on the Toge
page ranks below the qa beam for the counterfactual phrasing (bundle triage:
8 beats, all Maki/Hanami-adjacent, the outcome line absent; answer
content-words `maki`/`battle`/`hanami` present, the exact sentence not
served).

## Parallel work (this release)

- **P1 — `reports/page-campaign/retire_ledger.json`:** 338 retire rows across
  47 jjk batch files (the spec's 339/48 predates the R1 un-retire of mei_mei
  Q001, which dropped that file to 0 retires). One row per retire:
  `batch, id, question, reason, reason_class, owed_by_page, absorbed`.
  `owed_by_page` inferred from the reason and normalized to canonical slugs
  (120 of 338 named; the rest null, as the spec allows when unnameable).
  `absorbed=true` marks the 97 "superseded by page-gen" rows. Class
  distribution: superseded 97, other 101, open_set 59, not_stated 32,
  unchunked 17, cross_page 13, dated_retire 11, battle_scoped 8.
- **P2 — `reports/page-campaign/episode_prose_template.md`:** section-structure
  template for the 59-page episode wave (uniform 11-section layout; Plot
  Details is the prose mass at 402 KB total but EMPTY on Ep 53–59; route-two
  title sourcing — 16 `{{Ref}}` marks across all 59 pages; per-section
  authoring guidance + adversarial/lint loop).

## R5-c — standing LSP diagnostics, cleared

Enumerated (the editor's standing diagnostics across `scriptengine/` and
`tests/`; no type checker is installed or configured in the repo, so the
editor's pyright-class diagnostics are the list):

| diagnostic | site | class | disposition |
|---|---|---|---|
| `"cite" is not defined` | `chronology.py:347` (annotation `"cite.EpisodeIndex | None"`; `cite` was imported only inside two function bodies) | **latent defect** | FIXED: one module-level `from scriptengine.retrieve import citations as cite` (L38); both function-local imports removed. No cycle (citations imports nothing from `retrieve` at module level; `retrieve/__init__.py` is empty). |
| `"beats" is not a known attribute of "None"` | `test_chronology.py:413` | missing None-guard (house style has one at L395) | FIXED: `assert section is not None` after the `scaffold` call. |
| `"relations" is not a known attribute of "None"` | `test_chronology.py:421` | same | FIXED: same guard. |
| `No parameter named "subject"` | `test_router.py` (call at L552) | **stale LSP cache** — `route(..., subject=None)` has existed since R1-b (`router.py:323`) | No code change; verified the parameter; clears on LSP reindex. |

**Found defect (called out separately, per the pass rules):** the
`chronology.beats` annotation referenced `cite` at module scope where it was
never bound — `typing.get_type_hints(beats)` would have raised `NameError`.
Now resolves (verified: `get_type_hints` returns
`episodes: citations.EpisodeIndex | None`).

Nothing deliberately left (the stale-cache item is not a code defect).
**Re-gated after the pass — gate triple unmoved:** `pytest` **1068 passed**;
`eval --series jjk` **24/24 (100%)**; `canon-run --series opm` report
`2026-08-27-0157` on the fresh server (start 01:56:08Z > newest source mtime)
= **8/16 exact, 235/237 canon, 78.5% precision — all "no change"**.

## Still OPEN

- **G11 (R3):** location-scoped battle outcomes land below the top-k beam
  (G5 family). 2 remaining probe_r3 misses. Plan: a location-scope signal in
  the narrative route / beam widening for scoped outcomes, in
  `scriptengine/retrieve/`; re-run probe_r3 after.
- **G13 (new, R5):** the G9b routing fix exposed a retrieval gap — the
  counterfactual *phrasing* ("What would have happened if Maki had not taken
  over…") ranks the factual outcome sentence below the qa beam even though
  routing is now correct (probe `jjk-probe-r3-105`, subject Toge Inumaki; the
  outcome line "Maki takes over the battle." is absent from the 8-beat
  bundle). Same mechanism as G11/G5 (answer in-corpus, low rank for the
  query phrasing). Plan: fold into the G5/R4 retrieval-quality pass with G11
  (outcome-aware query focus); re-run `jjk-probe-r3-105` after. Not fixed in
  R5 (retrieval-quality, explicitly out of this release's scope).
- **G5/R4 (deferred):** buried-fact retrieval quality — answers present in
  the bundle but below the decision line. Plan: the R4 rerank/chunking pass.
- **toge_inumaki 051:** `ability`/`immobilize` absent from the beam (85/86).
  Plan: trace the query end to end; likely a chunking or section-extraction
  gap on that battle section.