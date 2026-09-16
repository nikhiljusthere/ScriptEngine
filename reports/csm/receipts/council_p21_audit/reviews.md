# CSM P2.1 runner council — peer reviews (council #30)

- Date: 2026-09-16/17, 23:58–00:21 IST
- Method: 5 peer reviewers deployed in parallel (owner directive 2026-09-12), each
  fresh-context, zero-GPU, read-only, reviewing the five advisor finals **anonymized by
  letter** (A–E); reviews ≤250 words.
- Provenance: finals transcribed **verbatim** from the session database
  (`~/.local/share/opencode/opencode.db`, message table).
- R1–R5 mapping: R1 = `ses_f548612dbffe6i4MdaJaiB6RG1`, R2 = `ses_f548612d3ffe9Hkn7O0VVhrp8d`,
  R3 = `ses_f548612cdffeoADL2l5jFhPT0o`, R4 = `ses_f548612c3ffesVV749HjqJv18a`,
  R5 = `ses_f548612baffeu3g4wxS0rEjOsE`.

## R1

VERDICT: SUPPORT A, C, D, E on all load-bearing claims; REBUT A on one wall-clock misstatement (minor; verdict unchanged).

CORRECTIONS:
1. **A** — "burns ~2.7 h per door": GATE.md:312 states "≈ 2.7 h **panel** (step-0 timer) + ~4 min heldout" — 2.7 h covers all four 17,181-row doors, so per-door ≈ 40 min. A's other citations all verify (p21_sweep.sh:12-13 service-state-only pre-checks, 153 no `--sanity`, 169-186 sidecar watchdog, 224-230 no-commit; api/main.py:79 five-mode Literal; span_recall.py:214 `mode=door`).
2. **E** — "6.2 GB free" is not a disk record; it is a GiB-unit derivation of work_log:118 (Qwen 25,576 MiB @122880 dial ≈ 6.2 GiB free of 31.25 GiB). Consistent, but a computed figure, not a citation.

CONFIRMATIONS:
1. Disk state as claimed: 4×100-row ledgers — qa/narrative/roster stamped `f2a611d`, auto stamped `2f67222` (matches GATE.md:337-340); HITs 95/35/2/37; no `.new` sidecars; `sweep_auto_ec15e0d8` absent; panel/heldout shas `cf72135f…`/`604dc8ca…`, h8 `e3d73720`/`ec15e0d8`; GATE.md:308-309 omit rc 3 dead-door (runner header p21_sweep.sh:22 covers it).
2. `chronology.py:616` `wants_chronology_set` exists (called from router.py:632); R-5 OOM at 66 MiB free (work_log:94); the in-gate co-location pattern is unique to work_log:118.

## R2

I have everything I need. Live state confirms Qwen pid 5625 @122880 (120k), 6.17 GB free, `:8000` down — so E's 120k VRAM math is on the live dial while B's "co-locate with Qwen 100k" is the stale label. The authoritative gate order (`plan/gpu_gate3_task.md`) and the exit-30 check (`p21_sweep.sh:196-97`, `PANEL_ROWS=17181`) are confirmed.

---
**Verdict: SUPPORT A, C, E; REBUT B only on its W1 co-locate VRAM premise (its "stop Qwen first" hedge is the right branch).**

LOGIC DEFECTS
1. **B (Q1) — stale dial.** "Co-locate with Qwen 100k": the live dial is 122880/120k (`qwen_mode.txt`), ~6.2 GB free; the 5.3 GB W1 in-process load leaves ~0.9 GB headroom — thin against the R-5 OOM precedent (0.07 GB). Stop Qwen before W1 (E's order): same stop/start count, safer.
2. **A (Q2) — INTEGRITY gap.** A `--sanity 100` pre-pass ends at ledger=100; through the runner's per-door check (`p21_sweep.sh:196-97`, 17,181 expected) it trips exit 30. It works only as a standalone call before the full-door loop; "first-run only" is right but that bypass isn't made explicit.

SOUND REASONING
- **A (Q2):** `limit` applies to un-probed rows (`span_recall.py:427-28`); a fresh pre-pass = the 100 floor rows, clean-merge, full resume = 17,181 (no exit 30); a resumed capped-100 *will* trip exit 30, so "drop on resume" is correct.
- **C (Q5):** `route(series_paths("csm"), sentence)` mirrors the auto-door exactly — `api/main.py:208` is `route(...,subject=None)`, the sweep sends no subject, and R-8's guard (`chronology.py:597/616`) is a pure query regex, no series context. B's first-100 canary (Q3) is sound too; E's six-step order (Q4) is correct.

## R3

**Verdict:** SUPPORT A (both actions) + B + D's rc-3/stop-tool lines (fold into B's rewrite); REBUT C's two pre-sweep expansions as marginal-to-skip for the hand-off.

