# Council session audit — advisor: First Principles

**What is actually being solved.** Stripped of vocabulary, the campaign is not
"CSM comprehension" — the asset is a checkable 100%: the D1–D10 done-set, raw
receipts, zero unexplained failures. CSM is the first corpus run under that
definition — the authorized successor (todo #9) after JJK halted before P6.
But the audit's framing is stale: QUESTION.md/CLAUDE.md say "JJK D6 still
open"; on disk GATE.md:687 + DONE_DECLARATION.md (09-07) declare it closed —
"terminal state: done." So "can CSM close faster than JJK?" is the wrong
question: CSM is not finishing JJK's open D-layer work — it *is* the P6
cross-corpus successor. JJK's D6 campaign ran without the A/B bay, machine
monitor, or per-engine-change council trigger — you cannot beat a baseline
that did not pay your verification cost.

**Is the decomposition right?** Two-phase + closure loop is the right shape:
Phase 1 fixes are cheap and shrink Phase 2's 51 GPU-h (council R4); the
frozen-miss-queue → one-class-at-a-time → re-sweep → halt machinery is right
for a finite miss set. The mis-shaped part is the process layer: (1) the
council's own record prices per-engine-fix overhead at 2.5–5 h × up to 5
fixes ≈ 12.5–25 h — "not the sweep… is unit-3's wall-clock driver"; (2) the
"at every big engine change" trigger (09-09 rule) counseled a 22-line router
rule (R-1, ledger #22) at full 11-member cost — 7 councils in 3 days, where
JJK counseled at build/phase granularity; (3) the incidents are process
fragility, not corpus: 60-min worker timeouts, the stale ESC voiding gate-3,
/tmp loss on reboot.

**Carry / change.** Carry from JJK: checkable done-set, frozen pre-registered
sets, fix-root-cause-never-reword, raw receipts, per-wiki overrides — all
active in CSM. Change: counsel on pre-registered fix *classes* (R-1..R-5),
not per hunk; re-anchor the goal: "close 21 reds + 30 queue rows + 51 GPU-h
in ~2 GPU-days without process overhead eating the wall-clock."
