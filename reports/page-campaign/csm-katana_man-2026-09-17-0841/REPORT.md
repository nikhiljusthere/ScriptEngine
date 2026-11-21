# Page campaign csm/katana_man — 2026-09-17-0841

Batch `_csm_page_katana_man.json`: 12 questions (8 set, 4 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 4.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **4/12** |
| set questions exact | 0/8 (0.0%) |
| canon items recovered | 0/41 (0.0%) |
| fact answers present | 4/4 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Katana Man? | Hybrid Transformation, Augmented Strength, Augmented Durability, Augmented Speed, Sword-Draw Dash, Blood Consumption, Nigh-Immortality, Marksmanship, Swordsmanship | - | <sub>https://chainsaw-man.fandom.com/wiki/Katana_Man</sub> |
| `-` | set | What are all the allies of Katana Man? | Akane Sawatari, Nail Fiend, Yoru, Asa Mitaka, Pochita, Denji | - | <sub>https://chainsaw-man.fandom.com/wiki/Katana_Man</sub> |
| `-` | set | What are all the enemies of Katana Man? | Denji, Aki Hayakawa, Kobeni Higashiyama, Pochita, Takagi, Quanxi, Asa Mitaka, Power, Himeno | - | <sub>https://chainsaw-man.fandom.com/wiki/Katana_Man</sub> |
| `-` | set | What are all the rivals of Katana Man? | Pochita, Denji | - | <sub>https://chainsaw-man.fandom.com/wiki/Katana_Man</sub> |
| `-` | set | What are all the subordinates of Katana Man? | Akane Sawatari, Takagi, Makima | - | <sub>https://chainsaw-man.fandom.com/wiki/Katana_Man</sub> |
| `-` | set | What are all the superiors of Katana Man? | Makima, Akane Sawatari, Takagi | - | <sub>https://chainsaw-man.fandom.com/wiki/Katana_Man</sub> |
| `-` | set | What are all the affiliations of Katana Man? | Yakuza (formerly), Gun Devil (ruse), Akane Sawatari (formerly), Makima (brainwashed), Tokyo Special Division 5 (formerly), Public Safety Devil Hunters (temporarily), Tokyo Special Division 7 (formerly), Nail Fiend | - | <sub>https://chainsaw-man.fandom.com/wiki/Katana_Man</sub> |
| `-` | set | What are all the aliases of Katana Man? | Samurai Sword Sideburns Man (by Denji) Katana Samurai | - | <sub>https://chainsaw-man.fandom.com/wiki/Katana_Man</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Katana Man? | `-` / `-` | 0 found, 9 missing; returned 0 |
| no | set | What are all the allies of Katana Man? | `-` / `-` | 0 found, 6 missing; returned 0 |
| no | set | What are all the enemies of Katana Man? | `-` / `-` | 0 found, 9 missing; returned 0 |
| no | set | What are all the rivals of Katana Man? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the subordinates of Katana Man? | `-` / `-` | 0 found, 3 missing; returned 0 |
| no | set | What are all the superiors of Katana Man? | `-` / `-` | 0 found, 3 missing; returned 0 |
| no | set | What are all the affiliations of Katana Man? | `-` / `-` | 0 found, 8 missing; returned 0 |
| no | set | What are all the aliases of Katana Man? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What is Katana Man's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is Katana Man's height? | `routed qa` / `-` | 195 cm (6'5") |
| **yes** | fact | What is the status of Katana Man? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Katana Man's occupation? | `routed qa` / `-` | Yakuza (formerly) Private Devil Hunter (formerly) Public Safety Devil Hunter (formerly) |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
