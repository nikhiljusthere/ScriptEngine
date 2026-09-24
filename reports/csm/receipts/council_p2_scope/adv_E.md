# The Executor — council #38 (2026-09-24)

**Q1** Yes — the D6 zero-flip is mechanical (the events table feeds only the narrative door; qa rows lose at ranking against chunks that already hold the expect sentences), so no row is extraction-content. The state-over-time interval facts are already on the in-scope narrative axis.

**Q2** Sound; add the post-shape span-recall + coverage re-proof line (the P2-execute step demands it; it's missing from the budget table, ~10 min) and re-run the `--dry-run` at window start to re-verify 230/406 at current HEAD.

**Q3** Faithful — class-scoped, zero engine change, counters measured (149/252 + 486), not assumed. Other counter-flips reopen class scope without voiding the trigger bar: exactly #37's line.

**Q4** Run (d) right after (b): it's in-process, 30–45 min, independent of extraction. The width decision must not ride on extraction; a RED at hour 3 lets you shrink the window.

**Q5** Separate gated window — it's an engine commit; #37 already ruled it standalone. Bundling it into a measurement window breaks one-mechanism-at-a-time attribution.

**Legs** (launch → poll → proof → wedge):
- **(a)** `setsid nohup bash tools/csm/d7_gates.sh </dev/null >/dev/null 2>&1 &` → `tail /tmp/d7_gates.log; cat /tmp/d7_gates/state` → `/tmp/d7_gates/STATE.{pytest,eval,span,canon,banks}` + pre-bank snapshot. Wedge: the restore trap runs the owner's UNCOMMITTED argv (`/mnt/PROJECTS/ninfer-transfer` model path, root-owned mount) — if that mount is down at window start, Qwen never comes back.
- **(b)** `setsid nohup bash tools/csm/p21_sweep.sh >/dev/null 2>&1 < /dev/null &` → `reports/master-work/p21_sweep_<stamp>_run.log` → `p21_sweep_<stamp>_RECEIPT.md`. Wedge: stale stamp @`4b60043` — wipe stamps at current HEAD first or pre-checks 10–12 halt.
- **(c)** first `scriptengine/.venv/bin/python -m scriptengine.cli events-extract --series csm --scope corpus --pages reports/csm/p2_keep_pages.txt --dry-run` (re-verify 230/406), then the same command detached `--workers 2` → per-page lines in the log → a fresh session must WRITE `reports/csm/receipts/p2_extract/RECEIPT_<stamp>.md` — no pre-baked runner exists; that's the first Monday-morning build. Wedge: OOM → resume `--workers 1`.
- **(d)** first: write `tools/csm/widthclass_run.py` (driver over `p23_grader.grade_item(top_k=30)`: 4 rows + 486 sweep + blind/OOS), then detach in-process → run log → `reports/csm/receipts/d6_probe/widthclass_run.md`. Wedge: GPU free < 6 GB after Qwen down (halt 11) / missing venv (halt 12).
- **(e)** `setsid nohup bash tools/csm/p23_handoff.sh >/dev/null 2>&1 < /dev/null &` → newest `reports/master-work/p23_grader_*_RECEIPT.md` (the proof) → halt 10: Qwen still up (mode file not off).

**Window** One window: (a)+(b)+(d)+(e) ≈ 4.75–5.75 h is minimum-viable; (c) is the stretch leg (total 7–9 h, still < 2 GPU-days). If any gate leg is RED or the start is late, cut (c) to a second window — nothing in (d)/(e) depends on it.