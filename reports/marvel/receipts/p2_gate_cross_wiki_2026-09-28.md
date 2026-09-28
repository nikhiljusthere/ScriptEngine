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
| csm | 537 | 5,081 | 5,081 | +0.00% | no |
| opm | 1,571 | 14,527 | 14,527 | +0.00% | no |
| bleach | 2,252 | 21,535 | 21,535 | +0.00% | no |
| hxh | 2,018 | 19,475 | 19,475 | +0.00% | no |
| berserk | 762 | 4,670 | 4,670 | +0.00% | no |
| db | 8,052 | 69,634 | 69,634 | +0.00% | no |
| onepiece | 7,613 | 59,823 | 59,823 | +0.00% | no |
| marvel | 236,720 | 3,796,438 | 3,796,438 | +0.00% | no |
| mcu | 35,234 | 126,195 | 126,195 | +0.00% | no |

**Eight series: zero delta, zero type changes** — the hook is a no-op where
nothing is declared, exactly as designed.

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
- `series/mcu/overrides.yaml` — `alias_map: {tony stark: Iron Man}` pin, so
  the merge is deterministic regardless of the harvest count.
- `tests/test_alias_merge.py` — 8 tests green (resolver claim rules,
  chunk-entity re-pointing, the Iron Man corpus case, legacy fallback).
- Dry-run census (`p2b_tony_stark_repair.py --dry-run`): discard 382 edges /
  3,102 chunk_nodes (duplicates of the Iron Man node), re-point 2,615 edges /
  10,202 chunk_nodes, delete node 35256 + its 1 alias row.

**Store is mutated only by a re-index after the gates pass** — the index
rebuilds `facts.db` from wikitext, so any hand edit would be wiped or would
silently diverge from a rebuild.

## Environmental notes (not regressions)

- `test_blind_panel`: pre-existing date-rot, documented in GATES.md (today's
  panel not yet drawn).
- `test_context`/mcp 500s during the pre-gate suite runs: the `:8000`
  embedder hit a CUDA OOM — `ninfer-serve` (Qwen 27B, 23.5 GB) plus the
  4.3 GB embedder left <5 GB headroom. Environmental VRAM contention;
  passes in isolation. Proof it is not the P2a diff: stash-pop re-run with
  the working tree stashed still shows the same 4 failures.

## Verdict

**P2a adopted** (commit `9a335d40`): gate-clean on all 9 series, the 430+218
mcu type moves are the intended restoration, no fact or key movement.
**P2b staged**: re-index mcu after the four standing gates, then re-run the
P2 diff to confirm the store matches the extraction (the Tony Stark node
must be gone; 35256 absent, Iron Man carrying the `tony stark` alias).