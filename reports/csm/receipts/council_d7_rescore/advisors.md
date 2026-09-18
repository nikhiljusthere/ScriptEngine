# COUNCIL RECORD — D7 re-score council (CSM Phase 1, §9a closure loop)

**Members:** 5 advisors (A–E) + 5 peer reviewers (R1–R5) + 1 chairman.
**Method (owner rule 2026-09-08):** strictly sequential — one subagent at a
time, each fresh-context, GPU-free, read-only. Advisors A–E deployed in
order; then R1–R5 each reviewed all five advisor responses; then the
chairman ruled on the record.

**Letter↔session map (advisors):**
| Letter | Role | opencode task session |
|---|---|---|
| A | Executor | `ses_f4bbd8163ffeHmvdZKBbQIjB36` |
| B | Outsider | `ses_f4bbea15dffesrMlf57HY8Atvv` |
| C | First-Principles | `ses_f4bc102f7ffeJeedDvB9KxCm16` |
| D | Contrarian | `ses_f4bc2b8faffevR6VRVfwJT06yG` |
| E | Expansionist | `ses_f4bbf8b4cffeF3L99xQw6upI28` |

**Letter↔session map (reviewers):** see `reviews.md`. **Chairman:**
`ses_f4bb05537ffeYp79GIRq7R63az` (verdict in `chairman.md`).

Framed question + evidence pack: `framed_question.md`.

> Fidelity note: all member responses below were restored verbatim from the
> opencode.db session transcripts (final assistant message of each task
> session); opencode transport markers (`[step-start]`/`[step-finish]`)
> stripped, no words changed.

---

## ADVISOR A — Executor

Monday morning, in order. Legs first, all sequential, one subagent at a time.

**Q1: legs first, spike after.** The legs are bounded: TIERED is already measured (473, 0 counter-flips), ABILWIDTH is exactly two rows. The spike has no first step — "focus-resolution" is a code-reading morning with no committable artifact. Bank the green first: legs landing means a committed 473+ tree, so the spike starts from a green baseline. If a leg goes red, its root cause sits next to the spike's class and you'll be reading that code anyway.

**Q2: grade ABILWIDTH unflagged.** The gates are the safety device — JJK eval 31/31 re-runs at closure and catches any regression. A flag adds test surface for zero extra safety. If the JJK gate goes red, flag it then.

**Q3: (b).** Same session downtime as (a), but one manual op instead of two, and no stale state record: stop Qwen → `nvidia-smi` confirms free → grade → relaunch 135k from the captured argv → health check. (a) leaves a stale state record plus a second manual restore — two places to get it wrong. CPU is already off the table.

**Q4: one task = "grade the two legs, singly, in this order; stop at the first red."**

1. Snapshot p23 grade files + D6_OOS_PRE.jsonl to /tmp.
2. Stop Qwen, confirm 32 GB free.
3. Leg A: revert the ABILWIDTH hunk; pre-register (473; arcn-02/10, org-03, state-08; 0 counter-flips); `SCRIPTENGINE_TIERED_RECALL=1 CENSUS_DEVICE=cuda …/p23_grader.py` → `blind_score.py` (19/19) → `d6_flip.py`.
4. Leg B: restore ABILWIDTH, TIERED off; pre-register (pool-140/358 green, 0 counter-flips); same three commands.
5. Leg C: combined tree, same three.
6. Only if all green: the four standing gates (pytest overlaps the first GPU gate — the only safe parallel).
7. Relaunch 135k, health check.

Stop conditions: first red grade → halt, no retuning (D59); OOM → halt; no commit without owner word. Spike is the next task, after the legs close.

---

## ADVISOR B — Outsider

Fresh-eyes pass.

**Confusing to a new reader:** (1) OOS200 is 190 by one instrument, 194 by another, and the pass bar is "not below floor" — two meters, a four-row gap, no named authority. Declare which instrument owns the floor before any grading. (2) The briefing contradicts itself: "four gates after EVERY engine change" vs "full re-run at each fix-class closure" (Ruling 5e). A fresh reader cannot tell whether committing TIERED triggers the gates. (3) GATE's "spike first" line is stale — it predates D59, where TIERED already flipped org-03, one of the seven D7 holdouts. A red probe on arcb-05, which is not in the seven (a fragile green or a Phase-2 floor row), is no reason to hold a green, pre-registered, fully measured change.

**Q1:** TIERED first. It is done: predicted, measured (473, 0 counter-flips, blind 19/19, eval 31/31), gates passed. Commit it, then ABILWIDTH, then the spike — and only if arcb-05 is actually Phase-1 scope.

**Q2:** Flag it. An unflagged, unconditional, unmeasured engine change has no off-switch, and it silently re-tunes retrieval for every future wiki. `SCRIPTENGINE_ABILWIDTH` default off, like TIERED. The JJK no-op claim ("no abilities table → no change") must ride the gates, not be asserted.

**Q3:** (b). The council ends before the subagent runs, so the "switch kills the session" risk is moot. (a) leaves a stale 100k profile plus a second manual switch; (c) is forbidden. One window: stop Qwen → pytest + gates + p23 (flag on) + blind + d6_flip on CUDA → restore 135k from the captured argv.

**Q4:** One task: pre-register ABILWIDTH predictions (pool-140/358 green, 0 counter-flips) → implement behind the flag → p23 + blind + d6_flip in one Qwen-stop window → commit flag default off if all green. Stop condition: any counter-flip or OOS200 floor regression → leave uncommitted, report, no ex-post retuning. The spike is a separate, not-yet-authorized task.

---

## ADVISOR C — First-Principles

