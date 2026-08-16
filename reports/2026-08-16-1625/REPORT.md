# Canon run 2026-08-16-1625

160 set questions and 151 fact questions over 8 series, asked of the live server and scored against `questions/`.

## Headline

| | |
|---|---:|
| canon items recovered | **1297/1360** (95.4%) (+0.4%) |
| precision, closed sets | **63.2%** over 142/160 questions (+0.1%) |
| questions at recall 0 | 0/160 |
| questions at recall >= 0.8 | 149/160 |
| confident and wrong | **0** |
| fact answers present in the bundle | 126/151 |
| members returned | 2925 |

> **The bank changed between these two runs.** Canon shrank from 1361 to 1360 items (-1), so the deltas above are *not* a clean measurement of the engine: part of any move belongs to the target. A correction that adds a name the engine was already returning raises precision without the retriever changing at all. Compare engine changes only across runs whose canon total matches.

**Comparable subset.** The 36 questions carried over from the 2026-08-04 gold set score **284/313** (90.7%). The bank grew underneath every other number here, and the questions added since deliberately target known weak spots, so a lower headline is the expected and more honest result.

This subset is comparable with earlier runs *only* while its own 313 items are unchanged. The 2026-08-14 bank audit corrected questions inside it -- adding names the wiki documents and the bank had omitted, and aliases for names it had spelled differently -- so its denominator has moved and this figure is no longer a like-for-like comparison with the pre-migration 162/217 (74.7%). It remains a fixed set of *questions*; it is no longer a fixed set of *items*.

## What the engine gets wrong

Ordered by what reaches a script. A confidently wrong answer is first because the engine gives a caller no reason to check it; a visibly thin one gets checked.

| | series | question | canon | found | recall | engine said | missing |
|---|---|---|---:|---:|---:|---|---|
|  | `onepiece` | Every technique of Zoro | 10 | 1 | 10.0% | `partial` | Oni Giri, Santoryu Ogi: Sanzen Sekai, Tatsumaki, Shishi Sonson, Ashura, Yakkodori, +3 more |
|  | `bleach` | Every form of Ichigo Kurosaki | 12 | 4 | 33.3% | `partial` | Full Hollowfication, Vasto Lorde, Fullbring, Fullbring Bankai, True Shikai, True Bankai, +2 more |
|  | `bleach` | Every named technique Ichigo uses with Zangetsu | 4 | 2 | 50.0% | `partial` | Deadly Darts, Ichigo Homerun |
|  | `berserk` | Every type of beherit | 2 | 1 | 50.0% | `declared` | Crimson Beherit |
|  | `berserk` | Every weapon Serpico wields | 2 | 1 | 50.0% | `partial` | Rapier |
|  | `hxh` | Every ability of Killua Zoldyck | 9 | 6 | 66.7% | `partial` | The Snake Awakens, Silent Gaits, Rhythm Echo |
|  | `hxh` | Every Nen ability of Chrollo | 3 | 2 | 66.7% | `partial` | Borrowed Time |
|  | `onepiece` | Every ability of Usopp | 14 | 10 | 71.4% | `partial` | Marksmanship, Engineering Expertise, Tactical Skills, Observation Haki |
|  | `bleach` | Every position Aizen has held | 4 | 3 | 75.0% | `declared` | Instructor at the Shin'ō Academy |
|  | `onepiece` | How many Sweet Commanders are in the Big Mom Pirates in One Piece? | 4 | 3 | 75.0% | `declared` | Three Sweet Commanders |
|  | `onepiece` | How many All-Stars are in the Beasts Pirates in One Piece? | 4 | 3 | 75.0% | `declared` | Three All-Stars |

### Fact answers not present in what was served

The engine serves context rather than an answer sentence, so the claim here is only that the correct answer was **not present in the bundle** -- a writer had nothing to write the line from.

