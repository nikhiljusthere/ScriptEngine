# Review 1

**1. Strongest: A.** The only verifiable structural diagnosis: §9a engine work uncommitted
(per git status, hybrid.py/roster.py/facts.py + csm overrides + 2 test files uncommitted;
133 commits since 09-07, only 16 touch scriptengine/), and /tmp/csm_iter1_records gone
(verified). Its claim — "raw receipts on disk protect files, not gated state" — is the real
finding. B/D correctly catch the stale "JJK D6 open" framing (GATE.md:697 says done), but
that is reframing, not diagnosis; E is a solid execution plan but assumes the failure modes
won't recur; C is a cross-corpus detour.

**2. Shared blind spot: the owner's attention is the binding resource.** All five price
LLM/wall-clock cost (councils, 60-min timeouts, 51 GPU-h) but none asks why the owner had
to queue the override commit, override-switch to CUDA mid-run (voiding the 400-probe
window), and close bay B. The campaign only moves while the owner watches; no response
proposes an owner-free run mode.

**3. Add: make committing verified state part of the gate pipeline.** "Commit now" (A/E) is
a one-off. Gate-green ⇒ auto-commit (ledgers + records included) makes the "reboot loses
verified state" incident class structurally impossible and ends live-supervised gate
windows.