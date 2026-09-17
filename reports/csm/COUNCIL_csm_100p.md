# Council #34 — CSM 100% Phase-1 closure path (2026-09-17)

Council #34 of the CSM 100% campaign. Sequential, one agent at a time
(owner rule 2026-09-08, supersedes the parallel convention): 5 advisors →
5 reviewers (blind to each other's positions) → chairman, each in a fresh
context, no shared transcript. This file is the complete on-disk record
(positions, critiques, ruling) — no separate digest receipts; the raw
per-agent outputs live in the opencode session transcripts of the day.

**De-anonymization (fixed at deployment):** A = Executor, B =
First-Principles, C = Outsider, D = Contrarian, E = Expansive;
R1 = Rigor, R2 = Practicality, R3 = Risk, R4 = Voice/Clarity,
R5 = Stakeholder.

## Framed question

What is the correct, minimal closure path for CSM (Chainsaw Man) 100% in
Phase 1, and what stays for Phase 2?

- **(i)** Declare Phase 1 done NOW: formally re-assert P2.5 (produce the
  missing (d)#3/#4 numbers, re-assert (e) at pin 1,331 with D36 receipts),
  keep the markers as written, unlock P6 — treating the 134 set/relation
  residual pages + 22 floor rows as documented floor (Phase-2 territory).
- **(ii)** Do more Phase-1 work first: attempt to fix the 134-page
  set/relation residual (a second sweep, a new fix-class beyond R-1…R-8)
  before closure.
- **(iii)** Something else: fresh re-sweep to re-verify the floor, chasing
  the 42 NEW dim reds, or a narrower/looser "100%" definition.

## Trigger

- CSM Phase 1 reached its documented floor: all seven R-classes closed,
  four standing gates green, the queue at the 35-row halt residual.
- Two documents on disk set the terms: `reports/csm/csm100_inventory.md`
  (the residual inventory) and `reports/csm/p25_done_audit.md` (the P2.5
  done-audit, 7/8 PASS with (d) PENDING).
- The open question the owner put to the council: is "declare now"
  correct, or does Phase 1 owe more work, or does "100%" itself need
  re-definition?

## Inputs verified on disk (fact base, 2026-09-17)

- Four standing gates green: pytest pin **1,331** (1,329 passed + 2 xpassed);
  eval jjk **31/31**; span-recall jjk offline **48,572/48,572** rc=0 +
  live probe **398/400**; canon-run opm **236/236** (10/16 exact, 79.0%).
- CSM coverage **473/537 (88.1%)**; in-scope content remainder 0; 64 pages
  out-of-scope by design (council #32 P-6 re-scope).
- Page-run D36 model window (`reports/csm/receipts/model_window_d36/`):
  475 batches, **339 rc=0 / 136 rc=2** (134 in-scope pages + 2 sweep
  artifacts), **424 failing questions, all of the "all X of Y"
  set/relation shape** (16 of them empty-answer). Council #33 ruled the
  class "not a router lever; R-9 absorbed, no-fire"
  (`reports/csm/p23_red_triage.md` @`3d43a21`: 37 box-class wrong-page
  ranking + 27 width/enumeration + 5 state-over-time).
- **22 extraction-gated floor rows** (21 `csm-dim-*` 1:1 with the census
  reds + `csm-char-04` Makima abilities R-7x); halt residual 35 =
  22 floor + 10 by-design + 3 stamps.
- p23 widened bank: **417/486 MECH_GREEN** (85.8%); 69 reds = 21 floor
  + **42 NEW dim reds** (post-freeze: story_arcs_box, chapter_box,
  episode, volume_box, organization) + 6 ability-pool. Bar-audit:
  qa 11/26 + auto 16/26 (2026-09-17).
- P2.5 done-audit (`reports/csm/p25_done_audit.md`): 7/8 PASS;
  **(d) PENDING** — pilot #3 (new numbered gaps) + #4 (human round-trips)
  not on disk.
- Phase markers on disk: PHASE_A_COMPLETE @`407c016`, PHASE_B_COMPLETE
  @`2419a01`. Rule A20: a marker is valid at the documented floor; a
  regression (not the floor) voids it.
- JJK remains 100% and baseline-exact (the reference no CSM change may
  regress); P6 (cross-corpus, `plan/Plan_to_perfection.md` §7) is locked
  behind Phase-1 closure.

## The five positions

**[A] Executor.** "Pick (i). Closure is a four-step procedure: (1) floor
re-verify — diff the frozen miss queue against the documented floor
(35 = 22+10+3); a regression voids both markers per A20 and stops the
declaration; exit: diff = 0 new rows, offline ~15 min. (2) Produce
(d)#3/#4 from disk, not memory ('0 filed' is a legitimate value); append
the named 'four pilot numbers' block to GATE.md; exit: audit 8/8 PASS,
numbers reproducible. ~1–2 h. (3) Re-assert (e) at pin 1,331 citing the
R-8 window + D36 receipts; the plan's 1,305 is stale by the known +10
(Ruling 5e); leave both markers as written. ~15 min. (4) Drift-log entry
+ GATE.md update + switchpoint commit; P6 unlocks at that commit.
Wall-clock: half a day, one executor; no engine change → no gate re-run
owed; a 1-second offline span-recall liveness check suffices. Refusals:
no second sweep of the 134-page residual (council #33 already ruled that
class); no chasing the 42 new dim reds now — document them as Phase-2
targets in the closure entry. Phase-2 D6 owns: the 22 floor rows, the 134
set/relation pages (424 questions incl. 16 empty-answer), and the 42 new
dim + 6 ability-pool reds."

**[B] First-Principles.** "Strip the paper. The unit of value isn't a
number or a marker — it's: the writer can pull cited, complete context for
any in-scope CSM question, AND the engine can prove the open set is fully
classified. A '100%' resting on a 22-row floor while 134 residual pages +
42 new dim reds + 6 ability-pool reds sit untriaged is not a floor; it's
an open set you stopped enumerating. The right question isn't 'declare
done or do more work' — it's 'is the floor complete?' You already drew
the sound line: extraction-gated (needs D6) vs engine-fixable (Phase 1).
The 22-row floor is the named extraction-gated set. But council #33
itself classed the 134 residual as 'box-ranking / width /
state-over-time, not a router lever' — the SAME class, never folded into
the floor; the 42 new dim reds are the same shapes, landed after the
floor froze. The floor is under-scoped by construction. Minimal closure
path: (1) triage the full open population (134 + 42 + 6) row-by-row:
extraction-gated (fold into floor, 22 → N) or engine-fixable. Cheap —
classifying data already on disk. (2) Engine-fixable set empty →
re-assert P2.5, declare Phase 1 done, unlock P6; non-empty → that set IS
the Phase-1 work, do it, return to step 1. (3) Phase 2 = the COMPLETE
extraction-gated floor via D6 — bigger than the 22 currently on disk.
P2.5 re-assertion evidence: (d)#3/#4 as two on-disk numbers; (e) at pin
1,331 with D36 receipts (drop 1,305); and the completed floor triage.
Without the last, the declaration is paper."

**[C] Outsider.** "You're calling a system '100% complete' while 424
known-failing questions are parked as 'documented floor.' In my industry
that's not 100%. That's 88% with an apology attached. The 424
set/relation failures are not 17 separate problems; they're one failure
mode: the engine retrieves single candidates and cannot enumerate sets.
Council #33 ruling this 'not a router lever, R-9 absorbed, no-fire' is a
scope cut dressed as a technical ruling. Demand five of those 424 traced
through the retrieval layer, one-line root cause each: data-sparse,
design-limited, or extraction-fixable. 'Extraction-gated' is a deferral
with a label, not a root-cause analysis. The floor has moved and no one
has said so: the p23 bank found 42 NEW dim reds not in the v1 floor
triage; the 22-row floor was triaged against the v1 bank — you cannot
declare the floor stable while 42 new reds are untriaged. Triage them:
extraction-gated or Phase-1 fixable? The answer changes the closure
path. P2.5 has a PENDING item: two numbers not on disk. You cannot
'formally re-assert' a declaration with a missing deliverable;
re-asserting with a PENDING is fabricating the declaration. The four
standing gates test JJK, not CSM's failures — green lights that don't
test the thing actually failing are theater. Demands before any
declaration: (1) rename the metric to '88% with a 12% documented scope
cut'; (2) a one-page failure-mode analysis of the 424, root cause per
sub-mode, not a council vote; (3) the 42 new reds triaged; (4) the two
missing P2.5 numbers on disk. If the set/relation class is a
retrieval-layer design limitation, the 424 will still be red and you'll
be back in front of this council in six weeks."

**[D] Contrarian.** "The plan redefines '100%' down to a weaker metric.
'In-scope content remainder 0' is content coverage — every line in a
chunk. The page-run sweep is the stricter test and it's failing: 134
in-scope pages, 424 failing set/relation questions. Option (i) calls
that 'documented floor.' But the documented floor is 35 rows (22
extraction-gated + 10 by-design + 3 stamps); 424 questions / 134 pages
is not 35 rows — a non-pre-registered residual laundered as 'floor.'
Worse, that residual has no closer: the 22 floor rows name Phase 2 D6
extraction; the 134-page residual is ruled 'not a router lever' and
isn't extraction-gated (only 5 of 22 are state-over-time). Neither
phase closes it — orphaned — and the p23 bank just added 42 NEW dim reds
not in the floor. 'Known class, no lever owed' = 'we stopped and called
it a floor.' What fails first: the '100%' claim — 134 in-scope pages
carry 424 known-failing relational questions with no owning phase.
Sequencing trap: (d)#3 (new numbered gaps) isn't on disk; if it's high,
the floor is moving and A20's 'queue at documented floor' isn't met —
'declare now' is premature. The inventory flags its own numbers
UNVERIFIED (474 vs 475; qa-mode 15 reds, not 10). What the council
waves through: (i) — 'markers on disk, gates green, 7/8 PASS' reads as
done. What it shouldn't: the orphaned residual, the 42 new dim reds, the
missing (d) numbers. Cover now: (d)#3/#4 on disk (if #3 rising, don't
stamp); resolve UNVERIFIED discrepancies; declare Phase 1 done only on
the pre-registered scope; name an owner + closer for the residual.
Defer to Phase 2: the 22 floor rows + 200-row held-out. Keep P6 locked
until the residual has an owner."

**[E] Expansive.** "Take (i) — declare Phase 1 done NOW — and use the
closure to arm P6, where the real leverage is. Why (ii) is a trap: the
134-page residual is ruled a known class and the queue sits at its
documented floor — the A20 marker's precondition. A second sweep or new
fix-class is un-pre-registered work against a closed gate, a regression
risk to JJK's baseline. (iii)'s re-sweep is the same: D36 already ran at
this tree with all four gates green; nothing new justifies re-execution.
Unlocks: (1) The floor-triage method IS the P6 template —
census_v1_floor_triage.jsonl (ROUTING/CONTENT/PARTIAL × recovered_by
lever) is what every P6 corpus needs to split 'fix now' from 'defer to
extraction'; closing CSM without naming it cross-corpus makes seven
wikis re-derive it. File one §7 section: P6 adopts the CSM v1 schema,
grader, and 200-row held-out. (2) The D6 extraction-leg test design
locks now, while receipts are fresh — the null-branch design (486-item
bank, 5.4 re-adjudication, '21/21 reds identical') is a pre-registered
extraction-pass test that every P6 corpus will need (Berserk's
0%-sourced case is extraction-gated in the same shape); locking it now
is hours of writing, at P6 it's a campaign. (3) JJK stays the finished
reference; CSM the second anchor P6 needs. Cover now: the four-step
re-assertion — produce (d)#3/#4 ('0 filed' is a legitimate value),
re-assert (e) at pin 1,331 with D36 receipts, keep both markers — plus
tag the 16 empty-answer pages and 42 new dim reds as D6 triage inputs,
and file the P6 addendum. Defer to D6: the 22 floor rows, 42 new reds,
6 ability-pool reds, 16 empty-answer pages."

## The five critiques

**R1 (Rigor).** [A] is the weakest position: it folds the 134 residual
into "documented floor" but the fact base defines the floor as the
35-row pre-registered set and the 134 are not in it; council #33's
"no router lever" establishes no Phase-1 lever, NOT that D6 closes the
134 — [A]'s "D6 owns" is unsupported; step 1's diff runs against 35 and
never folds in the 42 post-freeze reds, so "floor stable" may be false
(22 → N); [E] shares the gap; both A and E cite "16 empty-answer pages"
that the reviewer's fact base did not settle. Fact contradiction to
resolve: does #33's "no-fire" close AND own the class? [A]/[E] read
class-closed + Phase-2-owned; [B]/[C]/[D] read "no Phase-1 lever" with
the residual untriaged/orphaned. Also: 22 floor rows vs 21 p23 floor
reds (reconcile); [D]'s UNVERIFIED flags (474 vs 475; qa-mode 15 vs 10)
contradict the settled 35. The synthesis must state: no unqualified
"100%"; 134+42+6 are floor-or-open only after row-level triage; P2.5
cannot be re-asserted while (d)#3/#4 pending; no floor count until
22/21 reconciles; "16 empty-answer" unclaimable without an on-disk
receipt; the standing gates do not test CSM's failures.

**R2 (Practicality).** [A] is the only executable position (steps, exit
criteria, durations, named refusals). First thing that breaks: step 1's
diff runs against the FROZEN queue, so the 42 post-freeze reds never
surface — diff=0 passes trivially and the marker stamps over the
orphan. Cuts to make it shippable: (a) replace "document 42 as Phase-2
targets" with a 48-row triage table (42+6, on-disk classification,
~1 h); (b) collapse [E]'s P6 §7 addendum to one drift-log pointer
(filed within a week); (c) [B]'s full 182-row sweep is overkill — the
134 keep their #33 class, triage only the 48 fresh. Mandated artifact:
the **open-set register** — a JSONL + one-pager committed at the
switchpoint listing every open row (134+42+6+22+10+3+16) with class,
root cause, owning phase, named closer, re-test trigger. A20 stamps
against the register, not the number 35. In six weeks the floor is a
diff against the register, not an argument.

**R3 (Risk).** Worst option = (iii) redefine: CSM/JJK lose the shared
bar, P6 loses its measurement foundation, and the drift is silent and
unrecoverable. Worst position = [E]: a wrong call propagates the
under-scoped floor-triage method to 7 wikis and pre-locks a stale
design (×7 multiplier, hard to roll back). Cheapest insurance: extend
`census_v1_floor_triage.jsonl`'s schema to the FULL open population
(134+42+6+16), each row tagged extraction_gated + lever from on-disk
D36/p23 receipts (offline); GATE: no marker stamp, no P6 addendum, no
D6 design lock until that artifact is on disk; if the engine_fixable
count comes back > 0, the declaration reverts to doing that set first.

**R4 (Voice/Clarity).** [A] is what the owner can act on — the only work
order. Graft on [D]'s "name an owner + closer for the 134-residual."
[C] contains the claim that would sink the verdict with the owner:
"the four standing gates test JJK, not CSM's failures — green lights
that don't test the thing actually failing are theater" (the gates are,
by documented design, JJK no-regression guards; "88% with an apology
attached" attacks the owner's own defined metric). The verdict should
LEAD with the definitional sentence: "'100%' in this project means
every in-scope CSM line is chunk-reachable, the four standing gates are
green, and every open red is triaged into a named, owned bucket
(extraction-gated → Phase-2 D6 / by-design / documented-floor no-lever)
and frozen at a commit — a classification claim, not a zero-reds
claim."

**R5 (Stakeholder).** [B] best serves the consumer — only it closes the
floor as a complete enumeration; [A]/[E] optimize the project's
self-image ("100%" with a 134-page residual neither phase owns, plus 42
untriaged reds); [D] is right the residual is orphaned but holds P6 for
no benefit to the queue. Honest writer-facing statement: narrative/
character/fight context is complete, cited, usable today; set/relation
enumeration ("all X of Y") has 424 known failures with no closer until
D6 — cross-check those against the wiki manually; 22 extraction-gated
facts stay missing until Phase 2. Early P6 unlock serves the 7 queued
wiks ONLY with [B]'s completed triage as the P6 schema — each corpus
inherits a closed floor rather than CSM's under-scoped one; unlock
without that artifact and the queue inherits the same hole.

## The chairman's ruling

**VERDICT.** Option (i), conditional: the close stamps only after the
mandated open-set register is on disk; P2.5 re-asserts only after
(d)#3/#4 land. [B]'s triage is the condition, [A]'s sequence the
vehicle. Owner's lead sentence: "'100%' here means every in-scope CSM
line is chunk-reachable, the four standing gates are green, and every
open red is triaged into a named, owned bucket (extraction-gated →
Phase-2 D6 / by-design / documented-floor-no-lever) and frozen at a
commit — a classification claim, not a zero-reds claim."

**RULINGS.**

1. **Closure = [A]'s steps corrected:** (d)#3/#4 on disk; 22/21
   reconciliation; register committed; (e) re-asserted at pin 1,331;
   drift-log + GATE.md + switchpoint.
2. **Register (mandated, R2/R3):** extend
   `census_v1_floor_triage.jsonl` to the full open population
   (134+42+6+16+22+10+3); each row carries class, root cause, owning
   phase, named closer, re-test trigger. The 134 keep their #33 class;
   the 48 (42+6) triage fresh from on-disk D36/p23 receipts; the 16
   empty-answer rows carry a receipt or are struck. Gate: no marker
   stamp, P6 addendum, or D6 lock until the register is on disk; A20
   stamps against the register diff, not 35.
3. **No-fire scope:** #33 establishes the set/relation class is NOT a
   Phase-1 router lever. It does NOT establish that D6 closes them, nor
   that the 134 are the pre-registered floor — so the 134 are register
   rows with a named owning phase, not auto-floor; the floor count is a
   reconciled N, not 22 or 35, until 22/21 lands.
4. **P6 unlocks at the closure commit**, scoped to the §7 method
   addendum (Census v1 schema + grader + 200-row held-out, one
   drift-log pointer, ≤1 week), conditioned on the register proving the
   schema complete on CSM. The D6 design lock and 7-wiki rollout are
   refused now (R3's ×7 risk); they return post-register.
5. **Writer-facing (GATE.md):** narrative/character/fight context is
   complete, cited, usable today; set/relation ("all X of Y") has 424
   known failures with no closer until D6 — cross-check those against
   the wiki; 22 extraction-gated facts stay missing until Phase 2.

**REFUSED.**

1. (ii) second sweep of the 134: un-pre-registered, closed gate, #33
   no-lever, JJK regression risk.
2. (iii) redefine "100%" / chase the 42 reds: destroys the JJK/CSM
   shared bar and the P6 measurement foundation.
3. [C]'s rename + "theater" framing: the standing gates are JJK
   no-regression guards by documented design, not CSM quality bars.
4. [B]'s 182-row re-triage: the 134 keep their #33 class; only the 48
   need fresh triage.
5. [D]'s P6 lock: the register is the gate; an indefinite lock benefits
   no queued wiki.
6. [E]'s D6 lock + 7-wiki addendum now: R3's under-scoped ×7 risk;
   deferred past the register.

**CLOSURE SEQUENCE** (one executor):

1. (d)#3/#4 on disk + four-pilot-numbers block in GATE.md (1–2 h).
   **Hard gate: if #3 is non-zero → floor is moving, A20 precondition
   fails; halt, no marker, council reconvenes with the new count.**
2. 22/21 reconciliation, one-line diff in the register (30 min).
3. Register on disk: JSONL + one-pager, 48 rows triaged offline from
   receipts (1 h); commit.
4. Re-assert (e) at pin 1,331 (15 min).
5. Drift-log + GATE.md + switchpoint commit; A20 stamps against the
   register diff (15 min); P6 addendum pointer filed ≤1 week.

**RECORD** (so no one re-argues this in six weeks):

- This ruling + de-anonymized positions (this file).
- Register JSONL + one-pager + commit hash (the six-week floor diff).
- (d)#3/#4 receipts + pilot-numbers block.
- #33 scope statement (does/does-not-establish); 22/21 line; A20
  stamp rule (register diff, regression voids).
- Writer-facing statement (GATE.md); standing-gates scope note; P6
  unlock condition.