# Canon run 2026-08-14-2131

186 set questions and 132 fact questions over 8 series, asked of the live server and scored against `questions/`.

## Headline

| | |
|---|---:|
| canon items recovered | **888/1384** (64.2%) (-20.8%) |
| precision, closed sets | **23.4%** over 168/186 questions (-35.4%) |
| questions at recall 0 | 68/186 |
| questions at recall >= 0.8 | 88/186 |
| confident and wrong | **14** |
| fact answers present in the bundle | 122/132 |
| members returned | 4125 |

> **The bank changed between these two runs.** Canon grew from 984 to 1384 items (+400), so the deltas above are *not* a clean measurement of the engine: part of any move belongs to the target. A correction that adds a name the engine was already returning raises precision without the retriever changing at all. Compare engine changes only across runs whose canon total matches.

**Comparable subset.** The 36 questions carried over from the 2026-08-04 gold set score **281/313** (89.8%). The bank grew underneath every other number here, and the questions added since deliberately target known weak spots, so a lower headline is the expected and more honest result.

This subset is comparable with earlier runs *only* while its own 313 items are unchanged. The 2026-08-14 bank audit corrected questions inside it -- adding names the wiki documents and the bank had omitted, and aliases for names it had spelled differently -- so its denominator has moved and this figure is no longer a like-for-like comparison with the pre-migration 162/217 (74.7%). It remains a fixed set of *questions*; it is no longer a fixed set of *items*.

## What the engine gets wrong

Ordered by what reaches a script. A confidently wrong answer is first because the engine gives a caller no reason to check it; a visibly thin one gets checked.