Q1/Q3 assume the next fact to buy is a grade. It may already be on disk: D59's flag-ON receipts exist, and ABILWIDTH is unconditional — presence in that tree = active. If D59's tree contained ABILWIDTH, pool-140/358 absent from its +4 greens means it already measured red on its targets. Read the receipts first.

Q1: legs first, but not for GATE.md's reason. "Spike, then D7 leg" orders the spike ahead of the D7 leg proper; the uncommitted legs are not that leg — they are the last measurement of already-registered fix classes. The spike targets the arcb-05 class, which is not among the 7 D7 rows. Diagnose the 4 undiagnosed reds (chap-01, org-05/06, vol-10) by reading their retrieval traces before spiking: cheaper, and it tells you whether the spike is even on the critical path.

Q2: grade as-is. Pre-registered, generic (per-wiki table, no hardcoded names); red → git revert. A flag adds a permanent state every future grader must choose; TIERED already pays that cost. In a campaign the gates are the rollout.

Q3: (b). Owner stops Qwen, grade on CUDA, manually relaunch 135k from the captured argv. The 100k switch has a stale state record and strands the tree on a profile the owner didn't choose — two manual flips instead of one. The flip is an owner operation at the approval boundary (checkpoint first); the agent grades only. CPU is out under the 15-minute rule.

Q4: one task: (1) read the D59 receipts — if ABILWIDTH was in that tree, discard it, no GPU; (2) else pre-register (pool-140/358 green, 0 counter-flips, blind 19/19) and snapshot grade files; (3) owner flips GPU; (4) run p23 + blind + d6_flip on the TIERED-OFF tree. Pass: W ≥ 471, pool-140/358 green, 0 counter-flips, gates green → commit on owner's word. Stop: targets red → revert ABILWIDTH, re-scope to the remaining D7 rows, no spike yet.

---

## ADVISOR D — Contrarian

Q3 is the trap: 5,142 MiB free < 5.3 GB needed, so BOTH the 100k-switch and stop-Qwen kill the Qwen server this council runs on; CPU is forbidden. There is no non-killing grade. Hence the p23 grade is the FINAL, session-killing act — never a step inside a task that also pre-registers. If a subagent grades before checkpointing, the kill loses uncommitted state (the diff survives on disk; your pre-registrations may not). Grade last, at a committed SWITCHPOINT, restore argv on disk first.

Q1: spike FIRST, GPU-free. GATE's last line already ordered it; chasing the half-done legs is the sunk-cost/ex-post move D59 exists to stop. arcb-05 is a focus-resolution defect (gold rank 4988, upstream); the four D7 rows neither leg touches (chap-01, org-05/06, vol-10) are the same class in disguise. The story-page resolution read needs no GPU, so the spike runs while 135k stays up. Stacking two uncommitted engine changes before you know the upstream defect adds regressions to keep green through the spike.

Q2: flag ABILWIDTH before grading. Unconditional shared-file change, implemented but not pre-registered, violates "JJK baseline untouched" and D59. Mirror TIERED's env flag (OFF = byte-identical); grading as-is is the ex-post retune the rule forbids.

Also: TIERED's +4 includes arcn-02/10/state-08, rows classed Phase-2 extraction-floor. A width flag moving 3 "extraction-gated" rows means your halt boundary isn't extraction-gated — reconcile before banking it. OOS200 190 vs 194 across two instruments is an uncalibrated floor; "not below floor" is meaningless until they agree.

Q4: the ONE task = the GPU-free spike — diagnose arcb-05's resolution, classify the four rows, pre-register the D7-leg fix-class, commit a SWITCHPOINT. Pass bar: written diagnosis + a CPU repro command + committed checkpoint. Stop: checkpoint committed. It does NOT run the full-bank grade — that's the next, session-killing task.

---

## ADVISOR E — Expansionist

The upside everyone's missing: **the 44-line diff is a P6 seed, not a CSM patch.** TIERED (tier-2 recall) and ABILWIDTH (per-wiki abilities width) are generic, zero-hardcoded retrieval mechanisms. TIERED's "0 counter-flips + eval 31/31" proves it's safe to generalize. If they work for CSM they work for JJK/OPM/Bleach — the cross-corpus phase gets a head start. Bank it as CSM, but recognize it as the first cross-corpus retrieval primitive.

**The focus-resolution spike is the real upside, and it's upstream.** arcb-05's gold chunk at rank 4988 isn't an anomaly — it's a signal that "what happens in [arc]?" is broken for story pages, and that class breaks for *every* wiki. Fix the root cause and you recover an entire question class across all 8 corpora, not one row. That's the "works better than expected" payoff.

Q1: **spike first.** Beyond GATE's own order, the economic upside you're not counting: grading the 44-line diff *before* the spike grades against a moving floor — the spike changes retrieval, so a pre-spike grade is wasted work.

Q2: **grade ABILWIDTH unflagged.** It's generic (per-wiki abilities table) — exactly what should ship unconditional. Gating a clean generic win behind a flag buries it. The pre-registration + 0-counter-flip bar is the safety net; that's the conservative job, already covered.

Q3: **100k switch.** Fastest, one atomic script call in; the 135k restore is manual either way (owner launched it manually), so way-in reliability decides it. CPU is dead by rule. The in-flight kill is a non-issue — it fires after this council; owner resumes `-c`, then switches.

Q4: **ONE task = the focus-resolution spike, scoped.** "Fix story-arc focus resolution so arcb-05's gold chunk enters the shortlist. Story-page focus path only — no width changes. Run p23 + blind + d6_flip on CUDA. Pass bar: arcb-05 green, 0 counter-flips, four gates green. Stop: if arcb-05 still red after the focus fix, report the true upstream root cause (chunking? ontology?) and STOP — do not chase it with width or retuning."

Bank the generic wins; spend effort where the class-level upside lives.