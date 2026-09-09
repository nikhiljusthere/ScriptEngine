# Advisor D (The Outsider) — plan-approval council, plan v2 (2026-09-09)

As a first-time reader, this plan reads like an instruction manual with the
glossary page torn out.

**It contradicts the repo's own instruction file.** CLAUDE.md (lines 298–300)
says "The **150k Phase-1 mode** (owner rule 2026-09-08, CSM two-phase plan
`plan/CSM_2PHASE_PLAN.md`) … runs at 150k" — i.e. it attributes 150k to this
very plan — and the unit-3 council record (`plan/state.md` 2026-09-09 04:31)
says "stay 150k, no mid-phase switch." Plan v2 instead says "One dial switch
total: 262k → 100k", never mentions 150k, and its doc-hygiene list (item 7)
fixes CLAUDE.md lines 14/341 but not the 150k line. Either the plan silently
overturned an owner rule, or CLAUDE.md is stale; the plan should say which.

**Numbers that don't add up.** The miss queue is "58 rows (~30 fixable / 22
extraction-gated floors)" (plan lines 48, 108): 30+22=52, six rows
unaccounted for (the council record's basis — 55 open + 3 closed — is not
carried into the plan). Phase 2 sizes "the 17,181-row pinned panel" at
"~15,400 sentences × 3 doors ≈ 51 GPU-h" (line 130): two sizes for the same
panel, never reconciled, and the GPU-hours are asserted, not derived.

**Undefined jargon.** "one-copy", "halt meter", gate-1 through 4 (the plan
names only gate-4 "canon"; which is pytest and which is span-recall is never
said — the ordering lives in `plan/state.md`, unlinked), "seed-7", "5.4
re-adjudication" (5.4 of *what*?), "own-new-row HIT", invariants
"csm-set-14/15". "§9a" and "5.4" are sections of `plan/CSM_WAVE2_RESUME.md`,
which the plan never links. "Council #21 R4" and "#24" are cited as ledger
numbers with no file path.

**Strangest thing:** a CSM plan pins its "baseline-exact" invariant on
One-Punch-Man numbers (canon opm 236/236 @ 79.0%). Defensible — an engine
change must not regress sibling corpora — but the plan never explains why a
CSM invariant includes a third series.

Verdict: the shape is sound; the plan is written for people who already know
the project, not for the engineer who has to execute it next.