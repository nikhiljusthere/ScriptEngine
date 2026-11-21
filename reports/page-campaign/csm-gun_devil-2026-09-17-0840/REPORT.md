# Page campaign csm/gun_devil — 2026-09-17-0840

Batch `_csm_page_gun_devil.json`: 10 questions (5 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/10** |
| set questions exact | 0/5 (0.0%) |
| canon items recovered | 4/15 (26.7%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Gun Devil? | Bullet Flesh, Passive Regeneration, Bullet Projection | - | <sub>https://chainsaw-man.fandom.com/wiki/Gun_Devil</sub> |
| `exact` | set | What are all the allies of Gun Devil? | Reze | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Gun_Devil</sub> |
| `exact` | set | What are all the enemies of Gun Devil? | Denji, Aki Hayakawa, Himeno | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Gun_Devil</sub> |
| `exact` | set | What are all the aliases of Gun Devil? | Gun | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Gun_Devil</sub> |
| `exact` | set | What are all the affiliations of Gun Devil? | USA (formerly), Soviet Union (formerly), Multiple Governments Across The Globe | Yoru, Power, Leech Devil, Fire Devil, Guillotine Devil, Legs Devil, Teeth Devil, Justice Devil, Eternity Devil, Death Devil, Fami, Famine Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Gun_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Gun Devil? | `-` / `-` | 0 found, 3 missing; returned 0 |
| no | set | What are all the allies of Gun Devil? | `Devils` / `exact` | 2 found, 1 missing; returned 88 |
| no | set | What are all the enemies of Gun Devil? | `Devils` / `exact` | 1 found, 3 missing; returned 88 |
| no | set | What are all the aliases of Gun Devil? | `Devils` / `exact` | 0 found, 1 missing; returned 88 |
| no | set | What are all the affiliations of Gun Devil? | `Devils (Affiliation)` / `exact` | 1 found, 3 missing; returned 88 |
| **yes** | fact | What are the kanji for Gun Devil's name? | `routed qa` / `-` | 銃の悪魔 |
| **yes** | fact | What is the romaji of Gun Devil's name? | `routed qa` / `-` | Jū no Akuma |
| **yes** | fact | What is the status of Gun Devil? | `routed qa` / `-` | Deceased (48%) Alive (52%) |
| **yes** | fact | What is Gun Devil's occupation? | `routed qa` / `-` | Wild Devil (formerly)
Contract Devil for the USA
Contract Devil for Governments |
| **yes** | fact | How old is Gun Devil? | `routed qa` / `-` | 15 years (of known existence) |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