| | series | question | canon | found | recall | engine said | missing |
|---|---|---|---:|---:|---:|---|---|
| **confident and wrong** | `opm` | Every named Serious Series technique Saitama uses in One Punch Man | 7 | 0 | 0.0% | `exact` | Serious Punch, Serious Side Hops, Serious Squirt Gun, Serious Table Flip, Serious Sneeze, Serious Headbutt, +1 more |
| **confident and wrong** | `bleach` | Every position Aizen has held | 4 | 0 | 0.0% | `exact` | Captain of the 5th Division, Lieutenant of the 5th Division, Instructor at the Shin'ō Academy, Leader of the Arrancar Army |
| **confident and wrong** | `csm` | Every devil Aki Hayakawa contracted with | 4 | 0 | 0.0% | `declared` | Fox Devil, Curse Devil, Future Devil, Control Devil |
| **confident and wrong** | `bleach` | How many divisions are in the Gotei 13? | 1 | 0 | 0.0% | `declared` | 13 divisions |
| **confident and wrong** | `bleach` | How many captains are in the Gotei 13? | 1 | 0 | 0.0% | `declared` | 13 captains |
| **confident and wrong** | `hxh` | How many phases are in the Hunter Exam? | 1 | 0 | 0.0% | `exact` | 4 phases |
| **confident and wrong** | `hxh` | How many Nen categories exist? | 1 | 0 | 0.0% | `declared` | 6 categories |
| **confident and wrong** | `jjk` | How many Big Three Sorcerer Families exist? | 1 | 0 | 0.0% | `declared` | 3 families |
| **confident and wrong** | `onepiece` | How many members are in the Straw Hat Pirates crew in One Piece? | 1 | 0 | 0.0% | `exact` | 10 members |
| **confident and wrong** | `onepiece` | How many Sweet Commanders are in the Big Mom Pirates in One Piece? | 1 | 0 | 0.0% | `exact` | Three Sweet Commanders |
| **confident and wrong** | `onepiece` | How many All-Stars are in the Beasts Pirates in One Piece? | 1 | 0 | 0.0% | `exact` | Three All-Stars |
| **confident and wrong** | `opm` | How many hero classes are in the Hero Association in One Punch Man? | 1 | 0 | 0.0% | `declared` | Four classes |
| **confident and wrong** | `opm` | How many members are in the Blizzard Group in One Punch Man? | 1 | 0 | 0.0% | `exact` | 38 members |
| **confident and wrong** | `bleach` | Every named Bankai technique Byakuya uses | 4 | 1 | 25.0% | `exact` | Senkei, Ikka Senjinka, Shūkei: Hakuteiken |
| recall 0 | `opm` | Who are the S-Class heroes in One Punch Man? | 17 | 0 | 0.0% | `-` | Blast, Tatsumaki, Bang, Atomic Samurai, Child Emperor, Metal Knight, +11 more |
| recall 0 | `bleach` | Who are the current Gotei 13 captains? | 13 | 0 | 0.0% | `-` | Shunsui Kyōraku, Suì-Fēng, Rōjūrō Ōtoribashi, Isane Kotetsu, Shinji Hirako, Byakuya Kuchiki, +7 more |
| recall 0 | `hxh` | Who are the members of the Phantom Troupe? | 13 | 0 | 0.0% | `-` | Chrollo Lucilfer, Nobunaga Hazama, Machi Komacine, Feitan Portor, Phinks Magcub, Shalnark, +7 more |
| recall 0 | `db` | How many Gods of Destruction exist across the multiverse? | 12 | 0 | 0.0% | `weak` | Beerus (Universe 7), Champa (Universe 6), Belmod (Universe 11), Quitela (Universe 4), Arack (Universe 5), Liquiir (Universe 8), +6 more |
| recall 0 | `hxh` | Who are the Zodiacs of the Hunter Association? | 12 | 0 | 0.0% | `-` | Mizaistom Nana, Cheadle Yorkshire, Ging Freecss, Pariston Hill, Botobai Gigante, Kanzai, +6 more |
| recall 0 | `bleach` | Who are the Espada members? | 11 | 0 | 0.0% | `-` | Yammy Llargo, Coyote Starrk, Baraggan Louisenbairn, Nelliel Tu Odelschwanck, Tier Harribel, Ulquiorra Cifer, +5 more |
| recall 0 | `db` | Every mentor who trained Goku | 11 | 0 | 0.0% | `partial` | Grandpa Gohan, Master Roshi, Korin, Mr. Popo, Kami, King Kai, +5 more |
| recall 0 | `db` | Who are the members of Team Universe 7 in the Tournament of Power? | 10 | 0 | 0.0% | `-` | Goku, Vegeta, Gohan, Piccolo, Android 17, Android 18, +4 more |
| recall 0 | `jjk` | What are Yuji Itadori's named cursed techniques? | 10 | 0 | 0.0% | `-` | Divergent Fist, Black Flash, Blood Manipulation, Piercing Blood, Convergence, Shrine, +4 more |
| recall 0 | `jjk` | What are Satoru Gojo's named cursed techniques? | 10 | 0 | 0.0% | `-` | Limitless, Infinity, Blue, Red, Purple, Reverse Cursed Technique, +4 more |
| recall 0 | `jjk` | What are Sukuna's named cursed techniques? | 10 | 0 | 0.0% | `-` | Shrine, Dismantle, Cleave, Spiderweb, Divine Flame, Malevolent Shrine, +4 more |
| recall 0 | `onepiece` | Who are the current members of the Straw Hat Pirates in One Piece? | 10 | 0 | 0.0% | `-` | Monkey D. Luffy, Roronoa Zoro, Nami, Usopp, Sanji, Tony Tony Chopper, +4 more |
| recall 0 | `db` | How many canonical Super Saiyan forms exist in Dragon Ball? | 9 | 0 | 0.0% | `partial` | Super Saiyan, Super Saiyan 2, Super Saiyan 3, Super Saiyan God, Super Saiyan Blue, Super Saiyan Blue Evolved, +3 more |
| recall 0 | `jjk` | What are Megumi Fushiguro's named shikigami? | 9 | 0 | 0.0% | `-` | Divine Dogs, Divine Dog: Totality, Nue, Great Serpent, Toad, The Well's Unknown Abyss, +3 more |
| recall 0 | `jjk` | Who are the Death Painting Wombs? | 9 | 0 | 0.0% | `-` | Eso, Kechizu, Choso, Noranso, Sho-oso, Tanso, +3 more |
| recall 0 | `opm` | Every major cyborg upgrade Genos has received in One Punch Man | 9 | 0 | 0.0% | `weak` | Anti-Saitama Tactical Arms, Arms Mode, Post-Sea-Monster-Arc Upgrade, G4 Upgrade, Post-Super-Fight-Arc Upgrade, Monster Association Arc Upgrade, +3 more |
| recall 0 | `berserk` | Who are the members of the Black Swordsman Party? | 8 | 0 | 0.0% | `-` | Guts, Puck, Casca, Farnese, Serpico, Isidro, +2 more |
| recall 0 | `jjk` | Who are the notable members of the Zenin Family? | 8 | 0 | 0.0% | `-` | Naobito Zenin, Ogi Zenin, Maki Zenin, Mai Zenin, Megumi Fushiguro, Touji Fushiguro, +2 more |
| recall 0 | `csm` | Every blood weapon Power can create | 7 | 0 | 0.0% | `-` | Blood Hammer, Blood Knife, Blood Spear, Blood Scythe, Blood Dagger, Blood Axe, +1 more |
| recall 0 | `csm` | Who are the members of Tokyo Special Division 4? | 7 | 0 | 0.0% | `-` | Makima, Aki Hayakawa, Denji, Power, Himeno, Kobeni Higashiyama, +1 more |
| recall 0 | `berserk` | Who are the core members of the original Band of the Falcon? | 6 | 0 | 0.0% | `-` | Griffith, Guts, Casca, Judeau, Pippin, Corkus |
| recall 0 | `csm` | Every devil whose power Makima can channel through her control ability | 6 | 0 | 0.0% | `partial` | Angel Devil, Future Devil, Snake Devil, Punishment Devil, Spider Devil, Zombie Devil |
| recall 0 | `hxh` | What are Kurapika's named Nen chains? | 6 | 0 | 0.0% | `-` | Dowsing Chain, Chain Jail, Holy Chain, Judgment Chain, Steal Chain, Stealth Dolphin |
| recall 0 | `berserk` | Every major title Griffith has held | 5 | 0 | 0.0% | `-` | Leader of the original Band of the Falcon, Viscount, White Phoenix General, Supreme Commander of the Midland Regular Army, Femto |
| recall 0 | `berserk` | Every name Casca has been known by | 5 | 0 | 0.0% | `-` | Casca, Big Sis, Elaine, Black Witch, Branded Girl |
| recall 0 | `berserk` | Who are the members of the God Hand? | 5 | 0 | 0.0% | `-` | Void, Slan, Ubik, Conrad, Femto |
| recall 0 | `bleach` | Who are the Schutzstaffel members? | 5 | 0 | 0.0% | `-` | Lille Barro, Gerard Valkyrie, Pernida Parnkgjas, Askin Nakk Le Vaar, Uryū Ishida |
| recall 0 | `db` | Who are the members of the Ginyu Force? | 5 | 0 | 0.0% | `-` | Captain Ginyu, Jeice, Burter, Recoome, Guldo |
| recall 0 | `hxh` | What are Killua Zoldyck's named Nen techniques? | 5 | 0 | 0.0% | `-` | Thunderbolt, Godspeed, Lightning Palm, Thunder Palm, Whirlwind |
| recall 0 | `opm` | Every named martial arts style Garou has mastered in One Punch Man | 5 | 0 | 0.0% | `partial` | Water Stream Rock Smashing Fist, Exploding Heart Release Fist, Whirlwind Iron Cutting Fist, Monster Calamity God Slayer Fist, All Life Eradication Fist |
| recall 0 | `opm` | Every named psychic technique Tatsumaki uses in One Punch Man | 5 | 0 | 0.0% | `partial` | Psychic Binding, Psychic Whirlwind, Psychic Barriers, Chi Manipulation, Psychic Remote |
| recall 0 | `opm` | Every named technique of Bang's Water Stream Rock Smashing Fist in One Punch Man | 5 | 0 | 0.0% | `partial` | Water Stream Encampment, Instant Movement, Piercing Fang, Allsight, Awakening Breath |
| recall 0 | `db` | Every mentor who trained Gohan | 4 | 0 | 0.0% | `partial` | Piccolo, Goku, Shin, Old Kai |
| recall 0 | `db` | Every student Piccolo has trained | 4 | 0 | 0.0% | `-` | Gohan, Goten, Trunks, Pan |
| recall 0 | `jjk` | What are Nobara Kugisaki's named cursed techniques? | 4 | 0 | 0.0% | `-` | Straw Doll Technique, Resonance, Hairpin, Black Flash |
| recall 0 | `onepiece` | Every named version of Nami's Clima-Tact weapon in One Piece | 4 | 0 | 0.0% | `partial` | Clima-Tact, Sorcery Clima-Tact, Clima-Tact Grow Up, Zeus-merged Clima-Tact |
| recall 0 | `bleach` | Every dance of Rukia's Shikai Sode no Shirayuki | 3 | 0 | 0.0% | `weak` | Some no mai, Tsukishiro, Tsugi no mai, Hakuren, San no mai, Shirafune |
| recall 0 | `csm` | Every devil contract Denji has made | 3 | 0 | 0.0% | `partial` | Chainsaw Devil Contract, Blood Devil Contract, Aging Devil Contract |
| recall 0 | `hxh` | What are Gon Freecss's named Nen techniques? | 3 | 0 | 0.0% | `-` | Rock, Paper, Scissors |
| recall 0 | `berserk` | Every weapon Puck uses | 2 | 0 | 0.0% | `partial` | Burdock, Puck Spark |
| recall 0 | `bleach` | Every release state of Kenpachi's Zanpakutō | 2 | 0 | 0.0% | `partial` | Shikai (Nozarashi), Bankai (Unnamed) |
| recall 0 | `hxh` | What are Hisoka Morow's named Nen techniques? | 2 | 0 | 0.0% | `-` | Bungee Gum, Texture Surprise |
| recall 0 | `berserk` | How many members are in the God Hand? | 1 | 0 | 0.0% | `partial` | 5 members |
| recall 0 | `berserk` | How many notable members are in the Black Swordsman Party? | 1 | 0 | 0.0% | `partial` | 12 members |
| recall 0 | `bleach` | How many Espada members are there? | 1 | 0 | 0.0% | `partial` | 10 Espada |
| recall 0 | `bleach` | How many Schutzstaffel members are in the current generation? | 1 | 0 | 0.0% | `-` | 5 members |
| recall 0 | `bleach` | How many Sternritter letters are there? | 1 | 0 | 0.0% | `partial` | 26 letters |
| recall 0 | `csm` | Every division Himeno was affiliated with in Public Safety | 1 | 0 | 0.0% | `-` | Tokyo Special Division 4 |
| recall 0 | `hxh` | What are Leorio Paradinight's named Nen techniques? | 1 | 0 | 0.0% | `-` | Remote Punch |
| recall 0 | `hxh` | How many members are in the Phantom Troupe? | 1 | 0 | 0.0% | `partial` | 13 members |
| recall 0 | `hxh` | How many floors does Heavens Arena have? | 1 | 0 | 0.0% | `partial` | 200 floors |
| recall 0 | `jjk` | How many grades of jujutsu sorcerers exist? | 1 | 0 | 0.0% | `partial` | 6 grades |
| recall 0 | `jjk` | How many special grade jujutsu sorcerers are there? | 1 | 0 | 0.0% | `partial` | 4 special grade sorcerers |
| recall 0 | `jjk` | How many fingers of Sukuna exist? | 1 | 0 | 0.0% | `partial` | 20 fingers |
| recall 0 | `opm` | How many S-Class heroes were there before the Monster Association Arc in One Punch Man? | 1 | 0 | 0.0% | `weak` | 17 S-Class heroes |
|  | `berserk` | Every member of the Black Swordsman Party | 12 | 2 | 16.7% | `partial` | Casca, Isidro, Farnese, Serpico, Schierke, Ivalera, +4 more |
|  | `onepiece` | Every technique of Zoro | 10 | 3 | 30.0% | `partial` | Oni Giri, Santoryu Ogi: Sanzen Sekai, Tatsumaki, Shishi Sonson, Yakkodori, Toro Nagashi, +1 more |
|  | `csm` | Every ability of Aki Hayakawa | 11 | 4 | 36.4% | `partial` | Swordsmanship, Hand-to-Hand Combat, Cooking, Driving, Strong Willpower, Enhanced Durability, +1 more |
|  | `jjk` | Every shikigami of Megumi Fushiguro | 9 | 4 | 44.4% | `partial` | Toad, Great Serpent, Round Deer, Piercing Ox, Mahoraga |
|  | `bleach` | Every form of Ichigo Kurosaki | 12 | 6 | 50.0% | `partial` | Full Hollowfication, Vasto Lorde, Final Getsuga Tensho, Fullbring Bankai, True Shikai, True Bankai |
|  | `csm` | How many members are in the Four Horsemen? | 4 | 2 | 50.0% | `partial` | Control Devil (Makima), War Devil (Yoru) |
|  | `berserk` | Every type of beherit | 2 | 1 | 50.0% | `declared` | Crimson Beherit |
|  | `hxh` | Every Nen ability of Hisoka | 2 | 1 | 50.0% | `partial` | Texture Surprise |
|  | `hxh` | Every ability of Hisoka Morow | 2 | 1 | 50.0% | `partial` | Texture Surprise |
|  | `bleach` | Every ability of Kenpachi Zaraki | 17 | 9 | 52.9% | `partial` | Highly Perceptive Combatant, Immeasurable Spiritual Power, Ryōdan, Immense Strength, Immense Endurance, Nozarashi, +2 more |
|  | `jjk` | Every ability of Satoru Gojo | 22 | 12 | 54.5% | `partial` | Master Hand-to-Hand Combatant, Immense Strength, Immense Speed & Reflexes, Immense Endurance, Great Tactical Intellect, Cursed Energy Capacity, +4 more |
|  | `jjk` | Every ability of Yuji Itadori | 23 | 13 | 56.5% | `partial` | Weapon Mastery, Master Hand-to-Hand Combatant, Immense Strength, Immense Speed and Reflexes, Immense Durability, Immense Stamina, +4 more |
|  | `jjk` | Every ability of Sukuna | 32 | 19 | 59.4% | `partial` | Master Hand-to-Hand Combatant, Immense Strength, Immense Speed, Immense Reflexes, Immense Durability, Great Tactical Intellect, +7 more |
|  | `db` | Which arcs of Dragon Ball Z start at which chapter? | 6 | 4 | 66.7% | `exact` | Saiyan Saga, Cell Saga |
|  | `db` | How many major sagas are in Dragon Ball Z? | 6 | 4 | 66.7% | `exact` | Saiyan Saga, Cell Saga |
|  | `csm` | How many devil hunter divisions are mentioned in Chainsaw Man? | 3 | 2 | 66.7% | `partial` | Tokyo Division 2 |
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

