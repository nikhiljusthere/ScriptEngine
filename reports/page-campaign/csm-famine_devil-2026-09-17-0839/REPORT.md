# Page campaign csm/famine_devil — 2026-09-17-0839

Batch `_csm_page_famine_devil.json`: 11 questions (5 set, 6 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.7s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **6/11** |
| set questions exact | 0/5 (0.0%) |
| canon items recovered | 5/13 (38.5%) |
| fact answers present | 6/6 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Famine Devil? | Life Absorption, Immense Healing Factor, Immense Durability, Hand-to-Hand Combat | - | <sub>https://chainsaw-man.fandom.com/wiki/Famine_Devil</sub> |
| `exact` | set | What are all the allies of Famine Devil? | Asa Mitaka | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Famine_Devil</sub> |
| `exact` | set | What are all the enemies of Famine Devil? | - | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Famine_Devil</sub> |
| `exact` | set | What are all the aliases of Famine Devil? | Famine Devil Hunger Devil Hunger (by Makima) Famine (by Yoru) Death Devil (façade by the real Death Devil) | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Famine_Devil</sub> |
| `exact` | set | What are all the affiliations of Famine Devil? | Fourth East High School, Death Devil (brainwashed) | Yoru, Power, Leech Devil, Fire Devil, Guillotine Devil, Legs Devil, Teeth Devil, Justice Devil, Eternity Devil, Death Devil, Fami, Famine Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Famine_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Famine Devil? | `-` / `-` | 0 found, 4 missing; returned 0 |
| no | set | What are all the allies of Famine Devil? | `Devils` / `exact` | 2 found, 1 missing; returned 88 |
| no | set | What are all the enemies of Famine Devil? | `Devils` / `exact` | 2 found, 0 missing; returned 88 |
| no | set | What are all the aliases of Famine Devil? | `Devils` / `exact` | 0 found, 1 missing; returned 88 |
| no | set | What are all the affiliations of Famine Devil? | `Devils (Affiliation)` / `exact` | 1 found, 2 missing; returned 88 |
| **yes** | fact | What are the kanji for Famine Devil's name? | `routed qa` / `-` | キガちゃん |
| **yes** | fact | What is the romaji of Famine Devil's name? | `routed qa` / `-` | Kiga-chan |
| **yes** | fact | What is Famine Devil's gender? | `routed qa` / `-` | Female |
| **yes** | fact | How old is Famine Devil? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Famine Devil? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Famine Devil's occupation? | `routed qa` / `-` | High School Student (cover) Wild Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
