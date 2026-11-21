# Page campaign csm/guillotine_devil — 2026-09-17-0840

Batch `_csm_page_guillotine_devil.json`: 7 questions (3 set, 4 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.2s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **4/7** |
| set questions exact | 0/3 (0.0%) |
| canon items recovered | 0/4 (0.0%) |
| fact answers present | 4/4 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Guillotine Devil? | Enhanced Durability, Slicing | - | <sub>https://chainsaw-man.fandom.com/wiki/Guillotine_Devil</sub> |
| `exact` | set | What are all the aliases of Guillotine Devil? | Guilly (by Death Devil) | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Guillotine_Devil</sub> |
| `exact` | set | What are all the affiliations of Guillotine Devil? | Death Devil (brainwashed) | Yoru, Power, Leech Devil, Fire Devil, Guillotine Devil, Legs Devil, Teeth Devil, Justice Devil, Eternity Devil, Death Devil, Fami, Famine Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Guillotine_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Guillotine Devil? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the aliases of Guillotine Devil? | `Devils` / `exact` | 0 found, 1 missing; returned 88 |
| no | set | What are all the affiliations of Guillotine Devil? | `Devils (Affiliation)` / `exact` | 0 found, 1 missing; returned 88 |
| **yes** | fact | What are the kanji for Guillotine Devil's name? | `routed qa` / `-` | ギロチンの悪魔 |
| **yes** | fact | What is the romaji of Guillotine Devil's name? | `routed qa` / `-` | Girochin no Akuma |
| **yes** | fact | What is the status of Guillotine Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Guillotine Devil's occupation? | `routed qa` / `-` | Death's Pawn |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
