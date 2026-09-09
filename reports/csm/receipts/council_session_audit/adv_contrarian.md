# Contrarian — CSM 100% campaign audit (2026-09-09)

The campaign's fatal flaw: **its validated state lives outside git.** The only
engine work of §9a iteration 1 — R-2+R-3 (`hybrid.py`, `roster.py`, `facts.py`,
`series/csm/overrides.yaml`, two test files; `git status` still shows all of it
modified) — has been uncommitted for ~10 hours, ever since the owner's 12:3x
override queued a commit that never ran. The staged 2-commit package sat in
`/tmp`; the machine rebooted, `/tmp/csm_iter1_records` is gone (verified:
directory absent), and the gate-3 window that was certifying the 9 files was
voided at ledger row 4,315 — 685 ERROR rows in
`reports/span-recall/jjk/recall_verbatim.jsonl` (verified). "Raw receipts on
disk" protects *files*, not *gated* state: one reboot erased two work-days of
validation, and recovery is a full CUDA gate re-run. The plan says commit after
each unit; unit 3 is ~40% done and uncommitted. One more reboot and the campaign
is re-proving work it already finished.

Process is the critical path. 7 councils = 77 sequential LLM runs, ~2h each.
Observed cost per engine class: R-1 ~1 day; R-2/R-3 a day and still uncommitted —
two workers (both hit the 60-min timeout in their final verification loop; R-2's
receipt was lost and B reconstructed it), a ~2h council, a 2–3h gate cycle (57–77
min of it a serial CPU 400-probe at 8.5 s/probe), re-sweeps. R-5, R-6, R-7 each
repeat the whole cycle. Of 133 commits since 09-07 (verified: 40+72+21), only 16
touch `scriptengine/` and just 4 are CSM engine commits. The repo is churning
governance, not fixes.

The A/B failure mode has already fired: A's stale-pid ESC killed the `:8000`
that B's probe depended on, voiding the 400-row window; the monitor's auto-kill
branch is blind to CPU `:8000` children (documented, unfixed). And the summary
layer keeps lying — the 49/60 digit transposition, the 29/26 arithmetic, the
heredoc bug that ate two field names (all CORRECTION lines in `work_log.md`) —
which is exactly why every council spends two hours re-verifying raw files.

Schedule: "faster than JJK" is unfalsifiable — JJK's D6 is still open (P0–P5), so
CSM is the first corpus run to D6 against a bar the reference corpus never
actually passed. Realistic close: 2–4 days to finish unit 3/4 (R-5 + hooks +
re-gates + the stuck commit), then Phase 2 (51 GPU-h + the 17,181-row control
arm) ≈ +3 days. ~1.5–2 weeks total — and 22 of the 55 open miss-queue rows are
extraction-gated floors (verified), so "100%" is not possible without Phase 2.