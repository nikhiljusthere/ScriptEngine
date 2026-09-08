# COUNCIL csm-3b — CSM-3b close decision

- **Date:** 2026-09-08
- **Campaign:** CSM (Comprehension System), wave **CSM-3b** (close decision)
- **Method:** 5 advisors (sequential) → 5 anonymized peer reviews (sequential,
  deterministic letter map: A=first-principles, B=outsider, C=contrarian,
  D=executor, E=expansionist) → chairman synthesis. One agent at a time
  (owner rule 2026-09-08). Fresh context per agent; artifacts in
  `reports/csm/council_csm-3b/`.
- **Chairman:** fresh-context subagent (this record); may overrule the
  majority where the reasoning supports it. Owner retains final authority.

## Framed question

CSM (Comprehension System) campaign, ScriptEngine repo, wave CSM-3b close
decision. Facts (all in the evidence files): (R1+R7) the span-recall
roster-door fix and panel-hash enforcement landed (engine commit f93d396,
close-out commit bc73795). The full standing-gate cycle was re-run on CUDA
and matches the 2026-09-08 re-baseline exactly: pytest 1,254 passed;
eval jjk 31/31; span-recall jjk 48,572/48,572 offline + 390/400 live probe
(97.5%); canon opm 10/16 exact, 236/236 canon, 79.0% precision. The
39-question CSM seed bank (questions/csm.json, measured by
`canon-run --series csm` — NOT the eval harness; gold_csm.json never
existed and is deliberately absent) shows NO NEW FAILS vs the CSM-1b
post-fix baseline (11/19 exact, 138/148 canon); known engine gaps
G-CSM-1 (csm-set-14 recall 0/5) and G-CSM-2 (csm-fact-06 empty qa bundle)
persist, scheduled for CSM-4/CSM-5. Heldout-panel live sanity: 4/4 HIT
(8/8 cumulative in the csm sweep ledger). Open findings: (F1) the
span-recall ledger pair (sweep_qa.jsonl + .new) is shared per series, not
per panel — a run on one panel merges only its own keys and then unlinks
the shared sidecar, silently dropping the other panel rows: a heldout
sanity run deleted 168 pinned-sweep progress rows from disk (recoverable
from git bc73795; proposed fix: key the ledger by panel hash). (F2)
gold_csm.json absent by design (bank is canon-run shaped; creating it is
an engine-design decision, flagged as a CSM-4/council item if ever
wanted). (F3) two false-positive monitor kills of pytest under the old
monitor rule-2 (it checked the bash wrapper fds, which never hold nvidia
fds during cold CUDA init); Control A ruled and replaced rule-2 (kill only
provably-CPU cases; default-device in-process = assumed CUDA, 300s LONG
flag). Decision before the council: (a) close CSM-3b as complete, or
reopen it? (b) Wave 2 (CSM-6 instrument + CSM-5 remainder) priority: fix
F1 before the Phase-2 exhaustive pinned-panel sweep (17,181 probes,
GPU-only) — or accept the git-recovery workaround? Fix G-CSM-1/2 now
instead of waiting for CSM-4/5? (c) any of F1/F2/F3 (or anything the
evidence surfaces) that the council should rule on?

**Evidence files:** `reports/csm/CSM3B_GATES.md` (gate-cycle receipt),
`reports/csm/COUNCIL_csm-3.md` (Rulings 1/3/7/8), `plan/CSM_2PHASE_PLAN.md`,
`reports/comprehension/COMPREHENSION_REMAINDER.md`, engine footprint
`git show f93d396 --stat`.

---

## Advisor responses (full text)

### Advisor 1 — The Contrarian

# Advisor 1 — The Contrarian (CSM-3b close council)

**Close the 3b gate cycle; CSM-3b as declared is not safe to close. One
receipt is missing from the close record; one live landmine sits in a temp
file on disk.**

**Roster door: no live proof this cycle.** CSM-3 Ruling 1 required a live
re-probe (31 members / 0 chars → must serve chars). The 3b gate cycle ran
only the held-out sanity-4, default door (qa) — zero roster probes in the
csm3b logs or the ledger pair; the only live "roster works" evidence on
disk is `GCSM1_ROSTER_DOOR.md`, a raw `build_roster` at git head 42aa296,
pre-CSM-3, before `served_text`/`returned_docs` were touched. Phase 2's
roster sweep (1/3 of the ~51 GPU-h) would launch on fake-bundle unit
proof only (the 13th `test_span_recall` test monkeypatches `_ask`), on a
failure mode this council already found live once. One 30-second
`/context` probe at door=roster on that line closes it — required before
Phase 2.

