# Page campaign csm/himeno — 2026-09-17-0840

Batch `_csm_page_himeno.json`: 15 questions (9 set, 6 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.3s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **6/15** |
| set questions exact | 0/9 (0.0%) |
| canon items recovered | 0/31 (0.0%) |
| fact answers present | 6/6 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Himeno? | Ghost Devil Contract | - | <sub>https://chainsaw-man.fandom.com/wiki/Himeno</sub> |
| `-` | set | What are all the allies of Himeno? | Aki Hayakawa, Denji, Hirokazu Arai, Kobeni Higashiyama, Power, Makima, Fushi, Kishibe, Ghost Devil | - | <sub>https://chainsaw-man.fandom.com/wiki/Himeno</sub> |
| `-` | set | What are all the enemies of Himeno? | Makima, Katana Man, Akane Sawatari, Gun Devil, Eternity Devil, Loneliness Fiend | - | <sub>https://chainsaw-man.fandom.com/wiki/Himeno</sub> |
| `-` | set | What are all the friends of Himeno? | Denji, Aki Hayakawa | - | <sub>https://chainsaw-man.fandom.com/wiki/Himeno</sub> |
| `-` | set | What are all the romantics of Himeno? | Aki Hayakawa, Denji, Hirokazu Arai | - | <sub>https://chainsaw-man.fandom.com/wiki/Himeno</sub> |
| `-` | set | What are all the subordinates of Himeno? | Makima, Kobeni Higashiyama, Ghost Devil | - | <sub>https://chainsaw-man.fandom.com/wiki/Himeno</sub> |
| `-` | set | What are all the superiors of Himeno? | Aki Hayakawa, Kobeni Higashiyama, Hirokazu Arai, Makima | - | <sub>https://chainsaw-man.fandom.com/wiki/Himeno</sub> |
| `-` | set | What are all the aliases of Himeno? | Barf Woman (by Denji) | - | <sub>https://chainsaw-man.fandom.com/wiki/Himeno</sub> |
| `-` | set | What are all the affiliations of Himeno? | Public Safety Devil Hunters, Tokyo Special Division 4 | - | <sub>https://chainsaw-man.fandom.com/wiki/Himeno</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Himeno? | `-` / `-` | 0 found, 1 missing; returned 0 |
| no | set | What are all the allies of Himeno? | `-` / `-` | 0 found, 9 missing; returned 0 |
| no | set | What are all the enemies of Himeno? | `-` / `-` | 0 found, 6 missing; returned 0 |
| no | set | What are all the friends of Himeno? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the romantics of Himeno? | `-` / `-` | 0 found, 3 missing; returned 0 |
| no | set | What are all the subordinates of Himeno? | `-` / `-` | 0 found, 3 missing; returned 0 |
| no | set | What are all the superiors of Himeno? | `-` / `-` | 0 found, 4 missing; returned 0 |
| no | set | What are all the aliases of Himeno? | `-` / `-` | 0 found, 1 missing; returned 0 |
| no | set | What are all the affiliations of Himeno? | `-` / `-` | 0 found, 2 missing; returned 0 |
| **yes** | fact | What are the kanji for Himeno's name? | `routed qa` / `-` | 姫野 |
| **yes** | fact | What is the romaji of Himeno's name? | `routed qa` / `-` | Himeno |
| **yes** | fact | What is Himeno's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is Himeno's height? | `routed qa` / `-` | 175 cm (5'9") |
| **yes** | fact | What is the status of Himeno? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Himeno's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
