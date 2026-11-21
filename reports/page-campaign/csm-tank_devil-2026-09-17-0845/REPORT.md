# Page campaign csm/tank_devil — 2026-09-17-0845

Batch `_csm_page_tank_devil.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.5s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/7** |
| set questions exact | 0/2 (0.0%) |
| canon items recovered | 1/3 (33.3%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `exact` | set | What are all the aliases of Tank Devil? | Tank | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Tank_Devil</sub> |
| `exact` | set | What are all the affiliations of Tank Devil? | Mexico (formerly) | Yoru, Power, Leech Devil, Fire Devil, Guillotine Devil, Legs Devil, Teeth Devil, Justice Devil, Eternity Devil, Death Devil, Fami, Famine Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Tank_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the aliases of Tank Devil? | `Devils` / `exact` | 0 found, 1 missing; returned 88 |
| no | set | What are all the affiliations of Tank Devil? | `Devils (Affiliation)` / `exact` | 1 found, 1 missing; returned 88 |
| **yes** | fact | What are the kanji for Tank Devil's name? | `routed qa` / `-` | 戦車の悪魔 |
| **yes** | fact | What is the romaji of Tank Devil's name? | `routed qa` / `-` | Sensha no Akuma |
| **yes** | fact | What is the status of Tank Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Tank Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Tank Devil's occupation? | `routed qa` / `-` | Wild Devil (formerly) |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
