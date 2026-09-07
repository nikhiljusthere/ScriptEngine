# COUNCIL: CSM campaign plan (2026-09-07)

**Chairman's synthesis of the CSM 100%-campaign plan review.** Five advisors were
convened; two (The Executor, The Expansionist) expired while waiting for admission,
so the substantive sample is **n = 3** (First Principles, Outsider, Contrarian) plus
five peer reviews. Because the sample is degraded, the chairman independently
re-verified every load-bearing in-tree claim before recording it; the verified
claims are listed under *Blind Spots* and are reproducible at the cited paths.
The JJK baseline (pytest 1,242 / eval 31/31 / canon-run 236/236 @ 79.0% /
span-recall jjk 390/400, measured 2026-09-07) stays untouched; CSM-only handling
goes in `series/csm/overrides.yaml` or CSM-specific scripts, never in JJK-verified
tooling.

---

## Where the Council Agrees

Points on which two or more advisors converged independently:

1. **The T0–T4 question-bank build (item 4) is not a component of D1–D6.** All
   three surviving advisors, and the plan's own text. The §2 done-set never
   references a bank: D1 = the coverage report; D2 = archetype depth floors;
   D3 = probing + a non-empty red list; D4 = a small *held-out* set authored by a
   party other than the executing agent; D5 = an exhaustive lines × doors sweep
   in which the probe *is* the wiki line (zero authoring); D6 = per-dimension
   censuses + door censuses + mechanical consistency checks. JJK's own D6 closed
   on frozen census questions (100 roster + 100 narrative + 140 dimension + 50
   open — `reports/comprehension/DONE_DECLARATION.md`), with zero hand-authored
   prose questions. §1: "the questions were never the deliverable."
2. **5.5 as proposed ("LLM-judge grading") is the opposite of plan §5.5.** Every
   surviving advisor flags it. §5.5's actual fixes, in order of strength, are
   generator-sliced gold → held-out probe sets → pre-registered red list. A judge
   model is a new gameable component — author-as-grader in model clothing. Judge
   as triage aid at most; never as the gate (D6's gate is explicitly mechanical,
   zero judgment).
3. **5.6 must precede any generation — and it is answerable from disk.**
   `questions/csm.json` exists: **39 questions** (22 added in the 2026-08-15 bank
   expansion, 1 retired, updated 2026-08-15, **zero revid stamps**) plus
   `questions/_csm_relations.json` and the declared rosters in
   `series/csm/overrides.yaml` (chairman-verified). Item 4 as written would
   clobber it; §5.6 exists for exactly this, and §0 names the failure mode.
4. **The §13 retention guard is already in-tree — not a build item.** Verified:
   `build.py:116` calls `store.require_rebuild(force=force)` before `reset()`;
   `facts.py:312` (`require_rebuild`) + `facts.py:345` (`remap_derived`); the guard
   is tested (`tests/test_stores.py:510`). The Outsider's revised item 1
   ("§13 guard + durable key, must precede CSM extraction") is phantom work built
   on the plan's pre-guard 2026-09-05 description. What *is* owed is one line of
   awareness: a refused routine `index` after a D6 extraction is **correct**
   behavior — read the remap report, never delete the guard (the JJK exposure).
5. **All four §2a measurement traps are live in-tree** (chairman-verified in
   `scriptengine/eval/span_recall.py`): seed 7 shuffle of tier-0-eligible probes
   (`:257,:284`); `done` resume dedupes on bare sentence text and the CLI never
   passes `done` (`:259,:294`, `cli.py:2086`) with append-mode jsonl; `hit_rate`
   divides by rows actually run, not the panel; roster and narrative doors have
   **zero** retrieval measurement (every JJK probe routed `qa`). Without a pinned
   hashed panel, any chunker fix swaps the panel and every delta is sample churn,
   not progress.
6. **Wave-0's rc=0 closed tier-0 only.** Tier 0 is the plan's named tautology
   ("a chunker that emits every sentence passes it by construction"). D5 is tier 1
   — and JJK's own record says "an exhaustive tier-1 has never run"
   (`COMPREHENSION_REMAINDER.md:87-89`). Item 5 ("until D1–D6 hold") would read
   wave-0's rc=0 as D5 done: the project's signature substitution, named twice in
   the plan.
7. **5.4 is over-scoped as "build the CSM prose.db/meaning layer."** That is the
   room-before-door mistake JJK formally retired (`semantics` 0 rows, `prose.db`
   corpse — §2c: "Do not create a third"). Door pre-check first, zero GPU;
   extraction only if the dimension census goes red (JJK D7/D8 precedent: X2.f
   "contingent extraction — the red set is empty, nothing built").
