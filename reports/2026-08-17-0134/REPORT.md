# Canon run 2026-08-17-0134

20 set questions and 18 fact questions over 1 series, asked of the live server and scored against `questions/`.

## Headline

| | |
|---|---:|
| canon items recovered | **206/211** (97.6%) (no change) |
| precision, closed sets | **55.0%** over 17/20 questions (+0.5%) |
| questions at recall 0 | 0/20 |
| questions at recall >= 0.8 | 20/20 |
| confident and wrong | **0** |
| fact answers present in the bundle | 13/18 |
| members returned | 332 |

**Comparable subset.** The 5 questions carried over from the 2026-08-04 gold set score **42/43** (97.7%). The bank grew underneath every other number here, and the questions added since deliberately target known weak spots, so a lower headline is the expected and more honest result.

## What the engine gets wrong

Ordered by what reaches a script. A confidently wrong answer is first because the engine gives a caller no reason to check it; a visibly thin one gets checked.

| | series | question | canon | found | recall | engine said | missing |
|---|---|---|---:|---:|---:|---|---|

### Fact answers not present in what was served

The engine serves context rather than an answer sentence, so the claim here is only that the correct answer was **not present in the bundle** -- a writer had nothing to write the line from.

| series | question | expected | intruders present |
|---|---|---|---|
| `jjk` | Who is Satoru Gojo's student? | Yuji Itadori, Megumi Fushiguro, Nobara Kugisaki | - |
| `jjk` | How many grades of jujutsu sorcerers exist? | 6 grades | - |
| `jjk` | How many Big Three Sorcerer Families exist? | 3 families | - |
| `jjk` | How many special grade jujutsu sorcerers are there? | 4 special grade sorcerers | - |
| `jjk` | How many fingers of Sukuna exist? | 20 fingers | - |

## Why each miss is missing

Assigned by a lookup against the store, not by eye.

| bucket | count | share | the fix lives in |
|---|---:|---:|---|
| extraction gap | 2 | 40% | `scriptengine/ingest/abilities.py` |
| corpus gap | 1 | 20% | `a crawl, or nothing` |
| retrieval gap | 1 | 20% | `scriptengine/retrieve/` |
| unlinked page | 1 | 20% | `series/<name>/overrides.yaml` |

## What to do about it

In order of items recovered per unit of effort.

1. **retrieval gap, 1 items.** Already in the store and still not returned -- the retriever had every chance. Trace one query end to end before writing code; the diagnosis names the row it expected to find.
   Fix lives in `scriptengine/retrieve/`.
   Biggest cluster: Every ability of Sukuna (1 items).

2. **unlinked page, 1 items.** The page exists and nothing ties it to the subject. This is the wiki's shape, not a retriever bug -- declare the link rather than trying to infer it.
   Fix lives in `series/<name>/overrides.yaml`.
   Biggest cluster: Who are the notable members of the Zenin Family? (1 items).

3. **extraction gap, 2 items.** The prose names it and the extraction pass did not return it. Fix the prompt and bump PROMPT_VERSION, or the cached answers survive the change.
   Fix lives in `scriptengine/ingest/abilities.py`.
   Biggest cluster: Every ability of Satoru Gojo (1 items).

4. **corpus gap, 1 items.** Not in the subject's prose at all. Check the crawl is not stale for that page; if it is current, the wiki does not support the claim and a script must not make it.
   Fix lives in `a crawl, or nothing`.
   Biggest cluster: Every cursed technique of Yuta Okkotsu (1 items).

## Padded rosters

Closed sets where the engine returned more than twice the canon count. This is the measured defect: recall is respectable and a caller still cannot use the answer, because the right names arrive buried in wrong ones. Roadmap phases 20 (current vs former member) and 21 (a set the wiki barely fills) are the two named causes.

| series | question | canon | returned | ratio | precision |
|---|---|---:|---:|---:|---:|
| `jjk` | Every member of the Disaster Curses (Mahito's group of unregistered special-grade cursed spirits) | 4 | 22 | 6x | 18.2% |
| `jjk` | Every cursed technique of Yuta Okkotsu | 5 | 24 | 5x | 16.7% |
| `jjk` | How many 1v1 battles did Yuji Itadori have with named characters | 9 | 24 | 3x | 37.5% |
| `jjk` | Every cursed technique of Sukuna | 10 | 25 | 2x | 40.0% |
| `jjk` | What are Sukuna's named cursed techniques? | 10 | 25 | 2x | 40.0% |

## Where the wrong names come from

Every one of the 107 members returned on a closed set that matched no canon item, by the candidate path that vouched for it. `recall_only` questions are excluded: their gold is a curated core list, so a name outside it is usually right.

| source | count | share | what it means |
|---|---:|---:|---|
| prose row | 66 | 62% | Extracted from prose at index time. Skips `validate_member` by design; filtered only by `ability_stopwords` and a word count. The section it came from is the lever. |
| category page | 35 | 33% | Arrived through a category or a declared roster rather than through the character, so the set itself is too broad, rather than the member. |
| ownership edge | 6 | 6% | The wiki wrote `X -user-> Y`. The only path already validated, and correspondingly the smallest. |

**77 (72%) are vouched for by one path only**, against 30 backed by more than one. Corroboration is the signal the union discards when it deduplicates on lowercased name alone. 1 (1%) are lead-level rows: the section they were extracted from is the bare page title, so they came from the article's opening rather than from any heading.

Sections supplying the most wrong names, from `abilities.section`, the breadcrumb each row was read from.

Worth knowing before acting on this table: `ability_sections` in `series/<name>/overrides.yaml` does **not** filter these. In `scriptengine/retrieve/` it is read in exactly one place (`roster.py:1208`, inside `_section_roster`), so it selects *headings*; `_extracted_roster` never consults it, and prose rows are the majority of what is listed here. Its other reader is `ingest/abilities.py`, which uses it to choose what to extract, so narrowing it there shrinks the next extraction rather than filtering what is already stored. Acting on this table at query time means a section filter in `_extracted_roster`, which is code and needs a server restart, though not a re-extraction.

| count | section |
|---:|---|
| 31 | `Abilities and Powers / Cursed Techniques` |
| 10 | `Abilities and Powers / Cursed Energy` |
| 6 | `Divine Dogs / Related Techniques` |
| 5 | `Abilities and Powers / Overview` |
| 5 | `Abilities and Powers / Cursed Technique` |
| 4 | `Abilities and Powers / Cursed Restrictions` |
| 3 | `Cursed Technique Lapse: Blue / Related Techniques` |
| 1 | `Abilities and Powers / Intelligence` |
| 1 | `Satoru Gojo` |

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

Run metadata: `2026-08-17-0134`, git `125eac4`, server started `2026-08-17T01:31:06+00:00`, 7s wall clock.

Sources for every answer are in `questions/<series>.json`, per item.
