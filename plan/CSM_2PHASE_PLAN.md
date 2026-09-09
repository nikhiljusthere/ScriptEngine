# CSM 100% — two-phase execution plan v2.2 (2026-09-09; supersedes v1 of 2026-09-08,
# which carries the retired "every 2–3 todos" cadence; incorporates the
# COUNCIL_csm_session_audit verdict, ledger #24; Phase-1 half amended by the
# P1 plan-approval council, reports/csm/COUNCIL_csm_p1_plan.md, ledger #25 —
# 14 amendments (A1–A14); Phase-2 half amended by the P2 plan-approval
# council, reports/csm/COUNCIL_csm_p2_plan.md, ledger #26 — 13 amendments
# (A15–A27: 11 mandatory + 2 optional), all applied 2026-09-09; approved
# Phase-1 artifact blob 840d413, approved Phase-2 artifact blob 8a098a75)

## The goal, and what 100 % means

**Goal:** the CSM corpus at full D1–D6 comprehension — the corpus
*understands* every character: what each line/fact/prose/event means, whether
it is an event, where it sits on the timeline, all structured dimensions.
CSM is the **P6 successor**: JJK's D6-comprehension is declared **done**
(2026-09-07, `reports/comprehension/DONE_DECLARATION.md` — done-set D1–D10,
"the terminal state is done", halted before P6). **Halt before P6** — no
cross-corpus work in this run.

**100 % = the checkable D1–D10 done-set** (JJK precedent, never "100 %"
prose — raw numbers on disk + a triage log entry for every residual):

| # | Item (JJK done-declaration §9, "item by item") |
|---|---|
| D1 | roster census — 100 frozen enumeration questions, ≥ 99 % reached. **Transfers vacuously to CSM:** CSM's roster census is 11 questions (`census_roster_100_csm.json`; doors 11/11) — D1 closes at 11/11, not 100 |
| D2 | narrative census — 100 frozen narrative questions, ≥ 99 % reached |
| D3 | reachability tiers — span-recall / chunk-containment (every line whole in a chunk) |
| D4 | preconditions recorded — frozen sets (seeded, revid-stamped) + pilot numbers on disk |
| D5 | placement-gate audit — the §12 dimension map bar met |
| D6 | unplaced events triaged — every non-ideal result has a recorded reason |
| D7 | no door-less table — every engine table has a serving door (or is formally retired) |
| D8 | contingent builds — the owed build set is empty, or each build is landed |
| D9 | standing gates green — the four gates, baseline-exact |
| D10 | halt — halted before P6, with the halt recorded |

## Position (2026-09-09, disk-verified)