8. **Item 3 (archetype mapping) and 5.1 (scoreboard generalization) are one
   artifact.** 5.1's fix is "move scope into `overrides.yaml` as declared
   in-scope and excluded-in-writing type lists" — that list *is* the
   per-type classification, and §6's archetype mapping is the same mapping file
   with depth floors and section scoping attached. Two items doing one job is
   double work.
9. **Gate discipline and the per-wiki overrides rule carry over unchanged**
   (all advisors): the four standing gates re-run before any pass is declared
   done; if a fix mentions a series name in a `.py` file it is in the wrong
   place; CSM-specific scripts for CSM-only page shapes.
10. **Fixed-data principle already carried by the proposal** (item 4's
    "generated once, seeded, frozen to JSON; re-runs execute the same questions")
    — the council keeps it, applied to the re-scoped measurement sets instead of
    a bank.

## Where the Council Clashes

Genuine disagreements, with both sides, and the chairman's ruling:

1. **D5: exhaustive tier-1 × 3 doors, or a 400-probe sample?**
   - *First Principles:* exhaustive tier-1 × 3 doors with pinned panel, held-out
     split and wired resume. CSM is an order of magnitude cheaper than JJK's
     ~7 GPU-days; it is finite, resumable, and it is the plan's D5 verbatim.
   - *Contrarian:* closes D5 with a tier-1 400-probe on csm (item 10), following
     JJK's DONE_DECLARATION D3 precedent ("MET" at 97.5% on 400 probes).
   - *Ruling:* **exhaustive.** The plan's D5 text is "exhaustively measured and
     its miss file is empty," and §2a: "the number everyone quotes is the wrong
     number." JJK's 400-probe "MET" was a sampling shortcut under a corpus that
     made the exhaustive sweep ~7 GPU-days; CSM's measured panel is ~15,400
     tier-0-eligible sentences → ×3 doors × ~4 s ≈ **51 GPU-hours ≈ 2 GPU-days**,
     affordable in Qwen quiet windows. CSM is *the pilot* — its §7 job is to
     produce the first real cost number, and a 400-probe close would inherit JJK's
     deviation by silence (peer D's instruction: adjudicate the fork explicitly).
     The 400-probe stays as the *standing gate*; the D5 done-criterion is the
     exhaustive sweep.
2. **§13: no item at all, or a documented-behavior item?**
   - *Outsider/Contrarian:* already in-tree; no item (the Outsider's phantom item
     notwithstanding). *First Principles:* the campaign must *know* a refused
     index is correct, or someone deletes the guard in a panic.
   - *Ruling:* no build item; one recorded line in the campaign record (item 5d
     below). The guard and its test exist; what was missing on JJK was awareness,
     not code.
3. **Order of item 3 vs 5.1: merged, 3→5.1, or 5.1 first?**
   - *First Principles:* merge — the scope list is the archetype map. *Outsider:*
     3 → 5.1 (cannot declare scope before classifying the 11 types).
     *Contrarian:* 5.1 first (it is D1's oracle; 0/537 is fake green).
   - *Ruling:* **one work item** (item 2 below): the classification is authored in
     `overrides.yaml` first and the tool reads it in the same commit; the
     done-criterion is the scoreboard denominator, so it lands "5.1-first" in
     effect without a separate ordering artifact.
4. **5.3 scope: one fixture per G1–G30, or pilot scope?**
   - *Proposed list:* full cross-series regression gate. *First
     Principles/Contrarian:* pilot scope — CSM fixtures only on the code CSM's
     fixes actually exercise; full per-gap fixtures are P6 cross-corpus work.
     Verified: `tests/` has **zero** `series_paths("csm")` references today.
   - *Ruling:* **pilot scope, before the closure loop** (the loop's fixes need CSM
     fixtures or the gates can't see CSM regressions): chunker skip set /
     `effective_boilerplate_sections`, the span-recall oracle,
     `citation_positional`, scope/archetype plumbing.
5. **Who authors the D4 held-out set?** No plan says; D4 silently degrades to
   self-grading, which is the defect §5.5 exists to kill. *Ruling:* **named
   author: a fresh-context subagent**, council-spawned, frozen to JSON with seed
   + revid, run by the executor but never edited by it (§16: the executing agent
   must not author its oracle; user input is banned by standing rule 1).
6. **Cross-page facts (§2a: "the requirement most worth building because it is
   the one currently at zero")** appear in no revised plan. *Ruling:* on CSM
   (537 pages, 11,261 edges, `chunk_nodes` already built) it is a cheap
   **measurement**, not a build: count (entity, off-page section) pairs + a probe
   sample; if red, file a numbered gap and defer the build to P6 (cross-corpus).

## Blind Spots the Council Caught

Items that emerged only in peer review or chairman verification — not in any
advisor's revised plan:

1. **The Outsider's item 1 is phantom work** (peers B, C, E): the §13 guard
   shipped before that plan was written; "completing" it risks editing a guard
   that protects JJK's events. Verified in-tree: `build.py:116`,
   `facts.py:312/:345`, `tests/test_stores.py:510`.
2. **The Contrarian's item 10 re-ships the sampling deviation** (peer B): a
   400-probe D5 close is exactly what §2a calls "the number everyone quotes is
   the wrong number"; adjudicated to exhaustive in Clashes #1.
3. **No revised plan ends with §7's pilot deliverable** (peers B, C, D, E): CSM
   "is not there to be finished"; it exists to answer **four cost questions** —
   how many T0 questions emerge, what fraction survive verification, how many
   new gaps a fresh wiki produces, how many human round-trips the whole thing
   took. "Every schedule estimate in any document is fiction until the CSM pilot
   produces a real number." The done-declaration must carry all four.
4. **Cross-page fact census in no plan** (peers B, C, E): §2a's "largest
   uncovered surface" (JJK: 14,194 entity/off-page pairs; 96–99% of character
   prose sits off-page) is currently at zero on every wiki. Measured, not
   built, on CSM (item 6f).
5. **The tier-0 rename** (peers A, C, E): the plan's explicit instruction to
   rename `span-recall` → `chunk-containment` for tier 0 appears in no revised
   plan; without it CSM inherits JJK's misread rc=0.
6. **The `min_words=6` short-line floor** (peers B, E): the oracle drops
   <6-word lines — CSM's own wave-0 log records one excluded 3-word line
   (`series/csm/overrides.yaml`). CSM could close D5 with the "no matter how
   small" lines out of scope; the floor must be declared (include or record the
   exclusion in the audit).
7. **Standing-gate re-baselining** (peer D): CLAUDE.md's gate values "have gone
   stale twice — verify before trusting" (§11). Re-baseline the four gates at the
   start and again before the done-declaration.
8. **CSM's 14 `unknown`-type pages** (chairman verification, `documents`
   histogram: chapter_box 232 · character 175 · volume_box 26 ·
   character_history 22 · music 20 · story_arcs_box 14 · **unknown 14** ·
   episode 12 · organization 11 · blu_ray_dvd 4 · establishment 3 · anime 2 ·
   saga_box 2 = 537): a D1 tripwire ("every page covered or excluded in
   writing") the proposed list never touches; item 2's classifier must resolve
   the 14 `unknown`s or exit non-zero.
9. **Sample degradation and completeness** (peers B, D, E): A and E expired →
   the council heard 3 of 5 advisors; First Principles' (c) is truncated at
   "(c) C". The chairman closed the gap by verifying the load-bearing claims
   directly: `census_dimensions.py:60` and `placement_audit.py:119` hardcode
   `series_paths("jjk")` (CSM's D6 has **no oracle** — `census_doors.py` is
   already `--series`-parameterized, only the dimension census and placement
   audit need the flag); `span_recall.py` seed-7 shuffle / unwired `done` /
   bare-text dedupe / partial-denominator `hit_rate` (all confirmed); the §13
   guard + test in-tree; the CSM seed bank on disk (39 questions, zero revids);
   `FAILING_LINES.md` still an empty table ("awaiting user acceptance cases") —
   so the §2c twenty-failures precondition has never been met even on JJK.
10. **"5.2 pin the gold bank" presumes a bank exists** (Outsider, chairman):
    with item 4 skipped, nothing exists to pin; re-scope to "stamp revid (or
    section content hash) on every gold artifact at authoring time," starting
    with the existing 39-question seed.

## The Recommendation

**Item 4 verdict: SKIP the T0–T4 question-bank build; KEEP T0 only as a frozen
pilot measurement; T1–T4 deferred out of the campaign.** Grounded in what D1–D6
actually require in `plan/Plan_to_perfection.md` §2: the done-set references the
coverage report (D1), archetype depth floors (D2), probing + a non-empty red list
(D3), a small held-out set authored by a non-executing party (D4), an exhaustive
lines × doors sweep where the probe is the wiki line itself (D5 — no questions
at all), and per-dimension/door censuses with mechanical consistency checks
(D6 — JJK closed it with 390 frozen census questions, zero hand-authored prose).
§1: "Questions are the instrument. Filed engine gaps are the product … the
questions were never the deliverable." T0 is free, mechanical
(`scriptengine/eval/page_gen.py` is series-agnostic; CSM: 535 identity-field
matches) and is the instrument for D1/D2 *plus* pilot numbers #1/#2 — keep it,
frozen to JSON per the fixed-data principle, and never let "a large T0 number end
a campaign" (§4 T0 limit: T0 will not buy D3; gap discovery comes from the
held-out set, the census reds, and novel shapes). T1 (paraphrase) and T2
(roster/sets) buy robustness and determinism, not done-set progress; T3 (prose)
is the only gap-producing tier and is the one the user directive says to skip if
not necessary — it is not necessary for D1–D6. T2's *method* (discovery against
declared rosters as a labeled oracle) is still inherited — via the wiki's
declared rosters driving the D6 door census — not as a bank campaign.

