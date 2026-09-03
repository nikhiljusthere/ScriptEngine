# Canon run 2026-08-15-1842

160 set questions and 151 fact questions over 8 series, asked of the live server and scored against `questions/`.

## Headline

| | |
|---|---:|
| canon items recovered | **1079/1362** (79.2%) (-11.2%) |
| precision, closed sets | **57.2%** over 142/160 questions (-0.0%) |
| questions at recall 0 | 20/160 |
| questions at recall >= 0.8 | 112/160 |
| confident and wrong | **4** |
| fact answers present in the bundle | 125/151 |
| members returned | 2608 |

**Comparable subset.** The 36 questions carried over from the 2026-08-04 gold set score **218/313** (69.6%). The bank grew underneath every other number here, and the questions added since deliberately target known weak spots, so a lower headline is the expected and more honest result.

## What the engine gets wrong

Ordered by what reaches a script. A confidently wrong answer is first because the engine gives a caller no reason to check it; a visibly thin one gets checked.

| | series | question | canon | found | recall | engine said | missing |
|---|---|---|---:|---:|---:|---|---|
| **confident and wrong** | `hxh` | Every ability of Gon Freecss | 6 | 0 | 0.0% | `exact` | Jajanken, Rock, Paper, Scissors, Round 2, Limitation Transformation |
| **confident and wrong** | `bleach` | Every dance of Rukia's Shikai Sode no Shirayuki | 3 | 0 | 0.0% | `declared` | Some no mai, Tsukishiro, Tsugi no mai, Hakuren, San no mai, Shirafune |
| **confident and wrong** | `hxh` | What are Gon Freecss's named Nen techniques? | 3 | 0 | 0.0% | `exact` | Rock, Paper, Scissors |
| **confident and wrong** | `db` | How many Gods of Destruction exist across the multiverse? | 15 | 3 | 20.0% | `declared` | Beerus (Universe 7), Champa (Universe 6), Belmod (Universe 11), Quitela (Universe 4), Arack (Universe 5), Liquiir (Universe 8), +6 more |
| recall 0 | `csm` | Every ability of Denji | 17 | 0 | 0.0% | `partial` | Enhanced Human Condition, Enhanced Endurance, Hybrid Transformation, Augmented Strength, Augmented Durability, Augmented Stamina, +11 more |
| recall 0 | `csm` | Every documented ability of Power | 16 | 0 | 0.0% | `partial` | Enhanced Strength, Enhanced Speed, Blood Manipulation, Blood Hammer, Blood Knife, Blood Spear, +10 more |
| recall 0 | `csm` | Every ability of Power | 14 | 0 | 0.0% | `partial` | Blood Manipulation, Blood Weaponization, Blood Spear, Blood Hammer, Blood Chainsaw, Thousand Tera Blood Rain, +8 more |
| recall 0 | `csm` | Every ability of Aki Hayakawa | 11 | 0 | 0.0% | `partial` | Precognition, Summoning, Swordsmanship, Hand-to-Hand Combat, Cooking, Driving, +5 more |
| recall 0 | `hxh` | Every ability of Kurapika | 10 | 0 | 0.0% | `-` | Chain Jail, Dowsing Chain, Holy Chain, Steal Chain, Judgment Chain, Emperor Time, +4 more |
| recall 0 | `onepiece` | Every technique of Zoro | 10 | 0 | 0.0% | `partial` | Oni Giri, Santoryu Ogi: Sanzen Sekai, Tatsumaki, Shishi Sonson, Ashura, Yakkodori, +4 more |
| recall 0 | `bleach` | Every technique of Byakuya Kuchiki | 7 | 0 | 0.0% | `partial` | Senbonzakura, Senbonzakura Kageyoshi, Senkei, Shukei: Hakuteiken, Gokei, Shunpo, +1 more |
| recall 0 | `hxh` | Every Nen ability of Kurapika | 7 | 0 | 0.0% | `partial` | Chain Jail, Dowsing Chain, Holy Chain, Steal Chain, Judgement Chain, Emperor Time, +1 more |
| recall 0 | `hxh` | Every Nen ability of Killua | 5 | 0 | 0.0% | `partial` | Lightning Palm, Thunderbolt, Whirlwind, Speed of Lightning, Godspeed |
| recall 0 | `hxh` | Every Nen ability of Gon | 4 | 0 | 0.0% | `partial` | Jajanken, Rock, Paper, Scissors |
| recall 0 | `hxh` | Every Nen ability of Chrollo | 3 | 0 | 0.0% | `partial` | Skill Hunter, Bookmark, Borrowed Time |
| recall 0 | `bleach` | Every form of Ulquiorra Cifer | 2 | 0 | 0.0% | `partial` | Resurreccion, Resurreccion: Segunda Etapa |
| recall 0 | `bleach` | Every release state of Kenpachi's Zanpakutō | 2 | 0 | 0.0% | `partial` | Shikai (Nozarashi), Bankai (Unnamed) |
| recall 0 | `hxh` | Every Nen ability of Hisoka | 2 | 0 | 0.0% | `partial` | Bungee Gum, Texture Surprise |
| recall 0 | `hxh` | Every ability of Hisoka Morow | 2 | 0 | 0.0% | `-` | Bungee Gum, Texture Surprise |
| recall 0 | `hxh` | Every ability of Leorio Paradinight | 1 | 0 | 0.0% | `-` | Remote Punch |
| recall 0 | `hxh` | What are Leorio Paradinight's named Nen techniques? | 1 | 0 | 0.0% | `partial` | Remote Punch |
|  | `hxh` | Every ability of Killua Zoldyck | 9 | 1 | 11.1% | `partial` | Lightning Palm, Thunderbolt, Whirlwind, Speed of Lightning, Godspeed, The Snake Awakens, +2 more |
|  | `onepiece` | Every technique of Sanji | 18 | 4 | 22.2% | `partial` | Concasse, Joue Shoot, Sky Walk, Blue Walk, Mouton Shot, Anti-Manner Kick Course, +8 more |
|  | `onepiece` | Every ability of Nami | 16 | 4 | 25.0% | `partial` | Mirage Tempo, Thunderbolt Tempo, Mirage Tempo: Fata Morgana, Thunder Lance Tempo, Gust Sword, Thunder Breed Tempo, +6 more |
|  | `bleach` | Every form of Ichigo Kurosaki | 12 | 3 | 25.0% | `partial` | Full Hollowfication, Vasto Lorde, Final Getsuga Tensho, Fullbring, Fullbring Bankai, True Shikai, +3 more |
|  | `bleach` | Every named technique Ichigo uses with Zangetsu | 4 | 1 | 25.0% | `partial` | Chain, Deadly Darts, Ichigo Homerun |
|  | `onepiece` | Every form of Luffy | 6 | 2 | 33.3% | `partial` | Gear Fourth: Boundman, Gear Fourth: Snakeman, Gear Fourth: Tankman, Gear Fifth |
|  | `bleach` | Every ability of Ichigo Kurosaki | 19 | 7 | 36.8% | `partial` | Zangetsu, Getsuga Jujisho, Chain, Enhanced Getsuga Tensho, Deadly Darts, Ichigo Homerun, +6 more |
|  | `csm` | Every ability of Makima | 8 | 3 | 37.5% | `partial` | Immense Strength, Enhanced Smell, Control, Force Manipulation, Prime Minister Contract |
|  | `bleach` | Every ability of Byakuya Kuchiki | 17 | 8 | 47.1% | `partial` | Senka, Utsusemi, Senbonzakura, Hurtless Area, Senbonzakura Kageyoshi, Gōkei, +3 more |
|  | `onepiece` | Every Gear of Luffy | 6 | 3 | 50.0% | `partial` | Gear Fourth: Snakeman, Gear Fourth: Tankman, Gear Fifth |
|  | `csm` | How many members are in the Four Horsemen? | 4 | 2 | 50.0% | `declared` | Control Devil (Makima), War Devil (Yoru) |
|  | `berserk` | Every type of beherit | 2 | 1 | 50.0% | `declared` | Crimson Beherit |
|  | `berserk` | Every weapon Serpico wields | 2 | 1 | 50.0% | `partial` | Rapier |
|  | `bleach` | Every ability of Rukia Kuchiki | 17 | 10 | 58.8% | `partial` | Kaidō, Sode no Shirayuki, Shikai, Some no mai, Tsukishiro, Tsugi no mai, Hakuren, San no mai, Shirafune, +1 more |
|  | `hxh` | What are Killua Zoldyck's named Nen techniques? | 6 | 4 | 66.7% | `declared` | Godspeed, Thunder Palm |
|  | `bleach` | Every current Espada (the ten active Espada of Aizen's Arrancar army) | 10 | 7 | 70.0% | `declared` | Tier Harribel, Grimmjow Jaegerjaquez, Szayelaporro Granz |
|  | `onepiece` | Every ability of Monkey D. Luffy | 10 | 7 | 70.0% | `exact` | Gomu Gomu no Mi, Gear 5, Red Hawk |
|  | `bleach` | Every ability of Kenpachi Zaraki | 17 | 12 | 70.6% | `partial` | Damage Resistance, Ryōdan, Nozarashi, Shikai, Bankai |
|  | `onepiece` | Every ability of Usopp | 14 | 10 | 71.4% | `partial` | Marksmanship, Engineering Expertise, Tactical Skills, Observation Haki |
|  | `opm` | Every named technique of Bang's Water Stream Rock Smashing Fist in One Punch Man | 7 | 5 | 71.4% | `declared` | Whirlwind Water Stream: Roaring Aura Sky Ripping Fist, Whirlwind Water Stream: Cross Fang Dragon Slayer Fist |
|  | `bleach` | Every technique of Ichigo Kurosaki | 12 | 9 | 75.0% | `partial` | Final Getsuga Tensho, Blut Vene, Shunpo |
|  | `bleach` | Every named Bankai technique Byakuya uses | 4 | 3 | 75.0% | `declared` | Shūkei: Hakuteiken |
|  | `bleach` | Every position Aizen has held | 4 | 3 | 75.0% | `declared` | Instructor at the Shin'ō Academy |
|  | `onepiece` | Every Gear technique of Monkey D. Luffy in One Piece | 4 | 3 | 75.0% | `exact` | Gear 5 |
|  | `onepiece` | How many Sweet Commanders are in the Big Mom Pirates in One Piece? | 4 | 3 | 75.0% | `declared` | Three Sweet Commanders |
|  | `onepiece` | How many All-Stars are in the Beasts Pirates in One Piece? | 4 | 3 | 75.0% | `declared` | Three All-Stars |
|  | `jjk` | Every shikigami of Megumi Fushiguro | 9 | 7 | 77.8% | `partial` | Round Deer, Piercing Ox |

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
| extraction gap | 161 | 57% | `scriptengine/ingest/abilities.py` |
| unlinked page | 63 | 22% | `series/<name>/overrides.yaml` |
| corpus gap | 36 | 13% | `a crawl, or nothing` |
| retrieval gap | 23 | 8% | `scriptengine/retrieve/` |

## What to do about it

In order of items recovered per unit of effort.

1. **retrieval gap, 23 items.** Already in the store and still not returned -- the retriever had every chance. Trace one query end to end before writing code; the diagnosis names the row it expected to find.
   Fix lives in `scriptengine/retrieve/`.
   Biggest cluster: Every ability of Usopp (4 items).

2. **unlinked page, 63 items.** The page exists and nothing ties it to the subject. This is the wiki's shape, not a retriever bug -- declare the link rather than trying to infer it.
   Fix lives in `series/<name>/overrides.yaml`.
   Biggest cluster: Every ability of Byakuya Kuchiki (8 items).

3. **extraction gap, 161 items.** The prose names it and the extraction pass did not return it. Fix the prompt and bump PROMPT_VERSION, or the cached answers survive the change.
   Fix lives in `scriptengine/ingest/abilities.py`.
   Biggest cluster: Every ability of Denji (17 items).

4. **corpus gap, 36 items.** Not in the subject's prose at all. Check the crawl is not stale for that page; if it is current, the wiki does not support the claim and a script must not make it.
   Fix lives in `a crawl, or nothing`.
   Biggest cluster: How many Gods of Destruction exist across the multiverse? (12 items).

## Padded rosters

Closed sets where the engine returned more than twice the canon count. This is the measured defect: recall is respectable and a caller still cannot use the answer, because the right names arrive buried in wrong ones. Roadmap phases 20 (current vs former member) and 21 (a set the wiki barely fills) are the two named causes.

| series | question | canon | returned | ratio | precision |
|---|---|---:|---:|---:|---:|
| `hxh` | Every ability of Gon Freecss | 6 | 126 | 21x | 0.0% |
| `hxh` | What are Gon Freecss's named Nen techniques? | 3 | 53 | 18x | 0.0% |
| `berserk` | Every armor of Guts | 1 | 7 | 7x | 14.3% |
| `hxh` | Every Nen ability of Hisoka | 2 | 13 | 6x | 0.0% |
| `bleach` | Every release state of Kenpachi's Zanpakutō | 2 | 12 | 6x | 0.0% |
| `jjk` | Every member of the Disaster Curses (Mahito's group of unregistered special-grade cursed spirits) | 4 | 22 | 6x | 18.2% |
| `onepiece` | Every named variation of Sanji's Diable Jambe technique in One Piece | 2 | 10 | 5x | 20.0% |
| `jjk` | Every cursed technique of Yuta Okkotsu | 5 | 24 | 5x | 16.7% |
| `hxh` | Every Nen ability of Chrollo | 3 | 13 | 4x | 0.0% |
| `bleach` | Every named technique Ichigo uses with Zangetsu | 4 | 17 | 4x | 5.9% |
| `onepiece` | Every Gear technique of Monkey D. Luffy in One Piece | 4 | 15 | 4x | 20.0% |
| `db` | Who are the members of the Ginyu Force? | 5 | 17 | 3x | 29.4% |
| `db` | Every form of Cell | 4 | 13 | 3x | 30.8% |
| `hxh` | Every Nen ability of Gon | 4 | 13 | 3x | 0.0% |
| `hxh` | What are Leorio Paradinight's named Nen techniques? | 1 | 3 | 3x | 0.0% |

## Where the wrong names come from

Every one of the 651 members returned on a closed set that matched no canon item, by the candidate path that vouched for it. `recall_only` questions are excluded: their gold is a curated core list, so a name outside it is usually right.

| source | count | share | what it means |
|---|---:|---:|---|
| category page | 333 | 51% | Arrived through a category or a declared roster rather than through the character, so the set itself is too broad, rather than the member. |
| heading | 173 | 27% | A section heading on the character's page. Also skips `validate_member`; `ability_sections` is what selects these. |
| prose row | 98 | 15% | Extracted from prose at index time. Skips `validate_member` by design; filtered only by `ability_stopwords` and a word count. The section it came from is the lever. |
| ownership edge | 32 | 5% | The wiki wrote `X -user-> Y`. The only path already validated, and correspondingly the smallest. |
| unattributed | 15 | 2% | No page, no edge, no row, no heading. Nothing vouches for it at all. |

**560 (86%) are vouched for by one path only**, against 76 backed by more than one. Corroboration is the signal the union discards when it deduplicates on lowercased name alone. 5 (1%) are lead-level rows: the section they were extracted from is the bare page title, so they came from the article's opening rather than from any heading.

Sections supplying the most wrong names, from `abilities.section`, the breadcrumb each row was read from.

Worth knowing before acting on this table: `ability_sections` in `series/<name>/overrides.yaml` does **not** filter these. In `scriptengine/retrieve/` it is read in exactly one place (`roster.py:1208`, inside `_section_roster`), so it selects *headings*; `_extracted_roster` never consults it, and prose rows are the majority of what is listed here. Its other reader is `ingest/abilities.py`, which uses it to choose what to extract, so narrowing it there shrinks the next extraction rather than filtering what is already stored. Acting on this table at query time means a section filter in `_extracted_roster`, which is code and needs a server restart, though not a re-extraction.

| count | section |
|---:|---|
| 31 | `Abilities and Powers / Cursed Techniques` |
| 13 | `Abilities and Powers / Cursed Energy` |
| 8 | `Abilities and Powers / Fighting Style` |
| 7 | `Abilities and Powers / Overview` |
| 6 | `Abilities and Powers / Cursed Technique` |
| 6 | `Abilities and Powers / Physical Abilities` |
| 4 | `Abilities and Powers / Cursed Restrictions` |
| 4 | `Abilities and Powers / Influence from "God" / Supernatural Abilities` |
| 3 | `Abilities and Powers / Influence from "God" / Fighting Style` |
| 2 | `Abilities and Powers / Physical Prowess` |
| 2 | `Abilities and Powers / Intelligence` |
| 2 | `Abilities and Powers / Cyborg Modifications` |
| 2 | `Abilities and Powers / Cyborg Modifications / List of Upgrades` |
| 2 | `Garou` |
| 2 | `Abilities and Powers / Human / Fighting Style` |

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

Run metadata: `2026-08-15-1842`, git `5b9e1a2`, server started `2026-08-15T18:42:09+00:00`, 183s wall clock.

Sources for every answer are in `questions/<series>.json`, per item.
