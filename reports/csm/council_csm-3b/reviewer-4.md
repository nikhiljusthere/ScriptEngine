# Peer reviewer 4 — CSM-3b council

**1. Strongest: D.** Only response that fully answers (a)(b)(c) with numbers: F1 as a ~30-line diff + one test as a *sequential pre-step* before the two-parallel Wave 2 — the wave cap is on parallel subagents, not prep work (the key sequencing insight); verification ~7 min (pytest 1,254 in-process CUDA + probe-400); sweep cost corrected from the plan's 51 h to 8–17 GPU-h; clean "do not pull G-CSM-1/2 forward" call.

**2. Biggest blind spot: A.** "Diagnose G-CSM-1/2 in Wave 2, fix only the cheap ones" — but Wave 2 is at the two-subagent cap with both slots filled (CSM-6, CSM-5). A diagnosis task either breaks the cap or displaces a slot. A ignores the budget constraint that C and D both respect.

**3. All five missed:** the close is already recorded on disk — SWITCHPOINT 3b stamped @ 78b5cf3, CSM3B_CLOSEOUT.md committed. The verdict (ratify vs reopen) needs a defined ratify/amend path, or a reopen leaves stale "complete" artifacts that an unattended Phase-2 side session will inherit and trust.