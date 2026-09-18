# COUNCIL VERDICT (chairman, verbatim) — D7 re-score council (CSM Phase 1, §9a closure loop)

Chairman: single fresh-context subagent `ses_f4bb05537ffeYp79GIRq7R63az` (2026-09-18,
opencode). Deployed after the 5 advisors (A–E) and 5 peer reviewers (R1–R5), all
sequential per the owner's 2026-09-08 council rule. Text restored verbatim from the
opencode.db session transcript (the in-conversation copy was truncated at C2);
transport markers stripped, no words changed. Input evidence: the 10 member
responses + the on-disk spot-check (D59 timeline in `plan/drift_log.md`,
`reports/csm/receipts/d6_probe/{TIERED,ABILWIDTH}_PREDICT.md`, `git status`,
`tools/csm/d6_flip.py`).

---

All evidence is on disk. Ruling.

---

# COUNCIL VERDICT — D7 re-score council (CSM Phase 1, §9a closure loop)

## 1. AGREEMENTS

- **Q3 = (b) stop→grade→restore-135k-from-captured-argv: 4–1** (A, B, C, D for (b); E for (a)). All five peer reviews concur (b) is the only path that restores the *live* profile: the `qwen-switch` state record is stale (last entry 2026-09-17 100k; Qwen is actually on an owner-manual 135k, pid 1137321, `--max-context 135168 --kv-capacity 143360`, verified live at 26,948/32,607 MiB).
- **The kill-window must be a detached `setsid nohup` chain with every post-kill step in shell** (R2/R3/R4, unanimous): this session runs *on* the server being killed; the LLM's death is moot only if nothing after the kill needs it.
- **Pre-stage everything before the window**: snapshots, pre-registrations, argv capture (R2/R4), `D6_OOS_PRE.jsonl` backup (R4b).
- **ABILWIDTH's "UNMEASURED" label is correct** — I verified on disk (below), which also settles C's receipts question negatively.
- **TIERED's flag-OFF byte-identity is asserted, not proven** (R1/R2) — folded into the gate run rather than a separate ceremony.

## 2. CLASHES + ADJUDICATION

**C1 — C/D/R5's "read the D59 receipts first" vs A's "grade the legs."** *Ruling: C is right as a pre-check, wrong as a window-killer.* I verified the timeline on disk: D59's 473 full-bank run (drift_log D59) measured **derivation + TIERED-flag-ON**; the ABILWIDTH pre-registration (`reports/csm/receipts/d6_probe/ABILWIDTH_PREDICT.md`) post-dates D60's "remaining reds: 17 (org-03, pool-140/358 + 14 floor)" and was authored at D62 staging. pool-140/358 stayed red in D59's run ⇒ **ABILWIDTH was not in D59's tree; a full-bank counter-flip grade genuinely remains unbought.** The window is needed. But the receipts read stays as pre-check #1 of the task (free, and it puts the fact on record).

**C2 — "ABILWIDTH was never pre-registered" (D/R4).** *Ruling: false, and the record matters.* `ABILWIDTH_PREDICT.md` exists, headered "written BEFORE the change," with registered flips, kill clause, and an explicit *deliberate* choice: "behind no new flag — the predicate itself scopes blast radius; rollback = revert hunk." That doesn't save the position: the no-op for JJK is **data-dependent** (JJK's overrides table has no ability pairs today — R5), not by-construction, and the campaign's own in-file pattern is the env flag (`_tiered_enabled`, "mirrors the events_order_enabled pattern"). *I rule AGAINST the 3-advisor as-is majority (A, C, E): flag it.* Three lines, mirrors the leg beside it, makes JJK no-op structural, and turns the kill switch from "hunk revert" into "unset." Standing rule that decides it: **JJK baseline-exact is a hard constraint, and a shared-file change whose JJK safety rides on wiki data is exactly what the gates exist to police.**