**F1: Phase-2 blocker, not a "documented workaround."** The 168-row
sidecar sits on disk *right now* at the temp path the merge contract
unlinks on the next csm span-recall run; the rows are CPU-provenance
(1200-s incident) with no device/commit field; Phase 2 runs in a fresh
side session with no memory of the git-recovery step. Recurrence means
50+ GPU-h lost, recoverable only by a human remembering a git command.
Fix now, while the ledger pair is 176 rows: key the ledger by panel hash
(or make the merge preserve cross-panel keys), stamp device/commit onto
rows, and re-probe the 168 on GPU (~3 min) for provenance purity.

**Wave 2: F1 is item 0** — fold it into the CSM-6 worker (both are
`span_recall.py` / sweep-infra territory); **G-CSM-1/2 stay at
CSM-4/CSM-5** — plan sequencing, and the 2-worker wave budget is already
full (CSM-6 + CSM-5). Don't pull the known gaps forward.

**Rulings:** F1 — Phase-2 blocker, fix in Wave 2, not a workaround. F2 —
absent-by-design upheld; a csm eval-gold bank is a separate design change
if ever wanted. F3 — the rule-2 replacement is acceptable only with an
ack loop: A acks each LONG flag within one control batch and kills
provably-CPU in-process work over 15 s; without that loop the flag is
theater.

### Advisor 2 — The First Principles Thinker

# First principles — CSM-3b close decision

**Strip the "gate = re-baseline, therefore complete" assumption.** The
four standing gates match the re-baseline exactly: a no-regression guard,
not progress. Against the checkable 100% definition (every line
classifiable; every event with a participant set + arc_index; the D1–D10
set), CSM-3b moved zero numbers: the only CSM-specific signal (seed bank
11/19 exact, 138/148 canon, G-CSM-1/2 persist) is identical to CSM-1b.

**CSM-3b is Phase 1: it builds the instrument.** Phase 2 measures
(17,181 × 3 doors) and fires D6 extraction only if the census goes red.
CSM-3b's deliverable is *measurement trust*: the roster door —
structurally zeroing 1/3 of the Phase-2 sweep — now flattens
`members`/`passages`, with a roster-shaped test (suite 13/13); the sweep
now reports the hash of what it actually ran (Ruling 7); the held-out 200
has a named consumer. The right bar for a fixing wave; met.

**(a) Close CSM-3b as a wave.** Scope complete (Rulings 1+7 verified,
gates re-baselined, `bc73795`/`78b5cf3`); do not reopen — F1 belongs to
Phase 2, not to CSM-3b's scope.

**(b) F1 is a hard precondition of the Phase-2 sweep.** The merge
contract (`span_recall.py:440-452`) rewrites the ledger with *only the
current panel's keys*, then unlinks the shared sidecar — a held-out run
silently dropped 168 pinned rows. Git is a backstop, not a state machine:
the sidecar is the only thing protecting a multi-day GPU resume. Fix —
ledger keyed by the panel hash Ruling 7 already stamps — is zero-GPU,
lands in Wave 2, and yields Ruling 8's fresh-results-file for free.
**G-CSM-1/2: diagnose in Wave 2, fix only the cheap ones.** The sweep
re-exposes both gaps 17,181 times; root-cause them offline now, route
expensive residue to CSM-5. Do not fix blind before measurement.

**(c) Rulings:** (1) F1 = CSM-4 blocker, recorded in GATE.md. (2) Ruling
1 is unit-verified only (monkeypatched `_ask`); the live check is
Ruling 3's N=100 roster sanity — record that so the done-declaration
does not overclaim. (3) F2/F3: record, no action.

### Advisor 3 — The Expansionist

# The Expansionist (CSM-3b council, advisor 3/5)

Close CSM-3b — but bank the two byproducts as campaign assets, not
footnotes.

**(a) Close.** All four standing gates identical to the 15:22–15:26
re-baseline, seed bank no NEW fails (11/19 · 138/148 = CSM-1b post-fix,
G-CSM-1/2 persist as scheduled), sanity-4 8/8 cumulative HIT. Nothing in
CSM-3b scope is left open. One condition: rule F1 a CSM-4 precondition
(below).

