# JJK Full-Wiki Page Campaign (2026-08-24)

**Goal:** extend the page-campaign (`page-gen` → verify → prose → gates) from the
single Angel cluster to the whole JJK wiki, using the **characters-first,
tiered-depth** strategy the user approved. The deterministic structured half
sweeps every in-scope page; the subagent prose/verify pipeline runs as a
tracked, sequential campaign on the characters.

This plan builds on `2026-08-23-page-gen.md` (the `page-gen`/`page-merge`
stack, tasks 0–10 done; Angel task 11 mid-flight). It supersedes the
single-cluster scope of that plan's task 11.

## Scope (987 JJK pages, by `documents.page_type`)

| type | count | tier |
|---|---|---|
| character | 146 | **A — full pipeline** |
| character_synopsis | 72 | B — structured-only |
| battle | 90 | B — structured-only |
| technique | 149 | B — structured-only |
| story_arcs | 9 | B — structured-only |
| event | 9 | B — structured-only |
| **worked total** | **579** | |
| chapter 304, episode 59, volume 35, blu_ray_dvd 20, music 20, item 20, location 14, misc | 408 | skipped (unless requested) |

- **Tier A — full pipeline (subagent-driven, sequential, Rule A):** all 146
  characters. Includes the 14 already-covered character redos.
- **Tier B — structured-only (batched, no subagents):** the 433 character-centric
  non-character pages above, plus the 4 non-character redos.
- **Redo set (18):** the existing JJK batches — characters `angel`, `aoi_todo`,
  `sukuna`, `satoru_gojo`, `kento_nanami`, `nobara_kugisaki`,
  `toji_fushiguro`, `naoya_zenin`, `megumi_fushiguro`, `maki_zenin`, `choso`,
  `kenjaku`, `yuji_itadori`, `yuta_okkotsu`; non-characters `culling_game_arc`,
  `shibuya_incident`, `story_arcs`, `volumes_chapters`. All 18 are re-run
  through the current pipeline: structured half regenerated, hand-authored
  questions retained, re-gated.

Observed generator behavior per type (smoke-tested 2026-08-24):
character → rich (Angel: 22 Qs); technique → decent (Antigravity System: 9);
battle → **over-generates** (Choso vs. Naoya Zenin: 107); story arc / event →
near-empty (2–3 Qs, mostly prose). Subtask 0.2 tunes the battle case.

## Subtask 0 — engine prereqs (one-time, TDD + re-gate)

- **0.1 `extra_sections` wiring.** `cli.py page_gen` must read the existing
  batch's `prose:`-noted questions, group them by section path, and pass them
  as `extra_sections` to `generate_structured` (and the batch as `existing`
  to `write_batch`). Without this a re-run's coverage ledger ignores the prose
  questions and the 100% section-coverage gate can never pass. Helper
  `prose_extra_sections(batch) -> dict[str, list[dict]]` in `page_gen.py`,
  unit-tested.
- **0.2 Battle-page over-generation.** Investigate why one battle page yields
  107 structured questions and cap/fix it so a battle page's structured half is
  its own infobox (outcome/place/date/chapters/arc/sides/powers) + the
  battles-set, not a combinatorial blow-up. Unit-tested.
- **0.3 Re-confirm the gate triple** after 0.1+0.2: `pytest tests/ -q`,
  `eval --series jjk` (24/24), `canon-run --series opm` (baseline
  8/16 + 235/237 + 78.5% + 20/20). Any `.py` change re-gates.

## Subtask 1 — structured sweep (batched, no subagents)

- **1.1 Driver.** A page-set source (Tier A + Tier B titles, derived from
  `documents.page_type`, deduped) plus a `page-sweep --series jjk
  [--tier a|b]` command: runs `page-gen` over each page, writes each
  batch/decl/coverage/verify, and emits a per-page status report (structured-Q
  count, uncovered-section count, rosters, errors). Resumable via a run
  manifest; a page already swept is skipped unless `--force`.
- **1.2 Run Tier B** (433 pages). Capture the report.
- **1.3 Triage** the report: 0-Q pages, over-generated pages, generator
  errors. Engine defects → TDD fixes + re-gate; data gaps → note in STATUS.md.

## Subtask 2 — full-pipeline campaign (sequential, one subagent at a time)

- **2.0 Order** the 146 characters: the 14 redos first, then by importance
  (link centrality in the `edges` table, then word count).
- **2.k Per character** (Rule A: dispatch one subagent, wait, next):
  1. `page-gen --series jjk --page <Char>` (structured half, now feeding
     `extra_sections`).
  2. **Phase 2** — ONE subagent verifies the batch against the raw crawl
     (`series/jjk/wikitext/<Char>.json` + battle-page wikitexts); gold errors
     → fix the batch, never the retriever; returns clean/fix/retire counts.
  3. **Phase 3** — ONE subagent authors `prose:<section-path>` questions for
     the uncovered content sections (poll counts stay prose-only, from the
     Trivia prose) + any prose-derived roster decls.
  4. **Phase 4** — re-run `page-gen` (ledger refresh) → `page-merge` →
     `page-run --series jjk --batch <slug>` to 100% → 100% section-coverage
     gate (no section left uncovered or unexplained) → six-class scan.
  5. STATUS.md row (structured Qs, prose Qs, rosters, retires-with-reasons,
     coverage result, reconciliation note).
- Every subagent prompt carries Rules A + B verbatim (graphify-first).

## Subtask 3 — record

- **3.1** `reports/page-campaign/STATUS.md` rows for all worked pages + a
  handoff note listing the remaining Tier-A queue and any triage findings.

## Discipline (carried from CLAUDE.md + the page-gen plan)

- **Rule A:** exactly one subagent at a time; every subagent phase dispatches
  a single subagent and waits. **Rule B:** graphify-first
  (`graphify-out/GRAPH_REPORT.md` / `graph.json` before grepping). Both
  restated verbatim in every subagent prompt.
- Every `.py` change: TDD first, then the gate triple.
- Gold error → fix the question, never the retriever; record the why.
- Commit engine + tests only. Campaign state (`questions/_jjk_page_*`,
  `series/jjk/overrides.yaml`, `reports/page-campaign/`) stays uncommitted.
- `page-run` to 100% means triaging every miss against the wikitext: rephrase
  inside the routing contract or retire with a reason.