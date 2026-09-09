# Peer-review input (anonymized)

## The question

# Council question — CSM 100% campaign audit (2026-09-09)

**Framed by the owner:** "What are we doing wrong? Are we going to fix it faster than JJK? What did we do right with JJK?" — run against the CSM 100% campaign's full history (sessions 09-07 → 09-09), verified in `reports/csm/SESSIONS_REVIEW_2026-09-09.md` (verifier receipts `reports/csm/receipts/sessions_review_verify_A/B/C.md`).

## The decision

Assess the CSM 100% campaign (Chainsaw Man corpus run to the D1–D6
comprehension bar JJK reached) on three questions, then recommend changes to
the remaining path (unit-4 phase close + Phase 2):

1. **What are we doing wrong** — process and technical execution so far
   (A/B bay overhead, 60-min worker timeouts, the gate-3 stale-ESC incident,
   the monitor gap, /tmp state loss on reboot, council cadence vs value, the
   CPU-vs-CUDA :8000 churn, the watch-loops that made the owner close B)?
2. **Can CSM close faster than JJK did?** JJK's page campaign ran 08-19 →
   08-24 (52 clusters) with the final prose-pass state 09-07; JJK's own D6
   comprehension is still open (P0–P5, halt before P6). CSM is ~35 % of JJK's
   line count (panel 17,181 + 200 vs 48,572) and ~54 % of its pages (537 vs
   988). Phase 2 estimates 51 GPU-h for CSM-4 exhaustive tier-1 × 3 doors.
   Is the current pace (3 days → items 0/1/2/3/3b/5/6-instrument done, §9a

## The three review questions (answer all, max 200 words total)

1. Which response (A–E) is the strongest, and why?
2. What is the single biggest blind spot the five responses SHARE?
3. What did all five miss that you would have added?

## Response A



The campaign's fatal flaw: **its validated state lives outside git.** The only
The campaign's fatal flaw: **its validated state lives outside git.** The only
engine work of §9a iteration 1 — R-2+R-3 (`hybrid.py`, `roster.py`, `facts.py`,
engine work of §9a iteration 1 — R-2+R-3 (`hybrid.py`, `roster.py`, `facts.py`,
`series/csm/overrides.yaml`, two test files; `git status` still shows all of it
`series/csm/overrides.yaml`, two test files; `git status` still shows all of it
modified) — has been uncommitted for ~10 hours, ever since the owner's 12:3x
modified) — has been uncommitted for ~10 hours, ever since the owner's 12:3x
override queued a commit that never ran. The staged 2-commit package sat in
override queued a commit that never ran. The staged 2-commit package sat in
`/tmp`; the machine rebooted, `/tmp/csm_iter1_records` is gone (verified:
`/tmp`; the machine rebooted, `/tmp/csm_iter1_records` is gone (verified:
directory absent), and the gate-3 window that was certifying the 9 files was
directory absent), and the gate-3 window that was certifying the 9 files was
voided at ledger row 4,315 — 685 ERROR rows in
voided at ledger row 4,315 — 685 ERROR rows in
`reports/span-recall/jjk/recall_verbatim.jsonl` (verified). "Raw receipts on
`reports/span-recall/jjk/recall_verbatim.jsonl` (verified). "Raw receipts on
disk" protects *files*, not *gated* state: one reboot erased two work-days of
disk" protects *files*, not *gated* state: one reboot erased two work-days of
validation, and recovery is a full CUDA gate re-run. The plan says commit after
validation, and recovery is a full CUDA gate re-run. The plan says commit after
each unit; unit 3 is ~40% done and uncommitted. One more reboot and the campaign
each unit; unit 3 is ~40% done and uncommitted. One more reboot and the campaign
is re-proving work it already finished.
is re-proving work it already finished.


Process is the critical path. 7 councils = 77 sequential LLM runs, ~2h each.
Process is the critical path. 7 councils = 77 sequential LLM runs, ~2h each.
Observed cost per engine class: R-1 ~1 day; R-2/R-3 a day and still uncommitted —
Observed cost per engine class: R-1 ~1 day; R-2/R-3 a day and still uncommitted —
two workers (both hit the 60-min timeout in their final verification loop; R-2's
two workers (both hit the 60-min timeout in their final verification loop; R-2's
receipt was lost and B reconstructed it), a ~2h council, a 2–3h gate cycle (57–77
receipt was lost and B reconstructed it), a ~2h council, a 2–3h gate cycle (57–77
min of it a serial CPU 400-probe at 8.5 s/probe), re-sweeps. R-5, R-6, R-7 each
min of it a serial CPU 400-probe at 8.5 s/probe), re-sweeps. R-5, R-6, R-7 each
repeat the whole cycle. Of 133 commits since 09-07 (verified: 40+72+21), only 16
repeat the whole cycle. Of 133 commits since 09-07 (verified: 40+72+21), only 16
touch `scriptengine/` and just 4 are CSM engine commits. The repo is churning
touch `scriptengine/` and just 4 are CSM engine commits. The repo is churning
governance, not fixes.
governance, not fixes.


The A/B failure mode has already fired: A's stale-pid ESC killed the `:8000`
The A/B failure mode has already fired: A's stale-pid ESC killed the `:8000`
that B's probe depended on, voiding the 400-row window; the monitor's auto-kill
that B's probe depended on, voiding the 400-row window; the monitor's auto-kill
branch is blind to CPU `:8000` children (documented, unfixed). And the summary
branch is blind to CPU `:8000` children (documented, unfixed). And the summary
layer keeps lying — the 49/60 digit transposition, the 29/26 arithmetic, the
layer keeps lying — the 49/60 digit transposition, the 29/26 arithmetic, the
heredoc bug that ate two field names (all CORRECTION lines in `work_log.md`) —
heredoc bug that ate two field names (all CORRECTION lines in `work_log.md`) —
which is exactly why every council spends two hours re-verifying raw files.
which is exactly why every council spends two hours re-verifying raw files.


Schedule: "faster than JJK" is unfalsifiable — JJK's D6 is still open (P0–P5), so
Schedule: "faster than JJK" is unfalsifiable — JJK's D6 is still open (P0–P5), so
CSM is the first corpus run to D6 against a bar the reference corpus never
CSM is the first corpus run to D6 against a bar the reference corpus never
actually passed. Realistic close: 2–4 days to finish unit 3/4 (R-5 + hooks +
actually passed. Realistic close: 2–4 days to finish unit 3/4 (R-5 + hooks +
re-gates + the stuck commit), then Phase 2 (51 GPU-h + the 17,181-row control
re-gates + the stuck commit), then Phase 2 (51 GPU-h + the 17,181-row control
arm) ≈ +3 days. ~1.5–2 weeks total — and 22 of the 55 open miss-queue rows are
arm) ≈ +3 days. ~1.5–2 weeks total — and 22 of the 55 open miss-queue rows are
extraction-gated floors (verified), so "100%" is not possible without Phase 2.
extraction-gated floors (verified), so "100%" is not possible without Phase 2.
## Response B


**What is actually being solved.** Stripped of vocabulary, the campaign is not
**What is actually being solved.** Stripped of vocabulary, the campaign is not
"CSM comprehension" — the asset is a checkable 100%: the D1–D10 done-set, raw
"CSM comprehension" — the asset is a checkable 100%: the D1–D10 done-set, raw
receipts, zero unexplained failures. CSM is the first corpus run under that
receipts, zero unexplained failures. CSM is the first corpus run under that
definition — the authorized successor (todo #9) after JJK halted before P6.
definition — the authorized successor (todo #9) after JJK halted before P6.
But the audit's framing is stale: QUESTION.md/CLAUDE.md say "JJK D6 still
But the audit's framing is stale: QUESTION.md/CLAUDE.md say "JJK D6 still
open"; on disk GATE.md:687 + DONE_DECLARATION.md (09-07) declare it closed —
open"; on disk GATE.md:687 + DONE_DECLARATION.md (09-07) declare it closed —
"terminal state: done." So "can CSM close faster than JJK?" is the wrong
"terminal state: done." So "can CSM close faster than JJK?" is the wrong
question: CSM is not finishing JJK's open D-layer work — it *is* the P6
question: CSM is not finishing JJK's open D-layer work — it *is* the P6
cross-corpus successor. JJK's D6 campaign ran without the A/B bay, machine
cross-corpus successor. JJK's D6 campaign ran without the A/B bay, machine
monitor, or per-engine-change council trigger — you cannot beat a baseline
monitor, or per-engine-change council trigger — you cannot beat a baseline
that did not pay your verification cost.
that did not pay your verification cost.


**Is the decomposition right?** Two-phase + closure loop is the right shape:
**Is the decomposition right?** Two-phase + closure loop is the right shape:
Phase 1 fixes are cheap and shrink Phase 2's 51 GPU-h (council R4); the
Phase 1 fixes are cheap and shrink Phase 2's 51 GPU-h (council R4); the
frozen-miss-queue → one-class-at-a-time → re-sweep → halt machinery is right
frozen-miss-queue → one-class-at-a-time → re-sweep → halt machinery is right
for a finite miss set. The mis-shaped part is the process layer: (1) the
for a finite miss set. The mis-shaped part is the process layer: (1) the
council's own record prices per-engine-fix overhead at 2.5–5 h × up to 5
council's own record prices per-engine-fix overhead at 2.5–5 h × up to 5
fixes ≈ 12.5–25 h — "not the sweep… is unit-3's wall-clock driver"; (2) the
fixes ≈ 12.5–25 h — "not the sweep… is unit-3's wall-clock driver"; (2) the
"at every big engine change" trigger (09-09 rule) counseled a 22-line router
"at every big engine change" trigger (09-09 rule) counseled a 22-line router
rule (R-1, ledger #22) at full 11-member cost — 7 councils in 3 days, where
rule (R-1, ledger #22) at full 11-member cost — 7 councils in 3 days, where
JJK counseled at build/phase granularity; (3) the incidents are process
JJK counseled at build/phase granularity; (3) the incidents are process
fragility, not corpus: 60-min worker timeouts, the stale ESC voiding gate-3,
fragility, not corpus: 60-min worker timeouts, the stale ESC voiding gate-3,
/tmp loss on reboot.
/tmp loss on reboot.


**Carry / change.** Carry from JJK: checkable done-set, frozen pre-registered
**Carry / change.** Carry from JJK: checkable done-set, frozen pre-registered
sets, fix-root-cause-never-reword, raw receipts, per-wiki overrides — all
sets, fix-root-cause-never-reword, raw receipts, per-wiki overrides — all
active in CSM. Change: counsel on pre-registered fix *classes* (R-1..R-5),
active in CSM. Change: counsel on pre-registered fix *classes* (R-1..R-5),
not per hunk; re-anchor the goal: "close 21 reds + 30 queue rows + 51 GPU-h
not per hunk; re-anchor the goal: "close 21 reds + 30 queue rows + 51 GPU-h
in ~2 GPU-days without process overhead eating the wall-clock."
in ~2 GPU-days without process overhead eating the wall-clock."

## Response C



**1. This is a corpus factory; CSM only pays the setup cost.** The census
**1. This is a corpus factory; CSM only pays the setup cost.** The census
tools take `--series`, JJK byte-identical; frozen sets generated fresh from
tools take `--series`, JJK byte-identical; frozen sets generated fresh from
CSM (seeded, revid-stamped, on disk); the T0 pilot — 843 questions,
CSM (seeded, revid-stamped, on disk); the T0 pilot — 843 questions,
843/843 survival — runs through series-agnostic `page_gen.py`. Seven other
843/843 survival — runs through series-agnostic `page_gen.py`. Seven other
corpora are already crawled+indexed on disk (JJK, Bleach, OPM, Berserk,
corpora are already crawled+indexed on disk (JJK, Bleach, OPM, Berserk,
Dragon Ball, One Piece, Hunterpedia), so their Phase-1
Dragon Ball, One Piece, Hunterpedia), so their Phase-1
measurement shrinks to `overrides.yaml` + `census_doors --series X --regen` + a
measurement shrinks to `overrides.yaml` + `census_doors --series X --regen` + a
dimension-map rerun. Left per corpus: Phase-2 GPU-hours — and D6
dimension-map rerun. Left per corpus: Phase-2 GPU-hours — and D6
extraction only fires on a red census, so a green corpus skips it.
extraction only fires on a red census, so a green corpus skips it.
CSM is not corpus #2; it is the factory's amortization leg.
CSM is not corpus #2; it is the factory's amortization leg.


**2. R-5 is the campaign's biggest cross-corpus asset.** Verified
**2. R-5 is the campaign's biggest cross-corpus asset.** Verified
read-only against every `facts.db`: CSM's 11,261 edges are 96.7 %
read-only against every `facts.db`: CSM's 11,261 edges are 96.7 %
cross-document; typed `relations` tables total 23,656 rows across the
cross-document; typed `relations` tables total 23,656 rows across the
eight corpora (JJK 821 → One Piece 14,527; CSM 748) over 1.05 M raw
eight corpora (JJK 821 → One Piece 14,527; CSM 748) over 1.05 M raw
`edges`. The router today has three modes; R-5's fourth, series-agnostic
`edges`. The router today has three modes; R-5's fourth, series-agnostic
`relations` mode (counseled) pays off in all eight — every future corpus
`relations` mode (counseled) pays off in all eight — every future corpus
inherits it for free.
inherits it for free.


**3. Two ops assets nobody is counting.** (a) Transcript import:
**3. Two ops assets nobody is counting.** (a) Transcript import:
`transcripts.db`'s 16,226 lines (verified) became 16,226 embedded points;
`transcripts.db`'s 16,226 lines (verified) became 16,226 embedded points;
the Toji script shipped 21 verbatim `[E n mm:ss]` citations — the
the Toji script shipped 21 verbatim `[E n mm:ss]` citations — the
strongest writer-facing differentiator (verbatim, timestamped grounding),
strongest writer-facing differentiator (verbatim, timestamped grounding),
repeatable for any corpus with subtitles. (b) A/B bay + `csm-control.sh`
repeatable for any corpus with subtitles. (b) A/B bay + `csm-control.sh`
monitor (tmux-aware, logdir arg) + `ab-bay`/`terminal-pilot` skills: a
monitor (tmux-aware, logdir arg) + `ab-bay`/`terminal-pilot` skills: a
reusable supervision pattern — footprint invariants,
reusable supervision pattern — footprint invariants,
auto-kill of CPU work, the jsonl as judge.
auto-kill of CPU work, the jsonl as judge.


**4. What CSM 100 % unlocks.** JJK's D6 is still open (P0–P5): CSM-8 will
**4. What CSM 100 % unlocks.** JJK's D6 is still open (P0–P5): CSM-8 will
be the *first* full D6 done-declaration, and its pilot memo becomes the
be the *first* full D6 done-declaration, and its pilot memo becomes the
reusable acceptance template for everything after. A second,
reusable acceptance template for everything after. A second,
different-genre corpus at D6 proves "nothing is hardcoded" — that is the
different-genre corpus at D6 proves "nothing is hardcoded" — that is the
product claim; today it is a single data point.
product claim; today it is a single data point.


*Verification: tools/census_*.py `--series` flags (grep), reports/csm/
*Verification: tools/census_*.py `--series` flags (grep), reports/csm/
census_*_csm.json + t0_pilot_csm.json (843 items) on disk,
census_*_csm.json + t0_pilot_csm.json (843 items) on disk,
series/<8>/facts.db read-only queries (relations: 821/748/359/617/651/5542/
series/<8>/facts.db read-only queries (relations: 821/748/359/617/651/5542/
14527/391; edges: 35,026/11,261/43,077/130,670/18,418/312,598/440,245/
14527/391; edges: 35,026/11,261/43,077/130,670/18,418/312,598/440,245/
62,066), series/jjk/transcripts.db line count = 16,226,
62,066), series/jjk/transcripts.db line count = 16,226,
tools/master-work/csm-control.sh header (tmux/logdir),
tools/master-work/csm-control.sh header (tmux/logdir),
~/.pi/agent/skills/{ab-bay,terminal-pilot}, router.py (no `relations`
~/.pi/agent/skills/{ab-bay,terminal-pilot}, router.py (no `relations`
mode yet), crosspage_census_csm.md (10,889/11,261 = 96.7 %).*
mode yet), crosspage_census_csm.md (10,889/11,261 = 96.7 %).*
## Response D

The campaign reads as a machine supervising a machine. Two LLM sessions sit in tmux: "A" watches "B" run shells through a 5-second-poll script that auto-kills "provably-CPU model work >15 s", types hints into B's terminal, then file-probes to confirm the typing landed. Two LLMs share ownership of one :8000 process, and the log records an incident where A killed a pid B still needed — a stale pid that had to be "re-verified against live state". Why do you need an LLM supervisor, plus a poll script, plus typed hints, plus a file probe, when a CI pipeline handles the same in an hour?
The campaign reads as a machine supervising a machine. Two LLM sessions sit in tmux: "A" watches "B" run shells through a 5-second-poll script that auto-kills "provably-CPU model work >15 s", types hints into B's terminal, then file-probes to confirm the typing landed. Two LLMs share ownership of one :8000 process, and the log records an incident where A killed a pid B still needed — a stale pid that had to be "re-verified against live state". Why do you need an LLM supervisor, plus a poll script, plus typed hints, plus a file probe, when a CI pipeline handles the same in an hour?


"JJK-100% invariant" is a slogan, not a number: the pinned gates include a 97.5% live probe (390/400) and a 79.0% canon score, and one of those gates is for One-Punch Man, a third series the invariant's name never mentions. What CSM actually holds is "baseline-exact" — equality with the 2026-09-08 numbers. The name contradicts the numbers it pins, and a new engineer cannot tell which is the contract.
"JJK-100% invariant" is a slogan, not a number: the pinned gates include a 97.5% live probe (390/400) and a 79.0% canon score, and one of those gates is for One-Punch Man, a third series the invariant's name never mentions. What CSM actually holds is "baseline-exact" — equality with the 2026-09-08 numbers. The name contradicts the numbers it pins, and a new engineer cannot tell which is the contract.


The docs contradict themselves on disk. CLAUDE.md's "Now active: JJK D6-comprehension completion" line is stale: `reports/comprehension/DONE_DECLARATION.md` (09-07) declares JJK D6 done — verified on disk. CSM_WAVE2_RESUME §1's table says CSM-3 landed in `bc73795`; git shows `bc73795` is the CSM-3b commit and CSM-3 is `f93d396` (the audit's own key facts agree with git, not the resume plan). CSM_2PHASE_PLAN still carries the "every 2–3 todos" council cadence that WAVE2_RESUME §3 explicitly retired — the older plan was never updated, so a first-time reader gets two rules.
The docs contradict themselves on disk. CLAUDE.md's "Now active: JJK D6-comprehension completion" line is stale: `reports/comprehension/DONE_DECLARATION.md` (09-07) declares JJK D6 done — verified on disk. CSM_WAVE2_RESUME §1's table says CSM-3 landed in `bc73795`; git shows `bc73795` is the CSM-3b commit and CSM-3 is `f93d396` (the audit's own key facts agree with git, not the resume plan). CSM_2PHASE_PLAN still carries the "every 2–3 todos" council cadence that WAVE2_RESUME §3 explicitly retired — the older plan was never updated, so a first-time reader gets two rules.


Finally the ritual weight: seven 11-member LLM councils (~2 h each, fresh context, "one agent at a time") for a campaign 3 days in, running beside four deterministic gates. A new engineer will ask: if the gates catch most defects, what is the eleven-LLM committee for, and when is it worth less than its cost? Nothing in these documents answers that.
Finally the ritual weight: seven 11-member LLM councils (~2 h each, fresh context, "one agent at a time") for a campaign 3 days in, running beside four deterministic gates. A new engineer will ask: if the gates catch most defects, what is the eleven-LLM committee for, and when is it worth less than its cost? Nothing in these documents answers that.
## Response E

First move: grade the CUDA gate legs, commit the staged R-2/R-3 package. The 400-probe window died mid-run on the owner-override switch to CUDA (ledger 4,315); the reboot lost the /tmp manifest; but all 9 package files (3 engine, 1 override, 3 test, 2 records) are on disk, names in work_log item 1. Seed-7 400-probe on the now-CUDA :8000 (expect ≥390/400), gate-4 canon (236/236, 79.0%), R-2 Part A panel (pre-built), R-3 re-sweep (Part B green). ~1h, zero added GPU-h. Commit now: the reboot proved uncommitted state is fragile, and every later change re-runs the shared gates on it.
First move: grade the CUDA gate legs, commit the staged R-2/R-3 package. The 400-probe window died mid-run on the owner-override switch to CUDA (ledger 4,315); the reboot lost the /tmp manifest; but all 9 package files (3 engine, 1 override, 3 test, 2 records) are on disk, names in work_log item 1. Seed-7 400-probe on the now-CUDA :8000 (expect ≥390/400), gate-4 canon (236/236, 79.0%), R-2 Part A panel (pre-built), R-3 re-sweep (Part B green). ~1h, zero added GPU-h. Commit now: the reboot proved uncommitted state is fragile, and every later change re-runs the shared gates on it.


(2) R-5 relations mode: 90-min fresh-context draft (60-min timeout killed both wave-2 workers at verification; use 90 or split), B grades, §3 council (~2h), four gates, re-sweep, commit — ~1 wall-day. (3) R-6 (3 display aliases) + R-7 (61-key identity map) as no-council per-wiki levers per unit-3 R7, folded into the R-5 wave. Halt on miss-queue convergence (58 rows; 30 fixable after R-1). (4) Unit-4 close: one-copy four gates + pre-registered 5.4 re-adjudication + extraction-pass test + coverage + PHASE_A_COMPLETE: ~2h. Then one 100k switch; Phase 2: CSM-4's 51 GPU-h (≈2 GPU days), D6 extraction only on the 21-red census class, CSM-8. Phase 1 ≈ 3 days vs JJK's 5 for ~2× the pages; critical path is the 51 GPU-h.
(2) R-5 relations mode: 90-min fresh-context draft (60-min timeout killed both wave-2 workers at verification; use 90 or split), B grades, §3 council (~2h), four gates, re-sweep, commit — ~1 wall-day. (3) R-6 (3 display aliases) + R-7 (61-key identity map) as no-council per-wiki levers per unit-3 R7, folded into the R-5 wave. Halt on miss-queue convergence (58 rows; 30 fixable after R-1). (4) Unit-4 close: one-copy four gates + pre-registered 5.4 re-adjudication + extraction-pass test + coverage + PHASE_A_COMPLETE: ~2h. Then one 100k switch; Phase 2: CSM-4's 51 GPU-h (≈2 GPU days), D6 extraction only on the 21-red census class, CSM-8. Phase 1 ≈ 3 days vs JJK's 5 for ~2× the pages; critical path is the 51 GPU-h.


Mechanisms: KEEP the A/B bay + monitor — it caught the stale-ESC collision and the CUDA misstart; patch its two known gaps before Phase 2 (blind to CPU :8000 children; ESCs re-verify live pids). SHRINK council to R-5 + phase-close (7 so far at 1.5–2h); pre-registration already turns close-steps into a checklist — don't re-council pre-registered items. SHRINK 2-parallel to parallel drafting + one shared verification pass (B did it cheaper this time; the one-copy rule forbids parallel gate legs).
Mechanisms: KEEP the A/B bay + monitor — it caught the stale-ESC collision and the CUDA misstart; patch its two known gaps before Phase 2 (blind to CPU :8000 children; ESCs re-verify live pids). SHRINK council to R-5 + phase-close (7 so far at 1.5–2h); pre-registration already turns close-steps into a checklist — don't re-council pre-registered items. SHRINK 2-parallel to parallel drafting + one shared verification pass (B did it cheaper this time; the one-copy rule forbids parallel gate legs).