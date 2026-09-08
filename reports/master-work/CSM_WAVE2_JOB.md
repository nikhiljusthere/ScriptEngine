# CSM Wave-2 job spec (B's units, in order)

Read `plan/CSM_WAVE2_RESUME.md` first — its §3 (council trigger) and §4
(JJK-100% invariant) are load-bearing for every unit.

## The contract (typed into B's terminal at bootstrap)

> Read `reports/master-work/CSM_WAVE2_JOB.md` and execute the units in order.
> Control A monitors every shell you run — GPU-only, no CPU shell >15 s,
> >300 s runs get flagged for A's judgment — re-run per its hints (they appear
> in your terminal or `reports/master-work/interventions.jsonl`).

## Units (wave rule: deploy 2 worker subs → both results on disk → verify with
raw receipts → next pair; councils are a separate cadence, one agent at a time)

1. **CSM-6 instrument (no extraction).** Parameterize `tools/csm/
   census_dimensions.py` + `placement_audit.py` with `--series`; regenerate
   the §12 dimension map from CSM's own sections; the eight-verb 100-sentence
   sample (reading — no model); frozen census sets (seeded + revid-stamped,
   generated fresh from CSM, never copied from JJK); T0 pilot via the
   series-agnostic `page_gen.py` (freeze to JSON, seed + revid, record
   emergence + survival = pilot numbers #1/#2); cross-page fact census (SQL
   over the graph, <15 s).
2. **CSM-5 remainder.** 5.3 pilot fixtures (only on the code CSM's fixes
   actually exercise); 5.5 generator-sliced gold + held-out set +
   pre-registered red list (NO LLM judge); 5.4 door pre-check (zero GPU —
   narrative door against existing cheap signals; extraction only if the
   Wave-2 dimension census goes red); the twenty-failures set (named author =
   a fresh-context subagent, executed never edited).
3. **§9a closure loop, iteration 1.** Batch sweep (Wave-1 pinned panel + the
   400-probe standing gate, on CUDA, one-copy ordering) → pre-triaged miss
   queue (MISS_DOC / MISS_SPAN / gate violation / twenty-failures hit) →
   serial engine-fix closure (one class per fix; per-wiki override preferred;
   never reword to pass). B (orchestrator, never the fixing subagent) runs
   the sweep that grades a fix. Halt: miss-count regression or two
   no-reduction iterations → council.
4. **Phase close.** The four standing gates on CUDA (pytest 1,254 / eval jjk
   31/31 / span-recall 48,572 + 400-probe / canon opm 236/236 · 79.0% — a
   regression = halt + fix, not a note); the phase-completion council
   (trigger §3a of the plan); commit; `tools/coverage_report.py`.

## File discipline (JJK-100% invariant)

- CSM-centric only: `tools/csm/*`, `series/csm/overrides.yaml`,
  `reports/csm/*`. Never the JJK baseline: `gold_jjk.json`, `series/jjk/*`,
  the JJK overrides, any JJK gate baseline.
- Per-wiki handling → `series/csm/overrides.yaml`, never engine code naming a
  series. New CSM-specific engine files are allowed (series-parameterized,
  `--series csm`).
- After every engine change: re-run the four standing gates. JJK stays at
  100%.
- Commit after each unit; named paths only, never `git add -A`.

## Bootstrap (the orchestrator types these, one per window)

**A — tmux session `control`** (after pi is up):

> You are Control A for the CSM Wave-2 bay. Read `plan/CSM_WAVE2_RESUME.md`
> §2. When B's pi pid is known (the `work` session), launch the monitor:
> `setsid nohup bash tools/master-work/csm-control.sh <b_pid> work
> reports/master-work > /dev/null 2>&1 &`. Then your standing loop: every ~3
> min read `reports/master-work/shell_log.jsonl` + `interventions.jsonl` and
> judge (kill / re-run / let run); typed hints go through the monitor, and
> probe a file side-channel after any hint — never assume a type landed.
> Commit after each intervention batch. B's job spec:
> `reports/master-work/CSM_WAVE2_JOB.md`.

**B — tmux session `work`** (after pi is up):

> Read `reports/master-work/CSM_WAVE2_JOB.md` and execute the units in order.
> Control A monitors every shell you run — GPU-only, no CPU shell >15 s,
> >300 s runs get flagged for A's judgment — re-run per its hints (they
> appear in your terminal or `reports/master-work/interventions.jsonl`).
> Read `plan/CSM_WAVE2_RESUME.md` §3–4 (council trigger, JJK-100% invariant)
> before unit 1.