### Fact answers not present in what was served

The engine serves context rather than an answer sentence, so the claim here is only that the correct answer was **not present in the bundle** -- a writer had nothing to write the line from.

| series | question | expected | intruders present |
|---|---|---|---|
| `csm` | What is Denji's hybrid transformation trigger? | Pulling the cord on his chest | - |
| `csm` | Who leads the Four Horsemen? | Control Devil (Makima) | - |
| `jjk` | Who is Satoru Gojo's student? | Yuji Itadori, Megumi Fushiguro, Nobara Kugisaki | - |
| `onepiece` | What is Monkey D. Luffy's current bounty in One Piece? | 3,000,000,000 Belly | - |
| `onepiece` | What is Roronoa Zoro's current bounty in One Piece? | 1,111,000,000 Belly | - |
| `onepiece` | What is Sanji's current bounty in One Piece? | 1,032,000,000 Belly | - |
| `onepiece` | What is Nami's current bounty in One Piece? | 366,000,000 Belly | - |
| `onepiece` | What is Usopp's current bounty in One Piece? | 500,000,000 Belly | - |
| `onepiece` | What type of ship is the Thousand Sunny in One Piece? | Brigantine | - |
| `opm` | What is Genos's hero rank in One Punch Man? | S-Class Rank 14 | - |

