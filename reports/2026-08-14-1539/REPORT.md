# Canon run 2026-08-14-1539

103 set questions and 32 fact questions over 8 series, asked of the live server and scored against `questions/`.

## Headline

| | |
|---|---:|
| canon items recovered | **811/984** (82.4%) (no change) |
| precision, closed sets | **57.2%** over 85/103 questions (+6.4%) |
| questions at recall 0 | 5/103 |
| questions at recall >= 0.8 | 72/103 |
| confident and wrong | **0** |
| fact answers present in the bundle | 32/32 |
| members returned | 2248 |

**Comparable subset.** The 36 questions carried over from the 2026-08-04 gold set score **272/313** (86.9%). The bank grew underneath every other number here, and the questions added since deliberately target known weak spots, so a lower headline is the expected and more honest result.

## What the engine gets wrong

Ordered by what reaches a script. A confidently wrong answer is first because the engine gives a caller no reason to check it; a visibly thin one gets checked.

| | series | question | canon | found | recall | engine said | missing |
|---|---|---|---:|---:|---:|---|---|
| recall 0 | `db` | Every form of Majin Buu | 7 | 0 | 0.0% | `partial` | Innocent Buu, Evil Buu, Super Buu, Buutenks, Buuhan, Kid Buu, +1 more |
| recall 0 | `berserk` | Every member of the Four Kings of the World | 4 | 0 | 0.0% | `-` | King of the East, King of the West, King of the South, King of the North |
| recall 0 | `berserk` | Every ability of Serpico | 3 | 0 | 0.0% | `partial` | Rapier, Sylph Sword, Sylph Cloak |
| recall 0 | `csm` | Every devil contract of Aki Hayakawa | 3 | 0 | 0.0% | `partial` | Fox Devil, Curse Devil, Future Devil |
| recall 0 | `csm` | Every ability of Himeno | 2 | 0 | 0.0% | `partial` | Ghost Devil Contract, Hand-to-Hand Combat |
|  | `berserk` | Every member of the Black Swordsman Party | 12 | 2 | 16.7% | `partial` | Casca, Isidro, Farnese, Serpico, Schierke, Ivalera, +4 more |
|  | `onepiece` | Every technique of Zoro | 10 | 3 | 30.0% | `partial` | Oni Giri, Santoryu Ogi: Sanzen Sekai, Tatsumaki, Shishi Sonson, Yakkodori, Toro Nagashi, +1 more |
|  | `csm` | Every ability of Aki Hayakawa | 11 | 4 | 36.4% | `partial` | Swordsmanship, Hand-to-Hand Combat, Cooking, Driving, Strong Willpower, Enhanced Durability, +1 more |
|  | `jjk` | Every shikigami of Megumi Fushiguro | 9 | 4 | 44.4% | `partial` | Toad, Great Serpent, Round Deer, Piercing Ox, Mahoraga |
|  | `bleach` | Every form of Ichigo Kurosaki | 12 | 6 | 50.0% | `partial` | Full Hollowfication, Vasto Lorde, Final Getsuga Tensho, Fullbring Bankai, True Shikai, True Bankai |
|  | `berserk` | Every type of beherit | 2 | 1 | 50.0% | `declared` | Crimson Beherit |
|  | `hxh` | Every Nen ability of Hisoka | 2 | 1 | 50.0% | `partial` | Texture Surprise |
|  | `hxh` | Every ability of Hisoka Morow | 2 | 1 | 50.0% | `partial` | Texture Surprise |
|  | `bleach` | Every ability of Kenpachi Zaraki | 17 | 9 | 52.9% | `partial` | Highly Perceptive Combatant, Immeasurable Spiritual Power, Ryōdan, Immense Strength, Immense Endurance, Nozarashi, +2 more |
|  | `jjk` | Every ability of Satoru Gojo | 22 | 12 | 54.5% | `partial` | Master Hand-to-Hand Combatant, Immense Strength, Immense Speed & Reflexes, Immense Endurance, Great Tactical Intellect, Cursed Energy Capacity, +4 more |
|  | `jjk` | Every ability of Yuji Itadori | 23 | 13 | 56.5% | `partial` | Weapon Mastery, Master Hand-to-Hand Combatant, Immense Strength, Immense Speed and Reflexes, Immense Durability, Immense Stamina, +4 more |
|  | `berserk` | Every named member of the original Band of the Falcon | 14 | 8 | 57.1% | `partial` | Dante, Errol, Riguel, Dillos, Kim, Sam |
|  | `jjk` | Every ability of Sukuna | 32 | 19 | 59.4% | `partial` | Master Hand-to-Hand Combatant, Immense Strength, Immense Speed, Immense Reflexes, Immense Durability, Great Tactical Intellect, +7 more |
|  | `hxh` | Every Nen ability of Chrollo | 3 | 2 | 66.7% | `partial` | Borrowed Time |
|  | `jjk` | Every ability of Megumi Fushiguro | 16 | 11 | 68.8% | `partial` | Expert Hand-to-Hand Combatant, Expert Weapons Specialist, Advanced Endurance, Immense Tactical Intellect, Cursed Energy Capacity |
|  | `bleach` | Every ability of Sōsuke Aizen | 20 | 14 | 70.0% | `partial` | Immeasurable Spiritual Power, Master Swordsman, Hakuda Master, Immense Strength, Immortality, Shikai |
|  | `bleach` | Every current Espada (the ten active Espada of Aizen's Arrancar army) | 10 | 7 | 70.0% | `declared` | Tier Harribel, Grimmjow Jaegerjaquez, Szayelaporro Granz |
|  | `onepiece` | Every ability of Monkey D. Luffy | 10 | 7 | 70.0% | `partial` | Supreme King Haki, Observation Haki, Armament Haki |
|  | `onepiece` | Every ability of Roronoa Zoro | 10 | 7 | 70.0% | `partial` | Supreme King Haki, Armament Haki, Observation Haki |
|  | `onepiece` | Every ability of Sanji | 10 | 7 | 70.0% | `partial` | Armament Haki, Observation Haki, Supreme King Haki |
|  | `bleach` | Every ability of Rukia Kuchiki | 17 | 12 | 70.6% | `partial` | Kaidō, Shikai, Some no mai, Tsukishiro, Tsugi no mai, Hakuren, San no mai, Shirafune |
|  | `bleach` | Every ability of Byakuya Kuchiki | 17 | 12 | 70.6% | `partial` | Senka, Utsusemi, Immense Endurance, Hurtless Area, Shūkei: Hakuteiken |
|  | `csm` | Every ability of Denji | 17 | 12 | 70.6% | `partial` | Enhanced Human Condition, Enhanced Endurance, Hand-to-Hand Combat, Strategic Intelligence, Swimming |
|  | `onepiece` | Every ability of Usopp | 14 | 10 | 71.4% | `partial` | Marksmanship, Engineering Expertise, Tactical Skills, Observation Haki |
|  | `bleach` | Every ability of Ichigo Kurosaki | 19 | 14 | 73.7% | `partial` | Getsuga Jujisho, Chain, Enhanced Getsuga Tensho, Deadly Darts, Ichigo Homerun |
|  | `hxh` | Every ability of Killua Zoldyck | 9 | 7 | 77.8% | `partial` | The Snake Awakens, Silent Gaits |

## Why each miss is missing

Assigned by a lookup against the store, not by eye.

| bucket | count | share | the fix lives in |
|---|---:|---:|---|
| extraction gap | 67 | 39% | `scriptengine/ingest/abilities.py` |
| retrieval gap | 44 | 25% | `scriptengine/retrieve/` |
| unlinked page | 40 | 23% | `series/<name>/overrides.yaml` |
| corpus gap | 22 | 13% | `a crawl, or nothing` |

## What to do about it

In order of items recovered per unit of effort.

1. **retrieval gap, 44 items.** Already in the store and still not returned -- the retriever had every chance. Trace one query end to end before writing code; the diagnosis names the row it expected to find.
   Fix lives in `scriptengine/retrieve/`.
   Biggest cluster: Every ability of Kenpachi Zaraki (5 items).

2. **unlinked page, 40 items.** The page exists and nothing ties it to the subject. This is the wiki's shape, not a retriever bug -- declare the link rather than trying to infer it.
   Fix lives in `series/<name>/overrides.yaml`.
   Biggest cluster: Every member of the Black Swordsman Party (10 items).

3. **extraction gap, 67 items.** The prose names it and the extraction pass did not return it. Fix the prompt and bump PROMPT_VERSION, or the cached answers survive the change.
   Fix lives in `scriptengine/ingest/abilities.py`.
   Biggest cluster: Every ability of Sukuna (12 items).

4. **corpus gap, 22 items.** Not in the subject's prose at all. Check the crawl is not stale for that page; if it is current, the wiki does not support the claim and a script must not make it.
   Fix lives in `a crawl, or nothing`.
   Biggest cluster: Every named member of the original Band of the Falcon (6 items).

## Padded rosters

Closed sets where the engine returned more than twice the canon count. This is the measured defect: recall is respectable and a caller still cannot use the answer, because the right names arrive buried in wrong ones. Roadmap phases 20 (current vs former member) and 21 (a set the wiki barely fills) are the two named causes.

| series | question | canon | returned | ratio | precision |
|---|---|---:|---:|---:|---:|
| `berserk` | Every armor of Guts | 1 | 8 | 8x | 12.5% |
| `db` | Every form of Cell | 4 | 24 | 6x | 16.7% |
| `jjk` | Every member of the Disaster Curses (Mahito's group of unregistered special-grade cursed spirits) | 4 | 22 | 6x | 18.2% |
| `jjk` | Every cursed technique of Yuta Okkotsu | 5 | 20 | 4x | 20.0% |
| `db` | Every form of Gohan | 6 | 22 | 4x | 22.7% |
| `jjk` | Every ability of Nobara Kugisaki | 4 | 13 | 3x | 30.8% |
| `onepiece` | Every sword style of Zoro | 7 | 22 | 3x | 31.8% |
| `csm` | Every form of Denji | 4 | 11 | 3x | 36.4% |
| `jjk` | How many 1v1 battles did Yuji Itadori have with named characters | 9 | 24 | 3x | 37.5% |
| `jjk` | Every shikigami of Megumi Fushiguro | 9 | 24 | 3x | 16.7% |
| `db` | Every form of Goku | 12 | 31 | 3x | 35.5% |
| `bleach` | Every technique of Byakuya Kuchiki | 7 | 18 | 3x | 33.3% |
| `bleach` | Every technique of Ichigo Kurosaki | 12 | 27 | 2x | 37.0% |
| `db` | Every transformation of Frieza | 8 | 18 | 2x | 44.4% |
| `hxh` | Every Nen ability of Gon | 4 | 9 | 2x | 44.4% |

## Where the wrong names come from

Every one of the 457 members returned on a closed set that matched no canon item, by the candidate path that vouched for it. `recall_only` questions are excluded: their gold is a curated core list, so a name outside it is usually right.

| source | count | share | what it means |
|---|---:|---:|---|
| prose row | 237 | 52% | Extracted from prose at index time. Skips `validate_member` by design; filtered only by `ability_stopwords` and a word count. The section it came from is the lever. |
| category page | 114 | 25% | Arrived through a category or a declared roster rather than through the character, so the set itself is too broad, rather than the member. |
| heading | 86 | 19% | A section heading on the character's page. Also skips `validate_member`; `ability_sections` is what selects these. |
| ownership edge | 20 | 4% | The wiki wrote `X -user-> Y`. The only path already validated, and correspondingly the smallest. |

**340 (74%) are vouched for by one path only**, against 117 backed by more than one. Corroboration is the signal the union discards when it deduplicates on lowercased name alone. 20 (4%) are lead-level rows: the section they were extracted from is the bare page title, so they came from the article's opening rather than from any heading.

Sections supplying the most wrong names, from `abilities.section`, the breadcrumb each row was read from.

Worth knowing before acting on this table: `ability_sections` in `series/<name>/overrides.yaml` does **not** filter these. In `scriptengine/retrieve/` it is read in exactly one place (`roster.py:1208`, inside `_section_roster`), so it selects *headings*; `_extracted_roster` never consults it, and prose rows are the majority of what is listed here. Its other reader is `ingest/abilities.py`, which uses it to choose what to extract, so narrowing it there shrinks the next extraction rather than filtering what is already stored. Acting on this table at query time means a section filter in `_extracted_roster`, which is code and needs a server restart, though not a re-extraction.

| count | section |
|---:|---|
| 48 | `Abilities` |
| 23 | `Powers & Abilities` |
| 15 | `Power` |
| 14 | `Abilities and Powers / Cursed Techniques` |
| 9 | `Abilities and Powers / Cursed Energy` |
| 8 | `Former Powers & Abilities` |
| 7 | `Powers & Abilities / Natural Abilities` |
| 7 | `Abilities & Powers / Nen` |
| 7 | `Abilities and Powers / Overview` |
| 6 | `Abilities / Antemortem Abilities / Devil Contracts` |
| 5 | `Abilities and Powers / Cyborg Modifications` |
| 4 | `Powers & Abilities / Zanpakutō` |
| 4 | `Powers & Abilities / Shinigami Powers & Abilities` |
| 4 | `Aki Hayakawa` |
| 4 | `Abilities & Powers` |

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

Run metadata: `2026-08-14-1539`, git `3615bae`, server started `2026-08-14T15:38:47+00:00`, 555s wall clock.

Sources for every answer are in `questions/<series>.json`, per item.
