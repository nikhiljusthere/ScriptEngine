# JJK VERIFY-7000 — GEN-2 ADDENDUM (2026-10-04, windowing-100 WP5)

Every number in this file is computed by `tools/train/gen2_addendum.py`
on the live JJK store (gen-2 universe 15,005 windows / 15,005 unique ids
0 collapsed), never estimated and never carried over from the
old 4,000/300 grid. `plan/JJK_VERIFY_7000_FINAL.md` (owner's file) is
left as written; where its paths or counts are stale, THIS file is the
corrected source. Re-run the script after any store or id change to
regenerate every number.

## 1. Remaining train-eligible gen-2 windows

```
universe                        15,005
- holdout pages (134)           2,114 windows
- gold (gold600 684 records -> 680 windows, union pilot
   kept/reexpressed 485 -> 484 windows; union 1,156)
- 3 pools (mimo/nemotron/spacebunny)          1,500 windows
= remaining train-eligible                    10,235 windows
    non-empty                                 2,670 (of which rare-verb 589)
    empty                                     7,565
```

Store evidence rows unmapped onto the grid: 1 (the window-level
G1's loud failures -- they are NOT silently attributed to a window).

## 2. Re-read queues (the 35B data phase)

| queue | records | distinct window ids | ids already in a pool | ids in the remaining set |
|---|---|---|---|---|
| gold600 reread | 79 | 79 | 0 | 0 |
| pilot reread | 143 | 143 | 15 | 128 |
| union | 222 | 222 | 15 | 128 |

A reread window that sits in a pool is re-read AS that pool's
verification (no separate queue entry); one that sits in the remaining
set is re-read in place. The reread records' windows are excluded from
the pools only for gold600 (all statuses) -- the pilot's reread windows
were left pool-eligible on purpose (WP3b-2): the 35B re-read owns them.

## 3. Old-grid label sources — WP3 re-key status

The WP3 rule (rekey_gold's council ruling): a record re-keys CLEAN when
its rows keep their adjudicated status on the new grid (status kept or
reexpressed; reexpressed may lose rows whose quotes no single new window
carries -- those rows drop for re-extraction). An empty adjudication
re-keys as `reread` (the 35B re-read owns it); a straddled/mapped-away
record drops whole for re-extraction.

| source | records | re-keyable (kept+reexpressed) | needs re-read (all else) | status detail |
|---|---|---|---|---|
| `v1/train.jsonl` | 4,375 | 2,110 | 2,265 | reread 1,990, straddle 275, unmapped 0, rows_dropped 0 (rows kept/lost 8,528/1) |
| `gold/cand_q6_train.jsonl` | 600 | 0 of 0 mapped (reexpressed 0, rows dropped 0) | 600 | mapped: reread 0, straddle 0, unmapped 0, rows_dropped 0 (rows kept/lost 0/0); + 600 records unmappable (no surviving source) |
| `gold/cand_q6_pilot400.jsonl` | 400 | 26 of 45 mapped (reexpressed 19, rows dropped 0) | 374 | mapped: reread 16, straddle 3, unmapped 0, rows_dropped 0 (rows kept/lost 134/0); + 355 records unmappable (no surviving source) |
| `gold/verifyrow_1000.jsonl` (audit rows, no event rows to re-key) | 400 | window mapping only: 45 of 400 ids found in the surviving old pools | 355 unmapped | audit verdicts re-attach by id where mapped; re-read otherwise |
| `gold/verifyrow_600.jsonl` (audit rows, no event rows to re-key) | 855 | window mapping only: 0 of 855 ids found in the surviving old pools | 855 unmapped | audit verdicts re-attach by id where mapped; re-read otherwise |
| `gold/verifyrow_extra.jsonl` (audit rows, no event rows to re-key) | 741 | window mapping only: 741 of 741 ids found in the surviving old pools | 0 unmapped | audit verdicts re-attach by id where mapped; re-read otherwise |
| `gold/verifyrow_q6_pilot400.jsonl` (audit rows, no event rows to re-key) | 18 | window mapping only: 1 of 18 ids found in the surviving old pools | 17 unmapped | audit verdicts re-attach by id where mapped; re-read otherwise |

Only 1,500 old window ids survive in the old-grid pool files (mimo/nemotron/spacebunny `*.old-grid`); a label record whose old id is not
among them has no surviving (page, section, passage) and must be re-read
from the store. `verifyrow_*` are row-level AUDITS (ok/rule/card, no
event rows): their verdicts re-attach to the re-keyed window by id where
mapped, and re-read otherwise.

## 4. Corrected file paths per VERIFY-7000 phase

| phase | old-grid source (as written in FINAL.md) | corrected gen-2 source |
|---|---|---|
| Phase 0 blind audit | `opencode/mimoP*_windows.jsonl` (10 random windows) | `opencode/{mimo,nemotron,spacebunny}_windows.jsonl` (the 1,500 gen-2 pool windows; audit draws from these) |
| Phase 1 Pool A (3x500, P1-P5 pilots) | `opencode/mimoP*_windows.jsonl`, `*_out.jsonl`, `.*_done` | `opencode/{mimo,nemotron,spacebunny}_windows.jsonl`; the P1-P5 files and done-logs are archived `*.old-grid` (retired grid, frozen evidence) |
| Probes (Guard 1) | `series/jjk/training/golden_probes.jsonl` (20-30, extracted from gold600.jsonl) | `opencode/golden_probes.jsonl` -- 24 probes (20 positive, 1-4 rows each, all 12 verbs, none on a holdout page + 4 earned empties), pool shape plus `expected`; rebuilt by `tools/train/rekey_testgold.py --probes` (old file -> `golden_probes.jsonl.pre-wp3b`) |
| Phase 2 Pool B (Qwen windows) | `gold/cand_q6_train.jsonl` | same file, re-keyed by the WP3 rule on the fly (section 3: the mapped/clean records are consumable; the unmapped 600 need re-reading); `gold/cand_q6_pilot400.jsonl` likewise |
| Phase 3 (v1 subset) | `v1/train.jsonl` | same file (4,375 records); 2,110 re-key clean, 1,990 join the re-read queue, 275 drop for re-extraction |
| Phase 4 empty re-read | "~2,265 windows" (old-grid count) | re-read the re-read queues (section 2: 222 reread windows, 128 in the remaining set) + the 7,565 empty windows of the remaining train-eligible set (section 1) |
| Test scoreboard | `recall_gold_v3/gold_test_v4.json` + `windows_100.json` (100 W-indexed entries) | `recall_gold_v3/gold_test_v4.gen2.json` -- 269 entries keyed by gen-2 window id (100 slice entries -> 269 intersecting windows; `straddle`/`partial` flags; 70 genuine empties); the v4 + windows_100 files stay as the annotation source of truth |
| Gold (train labels) | `gold600/gold600.jsonl` (old ids) | `gold600/gold600.gen2.jsonl` (684 records) + `gold/gold_pilot_all.gen2.jsonl` (628 records) |

## 5. Scorer note -- `eval_extraction.load_gold` (NOT changed here)

`tools/eval_extraction.py` `load_gold` (line 52) does
`sorted(Path(d).glob("gold_test_v*.json"))[-1:]` -- lexicographically that
picks `gold_test_v4.json` OVER `gold_test_v4.gen2.json` ("v4.g" < "v4.j"),
so the scorer still reads the old W-indexed file; and the W-index indirection
(`wins[i]["id"]` via the `windows` key, line 54-59) cannot represent the
gen-2 file's shape at all (its keys ARE the window ids; it has no `windows`
key, and 45/100 entries now span several windows). The exact fix for a later
WP (the planner's call -- this addendum does not touch the scorer):

```python
def load_gold(d):
    files = sorted(Path(d).glob("gold_test_v*.json"),
                    key=lambda p: ("gen2" not in p.name, p.name))[-1:]
    data = json.load(open(files[0]))
    if "gen" in data:  # gen-2 file: keys are the window ids
        return {k: v for k, v in data.items()
                if k not in ("version", "gen", "guideline", "note", "note_gen2")}
    # ... old W-indexed shape: the current indirection, unchanged ...
```

Generated 2026-10-04 17:20 by tools/train/gen2_addendum.py (zero-LLM, deterministic).
