# Canon run 2026-09-01-0648

20 set questions and 15 fact questions over 1 series, asked of the live server and scored against `questions/`.

## Headline

| | |
|---|---:|
| **answered exactly right** | **3/14** (21.4%) (-3.6%) |
| canon items recovered | **124/153** (81.0%) (-13.9%) |
| precision, closed sets | **45.3%** over 14/20 questions (-12.3%) |
| questions at recall 0 | 2/20 |
| questions at recall >= 0.8 | 18/20 |
| confident and wrong | **0** |
| fact answers present in the bundle | 15/15 |
| members returned | 1079 |

> **The bank changed between these two runs.** Canon grew from 119 to 153 items (+34), so the deltas above are *not* a clean measurement of the engine: part of any move belongs to the target. A correction that adds a name the engine was already returning raises precision without the retriever changing at all. Compare engine changes only across runs whose canon total matches.

**Comparable subset.** The 8 questions carried over from the 2026-08-04 gold set score **58/62** (93.5%). The bank grew underneath every other number here, and the questions added since deliberately target known weak spots, so a lower headline is the expected and more honest result.

This subset is comparable with earlier runs *only* while its own 62 items are unchanged. The 2026-08-14 bank audit corrected questions inside it -- adding names the wiki documents and the bank had omitted, and aliases for names it had spelled differently -- so its denominator has moved and this figure is no longer a like-for-like comparison with the pre-migration 162/217 (74.7%). It remains a fixed set of *questions*; it is no longer a fixed set of *items*.

## What the engine gets wrong

Ordered by what reaches a script. A confidently wrong answer is first because the engine gives a caller no reason to check it; a visibly thin one gets checked.

| | series | question | canon | found | recall | engine said | missing |
|---|---|---|---:|---:|---:|---|---|
| recall 0 | `db` | How many Gods of Destruction exist across the multiverse? | 15 | 0 | 0.0% | `-` | Beerus (Universe 7), Champa (Universe 6), Belmod (Universe 11), Quitela (Universe 4), Arack (Universe 5), Liquiir (Universe 8), +9 more |
| recall 0 | `db` | Who are the members of Team Universe 7 in the Tournament of Power? | 10 | 0 | 0.0% | `-` | Goku, Vegeta, Gohan, Piccolo, Android 17, Android 18, +4 more |

## Why each miss is missing

Assigned by a lookup against the store, not by eye.

| bucket | count | share | the fix lives in |
|---|---:|---:|---|
| unlinked page | 22 | 76% | `series/<name>/overrides.yaml` |
| corpus gap | 4 | 14% | `a crawl, or nothing` |
| extraction gap | 3 | 10% | `scriptengine/ingest/abilities.py` |

## What to do about it

In order of items recovered per unit of effort.

1. **unlinked page, 22 items.** The page exists and nothing ties it to the subject. This is the wiki's shape, not a retriever bug -- declare the link rather than trying to infer it.
   Fix lives in `series/<name>/overrides.yaml`.
   Biggest cluster: How many Gods of Destruction exist across the multiverse? (12 items).

2. **extraction gap, 3 items.** The prose names it and the extraction pass did not return it. Fix the prompt and bump PROMPT_VERSION, or the cached answers survive the change.
   Fix lives in `scriptengine/ingest/abilities.py`.
   Biggest cluster: Every form of Goku (1 items).

3. **corpus gap, 4 items.** Not in the subject's prose at all. Check the crawl is not stale for that page; if it is current, the wiki does not support the claim and a script must not make it.
   Fix lives in `a crawl, or nothing`.
   Biggest cluster: How many Gods of Destruction exist across the multiverse? (3 items).

## Padded rosters

Closed sets where the engine returned more than twice the canon count. This is the measured defect: recall is respectable and a caller still cannot use the answer, because the right names arrive buried in wrong ones. Roadmap phases 20 (current vs former member) and 21 (a set the wiki barely fills) are the two named causes.

| series | question | canon | returned | ratio | precision |
|---|---|---:|---:|---:|---:|
| `db` | Every form of Cell | 4 | 14 | 4x | 28.6% |
| `db` | Who are the members of the Ginyu Force? | 5 | 17 | 3x | 29.4% |
| `db` | Every form of Gohan | 6 | 20 | 3x | 25.0% |
| `db` | Every form of Trunks | 5 | 15 | 3x | 33.3% |
| `db` | Every form of Goku | 12 | 33 | 3x | 33.3% |
| `db` | Every form of Vegeta | 12 | 25 | 2x | 44.0% |

## Where the wrong names come from

Every one of the 99 members returned on a closed set that matched no canon item, by the candidate path that vouched for it. `recall_only` questions are excluded: their gold is a curated core list, so a name outside it is usually right.

| source | count | share | what it means |
|---|---:|---:|---|
| heading | 43 | 43% | A section heading on the character's page. Also skips `validate_member`; `ability_sections` is what selects these. |
| prose row | 31 | 31% | Extracted from prose at index time. Skips `validate_member` by design; filtered only by `ability_stopwords` and a word count. The section it came from is the lever. |
| ownership edge | 13 | 13% | The wiki wrote `X -user-> Y`. The only path already validated, and correspondingly the smallest. |
| category page | 12 | 12% | Arrived through a category or a declared roster rather than through the character, so the set itself is too broad, rather than the member. |

**67 (68%) are vouched for by one path only**, against 32 backed by more than one. Corroboration is the signal the union discards when it deduplicates on lowercased name alone. 0 (0%) are lead-level rows: the section they were extracted from is the bare page title, so they came from the article's opening rather than from any heading.

Sections supplying the most wrong names, from `abilities.section`, the breadcrumb each row was read from.

Worth knowing before acting on this table: `ability_sections` in `series/<name>/overrides.yaml` does **not** filter these. In `scriptengine/retrieve/` it is read in exactly one place (`roster.py:1208`, inside `_section_roster`), so it selects *headings*; `_extracted_roster` never consults it, and prose rows are the majority of what is listed here. Its other reader is `ingest/abilities.py`, which uses it to choose what to extract, so narrowing it there shrinks the next extraction rather than filtering what is already stored. Acting on this table at query time means a section filter in `_extracted_roster`, which is code and needs a server restart, though not a re-extraction.

| count | section |
|---:|---|
| 16 | `Power / Manga and Anime` |
| 5 | `Abilities / Forms and Transformations / Super Saiyan` |
| 2 | `Abilities / Forms and Transformations / Super Saiyan 3` |
| 2 | `Abilities / Forms and Transformations / Final Form` |
| 1 | `Abilities / Forms and Transformations / Ultimate` |
| 1 | `Abilities / Forms and Transformations / Great Saiyaman` |
| 1 | `Abilities / Forms and Transformations / Beast` |
| 1 | `Abilities / Forms and Transformations / Super Saiyan 2` |
| 1 | `Abilities / Forms and Transformations / Sword of Hope` |
| 1 | `Power / OVAs` |

## Offline regression suite

A different measurement: `gold_*.json` checked against the crawl, in-process, boolean. It gates the build; this report does not.

| series | score |
|---|---|
| `db` | 11/11 |

## Reproducing

```powershell
python start_scriptengine.py          # the server must be up
python -m scriptengine.cli canon-run
```

The server holds its code in memory, so restart it after any change under `scriptengine/` or the run measures the old code. `canon-run` refuses to start against a server older than the newest source file, because one earlier measurement was taken that way and reported no change from a fix that had worked.

Run metadata: `2026-09-01-0648`, git `9fbf9f3`, server started `2026-09-01T06:35:04+00:00`, 93s wall clock.

Sources for every answer are in `questions/<series>.json`, per item.
