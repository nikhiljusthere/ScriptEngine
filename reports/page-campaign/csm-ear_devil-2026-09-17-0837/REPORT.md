# Page campaign csm/ear_devil — 2026-09-17-0837

Batch `_csm_page_ear_devil.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.3s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/7** |
| set questions exact | 0/2 (0.0%) |
| canon items recovered | 0/3 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `exact` | set | What are all the aliases of Ear Devil? | Ear (by Public Safety) | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Ear_Devil</sub> |
| `exact` | set | What are all the affiliations of Ear Devil? | Public Safety Devil Hunters, Tokyo Special Division 5 | Yoru, Power, Leech Devil, Fire Devil, Guillotine Devil, Legs Devil, Teeth Devil, Justice Devil, Eternity Devil, Death Devil, Fami, Famine Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Ear_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the aliases of Ear Devil? | `Devils` / `exact` | 0 found, 1 missing; returned 88 |
| no | set | What are all the affiliations of Ear Devil? | `Devils (Affiliation)` / `exact` | 0 found, 2 missing; returned 88 |
| **yes** | fact | What are the kanji for Ear Devil's name? | `routed qa` / `-` | 耳の悪魔 |
| **yes** | fact | What is the romaji of Ear Devil's name? | `routed qa` / `-` | Mimi no Akuma |
| **yes** | fact | What is Ear Devil's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Ear Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Ear Devil's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
