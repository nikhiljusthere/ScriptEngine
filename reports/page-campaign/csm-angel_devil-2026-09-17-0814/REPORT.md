# Page campaign csm/angel_devil — 2026-09-17-0814

Batch `_csm_page_angel_devil.json`: 10 questions (4 set, 6 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.5s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **6/10** |
| set questions exact | 0/4 (0.0%) |
| canon items recovered | 0/12 (0.0%) |
| fact answers present | 6/6 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Angel Devil? | Enhanced Reflexes, Angelic Wings, Lifespan Absorption, Lifespan Weapons, Spearmanship, Swordsmanship | - | <sub>https://chainsaw-man.fandom.com/wiki/Angel_Devil</sub> |
| `exact` | set | What are all the allies of Angel Devil? | Aki Hayakawa, Denji, Beam | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Angel_Devil</sub> |
| `exact` | set | What are all the affiliations of Angel Devil? | Public Safety Devil Hunters, Tokyo Special Division 4 | Yoru, Power, Leech Devil, Fire Devil, Guillotine Devil, Legs Devil, Teeth Devil, Justice Devil, Eternity Devil, Death Devil, Fami, Famine Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Angel_Devil</sub> |
| `exact` | set | What are all the aliases of Angel Devil? | Angel | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Angel_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Angel Devil? | `-` / `-` | 0 found, 6 missing; returned 0 |
| no | set | What are all the allies of Angel Devil? | `Devils` / `exact` | 0 found, 3 missing; returned 88 |
| no | set | What are all the affiliations of Angel Devil? | `Devils (Affiliation)` / `exact` | 0 found, 2 missing; returned 88 |
| no | set | What are all the aliases of Angel Devil? | `Devils` / `exact` | 0 found, 1 missing; returned 88 |
| **yes** | fact | What are the kanji for Angel Devil's name? | `routed qa` / `-` | エンジェル 天使の悪魔 |
| **yes** | fact | What is the romaji of Angel Devil's name? | `routed qa` / `-` | Enjeru Tenshi no Akuma |
| **yes** | fact | What is the status of Angel Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Angel Devil's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |
| **yes** | fact | What is Angel Devil's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is Angel Devil's height? | `routed qa` / `-` | 155 cm (5'1") |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
