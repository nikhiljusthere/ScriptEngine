# D6 pre-window: CSM re-index + zero-regression receipt

**When:** 2026-09-18 (pre-window chain step 2 of GATE.md L736–737, after
`D6_RECREWL_RECEIPT.md`).
**Why:** the two refreshed pages (Yoru, Asa Mitaka) had to reach the CSM index
before the 30/200-row freezes and the GPU extraction window; and every CSM
engine-side step must leave the structured layer baseline-exact (zero delta on
the declared-fact counts).

## What ran

```
scriptengine/.venv/bin/python -m scriptengine.cli index --series csm
```

on CUDA. Qwen 100k (PID 495401) stayed up for the whole run; the `:8000`
service was stopped first (old PID 745658) because a steady-state index OOMs
with it resident (embedder peak 2.52 GiB vs ~151 MiB free after Qwen's 24.29
GiB pin + :8000's 4.01 GiB). With :8000 down, ~6.8 GiB headroom covered the
embedder+reranker. After the index, `:8000` was restored on CUDA (new PID
788943; health: `device cuda`, bge-large-en-v1.5 / bge-reranker-v2-m3).

## Results

Index status (`series/csm/audit/index.json`):

| documents | sections | nodes | edges | facts | chunks | embedded |
|---|---|---|---|---|---|---|
| 537 | 3,917 | 755 | 11,261 | 5,081 | 7,797 | 5,513 |

Page types: character 175, chapter_box 232, volume_box 26, character_history 22,
music 20, story_arcs_box 14, unknown 14, episode 12, organization 11, and 9
smaller types. All 537 pages resolved to nodes.

## Zero-regression (the gate this step exists for)

Pre-index baseline captured before the run (`/tmp/d6_csm_index_pre.json`),
post-index counts after (`/tmp/d6_csm_index_post.json`):

| table | pre | post | delta |
|---|---|---|---|
| relations | 748 | 748 | 0 |
| abilities | 376 | 376 | 0 |
| aliases | 1,079 | 1,079 | 0 |
| events | no table | no table | n/a |

**Delta 0/0/0 — GREEN.** The two refreshed pages re-parsed into the index
without disturbing any declared fact, so the `--pages` extraction list (whose
CONTENT rows are these two pages) is trustworthy. Qwen verified alive after
the run (`kill -0 495401`; 25,257 MiB used, 100k profile).

## Next (pre-window chain)

Frozen P/T/A triage + actual CSM `--pages` frozen list (22 floor + 42 dim
lever rows) → CSM dry-run equivalence receipt → 30-row + 200-row set freeze
(seeded, disjoint, before any model call) → pre-extraction OOS + 134 page-run
baselines (with `:8000` up) → GPU window (stop `:8000` current PID → dry-run
receipt → `events-extract --pages <list> --workers 2` → index rebuild →
model-unloaded side session (re-grade + 4 JJK gates) → closure council → A20
stamp → restore `:8000`).