**Proceed with the revised 8-item plan below, not the proposed 6-item list.**
Every JJK learning that landed late has a numbered home in it: the tier-1
pinned-panel/all-doors discipline (3), the §13 refusal behavior (5d), the D6
checkable definition + "a number no page files stays unmapped, never guessed" +
"thin dimension is a corpus property, not an engine defect" (6), the door
pre-check before any LLM spend (5c), audit-before-index + read "cited directly" /
"sentences w/ chapter" first (re-verify CSM's `citation_positional` shape per
re-index), the twenty-failures + eight-verb preconditions (5e, 6c), roster-driven
door census (6d), §9a loop shape "the agent never runs the sweep that grades it"
(7), and council cadence + raw receipts + coverage regenerated after every commit
(7). Already covered by the proposed list: the per-wiki overrides rule (wave-0
proved it), fixed-data freezing, the four standing gates, tier-0 span-recall
discipline, positional citations.

## The Revised CSM Campaign Plan

Order is the number; each item states scope and a checkable done-criterion.
Standing items for the whole campaign: council every 2–3 todos (written to
`reports/csm/COUNCIL_*.md` — if it is not on disk, it did not happen); raw
receipts, never "100% pass rate" prose; `coverage_report` regenerated after
every commit; JJK baseline untouched (re-verified at start and at the
done-declaration).

