# Peer review 1

1. **Agree most: A.** The forced-vs-assumption split is the load-bearing correction: constraints force only death-detection and judgment, so A should be a scripted poller plus one-shot LLM judgment — "A ceases to be long-lived." A long-lived A polling every 60 s recreates in the supervisor the exact overflow failure this council is reacting to.

2. **Disagree most: B.** "The overflow is already fixed (135k)" misreads the failure: the session died with strategy buried under ~90k of tool output, not at a capacity wall, and the SWITCHPOINT-on-disk discipline that already existed didn't save the in-context strategy. One session across a 100% campaign deterministically re-buries; "checkpoint more often" leaves strategy only on disk.

3. **Missing from all five:** the load-bearing claim "B is disposable, respawned from state files" is never tested. T0 tests the B→A round-trip, T4 tests loop safety; nobody kills B mid-unit and verifies the respawn resumes the right unit with no double-commit and ESCs preserved. Add a kill-respawn test before the first unattended run — if it fails, the split degrades into silent campaign corruption.