# P2 receipt: cross-wiki type diff for the structural_infoboxes hook (2026-09-28)

`tools/marvel/parse_diff.py` over all 9 series, isolating P2a
(`9a335d40`, the `structural_infoboxes:` override hook + the mcu declaration).

- base: `/tmp/se_p2base` — `e1734229` (post-P4, pre-P2a; its code ignores the
  new overrides key, so the base side is pure pre-P2a typing)
- new:  `/home/goblin/ScriptEngine` at `9a335d40` (P2a engine + mcu
  declaration), extraction at 19:50–20:44
- gate script: `/tmp/se_p2/run_gate_p2.sh`; reports `/tmp/se_p2/*_report.md`

## Result

| series | pages | base facts | new facts | stable delta | blocked |
|---|---:|---:|---:|---:|---|
| jjk | 987 | 10,064 | 10,064 | +0.00% | no |
| csm | 537 | 5,081 | 5,081 | +0.00% | no |
| opm | 1,571 | 14,527 | 14,527 | +0.00% | no |
| bleach | 2,252 | 21,535 | 21,535 | +0.00% | no |
| hxh | 2,018 | 19,475 | 19,475 | +0.00% | no |
| berserk | 762 | 4,670 | 4,670 | +0.00% | no |
| db | 8,052 | 69,634 | 69,634 | +0.00% | no |
| onepiece | 7,613 | 59,823 | 59,823 | +0.00% | no |
| marvel | 236,720 | 3,796,438 | 3,796,438 | +0.00% | no |
| mcu | 35,234 | 126,195 | 126,195 | +0.00% | no |

**Nine series: zero delta, zero type changes** — the hook is a no-op where
nothing is declared, exactly as designed. **jjk (the 100% baseline) is the
first row: 987 pages, 10,064 facts, no type changes, no key loss/gain**
(`/tmp/se_p2/jjk_report.md`, base `/tmp/se_p2/jjk_base.jsonl` vs new
`/tmp/se_p2/jjk_new.jsonl`).

**mcu type changes (all intended, no fact movement):**

| class | rows |
|---|---:|
| list→character | 302 |
| list→war | 53 |
| list→location | 17 |
| list→organization | 15 |
| list→item | 12 |
| list→concept | 6 |
| list→filmmaker | 6 |
| list→race | 6 |
| list→armor | 5 |
| list→project | 5 |
| list→vehicle | 2 |
| list→event | 1 |
| **list→subject total** | **430** |
| list_quote→character_quote | 216 |
| list_quote→item_quote | 2 |

- The 430 match the pre-run census (`/tmp/se_p2/census_mcu_list.out`: 302
  character, 53 war, 17 location, 15 organization, 12 item, 6 filmmaker,
  6 race, 6 concept, 5 project, 5 armor, 2 vehicle, 1 event; 0 unknown)
  exactly.
- The 218 quote rows are the same P2a mechanics on a second wrapper:
  `list_quote` pages whose `Infobox List` wrapper shadowed the subject quote
  box now type from that box (`character_quote`/`item_quote`). Not in the
  script's expected list; inspected — same class, intended, no consumer of
  the `list_quote` type exists (consumer grep clean, same as P4's gallery
  audit).
- **Keys net-lost / gained: none** on every series. The expected "subject
  boxes gain their facts" did not materialise as fact movement: the
  wrapper's facts and the subject box's facts were already both extracted,
  so the delta is purely the type label. Zero is the cleaner outcome for
  the gate.

## P2b (staged, not applied — per architect steer 2026-09-28)

The phantom `Tony Stark` node (35256: 2,997 in-edges, 13,304 chunk links) is
fixed **at index time**, not by store surgery:

