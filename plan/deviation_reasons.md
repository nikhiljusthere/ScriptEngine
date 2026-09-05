# deviation_reasons.md

One entry per **refuted premise**. This file records halts, not substitutions.

**A deviation is a refusal.** When a step's PREMISE is refuted, the step stops
and surfaces. It does not authorise doing something else instead. Both times
the executing agent deviated in this project and was right, it *refused* — it
declined to rewrite `arc_key`, which would have broken the only consumer.
Refusal fails safe and is cheap to review; substitution fails silently.

**Every entry must carry the raw evidence that refuted the premise** — query
output, or `file:line`. This file is agent-authored, which puts it in the same
class as reports that have been wrong five times. The evidence requirement is
what makes it checkable rather than narrative.

---

## Template

```
## <step id> — premise refuted <date>

- **premise as written:**
- **verified on tree:**            <path — a check on the wrong checkout is worse than none>
- **what the check returned:**     <raw output, or file:line>
- **why the step cannot proceed as written:**
- **what is now blocked:**
- **what would unblock it:**       <a question or a decision, not an action taken>
```

---

## Pre-run — "cherry-pick the twelve plan commits" refuted 2026-09-05

- **premise as written:** the planning documents live on branch
  `worktree-plan-to-perfection`, **not on the executing branch** — so cherry-pick
  `8b51e15 7fdc8a1 80d02cf 97aec46 acc4c3b f393c4e 8558d5a 8a1f30c 029e138
  97d2cf3 d204b0b cc448ba` in order.
- **verified on tree:** working tree `/home/goblin/ScriptEngine`, branch
  `character-scoped-questions`, HEAD `5270238`.
- **what the check returned:**
  - all twelve commits' subjects already exist on HEAD under different hashes:
    `ee0f80b 77da95e 623be9f 291e5f5 75d2517 78763dd 9273118 0b67d99 a1167a9
    cd9e812 b2c90f2 5270238` (same subjects, cherry-picked in a prior session).
  - `git diff --stat HEAD worktree-plan-to-perfection -- plan/` → empty (the
    `plan/` tree is byte-identical on both branches).
  - `sha256sum plan/ORACLE_v1.yaml` →
    `a788fa29652a58152edf0f2ce16caea626db35d7e4463ec66176b5635a15935e`
    (matches the oracle's published hash).
- **why the step cannot proceed as written:** cherry-picking the twelve commits
  again would create twelve empty commits (their changes are already in the
  tree) and risk conflicts with the working tree's uncommitted changes.
- **what is now blocked:** nothing. The intended end-state — the planning
  documents present on the executing branch and verified — already holds.
- **what would unblock it:** nothing; the step is skipped, not substituted.
  The next step (reading the four plan files) proceeds as written.

---

## 0A — "the `meaning` DDL is committed-but-unconfirmed" inaccurate 2026-09-05

- **premise as written:** the `meaning` DDL is committed-but-unconfirmed, its
  model columns empty, and three defects its own council found are cheap to fix.
- **verified on tree:** working tree `/home/goblin/ScriptEngine`, branch
  `character-scoped-questions`.
- **what the check returned:**
  - the `meaning` DDL was **uncommitted working-tree** (`stores/facts.py` and
    `schema.sql` not yet in git), not "committed-but-unconfirmed" as the premise
    stated.
  - the `meaning` table was **absent from the live store**
    (`series/jjk/facts.db`), so "meaning exists" held only in the DDL, not the
    live DB.
  - the model-populated columns (`class`, `is_event`, `participants`,
    `arc_index`, `chapter`) were empty, as the premise said.
- **why the step still proceeded as written:** VERIFY (`meaning` exists; its
  model-populated columns are empty) passed on the tree, and all three fixes
  (the "unverified complement" rename, the stop-citing-the-events-key edit, and
  the class-vocabulary `CHECK` + `is_event`-derived statement) applied cleanly
  to the DDL. The premise's "committed" is a git-state description, not a
  description of the defect being fixed, so it did not block the step.
- **what is now blocked:** nothing. **No halt, no substitution** — the step
  proceeded as written; this entry records the premise's factual inaccuracy for
  the record (VERIFY passed vacuously on the empty live store).
- **what would unblock it:** nothing; recorded, not a halt.
