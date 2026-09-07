# COUNCIL_p4-rescope — Phase 4 (state over time): the 4C gate is vacuous — re-scope it

**Verdict: RE-SCOPE 4C.** Replace the vacuous "B1 and B2 must move" criterion with a
newly **pre-registered arc-scoped earlier-state probe set** (wiki-pinned ground
truth, each verified to fail against live `/context` before any build). Build 4A
**only** against probes that actually fail, reusing `events` + the infobox fact
floor (not a wiki-wide 4B table), behind a hard serving-path spike. Re-label
A1/A2/A3/B1/B2 now as a recorded v2 (P3.3C condition 5). Re-run regression after
any 4A build. **Not** option A (build 4A as specified — dead table: no serving
path, nobody's scope), **not** option B (close 4C — closes an untested gap while
the re-label stays owed).

- **Subject:** Phase 4 (state over time). 4C's success criterion "B1 and B2 must
  move (fail→pass)" is **already met at the 2C baseline** — the B-group is 4/4
  PASS (run sha `a788fa`, 2026-09-06; DB-verified again 2026-09-07). The gate as
  written discriminates nothing. What should Phase 4 actually test, and how much
  of 4A/4B is real work vs. already done?
- **Date:** 2026-09-07
- **Council:** 5 advisors → 5 anonymized peer reviewers → chairman synthesis, run
  in parallel (the council working agreement in `CLAUDE.md`). The user directed
  this fork to the council (2026-09-07). No transcript file was saved, so the
  chairman synthesized from the recorded response sets of the two rounds;
  de-anonymized positions follow the round-2 mapping (A=Outsider, B=Executor,
  C=Contrarian, D=First Principles, E=Expansionist).
- **DB-verified before recording** (standing rule). Evidence:
  `reports/comprehension/raw/oracle_2c/oracle_2c_summary.json` (run sha
  `a788fa…`, the internal run-content hash; the on-disk file hash is
  `d712adfa…` — both recorded, cite the run sha), `series/jjk/facts.db` census
  re-verified 2026-09-07, `plan/flow.md:251-264`, `plan/ORACLE_v1.yaml:88-128`.

## Gate question

Phase 4 spec (`plan/flow.md:251-264`): *4A* model intervals (state, start arc,
end arc, source quote); *4B* populate from infobox `(Former)` facts + synopsis
prose; *4C* gate = re-run the B-group, "B1 and B2 must move (fail→pass)". The
oracle's B-group (`plan/ORACLE_v1.yaml:88-128`) is:

- **B1** "Is Satoru Gojo still alive?" (`expect: fail`, `check: contains`) —
  cross-page by its own note; the answer lives on the Culling Game (Arc) page.
- **B2** "What is Suguru Geto's current occupation?" (`expect: fail`,
  `check: value`) — `ground_truth` `Jujutsu Sorcerer (Former) Curse User`.
- **B3** "How old is Nobara Kugisaki in the Modulo timeline?" (`expect: pass`).
- **B4** "Who won the Tokyo Jujutsu High Special Grade exam?" (`expect: pass`).

