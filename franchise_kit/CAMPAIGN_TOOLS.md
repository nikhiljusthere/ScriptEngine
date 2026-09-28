# Campaign tools: what to reuse for the next franchise

The Marvel campaign built its tooling under `tools/marvel/`. Most of it is franchise-generic in *function* but carries Marvel paths or defaults. **The rule for the next franchise:** before first use, promote a tool to `tools/franchise/<tool>.py`:
- a required `--series`;
- paths derived as `reports/<series>/…` and `series/<series>/…`;
- no hard-coded series names;
- the Marvel copy left alone until the Marvel campaign closes (its receipts reference those paths).

Engine code never moves here. These are thin CLIs around `scriptengine`.

"Hard-wired" = count of `marvel`/`mcu` mentions (measured 2026-09-28).

## Reuse (generic function; promote with `--series`)

| tool | phase | what it does | hard-wired | promotion note |
|---|---|---|---:|---|
| `run_d3_sweep.sh` | D3 | 3-door tier-1 sweep supervisor: per-door sanity-100 gate, idempotent resume, `DOORS`/`WORKERS`/`TAG`/`SCRIPTENGINE_API_BASE` knobs | 6 | parameterize `PANEL`, `HASH8`, `PANEL_SIZE`, the ledger dir |
| `d3_monitor.py` | D3 | localhost browser monitor: per-door progress, s/probe, ETA, verdict mix, stack health, recent misses, supervisor logs | 5 | take `--series --panel-hash --panel-size` |
| `census_c6.py` | C6 | question bank + census + OOS freeze/score (CSM method) | 3 | already takes `--series` |
| `blind_panel.py` | D2 | sealed blind panel → validate → freeze → score. **Its test reads `date.today()` (fails any day but the seal day)**: pin the date when promoting | 8 | also fix the date defect |
| `parse_diff.py` | A gates 4/6 | base-parser vs new-parser extraction diff | 8 | takes `--series` |
| `title_drift_audit.py` | A (F2/F3) | zero-egress title drift + collision audit | 10 | takes `--series` |
| `recentchanges_delta.py` | A (S3) | delta-only re-enumeration (the owner's permanent rule) | 12 | takes `--series` |
| `revid_backfill.py`, `revid_spotcheck.py` | A (S1) | revid stamping + live spot-check | 10 / 5 | new crawls stamp revids natively (`rvprop=ids|content`), so backfill is only for legacy corpora |
| `fixlist_fetch.py`, `shard_fetch.py`, `make_shards.py`, `enumerate_pages.py` | A | fixed-list / sharded fetch, parallel enumeration | 5–9 | generic; note that Fandom rejects `list=allpageswithprefix` |
| `link_artifact_scan.py` | C1 | raw-wikitext / URL residue in generated golds | 6 | takes `--series` |
| `merge_sweep_shards.py`, `run_sweep_shards.sh` | C1/C6 | sharded page-sweep + merge | 1–3 | generic |
| `unknown_residue.py`, `d1_exclusions.py`, `d2_depth_floors.py`, `d3_red_list.py` | GATE C | residue report, D1 exclusion ledger, depth floors, red list | 11–67 | heaviest Marvel wiring; rewrite around `--series` + the plan's denominators |
| `egress_watchdog.sh`, `live_monitor.py` | A | long egress batch orchestration + monitor | 32 / 19 | only for throttled wikis; rotation policy per plan §1a |
| `batch_probe_ua.py`, `c2_diag.py` | A | WAF user-agent discrimination probe; asyncio task-dump stall diagnosis | 0 / 5 | keep as diagnostics |

## Marvel-specific (do not reuse as-is)

`cc_catalog_b0.py`, `cc_b1_pilot.py` (the Marvel CC/SDH corpus) · `export_fetch.py` + `reconcile.py` (source-B cross-check; reuse only if a wiki needs an independent source) · `reemit_f7.py` (one parser fix's re-emit) · `gate5_pick.py` · `post_sweep_chain.sh` (the Marvel GATE C chain; its *shape* is the template) · `netns_*` (a retired home-line experiment) · the `*.jsonl` fix lists.

## New, franchise-generic from day one

- `franchise_kit/tools/survey_wiki.py`: the structure survey (Phase S). Model-free, read-only, ~2 s on MCU and ~8 s on Marvel's 2.7 GB store.
