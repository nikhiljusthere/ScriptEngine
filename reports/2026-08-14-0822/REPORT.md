# Canon run 2026-08-14-0822

103 set questions and 32 fact questions over 8 series, asked of the live server and scored against `questions/`.

## Headline

| | |
|---|---:|
| canon items recovered | **626/878** (71.3%) (no change) |
| precision, closed sets | **33.5%** over 85/103 questions (no change) |
| questions at recall 0 | 12/103 |
| questions at recall >= 0.8 | 61/103 |
| confident and wrong | **1** |
| fact answers present in the bundle | 32/32 |
| members returned | 2466 |

**Comparable subset.** The 36 questions carried over from the 2026-08-04 gold set score **164/213** (77.0%). That is the only figure comparable with earlier runs -- the bank grew underneath every other number here, and the questions added since deliberately target known weak spots, so a lower headline is the expected and more honest result.

## What the engine gets wrong

Ordered by what reaches a script. A confidently wrong answer is first because the engine gives a caller no reason to check it; a visibly thin one gets checked.

| | series | question | canon | found | recall | engine said | missing |
|---|---|---|---:|---:|---:|---|---|
| **confident and wrong** | `jjk` | Every first-year student of Tokyo Jujutsu High in 2018 | 3 | 0 | 0.0% | `declared` | Yuji Itadori, Megumi Fushiguro, Nobara Kugisaki |
| recall 0 | `berserk` | Every named member of the original Band of the Falcon | 14 | 0 | 0.0% | `-` | Griffith, Guts, Casca, Judeau, Pippin, Corkus, +8 more |
| recall 0 | `csm` | Every named member of Tokyo Special Division 4 | 14 | 0 | 0.0% | `-` | Makima, Kishibe, Denji, Aki Hayakawa, Power, Himeno, +8 more |
| recall 0 | `berserk` | Every named member of the reborn Band of the Falcon | 10 | 0 | 0.0% | `-` | Griffith, Zodd, Grunbeld, Locus, Irvine, Rakshas, +4 more |
| recall 0 | `csm` | Every Weapon Devil | 7 | 0 | 0.0% | `partial` | Katana Devil, Bomb Devil, Bow Devil, Longsword Devil, Flamethrower Devil, Whip Devil, +1 more |
| recall 0 | `db` | Every form of Majin Buu | 7 | 0 | 0.0% | `partial` | Innocent Buu, Evil Buu, Super Buu, Buutenks, Buuhan, Kid Buu, +1 more |
| recall 0 | `berserk` | Every member of the Four Kings of the World | 4 | 0 | 0.0% | `-` | King of the East, King of the West, King of the South, King of the North |
| recall 0 | `berserk` | Every ability of Serpico | 3 | 0 | 0.0% | `partial` | Rapier, Sylph Sword, Sylph Cloak |
| recall 0 | `csm` | Every devil contract of Aki Hayakawa | 3 | 0 | 0.0% | `partial` | Fox Devil, Curse Devil, Future Devil |
| recall 0 | `opm` | Every disciple of Atomic Samurai | 3 | 0 | 0.0% | `partial` | Iaian, Okamaitachi, Bushidrill |
| recall 0 | `berserk` | Every type of beherit | 2 | 0 | 0.0% | `-` | Beherit, Crimson Beherit |
| recall 0 | `csm` | Every ability of Himeno | 2 | 0 | 0.0% | `partial` | Ghost Devil Contract, Hand-to-Hand Combat |
|  | `onepiece` | Every technique of Zoro | 8 | 1 | 12.5% | `partial` | Oni Giri, Santoryu Ogi: Sanzen Sekai, Tatsumaki, Shishi Sonson, Yakkodori, Toro Nagashi, +1 more |
|  | `berserk` | Every member of the Black Swordsman Party | 12 | 2 | 16.7% | `partial` | Casca, Isidro, Farnese, Serpico, Schierke, Ivalera, +4 more |
|  | `csm` | Every form of Denji | 3 | 1 | 33.3% | `partial` | Human, Chainsaw Devil |
|  | `hxh` | Every Nen ability of Chrollo | 3 | 1 | 33.3% | `partial` | Bookmark, Borrowed Time |
|  | `csm` | Every ability of Aki Hayakawa | 11 | 4 | 36.4% | `partial` | Swordsmanship, Hand-to-Hand Combat, Cooking, Driving, Strong Willpower, Enhanced Durability, +1 more |
|  | `jjk` | Every ability of Sukuna | 32 | 12 | 37.5% | `partial` | Master Hand-to-Hand Combatant, Immense Strength, Immense Speed, Immense Reflexes, Immense Durability, Great Tactical Intellect, +14 more |
|  | `bleach` | Every ability of Rukia Kuchiki | 17 | 7 | 41.2% | `partial` | Immense Spiritual Power, Kaidō, Enhanced Strength, Enhanced Endurance, Sode no Shirayuki, Shikai, +4 more |
|  | `jjk` | Every shikigami of Megumi Fushiguro | 9 | 4 | 44.4% | `partial` | Toad, Great Serpent, Round Deer, Piercing Ox, Mahoraga |
|  | `bleach` | Every form of Ichigo Kurosaki | 11 | 5 | 45.5% | `partial` | Full Hollowfication, Vasto Lorde, Final Getsuga Tensho, Fullbring Bankai, True Shikai, True Bankai |
|  | `jjk` | Every ability of Megumi Fushiguro | 16 | 8 | 50.0% | `partial` | Expert Hand-to-Hand Combatant, Expert Weapons Specialist, Advanced Endurance, Immense Tactical Intellect, Cursed Energy Capacity, Great Serpent, +2 more |
|  | `onepiece` | Every ability of Monkey D. Luffy | 10 | 5 | 50.0% | `partial` | Gomu Gomu no Mi, Gear 5, Supreme King Haki, Observation Haki, Armament Haki |
|  | `db` | Every form of Cell | 4 | 2 | 50.0% | `exact` | Imperfect Cell, Semi-Perfect Cell |
|  | `hxh` | Every Nen ability of Hisoka | 2 | 1 | 50.0% | `partial` | Texture Surprise |
|  | `hxh` | Every ability of Hisoka Morow | 2 | 1 | 50.0% | `partial` | Texture Surprise |
|  | `bleach` | Every ability of Kenpachi Zaraki | 17 | 9 | 52.9% | `partial` | Highly Perceptive Combatant, Immeasurable Spiritual Power, Ryōdan, Immense Strength, Immense Endurance, Nozarashi, +2 more |
|  | `csm` | Every ability of Denji | 17 | 9 | 52.9% | `partial` | Enhanced Human Condition, Enhanced Endurance, Hybrid Transformation, Devil Transformation, Nigh-Immortality, Hand-to-Hand Combat, +2 more |
|  | `jjk` | Every ability of Satoru Gojo | 22 | 12 | 54.5% | `partial` | Master Hand-to-Hand Combatant, Immense Strength, Immense Speed & Reflexes, Immense Endurance, Great Tactical Intellect, Cursed Energy Capacity, +4 more |
|  | `onepiece` | Every ability of Usopp | 9 | 5 | 55.6% | `partial` | Marksmanship, Engineering Expertise, Tactical Skills, Observation Haki |
|  | `jjk` | Every ability of Yuji Itadori | 23 | 13 | 56.5% | `partial` | Weapon Mastery, Master Hand-to-Hand Combatant, Immense Strength, Immense Speed and Reflexes, Immense Durability, Immense Stamina, +4 more |
|  | `bleach` | Every ability of Ichigo Kurosaki | 19 | 11 | 57.9% | `partial` | Zangetsu, Getsuga Jujisho, Chain, Enhanced Getsuga Tensho, Deadly Darts, Ichigo Homerun, +2 more |
|  | `bleach` | Every technique of Ichigo Kurosaki | 6 | 4 | 66.7% | `partial` | Blut Vene, Shunpo |
|  | `csm` | Every ability of Power | 6 | 4 | 66.7% | `partial` | Blood Weaponization, Blood Chainsaw |
|  | `hxh` | Every ability of Gon Freecss | 6 | 4 | 66.7% | `partial` | Jajanken, Limitation Transformation |
|  | `bleach` | Every ability of Sōsuke Aizen | 20 | 14 | 70.0% | `partial` | Immeasurable Spiritual Power, Master Swordsman, Hakuda Master, Immense Strength, Immortality, Shikai |
|  | `bleach` | Every current Espada (the ten active Espada of Aizen's Arrancar army) | 10 | 7 | 70.0% | `declared` | Tier Harribel, Grimmjow Jaegerjaquez, Szayelaporro Granz |
|  | `onepiece` | Every ability of Roronoa Zoro | 10 | 7 | 70.0% | `partial` | Supreme King Haki, Armament Haki, Observation Haki |
|  | `onepiece` | Every ability of Sanji | 10 | 7 | 70.0% | `partial` | Armament Haki, Observation Haki, Supreme King Haki |
|  | `bleach` | Every ability of Byakuya Kuchiki | 17 | 12 | 70.6% | `partial` | Senka, Utsusemi, Immense Endurance, Hurtless Area, Shūkei: Hakuteiken |
|  | `hxh` | Every ability of Killua Zoldyck | 8 | 6 | 75.0% | `partial` | The Snake Awakens, Silent Gaits |
|  | `hxh` | Every Nen ability of Gon | 4 | 3 | 75.0% | `partial` | Jajanken |

## Why each miss is missing

Assigned by a lookup against the store, not by eye.

| bucket | count | share | the fix lives in |
|---|---:|---:|---|
| unlinked page | 80 | 32% | `series/<name>/overrides.yaml` |
| retrieval gap | 78 | 31% | `scriptengine/retrieve/` |
| extraction gap | 68 | 27% | `scriptengine/ingest/abilities.py` |
| corpus gap | 26 | 10% | `a crawl, or nothing` |

## What to do about it

In order of items recovered per unit of effort.

1. **retrieval gap, 78 items.** Already in the store and still not returned -- the retriever had every chance. Trace one query end to end before writing code; the diagnosis names the row it expected to find.
   Fix lives in `scriptengine/retrieve/`.
   Biggest cluster: Every ability of Sukuna (8 items).

2. **unlinked page, 80 items.** The page exists and nothing ties it to the subject. This is the wiki's shape, not a retriever bug -- declare the link rather than trying to infer it.
   Fix lives in `series/<name>/overrides.yaml`.
   Biggest cluster: Every named member of Tokyo Special Division 4 (14 items).

3. **extraction gap, 68 items.** The prose names it and the extraction pass did not return it. Fix the prompt and bump PROMPT_VERSION, or the cached answers survive the change.
   Fix lives in `scriptengine/ingest/abilities.py`.
   Biggest cluster: Every ability of Sukuna (12 items).

4. **corpus gap, 26 items.** Not in the subject's prose at all. Check the crawl is not stale for that page; if it is current, the wiki does not support the claim and a script must not make it.
   Fix lives in `a crawl, or nothing`.
   Biggest cluster: Every named member of the original Band of the Falcon (6 items).

## Padded rosters

Closed sets where the engine returned more than twice the canon count. This is the measured defect: recall is respectable and a caller still cannot use the answer, because the right names arrive buried in wrong ones. Roadmap phases 20 (current vs former member) and 21 (a set the wiki barely fills) are the two named causes.

| series | question | canon | returned | ratio | precision |
|---|---|---:|---:|---:|---:|
| `csm` | Every Weapon Devil | 7 | 88 | 13x | 0.0% |
| `opm` | Every technique of Garou | 6 | 70 | 12x | 8.6% |
| `db` | Every form of Cell | 4 | 41 | 10x | 4.9% |
| `berserk` | Every armor of Guts | 1 | 8 | 8x | 12.5% |
| `opm` | Every technique of Genos | 5 | 38 | 8x | 13.2% |
| `opm` | Every Saitama technique | 7 | 43 | 6x | 14.0% |
| `bleach` | Every technique of Ichigo Kurosaki | 6 | 34 | 6x | 11.8% |
| `db` | Every form of Gohan | 6 | 34 | 6x | 14.7% |
| `jjk` | Every member of the Disaster Curses (Mahito's group of unregistered special-grade cursed spirits) | 4 | 22 | 6x | 18.2% |
| `hxh` | Every Nen ability of Killua | 5 | 27 | 5x | 18.5% |
| `bleach` | Every form of Ulquiorra Cifer | 2 | 10 | 5x | 20.0% |
| `db` | Every form of Goku | 12 | 59 | 5x | 18.6% |
| `onepiece` | Every technique of Sanji | 5 | 24 | 5x | 16.7% |
| `onepiece` | Every sword style of Zoro | 5 | 22 | 4x | 22.7% |
| `jjk` | How many 1v1 battles did Yuji Itadori have with named characters | 6 | 24 | 4x | 25.0% |

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

Run metadata: `2026-08-14-0822`, git `3ceeb61`, server started `2026-08-14T08:22:14+00:00`, 571s wall clock.

Sources for every answer are in `questions/<series>.json`, per item.
