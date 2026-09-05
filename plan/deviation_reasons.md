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

---

## 2B — "oracle F1/F2 failed at 1A" refuted 2026-09-05

- **premise as written:** flow.md 2B: "PREMISE: oracle F1/F2 failed at 1A
  (i.e. retrieval does not already serve these). IF REFUTED: no extraction
  owed — halt and record."
- **verified on tree:** working tree `/home/goblin/ScriptEngine`, branch
  `character-scoped-questions`, HEAD `94909d2` (Phase 0); `:8000` on CPU
  (PID 94330, start 2026-09-05T18:03:22Z — after the commit, so the committed
  code served every item).
- **what the check returned:** F1 and F2 both **PASS** at 1A —
  `reports/comprehension/PHASE1A_ORACLE.md:48-49` (F1: "Todo `Equipment`
  section served (Playful Cloud entry)"; F2: "Todo `Quotes` section served");
  raw bundles `reports/comprehension/raw/oracle_1a/F1.json` (sha256
  `60bafa963b34f8c6d81591d0b31537fd08739add2725fbc4ea8754a6c94e9b7f`) and
  `F2.json` (sha256
  `5e05eab1bda323cabe7a06a627e8db4b06cd7a56f004facfffd09747fa0c72ef`),
  pinned in `reports/comprehension/COUNCIL_1.md`.
- **why the step cannot proceed as written:** the premise is refuted by its
  own measure — retrieval already serves Equipment and Quotes in plain
  phrasing, so no extraction is owed.
- **what is now blocked:** nothing. 2B halts; the 3,782 (Equipment) + 1,518
  (Quotes) words leave the build list.
- **what would unblock it:** nothing; the halt is the end-state. A future
  phase that needs Equipment/Quotes extraction must bring its own oracle
  evidence (a new ORACLE_v2 item, council-approved).

---

## Phase 5 — premise gate unmet; the phase closes in full 2026-09-05

- **premise as written:** flow.md:231-243 — Phase 5 (the subjective set:
  Personality / Appearance / Overview / Trivia / History) is "gated behind
  retrieval" and "may not exist"; it opens only if retrieval does not already
  serve the sections (the plan's per-section list, ~106,000 words).
- **verified on tree:** working tree `/home/goblin/ScriptEngine`, branch
  `character-scoped-questions`, HEAD `94909d2`; live store
  `series/jjk/facts.db` probed via copy (read-only store).
- **what the check returned:** E1–E4 (all `category: personality`) all
  **PASS** at 1A — `reports/comprehension/PHASE1A_ORACLE.md:44-47`; raw
  bundles `E1.json`–`E4.json` in `reports/comprehension/raw/oracle_1a/`,
  sha256s pinned in `COUNCIL_1.md`. Live `sections.word_count` sums:
  Personality 42,533 / Appearance 14,180 / Overview 18,357 / Trivia 25,012 /
  History 17,169 = **117,251** — flow.md:243's "~106,000" matches neither the
  plan's own list (42,533+14,180+16,731+15,887+11,595 = 100,926) nor the live
  store.
- **why the step cannot proceed as written:** the 1C rule (flow.md:171-178)
  makes E1–E4 passing mean Personality is a retrieval problem — ~42,533 words
  leave the build list — and Phase 5's own gate (oracle evidence that
  retrieval does not serve the sections) is unmet, so the phase "may not
  exist" and closes in full. The other four families (74,718 live words)
  leave the build list by the gating condition, not by section-specific
  evidence (`COUNCIL_1.md`, P14).
- **what is now blocked:** nothing. Phase 5 does not open.
- **what would unblock it:** a future phase needing any of the five section
  families must bring its own oracle evidence (a new ORACLE_v2 item,
  council-approved).

---

## Pending owner decisions (not halts — a decision, not an action taken)

## 4C — re-anchor pending owner approval (recorded at the 1C gate, 2026-09-05)

- **as written:** flow.md:226: "4C — GATE. Oracle B-group re-run; B1 and B2
  must move."
- **why it goes stale:** after 1A, B1 is already green (the cross-page state
  fact is reachable through the plain ranked beam); after the 2-prep
  fact-floor fix, B2 is expected green. "B1 and B2 must move" would then be
  vacuous, and the B-group would no longer size the state-over-time gap
  (it measures reachability of *static* state facts, not a time index).
- **proposed re-anchor** (P26, round-2 reviewer R3): 4C = B-group **holds**
  (no regression) + the interval state table is non-empty and cited by
  `/context`; any true time-indexed-state probe is a new ORACLE_v2 item,
  council-approved. ORACLE_v1 stays frozen and is never edited.
- **status:** PENDING OWNER DECISION — out of council authority
  (flow.md:78 condition 7: a decision only the owner can make). Apply at 4C
  if approved; the gate as written stands until then.