DB-verified at the 2C baseline (run sha `a788fa`, 2026-09-06): **B1 PASS
(`contains`)** — the Angel-page Gojo quote is in the bundle; **B2 PASS
(`value_match`)** — Geto's infobox `occupation` `Jujutsu Sorcerer (Former)
Curse User` is served verbatim by the 2-prep fact floor (the same bundle also
serves `Status: Deceased` + `Affiliation: Tokyo Jujutsu High (Former) Geto's
"Family"`); B3/B4 PASS. So "B1 and B2 must move" is **already met**: the gate
is vacuous as written.

The un-modeled gap, confirmed by the 2C evidence, is **when a state held**
(intervals over arcs), not terminal values: the infobox `(Former)` facts + the
qa fact floor already serve *terminal* state. A writer asking "Was Gojo alive
at the START of the Culling Game?" or "What was Geto's status DURING Shibuya?"
gets the terminal fact, which is wrong for that framing.

## DB-verified evidence

| Measure | Value | Note |
|---|---|---|
| 2C oracle B-group | **4/4 PASS** (B1 `contains`, B2 `value_match`, B3, B4) | run sha `a788fa`, 2026-09-06 |
| 2C oracle total | **16/18 = 88.9%** (Wilson 95% CI ≈ [67%, 97%] at n=18) | 5 of the 2 "failures" are surprises |
| 2C surprises | **5** — `A1, A2, A3, B1, B2` (`expect=fail` → PASS) | labels miscalibrated; 88.9% is inflated |
| RED_floorfirst variant | **11/18 (61%)** | B1 regressed → its PASS is beam-dependent |
| `facts.db` census (re-verified 2026-09-07) | facts **10 064** · events **2 748** · documents **987** · nodes **1 557** · relations **821** · abilities **594** · sections **7 601** | `events` already carries `arc_key`/`arc_index`/`quote`/`temporal`/`time_rank` |
| Arc-keyed documents | **10** (arc pages: Tokyo Jujutsu High, Shibuya Incident, Culling Game; 6 volume pages; `Story Arcs` hub) | `events.arc_index` is the usable temporal order; the infobox previous/next arc chain is circular |
| Phase 4 spec | `plan/flow.md:251-264` (4A intervals / 4B populate / 4C B-group re-run) | B1/B2 "must move" |
| Oracle B-group | `plan/ORACLE_v1.yaml:88-128` | file header: `editable_by_executing_agent: false` |
| Live API | **DOWN** at `http://127.0.0.1:8000` (curl `/health`, 2026-09-07) | 4C probe runs need it up (GPU-first start per working agreement) |

## Advisor positions (one line each)

- **Contrarian — (C) tightened.** B1's PASS is *fragile*: it's a cross-page
  case by the oracle's own note, and it regressed under `RED_floorfirst`
  (11/18). A 4C gate anchored on miscalibrated probes has zero discriminating
  power. And 4A as specified is a **dead table**: nothing routes arc-scoped
  questions to it, the router is in nobody's scope, and the qa fact floor
  already serves terminal state. Pre-register the probes → verify each fails
  today → gate 4A on a serving path + audit → only then 4B. Re-label the
  surprises either way.
