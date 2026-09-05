# HANDOFF — continuity-check scaffold (D6 consumer)

Checkpoint written mid-session, 2026-09-05, after a power loss aborted the
full-suite run. Everything below is on disk and verified unless marked
PENDING. Read this first, then "Resume steps".

## What the scaffold is

The placement-signal fix (GATE.md:217) named an owner for the 116
generic-heading residual rows: **the continuity-check consumer**. This is that
consumer, shipped as a **validation-layer scaffold** per the plan: a gap is a
*flag, not a verdict* — it names a beat that references an event out of order
and leaves the flashback/recap call to the writer. Model-free (reads `events` +
cross-page majority only). Design record: `reports/comprehension/COUNCIL_continuity-check.md`
(5 advisors + 5 peer reviews + verified ledger; direction split 9 premature +
22 delayed recorded).

## What is done (on disk, verified)

| artifact | status |
|---|---|
| `scriptengine/ingest/continuity.py` | **written + tested**. Functions: `adjudicated_arc` (cross-page majority = the wiki's own truth, disputed flag on tie), `beat_gap` (the core subtraction: claimed vs adjudicated arc, direction, flag at gap≥2), `walk_monotonicity` (backward-jump flags, flashback exemption), `knowledge_frontier` (subject-scoped prefix read, subject-OR-object, `arc_index<=n`), `triage_filings` (107 → class split + direction split + span histogram), `run_gold` (frozen set check). `_STATE_VERBS = frozenset({"arrived","departed"})`. Sibling of `gate.py`, no model. |
| `scriptengine/eval/gold_continuity.json` | **generated** (20 cases, top draw of the 31 interaction-verb filings, sorted by `(-gap, majority_share, participants[0])`). Regenerable: `PYTHONPATH=. scriptengine/.venv/bin/python /tmp/opencode/gen_gold.py` (script may have been lost in the power loss; the JSON artifact itself is in the repo and is the source of truth). |
| `scriptengine/cli.py` | **`continuity` command added** (inserted between `comprehension-gate` and `link`, ~line 875): `--series` (required), `--subject` + `--upto N` (frontier), `--triage` (class split + histogram), `--gold/--no-gold` (default on, runs the frozen set), `--limit N`. One rich-markup bug found + fixed (mismatched `[/dim]` in the triage print). |
| `tests/test_continuity.py` | **written, 19/19 passing** (0.61 s). Covers: `_participant_match` (both orderings, 5 placeholders), `adjudicated_arc` (Sukuna/Yuji majority, nonexistent→None, share bounds), `beat_gap` (premature flagged early, gap 0 not flagged, unplaced→None), `walk_monotonicity` (forward clean, back-jump flagged jump=4, flashback reported not hidden, within-threshold not a jump), `knowledge_frontier` (prefix read, grows with arc), `triage_filings` (classes partition total, core=prem+delay, state-verbs absent from core), `run_gold` (all 20 hold live; a doctored case breaks exactly one). |
| `reports/comprehension/COUNCIL_continuity-check.md` | **written + amended** (direction split 9+22; bouncer 31≥20 either-direction; premature-only=9 thin signal; minimal runnable path). |

### Measured numbers (JJK, post placement-signal fix; do not re-measure)

- **107 cross-arc filings = 26 adjacent** (span=1 boundary straddle) **+ 50
  state-verb** (arrived 30 + departed 20, coarse keying) **+ 31 interaction-verb**
  (fought 12 + saved 10 + killed 5 + awakened 4).
- **31 = 9 premature (early) + 22 delayed (late); 0 both.** Bouncer "twenty real
  failures": 31 ≥ 20 → **passes** either-direction. The literal what-X-knew
  (premature-only) subset is **9 < 20 — an honest thin signal, recorded, not
  dodged.**
- **62 `modeling_problem`** (group ≥4, majority <0.8) — recorded, not auto-fixed.
- **Span histogram:** 1:26, 2:17, 3:8, 4:5, 5:10, 6:11, 7:17, 8:13.
- **Frontier:** Yuji Itadori → **386** events ≤ arc 7, **298** ≤ arc 6, **447** total.
- **Gold:** 20/20 hold against the live store (verified via CLI + test).
- **Non-circular:** "actual" arc = the wiki's own cross-page majority filing,
  independent of `events.arc_index` (the axis under test). `chapter_arc_index`
  reads the `facts` table (timeaxis.py:183), not `events.arc_index`.
- DB state: 2,748 events, 2,594 placed / 154 NULL (unchanged by this scaffold).

## What is PENDING (power loss aborted here)

1. **Full-suite count unverified.** Last known green total was **1,175** (placement-signal
   section). 1,175 + 19 new = **expect 1,194**. The run was aborted mid-suite by
   the outage.
2. **`GATE.md` continuity-check section NOT yet written** (see "Exact GATE.md
   section text" below — paste + adjust gate numbers after re-runs).
3. **Standing gates NOT re-run** since the CLI/module landed:
   - `eval --series jjk` (expect 24/24)
   - `span-recall --series jjk` (expect 48,570/48,572, rc=2, the known 2 misses)
   - `canon-run --series opm` (expect 10/16 · 236/236 · 79.0%). **May need the
     `:8000` API up** (GPU reranker) — per GATE.md, the API was stopped for pytest
     and relaunched for canon-run; check `curl -s localhost:8000/health` first.
     If Qwen holds the GPU, run the API on CPU: `SCRIPTENGINE_DEVICE=cpu setsid
     nohup python -m scriptengine.api.main > /tmp/scriptengine_api.log 2>&1
     < /dev/null &`.
4. **NOT committed.** Staging list (named paths only, author
   `nikhiljusthere <nikhil.shrivastava003@gmail.com>`, branch
   `character-scoped-questions`, no push):
   ```
   scriptengine/ingest/continuity.py
   scriptengine/eval/gold_continuity.json
   scriptengine/cli.py
   tests/test_continuity.py
   reports/comprehension/COUNCIL_continuity-check.md
   reports/comprehension/GATE.md
   reports/comprehension/HANDOFF_continuity-scaffold.md
   ```
   Message: `comprehension: continuity-check scaffold (gap detector, triage, frontier, frozen gold)`

## Resume steps (in order)

1. `git status` in `/home/goblin/ScriptEngine` — confirm the seven paths above
   are the only changes (plus nothing unexpected; `series/` is gitignored).
2. `cd /home/goblin/ScriptEngine && scriptengine/.venv/bin/python -m pytest
   tests/ -q` → expect **1,194 passed**. If not, fix before proceeding.
3. Write the GATE.md section (text below) into `reports/comprehension/GATE.md`
   between "Placement-signal fix (complete)" and "## Commands"; add the
   `continuity` commands to the Commands block; refresh the "Standing gates"
   table's pytest row with the real count.
4. Run the three standing gates (step 3 of PENDING); record actual numbers.
5. Commit the seven paths with the message above.
6. After commit: this handoff is done; next last-bucket todo is the
   **3b follow-ups** (scope-shrink check, queued FK / re-extract fix) and the
   **cross-corpus Phase plan** (`Plan_to_perfection.md` §7, Wave 0 reachability
   pre-pass: 20,655 unreachable lines across the other 7 wikis).

## Exact GATE.md section text (paste, then adjust numbers)

```markdown
## Continuity-check scaffold (D6 consumer, shipped)

The placement-signal fix named an owner of the 116 generic-heading rows above:
the continuity-check consumer. This section is that consumer, shipped as a
scaffold — a **validation layer, not a rejector**. A gap is a *flag, not a
verdict*: it names a beat that references an event out of order (three arcs
early, or a filing two arcs off the wiki's own cross-page majority) and leaves
the flashback/recap call to the writer. Model-free. Design record:
`COUNCIL_continuity-check.md`.

Ships with: `scriptengine/ingest/continuity.py` (`adjudicated_arc`, `beat_gap`,
`walk_monotonicity`, `knowledge_frontier`, `triage_filings`, `run_gold`);
`scriptengine/eval/gold_continuity.json` (frozen top-20 draw of the 31
interaction-verb filings); the `continuity` CLI door; 19 tests.

**Measured on JJK (post placement-signal fix).** The 107 cross-arc filings
triage as: **26 adjacent** (span=1 boundary straddle, not anachronisms),
**50 state-verb** (arrived 30 + departed 20 — a coarse `(verb, participant)`
keying problem, not a wiki contradiction), **31 interaction-verb** (fought 12 +
saved 10 + killed 5 + awakened 4). The 31 is the anachronism core, split
**9 premature + 22 delayed** (0 both). The plan's "twenty real failures"
bouncer passes either-direction (31 ≥ 20); the literal what-X-knew subset is
the 9 premature — an honest thin signal, recorded, not rephased away. 62
filings are `modeling_problem` (group ≥4, majority <0.8) — recorded, not
auto-fixed. Span histogram: 1:26, 2:17, 3:8, 4:5, 5:10, 6:11, 7:17, 8:13.
Knowledge frontier: Yuji Itadori → 386 events ≤ arc 7 (298 ≤ arc 6; 447 total).
The frozen gold set holds 20/20 against the live store.

**Non-circular by construction.** The "actual" arc a gap is measured against is
the wiki's own cross-page majority filing — a corpus truth, independent of the
`events.arc_index` axis under test (`chapter_arc_index` reads the `facts`
table, timeaxis.py:183). A re-index that silently moved an event breaks a gold
case and is caught by `tests/test_continuity.py`.

**Hazards / hand-off.** The 50 state-verb and 26 adjacent filings are excluded
from the core (keying + boundary straddles, not anachronisms). The 116
generic-heading placement residual is owned by this consumer's **write-layer
(D6)** — not yet built. The real *script-line* harvest is deferred:
`scripts output/` is thin (no per-beat `sourced:` headers yet), so the gold set
is corpus-derived (the 31 filings), not harvested script lines.
```

## Commands (for the resume session)

```
cd /home/goblin/ScriptEngine
scriptengine/.venv/bin/python -m scriptengine.cli continuity --series jjk --triage
scriptengine/.venv/bin/python -m scriptengine.cli continuity --series jjk --subject "Yuji Itadori" --upto 7 --limit 6
scriptengine/.venv/bin/python -m scriptengine.cli eval --series jjk
scriptengine/.venv/bin/python -m scriptengine.cli span-recall --series jjk
scriptengine/.venv/bin/python -m scriptengine.cli canon-run --series opm
```

## Standing constraints (unchanged)

- Branch `character-scoped-questions`; worktree `worktree-plan-to-perfection`.
- Python: `scriptengine/.venv/bin/python`; scripts from `/tmp` need
  `PYTHONPATH=/home/goblin/ScriptEngine`. ~120 s shell cap; no bare `sleep`.
- Qwen owns the GPU (24.6/32 GB); the `:8000` reranker OOMs it — stop the API
  or run it on CPU (`SCRIPTENGINE_DEVICE=cpu`) before heavy GPU work.
- Commit: named paths only, author `nikhiljusthere`, prefix `comprehension:`,
  no push. `series/` is gitignored.