## Why each miss is missing

Assigned by a lookup against the store, not by eye.

| bucket | count | share | the fix lives in |
|---|---:|---:|---|
| unlinked page | 206 | 42% | `series/<name>/overrides.yaml` |
| retrieval gap | 148 | 30% | `scriptengine/retrieve/` |
| extraction gap | 76 | 15% | `scriptengine/ingest/abilities.py` |
| corpus gap | 66 | 13% | `a crawl, or nothing` |

## What to do about it

In order of items recovered per unit of effort.

1. **retrieval gap — 148 items.** Already in the store and still not returned -- the retriever had every chance. Trace one query end to end before writing code; the diagnosis names the row it expected to find.
   Fix lives in `scriptengine/retrieve/`.
   Biggest cluster: What are Yuji Itadori's named cursed techniques? (10 items).

2. **unlinked page — 206 items.** The page exists and nothing ties it to the subject. This is the wiki's shape, not a retriever bug -- declare the link rather than trying to infer it.
   Fix lives in `series/<name>/overrides.yaml`.
   Biggest cluster: Who are the S-Class heroes in One Punch Man? (17 items).

3. **extraction gap — 76 items.** The prose names it and the extraction pass did not return it. Fix the prompt and bump PROMPT_VERSION, or the cached answers survive the change.
   Fix lives in `scriptengine/ingest/abilities.py`.
   Biggest cluster: Every ability of Sukuna (12 items).