| series | question | expected | intruders present |
|---|---|---|---|
| `berserk` | How many members are in the God Hand? | 5 members | - |
| `berserk` | How many notable members are in the Black Swordsman Party? | 12 members | - |
| `bleach` | How many Espada members are there? | 10 Espada | - |
| `bleach` | How many Schutzstaffel members are in the current generation? | 5 members | - |
| `bleach` | How many Sternritter letters are there? | 26 letters | - |
| `bleach` | How many captains are in the Gotei 13? | 13 captains | - |
| `csm` | What is Denji's hybrid transformation trigger? | Pulling the cord on his chest | - |
| `hxh` | How many members are in the Phantom Troupe? | 13 members | - |
| `hxh` | How many phases are in the Hunter Exam? | 4 phases | - |
| `hxh` | How many Nen categories exist? | 6 categories | - |
| `jjk` | Who is Satoru Gojo's student? | Yuji Itadori, Megumi Fushiguro, Nobara Kugisaki | - |
| `jjk` | How many grades of jujutsu sorcerers exist? | 6 grades | - |
| `jjk` | How many Big Three Sorcerer Families exist? | 3 families | - |
| `jjk` | How many special grade jujutsu sorcerers are there? | 4 special grade sorcerers | - |
| `jjk` | How many fingers of Sukuna exist? | 20 fingers | - |
| `onepiece` | What is Monkey D. Luffy's current bounty in One Piece? | 3,000,000,000 Belly | - |
| `onepiece` | What is Roronoa Zoro's current bounty in One Piece? | 1,111,000,000 Belly | - |
| `onepiece` | What is Sanji's current bounty in One Piece? | 1,032,000,000 Belly | - |
| `onepiece` | What is Nami's current bounty in One Piece? | 366,000,000 Belly | - |
| `onepiece` | What is Usopp's current bounty in One Piece? | 500,000,000 Belly | - |
| `onepiece` | How many members are in the Straw Hat Pirates crew in One Piece? | 10 members | - |
| `onepiece` | What type of ship is the Thousand Sunny in One Piece? | Brigantine | - |
| `opm` | What is Genos's hero rank in One Punch Man? | S-Class Rank 14 | - |
| `opm` | How many S-Class heroes were there before the Monster Association Arc in One Punch Man? | 17 S-Class heroes | - |
| `opm` | How many members are in the Blizzard Group in One Punch Man? | 38 members | - |

## Why each miss is missing

Assigned by a lookup against the store, not by eye.

| bucket | count | share | the fix lives in |
|---|---:|---:|---|
| extraction gap | 21 | 33% | `scriptengine/ingest/abilities.py` |
| corpus gap | 15 | 24% | `a crawl, or nothing` |
| retrieval gap | 14 | 22% | `scriptengine/retrieve/` |
| unlinked page | 13 | 21% | `series/<name>/overrides.yaml` |

## What to do about it

In order of items recovered per unit of effort.

1. **retrieval gap, 14 items.** Already in the store and still not returned -- the retriever had every chance. Trace one query end to end before writing code; the diagnosis names the row it expected to find.
   Fix lives in `scriptengine/retrieve/`.
   Biggest cluster: Every ability of Usopp (4 items).

2. **unlinked page, 13 items.** The page exists and nothing ties it to the subject. This is the wiki's shape, not a retriever bug -- declare the link rather than trying to infer it.
   Fix lives in `series/<name>/overrides.yaml`.
   Biggest cluster: Every form of Ichigo Kurosaki (2 items).

3. **extraction gap, 21 items.** The prose names it and the extraction pass did not return it. Fix the prompt and bump PROMPT_VERSION, or the cached answers survive the change.
   Fix lives in `scriptengine/ingest/abilities.py`.
   Biggest cluster: Every technique of Zoro (7 items).

4. **corpus gap, 15 items.** Not in the subject's prose at all. Check the crawl is not stale for that page; if it is current, the wiki does not support the claim and a script must not make it.
   Fix lives in `a crawl, or nothing`.
   Biggest cluster: How many Gods of Destruction exist across the multiverse? (3 items).

## Padded rosters

Closed sets where the engine returned more than twice the canon count. This is the measured defect: recall is respectable and a caller still cannot use the answer, because the right names arrive buried in wrong ones. Roadmap phases 20 (current vs former member) and 21 (a set the wiki barely fills) are the two named causes.

