# Advisor (executor lens) — CSM plan v2 approval council

Executed on paper. P1.1 is the load-bearing step and it has three missing
preconditions. (1) The switch is not a P1.1 step: at 262k the CUDA-`:8000`
400-probe is impossible (free_mib=1563, api=off — verified). It must come
first: fill SWITCHPOINT's stale hand-written section → `qwen-switch.sh 100k
--force` → `pi_restart` (checkpoint line already exists in SWITCHPOINT). (2)
The bay is gone post-reboot (no tmux, verified): A/B redeploy is an unlisted
~30-min precondition; with the monitor's patches deferred to Phase 2, the
stale-ESC hazard that voided the last gate-3 window stays live through P1.1.
(3) The R-2 Part-A panel is not pre-built: work_log item 4 was never marked
DONE and no Part-A file is on disk — P1.1 assumes it. `/tmp/csm_iter1_records/`
is confirmed gone, so commit messages + the R-5 brief must be rewritten; C1/C2
as written do not cover the dirty plan/SWITCHPOINT/decisions/index/a_wake_log
files or the unlanded CLAUDE.md/WAVE2 doc hygiene (CLAUDE.md:14 still "JJK D6
active") — a third commit or list amendment is needed. The 9-file C1 package is
intact on disk (git status verified). P1.2 is executable but the tightest step:
the 90-min draft now covers relations mode + bundle builder + 2 engine hooks +
the 61-key override (JSON verified: `t0_pilot_csm.json`, 61 keys), and its
brief is the lost `r5_class_plan.md`. P2.1: preconditions check out (panel ✓,
200-held-out ✓, ledger `reports/span-recall/csm/` ✓, handoff doc ✓) except
`reports/csm/GATE.md` does not exist yet — create it. P2.5: all inputs on disk.
Single first move: the model-free rebuild pass — rewrite the lost /tmp staging
(commit messages, Part-A rows + hash, R-5 brief), amend the C1/C2 lists, then
switch → bay → gate legs. Phase-1 done, at machine level: `PHASE_A_COMPLETE
<ts>` in `reports/master-work/phase_status.txt`; miss queue at its 22-floor +
named residuals; ledger-of-record committed, CSM paths git-clean; ~5–6 commits;
Qwen 100k, `:8000` down/CPU, no bay.