# COUNCIL RECORD — D7 re-score council: peer reviews (R1–R5, verbatim)

Each reviewer independently read all five advisor responses (A–E, see
`advisors.md`) and was asked: (1) which advisor is strongest and why,
(2) the biggest blind spot, (3) what all five missed. Deployed strictly
sequentially, fresh-context, GPU-free, read-only (owner rule 2026-09-08).

**Letter↔session map (reviewers):**
| Letter | opencode task session |
|---|---|
| R1 | `ses_f4bbc4629ffe5esY0FOH7ZhWfh` |
| R2 | `ses_f4bba804bffeBcOCCVtgQc1n0J` |
| R3 | `ses_f4bb87c8cffeB7kGCb01wSnIH1` |
| R4 | `ses_f4bb6bd9fffeMIysL0T0j8AwyA` |
| R5 | `ses_f4bb4aad0ffeQEgHTkjwXbLfll` |

> Fidelity note: restored verbatim from the opencode.db session transcripts
> (final assistant message of each task session); transport markers
> stripped, no words changed.

---

## REVIEW R1

**1. Strongest: D.** Only D spots the real trap: 5,142 MiB free < the 5.3 GB the in-process grader needs, so *no* non-killing grade exists — any CUDA grade stops the Qwen model that *is* the executing agent. D orders around it: pre-registration, snapshot, diff, and SWITCHPOINT all committed to disk *before* the kill; the grade is the final session-killing act, never mid-task; the spike runs GPU-free now with a CPU-repro pass bar that doesn't spend the kill. D also uniquely catches that TIERED's +4 includes Phase-2 floor rows, so the "extraction-gated" halt boundary is incoherent — don't bank 473 as-is.

**2. Biggest blind spot: A** (B, C share the core). A grades at step 3 of 7, then has the *agent* run gates and relaunch at 6–7 — impossible, because the agent is the Qwen model, which is stopped during the grade. A also ships ABILWIDTH unflagged (unmeasured, live, silently re-tunes every future wiki) and its 3-leg plan is three redundant session-kills when D59 already measured TIERED.

**3. What all five missed:** they all couple commit to a green grade. But the flag-guarded tree with flags **OFF** is byte-identical and needs no GPU: flag ABILWIDTH OFF, commit both flags-OFF (JJK untouched by construction), and reserve the session-killing CUDA grade *solely* for the flag-ON decision. The kill is off the critical path for landing the code.

---

## REVIEW R2

**1. Strongest: D.** Only response modeling the Q3 trap: all three GPU options kill the Qwen server this session runs on, so the grade must be the final, session-killing act at a committed SWITCHPOINT — never a mid-task step (A's step 2) nor "moot" (B). D's Q4 (GPU-free spike + checkpoint, kill-grade separate) is the only executable design. Unique catch: TIERED's +4 greens include extraction-floor rows (arcn-02/10, state-08) — banking TIERED invalidates the "extraction-gated halt boundary." (B's OOS200-instrument critique is also right but secondary.)