4. **corpus gap — 66 items.** Not in the subject's prose at all. Check the crawl is not stale for that page; if it is current, the wiki does not support the claim and a script must not make it.
   Fix lives in `a crawl, or nothing`.
   Biggest cluster: How many Gods of Destruction exist across the multiverse? (12 items).

## Padded rosters

Closed sets where the engine returned more than twice the canon count. This is the measured defect: recall is respectable and a caller still cannot use the answer, because the right names arrive buried in wrong ones. Roadmap phases 20 (current vs former member) and 21 (a set the wiki barely fills) are the two named causes.

| series | question | canon | returned | ratio | precision |
|---|---|---:|---:|---:|---:|
| `opm` | How many S-Class heroes were there before the Monster Association Arc in One Punch Man? | 1 | 71 | 71x | 0.0% |
| `jjk` | How many grades of jujutsu sorcerers exist? | 1 | 67 | 67x | 0.0% |
| `jjk` | How many special grade jujutsu sorcerers are there? | 1 | 67 | 67x | 0.0% |
| `bleach` | Every named technique Ichigo uses with Zangetsu | 4 | 200 | 50x | 2.0% |
| `bleach` | Every named Bankai technique Byakuya uses | 4 | 200 | 50x | 0.5% |
| `db` | Every mentor who trained Gohan | 4 | 200 | 50x | 0.0% |
| `csm` | How many special divisions exist in Public Safety Devil Hunters? | 2 | 74 | 37x | 2.7% |
| `bleach` | How many Sternritter letters are there? | 1 | 33 | 33x | 0.0% |
| `bleach` | How many captains are in the Gotei 13? | 1 | 29 | 29x | 0.0% |
| `csm` | How many devil hunter divisions are mentioned in Chainsaw Man? | 3 | 74 | 25x | 2.7% |
| `berserk` | How many notable members are in the Black Swordsman Party? | 1 | 21 | 21x | 0.0% |
| `onepiece` | How many Sweet Commanders are in the Big Mom Pirates in One Piece? | 1 | 20 | 20x | 0.0% |
| `db` | Every mentor who trained Goku | 11 | 200 | 18x | 0.0% |
| `bleach` | How many Espada members are there? | 1 | 18 | 18x | 0.0% |
| `hxh` | How many floors does Heavens Arena have? | 1 | 17 | 17x | 0.0% |