**Done:** campaign items 0 (Wave-0 439→0), 1 (CSM-1 `064093e`), 2 (CSM-2
`42aa296`), 3 (CSM-3 `f93d396`), 3b (`bc73795`, ratified, ledger #20), 5
(CSM-5 remainder `0e0e19e`), 6-instrument (`0e0e19e`).

**§9a iteration 1 (in progress, ~40 %):** R-1 class closed (`b84445f` +
`aef6707`, D18; queue 33 fixable → 30). **R-2 (qa-passage leg) + R-3
(roster scoping): counseled (ledger #23, AMEND×2, amendments landed, model-
free batteries green), gates 1–2 + gate-3 offline green; the 9-file package
is on disk, uncommitted** — the gate-3 400-probe window (4,055–4,454) was
voided by the stale-ESC incident, `/tmp/csm_iter1_records/` was lost in the
reboot, and ledger row #23 ships with the commit.

**Measurements on disk:** census 39/60 green / **21 red** (Phase-1 documented
floor; the 5.4 extraction gate is LIVE); doors: roster 11/11, narrative
97/100 (3 arc-display misses); miss queue `reports/csm/miss_queue_csm_iter1.
jsonl` = 58 rows (~30 fixable / 22 extraction-gated floors); T0 pilot 843/843
survival; cross-page edges 11,261 (96.7 % cross-document).

**Machine (now):** Qwen 262k, `:8000` down, no bay.

## Process layer v2 (council #24 rulings; replaces the v1 standing cadence)

1. **Council trigger, shrunk:** councils only at **(a) the R-5 class,
   (b) the unit-4/phase close, (c) P6**. Pre-registered items (R-6, R-7,
   the close-steps, the gate legs) are **no-council checklists**. Sequential
   11, zero-GPU, fresh context (owner rule 2026-09-08 stands).
2. **Worker timeout: 90 min, or split** — verify/record as a separate short
   pass (wave-2 lesson: both workers died at 60 min in the final loop).
3. **Gate-green ⇒ auto-commit.** Verified state + ledgers + records commit
   atomically at each gate close (the v1 manual /tmp staging lost two
   work-days to a reboot). One committed **machine-readable ledger-of-record**
   (done / gated / uncommitted / next-action, single file, updated at each
   gate close) — reboots then cost zero.
4. **A/B bay + `csm-control.sh` monitor: KEEP**, patched before Phase 2:
   (a) the auto-kill branch is blind to CPU `:8000` children; (b) ESCs must
   re-verify live pids before acting (the gate-3 incident).
5. **Waves:** 2-parallel *drafting* + one shared verification pass (B grades
   both receipts on disk); gate legs run one-copy, never parallel.
6. **The invariant, renamed honestly: "baseline-exact"** (not "JJK-100 %"):
   after every engine change, the four gates equal the 2026-09-08/09
   re-baseline — pytest **1,303+2xp** · eval jjk **31/31** · span-recall
   **48,572/48,572 + ≥390/400 (97.5 %)** · canon opm **236/236 @ 79.0 %**
   (the opm-set-16 pre-registration stays live). JJK baseline untouched;
   `coverage_report.py` after every commit; raw receipts, never prose.
7. **Doc hygiene (with this plan's commit):** CLAUDE.md lines 14/341
   ("JJK D6 active" → done, P6-successor framing), WAVE2_RESUME §1 hash
   table (CSM-3 = `f93d396`, not `bc73795`), v1's un-retired cadence here.
   Gate values as generated artifacts (doc↔gate lint) = Phase-2 tooling.

## Phase 1 — the fixing process (rest of §9a iteration 1 + unit-4 close)

**One dial switch total: 262k → 100k** (checkpoint first). 100k frees
~7–8 GB so the embedder+reranker co-locate on the CUDA `:8000` (100k
use-case 1). Phase 2 runs on the same dial — no second switch; a 64k
dial-down only if VRAM demands (measure, don't guess).

- **P1.1 Gate legs + commit (~1 h of gate time after the preconditions, zero
  added GPU-h).** Ordered steps (council P1 A1–A5):
  1. **Step 0 — zero-GPU baseline re-verify** (on the current tree, before
     anything else): pytest collect (= 1,305 = 1,303+2xp) + `span-recall
     --series jjk` offline (48,572/48,572) + red-list recount — re-anchors
     "baseline-exact" post-reboot; the gate legs run only after this.
  2. **Step 1 — model-free rebuild pass (~30 min):** `/tmp/csm_iter1_records/
     ` was lost in the reboot → reconstruct from work_log 06:49:04/06:49:42
     + the on-disk receipts: the C1/C2 commit messages, the R-5 brief
     (`r5_class_plan.md` survives verbatim in work_log), and the R-2 Part-A
     panel rows + hash + ledger target (work_log owner-item 4 was never
     DONE — the panel must be **rebuilt**, not assumed pre-built).
  3. **Step 2 — the 100k switch, as an ordered precondition** (qwen_mode.txt
     = 262k now, free_mib ≈ 1,600 — a CUDA `:8000` is impossible as-is):
     SWITCHPOINT checkpoint (committed in C3) → `ninfer-work/qwen-switch.sh
     100k` → `pi_restart.sh` → **bring up the CUDA `:8000`** (named
     redeployer: A, per the owner standing rule; no bay exists post-reboot).
     **Abort branch:** switch/restart failure → abort before any gate leg;
     rollback = `qwen-switch.sh 262k`; no gate legs on a dead model.
  4. **Step 3 — the four gate legs:** seed-7 400-probe on the CUDA `:8000`
     (≥ 390/400) → gate-4 canon (236/236 @ 79.0 %) → R-2 Part-A panel
     (rebuilt rows + hash + ledger) → R-3 re-sweep (Part B green;
     invariants csm-set-14/15; csmdoor-01 floor held).
  5. **Step 4 — the selective 3-commit** (path-limited `git add` by named
     paths only; **`git add .` is banned** — the dirty tree carries
     unrelated files one `git add .` from contamination): C1 = 3 engine
     (`hybrid.py`, `roster.py`, `facts.py`) + 1 override + 3 tests + 2
     records + council package + red list + `COUNCIL_HISTORY` #23 + D19;
     C2 = queue stamps + gate-3 ledger + gate-4 report + Part-A panel +
     mini-sweep ledger + work_log + state; **C3 (new) = the doc-hygiene
     commit** (CLAUDE.md L14/341 "JJK D6 active" → done + P6-successor
     framing, the stale 150k-Phase-1-mode lines → 262k ↔ 100k per
     qwen_mode.txt, the 1,254 suite-count line → 1,303+2xp = 1,305
     collected; `CSM_WAVE2_RESUME.md` §1 CSM-3 = `f93d396` not
     `bc73795`; the v1 un-retired cadence; the untracked `reports/csm/
     receipts/` dirs). Also create the **`reports/csm/GATE.md` skeleton**
     (P2.1's per-door raw numbers land there). Ledger-of-record v1 lands
     with the package.
- **P1.2 The R-5 relations-mode wave (~1 wall-day).** **Split draft (A6):**
  the 90-min-or-split fresh-context draft covers **R-5 core only** (a 4th,
  series-agnostic router mode `relations` — phrasing trigger, checked
  before the enumeration branch — + a dedicated budgeted bundle builder,
  edges as the primary answer + MODES/endpoint update). B grades → **§3
  council (kept trigger)** → four gates → **R5-meter class re-sweep (≥ 1
  own-new-row HIT or halt)** → commit (auto-commit rule). **R-6
  (`subject_aliases`, 3 arc-display names) + R-7 (`identity_fields`, the
  61-key map) run as separate short no-council passes** under Process rule
  2 of this plan — the bundled 90-min draft re-triggers the 60-min timeout
  incident class (two wave-2 workers died there) and its brief was lost in
  the reboot. **A7:** the R-5 council brief pre-registers the **R-6
  floor-inheritance question** (`reports/csm/receipts/council_r2r3/
  chairman.md:43`: does an alias-resolved subject inherit the new level-0
  card via the subject floor?) so the no-council lever hides no open design
  question. **A8 (optional, does not gate Phase 1):** register 2–3
  relationship phrasings per other corpus as cross-corpus R-5 spot-pins
  (model-free; JJK/OPM invariant pins per the R-1 pattern), so P6 starts
  with 8-corpus router coverage proven. **A9 — "own-new-row HIT", defined:**
  the class's own targeted re-sweep hits ≥ 1 of the class's own new/
  stamped rows (work_log R-3-leg usage: set-17/set-01/char-02 = 3/3), or
  halt; every re-sweep carries the JJK/OPM invariant pins.
- **P1.3 Halt-meter convergence.** Miss-queue = **58 rows = 33 fixable
  (30 open + 3 closed by R-1) + 22 extraction-gated floors + 3 stamped**
  (verified against `miss_queue_csm_iter1.jsonl`). Class by class; class
  closure = its own class-targeted re-sweep green (own-new-row HIT + zero
  new misses on stamped rows); halt on miss-count regression or two
  no-reduction iterations → council. **Halt-meter scoping (council #21 R3,
  stated in prose):** the meter counts **only the 33 fixable rows**; the 22
  floor rows + 3 stamped rows are excluded ("the halt rule counts only
  Phase-1-fixable classes", `reports/csm/COUNCIL_unit3_sweep.md`) — without
  this, a literal reading trips on iteration 1 into a council the shrunk
  trigger list does not authorize. The 22 floors stay a **documented
  Phase-1 floor** — they close in Phase 2.
- **P1.4 Unit-4 close (~2 h).** One-copy four gates + the 34 s one-copy
  5.4 re-adjudication (class-by-class; a closed red de-scopes the
  extraction) + the pre-registered extraction-pass test shape +
  `coverage_report.py`, then **all close conditions (A12) before the
  marker**: (a) the campaign-todos section sync (moved here from the
  done-criterion); (b) the C3 doc-hygiene commit (A4) landed; (c) the
  `reports/csm/GATE.md` skeleton (A5) exists; (d) **bar-audit pull-in:**
  P2.2's model-free 3–5 pre-registered CSM panel-line cases per D6
  dimension run **before the marker**, so the done-set is bar-adjudicated
  before any of P2.1's 51 GPU-h; (e) the **R-6 floor-inheritance verdict**
  (from the R-5 council, A7) recorded. Last act: the `PHASE_A_COMPLETE
  <ts>` marker (`reports/master-work/phase_status.txt`). **A20 — the marker
  is written only when the miss queue sits at its documented floor** (the
  Phase-1 done-criterion below). A regression halt is a council state, not
  a floor: **no marker, no Phase 2** — a miss-count regression (P1.3) voids
  the precondition set and returns to the halt-meter loop; Phase 2's gate
  reads "marker present" and nothing else.

**Phase-1 done-criterion:** P1.1–P1.4 green; the miss queue at its
documented floor (extraction-gated reds + named residuals); the red list +
frozen sets synced; campaign todos section synced; ledger-of-record shows
*everything* committed.

## Phase 2 — exhaustive & extraction (same 100k dial; gpu-handoff authorized)

1. **P2.1 CSM-4: D5 exhaustive tier-1 × 3 doors.** **Step 0 — the bounded
   per-door sanity-100 (A15, the timer):** before any panel spend, in one
   100k side session (~21 min total, zero panel spend): `--sanity 100` on
   qa → narrative → roster (`--sanity` is first-run-only — resume runs drop
   it, since mid-sweep re-runs check a moving window and false-halt the
   low-yield doors). From the sanity raws, measure the per-door CSM s/probe
   → re-estimate the full-sweep cost **per door** (17,181 × measured
   s/probe, no uniform-rate assumption) → **go/no-go**: commit the 2-GPU-
   day budget only if the re-estimate fits; otherwise shrink (drop a door /
   a panel subset) or council. Record the measured s/probe + re-estimate in
   `reports/csm/GATE.md` (council #3 (d)(2): "the sanity runs must produce
   it"). Pre-registered threshold: measured re-estimate > 2 GPU-days ⇒
   abort/defer/shrink, do not start. The sweep itself: the **pre-extraction
   17,181-row pinned panel** (council #21 R4: it is the control arm). **A18
   — the control arm is a fresh full-panel run after `PHASE_A_COMPLETE`:**
   commit-stamped Phase-1 rows resume forward only when their stamp-commit ≥
   the last P1 engine change (C1/C2/C3) — a pre-fix stamp would attribute P1
   parser fixes to P2.3 in the pre/post delta. Default: start from zero
   (the resume machinery still guards mid-run crashes). + the 200-row
   held-out. **A16 — cost line, estimate unmeasured:** ~15,400 sentences was
   the pre-pin estimate, superseded by the 17,181-row pinned panel (the
   1,781-row gap lived only in council #24); the 51-GPU-h figure prices
   17,181 × 3 × an unmeasured 4 s/probe JJK number (council #3 (d)(2): "the
   58-GPU-h is still fiction"; JJK warm probe measured ≈0.47 s → ≈8 h at
   JJK's rate; the on-disk CSM ceiling is 8.5 s/probe CPU@150k @ `f81a1af`
   ≈ 122 h). **The sanity-100 re-estimate (A15) decides the budget; no panel
   hour is spent before it exists on disk.** Batched, checkpointed, resumed
   in Qwen quiet windows via the gpu-handoff chain (`docs/ops/PC_GPU_HANDOFF.
   md` — reserved for exactly this). **A19 — at the 100k dial the sanctioned
   mechanism is the chain's tier-1** (no-flip batched side session in Qwen
   quiet windows); the tier-2 262k→100k handoff fires only if VRAM forces
   the 64k dial-down (the plan's "measure, don't guess" clause). **A17 —
   exit = a pre-declared per-door floor policy** (council #3 (d)(1),
   recorded in GATE.md before the sweep): the qa door grades in JJK's 97.5 %
   band (the standing 400-gate's ≥390/400 hit band applied to the full
   panel); roster + narrative are structurally low-yield on verbatim-line
   probes (G-CSM-2: the qa fact/passage leg is dead wholesale on CSM; the
   roster door was functionally dead until `bc73795`) — their floors are
   the measured sanity rates, declared as documented floors, not regression
   targets. "Miss file empty" applies only to the qa door; on the low-yield
   doors closure = floor + every residual miss triaged into the triage log
   with class + reason. Zero-hit sanity on qa → the G-CSM-2 disposition
   (route to CSM-7, document the floor, do not burn the sweep hours);
   zero-hit on roster/narrative = a documented corpus-property floor,
   recorded, not a halt. Per-door raw numbers into `reports/csm/GATE.md`.
   **A26 (optional, belt-and-suspenders — Ruling 7 already recomputes-and-
   enforces the panel hash at load and `tools/csm/panel_heldout.py`
   validates the held-out shape):** at P2 start, record `panel_csm.json`
   's stored hash + the held-out file's hash into GATE.md, so the
   control-arm inputs are frozen in the receipt (add if a panel edit ever
   lands between the marker and P2.1).
2. **P2.2 Bar audit (A21 — de-duplicated against P1.4(d), pre-registered,
   gating):** P2.2 = "**ran in P1.4** (close condition d, pre-marker); re-
   grade only if P2.1's misses change a dimension." Pre-registration
   (named, on disk before the marker): 3–5 cases per D6 census class (the 6
   census classes — arc-narrative / abilities / state-over-time / appearance
   / causality / personality — not JJK's 14) pulled from panel lines, so
   the control arm's output is directly adjudicated + an owner-accepted
   residual cap; grader = a fresh-context subagent authors the cases
   (executor never edits — campaign-council D4 ruling: "the executing agent
   must not author its oracle"), graded mechanically per JJK 3b (no LLM
   judge). **P2.1 starts only on the on-disk verdict.** (Council #24 blind-
   spot: the done-set is a reachability proxy until this audit proves it
   transfers.)
3. **P2.3 D6 extraction (only on the red class, JJK precedent).** The 21-red
   census class (recounted from the raw
   `reports/csm/census_dimensions_csm_results.jsonl`: arc-narrative **8**,
   abilities **6**, state-over-time **5**, appearance **1**, causality **1**
   — plus whatever the P1.4 re-adjudication leaves or adds) → events +
   meaning layer, contingent per the council-#19 P4 ruling. **A14 flag:
   this is the plan's sole comprehension step** — if it does not fire, the
   D1–D10 done-set closes on triage-log lines, not understanding (the
   plan's own P2.2 concession, verified). Whether to de-contingent it or
   add a numbered D6 comprehension item is the **Phase-2 council's
   decision** (owner phase-scoped instruction 23:2x). **A22 — council
   ruling (this record's P2 council): the null branch — the P1.4 5.4 re-
   adjudication closes all 21 reds, de-scoping P2.3 entirely — voids P2.5,
   it does not pass it** (the done-set closing on triage-log lines with no
   comprehension layer = the goal noun unmet; JJK's D8 "no reds → nothing
   built" was about contingent build sets, not the comprehension layer, and
   does not transfer to CSM's understanding noun). The default path de-
   contingents P2.3: a numbered **D6 comprehension item (P2.3b)** — extract
   the meaning layer over the red class ∪ a pre-registered sample of the
   green class (N panel lines per green dimension, frozen before the
   extraction), so the comprehension step fires even at 0 reds. If the
   owner refuses P2.3b on budget, the null branch stands: P2.5 is void, the
   campaign halts with the triage log + a dimension census recounted from
   the raw jsonl at P2 start. Then the
   pre-registered **extraction-pass test**: the same 400-gate + red
   dimensions green post-extraction + the 200-row held-out out-of-sample.
4. **P2.4 Writer-facing acceptance leg (A23 — done-criterion, not a last
   step):** one `script-gen` + `cli verify` against CSM (the instrument —
   one script is sufficient; the bar is what makes it a criterion).
   **Pre-registered pass bar (named before the run):** every tag resolves
   to a chapter/episode through the graph, zero unverified (a chapter the
   anime never adapted gets no episode — the verify backstop); the §5 last
   clause (COMPREHENSION_REMAINDER §5: "a writer can ask, of any line, what
   it means and where it sits") is carried into P2.5's done-declaration
   with this receipt attached (A24(b)). The done-set must mean something to
   the writer consuming `/context`, not only to the census. **A27
   (optional, scope expansion — owner call):** a CSM caption import + embed
   buys verbatim `[E n mm:ss]` quotes for CSM scripts (`transcripts.py`
   docstring: "JJK only, for now"; the JJK corpus is 16,226 embedded
   points, ~3.5-min CUDA embed). Pre-registered probe: CSM caption-source
   availability, checked before any commitment; one import + embed if the
   probe is green (add when P2.4's pass bar demands verbatim timestamps on
   CSM and the probe is green).
5. **P2.5 CSM-8: done-declaration + pilot memo (A24 — the full receipt
   set).** The D1–D10 done-set on CSM, item by item, raw numbers (JJK
   `DONE_DECLARATION.md` as the template), and, on disk, before any "done"
   word: (a) P2.1's measured s/probe + per-door raws + the panel hash into
   `reports/csm/GATE.md` (skeleton lands in P1.1/C3) — including the 200-
   row held-out out-of-sample number (a memorised panel looks green); (b)
   the P2.4 receipt (pass bar met); (c) the triage log for every residual;
   (d) the four pilot numbers, **named** per campaign-council item 8: #1
   T0 emergence (843 questions vs the JJK-derived ~535 — `t0_pilot_csm.
   json`, on disk) · #2 T0 survival (843/843 = 100 % — on disk) · #3 new
   numbered gaps · #4 human round-trips (item-8 deliverables, to be
   produced); (e) the JJK baseline diff-empty against the **named**
   baseline — the 2026-09-08/09 re-baseline (pytest 1,303+2xp = 1,305
   collected; eval 31/31; span-recall 48,572/48,572 + ≥390/400 @ 97.5 %;
   canon opm 236/236 @ 79.0 % per `GATE_REBASELINE_2` + plan process §6) —
   **not the stale 1,242** (`GATE_REBASELINE.md` round 1); (f) the P2.3
   null-branch evidence (the P2.3b receipt or the re-verified dimension
   census); (g) the bar-audit verdict (P2.2/A21); (h) a new
   `PHASE_B_COMPLETE <ts>` marker (`reports/master-work/phase_status.txt`) —
   the plan names no Phase-2 completion marker today. **Halt before P6**
   recorded.

## Cost & schedule (re-anchored by the P2 council, A25)

Phase-1 remainder ≈ **2–3 days** (P1.1 ~1 h of gate time after its
preconditions · P1.2 ~1 day · P1.3/P1.4 ~1 day). **Phase 2 ≈ unmeasured:**
the 51-GPU-h line is an estimate; the A15 sanity re-estimate decides the
budget (≈8 h at JJK's measured rate vs ≈122 h at the on-disk CSM CPU
ceiling; 2–4 worker concurrency, undecided per council #3 (d)(2), swings
wall-clock 2–4× — dial and concurrency *are* process changes, so the
frozen-number framing is retracted). P2.2–P2.5 ≈ 1 day **plus the priced
legs**: the phase-close council cycle (11-member, ≈ 2 h wall), the four
one-copy gate re-runs, the P2.4 leg, and any P1.3/P2 halt-trigger councils
if they fire. Total wall-clock ≈ re-estimate + those legs (≈1.5–2 weeks
holds only if the re-estimate lands near ≈8 h and the shrunk process layer
stops eating wall-clock). "100 %" (the D1–D10 set) is unreachable in Phase
1 alone (the 22 extraction-gated floors).