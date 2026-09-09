# iter-1 R-5 relations-mode — relations-bank sweep + re-pin + meter (raw)

Window: 2026-09-09 23:18–23:50Z. Model-free sweep legs (SQLite read-only +
in-process regex, no model load, GPU unchanged at the Qwen-only 25,053 MiB);
meter legs over `:8000` (CUDA, bge-large + bge-reranker).

## Sweep (tools: /tmp/csm_iter1_records/sweep_relations_bank.py)

Banks: `questions/*.json` official + `_`-prefixed page batches (sidecars
`_*.coverage.json` / `_*.verify.json` excluded) + `scriptengine/eval/gold_*.json`
= 43,441 items. Item shape: `{id, kind, question, subject, expect_mode, scope,
answer}`; pin source = structured `expect_mode`.

PRE-amendment trigger (router.py:475 as committed, 5 alternatives):

| alt | fired |
|---|---|
| alt1_relationship | 123 |
| alt2_how_related | 1 |
| alt3_how_relate | 0 |
| alt4_connection | 20 |
| alt5_who_x_to | 89 |
| **total** | **233** |

re-bind debt (fired, pin != relations): **222** (matches rev-2's ~222).
Empty-pair firings (pair extracted, 0 `facts.db` rows): **77** (name-only
match; alias-inherited rows are R-6, so some are false halts — D's halt-risk set).
Official + eval banks: 0 hits (the trigger is batch-bank-only as committed).

POST-amendment trigger (A1–A5 applied):

- total fired: **79** (0 new hits in official + eval banks — verified)
- per-alt: alt1 (tightened) + alt2/alt3 + tightened who-branch; `\bconnection\b`
  and the who-branch verb-phrase over-captures removed
- re-bind debt after re-pin: **0** (see below)
- empty-pair firings: **39** (residual D halt-risk set, all answer via the
  relations→qa empty fallback, A3/A4)

Re-pin (council Residual 4, deterministic list from the post-amendment sweep):
**68 rows / 25 `_`-batch files** re-pinned `expect_mode: relations`
(39 qa + 29 roster). One row (`_jjk_page_paraphrase_r6.json`) needed a
prefix-match re-pin (sweep extraction had truncated the text at 100 chars);
BOM preserved on 12 of the 25 files.

Post re-pin: fired = 79, all 79 pinned `relations` (11 probe rows + 68 re-pins).

## R-5 meter (tools/csm/validate_relations.py, over :8000, 2026-09-09 23:43Z)

**5/11 complete** (gate bar for this wave: ≥1 HIT off 0/11 — MET). The tool's
strict exit (every row complete) = RC 1, explained per row:

| row | result | missing | class |
|---|---|---|---|
| csm-rel-01 Aki Hayakawa | 5/6 | Angel Devil | budget-trim |
| csm-rel-02 Asa Mitaka | 3/5 | Barem Bridge, Yuko | budget-trim |
| csm-rel-03 Chocolate | 1/2 | Denji | **content gap** (1 relation row in store) |
| csm-rel-04 Death Devil | 6/7 | Miri Sugo | budget-trim |
| csm-rel-05 Denji | 4/12 | 8 names | budget-trim (proven below) |
| csm-rel-06 Famine Devil | 3/3 | — | HIT |
| csm-rel-07 Himeno | 4/4 | — | HIT |
| csm-rel-08 Makima | 3/3 | — | HIT |
| csm-rel-09 Meowy | 1/1 | — | HIT |
| csm-rel-10 Power | 4/4 | — | HIT |
| csm-rel-14 Yoru | 3/5 | Death Devil, Famine Devil | budget-trim |

**Budget-trim class (5 rows):** the meter's `/context` call runs at a small
default `token_budget`; the budgeted relations builder (A2-fixed, correct
token units) trims the ranked tail. Proven with csm-rel-05: `POST /context
{query: "Every documented relationship of Denji", mode: relations,
token_budget: 60000}` → **208 rows, all 12 expected names present**
(7,769 tokens used). `facts.db` holds 168 Denji relation rows, so no content
is missing — the harness budget is. Fixing the harness's budget is
meter-side, not the R-5 fix class; noted for the close council.

**Content-gap class (csm-rel-03):** `facts.db` holds exactly 1 Chocolate
relation row; the Chocolate–Denji relation is not extracted. Phase-2
extraction territory (not R-5's fix class).

Raw: /tmp/w2_r5meter.log; sweep raws /tmp/csm_iter1_records/sweep_relations_bank_
{PRE_amend,out}.txt; re-pin list /tmp/csm_iter1_records/repin_68.json.