## Where the wrong names come from

Every one of the 2256 members returned on a closed set that matched no canon item, by the candidate path that vouched for it. `recall_only` questions are excluded: their gold is a curated core list, so a name outside it is usually right.

| source | count | share | what it means |
|---|---:|---:|---|
| category page | 1789 | 79% | Arrived through a category or a declared roster rather than through the character, so the set itself is too broad — not the member. |
| prose row | 305 | 14% | Extracted from prose at index time. Skips `validate_member` by design; filtered only by `ability_stopwords` and a word count. The section it came from is the lever. |
| heading | 125 | 6% | A section heading on the character's page. Also skips `validate_member`; `ability_sections` is what selects these. |
| ownership edge | 26 | 1% | The wiki wrote `X -user-> Y`. The only path already validated, and correspondingly the smallest. |
| unattributed | 11 | 0% | No page, no edge, no row, no heading. Nothing vouches for it at all. |

**2103 (93%) are vouched for by one path only**, against 142 backed by more than one. Corroboration is the signal the union discards when it deduplicates on lowercased name alone. 24 (1%) are lead-level rows — the section they were extracted from is the bare page title, so they came from the article's opening rather than from any heading.

Sections supplying the most wrong names, from `abilities.section` — the breadcrumb each row was read from.

Worth knowing before acting on this table: `ability_sections` in `series/<name>/overrides.yaml` does **not** filter these. In `scriptengine/retrieve/` it is read in exactly one place (`roster.py:1208`, inside `_section_roster`), so it selects *headings*; `_extracted_roster` never consults it, and prose rows are the majority of what is listed here. Its other reader is `ingest/abilities.py`, which uses it to choose what to extract — so narrowing it there shrinks the next extraction rather than filtering what is already stored. Acting on this table at query time means a section filter in `_extracted_roster`, which is code and needs a server restart, though not a re-extraction.

