# CSM Phase 1 job spec (Terminal B, 2026-09-09)

**Read first:** `plan/CSM_2PHASE_PLAN.md` (v2.2 — the P1 council and P2
council amendments are applied; ledger #25/#26). Work **Phase 1 only
(P1.1–P1.4), in order**. Phase 2 does NOT start when P1.4 looks done —
it starts only after the phase-close reviewer (below) has passed the close
gate. B's last act of Phase 1 is the marker + a stop.

## The contract (typed into B's terminal at boot)

- Control A monitors every shell B runs. **GPU-only shells** (owner rule
  2026-09-09, Phase A): every model-bearing shell runs on CUDA (in-process
  under the one-copy rule — stop `:8000` first via A; probes/canon against
  the CUDA `:8000`). CPU-caught → A kills it and types the standard
  message ("Control A killed your shell (pid …). Re-run on GPU: …") — that
  line is an instruction: re-run the same command on the GPU path
  immediately, checkpoint the kill+rerun in `work_log.md`.
- Checkpoint every unit into `reports/master-work/work_log.md`;
  escalations (incl. `:8000` stops/restarts) go to `plan/state.md` for A.
- `:8000` is up on CUDA (the switch placed it there; A verifies at boot).
  In-process model jobs (pytest/eval with model loads) need `:8000`
  stopped — B signals A, A executes + health-checks + logs the decision.
- The four standing gates run on the one-copy ordering (server down for
  in-process CUDA legs, up on CUDA for the HTTP legs).

## The units (plan v2.2, in order)

1. **P1.1** (plan §Phase 1, steps 0–4, exactly as amended):
   0. zero-GPU baseline re-verify (pytest collect = 1,305 + span-recall
      offline 48,572/48,572 + red-list recount) — re-anchor baseline-exact
      post-reboot.
   1. model-free rebuild of the reboot-lost `/tmp/csm_iter1_records`
      artifacts (C1/C2 commit messages, the R-5 brief, the R-2 Part-A
      panel rows + hash + ledger target — from work_log 06:49:04/06:49:42
      + the on-disk receipts; the Part-A panel was never DONE pre-reboot,
      so REBUILD it, don't assume it).
   2. the 100k switch is ALREADY DONE by the directing session (verify
      `qwen_mode.txt` = 100k; if not, escalate to A — do not switch from B).
      A brings `:8000` to CUDA (named redeployer = A; abort branch per
      plan if the model is dead).
   3. the four gate legs: seed-7 400-probe on the CUDA `:8000` (≥ 390/400)
      → gate-4 canon (236/236 @ 79.0 %) → R-2 Part-A panel (rebuilt) →
      R-3 re-sweep (Part B green; invariants csm-set-14/15; csmdoor-01
      floor held).
   4. the selective 3-commit (C1/C2/C3, path-limited `git add` by named
      paths only — `git add .` is BANNED; the dirty tree carries
      unrelated files). Create the `reports/csm/GATE.md` skeleton (C3).
      Ledger-of-record v1 lands with the package.
2. **P1.2** — the R-5 relations-mode wave: split draft (90-min-or-split,
   R-5 core only: 4th series-agnostic router mode `relations` + budgeted
   bundle builder + MODES/endpoint update) → B grades → the §3 council
   (the kept trigger — **one member at a time, never 2/wave: see "Council
   concurrency" below**; 5 advisors, then reviewers, then chairman; the R-6
   floor-inheritance question is pre-registered in the brief,
   council_r2r3/chairman.md:43) → four gates
   → R5-meter re-sweep (own-new-row HIT ≥ 1 of the class's own new/stamped
   rows, or halt; JJK/OPM invariant pins) → auto-commit. R-6
   (`subject_aliases`) + R-7 (`identity_fields`, 61-key map) run as
   separate short no-council passes. Optional: cross-corpus R-5 spot-pins
   (2–3 phrasings per other corpus, model-free).
3. **P1.3** — halt-meter convergence: the miss queue = 58 rows (33
   fixable [30 open + 3 closed by R-1] + 22 floors + 3 stamped); the meter
   counts ONLY the 33 fixable rows (council #21 R3 scoping — the 22 floors
   + 3 stamped are excluded; without that the meter trips on iteration 1).
   Class closure = own class-targeted re-sweep green. Halt on
   miss-count regression or two no-reduction iterations → council.
4. **P1.4** — the unit-4 close: one-copy four gates + the 34 s 5.4
   re-adjudication (class-by-class) + the pre-registered extraction-pass
   test shape + `coverage_report.py`, then ALL close conditions (a–e:
   campaign-todos sync; C3 landed; GATE.md skeleton exists; the P2.2
   model-free bar audit (3–5 cases per census class, pre-registered)
   run BEFORE the marker; the R-6 floor-inheritance verdict recorded).
   **Then the marker — only at floor, never at regression (A20):**
   `PHASE_A_COMPLETE <ts>` into `reports/master-work/phase_status.txt`.
   **A regression halt = no marker, no Phase 2** (council state; return to
   the halt-meter loop).

## Council concurrency — ONE member at a time (owner 2026-09-10, measured)

**Never run council members 2-per-wave.** Qwen runs `--kv-capacity 102400`
and a single council member's context measures 50,000–86,751 tokens, so two
members can never be resident at once: each evicts the other's prefix and
every turn re-prefills the whole conversation from scratch.

Measured on the live server over 60 consecutive calls during the R-5 council:

- `prefix_reuse_path` = `full_reset` on **56 of 60 calls**; only 4 reused
- **6.1 %** of prompt tokens served from the prefix cache (227,838 of 3,755,807)
- **3,755,807 prompt tokens sent to generate 109,681 completion tokens** — the
  same ~50–86 k context re-sent every turn (this is the whole of what a
  member's "646 k spent" counter is measuring; it is not 646 k of reasoning)

Serial is **faster in wall-clock here, not slower**: one member alone fits the
pool (86 k < 102.4 k), so its prefix stays resident and each turn appends
instead of re-prefilling. This also restores the standing owner rule (councils
= one agent at a time, 2026-09-08).

The 2-subagent wave rule still holds for **non-council** work — short,
model-free workers whose contexts are small enough to co-reside.

## B's last act (Phase 1 end) — AMENDED (owner directive 2026-09-10, `[STEER]`)

**P1.5 (the MCP bridge) is NOT B's work — the directing session took it.**
Drop it from the queue: no `pi install`, no edits to
`scriptengine/mcp/server.py` or `.pi/mcp.json`, and the work_log
`P1.5 START` trigger is void for B. Receipts land in
`reports/master-work/MCP_BRIDGE_P1_5.md`, committed by the directing
session.

Write the marker (floor only), append the final `work_log.md` line
("PHASE 1 COMPLETE — marker written at floor"), then run the **Phase-1
close council** (the §3 trigger: a council after every phase completion).

**The close council MUST carry `reports/csm/CLOSE_COUNCIL_PREREGISTERED.md`
as a numbered item** (owner-raised 2026-09-10: the coverage denominator —
CSM's own tracker reads 0/537 pages and 0 questions against JJK's 893/987 and
29,819, and the 60-question dimension census is character-only). Its
questions 1–4 must be answered on disk, with reasons, **before any Phase-2
GPU-day is committed.**
**On the council's PASS, continue straight into Phase 2** — P2.1 step 0
first (the bounded per-door sanity-100, before any panel spend). No
stop-and-wait for a separate owner go, and no waiting on P1.5.

Unchanged and still binding: the marker is written **only at floor, never
at a regression** (A20). A regression halt = no marker, no Phase 2 — return
to the halt-meter loop and escalate to A.