**2. Biggest blind spot: A.** "Stop Qwen, confirm 32 GB free" is step 2, then five more steps — but the agent's LLM *is* Qwen; it dies at step 2. A also skips C's receipts check (D59's tree may already contain ABILWIDTH → pool-140/358 already measured, no GPU needed) and grades an unmeasured shared-file change unflagged.

**3. All five missed:** (a) kill-window execution: only a detached `setsid nohup` chain (stop → grade → relaunch 135k → write receipts) survives the LLM's death; owner resumes with `opencode -c` and reads receipts. No one named who actually runs the grade. (b) TIERED's flag-OFF byte-identity is asserted, not verified — diff /context output pre-diff vs flag-OFF.

---

## REVIEW R3

**1. Strongest: D.** Only response that solves Q3: (a) and (b) both kill the Qwen instance this session itself runs on (5.1 GiB free < 5.3 GB needed; CPU forbidden), so the grade must be the final, session-killing act, with the SWITCHPOINT + argv committed *before*. D uniquely catches that TIERED's +4 flips extraction-gated rows (arcn-02/10, state-08): a width change moving floor rows means the halt boundary isn't extraction-gated — reconcile before banking 473. Spike-first is GATE's own ordering and is GPU-free; Q4 stops at a committed checkpoint, keeping the killing grade out of the live session.

**2. Biggest blind spot: A.** A stops Qwen at step 2, killing the subagent's own model — "stop at first red" dies with it. It also pre-registers D59's 473 for the TIERED-only leg, but D59 measured a tree where ABILWIDTH was unconditionally active: a contaminated ex-post number; its "flag if the gate goes red" retro-gating is the same D59 violation.

**3. What all five missed:** the campaign's own detached-chain pattern (`setsid nohup bash -c`): pre-stage snapshots + pre-registrations, then queue a detached grading chain that polls for the GPU window, grades, and restores 135k from the on-disk argv — no LLM step follows the flip, so the model death is moot. That dissolves D's "grade last" constraint and C's owner-flip deadlock in one move.

---

## REVIEW R4

**1. Strongest: D.** Gets the decisive constraint: stopping/switching Qwen kills the very session running the work, so the grade is the *last* act, at a committed SWITCHPOINT with pre-registrations and restore-argv on disk first. D alone also catches: ABILWIDTH was never pre-registered (grading it as-is is the ex-post move D59 forbids), and TIERED's +4 includes 3 rows classed extraction-floor — banking 473 quietly moves the halt line. Its task is the only GPU-free, checkpointed one. (Should absorb C's receipts-first step.)

**2. Biggest blind spot: A.** Schedules the killing window as step 2 of the task: stopping Qwen kills the session running it, and A checkpoints nothing to disk first (pre-registrations, restore argv). A also burns the window without reading D59's receipts — ABILWIDTH was unflagged, so it may have been active in D59's tree; then pool-140/358 is already measured red and the window is unnecessary.

**3. All five miss:** (a) "read D59's receipts" as the gating question — if ABILWIDTH was in that tree, discard it; no GPU needed (C sees it, buries it). (b) Restore precondition: nobody verifies the captured 135k argv before betting the session on it; B/E omit the D6_OOS_PRE.jsonl backup the briefing warns about. (c) 486−469=17 but the briefing counts 23 reds; nobody names which instrument owns which, so halt-line arithmetic is unverified.

---

## REVIEW R5

**1. Strongest: C.** Found the decision-changing fact: D59's receipts may already have measured ABILWIDTH — it's unflagged, so if it was in D59's tree, its targets pool-140/358 are absent from the +4 green → already measured net-zero; the briefing's "UNMEASURED" is suspect. Free to check (no GPU); can collapse Q2 and the window. A is the best task skeleton but builds Leg A on the tree assumption C flagged, and its unflagged Q2 is the weakest position in the room.

**2. Biggest blind spot: E.** E optimizes for a P6 upside the campaign defers (P6 waits until Phase 1 closes) and concludes ABILWIDTH should ship unconditional — but the JJK no-op is data-dependent (JJK's table is empty today), not by construction; the flag makes JJK byte-identical by construction (B/D), and (a) rides a stale switch state record, while (b) restores the owner's exact 135k.

**3. All five missed: the post-commit configuration.** With both flags default OFF (B), the commit banks no gain — org-03 stays red in the standing grade, D7 unclosed; the default-flip decision (its 4-gate rerun, the grader's flag env, GATE.md record) is scoped by no one. Also: one diff in context.py — committing TIERED alone needs a hunk split.

---

## Tally (pre-chairman)

- **Strongest advisor:** D ×4 (R1–R4), C ×1 (R5).
- **Blind spot:** A ×4 (R1–R4), E ×1 (R5).
- **Q1 (order):** legs-first A/B/C (3) vs spike-first D/E (2).
- **Q2 (ABILWIDTH flag):** unflagged A/C/E (3) vs flag B/D (2).
- **Q3 (GPU):** (b) A/B/C (3), (b)-grade-last-at-switchpoint D (1), (a) 100k-switch E (1).
- **Q4 (the task):** legs-window A/B/C variants vs GPU-free-spike task D/E.