| count | section |
|---:|---|
| 61 | `Abilities` |
| 25 | `Powers & Abilities` |
| 24 | `Power` |
| 14 | `Abilities and Powers / Cursed Techniques` |
| 12 | `Abilities / Hybrid Powers` |
| 9 | `Former Powers & Abilities` |
| 9 | `Abilities and Powers / Cursed Energy` |
| 7 | `Powers & Abilities / Natural Abilities` |
| 7 | `Abilities & Powers / Nen` |
| 7 | `Abilities and Powers / Overview` |
| 6 | `Monkey D. Luffy` |
| 6 | `Physical Abilities / Black Leg Style` |
| 6 | `Physical Abilities / Black Leg Style / Diable Jambe` |
| 5 | `Abilities / Physical Abilities` |
| 5 | `Powers & Abilities / Zanpakutō` |

## Offline regression suite

A different measurement: `gold_*.json` checked against the crawl, in-process, boolean. It gates the build; this report does not.

| series | score |
|---|---|
| `berserk` | — --skip-eval |
| `bleach` | — --skip-eval |
| `csm` | — --skip-eval |
| `db` | — --skip-eval |
| `hxh` | — --skip-eval |
| `jjk` | — --skip-eval |
| `onepiece` | — --skip-eval |
| `opm` | — --skip-eval |

## Reproducing

```powershell
python start_scriptengine.py          # the server must be up
python -m scriptengine.cli canon-run
```

The server holds its code in memory, so restart it after any change under `scriptengine/` or the run measures the old code. `canon-run` refuses to start against a server older than the newest source file, because one earlier measurement was taken that way and reported no change from a fix that had worked.

Run metadata: `2026-08-14-2131`, git `b85ef62`, server started `2026-08-14T21:30:54+00:00`, 2569s wall clock.

Sources for every answer are in `questions/<series>.json`, per item.
