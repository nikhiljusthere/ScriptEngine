# Page campaign csm/fire_devil — 2026-09-17-0839

Batch `_csm_page_fire_devil.json`: 9 questions (4 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/9** |
| set questions exact | 0/4 (0.0%) |
| canon items recovered | 0/11 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Fire Devil? | Desire Granting, Collective Empowerment, Fire Imagery, Fire Dispersement | - | <sub>https://chainsaw-man.fandom.com/wiki/Fire_Devil</sub> |
| `exact` | set | What are all the allies of Fire Devil? | Class president, Fake Chainsaw Man | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Fire_Devil</sub> |
| `exact` | set | What are all the affiliations of Fire Devil? | Death Devil (brainwashed), Fourth East High School (Allegedly), Barem Bridge, Chainsaw Man Church | Yoru, Power, Leech Devil, Fire Devil, Guillotine Devil, Legs Devil, Teeth Devil, Justice Devil, Eternity Devil, Death Devil, Fami, Famine Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Fire_Devil</sub> |
| `exact` | set | What are all the aliases of Fire Devil? | Justice Devil (fake alias) | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Fire_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Fire Devil? | `-` / `-` | 0 found, 4 missing; returned 0 |
| no | set | What are all the allies of Fire Devil? | `Devils` / `exact` | 0 found, 2 missing; returned 88 |
| no | set | What are all the affiliations of Fire Devil? | `Devils (Affiliation)` / `exact` | 0 found, 4 missing; returned 88 |
| no | set | What are all the aliases of Fire Devil? | `Devils` / `exact` | 0 found, 1 missing; returned 88 |
| **yes** | fact | What are the kanji for Fire Devil's name? | `routed qa` / `-` | 火の悪魔 |
| **yes** | fact | What is the romaji of Fire Devil's name? | `routed qa` / `-` | Hi no Akuma |
| **yes** | fact | What is Fire Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Fire Devil? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Fire Devil's occupation? | `routed qa` / `-` | Wild Contract Devil High School Student (Allegedly) Death's Pawn |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