- `scriptengine/index/build.py` — a bare name written by edges/chunk entities
  is merged into the page its own evidence points at (link-harvest usage ≥3
  pages, or a page's own alias fields); `chunk_nodes` is re-pointed with
  `(chunk_id, node_id)` dedup; merged names register as aliases.
- **Gate (architect 2026-09-28, after the merge census below):** the
  *inferred* evidence (alias fields + usage ≥3) applies only when the series
  declares `alias_merge: true` in its overrides — default **off**. A merge
  reshapes the graph that drives retrieval, so every wiki opts in on its own
  evidence and the 100% baselines stay byte-identical. An `alias_map` pin is
  a declaration in its own right and always applies.
- `series/mcu/overrides.yaml` — `alias_map: {tony stark: Iron Man}` pin, so
  the merge is deterministic regardless of the harvest count.
- `tests/test_alias_merge.py` — 10 tests green (resolver claim rules, the
  `alias_merge` gate, the multi-claimer abstention, chunk-entity re-pointing,
  the Iron Man corpus case, legacy fallback).

### Per-series merge census (10 stores, architect 2026-09-28)

`/tmp/se_p2/merge_census.py` (copied to `tools/marvel/merge_census.py`),
pre-gate (un-gated heuristic) vs post-gate (the declaration gate):

| series | pages | pre: names merged | pre: edges re-pointed | pre: chunk links re-pointed | pre: stubs absorbed | post-gate merges |
|---|---:|---:|---:|---:|---:|---|
| jjk | 987 | 1,203 | 415 | 2,951 | 26 | **0** |
| csm | 537 | 297 | 141 | 896 | 28 | **0** |
| opm | 1,571 | 717 | 1,761 | 5,602 | 38 | **0** |
| bleach | 2,252 | 1,371 | 10,426 | 122,376 | 380 | **0** |
| hxh | 2,018 | 1,581 | 89 | 1,092 | 49 | **0** |
| berserk | 762 | 169 | 149 | 775 | 9 | **0** |
| db | 7,205 | 3,261 | 2,400 | 12,189 | 225 | **0** |
| onepiece | 7,613 | 4,742 | 6,445 | 31,929 | 591 | **0** |
| marvel | 236,720 | 80,888 | 42,670 | 60,295 | 10,426 | **0** by construction |
| mcu | 35,234 | 5,870 | 34,764 | 168,064 | 438 | **1** — `tony stark` (2,997 edges, 13,304 chunk links) |

- The un-gated heuristic fires on **every** wiki — 1,203 names in jjk alone,
  28 absorbed stub nodes in csm — so per-name justification is infeasible
  and the architect's fallback is adopted: the heuristic is gated behind a
  per-wiki `alias_merge` declaration, default off.
- Post-gate: no baseline wiki declares `alias_merge`, so all 9 non-mcu
  series merge **zero** names / re-point zero edges / absorb zero stubs —
  the stores are byte-identical at the graph level
  (`/tmp/se_p2/census_postgate_9.out`). marvel declares neither `alias_merge`
  nor `alias_map`, so it is zero by construction.
- mcu's only post-gate merge is its declared pin: `tony stark → Iron Man`
  (2,997 edges + 13,304 chunk links re-pointed onto the Iron Man node, which
  already carries the `tony stark` alias). Pre-gate candidates show why the
  gate is needed, not just scale: jjk `"zenin clan" → "Sorcerer Clan"`
  (35 edges) and `"maru" → "Marulu Val Vol Yelvori"` (34 edges) are
  implausible, and db `"funimation" → "Crunchyroll"` (439 edges) confuses
  two rival distributors. Every one of the ~100k candidates across the 10
  stores would need per-name human review, so the heuristic ships off and a
  wiki adopts it only by declaring `alias_merge: true`.
- Dry-run census (`p2b_tony_stark_repair.py --dry-run`): discard 382 edges /
  3,102 chunk_nodes (duplicates of the Iron Man node), re-point 2,615 edges /
  10,202 chunk_nodes, delete node 35256 + its 1 alias row.

**Store is mutated only by a re-index after the gates pass** — the index
rebuilds `facts.db` from wikitext, so any hand edit would be wiped or would
silently diverge from a rebuild.

### Four standing gates (pre-re-index, 2026-09-28 ~21:00)

The architect's pin, all on the gated working tree:

| gate | pin | result |
|---|---|---|
| pytest | 1,397 passed + 2 xpassed + 4 env failed (the 14:27 state) | **4 failed, 1,416 passed, 2 xpassed** (259.6s, `:8000` down) — the 4 are the same env set: 3× `test_mcp_server` (`:8000`-down ValueError, identical wording) + 1× `test_blind_panel` date-rot. Passed = 1,397 + 10 P2b (`test_alias_merge`) + 9 P4b (`test_p4b_facts_only.py`, untracked, separate workstream — collected because it lives in `tests/`) |
| eval jjk | 31/31 | **31/31** (21:1x, `:8000` down, clean GPU) |
| span-recall jjk | 48,572 present / 0 unreachable + 398/400 live probe | **48,572 / 0** offline + **398/400 (99.5%)** live probe (`--probe 400`, `:8000` up; 1 MISS_DOC + 1 MISS_SPAN — the same deterministic misses as the 09-25 baseline) |
| canon opm | 10/16 exact · 236/236 · 79.0% · 0 recall-0 · 0 wrong · 20/20 | **exact** (21:05, fresh `:8000`) |

All four gates match the architect's pin. `:8000` was restarted for the
probe and stopped again afterwards (steady state: down).

- The 21:03 eval showed 29/31 under GPU contention (qwen 23.5 GB + the
  `:8000` embedder 5.2 GB left the in-process reranker CUDA-OOMing); with
  the API down the same run returns 31/31, and both failed questions'
  expected text is present in the store (Kento Nanami chunks 11665/11666)
  — ranking under OOM, not a store or P2b issue.

## Environmental notes (not regressions)

- `test_blind_panel`: pre-existing date-rot, documented in GATES.md (today's
  panel not yet drawn).
- `test_context`/mcp 500s during the pre-gate suite runs: the `:8000`
  embedder hit a CUDA OOM — `ninfer-serve` (Qwen 27B, 23.5 GB) plus the
  4.3 GB embedder left <5 GB headroom. Environmental VRAM contention;
  passes in isolation. Proof it is not the P2a diff: stash-pop re-run with
  the working tree stashed still shows the same 4 failures.

## Verdict

**P2a adopted** (commit `9a335d40`): gate-clean on all 10 series (jjk the
100% baseline added per architect 2026-09-28), the 430+218 mcu type moves
are the intended restoration, no fact or key movement.
**P2b adopted with the declaration gate** (commit `8ee3f0ae` + the
`alias_merge` gate): the merge census over all 10 stores shows the un-gated
heuristic fires everywhere (~100k candidates, several implausible), so the
inferred evidence is gated behind a per-wiki `alias_merge: true` (default
off) and the mcu `alias_map` pin stands alone — baselines byte-identical,
mcu merges exactly `tony stark → Iron Man`. All four standing gates match
their pins on the gated tree, so the mcu (and marvel) re-index is
unblocked; the re-index re-runs this P2 diff afterwards to confirm the
store matches the extraction (the Tony Stark node must be gone; 35256
absent, Iron Man carrying the `tony stark` alias).