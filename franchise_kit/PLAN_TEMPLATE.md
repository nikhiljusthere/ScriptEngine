# <FRANCHISE> 100%: campaign plan (<date>)

Reference shapes: `franchise_kit/RUNBOOK_100.md` (phase order + roles), `plan/MARVEL_100_PLAN.md` (the fullest precedent), `plan/CSM_100_CLOSE.md`. Only the final council declares 100%.

**Objective: a <franchise> brain** (RUNBOOK §0). Every line is understood, recallable and traceable, **and** the served evidence supports grounded reasoning: comparisons and match-ups (incl. across realities), hypotheticals, trajectories, group/state questions, with facts cited and assumptions labeled. The four standing gates stay green at every change; JJK and CSM stay byte-identical baselines.

## Denominator annex (re-measure before each phase; a fresh run wins)

| surface | number | measured | regenerate |
|---|---:|---|---|
| wiki articles | | | `allpages` enumeration (then delta-only) |
| pages on disk | | | manifest accounting (on-disk ∪ skipped ∪ failed) |
| tier-0 sentences | | | `chunk-containment` |
| D3 pinned panel | | | `span-recall --make-panel` (hash + sha256) |
| event passages (dry-run, per class) | | | `events-extract --scope all --dry-run` |

## Standing rules
1. No user input at runtime: councils decide walls (`llm-council`, one agent at a time), and records are committed.
2. GPU-only for model work; the resource modes from RUNBOOK §2.
3. Council cadence: every 2–3 todos, the end of every sub-list, every phase gate.
4. Coverage is never a budget variable; no triage model drops work.
5. Commit by named paths; logs go to `/tmp/opencode/`; receipts go to `reports/<series>/receipts/`.

## Phase A: acquire
A1 crawl (stall watchdog, UA, concurrency, egress policy) · A2 accounting closes exactly · A3 revid stamp · A4 audit.
**GATE A** (council): enumeration = denominator, accounting exact, revid spot-check, type histogram (`unknown` < 5%), gates green.

## Phase S: survey and declare
S1 `index --no-embed` · S2 `franchise_kit/tools/survey_wiki.py` → `reports/<series>/SURVEY.md` · S3 declare `overrides.yaml` (types, placement types, narrative fact keys, axis, reality, furniture, content sections, citation grammar, rosters) · S4 engine gaps → design → review → mechanism + key → gates · S5 full index · S6 chunk-containment = 0 unreachable.

## Phase C: understanding
C1 structured facts · C2 category relations · C3 alias/disambiguation alignment · C4 events: dry-run coverage 100%/named → pilot → council (throughput) → full run → failed = 0 → re-resolve participants → time-axis re-derivation (temporal coverage) · C5 relations/abilities (consumer + failing test; sequenced, never skipped) · C6 question bank + census + OOS pre.
**GATE C** (council): D1 every page covered/excluded · D2 depth floors · D3 red list · census/OOS · four gates · containment.

## Phase D: declaration
D1 standing gates per change · D2 blind fresh set (owner-authored) · D3 tier-1 sweep, all doors, final build · D4 consistency = 0 violations · **reasoning bank + owner blind reasoning set** · D5 declaration council → `PHASE_<FRANCHISE>_100.md`.

## Open owner decisions (recorded, never asked at runtime)
- scope boundary (licensed / third-party titles)
- egress / ToS for any non-wiki source
- the order to use when the wiki gives two (in-universe vs publication)
