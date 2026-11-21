# Page campaign csm/fox_devil — 2026-09-17-0839

Batch `_csm_page_fox_devil.json`: 8 questions (3 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/8** |
| set questions exact | 0/3 (0.0%) |
| canon items recovered | 0/6 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Fox Devil? | Enhanced Strength, Enhanced Durability, Blood Consumption | - | <sub>https://chainsaw-man.fandom.com/wiki/Fox_Devil</sub> |
| `exact` | set | What are all the allies of Fox Devil? | Aki Hayakawa, Hirokazu Arai | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Fox_Devil</sub> |
| `exact` | set | What are all the affiliations of Fox Devil? | Public Safety Devil Hunters | Yoru, Power, Leech Devil, Fire Devil, Guillotine Devil, Legs Devil, Teeth Devil, Justice Devil, Eternity Devil, Death Devil, Fami, Famine Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Fox_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Fox Devil? | `-` / `-` | 0 found, 3 missing; returned 0 |
| no | set | What are all the allies of Fox Devil? | `Devils` / `exact` | 0 found, 2 missing; returned 88 |
| no | set | What are all the affiliations of Fox Devil? | `Devils (Affiliation)` / `exact` | 0 found, 1 missing; returned 88 |
| **yes** | fact | What are the kanji for Fox Devil's name? | `routed qa` / `-` | 狐の悪魔 |
| **yes** | fact | What is the romaji of Fox Devil's name? | `routed qa` / `-` | Kitsune no Akuma |
| **yes** | fact | What is the status of Fox Devil? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Fox Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Fox Devil's occupation? | `routed qa` / `-` | Wild Devil (formerly) Contract Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
