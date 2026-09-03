# Canon run 2026-09-01-0645

32 set questions and 23 fact questions over 1 series, asked of the live server and scored against `questions/`.

## Headline

| | |
|---|---:|
| **answered exactly right** | **23/29** (79.3%) (+29.3%) |
| canon items recovered | **224/238** (94.1%) (+17.8%) |
| precision, closed sets | **90.0%** over 29/32 questions (+8.9%) |
| questions at recall 0 | 0/32 |
| questions at recall >= 0.8 | 31/32 |
| confident and wrong | **1** |
| fact answers present in the bundle | 22/23 |
| members returned | 250 |

> **The bank changed between these two runs.** Canon grew from 237 to 238 items (+1), so the deltas above are *not* a clean measurement of the engine: part of any move belongs to the target. A correction that adds a name the engine was already returning raises precision without the retriever changing at all. Compare engine changes only across runs whose canon total matches.

**Comparable subset.** The 5 questions carried over from the 2026-08-04 gold set score **21/29** (72.4%). The bank grew underneath every other number here, and the questions added since deliberately target known weak spots, so a lower headline is the expected and more honest result.

This subset is comparable with earlier runs *only* while its own 29 items are unchanged. The 2026-08-14 bank audit corrected questions inside it -- adding names the wiki documents and the bank had omitted, and aliases for names it had spelled differently -- so its denominator has moved and this figure is no longer a like-for-like comparison with the pre-migration 162/217 (74.7%). It remains a fixed set of *questions*; it is no longer a fixed set of *items*.

## What the engine gets wrong

Ordered by what reaches a script. A confidently wrong answer is first because the engine gives a caller no reason to check it; a visibly thin one gets checked.

| | series | question | canon | found | recall | engine said | missing |
|---|---|---|---:|---:|---:|---|---|
| **confident and wrong** | `jjk` | Every cursed technique of Yuta Okkotsu | 9 | 1 | 11.1% | `declared` | Cursed Speech, Dhruv Lakdawalla's Shikigami Technique, Sky Manipulation, Technique Extinguishment, G Warstaff, Shrine, +2 more |

### Fact answers not present in what was served

The engine serves context rather than an answer sentence, so the claim here is only that the correct answer was **not present in the bundle** -- a writer had nothing to write the line from.

| series | question | expected | intruders present |
|---|---|---|---|
| `jjk` | How many rank classifications are in the jujutsu sorcerer grading system? | 8 rank classifications | - |

## Why each miss is missing

Assigned by a lookup against the store, not by eye.

| bucket | count | share | the fix lives in |
|---|---:|---:|---|
| retrieval gap | 11 | 79% | `scriptengine/retrieve/` |
| extraction gap | 2 | 14% | `scriptengine/ingest/abilities.py` |
| corpus gap | 1 | 7% | `a crawl, or nothing` |

## What to do about it

In order of items recovered per unit of effort.

1. **retrieval gap, 11 items.** Already in the store and still not returned -- the retriever had every chance. Trace one query end to end before writing code; the diagnosis names the row it expected to find.
   Fix lives in `scriptengine/retrieve/`.
   Biggest cluster: Every cursed technique of Yuta Okkotsu (7 items).

2. **extraction gap, 2 items.** The prose names it and the extraction pass did not return it. Fix the prompt and bump PROMPT_VERSION, or the cached answers survive the change.
   Fix lives in `scriptengine/ingest/abilities.py`.
   Biggest cluster: Every ability of Satoru Gojo (1 items).

3. **corpus gap, 1 items.** Not in the subject's prose at all. Check the crawl is not stale for that page; if it is current, the wiki does not support the claim and a script must not make it.
   Fix lives in `a crawl, or nothing`.
   Biggest cluster: Every cursed technique of Yuta Okkotsu (1 items).

## Padded rosters

Closed sets where the engine returned more than twice the canon count. This is the measured defect: recall is respectable and a caller still cannot use the answer, because the right names arrive buried in wrong ones. Roadmap phases 20 (current vs former member) and 21 (a set the wiki barely fills) are the two named causes.

| series | question | canon | returned | ratio | precision |
|---|---|---:|---:|---:|---:|
| `jjk` | What are Satoru Gojo's named cursed techniques? | 1 | 5 | 5x | 20.0% |
| `jjk` | What are Yuji Itadori's named cursed techniques? | 2 | 8 | 4x | 25.0% |
| `jjk` | Every cursed technique of Sukuna | 2 | 5 | 2x | 40.0% |
| `jjk` | What are Sukuna's named cursed techniques? | 2 | 5 | 2x | 40.0% |

## Where the wrong names come from

Every one of the 16 members returned on a closed set that matched no canon item, by the candidate path that vouched for it. `recall_only` questions are excluded: their gold is a curated core list, so a name outside it is usually right.

| source | count | share | what it means |
|---|---:|---:|---|
| prose row | 14 | 88% | Extracted from prose at index time. Skips `validate_member` by design; filtered only by `ability_stopwords` and a word count. The section it came from is the lever. |
| ownership edge | 2 | 12% | The wiki wrote `X -user-> Y`. The only path already validated, and correspondingly the smallest. |

**12 (75%) are vouched for by one path only**, against 4 backed by more than one. Corroboration is the signal the union discards when it deduplicates on lowercased name alone. 0 (0%) are lead-level rows: the section they were extracted from is the bare page title, so they came from the article's opening rather than from any heading.

Sections supplying the most wrong names, from `abilities.section`, the breadcrumb each row was read from.

Worth knowing before acting on this table: `ability_sections` in `series/<name>/overrides.yaml` does **not** filter these. In `scriptengine/retrieve/` it is read in exactly one place (`roster.py:1208`, inside `_section_roster`), so it selects *headings*; `_extracted_roster` never consults it, and prose rows are the majority of what is listed here. Its other reader is `ingest/abilities.py`, which uses it to choose what to extract, so narrowing it there shrinks the next extraction rather than filtering what is already stored. Acting on this table at query time means a section filter in `_extracted_roster`, which is code and needs a server restart, though not a re-extraction.

| count | section |
|---:|---|
| 5 | `Abilities and Powers / Cursed Restrictions` |
| 4 | `Abilities and Powers / Cursed Techniques` |
| 2 | `Abilities and Powers / Cursed Technique` |
| 1 | `Abilities and Powers / Intelligence` |
| 1 | `Abilities and Powers / Physical Prowess` |
| 1 | `Cursed Technique Lapse: Blue / Related Techniques` |

## Offline regression suite

A different measurement: `gold_*.json` checked against the crawl, in-process, boolean. It gates the build; this report does not.

| series | score |
|---|---|
| `jjk` | n/a (--skip-eval) |

## Reproducing

```powershell
python start_scriptengine.py          # the server must be up
python -m scriptengine.cli canon-run
```

The server holds its code in memory, so restart it after any change under `scriptengine/` or the run measures the old code. `canon-run` refuses to start against a server older than the newest source file, because one earlier measurement was taken that way and reported no change from a fix that had worked.

Run metadata: `2026-09-01-0645`, git `9fbf9f3`, server started `2026-09-01T06:35:04+00:00`, 48s wall clock.

Sources for every answer are in `questions/<series>.json`, per item.
