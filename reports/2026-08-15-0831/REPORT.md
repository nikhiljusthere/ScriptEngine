# Canon run 2026-08-15-0831

160 set questions and 151 fact questions over 8 series, asked of the live server and scored against `questions/`.

## Headline

| | |
|---|---:|
| canon items recovered | **1161/1362** (85.2%) (-1.1%) |
| precision, closed sets | **59.4%** over 142/160 questions (+5.9%) |
| questions at recall 0 | 2/160 |
| questions at recall >= 0.8 | 124/160 |
| confident and wrong | **3** |
| fact answers present in the bundle | 125/151 |
| members returned | 2764 |

**Comparable subset.** The 36 questions carried over from the 2026-08-04 gold set score **281/313** (89.8%). The bank grew underneath every other number here, and the questions added since deliberately target known weak spots, so a lower headline is the expected and more honest result.

## What the engine gets wrong

Ordered by what reaches a script. A confidently wrong answer is first because the engine gives a caller no reason to check it; a visibly thin one gets checked.

| | series | question | canon | found | recall | engine said | missing |
|---|---|---|---:|---:|---:|---|---|
| **confident and wrong** | `bleach` | Every dance of Rukia's Shikai Sode no Shirayuki | 3 | 0 | 0.0% | `declared` | Some no mai, Tsukishiro, Tsugi no mai, Hakuren, San no mai, Shirafune |
| **confident and wrong** | `bleach` | Every ability of Sōsuke Aizen | 20 | 2 | 10.0% | `exact` | Genius Intellect, Master Strategist & Tactician, Master Manipulator, Master Combatant, Knowledge, Master Scientist, +12 more |
| **confident and wrong** | `db` | How many Gods of Destruction exist across the multiverse? | 15 | 3 | 20.0% | `declared` | Beerus (Universe 7), Champa (Universe 6), Belmod (Universe 11), Quitela (Universe 4), Arack (Universe 5), Liquiir (Universe 8), +6 more |
| recall 0 | `bleach` | Every release state of Kenpachi's Zanpakutō | 2 | 0 | 0.0% | `partial` | Shikai (Nozarashi), Bankai (Unnamed) |
|  | `berserk` | Every member of the Black Swordsman Party | 12 | 2 | 16.7% | `partial` | Casca, Isidro, Farnese, Serpico, Schierke, Ivalera, +4 more |
|  | `bleach` | Every named technique Ichigo uses with Zangetsu | 4 | 1 | 25.0% | `partial` | Chain, Deadly Darts, Ichigo Homerun |
|  | `onepiece` | Every technique of Zoro | 10 | 3 | 30.0% | `partial` | Oni Giri, Santoryu Ogi: Sanzen Sekai, Tatsumaki, Shishi Sonson, Yakkodori, Toro Nagashi, +1 more |
|  | `csm` | Every ability of Aki Hayakawa | 11 | 4 | 36.4% | `partial` | Swordsmanship, Hand-to-Hand Combat, Cooking, Driving, Strong Willpower, Enhanced Durability, +1 more |
|  | `jjk` | Every shikigami of Megumi Fushiguro | 9 | 4 | 44.4% | `partial` | Toad, Great Serpent, Round Deer, Piercing Ox, Mahoraga |
|  | `bleach` | Every form of Ichigo Kurosaki | 12 | 6 | 50.0% | `partial` | Full Hollowfication, Vasto Lorde, Final Getsuga Tensho, Fullbring Bankai, True Shikai, True Bankai |
|  | `csm` | How many members are in the Four Horsemen? | 4 | 2 | 50.0% | `declared` | Control Devil (Makima), War Devil (Yoru) |
|  | `berserk` | Every type of beherit | 2 | 1 | 50.0% | `declared` | Crimson Beherit |
|  | `hxh` | Every Nen ability of Hisoka | 2 | 1 | 50.0% | `partial` | Texture Surprise |
|  | `hxh` | Every ability of Hisoka Morow | 2 | 1 | 50.0% | `partial` | Texture Surprise |
|  | `bleach` | Every ability of Kenpachi Zaraki | 17 | 9 | 52.9% | `partial` | Highly Perceptive Combatant, Immeasurable Spiritual Power, Ryōdan, Immense Strength, Immense Endurance, Nozarashi, +2 more |
|  | `jjk` | Every ability of Satoru Gojo | 22 | 12 | 54.5% | `partial` | Master Hand-to-Hand Combatant, Immense Strength, Immense Speed & Reflexes, Immense Endurance, Great Tactical Intellect, Cursed Energy Capacity, +4 more |
|  | `jjk` | Every ability of Yuji Itadori | 23 | 13 | 56.5% | `partial` | Weapon Mastery, Master Hand-to-Hand Combatant, Immense Strength, Immense Speed and Reflexes, Immense Durability, Immense Stamina, +4 more |
|  | `jjk` | Every ability of Sukuna | 32 | 19 | 59.4% | `partial` | Master Hand-to-Hand Combatant, Immense Strength, Immense Speed, Immense Reflexes, Immense Durability, Great Tactical Intellect, +7 more |
|  | `hxh` | What are Killua Zoldyck's named Nen techniques? | 6 | 4 | 66.7% | `declared` | Godspeed, Thunder Palm |
|  | `hxh` | Every Nen ability of Chrollo | 3 | 2 | 66.7% | `partial` | Borrowed Time |
|  | `jjk` | Every ability of Megumi Fushiguro | 16 | 11 | 68.8% | `partial` | Expert Hand-to-Hand Combatant, Expert Weapons Specialist, Advanced Endurance, Immense Tactical Intellect, Cursed Energy Capacity |
|  | `bleach` | Every current Espada (the ten active Espada of Aizen's Arrancar army) | 10 | 7 | 70.0% | `declared` | Tier Harribel, Grimmjow Jaegerjaquez, Szayelaporro Granz |
|  | `onepiece` | Every ability of Monkey D. Luffy | 10 | 7 | 70.0% | `partial` | Supreme King Haki, Observation Haki, Armament Haki |
|  | `onepiece` | Every ability of Roronoa Zoro | 10 | 7 | 70.0% | `partial` | Supreme King Haki, Armament Haki, Observation Haki |
|  | `onepiece` | Every ability of Sanji | 10 | 7 | 70.0% | `partial` | Armament Haki, Observation Haki, Supreme King Haki |
|  | `bleach` | Every ability of Rukia Kuchiki | 17 | 12 | 70.6% | `partial` | Kaidō, Shikai, Some no mai, Tsukishiro, Tsugi no mai, Hakuren, San no mai, Shirafune |
|  | `bleach` | Every ability of Byakuya Kuchiki | 17 | 12 | 70.6% | `partial` | Senka, Utsusemi, Immense Endurance, Hurtless Area, Shūkei: Hakuteiken |
|  | `csm` | Every ability of Denji | 17 | 12 | 70.6% | `partial` | Enhanced Human Condition, Enhanced Endurance, Hand-to-Hand Combat, Strategic Intelligence, Swimming |
|  | `onepiece` | Every ability of Usopp | 14 | 10 | 71.4% | `partial` | Marksmanship, Engineering Expertise, Tactical Skills, Observation Haki |
|  | `opm` | Every named technique of Bang's Water Stream Rock Smashing Fist in One Punch Man | 7 | 5 | 71.4% | `declared` | Whirlwind Water Stream: Roaring Aura Sky Ripping Fist, Whirlwind Water Stream: Cross Fang Dragon Slayer Fist |
|  | `bleach` | Every ability of Ichigo Kurosaki | 19 | 14 | 73.7% | `partial` | Getsuga Jujisho, Chain, Enhanced Getsuga Tensho, Deadly Darts, Ichigo Homerun |
|  | `bleach` | Every named Bankai technique Byakuya uses | 4 | 3 | 75.0% | `declared` | Shūkei: Hakuteiken |
|  | `bleach` | Every position Aizen has held | 4 | 3 | 75.0% | `declared` | Instructor at the Shin'ō Academy |
|  | `onepiece` | How many Sweet Commanders are in the Big Mom Pirates in One Piece? | 4 | 3 | 75.0% | `declared` | Three Sweet Commanders |
|  | `onepiece` | How many All-Stars are in the Beasts Pirates in One Piece? | 4 | 3 | 75.0% | `declared` | Three All-Stars |
|  | `hxh` | Every ability of Killua Zoldyck | 9 | 7 | 77.8% | `partial` | The Snake Awakens, Silent Gaits |

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
| `csm` | Who leads the Four Horsemen? | Control Devil (Makima) | - |
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
| extraction gap | 64 | 32% | `scriptengine/ingest/abilities.py` |
| retrieval gap | 54 | 27% | `scriptengine/retrieve/` |
| unlinked page | 48 | 24% | `series/<name>/overrides.yaml` |
| corpus gap | 35 | 17% | `a crawl, or nothing` |

## What to do about it

In order of items recovered per unit of effort.

1. **retrieval gap, 54 items.** Already in the store and still not returned -- the retriever had every chance. Trace one query end to end before writing code; the diagnosis names the row it expected to find.
   Fix lives in `scriptengine/retrieve/`.
   Biggest cluster: Every ability of Sōsuke Aizen (16 items).

2. **unlinked page, 48 items.** The page exists and nothing ties it to the subject. This is the wiki's shape, not a retriever bug -- declare the link rather than trying to infer it.
   Fix lives in `series/<name>/overrides.yaml`.
   Biggest cluster: Every member of the Black Swordsman Party (10 items).

3. **extraction gap, 64 items.** The prose names it and the extraction pass did not return it. Fix the prompt and bump PROMPT_VERSION, or the cached answers survive the change.
   Fix lives in `scriptengine/ingest/abilities.py`.
   Biggest cluster: Every ability of Sukuna (12 items).

4. **corpus gap, 35 items.** Not in the subject's prose at all. Check the crawl is not stale for that page; if it is current, the wiki does not support the claim and a script must not make it.
   Fix lives in `a crawl, or nothing`.
   Biggest cluster: How many Gods of Destruction exist across the multiverse? (12 items).

## Padded rosters

Closed sets where the engine returned more than twice the canon count. This is the measured defect: recall is respectable and a caller still cannot use the answer, because the right names arrive buried in wrong ones. Roadmap phases 20 (current vs former member) and 21 (a set the wiki barely fills) are the two named causes.

| series | question | canon | returned | ratio | precision |
|---|---|---:|---:|---:|---:|
| `csm` | How many special divisions exist in Public Safety Devil Hunters? | 2 | 74 | 37x | 2.7% |
| `onepiece` | Every named variation of Sanji's Diable Jambe technique in One Piece | 2 | 24 | 12x | 8.3% |
| `berserk` | Every armor of Guts | 1 | 8 | 8x | 12.5% |
| `bleach` | Every named technique Ichigo uses with Zangetsu | 4 | 27 | 7x | 3.7% |
| `onepiece` | Every Gear technique of Monkey D. Luffy in One Piece | 4 | 25 | 6x | 16.0% |
| `db` | Every form of Cell | 4 | 24 | 6x | 16.7% |
| `jjk` | Every member of the Disaster Curses (Mahito's group of unregistered special-grade cursed spirits) | 4 | 22 | 6x | 18.2% |
| `jjk` | Every cursed technique of Yuta Okkotsu | 5 | 20 | 4x | 20.0% |
| `db` | Every form of Gohan | 6 | 22 | 4x | 22.7% |
| `db` | Who are the members of the Ginyu Force? | 5 | 17 | 3x | 29.4% |
| `onepiece` | Every sword style of Zoro | 7 | 22 | 3x | 31.8% |
| `bleach` | Every release state of Kenpachi's Zanpakutō | 2 | 6 | 3x | 0.0% |
| `csm` | Every form of Denji | 4 | 11 | 3x | 36.4% |
| `jjk` | How many 1v1 battles did Yuji Itadori have with named characters | 9 | 24 | 3x | 37.5% |
| `db` | Every form of Goku | 12 | 31 | 3x | 35.5% |

## Where the wrong names come from

Every one of the 656 members returned on a closed set that matched no canon item, by the candidate path that vouched for it. `recall_only` questions are excluded: their gold is a curated core list, so a name outside it is usually right.

| source | count | share | what it means |
|---|---:|---:|---|
| prose row | 300 | 46% | Extracted from prose at index time. Skips `validate_member` by design; filtered only by `ability_stopwords` and a word count. The section it came from is the lever. |
| category page | 201 | 31% | Arrived through a category or a declared roster rather than through the character, so the set itself is too broad, rather than the member. |
| heading | 104 | 16% | A section heading on the character's page. Also skips `validate_member`; `ability_sections` is what selects these. |
| ownership edge | 26 | 4% | The wiki wrote `X -user-> Y`. The only path already validated, and correspondingly the smallest. |
| unattributed | 25 | 4% | No page, no edge, no row, no heading. Nothing vouches for it at all. |

**486 (74%) are vouched for by one path only**, against 145 backed by more than one. Corroboration is the signal the union discards when it deduplicates on lowercased name alone. 23 (4%) are lead-level rows: the section they were extracted from is the bare page title, so they came from the article's opening rather than from any heading.

Sections supplying the most wrong names, from `abilities.section`, the breadcrumb each row was read from.

Worth knowing before acting on this table: `ability_sections` in `series/<name>/overrides.yaml` does **not** filter these. In `scriptengine/retrieve/` it is read in exactly one place (`roster.py:1208`, inside `_section_roster`), so it selects *headings*; `_extracted_roster` never consults it, and prose rows are the majority of what is listed here. Its other reader is `ingest/abilities.py`, which uses it to choose what to extract, so narrowing it there shrinks the next extraction rather than filtering what is already stored. Acting on this table at query time means a section filter in `_extracted_roster`, which is code and needs a server restart, though not a re-extraction.

| count | section |
|---:|---|
| 53 | `Abilities` |
| 21 | `Powers & Abilities` |
| 17 | `Power` |
| 16 | `Former Powers & Abilities` |
| 15 | `Abilities and Powers / Cursed Techniques` |
| 12 | `Powers & Abilities / Natural Abilities` |
| 12 | `Abilities and Powers / Cursed Energy` |
| 10 | `Abilities & Powers / Nen` |
| 9 | `Abilities and Powers / Overview` |
| 8 | `Powers & Abilities / Shinigami Powers & Abilities` |
| 6 | `Monkey D. Luffy` |
| 6 | `Physical Abilities / Black Leg Style` |
| 6 | `Physical Abilities / Black Leg Style / Diable Jambe` |
| 5 | `Powers & Abilities / Zanpakutō` |
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

Run metadata: `2026-08-15-0831`, git `fe86f4a`, server started `2026-08-15T08:30:51+00:00`, 170s wall clock.

Sources for every answer are in `questions/<series>.json`, per item.
