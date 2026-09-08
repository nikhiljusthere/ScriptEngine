# Canon run 2026-09-08-1245

21 set questions and 18 fact questions over 1 series, asked of the live server and scored against `questions/`.

## Headline

| | |
|---|---:|
| **answered exactly right** | **11/19** (57.9%) (-4.6%) |
| canon items recovered | **138/148** (93.2%) (-6.8%) |
| precision, closed sets | **81.4%** over 19/21 questions (+2.4%) |
| questions at recall 0 | 2/21 |
| questions at recall >= 0.8 | 19/21 |
| confident and wrong | **0** |
| fact answers present in the bundle | 17/18 |
| members returned | 174 |

> **The bank changed between these two runs.** Canon shrank from 236 to 148 items (-88), so the deltas above are *not* a clean measurement of the engine: part of any move belongs to the target. A correction that adds a name the engine was already returning raises precision without the retriever changing at all. Compare engine changes only across runs whose canon total matches.

**Comparable subset.** The 3 questions carried over from the 2026-08-04 gold set score **20/20** (100.0%). The bank grew underneath every other number here, and the questions added since deliberately target known weak spots, so a lower headline is the expected and more honest result.

This subset is comparable with earlier runs *only* while its own 20 items are unchanged. The 2026-08-14 bank audit corrected questions inside it -- adding names the wiki documents and the bank had omitted, and aliases for names it had spelled differently -- so its denominator has moved and this figure is no longer a like-for-like comparison with the pre-migration 162/217 (74.7%). It remains a fixed set of *questions*; it is no longer a fixed set of *items*.

## What the engine gets wrong

Ordered by what reaches a script. A confidently wrong answer is first because the engine gives a caller no reason to check it; a visibly thin one gets checked.

| | series | question | canon | found | recall | engine said | missing |
|---|---|---|---:|---:|---:|---|---|
| recall 0 | `csm` | How many special divisions exist in Public Safety Devil Hunters? | 5 | 0 | 0.0% | `-` | Tokyo Special Division 1, Tokyo Special Division 4, Tokyo Special Division 5, Tokyo Special Division 6, Tokyo Special Division 7 |
| recall 0 | `csm` | How many members are in the Four Horsemen? | 4 | 0 | 0.0% | `-` | Control Devil (Makima), War Devil (Yoru), Famine Devil, Death Devil |

### Fact answers not present in what was served

The engine serves context rather than an answer sentence, so the claim here is only that the correct answer was **not present in the bundle** -- a writer had nothing to write the line from.

| series | question | expected | intruders present |
|---|---|---|---|
| `csm` | What is Denji's hybrid transformation trigger? | Pulling a cord on his chest | - |

## Why each miss is missing

Assigned by a lookup against the store, not by eye.

| bucket | count | share | the fix lives in |
|---|---:|---:|---|
| unlinked page | 4 | 40% | `series/<name>/overrides.yaml` |
| corpus gap | 3 | 30% | `a crawl, or nothing` |
| retrieval gap | 2 | 20% | `scriptengine/retrieve/` |
| extraction gap | 1 | 10% | `scriptengine/ingest/abilities.py` |

## What to do about it

In order of items recovered per unit of effort.

1. **retrieval gap, 2 items.** Already in the store and still not returned -- the retriever had every chance. Trace one query end to end before writing code; the diagnosis names the row it expected to find.
   Fix lives in `scriptengine/retrieve/`.
   Biggest cluster: How many members are in the Four Horsemen? (2 items).

2. **unlinked page, 4 items.** The page exists and nothing ties it to the subject. This is the wiki's shape, not a retriever bug -- declare the link rather than trying to infer it.
   Fix lives in `series/<name>/overrides.yaml`.
   Biggest cluster: How many special divisions exist in Public Safety Devil Hunters? (2 items).

3. **extraction gap, 1 items.** The prose names it and the extraction pass did not return it. Fix the prompt and bump PROMPT_VERSION, or the cached answers survive the change.
   Fix lives in `scriptengine/ingest/abilities.py`.
   Biggest cluster: Every ability of Makima (1 items).

4. **corpus gap, 3 items.** Not in the subject's prose at all. Check the crawl is not stale for that page; if it is current, the wiki does not support the claim and a script must not make it.
   Fix lives in `a crawl, or nothing`.
   Biggest cluster: How many special divisions exist in Public Safety Devil Hunters? (3 items).

## Where the wrong names come from

Every one of the 24 members returned on a closed set that matched no canon item, by the candidate path that vouched for it. `recall_only` questions are excluded: their gold is a curated core list, so a name outside it is usually right.

| source | count | share | what it means |
|---|---:|---:|---|
| prose row | 10 | 42% | Extracted from prose at index time. Skips `validate_member` by design; filtered only by `ability_stopwords` and a word count. The section it came from is the lever. |
| category page | 9 | 38% | Arrived through a category or a declared roster rather than through the character, so the set itself is too broad, rather than the member. |
| heading | 5 | 21% | A section heading on the character's page. Also skips `validate_member`; `ability_sections` is what selects these. |

**24 (100%) are vouched for by one path only**, against 0 backed by more than one. Corroboration is the signal the union discards when it deduplicates on lowercased name alone. 0 (0%) are lead-level rows: the section they were extracted from is the bare page title, so they came from the article's opening rather than from any heading.

Sections supplying the most wrong names, from `abilities.section`, the breadcrumb each row was read from.

Worth knowing before acting on this table: `ability_sections` in `series/<name>/overrides.yaml` does **not** filter these. In `scriptengine/retrieve/` it is read in exactly one place (`roster.py:1208`, inside `_section_roster`), so it selects *headings*; `_extracted_roster` never consults it, and prose rows are the majority of what is listed here. Its other reader is `ingest/abilities.py`, which uses it to choose what to extract, so narrowing it there shrinks the next extraction rather than filtering what is already stored. Acting on this table at query time means a section filter in `_extracted_roster`, which is code and needs a server restart, though not a re-extraction.

| count | section |
|---:|---|
| 4 | `Abilities / Antemortem Abilities / Devil Contracts` |
| 2 | `Abilities / Hybrid Powers` |
| 2 | `Abilities / Physical Abilities` |
| 1 | `Abilities / Other Abilities` |
| 1 | `Abilities / Antemortem Abilities / Physical Prowess` |

## Offline regression suite

A different measurement: `gold_*.json` checked against the crawl, in-process, boolean. It gates the build; this report does not.

| series | score |
|---|---|
| `csm` | n/a (no gold set) |

## Reproducing

```powershell
python start_scriptengine.py          # the server must be up
python -m scriptengine.cli canon-run
```

The server holds its code in memory, so restart it after any change under `scriptengine/` or the run measures the old code. `canon-run` refuses to start against a server older than the newest source file, because one earlier measurement was taken that way and reported no change from a fix that had worked.

Run metadata: `2026-09-08-1245`, git `fd8bdd0`, server started `2026-09-08T12:38:01+00:00`, 6s wall clock.

Sources for every answer are in `questions/<series>.json`, per item.
