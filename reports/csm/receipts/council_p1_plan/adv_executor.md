# Advisor (executor lens) — Phase-1 plan approval

Executed P1.1–P1.4 on paper against the machine state.

**P1.1 not executable as written — four missing preconditions.** (1) The
switch is not a step: qwen_mode.txt reads mode=262k, free_mib=1606, api=off —
a CUDA `:8000` (~7 GB) is impossible as-is. Order: SWITCHPOINT checkpoint
(exists) → `qwen-switch.sh 100k --force` → `pi_restart.sh` → bring up the
CUDA `:8000` (no bay exists post-reboot; P1.1 names no one to do it).
(2) `/tmp/csm_iter1_records/` gone (verified): C1/C2 messages + R-5 brief
lost, but reconstructable model-free from work_log 06:49:04/06:49:42 — an
unlisted ~30-min rebuild pass. (3) R-2 Part-A panel: owner item 4 never
marked DONE and /tmp died — P1.1's "pre-built rows + hash" is false;
rebuild before the CUDA probe. (4) Monitor-gap patches deferred "before
Phase 2" — the stale-ESC hazard that voided the last gate-3 window stays
live through P1.1 if a bay is used; no bay, gap moot.

The 9-file package is intact (git status). The dirty tree (15 modified + 15
untracked, incl. `E:\Personal\Plot Works/`, `sample scripts/`, stale `STOP`)
is one `git add .` from contamination, and C1/C2 cover neither the
plan/SWITCHPOINT/decisions/index/a_wake_log files nor the R-7 doc-hygiene
targets (CLAUDE.md, CSM_WAVE2_RESUME — unmodified on disk): add a C3.

**P1.2** executable; its brief (lost `r5_class_plan.md`) survives verbatim in
work_log. Add the R-6 floor-inheritance question to the R-5 council brief so
"no-council" doesn't hide it. **P1.3:** the meter as written counts the
whole 58-row queue (verified 33 fixable / 22 floor / 3 stamped); the 22
floors never reduce, so a global meter halts on iteration 1 — carry #21 R3's
scoping in one sentence: count only the 33 fixable. **P1.4** missing:
campaign-todos sync (done-criterion only), the doc-hygiene commit, a
`reports/csm/GATE.md` skeleton (does not exist; P2.1's receipts need it),
ledger row #23 (reserved, unwritten — `reports/comprehension/
COUNCIL_HISTORY.md`).

**Single first move:** model-free rebuild pass (C1/C2 lists, R-5 brief,
Part-A rows+hash) → checkpoint → 100k switch → CUDA `:8000` → gate legs.
**Phase-1 done, machine-level:** CSM paths git-clean (C1+C2+C3+ledger-of-
record v1); `PHASE_A_COMPLETE <ts>` in `reports/master-work/phase_status.txt`
(does not exist yet); miss queue = 33 fixable green + 22 floor + 3 stamped
documented; red list synced; qwen_mode.txt mode=100k, `:8000` down/CPU.