- **First Principles — probe first, minimum model.** What actually fails
  today? The terminal-state slice of 4A/4B is **already done, uncredited**
  (B2's `value_match` on the fact floor). Author 2–3 arc-scoped questions where
  the terminal fact is *wrong for the framing*; if they pass → close 4C
  honestly; if they fail → 4C becomes a real gate and the minimum model is
  `events` + the infobox floor, not a new table.
- **Expansionist — discount the signal.** The interval model is ~80% present
  (`events` 2 748 rows, `timeaxis.py`, the consumer-less `continuity.py`
  "what did X know by arc N"); upside if probes fail: C-group closure,
  anachronism QA, cross-wiki, a new `/context` door.
- **Outsider — write the first failing test.** A gate that is green before
  its feature exists is worthless; B1/B2 test terminal status, not intervals,
  and no probe touches the earlier-state gap; a new pre-registered probe set is
  the only thing that produces a real test; if nothing fails, the phase closes
  on evidence instead of on a table.
- **Executor — Monday sequence.** Author 3–5 arc-scoped probes with
  wiki-pinned ground truth, run them live against `/context` via the oracle
  harness; all pass → close 4C + interval model to backlog; any fail →
  promote to the real 4C gate and build 4A **bounded to the characters the
  probes touch**; in parallel a 1-hour spike: hand-insert 2 interval rows and
  confirm they ride the fact floor to `/context`.

## Peer-review consensus (5 reviewers)

- **Strongest: B/Executor (3 of 5); C/Contrarian (2 of 5).**
- **Largest blind spot: E/Expansionist (5 of 5)** — commits to the build
  without verifying that *any* arc-scoped probe fails today; the speculative
  upside (cross-wiki, a new `/context` door) inflates cost outside the
  decision; the "80% built" claim is unverified — `events` models *events*,
  not *states*.
- **What all five missed (convergent):**
  1. **Bundle containment ≠ writer output** — a bundle can hold the right
     earlier-state quote and the terminal "Deceased" simultaneously; a "pass"
     may be fixable by ranking/ordering, not by 4A. An answer-level gate is
     the stronger test.
  2. **The router is unowned** — nothing routes an arc-scoped question to the
     interval store; 4A's serving path is an unexamined assumption in every
     option.
  3. **No demand-side evidence** that writers actually ask earlier-state
     questions (the 2C oracle is the executor's own probe set).
  4. **Data availability** — `events.arc_index` coverage of state-bearing
     facts is unverified; some states may have no arc anchor at all.
  5. **No one planned the regression re-run** (`eval`, `canon-run`,
     `span-recall`) after a 4A build.
  6. **Gold-bank hygiene** — new probes need recorded reasons; this very set
     already produced 5 miscalibrated surprises.

## DB-verify: claims struck / corrected

- **Corrected (this record):** the session note quoted the run's sha as
  `a788fa` — that is the *run-content* sha recorded inside
  `oracle_2c_summary.json`; the on-disk file hash is `d712adfa…`. Both
  recorded; cite the run sha.
- **Amplified (Contrarian + reviewers):** B1's PASS is **not stable** — it
  regressed under `RED_floorfirst` (11/18) and is a cross-page case by the
  oracle's own note; the B-group cannot be trusted as a gate.
- **Confirmed:** B-group 4/4 at 2C; 5 surprises; terminal facts already ride
  the fact floor (B2's bundle serves `Status: Deceased` alongside the
  `(Former)` occupation).

## Recommendation (chairman)

Adopt **option C, as the Executor's Monday, hardened by the Contrarian and the
reviewers**:

1. **Author 3–5 arc-scoped earlier-state probes** (e.g. "Was Gojo alive at the
   START of the Culling Game?", "What was Geto's status DURING the Shibuya
   Incident?", "Was Nanami alive during the Culling Game?") with **wiki-pinned
   ground truth** — a verbatim substring from a named page, looked up in the
   crawl, never inferred — pre-registered with a recorded reason each, in a
   v2 oracle record.
2. **Verify each probe fails against live `/context` before building** (no
   green on paper). Run via `oracle_run2c.py` against
   `http://127.0.0.1:8000/context` (server currently down).
3. **All pass** → close 4C on that evidence; the interval model goes to the
   backlog. **Any fail** → that probe set becomes the real 4C gate (replacing
   "B1 and B2 must move"); build 4A **bounded** to the characters the failing
   probes touch, reusing `events` + the infobox fact floor (not a wiki-wide
   4B). The **serving-path spike** (hand-insert 2 interval rows; confirm they
   reach `/context` with zero router/chunker changes) is a hard prerequisite.
4. **Re-label A1, A2, A3, B1, B2 now** (P3.3C condition 5) — as a recorded v2
   oracle, not an in-place edit of v1 (v1 is reviewer-owned:
   `editable_by_executing_agent: false`).
5. **After any 4A build:** re-run `eval`, `canon-run`, `span-recall` (the
   regression re-runs no advisor planned).
6. The cross-wiki / new-door upside is a **backlog ticket**, not part of this
   fork.

## The one thing to do first

Author 3–5 arc-scoped earlier-state probes with wiki-pinned (verbatim,
named-page) ground truth and a recorded reason each, pre-register them, and
run them against live `/context` — that single evidence set resolves the
A/B/C fork.

## Disposition

- **4C re-scoped:** the new pre-registered probe set replaces "B1 and B2 must
  move" as the gate criterion, gated on *failure evidence* from a live run.
- **4A:** bounded to failing probes' characters; `events` + infobox fact
  floor; serving-path spike is a hard prerequisite.
- **Re-label (condition 5)** lands as an ORACLE v2 record, not an in-place
  edit of v1.
- **Cross-wiki / new-door upside** → backlog ticket.
- **Next work step (this session):** probe authoring + pinning (offline,
  against the crawl), then server start (GPU-first) + live probe run.