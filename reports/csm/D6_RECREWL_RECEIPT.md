# D6 pre-window: 2-page re-crawl receipt (Yoru + Asa Mitaka)

**When:** 2026-09-18 (pre-window chain step 1 of GATE.md L736–737).
**Why:** both census CONTENT rows are extraction-gated on these two pages, and
both were edited on the live wiki after the 2026-08-16 crawl (Yoru revid 44672,
2026-09-10; Asa Mitaka revid 44657, 2026-09-04 — live-verified). Stale wikitext
would leave `csm-dim-abl-01` / `csm-dim-caus-03` gated on pre-edit content.

## What ran

`tools/recrawl_pages.py` (new, untracked) — mirrors the `crawl` worker path
(`list_templates` → `build_ontology` → `fetch_batch` → `build_page` →
`_learn_labels` → skip checks → JSON write), so the refreshed pages are
byte-equivalent to what a full crawl would produce. No new crawl-CLI flag
(out of D6 scope); no `--refresh` (537-page diff surface); no resume (disk
glob would skip the on-disk pages).

```
scriptengine/.venv/bin/python tools/recrawl_pages.py --series csm \
  --start-url https://chainsaw-man.fandom.com/wiki/Chainsaw_Man Yoru "Asa Mitaka"
```

## Root-cause fix found on the way (shared `crawler.py`)

First run failed with HTTP 403 from Fandom's edge on every request. Isolated
by probing: the WAF 403s on the `Accept: application/json` request header
(present + 403 / absent + 200, all else equal — UA and Accept-Language are
fine). The header is functionally redundant (response format is pinned by the
`format=json` parameter), so it was **removed from `WikiCrawler._get`**
(`scriptengine/ingest/crawler.py`, comment records the 2026-09-18 verification).
This un-breaks all Fandom crawling, not just this re-crawl. No series name in
the fix; JJK on-disk index untouched.

## Results

| title | status | wikitext_changed | sections | fetched_at |
|---|---|---|---|---|
| Asa Mitaka | written | true | 20 | 2026-09-18T02:42:03 |
| Yoru | written | true | 24 | 2026-09-18T02:42:03 |

## Invariants preserved (checked, not assumed)

- Corpus-wide `revid: 0` / `facts: 0` / mostly `page_type: unknown` (479/537)
  are the **original crawl's** shape (verified on untouched `Denji.json` and
  all 537 files) — the re-crawl preserves them, it did not introduce them.
  The earlier expectation that refreshed JSONs would carry live revids was
  wrong: `build_page` never populated `revid` for any series.
- Exactly 2 files carry the 2026-09-18 `fetched_at`; the other 535 are
  byte-untouched (only `fetched_at`/`wikitext`-bearing fields of the two
  changed files differ).
- Same key set as every other corpus file (18 keys).

## Next (pre-window chain)

CSM `audit` → `index` (CUDA, Qwen 100k co-location) → **zero-regression
receipt**: post-index structured counts must match the pre-index baseline
(relations 748 / abilities 376 / aliases 1079 in `series/csm/facts.db`); any
delta must be explainable by the two refreshed pages alone. Then: frozen
P/T/A triage + `--pages` list → CSM dry-run equivalence receipt → 30-row +
200-row set freeze → pre-extraction OOS + 134 setrel page-run baselines →
GPU window.