# JJK PROSE PASS — FINAL RECORD (consolidated, 2026-09-07)

The single final record of the JJK page campaign: the structured layer plus the
prose pass, which took Jujutsu Kaisen to 100% on every in-scope narrative page
type. Consolidated from `HANDOFF_PROSE_PASS.md` (126 states, deleted 2026-09-07
— recoverable from git history @ `faf6ce6`), the wave reports in this
directory, `CHECKPOINT_ROSTER_BUILD.md`, `STATUS.md` and the
council/drift records under `reports/comprehension/` + `plan/`. If a fact below
conflicts with an older document, this file and the live artifacts it points at
win.

> **Relation to the overall goal.** This pass is the *reachability/coverage*
> layer: every in-scope factual line is now a gold question and the engine
> serves it. The project's goal is **D6 comprehension** — the corpus
> *understands* everything about a character (what each line/fact/prose/event
> means, whether it is an event, where it sits on the anime's timeline, all
> structured dimensions) — a different, separate layer (plan §2 D5 vs D6;
> "current goal" in `docs/ROADMAP.md`). Do not read this pass as the goal
> being met. The live remainder and the checkable definition of "100%
> comprehension" are `reports/comprehension/COMPREHENSION_REMAINDER.md` (§2, §5).

## Final state (2026-09-07)

- **All in-scope narrative page types at 100%** (`COVERAGE.md`, regenerated
  2026-09-07 by `tools/coverage_report.py` — never hand-edit it):
  chapter 304/304 (941/941 questions), technique 149/149, character 146/146,
  battle 90/90, character_synopsis 72/72, episode 59/59, event 9/9,
  story_arcs 9/9, plus location / item / organizations / simple_box / species /
  occupation. **In-scope content remainder: 0 pages.**
- **Headline: 893 / 987 pages covered (90.5%) · 29,819 active questions.** The
  uncovered remainder is out-of-scope media / nav / release pages (volume,
  blu_ray_dvd, music, game, series, anime, novel, stage_play, residual
  `unknown`) — not authorable prose.
- **Standing gates, all green:** `eval --series jjk` = 31/31 · `canon-run
  --series opm` = 10/16 exact, 236/236 canon, 79.0% (identical to the 2C-era
  baseline — the pass moved nothing it should not have) · `pytest tests/ -q` =
  1,239 · `span-recall --series jjk` = 48,572/48,572 (0 unreachable, rc=0) ·
  `audit` gates all PASS.
- **545-prose census** (the five prose dimensions over every cast page,
  `reports/comprehension/STEP5_CENSUS_545.md`): 98.7% reached, **0 main-cast
  misses**; the 2 genuine faults (Trivia/Kenjaku beam-starves-floor;
  Trivia/Noritoshi-Kamo qualified-title disambiguation) fixed retrieval-only
  and gated. Remaining not-reached rows are thin minor-profile pages (depth
  limit), not fixable misses.
- **G30 CLOSED** (`ee9fa2e`): the narrative short-prose floor no longer drops a
  page's own 12-word Epilogue `Summary` — the chapter wave closed 940/941 →
  **941/941**, the last open gap of the pass.
- **Structured layer:** declared rosters 797 → **1,355** (the 558-entry
  chapter-tranche delta, `5d3f3f4`), verified against `facts.db`; Finding A
  (generic 40-member roster fallback) closed and probe-verified. **P4.A:**
  interval facts (a character's state *during* an arc, which the infobox's
  current-state read cannot express) are durable via `extra_facts` in
  `series/jjk/overrides.yaml` + `_apply_declared_facts` in
  `scriptengine/index/build.py` (`61311c2`) — re-landed on every `index`, so
  the S-group oracle stays green across re-index.

## The method (why it reached 100%)