**C3 — legs-first (A/B/C) vs spike-first (D/E, citing GATE.md's last line).** *Ruling: legs first, against GATE's own line.* B's staleness argument holds and is confirmed on disk: GATE's "spike first, then the D7 leg proper" line was written when the spike was presumed to *block* D7; D59's flag-ON measurement already flipped org-03 (a D7 holdout row) before that ordering mattered. The tie-break is the campaign's definition of its own loop: Phase 1 = **close the pre-registered fix-classes, re-run the four gates, halt at the extraction floor.** The legs *are* that registered work; the spike is an unregistered probe on a row (arcb-05) that is in **none** of the 7 D7 holdout rows, with zero code overlap with the width hunks (different path: story-page focus resolution vs top_k/tiered width). E's upside argument (P6, cross-corpus) optimizes a corpus the campaign has explicitly deferred until Phase 1 closes. The GATE line is recorded as **superseded by this council** and amended at commit. The spike runs *next*, GPU-free in a live session, no window — so D's GPU-free advantage survives as ordering-of-the-next-task, not as a hold on the legs.

**C4 — A's task design "stop Qwen at step 2."** *Ruling: fatal, unanimously (R1–R4).* A's subagent dies at its own step 2, leaving no gates, no restore, no receipts. D's "grade last, at a committed switchpoint" over-corrects: R3's detached-chain insight dissolves both constraints — the kill, the grading, the gates, the 135k restore, and the receipts are *one shell artifact* issued as the task's last act. No LLM step follows the kill.

**C5 — D's TIERED floor-row catch.** *Adopted as a record obligation, not a blocker:* TIERED's +4 (arcn-02/10, state-08) flips rows the campaign classified as Phase-2 extraction floor. A Phase-1 flag moving "extraction-gated" rows means the halt boundary is wider than the floor says. The receipt must re-count the floor after the legs (which of the 16 floor rows actually flip) and GATE.md carries the re-count. The 473 itself stands (real flips, 0 counter-flips, blind/eval green).

**C6 — the 17-vs-23 arithmetic (R4).** Verified: p23 486-bank reds = **17** (486−469; D60's list: org-03, pool-140/358 + 14 floor). OOS200 second instrument = **194/200 ⇒ 6 reds**. 17 + 6 = **23** = the briefing's 7 D7 holdout rows + 16 Phase-2 floor rows (7 D7 rows span both instruments; org-05/06/vol-10 are already green post-commit `20d6da4e`, leaving 4 live D7 reds: chap-01, org-03, pool-140/358). OOS floor authority: `d6_flip.py` exit-2 = **any green30 flip OR oos200 drop ≥ 3 vs `D6_OOS_PRE.jsonl`** — that *is* the named floor. The task must re-state instrument ownership before any pass bar is applied.

## 3. FINAL DECISIONS

### Q1 — ORDER
**Narrow legs first, singly and in order (A → B → C), in one kill-window; focus-resolution spike immediately after, GPU-free in the live session.** The legs are bounded, pre-registered (`TIERED_PREDICT.md`, `ABILWIDTH_PREDICT.md`), target-measured (D59: 473/0-counter; Q7/Q8: pool-140/358 flip at top_k=30), and are the registered fix-class closure. The spike's GPU-free-ness makes it the natural *next* task, not a hold. GATE's spike-first line is superseded (C3).

### Q2 — ABILWIDTH FLAG
**Flag it. Against the as-is majority.** Exact semantics:
- New `SCRIPTENGINE_ABILWIDTH_RECALL`, default `"0"`; new `_abilwidth_enabled()` mirroring `_tiered_enabled()` in `scriptengine/api/context.py` (read on every call; kill = unset, no revert commit).
- The existing ABILWIDTH hunk (context.py:619 area) gains `and _abilwidth_enabled()` in its guard — 1 modified line, 2 added. Flag OFF ⇒ predicate never evaluated ⇒ JJK/CSM behavior byte-identical to the committed `20d6da4e` tree, **by construction**.
- Pre-register the flag amendment in the window's PREDICT.md: "Q7/Q8 evidence carries over (predicate unchanged; a gate was added); flag-off = committed-tree behavior, verified by the flag-off gate run."

### Q3 — GPU PATH
**(b), executed as one detached chain.** (a) is rejected: `qwen-switch.sh` restores from a stale state record and strands a second manual restore. (c) is forbidden (full-bank > 15 min CPU).

**Who issues it:** the Phase-1 subagent (Qwen alive) does all pre-staging, writes the chain to `tools/csm/d7_window_chain.sh`, commits the SWITCHPOINT checkpoint (governance commit — engine code stays uncommitted), then issues the chain as its **final act** and ends. The turn dies by design; the **owner** then runs `opencode -c` and reads `reports/csm/receipts/d7_window/RECEIPT_DONE` + `/tmp/d7_gpu_chain.log`. The owner says "commit" only on all-green + green gates.

**Pre-staging (alive, before issue):**
1. **D59 receipts gate** — confirm (as this council did) that D59's 473 tree excluded the ABILWIDTH hunk; write the finding to the receipt. If contradicted: discard legs B/C, no window, record and stop.
2. **Arithmetic** — re-state 17 (p23) / 6 (OOS2nd) / 23-union with per-row instrument ownership; confirm HEAD's `census_widened_csm_results.jsonl` is the 469-era baseline that `d6_flip.py` diffs against.
3. **Backups/snapshots** → `reports/csm/receipts/d7_window/`: `D6_OOS_PRE.jsonl`, `census_widened_csm_results.jsonl`, `blind_fresh_d7_results.jsonl`.
4. **Argv capture (R4: verify before betting the session)** — `ps -o pid= -p <pid>` → `/tmp/d7_qwen_pid.txt`; full argv → `/tmp/d7_qwen_argv.txt`; cwd → `/tmp/d7_qwen_cwd.txt`; `test -x` the binary and `test -e` the model path; record both to the receipt.
5. **The 3-line flag edit** (Q2) + `PREDICT.md` (per-leg pass bars below) + `check_targets.py` (asserts each leg's registered flips against the graded results file; prints PASS/RED per leg).
6. **SWITCHPOINT commit** (plan/SWITCHPOINT.md + drift_log + receipts).

**The chain, verbatim** (`tools/csm/d7_window_chain.sh`; issued as `setsid nohup bash tools/csm/d7_window_chain.sh > /tmp/d7_gpu_chain.log 2>&1 < /dev/null &`):

```bash
#!/usr/bin/env bash
# D7 GPU window: stop 135k -> grade legs singly -> 4 gates -> restore 135k.
# Every step after the kill is shell: no LLM survives by design.
set -u
S=/home/goblin/ScriptEngine
W=$S/reports/csm/receipts/d7_window

# 1. stop the 135k owner-manual Qwen (pid captured on disk in pre-stage)
kill "$(cat /tmp/d7_qwen_pid.txt)"

# 2. poll for the whole card (bounded, status lines)
for i in $(seq 1 36); do
  f=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | tr -d ' ')
  echo "[chain] $(date +%T) gpu_free=${f}MiB"
  [ "$f" -ge 8000 ] && break
  sleep 10
done

# 3. legs, singly, in order — stop at the first red
for leg in A B C; do
  case $leg in
    A) export SCRIPTENGINE_TIERED_RECALL=1  SCRIPTENGINE_ABILWIDTH_RECALL=0 ;;
    B) export SCRIPTENGINE_TIERED_RECALL=0  SCRIPTENGINE_ABILWIDTH_RECALL=1 ;;
    C) export SCRIPTENGINE_TIERED_RECALL=1  SCRIPTENGINE_ABILWIDTH_RECALL=1 ;;
  esac
  CENSUS_DEVICE=cuda python $S/tools/csm/p23_grader.py      > $W/LEG${leg}_p23.log 2>&1 || { echo "$leg: p23 rc=$? (halt)"; break; }
  python $S/tools/csm/blind_score.py                        > $W/LEG${leg}_blind.log 2>&1
  python $S/tools/csm/d6_flip.py                            > $W/LEG${leg}_flip.log 2>&1
  python $S/tools/csm/check_targets.py $leg                 > $W/LEG${leg}_targets.log 2>&1
  grep -q '^RED' $W/LEG${leg}_targets.log $W/LEG${leg}_flip.log 2>/dev/null && { echo "$leg: RED (halt)"; break; }
done

# 4. four standing gates (default env = both flags OFF = committed-tree JJK no-op)
python -m pytest $S/tests/ -q > $W/gate_pytest.log 2>&1
CENSUS_DEVICE=cuda python -m scriptengine.cli eval --series jjk > $W/gate_eval.log 2>&1
python -m scriptengine.cli chunk-containment --series jjk > $W/gate_span.log 2>&1
setsid nohup python -m scriptengine.api.main > $W/gate_api.log 2>&1 < /dev/null &
for i in $(seq 1 60); do curl -sf http://127.0.0.1:8000/health >/dev/null && break; sleep 5; done
python -m scriptengine.cli chunk-containment --series jjk --probe 400 >> $W/gate_span.log 2>&1
pkill -f 'scriptengine\.api\.main'
CENSUS_DEVICE=cuda python -m scriptengine.cli canon-run --series opm --skip-eval > $W/gate_canon.log 2>&1

# 5. restore 135k from the captured argv (cwd + args verified in pre-stage)
( cd "$(cat /tmp/d7_qwen_cwd.txt)" && setsid nohup bash -c "$(cat /tmp/d7_qwen_argv.txt)" > /tmp/qwen135k_restore.log 2>&1 < /dev/null & )
for i in $(seq 1 60); do curl -sf http://127.0.0.1:18080/health >/dev/null && break; sleep 5; done
nvidia-smi > $W/gpu_after.txt
echo DONE > $W/RECEIPT_DONE
```

### Q4 — THE ONE SUBAGENT TASK

**Scope.** Phase 1 (LLM alive, Qwen at 135k): execute the six pre-staging steps above. Phase 2 (shell only): the chain. The subagent's final act is issuing the chain; it does not continue.

**Pre-checks (Phase 1, all GPU-free):**
1. D59 receipts gate (above) — *if contradicted, task collapses to "record + no window"; stop.*
2. 17/6/23 arithmetic re-statement + HEAD census baseline = 469-era confirmation.
3. OOS floor authority recorded: `d6_flip.py` exit-2 (green30 flip OR oos200 drop ≥ 3 vs `D6_OOS_PRE.jsonl`); `D6_OOS_PRE.jsonl` backed up.
4. TIERED flag-off inertness by read (flag off ⇒ `tier2=[]` ⇒ `ordered` unchanged); JJK no-op lands in the gate run, not asserted.
5. Argv capture + verification.
6. Snapshots.

**Pre-registration content** (`$W/PREDICT.md`, timestamped pre-window; builds on the two on-disk predicts):
- Leg A (TIERED=1, ABILWIDTH=0): W ≥ 469 with flips ⊇ {arcn-02, arcn-10, org-03, state-08}; 0 counter-flips; blind 19/19; d6_flip rc=0. (D59 already measured this tree at 473 — the window re-buys it *singly and cleanly*, ex-post-retuning-safe.)
- Leg B (TIERED=0, ABILWIDTH=1): W ≥ 469 with flips ⊇ {pool-140, pool-358}; 0 counter-flips; blind 19/19; d6_flip rc=0.
- Leg C (both on): W ≥ 469 with the union of both flip sets; 0 counter-flips; blind 19/19; d6_flip rc=0.
- Floor re-count: which of the 16 Phase-2 floor rows flip under each leg (C5 record line).

**Pass bar (whole task).** All three legs PASS their registered bars; pytest 1,331 pin; eval jjk 31/31; span-recall jjk 48,572 offline rc=0 + 400-probe ≥ prior baseline; canon opm ≥ 10/16·236/236·79.0%. **Stop conditions:** any leg RED (targets red, counter-flip, OOS drop ≥ 3, green30 flip, grader rc=3) → halt remaining legs, gates still run for the record, restore Qwen, receipt = RED + that leg's kill clause (revert its hunk / unset its flag; re-scope, no ex-post retuning per D59). OOM or restore failure → receipt, owner relaunches manually. **No commit of engine code without owner word** (standing rule); the chain writes receipts only.

**Post-commit flag configuration (R5 gap, closed):**
- Ships: **both flags default OFF** (`SCRIPTENGINE_TIERED_RECALL=0`, `SCRIPTENGINE_ABILWIDTH_RECALL=0`).
- Standing grade: the CSM campaign grade (`p23_grader`) runs **flag-ON** (the CSM win is captured where it belongs — `tools/csm/`); the **four standing gates run default-OFF** (the committed tree), which is the structural JJK no-op proof.
- **Default-flip (shipping CSM default-ON) + its 4-gate rerun + GATE.md record: deferred** — a separate owner decision after this window, one GATE.md line: "default-flip pending owner word; CSM grade runs flag-ON; JJK gates run flag-off."

## 4. RECORD (for COUNCIL_HISTORY.md)

> **D7 re-score council (opencode, 2026-09-18).** Verdict: narrow legs first, singly (A: TIERED=1/ABILWIDTH=0 → B: TIERED=0/ABILWIDTH=1 → C: both), in one detached kill-window; focus-resolution spike after, GPU-free. Ruled ABILWIDTH flagged (`SCRIPTENGINE_ABILWIDTH_RECALL`, default OFF, 3-line mirror of `_tiered_enabled`) **against the as-is majority**, on the JJK-baseline-untouched rule (its no-op was data-dependent, not by-construction; `ABILWIDTH_PREDICT.md` had deliberately chosen unflagged, and the council overrode that pre-registered choice). GPU path (b): stop owner-manual 135k (pid/argv/cwd captured and verified on disk — the `qwen-switch` record is stale), grade legs + 4 standing gates with the card whole, restore 135k from captured argv; the whole kill window is one `setsid nohup` chain issued as the subagent's last act (the session runs on the killed server; all post-kill steps are shell). Pre-checks gate the window: D59 receipts confirm ABILWIDTH was NOT in the 473 tree (full-bank grade genuinely unbought; 17 p23 reds + 6 OOS reds = the briefing's 23, instrument ownership re-stated; OOS floor = `d6_flip.py` exit-2 vs `D6_OOS_PRE.jsonl`). Both flags ship default-OFF; CSM standing grade runs flag-ON, JJK gates flag-off; default-flip deferred to owner. GATE.md's "spike first" line ruled stale (predates D59, which already flipped D7 row org-03) and superseded. Receipts: `reports/csm/receipts/d7_window/`.

---
*Skipped: a dedicated byte-identity /context-diff step (flag-off inertness is read-provable; the gate run is the JJK no-op check). Add when a future leg mutates the flag-off path.*