**(b) Fix F1 before the Phase-2 exhaustive sweep — it is small, and it
converts the trap into an asset.** The F1 sidecar trap (ledger pair
shared per series, not per panel; a merge on one panel silently unlinks
the other panel's rows — today: 168 pinned-sweep rows dropped from disk)
is the seed of a general *resumable, auditable per-panel ledger*. Key
the ledger by panel hash and the 17,181×3 sweep, the 200-row heldout,
and every future panel get their own append-only, committable, diffable
progress record. That is what turns the 1200-s incident from a one-off
into a closed bug class. The git-recovery workaround is a band-aid: the
third door batch's resume hits the same trap again. G-CSM-1/2 stay in
CSM-4/5 — pulling them forward mixes the measurement pass with a fixing
pass, and §9a (the fixing agent never grades its own fix) exists for
exactly this.

**Undervalued upside if this wave lands clean:**
1. **The instrument is series-agnostic** — `build_panel`/`--panel`/
   `--door`/`--sanity` + Ruling-7 bare-list loading take any series. CSM
   is the first of the 8 wikis with a pinned, resumable exhaustive
   tier-1; the same sweep runs on JJK's 48,572 lines, where D5
   exhaustive *has never run* (COMPREHENSION_REMAINDER §2a). That is the
   P6 unlock nobody is pricing.
2. **The seed-bank method** — revid-stamped `questions/csm.json` +
   `canon-run` (7 s, zero GPU, rc=0) — is a per-wiki comprehension smoke
   test. Standing-gate candidate #5 for all eight wikis: "does the
   engine still answer the campaign's own questions."
3. **The 200-row heldout is a free out-of-sample fixture.** A 200-probe
   CUDA probe is minutes — a standing early-warning number after every
   reindex, far cheaper than the exhaustive sweep.

If CSM-3b closes green, Phase 2 stops being "the CSM sweep" and becomes
the cross-wiki D5 template. Price that, not the gate cycle.

### Advisor 4 — The Outsider

**Verdict: close CSM-3b.** The four standing gates match the re-baseline
exactly, both engine fixes (roster-door, panel-hash) are committed and
green in the 1,254-test suite, and every open item (F1, G-CSM-1/2) has a
documented owner and schedule. That is a close, not a dodge; reopening
adds no signal.

A fresh-eyes read still flags three things:

1. **The receipt is not self-contained.** CSM3B_GATES.md says "COMPLETE"
   and "matches re-baseline" but assumes the reader knows what CSM-3b
   was and what the re-baseline numbers are. Phase 2 runs on receipts
   alone (side sessions, Qwen quiet windows); a reader who has not read
   COUNCIL_csm-3.md cannot reconstruct this wave. Add a five-line "what
   this wave delivered" header to the receipt or SWITCHPOINT. Cheap,
   high value.

2. **F1 is an efficiency trap Phase 2 will hit again.** Because
   hit_rate uses the full-panel denominator, the wiped 168 rows
   corrupted no number — they only cost re-probe time. So git recovery
   "worked" by luck, not by design. Phase 2 is 17,181 probes × 3 doors,
   ~2 GPU-days, unattended: any interleaved sanity run silently re-burns
   hours of GPU. The fix (key the ledger by panel hash) is a few lines —
   land it inside the CSM-4 wave, before the sweep starts. That is the
   one ruling I want recorded.

3. **Check G-CSM-1/G-CSM-2 before CSM-5.** If either is a zero-GPU
   cheap-signal fix (like the 5.4 door pre-check), pull it into Wave 2.
   Also keep the labels apart: 4/4 sanity is liveness, not health — the
   real state is 57.9% exact with two zero-recall questions.

F2: no ruling needed — intentional, already documented. F3: not a council
item, but verify monitor rule-2 before any unattended Phase-2 window; a
kill heuristic that already killed two CUDA jobs is a pre-flight check,
not a formality.

### Advisor 5 — The Executor

# Advisor 5 — The Executor (CSM-3b close)

**Close CSM-3b today — <30 min, zero GPU.** All four standing gates sit
at re-baseline, the seed bank shows zero new FAILs, and R1/R7 are
verified landed (f93d396 + bc73795, roster-door test in the suite).
Reopening without a new failure buys nothing; the close-out is just the
council verdict + the COUNCIL_HISTORY line + the SWITCHPOINT 3b line.

**F1 is the critical-path trap — fix before Phase 2. Cost: one subagent
hour, zero GPU.** The 17,181 × 3-door exhaustive sweep is the campaign's
critical path (≈8–17 GPU-hours at the measured 0.49 s/probe CUDA rate;
the plan's 51 h is an unmeasured JJK figure per CSM-3's chairman), and
F1 guarantees it: every cross-panel run unlinks the other panel's
sidecar — it already fired once (168 rows dropped from disk). The
git-recovery workaround costs nothing today but arms the trap at every
Phase-2 panel switch; whoever trips it mid-sweep loses hours of GPU
probes and a recovery trick that isn't written down. Concrete first
step: key the ledger pair by the 8-char panel hash (`sweep_<hash8>.jsonl`
+ `.new`) in `span_recall.py` resume/merge — ~30-line diff + one test,
and restore the 168 rows into the pinned-keyed ledger. Run it as a small
pre-step of Wave 2 (sequential, *before* the two parallel Wave-2
subagents — the wave cap is on parallel subagents, not prep work) and it
must land before the Phase-2 400-probe standing gate. Verification cost:
pytest 1,254 in-process CUDA (~3 min, one-copy ordering) + probe-400
(~3.5 min HTTP).

**Do not pull G-CSM-1/2 forward.** The CSM-5 remainder (5.3–5.5 + the
20-failure set) is exactly the slot that consumes them, and Wave 2 is
already at the two-subagent cap. F2: leave `gold_csm.json` absent — zero
cost; revisit at CSM-4 only if an eval-harness csm bank becomes needed.
F3: A already ruled the monitor fix; nothing for me to do.

**GPU budget this week:** Wave 2 is zero-GPU (CSM-6 explicitly
no-extraction; CSM-5 zero-GPU except the conditional 5.4 extraction,
which fires only on a red dimension census). The only GPU-hour block is
the F1 verification (~7 min) plus the exhaustive sweep itself (~8–17
GPU-hours, batched in a tier-2 side session via the gpu-handoff chain,
100k dial, one-copy). Everything else fits the 15 s CPU rule.

---

## Peer reviews (full text)

### Reviewer 1

All five files present and non-empty (A=first-principles, B=outsider,
C=contrarian, D=executor, E=expansionist).

**1. Strongest: C (Contrarian).** Only response to catch the concrete
evidence gap the others glossed: the roster door — Phase 2's largest
consumer (1/3 of sweep GPU-hours) — has no live proof in the 3b cycle
(unit-level monkeypatched `_ask` only, plus pre-CSM-3 42aa296 evidence).
C also names F1 a live armed landmine (sidecar on disk now,
CPU-provenance 168 rows, no device/commit field, a fresh side session
won't remember the git recovery) rather than a "documented workaround",
and demands the 30-second `door=roster` probe before Phase 2.

**2. Biggest blind spot: E (Expansionist).** All upside pricing
(cross-wiki D5 template, P6 unlock, gate #5, heldout fixture), zero
critical-path risk. E prices a "clean close" before validating the
instrument's largest consumer, ignores F3's flag-theater point, and
never touches provenance.

**3. What all five missed:** (a) F1's fix rekeys the ledger files in the
code Ruling 7 just shipped — migrating the committed `sweep_qa.jsonl`/
`.new` pair, the 400-probe gate command that references that path, and
resume-key semantics are all unbudgeted. (b) The council's new items (F1
+ roster probe + optional G-CSM diagnosis) collide with the two-worker
cap — a de-facto Wave 2.5 before the Phase-2 400-probe gate. (c) The 8
cumulative live rows are the only clean csm evidence; the 168 rows are
CPU-provenance, so Phase 2 resumes from a provenance-tainted ledger
unless re-probed.

### Reviewer 2

**1. Strongest: C (the contrarian).** The only response that surfaced a
new landmine instead of adjudicating the record: the csm3b gate cycle
ran zero live roster-door probes (sanity-4 is qa-door; the only live
roster evidence, `GCSM1_ROSTER_DOOR.md`, predates CSM-3), yet a third of
the Phase-2 sweep is roster — a 30-second `/context` probe at door=roster
closes it. C also correctly notes the 168-row sidecar is armed *right
now* on disk, CPU-provenance, with no device/commit stamp. A's "guard ≠
progress" framing is a close second — cleanest epistemics, no new
findings.

**2. Biggest blind spot: E (the expansionist).** All upside, no
downside: no cost for the F1 ledger keying (migration of the live 168+8
rows, interplay with Ruling-7 hash enforcement), and unverified
expansion claims (JJK D5 exhaustive "never ran"; the heldout as
standing gate #5) asserted without checking.

**3. What ALL five missed:** F1 is framed as a Phase-2 blocker, but the
§9a closure-loop iteration 1 — the next pinned-panel batch sweep, due
right after Wave 2 and *before* Phase 2 — is the first unattended GPU
event that can fire the trap (pinned-vs-heldout interleaving) and the
first sweep needing C's roster probe. So the F1 fix + roster probe is a
**§9a precondition (Wave-2 pre-step), not merely "before Phase 2"**; and
the 168/8-row migration with device/commit stamps remains unspecified.

### Reviewer 3

**1. Strongest: C (contrarian).** Its finding is new and verifiable: zero
roster probes in the 3b cycle (sanity-4 ran the default qa door), so the
roster sweep (1/3 of Phase-2 GPU) would launch on monkeypatched unit
proof + pre-CSM-3 live doc (42aa296); a 30-second /context probe at
door=roster settles it. C also nails F1's worst case (re-armed .new at
the temp path the next csm run unlinks; CPU-provenance rows;
side-session amnesia) and F3's ack loop. (D close second: concrete diff
+ ordering.)

**2. Biggest blind spot: E (the expansionist).** Skips the roster-door
live-proof gap, prices F1 at lowest urgency (CSM-4 precondition vs
Wave-2 item 0), and banks on upside the plan defers (cross-wiki D5 =
P6, out of this run). E reads the close as upside, not close-safety.

**3. All five missed:** (a) **no verification spec for the F1 fix** — no
interleaved two-panel survival probe (pinned sanity → heldout sanity →
assert both ledgers), no named test, and no §9a note that the
orchestrator, not the fixing subagent, grades it. Unverified, the ledger
fix is a second trap. (b) **F3's rule-2 replacement should land in
GATE.md as a Phase-2 pre-flight line**, not stay in interventions.jsonl
— side sessions only read the receipt.

### Reviewer 4

**1. Strongest: D.** Only response that fully answers (a)(b)(c) with
numbers: F1 as a ~30-line diff + one test as a *sequential pre-step*
before the two-parallel Wave 2 — the wave cap is on parallel subagents,
not prep work (the key sequencing insight); verification ~7 min (pytest
1,254 in-process CUDA + probe-400); sweep cost corrected from the plan's
51 h to 8–17 GPU-h; clean "do not pull G-CSM-1/2 forward" call.

**2. Biggest blind spot: A.** "Diagnose G-CSM-1/2 in Wave 2, fix only
the cheap ones" — but Wave 2 is at the two-subagent cap with both slots
filled (CSM-6, CSM-5). A diagnosis task either breaks the cap or
displaces a slot. A ignores the budget constraint that C and D both
respect.

**3. What all five missed:** the close is already recorded on disk —
SWITCHPOINT 3b stamped @ 78b5cf3, CSM3B_CLOSEOUT.md committed. The
verdict (ratify vs reopen) needs a defined ratify/amend path, or a
reopen leaves stale "complete" artifacts that an unattended Phase-2 side
session will inherit and trust.

### Reviewer 5

**1. Strongest: C.** The only response with two new findings of its own:
(a) no live roster-door proof this cycle — the 13th suite test
monkeypatches `_ask`, and the only live "roster works" evidence on disk
predates CSM-3, so Phase 2's roster sweep (1/3 of the GPU-hours) would
launch on unit proof alone; (b) F3's 300-s LONG flag is "theater" without
an A-ack loop. Also the most operationally precise: names the live
temp-path sidecar, the CPU-provenance of the 168 rows, and the
fresh-side-session amnesia that makes git-recovery a 50+ GPU-hour
recurrence, not a workaround.

**2. Biggest blind spot: E.** Its upside case (JJK 48,572-line D5
exhaustive, standing-gate #5, 200-row fixture as cross-wiki template)
prices P6-adjacent value that this run explicitly defers ("JJK only;
stops before P6"). Every upside it lists is conditioned on the F1 fix +
Phase-2 sweep succeeding — neither is a Phase-1 done-criterion. It is
the only response that silently re-scopes the campaign, and it prices
the re-scoping at zero cost.

**3. What all five missed: the 168-row provenance fork.** C says
re-probe the 168 rows on CUDA (~3 min) for provenance purity; D says
restore them as-is into the pinned-keyed ledger; A, B, E never address
it. Phase 2 is GPU-only, so restoring CPU-provenance rows (1200-s
incident) into the resume ledger silently contaminates the sweep state.
The council should rule: re-probe and drop, or restore with a
device/commit stamp — and record which.

---

## The Verdict

## Where the Council Agrees

- **Close CSM-3b as a wave** — unanimous. All four standing gates sit
  exactly on the 2026-09-08 re-baseline (pytest 1,254; eval jjk 31/31;
  span-recall jjk 48,572/48,572 offline + 390/400 live; canon opm
  10/16 · 236/236 · 79.0%); R1+R7 verified landed (f93d396, bc73795,
  close-out 78b5cf3); the seed bank shows no NEW fails vs the CSM-1b
  post-fix baseline (11/19 · 138/148, G-CSM-1/2 persist as scheduled);
  heldout sanity 8/8 cumulative HIT. A re-baseline gate is a
  no-regression guard, not progress — but CSM-3b is a *fixing* wave and
  its bar (measurement trust: roster door flattens members/passages,
  sweep reports the hash it actually ran, held-out 200 has a named
  consumer) is met. Reopening without a new failure buys nothing.
- **F1 (ledger sidecar trap) is a hard precondition, fixed in Wave 2 as
  a zero-GPU pre-step — the git-recovery workaround is rejected.**
  Unanimous on substance: the trap already fired once (168 pinned rows
  dropped from disk), it re-arms on every cross-panel run, Phase 2
  (17,181 × 3 doors, unattended) and §9a iteration 1 both expose it, and
  a fresh side session will not remember a git recovery trick.
- **G-CSM-1/2 stay scheduled at CSM-4/CSM-5** (majority). Wave 2 is at
  the two-subagent cap; §9a keeps the fixing agent from grading its own
  fix.
- **F2: gold_csm.json stays absent by design** (bank is canon-run
  shaped; unanimous, no action).
- **F3: the rule-2 replacement is accepted with an accountability
  condition** (ack loop + pre-flight verification), not as a formality.

## Where the Council Clashes

- **Roster-door live proof — when it gates.** The Contrarian: zero live
  roster probes this cycle (sanity-4 is qa-door; the only live roster
  evidence, `GCSM1_ROSTER_DOOR.md` @42aa296, predates CSM-3; the 13th
  suite test monkeypatches `_ask`) → the Phase-2 roster sweep (1/3 of
  the GPU-hours) would launch on unit proof alone; a live
  `door=roster` check (Ruling-1's 31-member line must serve chars,
  escalating to Ruling-3's N=100 roster sanity) is a **hard
  precondition** before §9a/Phase 2. The First Principles Thinker
  agrees Ruling 1 is unit-verified only but treats the live check as a
  *recorded condition of the done-declaration*, not a sweep gate. The
  chair sides with the Contrarian's stronger claim: Ruling-1's own
  verification spec ("re-probe the 31-member line → must serve chars")
  was never executed live, and this exact failure mode was found live
  once already — a 30-second probe is not worth shipping the sweep's
  largest consumer on untested code.
- **The 168-row provenance fork** (surfaced only in peer review). The
  Contrarian: re-probe the 168 rows on CUDA (~2–3 min at the measured
  0.49 s/probe) for provenance purity — they are CPU-provenance from the
  1200-s incident with no device/commit field. The Executor: restore
  them as-is into the pinned-keyed ledger. A/B/E never addressed it.
  The chair rules **re-probe and stamp**: Phase 2 is GPU-only, so
  restoring CPU-provenance rows into the resume ledger silently
  contaminates sweep state; ~2 minutes of GPU buys a clean provenance
  story and costs a rounding error against the 8–17 GPU-h sweep.
- **G-CSM pull-in.** The Outsider and First Principles Thinker want a
  zero-GPU diagnosis pre-check (pull cheap fixes into Wave 2); the
  Contrarian and Executor say don't touch — CSM-5 is exactly the slot
  that consumes them, and Wave 2 is cap-full. The chair keeps the
  schedule (CSM-4/5) but gives the CSM-5 brief one zero-GPU
  root-cause pre-check line, so Wave 2 costs no subagent slot and the
  sweep doesn't re-expose both gaps 17,181 times without a diagnosis on
  file.
- **Where F1 lands.** Label split: "Phase-2 blocker" (Contrarian) vs
  "lands in the CSM-4 wave" (Outsider/Expansionist) vs "Wave-2
  sequential pre-step" (Executor). Peer review resolved it: §9a
  iteration 1 (the pinned-panel batch sweep due right after Wave 2,
  before Phase 2) is the *first* unattended GPU event that can fire the
  trap — so F1 is a **§9a precondition**, i.e. a Wave-2 pre-step that
  must land before the two parallel Wave-2 subs deploy.

## Blind Spots the Council Caught

*(Emerging only through the peer-review round; individual advisors
missed each of these.)*

1. **The F1 fix needs a verification spec** — interleaved two-panel
   survival probe (pinned sanity → heldout sanity → assert *both*
   ledgers survive) + a named test in `test_span_recall.py`; §9a note
   that the orchestrator (never the fixing subagent) grades it.
   Unverified, the ledger fix is a second trap. (Reviewer 3)
2. **The F1 re-key migration scope is unbudgeted** — re-keying the
   ledger pair touches code Ruling 7 just shipped: migrating the
   committed `sweep_qa.jsonl`/`.new` pair, the 400-probe gate command's
   path reference, and resume-key semantics. The wave cap is on
   *parallel* subagents, not sequential prep — the pre-step fits.
   (Reviewers 1, 2)
3. **§9a iteration 1, not Phase 2, is the first unattended GPU event**
   that fires F1 — the fix is a §9a precondition, and the done-
   declaration must say so. (Reviewer 2)
4. **The 168-row provenance fork** — CPU-provenance rows restored as-is
   contaminate a GPU-only resume state; the council must rule re-probe
   + stamp vs restore-as-is and record which. (Reviewer 5)
5. **The receipt is not self-contained** — Phase-2 side sessions read
   receipts alone; a five-line "what this wave delivered" header on
   `CSM3B_GATES.md` (or SWITCHPOINT) is cheap, high value. (Outsider)
6. **F3 must land in GATE.md as a Phase-2 pre-flight line** — side
   sessions read receipts, not `interventions.jsonl`; a kill heuristic
   that already killed two CUDA jobs is a pre-flight check. (Reviewer 3,
   Outsider)
7. **The close is already recorded on disk** (SWITCHPOINT 3b @ 78b5cf3,
   `CSM3B_CLOSEOUT.md` committed) — the verdict needs a defined
   ratify/amend path, or a reopen leaves stale "complete" artifacts an
   unattended side session will inherit and trust. (Reviewer 4)

## The Recommendation

**Close (ratify) CSM-3b as complete**, with three hard preconditions —
all zero-GPU, all a sequential Wave-2 pre-step, deployed *before* the
two parallel Wave-2 subs and *before* §9a iteration 1 / the Phase-2
400-probe standing gate:

1. **F1 ledger fix** (R-CSM3B-2): re-key the ledger pair by 8-char
   panel hash, stamp device+commit on rows, migrate the committed pair,
   re-probe the 168 CPU-provenance rows on CUDA, add the two-panel
   survival test. ~30-line diff + one test.
2. **Live roster-door check** (R-CSM3B-3): Ruling-1's 31-member line
   must serve chars at `door=roster` (escalate to Ruling-3's N=100
   roster sanity if low-yield). Record the live result in the done-
   declaration.
3. **GATE.md pre-flight lines** (R-CSM3B-6 + 7): F3 rule-2 re-verified
   before any unattended Phase-2 window; F1/roster listed as §9a
   preconditions; five-line self-contained header on the receipt.

**G-CSM-1/2 stay at CSM-4/5** (R-CSM3B-4): no pull-in; the CSM-5 brief
carries the zero-GPU root-cause pre-check. **F2 stays as-is**
(R-CSM3B-5): no `gold_csm.json` unless CSM-4 ever needs an eval-gold
shaped csm bank.

The Expansionist's upside pricing (series-agnostic D5 instrument,
P6-adjacent JJK unlock, gate-#5 seed-bank method, 200-row heldout
fixture) is noted as campaign context — it is deferred P6 material,
**not** a Phase-1 done-criterion, and every line of it is conditioned on
the F1 fix + Phase-2 sweep succeeding. It prices the re-scoping at zero
cost; the chair declines to re-scope this run.

## The One Thing to Do First

**The F1 pre-step** (R-CSM3B-2): re-key the csm sweep ledger pair by
the 8-char panel hash (`sweep_<hash8>.jsonl` + `.new`) in
`span_recall.py` resume/merge, stamp device/commit on rows, migrate the
committed 8-row heldout + 168-row pinned ledgers into the keyed names,
re-probe the 168 CPU-provenance rows on CUDA (~2 min), add the
interleaved two-panel survival test, and land it as a sequential
Wave-2 pre-step — *before* the two parallel Wave-2 subagents deploy and
before §9a iteration 1. One subagent hour, zero model work, zero
ambiguity.

## RULINGS

1. **R-CSM3B-1 — Close (ratify) CSM-3b as complete.** All four standing
   gates = re-baseline; R1+R7 verified landed (f93d396, bc73795,
   78b5cf3); seed bank no new fails; sanity 8/8 cumulative; no new
   failure surfaced in the cycle. Ratify/amend path: this record + a
   `COUNCIL_HISTORY.md` ledger line are the close artifacts; a reopen
   requires a fresh council (owner retains final authority). —
   **Execute: orchestrator** (ledger line + SWITCHPOINT stamp @ the
   council commit).
2. **R-CSM3B-2 — F1 is a §9a precondition; fix in Wave 2 as a
   zero-GPU sequential pre-step; the git-recovery workaround is
   rejected.** The first unattended GPU event (§9a iteration 1's pinned
   sweep) fires the trap; git is a backstop, not a state machine. Fix
   spec: (a) re-key the ledger pair by 8-char panel hash
   (`sweep_<hash8>.jsonl` + `.new`); (b) device + commit stamp on rows;
   (c) migrate the committed `sweep_qa.jsonl` (8 heldout rows) +
   168-row pinned sidecar into the keyed names; (d) re-probe the 168
   CPU-provenance rows on CUDA and drop the CPU rows (provenance
   purity); (e) verification = interleaved two-panel survival probe
   (pinned sanity → heldout sanity → assert both ledgers survive) + a
   named test; the orchestrator — never the fixing subagent — grades
   it (§9a). Must land before the two parallel Wave-2 subs deploy and
   before the Phase-2 400-probe standing gate. — **Execute: Wave 2
   (sub 3 / CSM-6 worker owns span_recall.py territory; orchestrator
   grades).**
3. **R-CSM3B-3 — Live roster-door check before §9a / the Phase-2 roster
   sweep.** Re-probe the CSM 31-member line (Ruling-1 verification
   spec) at `door=roster` → must serve chars; if it passes but is
   low-yield, run Ruling-3's N=100 roster sanity (first-run-only per
   Ruling 3). The done-declaration records the live result — Ruling 1
   stands unit-verified only (13th test monkeypatches `_ask`); do not
   overclaim. — **Execute: Wave-2 pre-step (same sequential slot as
   R-CSM3B-2); orchestrator records.**
4. **R-CSM3B-4 — G-CSM-1/2 stay scheduled at CSM-4/CSM-5 (no pull-in);
   CSM-5's brief carries a zero-GPU root-cause pre-check.** The
   two-subagent wave cap is full and §9a keeps fixers and graders
   separate; the sweep re-exposes both gaps 17,181 times, so a
   diagnosis goes on file before Phase 2 — csm-set-14 (recall 0/5) and
   csm-fact-06 (empty qa bundle). Fixes land in CSM-4/5. — **Execute:
   CSM-5 (pre-check) + CSM-4/5 (fixes).**
5. **R-CSM3B-5 — F2 upheld: `gold_csm.json` stays absent by design.**
   The bank is canon-run shaped (`questions/csm.json`, `canon-run --
   series csm`, 7 s, zero GPU, rc=0); an eval-gold-shaped csm bank is a
   separate engine-design item if CSM-4 ever needs it. — **Execute:
   none (recorded).**
6. **R-CSM3B-6 — F3 accepted with an accountability condition: A acks
   each LONG flag within one control batch, and a GATE.md Phase-2
   pre-flight line re-verifies monitor rule-2 before any unattended
   GPU window.** A kill heuristic that already killed two CUDA jobs is
   a pre-flight check, not a formality; without the ack loop the 300-s
   flag is theater. — **Execute: Control A (ack loop) + orchestrator
   (GATE.md line).**
7. **R-CSM3B-7 — The receipt becomes self-contained.** Add a five-line
   "what this wave delivered" header to `reports/csm/CSM3B_GATES.md`
   (scope, R1/R7 landed, gates = re-baseline, seed bank no new fails,
   F1/roster as §9a preconditions) so Phase-2 side sessions — which read
   receipts alone — can reconstruct the wave. — **Execute: orchestrator
   (with the R-CSM3B-6 GATE.md line, same commit).**