1. **The verbatim rule.** Every question's `answer` is a verbatim substring of
   the wiki text; the scorer (`scriptengine/eval/canon_gold.py`, used by
   `page-run`) does word-boundary containment of the answer inside the folded
   served bundle (beats + passages + facts + relations + members, `norm()`
   diacritic/plural folding). A paraphrase fails even when the idea is right —
   so golds are copied, never rephrased. A claim that is a cross-page fact is
   **retired** with a reason (appended to the batch's `retired` list), never
   forced onto a page that does not carry it.
2. **Method correction (user mandate, 2026-08-24 — the load-bearing one).**
   When a natural question fails, **diagnose the root cause and fix the gap —
   never rephrase the question to dodge it.** Four classes: (a) gold error →
   fix the answer in-lane; (b) cross-page fact → retire; (c) router gap → fix
   `scriptengine/retrieve/router.py`; (d) retrieval/chunking gap → fix
   `scriptengine/index/…`. An earlier "rephrase until it routes" era left
   masked gaps (32 masked rephrases later **reverted** to natural phrasings
   once the engine was fixed and the batches re-ran clean) — that mistake is
   what the mandate forbids.
3. **Faithful scorer replica.** The probe must replicate `page-run`'s scoring
   exactly: `mode="auto"` + `token_budget=60000`, flatten beats+passages+facts+
   relations+members, `norm()` fold, word-boundary containment. A qa-mode
   probe *masks* routing failures (it bypasses the router) — using it as the
   check was a recurring false-green source.
4. **The fast system (pilot 2026-08-24).** Per-page-type templates
   (`character_synopsis_prose_template.md`, `episode_prose_template.md`,
   `battle_prose_template.md`, `chapter_prose_template.md`,
   `content_pages_template.md` in this directory) + a fast inline
   author-verify-page-run loop; subagents carry the volume (dispatches D1–D16
   of the synopsis wave ran in parallel a/b splits, fourteen consecutive
   first-run clean sweeps). Band floors: 1–2 questions per non-empty section,
   2 on sections ≥ the section word band.
5. **Gate discipline.** Every engine change re-runs the triple (`pytest` +
   `eval jjk` + `canon-run opm`); `span-recall` after every `index`; every gap
   fix lands with a named regression test (the `TestG30ShortProseSection`,
   `TestScrollBox`, `TestPandaGaps` families). A fix is not done until gated.

## The crucial engine fixes (kept here on purpose)

These are the defects that stood between the corpus and 100%; each is fixed
in-engine and gated, so they should never need re-discovering:

- **Router — scope-word set misroute (G1).** "What are Nanami's two greatest
  assets in battle?" resolved the declared `Nanami Battles` roster on the
  *scope word* "battle" → 0-beat roster. Fix: `_resolves_a_set` strips a
  prepositional scope phrase (`_SCOPE_PHRASE`) before the roster probe; a set
  counts only when its noun is the wh-object.
- **Router — discourse-opener wh-anchor (G2/G2b).** "Despite…", "Although…",
  "If…", "According to…, what…", "Using Playful Cloud, what…" dropped the
  wh-anchor and fell to narrative. Fix: `_LEADING_DISCOURSE` set + a
  non-anchored `_WH_ANY` search + the comma rule (wh after the first comma) +
  `using` in `_LEADING_PREPS`.
- **Router — `whose` (G4/G4b/G7).** `Whose` was not a wh-word; the
  effect-form "What happens to targets in X's domain?" read `happens` as a
  narrative verb. Fixes: `whose`/`who's` in `_WH`; `_EFFECT_ON` matches only
  present/will/would `happens to/if` (past forms stay narrative — the gold
  "What happened to Nanami during the Shibuya Incident?" is untouched).
- **Router — bare-roster confidence default (G6).** `build_roster` returns a
  bare `Roster` with the dataclass-default `confidence="declared"` when it
  finds nothing; the probe read that as "the set exists". Fix: the probe
  requires a found set to carry a basis or a rendered member.
- **Router — OOA list-asks (G28 `b976cf8`, G29 `063c7c4`).** "Which
  characters appear in X?" on non-chapter recovered pages misrouted to
  narrative (under-enumerating the Order-of-Appearance list 1/12, 4/12); now
  routes `qa` under `auto`. The copular plural-ask follow-on ("Who are X and
  Y?" / "What are the curses … revealed to be?") closed the
  single-valued-predicate hole in the plural-ask path.
- **Parser — `{{Scroll box |content=}}` recovery.** `wikitext.py` built
  transparent-template candidates from positional args only, so the named
  `|content=` form dropped 91 boxes / 979 character names (83 empty
  "Characters in Order of Appearance" sections). Fix:
  `TRANSPARENT_NAMED_PARAMS = {"scroll box": {"content"}}` (layout params
  `height`/`width`/`name` stay excluded); `TestScrollBox` pins it. All 372 OOA
  sections now carry content; zero layout leaks, zero positional regressions.
- **Chunker — short-prose-section floor (G30, `ee9fa2e`).** The G15 20-word
  beat floor dropped a page's *own* short `Summary`/`Synopses`/`Plot` section
  (the 12-word Epilogue `Summary`). Fix in `scriptengine/retrieve/narrative.py`
  (the narrow `G30` exemption set, `narrative.py:60-65`): a page's own short
  prose content section beats; furniture still floors. The sibling Trivia
  chunking gap (a Trivia bullet not served for a generic question) was
  likewise fixed and gated — `personality-01`/`trivia-01` went 29/31 → 31/31.
- **Roster — chapter-tranche delta (Finding A).** 558 declared-member entries
  (overrides 797 → 1,355) so every chapter/episode page's OOA and
  Battles-&-Events list resolves through the roster door instead of the
  generic 40-member fallback (which overlapped 0/40 with Ao no Sumika's real
  13 names).
- **P4.A — durable interval facts.** See final state. The mechanism (per-wiki
  data in `overrides.yaml` `extra_facts`, generic upsert in `index/build.py`)
  is the standing pattern for any interval fact a future pass declares: a
  node absent from the build is skipped, never invented; each (node, key) is
  replaced, never appended.

## Where the history lives (after the handoff deletions)

- **Per-run artefacts:** `reports/page-campaign/jjk-<page>-<ts>/`
  (`REPORT.md` + `run.json` + `scores.json` each; now fully committed).
- **Campaign history:** `STATUS.md` (rounds 1–3, OPM + JJK waves, the 545
  census milestone), `CHECKPOINT_ROSTER_BUILD.md` (the open/closed findings
  ledger: Finding A/B, G29, G30), the `CHAPTER_PROSE_*` /
  `EPISODE_SWEEP_PROGRESS` wave records, the per-type templates above.
- **Live coverage:** `COVERAGE.md` (regenerate; never hand-edit).
- **Engine-gap + council records:** `reports/comprehension/` (`GATE.md`,
  `COUNCIL_*.md`, `COUNCIL_HISTORY.md` ledger) and `plan/` (`drift_log.md`
  §4 = current position, `flow.md` = trunk structure).
- **Deleted 2026-09-07 (git-recoverable @ `faf6ce6`):** `HANDOFF.md`,
  `HANDOFF_JJK_ONLY.md`, `HANDOFF_OPM.md`, `HANDOFF_ROUND2.md`,
  `HANDOFF_PROSE_PASS.md` (this directory), `HANDOFF_continuity-scaffold.md`
  (comprehension), `docs/CONTINUATION_BRIEF.md`. Windows-era environment
  notes in them (`E:\` paths, PowerShell 5.1) are obsolete on this native
  Ubuntu machine; the current environment contract is `CLAUDE.md`.