**0. Wave-0 tier-0 reachability — DONE.** 439 → 0 unreachable lines,
`span-recall --series csm` rc=0; fix = post-G15 re-index +
`content_sections: [Notes, References]` in `series/csm/overrides.yaml`.
Record only. Note for the audit: the oracle's 6-word floor already excluded one
3-word line in wave-0 (documented in the overrides comment).

**1. Inventory + revid-stamp the existing CSM seed bank (5.6 → 5.2 re-scoped).**
*Scope:* inventory `questions/csm.json` (39 questions, 22 from the 2026-08-15
expansion, 1 retired, zero revid stamps) + `questions/_csm_relations.json` + the
declared rosters in `overrides.yaml`; stamp revid / section content hash on every
existing question; commit the inventory as an artifact. Zero new questions in
this item. *Done:* inventory file on disk and committed; every existing CSM
question carries a revid stamp; the "pin the bank" item is retired (5.2 now
means "stamp at authoring time" for everything this campaign adds).

**2. Classify every CSM page type; generalize the scoreboard (5.1 + item 3
merged).** *Scope:* in `series/csm/overrides.yaml`, classify all 537 pages /
all page types (chapter_box 232, character 175, volume_box 26,
character_history 22, music 20, story_arcs_box 14, **unknown 14**, episode 12,
organization 11, blu_ray_dvd 4, establishment 3, anime 2, saga_box 2) as
in-scope / excluded-in-writing (one-line reason each) + archetype
(character / chapter / episode / battle / technique / location / release /
organisation / item); that list is simultaneously 5.1's scope list and §6's
archetype mapping — the reusable archetype schema (depth floors, section
scoping, per-archetype templates) is defined once here, inherited by the other
six; `tools/coverage_report.py` reads scope from overrides (the JJK-hardcoded
`IN_SCOPE_TYPES` is retired) and **exits non-zero** on any `page_type` it has
not been told how to classify — "silence must become an error." No series name
in any `.py`. *Done:* `coverage_report --series csm` denominator = 537 with 0
unclassified and 0 `unknown`-type pages (the 14 unknowns classified or excluded
in writing); `coverage_report --series jjk` output byte-identical (regression);
non-zero-exit path + a CSM scope test in `tests/`; pytest green.

