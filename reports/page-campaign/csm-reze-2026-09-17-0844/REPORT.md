# Page campaign csm/reze — 2026-09-17-0844

Batch `_csm_page_reze.json`: 14 questions (7 set, 7 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 4.6s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **7/14** |
| set questions exact | 0/7 (0.0%) |
| canon items recovered | 0/41 (0.0%) |
| fact answers present | 7/7 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Reze? | Enhanced Strength, Enhanced Speed, Hybrid Transformation, Augmented Durability, Explosion Creation, Explosive Propulsion, Augmented Strength, Augmented Speed, Explosive Spark, Self-Detonation, Torpedo Transformation, Blood Consumption, Nigh-Immortality, Knifemanship, Hand-to-Hand Combat, Bilingual | - | <sub>https://chainsaw-man.fandom.com/wiki/Reze</sub> |
| `-` | set | What are all the allies of Reze? | Typhoon Devil, Denji, Gun Devil | - | <sub>https://chainsaw-man.fandom.com/wiki/Reze</sub> |
| `-` | set | What are all the enemies of Reze? | Beam, Nomo, Kato, Tanabe, Aki Hayakawa, Denji, Makima, Pochita, Kobeni Higashiyama, Angel Devil, Galgali, Masaki Ando | - | <sub>https://chainsaw-man.fandom.com/wiki/Reze</sub> |
| `-` | set | What are all the subordinates of Reze? | Typhoon Devil, Makima | - | <sub>https://chainsaw-man.fandom.com/wiki/Reze</sub> |
| `-` | set | What are all the superiors of Reze? | Aki Hayakawa, Kobeni Higashiyama, Makima | - | <sub>https://chainsaw-man.fandom.com/wiki/Reze</sub> |
| `-` | set | What are all the affiliations of Reze? | Gun Devil (ruse), Soviet Union (formerly), Makima (brainwashed), Tokyo Special Division 5 (formerly) | - | <sub>https://chainsaw-man.fandom.com/wiki/Reze</sub> |
| `-` | set | What are all the aliases of Reze? | Lady Reze Bomb Bomb Girl | - | <sub>https://chainsaw-man.fandom.com/wiki/Reze</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Reze? | `-` / `-` | 0 found, 16 missing; returned 0 |
| no | set | What are all the allies of Reze? | `-` / `-` | 0 found, 3 missing; returned 0 |
| no | set | What are all the enemies of Reze? | `-` / `-` | 0 found, 12 missing; returned 0 |
| no | set | What are all the subordinates of Reze? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the superiors of Reze? | `-` / `-` | 0 found, 3 missing; returned 0 |
| no | set | What are all the affiliations of Reze? | `-` / `-` | 0 found, 4 missing; returned 0 |
| no | set | What are all the aliases of Reze? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What are the kanji for Reze's name? | `routed qa` / `-` | レゼ |
| **yes** | fact | What is the romaji of Reze's name? | `routed qa` / `-` | Reze |
| **yes** | fact | What is Reze's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is the status of Reze? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Reze's occupation? | `routed qa` / `-` | Spy (formerly) Waitress (formerly) |
| **yes** | fact | How old is Reze? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Reze's birthday? | `routed qa` / `-` | Unknown |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
