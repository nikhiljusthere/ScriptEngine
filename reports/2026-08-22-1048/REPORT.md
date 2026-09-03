# Canon run 2026-08-22-1048

19 set questions and 20 fact questions over 1 series, asked of the live server and scored against `questions/`.

## Headline

| | |
|---|---:|
| **answered exactly right** | **8/16** (50.0%) (no change) |
| canon items recovered | **235/237** (99.2%) (no change) |
| precision, closed sets | **78.5%** over 16/19 questions (no change) |
| questions at recall 0 | 0/19 |
| questions at recall >= 0.8 | 19/19 |
| confident and wrong | **0** |
| fact answers present in the bundle | 18/20 |
| members returned | 372 |

**Comparable subset.** The 4 questions carried over from the 2026-08-04 gold set score **79/80** (98.8%). The bank grew underneath every other number here, and the questions added since deliberately target known weak spots, so a lower headline is the expected and more honest result.

## What the engine gets wrong

Ordered by what reaches a script. A confidently wrong answer is first because the engine gives a caller no reason to check it; a visibly thin one gets checked.

| | series | question | canon | found | recall | engine said | missing |
|---|---|---|---:|---:|---:|---|---|

### Fact answers not present in what was served

The engine serves context rather than an answer sentence, so the claim here is only that the correct answer was **not present in the bundle** -- a writer had nothing to write the line from.

| series | question | expected | intruders present |
|---|---|---|---|
| `opm` | How many S-Class heroes were there before the Monster Association Arc in One Punch Man? | 17 S-Class heroes | - |
| `opm` | How many members are in the Blizzard Group in One Punch Man? | 38 members | - |

## Why each miss is missing

Assigned by a lookup against the store, not by eye.

| bucket | count | share | the fix lives in |
|---|---:|---:|---|
| retrieval gap | 1 | 50% | `scriptengine/retrieve/` |
| corpus gap | 1 | 50% | `a crawl, or nothing` |

## What to do about it

In order of items recovered per unit of effort.

1. **retrieval gap, 1 items.** Already in the store and still not returned -- the retriever had every chance. Trace one query end to end before writing code; the diagnosis names the row it expected to find.
   Fix lives in `scriptengine/retrieve/`.
   Biggest cluster: Every technique of Speed-o'-Sound Sonic (1 items).

2. **corpus gap, 1 items.** Not in the subject's prose at all. Check the crawl is not stale for that page; if it is current, the wiki does not support the claim and a script must not make it.
   Fix lives in `a crawl, or nothing`.
   Biggest cluster: How many hero classes are in the Hero Association in One Punch Man? (1 items).

## Where the wrong names come from

Every one of the 49 members returned on a closed set that matched no canon item, by the candidate path that vouched for it. `recall_only` questions are excluded: their gold is a curated core list, so a name outside it is usually right.

| source | count | share | what it means |
|---|---:|---:|---|
| prose row | 30 | 61% | Extracted from prose at index time. Skips `validate_member` by design; filtered only by `ability_stopwords` and a word count. The section it came from is the lever. |
| category page | 9 | 18% | Arrived through a category or a declared roster rather than through the character, so the set itself is too broad, rather than the member. |
| ownership edge | 6 | 12% | The wiki wrote `X -user-> Y`. The only path already validated, and correspondingly the smallest. |
| heading | 4 | 8% | A section heading on the character's page. Also skips `validate_member`; `ability_sections` is what selects these. |

**45 (92%) are vouched for by one path only**, against 4 backed by more than one. Corroboration is the signal the union discards when it deduplicates on lowercased name alone. 3 (6%) are lead-level rows: the section they were extracted from is the bare page title, so they came from the article's opening rather than from any heading.

Sections supplying the most wrong names, from `abilities.section`, the breadcrumb each row was read from.

Worth knowing before acting on this table: `ability_sections` in `series/<name>/overrides.yaml` does **not** filter these. In `scriptengine/retrieve/` it is read in exactly one place (`roster.py:1208`, inside `_section_roster`), so it selects *headings*; `_extracted_roster` never consults it, and prose rows are the majority of what is listed here. Its other reader is `ingest/abilities.py`, which uses it to choose what to extract, so narrowing it there shrinks the next extraction rather than filtering what is already stored. Acting on this table at query time means a section filter in `_extracted_roster`, which is code and needs a server restart, though not a re-extraction.

| count | section |
|---:|---|
| 8 | `Abilities and Powers / Fighting Style` |
| 6 | `Abilities and Powers / Physical Abilities` |
| 4 | `Abilities and Powers / Influence from "God" / Supernatural Abilities` |
| 3 | `Abilities and Powers / Influence from "God" / Fighting Style` |
| 2 | `Garou` |
| 2 | `Abilities and Powers / Human / Fighting Style` |
| 1 | `Abilities and Powers / Supernatural Abilities` |
| 1 | `Abilities and Powers / Cyborg Modifications / List of Upgrades` |
| 1 | `Abilities and Powers / Cyborg Modifications` |
| 1 | `Abilities and Powers / Influence from "God"` |
| 1 | `Bang` |

## Offline regression suite

A different measurement: `gold_*.json` checked against the crawl, in-process, boolean. It gates the build; this report does not.

| series | score |
|---|---|
| `opm` | n/a (no gold set) |

## Reproducing

```powershell
python start_scriptengine.py          # the server must be up
python -m scriptengine.cli canon-run
```

The server holds its code in memory, so restart it after any change under `scriptengine/` or the run measures the old code. `canon-run` refuses to start against a server older than the newest source file, because one earlier measurement was taken that way and reported no change from a fix that had worked.

Run metadata: `2026-08-22-1048`, git `2110e4c`, server started `2026-08-22T00:27:20+00:00`, 14s wall clock.

Sources for every answer are in `questions/<series>.json`, per item.