**3. D5 measurement infrastructure — close the four §2a traps.** *Scope:*
(a) pinned hashed probe panel keyed `(title, section, sentence)`, with a
held-out split the executing agent never sees; (b) wire CLI resume — `done`
keyed `(title, sentence)`, jsonl rewritten not append-duped; (c) `hit_rate`
over the full panel denominator, not rows run; (d) declared short-line floor —
include <6-word lines in the panel *or* record the exclusion in CSM's audit
("no matter how small" is the contract's words); (e) all three doors
(qa + roster + narrative — roster/narrative have had zero retrieval
measurement); (f) rename tier-0 `span-recall` → `chunk-containment` (old name
kept as an alias) so CSM doesn't inherit JJK's misread rc=0. *Done:* two
consecutive sweeps reproduce the identical panel (hash stamped in the report)
and their delta is attributable to a named fix, not sample churn; a resumed run
is idempotent; per-door raw counts printed; the renamed command and its alias
both work; pytest green.

**4. D5, the real one — exhaustive tier-1 × 3 doors on CSM.** *Scope:* full
panel (~15,400 tier-0-eligible sentences × 3 doors ≈ 51 GPU-hours ≈ 2 GPU-days
at ~4 s/probe; the measured panel replaces this estimate, and the estimate is
itself a pilot input). Batch job, checkpointed, resumed in Qwen quiet windows
(CUDA per the standing GPU rules; a sustained multi-day run switches Qwen
262k→100k first). The executing agent **never runs the sweep that grades a fix
it made** (§9a). Misses triaged by class: MISS_DOC (ranking) / MISS_SPAN
(chunk selection). *Done:* miss file empty, or every residual miss triaged with
a documented floor recorded in CSM's audit; per-door raw numbers pasted into
`reports/csm/GATE.md`; a re-run reproduces the panel; standing gates green.

**5. Phase-0 remainder, re-scoped (5.3 pilot / 5.5 no judge / 5.4 door-first /
§13 awareness).** *Scope:* (a) 5.3 — CSM fixtures **only on the code paths
CSM's fixes actually exercise** (chunker skip set / `effective_boilerplate_
sections`, the span-recall oracle, `citation_positional`, scope/archetype
plumbing); zero `series_paths("csm")` in `tests/` today, and the closure loop's
fixes need CSM coverage; full per-G1–G30 fixtures are P6 cross-corpus work.
(b) 5.5 — **no LLM judge**; generator-sliced gold where the generator slices
verbatim from `sections.text`, + the held-out set (item 6d), + a pre-registered
red list. (c) 5.4 — **door pre-check first, zero GPU**: point the narrative door
at CSM's existing cheap signals (episode/chapter facts, era-carrying relations,
declared rosters); hand-write ~25 CSM event rows into an `events` table only if
the door needs them; **extraction only if the item-6 dimension census goes
red** — JJK's `semantics`/`prose.db` corpses are the precedent for why.
(d) §13 — record the standing awareness: the guard + durable key + test are
already in-tree (`build.py:116`, `facts.py:312/:345`, `tests/test_stores.py:
510`); a **refused** routine `index` after a D6 extraction is correct behavior —
read the remap report, never delete the guard. (e) **the §2c twenty failures**,
frozen as acceptance cases **before any extraction spend** —
`FAILING_LINES.md` is still an empty table on JJK ("awaiting user acceptance
cases"), so CSM writes its own; if twenty cannot be produced, that is itself a
finding worth knowing. *Done:* ≥1 CSM fixture per exercised path in `tests/`;
the door verdict on disk with raw receipts (a script writer's difference test,
recorded); the red list and the twenty-failures set frozen on disk with a named
author; the §13 awareness line recorded in the campaign record.

**6. The D6 oracle + the bounded instrument (replaces item 4).** *Scope:*
(a) parameterize the two JJK-hardcoded tools (`tools/census_dimensions.py:60`,
`tools/placement_audit.py:119` → `--series`; `tools/census_doors.py` already
accepts it); (b) **regenerate the §12 dimension map from CSM's own sections** —
JJK's map is cursed-technique-specific and does not transfer; CSM's is built
from CSM's character / character_history sections + Outcomes + Causality +
state-over-time, and a dimension is scheduled only when its consumer column
names a real query and its acceptance column names a test that can fail; a
dimension CSM's wiki leaves thin is **a corpus property, not an engine defect**,
and a number no page files **stays unmapped, never guessed**; (c) the §12
**eight-verb 100-sentence sample** — no model, only reading; it decides whether
extracted events are a foundation or a sample, and it is the extraction
precondition; (d) **frozen census sets generated fresh from CSM** (fixed-data:
seeded, revid-stamped, never copied from JJK): door censuses 100 + 100 from the
wiki's declared rosters, 10 frozen questions per dimension, and the **D4
open-50 set authored by a fresh-context subagent** (council-spawned; the
executor runs it, never edits it — §16); (e) **T0 pilot**: the existing
series-agnostic `page_gen.py` over CSM's 535 identity-field matches → generate,
freeze to JSON (seed + revid), run; record emergence + verification-survival
rate (pilot numbers #1/#2). **No T1–T4 authoring.** (f) **cross-page fact
census** (§2a's "largest uncovered surface," at zero on every wiki): count
(entity, off-page section) pairs on CSM + a probe sample — measure, don't
build; if red, file a numbered gap, build deferred to P6. *Done:* every runner
green `--series csm` with thresholds pre-declared; all sets frozen with seed +
revid; the eight-verb report on disk (the fraction it cannot hold, with the
sentences); the D4 set's named author on disk and zero executor edits to it
(git-blame checkable); T0 set frozen with pilot numbers recorded.

**7. The §9a closure loop (D1–D6).** *Scope:* batch sweep (item-4 panel +
item-6 censuses) → pre-triaged queue (classes, not questions: MISS_DOC /
MISS_SPAN / gate violation / twenty-failures hit) → serial engine-fix closure
(one class per fix; per-wiki override preferred — no series name in `.py`;
**never reword to pass**: the 3-phrasing probe is pasted into the triage file,
never summarized) → the next sweep grades (the agent never runs the sweep that
grades it); gold/engine split reported every batch; receipts are raw query
output; `coverage_report` regenerated after every commit; **council every 2–3
todos** → `reports/csm/COUNCIL_*.md`; the CSM section of `GATE.md` is the live
record; the loop halts on a miss-count regression or two iterations with no net
reduction (escalate, do not grind). *Done:* D5 miss file 0 (or the documented
floor); D6 consistency checks — arc placement, cross-page agreement, beat
ordering vs `episode` facts — zero violations, and the dimension censuses at
their pre-declared thresholds; the twenty failures each fixed or retired with
reason; the four standing gates green on the final tree; the JJK baseline
diff-empty (pytest 1,242 / eval jjk 31/31 / canon-run opm 236/236 @ 79.0% /
span-recall jjk 390/400 — re-baselined at start, because CLAUDE.md has gone
stale twice).

**8. Done-declaration + pilot memo.** *Scope:* D1–D6 answered **by pasted raw
output, never prose** (JJK's `DONE_DECLARATION.md` D1–D10 shape), plus §7's
**four pilot numbers** (T0 emergence, T0 survival, new numbered gaps, human
round-trips) — "every schedule estimate in any document is fiction until the
CSM pilot produces a real number"; standing gates re-baselined; halt before P6
(cross-corpus is the next campaign; CSM's job was to produce the number, not to
be finished). *Done:* memo + receipts committed under `reports/csm/`; the four
pilot numbers present; the four gates green; the JJK baseline diff empty; the
JJK campaign and its 1,242-test baseline untouched.

## The One Thing to Do First

**Item 1 — the 30-minute inventory + revid-stamp of `questions/csm.json` (39
questions, 22 from the 2026-08-15 expansion, zero revid stamps) and
`questions/_csm_relations.json`, committed before anything generative.** It
kills the clobber risk that §5.6 exists to name, it defines what "pin the gold
bank" (5.2) actually means once item 4 is skipped, and it is the cheapest item
in the plan that is not already done. Everything else in the revised plan can
start only after it is on disk.
---

## SUPPLEMENT — recovered advisors (2026-09-07)

**Recovery status.** The Executor's re-run completed and produced a full
advisory response. The Expansionist's re-run **expired again mid-first-tool-
call**: its entire transcript is two `read` invocations (`plan/
Plan_to_perfection.md` at offset 1036; `reports/comprehension/
COMPREHENSION_REMAINDER.md`) plus a truncated word fragment, with zero
advisory content. The substantive sample is therefore **n = 4** (First
Principles, Outsider, Contrarian, Executor), not n=5.

### The Executor:

**Monday morning:** you do not start with the bank. You start with the scoreboard — right now CSM's "0 remainder" is a JJK allowlist (5.1), i.e. the campaign's canary is dead before it starts. And T0 is not a build, it's a command.

**(a) Is the bank necessary?** No, not as item 4. D1–D6 (§2) need: D1 written coverage/exclusion (scoreboard), D2 archetype floors, D3 red list + zero unfiled gaps, D4 a *held-out probe set*, D5 done, D6 placed events. D4 is a small probe set, not a 21k-question factory. T0 (535 rows, `page_gen` already series-agnostic) and T2 (free SELECTs, 12 rosters already declared) are zero-authoring — run them, frozen to JSON. T3 authored prose is the only scaling tier; skip it unless the red list demands. Also: the plan defines T0–T3. "T4" does not exist.

**(b) Scope/order:** 5.6 is ten minutes — run it first. 5.5 mis-framed: the plan's fix is generator-sliced gold + held-out set + red list, not "LLM-judge grading." Item 3 under-scoped: D2 needs depth floors declared per archetype, not just the mapping. Item 5 missing the §9a invariants (work unit = engine fix, pinned-panel deltas, halt conditions). Missing entirely: **§13 retention guard — `build.py`'s `reset()` wipes events/meaning on every re-index; run CSM's D6 extraction and your next `index` destroys it. JJK's 2,594 rows are exposed right now.** Also missing: pre-registered red list (20 failures), CSM dimension census, the pilot's four cost numbers as an artifact.

**(c) Port from day one:** audit→index→span-recall discipline, overrides-only rule, fixed-data freeze, the four standing gates, `citation_positional` (done). Not yet listed: D6 census shape (dimensions × 10 frozen questions, term-coverage verdict; thin dimension = corpus property, declare a floor), §13 guard, D4 non-executing authorship.

**Revised plan:**
1. **Inventory** (5.6): committed file listing `questions/csm.json` + `_csm_relations.json`, counts + revids. Done: on disk.
2. **Scoreboard** (5.1): in-scope/excluded type lists move to `overrides.yaml`; unclassified `page_type` = non-zero exit. Done: CSM shows real N/537; JJK number reproduces.
3. **Archetypes + D2 floors** (11 types → archetypes, floors declared in `overrides.yaml`). Done: audit 0 unmapped; floor measurable per archetype.
4. **Cross-series fixtures** (5.3): one csm fixture per engine fix. Done: `series_paths("csm")` ≥ fixes; opm canon 236/236.
5. **Bank, scoped**: T0 + T2 + ~40 council-authored D4 held-out probes (agent cannot edit), all frozen + revid-pinned (5.2). Done: re-run emits identical IDs.
6. **§13 guard**: `build.py` refuses `reset()` on non-empty derived tables without `--force` + durable-key remap. Done: `index` after `events-extract` preserves rows.
7. **D6**: clone `ingest/events.py` for CSM (generalize, don't fork) + meaning layer; CSM dimension census. Done: all rows placed-event or standing-state; three survival checks + cross-page agreement zero violations; thin dimensions declared corpus property.
8. **Red list + 5.5**: 20 pre-registered failures; generator-sliced gold; D4 passes at declared threshold, zero rewordings.
9. **§9a closure loop** to D3: engine-fix units, pinned-panel deltas, halt on regression/no-reduction.
10. **Final gates + memo**: pytest 1242 / eval jjk 31/31 / span-recall jjk / span-recall csm rc=0 / opm 236/236; four pilot cost numbers (T0 yield, survival rate, new gaps, round-trips).

### The Expansionist:

(Expired mid-first-tool-call; no advisory content. Verbatim record of the re-run transcript: two `read` tool invocations — `plan/Plan_to_perfection.md` (offset 1036) and `reports/comprehension/COMPREHENSION_REMAINDER.md` — plus a truncated word fragment "ist"; zero advisory text.)

### Assessment against the n=3 verdict

**Agreements (no new ground).** The recovered Executor independently re-derives
most of the n=3 consensus: the bank is not a component of D1–D6 and D4 is "a
small probe set, not a 21k-question factory" (consensus 1); T0 is free and
series-agnostic (its 535-row figure matches the verdict) and T2 is free
SELECTs, with T3 the only scaling tier, skipped unless the red list demands
(item-4 ruling); 5.6 first, ten minutes ("The One Thing to Do First"); 5.5
mis-framed — the fix is generator-sliced gold + held-out set + red list, not
LLM-judge grading (consensus 2); unclassified `page_type` = non-zero exit
(bid spot 8); D6 census shape — "dimensions × 10 frozen questions; thin
dimension = corpus property, declare a floor" (item 6); the §9a invariants
(work unit = engine fix, pinned-panel deltas, halt conditions) (item 7); and
the port-from-day-one list (audit→index→span-recall, overrides-only, fixed-
data freeze, the four standing gates, positional citations) (consensus 9–10).
Its "missing entirely / also missing" list (pre-registered 20-failure red
list, CSM dimension census, the four pilot cost numbers as an artifact) names
items the council's revised plan already carries (5e, 6, 8) — the fresh run
was reviewing the *proposed* 6-item list, so nothing is actually missing.

**New points.**

1. *Verified terminological correction:* "The plan defines T0–T3. 'T4' does
   not exist." Chairman re-check of `plan/Plan_to_perfection.md`: the tier
   headings are T0 (Structured generation), T1 (Mechanical paraphrase),
   T2 (Sets and rosters from structure), T3 (Prose) — no T4 heading exists.
   The verdict's "T0–T4" shorthand was loose; the substance (skip the bank,
   keep T0 frozen, defer the rest) is unaffected. Adopted as a wording fix
   for future citations.
2. *D4 authorship nuance:* the Executor's "~40 council-authored D4 held-out
   probes (agent cannot edit)" vs. ruling 5's "named author: a fresh-context
   subagent, council-spawned, ~50 open." Compatible if "council-authored"
   means the council-spawned subagent; ruling 5's wording stays operative.
3. *Divergence (not a flip):* the Executor's revised item 7 schedules the D6
   extraction ("clone `ingest/events.py` for CSM (generalize, don't fork) +
   meaning layer" — `ingest/events.py` exists, verified) **unconditionally**,
   before the red list and the §9a loop. That re-raises the room-before-door
   scope the council rejected in consensus 7 / item 5c ("extraction only if
   the item-6 dimension census goes red"; JJK's `semantics`/`prose.db`
   corpses are the precedent; X2.f contingent extraction). The gate stands:
   census first, extraction only on red.

**Load-bearing conflict adjudicated: the §13 claim is false.** The Executor
asserts "§13 retention guard — `build.py`'s `reset()` wipes events/meaning on
every re-index; run CSM's D6 extraction and your next `index` destroys it.
JJK's 2,594 rows are exposed right now." This re-ships the Outsider's
phantom item (blind spot 1). Chairman re-verification for this supplement:

- `scriptengine/index/build.py` (`build_index`) calls
  `store.require_rebuild(force=force)` **before** `store.reset()` — the code
  comment is explicit: "refuse a non-forced rebuild while the derived layers
  are non-empty, so a reflexive `index` never destroys an extraction pass";
  a non-forced rebuild raises `ResetRefusedError`.
- `scriptengine/stores/facts.py`: `require_rebuild` (guard 0B) refuses while
  `events`/`meaning` are non-empty unless forced; `remap_derived` (durable
  key, 0C) snapshots and re-keys the rows onto the new build's ids — "only
  rows that went stale … orphaned, or unverified … are dropped, each counted
  and reported" — so even a `--force` re-index does not wipe.
- Tested: `tests/test_stores.py` `test_require_rebuild_refuses_a_non_forced_
  rebuild` and `test_a_forced_rebuild_remaps_the_events`.
- JJK's live data, queried 2026-09-07 against `series/jjk/facts.db`:
  `events` = **2,748** rows (the Executor's 2,594 is stale), `meaning` = 0,
  `abilities` = 594 — all behind the guard.

So a reflexive `index` after a D6 extraction is *refused* (correct
behavior), and a `--force` re-index remaps rather than wipes. The "JJK rows
exposed" claim fails on both the mechanism and the number. Ruling 2 stands as
recorded: no build item; one awareness line (the Executor's own revised item
6, read through its Done-criterion — "`index` after `events-extract`
preserves rows" — is exactly that awareness check, not a build).

**Per-ruling check.** Ruling 1 (D5 exhaustive): no contrary point; the
Executor's plan is silent on the sweep shape, and the standing-400-probe-gate
vs exhaustive-D5 split in item 4 of the revised plan is untouched. Ruling 2
(§13): challenged; the challenge is false in-tree (above); stands. Ruling 3
(one merged 5.1/item-3 work item): the Executor splits it into two ordered
items (scoreboard, then archetype + D2 floors); the substance — classify in
`overrides.yaml` first, the tool reads it in the same commit, done-criterion
= the scoreboard denominator — is preserved; stands. Ruling 4 (5.3 pilot
scope): the Executor's "one csm fixture per engine fix" **is** pilot scope;
agrees. Ruling 5 (D4 authorship): nuance 2 above; wording stands. Ruling 6
(cross-page fact census: measure, don't build): the Executor's plan is silent
on it; item 6f of the revised plan stands.

**Corrected rulings:** none.

**No rulings change; the n=3 verdict stands** — with one correction to the
sample count: the record is **n=4, not n=5**, because the Expansionist's
re-run produced no advisory content (expired mid-tool-call, as in the first
pass); a fifth substantive response requires another fresh run.