**PRICINGS**
1. **W1/W2 + ledger-sha (B/E, GATE.md:342-349, 16-19):** deferred → literal executor stalls at gate-3 (needs :8000) and re-runs the window; sha trap (phase_status.txt:4/:9) alone = 1–2 GPU-h. NOW: 20–30 min docs + re-stamp. **DO.**
2. **Wrong stop tool (D/E):** deferred → qwen-switch.sh leaves no mode=off marker → ninfer_restart poller resurrects Qwen mid-sweep → exit 4 + the zero-contention premise (2.7 h) void; recovery ≈ 30–60 min + re-estimate. NOW: 2 lines. **DO (fold in).**
3. **rc-3 omission (D):** reachable only if #4 lands; misread as tamper (rc 2) → 1–2 GPU-h wrong triage. NOW: 1 line. **DO (fold in).**
4. **Runner: --sanity 100 fresh-only + record /health `device` (A):** deferred → dead door burns ~40 min/door blind, go/no-go deferred 2.7 h; CPU :8000 → estimate void (5–10×) and A17 floors are CPU numbers → spurious council-#26 abort/go. NOW: ~30–45 min; re-bakes d1c1ff8's dry-run (zero GPU, minutes; nothing GPU-side invalidated). **DO — best value in the set.**
5. **C route() bucketing (30 min, model-free):** sanity pre-pass already catches dead doors in ~10 min; hit-rate shortfall is an A17 post-run finding, not an abort trigger (council #26 gates on wall-time). **SKIP pre-sweep; run post-hoc if triage needs it.**
6. **C Q1/Q2 bank (≈1–2 h model-free, bar-audit precedent):** gates P2.3, not the sweep; GPU session's CPU is free during the detached 2.7 h run → do it on-card in parallel at zero marginal cost. **SKIP now.**

**RECOMMENDED SET:** #4 + #1 + #2 + #3 in one ~1 h zero-GPU coding pass (runner + one GATE.md/phase_status re-stamp + commit); C's items ride the GPU session.

## R4

**VERDICT: SUPPORT — ship-with-changes.** Runner, ledger, merge verified clean: merge is atomic (span_recall.py:352, tmp+rename, sidecar unlinked after → mid-merge kill = idempotent re-merge, no backup needed); rows are ~730 B (100-row ledgers are 72–75 KB) → ~65 MB total, 29 GB free → no disk check required; 120 s probe timeout (span_recall.py:371) makes a dead :8000 a caught ERROR (≈102 min to the 51-row halt), not a silent stall. **Rebut D/E:** their bare-`kill` leaves `qwen_mode.txt` at `mode=122880` — `ninfer_restart.sh:13` (via csm-watch/gpu-handoff) resurrects Qwen at 120 k *mid-sweep*. Use `ninfer-stop.sh` (writes `mode=off`).

1. **Qwen dial trap** — disk dial 122880, stop-tool hint says 262k (`ninfer-stop.sh`), plan's Phase-2 dial is 100k (`plan/CSM_2PHASE_PLAN.md` header, A19). Fix: hand-off line "stop via ninfer-stop.sh, verify `mode=off`; post-sweep restart `qwen-switch.sh 100k` for D6, not 262k."
2. **1,331 pin lacks W-state** — W1 (down) = 1,331 + 3 env-mc fails; W2 (up) = 1,334/0 after R-8's test fix (`tests/test_mcp_server.py:20,35,46`); GATE.md R-8 section is silent → false re-pin risk. Fix: one line in GATE.md.
3. **2.7 h estimate omits the auto full-panel door** — `reports/csm/GATE.md:312` sums only qa/narr/roster; auto measured 0.192 s/probe (:137 addendum) → ≈3.7 h; no wall-time cap in the runner. Fix: correct the figure.
4. **Orphan door CLI** — no trap in `p21_sweep.sh` run_door; non-reboot runner death + "re-run the launch line" = two sweeps into one sidecar. Fix: `trap 'kill $pid' EXIT`.
5. **Post-sweep steps uncarried** — P2.2 re-grade only if misses shift a dimension; A14 comprehension step must fire (P2.3b if null) before PHASE_B_COMPLETE.

## R5

**REBUT** the "runner is sound / doc-only" consensus — one code-level defect survives d1c1ff8, on the resume path.

1. **ERROR window straddles the resume boundary** — `p21_sweep.sh:177` counts ERROR over the last 50 rows of *main+sidecar*, but the sidecar is never reset on resume: `span_recall.py:408-411` reads the stale `.new` into `prior`, `:469` appends fresh rows *after* the old ERROR burst; merge only on clean exit (`:488-489`). After an exit-5 halt + the documented resume (`p21_sweep.sh:224-230`), if <40 rows are probed by tick 1 (30s sleep, `:47,157`), the stale burst still sits in the window → **false exit 5, ~coin-flip at every resume after an ERROR burst**. The advertised recovery procedure is unreliable in exactly the most-likely halt mode. HIGH. Fix: two runner lines (baseline sidecar row-count at door start, count only this run's rows) + receipt wording `:222`; re-verify = the 14-assert dry-run + one new assertion. No CLI change.
2. **Wedged :8000 defeats both halts** — `/health` (`api/main.py:149-165`) never touches the model, so a wedged server passes health (exit 4 never fires); probes time out at 120s (`span_recall.py:371`) so the 50-row bound needs ~100 min per wedged door; runner has no wall cap. MEDIUM.
3. **"Device not recorded" is code, not doc** — `/health` serves `device` (`main.py:161`); receipt records VRAM only (`p21_sweep.sh:71`); a CPU :8000 passes all pre-checks (`:83-88`). One curl line.

Refuted: halt receipt *does* carry halt sections (`:219-230`, pre-written); no kill/merge dual-writer (merge only on clean exit, atomic rename `:352-366` → worst case rc 2→exit 22); HIT is content-based (`span_recall.py:447`), so "all-HIT on wrong docs" is impossible; ledger names verified on disk (e3d73720/ec15e0d8 recomputed-match).

Doc-only defensible? **No** — finding 1 + the device line are runner code; ship a small patch + re-run the dry-run, keep the rest doc-only.
