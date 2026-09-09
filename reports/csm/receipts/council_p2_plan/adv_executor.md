P2.1: not executable as written. Two council-csm3 (d) blockers closed on disk (roster-door `f93d396`; held-out loader `tools/csm/panel_heldout.py` in `bc73795`); what remains: (a) no pre-declared per-door floor policy — roster/narrative are structurally low-yield on verbatim probes, so "miss file empty" is unattainable on 2 of 3 doors (qa = JJK's 97.5% band; the others measured); (b) 51 GPU-h is wrong: 15,400 is stale — the pinned panel is 17,181 rows; 4 s/probe is an unmeasured JJK figure (JJK warm ≈0.47 s → ≈8 h); SWITCHPOINT L279 pre-registers "sanity runs measure it first"; the plan omits it. First move: three sanity-100 runs (per door, ~7 min) → measure s/probe, re-estimate → one 100k side session per door (~19 h) via gpu-handoff tier-2 in quiet windows.

Boundary: the preconditions are right — 58-row queue at floor (verified), ledger-of-record committed, 100k dial (now 262k; one switch in P1), gpu-handoff reserved (PC_GPU_HANDOFF L3). A regression halt must not write `PHASE_A_COMPLETE`: gate the marker on "floor, not regression."

Q3: P1 already pulled the bar audit into P1.4 (A12d) — amend P2.2's text to "ran in P1.4; re-grade only if P2.1's misses change a dimension." Grader: fresh-context subagent authors 3–5 pre-registered cases per dimension (executor never edits); owner accepts the residual cap.

Q4: reds re-verified from the raw jsonl: 8/6/5/1/1 = 21, plan right; a closed red re-opens only via the P1.4 34 s re-adjudication.

Q5: one script is a test, not a criterion: the pass bar (verify: every line tagged and resolved, zero confident-wrong) is a P2.5 done-criterion line.

Q6: the declaration is complete if it carries P2.1's s/probe + per-door raws + panel hash into `reports/csm/GATE.md` (absent; skeleton lands in P1.1), the P2.4 receipt, the triage log, and a `PHASE_B_COMPLETE` marker — the plan names no Phase-2 marker; "1.5–2 weeks" omits P2 council cycles.