| series | question | canon | returned | ratio | precision |
|---|---|---:|---:|---:|---:|
| `onepiece` | Every named variation of Sanji's Diable Jambe technique in One Piece | 2 | 22 | 11x | 9.1% |
| `berserk` | Every armor of Guts | 1 | 7 | 7x | 14.3% |
| `bleach` | Every release state of Kenpachi's Zanpakutō | 2 | 14 | 7x | 14.3% |
| `hxh` | Every ability of Leorio Paradinight | 1 | 7 | 7x | 14.3% |
| `onepiece` | Every Gear technique of Monkey D. Luffy in One Piece | 4 | 27 | 7x | 14.8% |
| `bleach` | Every named technique Ichigo uses with Zangetsu | 4 | 25 | 6x | 8.0% |
| `hxh` | Every Nen ability of Gon | 4 | 25 | 6x | 16.0% |
| `jjk` | Every member of the Disaster Curses (Mahito's group of unregistered special-grade cursed spirits) | 4 | 22 | 6x | 18.2% |
| `jjk` | Every cursed technique of Yuta Okkotsu | 5 | 24 | 5x | 16.7% |
| `hxh` | Every Nen ability of Chrollo | 3 | 13 | 4x | 15.4% |
| `hxh` | Every ability of Gon Freecss | 6 | 25 | 4x | 24.0% |
| `bleach` | Every form of Ulquiorra Cifer | 2 | 8 | 4x | 25.0% |
| `db` | Every form of Cell | 4 | 14 | 4x | 28.6% |
| `db` | Who are the members of the Ginyu Force? | 5 | 17 | 3x | 29.4% |
| `db` | Every form of Gohan | 6 | 20 | 3x | 25.0% |

## Where the wrong names come from

Every one of the 606 members returned on a closed set that matched no canon item, by the candidate path that vouched for it. `recall_only` questions are excluded: their gold is a curated core list, so a name outside it is usually right.

| source | count | share | what it means |
|---|---:|---:|---|
| prose row | 320 | 53% | Extracted from prose at index time. Skips `validate_member` by design; filtered only by `ability_stopwords` and a word count. The section it came from is the lever. |
| heading | 143 | 24% | A section heading on the character's page. Also skips `validate_member`; `ability_sections` is what selects these. |
| category page | 89 | 15% | Arrived through a category or a declared roster rather than through the character, so the set itself is too broad, rather than the member. |
| ownership edge | 45 | 7% | The wiki wrote `X -user-> Y`. The only path already validated, and correspondingly the smallest. |
| unattributed | 9 | 1% | No page, no edge, no row, no heading. Nothing vouches for it at all. |

**489 (81%) are vouched for by one path only**, against 108 backed by more than one. Corroboration is the signal the union discards when it deduplicates on lowercased name alone. 31 (5%) are lead-level rows: the section they were extracted from is the bare page title, so they came from the article's opening rather than from any heading.

Sections supplying the most wrong names, from `abilities.section`, the breadcrumb each row was read from.

Worth knowing before acting on this table: `ability_sections` in `series/<name>/overrides.yaml` does **not** filter these. In `scriptengine/retrieve/` it is read in exactly one place (`roster.py:1208`, inside `_section_roster`), so it selects *headings*; `_extracted_roster` never consults it, and prose rows are the majority of what is listed here. Its other reader is `ingest/abilities.py`, which uses it to choose what to extract, so narrowing it there shrinks the next extraction rather than filtering what is already stored. Acting on this table at query time means a section filter in `_extracted_roster`, which is code and needs a server restart, though not a re-extraction.

| count | section |
|---:|---|
| 57 | `Abilities & Powers` |
| 31 | `Abilities and Powers / Cursed Techniques` |
| 16 | `Power / Manga and Anime` |
| 13 | `Abilities and Powers / Cursed Energy` |
| 11 | `Powers & Abilities / Zanpakutō` |
| 10 | `Chrollo Lucilfer` |
| 9 | `Abilities and Powers / Fighting Style` |
| 8 | `Physical Abilities / Strength` |
| 7 | `Abilities & Powers / Nen` |
| 6 | `Physical Abilities / Black Leg Style` |
| 6 | `Abilities and Powers / Physical Abilities` |
| 5 | `Powers & Abilities / Immense Speed` |
| 5 | `Abilities / Forms and Transformations / Super Saiyan` |
| 5 | `Abilities and Powers / Overview` |
| 5 | `Abilities and Powers / Cursed Technique` |

## Offline regression suite

A different measurement: `gold_*.json` checked against the crawl, in-process, boolean. It gates the build; this report does not.

| series | score |
|---|---|
| `berserk` | n/a (--skip-eval) |
| `bleach` | n/a (--skip-eval) |
| `csm` | n/a (--skip-eval) |
| `db` | n/a (--skip-eval) |
| `hxh` | n/a (--skip-eval) |
| `jjk` | n/a (--skip-eval) |
| `onepiece` | n/a (--skip-eval) |
| `opm` | n/a (--skip-eval) |

## Reproducing

```powershell
python start_scriptengine.py          # the server must be up
python -m scriptengine.cli canon-run
```

The server holds its code in memory, so restart it after any change under `scriptengine/` or the run measures the old code. `canon-run` refuses to start against a server older than the newest source file, because one earlier measurement was taken that way and reported no change from a fix that had worked.

Run metadata: `2026-08-16-1625`, git `60ab5a6`, server started `2026-08-16T16:24:48+00:00`, 163s wall clock.

Sources for every answer are in `questions/<series>.json`, per item.
