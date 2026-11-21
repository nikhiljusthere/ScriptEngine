# Page campaign csm/typhoon_devil — 2026-09-17-0846

Batch `_csm_page_typhoon_devil.json`: 9 questions (4 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.2s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/9** |
| set questions exact | 0/4 (0.0%) |
| canon items recovered | 0/8 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Typhoon Devil? | Enhanced Strength, Storm Creation, Water Communication | - | <sub>https://chainsaw-man.fandom.com/wiki/Typhoon_Devil</sub> |
| `exact` | set | What are all the allies of Typhoon Devil? | Reze, Mysterious Man | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Typhoon_Devil</sub> |
| `exact` | set | What are all the enemies of Typhoon Devil? | Denji, Beam | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Typhoon_Devil</sub> |
| `exact` | set | What are all the affiliations of Typhoon Devil? | Reze | Yoru, Power, Leech Devil, Fire Devil, Guillotine Devil, Legs Devil, Teeth Devil, Justice Devil, Eternity Devil, Death Devil, Fami, Famine Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Typhoon_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Typhoon Devil? | `-` / `-` | 0 found, 3 missing; returned 0 |
| no | set | What are all the allies of Typhoon Devil? | `Devils` / `exact` | 0 found, 2 missing; returned 88 |
| no | set | What are all the enemies of Typhoon Devil? | `Devils` / `exact` | 0 found, 2 missing; returned 88 |
| no | set | What are all the affiliations of Typhoon Devil? | `Devils (Affiliation)` / `exact` | 0 found, 1 missing; returned 88 |
| **yes** | fact | What are the kanji for Typhoon Devil's name? | `routed qa` / `-` | 台風の悪魔 |
| **yes** | fact | What is the romaji of Typhoon Devil's name? | `routed qa` / `-` | Taifū no Akuma |
| **yes** | fact | What is the status of Typhoon Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Typhoon Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Typhoon Devil's occupation? | `routed qa` / `-` | Wild Devil Contract Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
