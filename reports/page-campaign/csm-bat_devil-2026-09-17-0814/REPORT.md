# Page campaign csm/bat_devil — 2026-09-17-0814

Batch `_csm_page_bat_devil.json`: 9 questions (4 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.7s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/9** |
| set questions exact | 0/4 (0.0%) |
| canon items recovered | 3/15 (20.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Bat Devil? | Enhanced Strength, Enhanced Durability, Bat Wings, Mouth Cannon, Blood Consumption, Enhanced Smell | - | <sub>https://chainsaw-man.fandom.com/wiki/Bat_Devil</sub> |
| `exact` | set | What are all the enemies of Bat Devil? | Denji, Meowy, Asa Mitaka, Yuko | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Bat_Devil</sub> |
| `exact` | set | What are all the affiliations of Bat Devil? | Power (briefly, via coercion) | Yoru, Power, Leech Devil, Fire Devil, Guillotine Devil, Legs Devil, Teeth Devil, Justice Devil, Eternity Devil, Death Devil, Fami, Famine Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Bat_Devil</sub> |
| `exact` | set | What are all the aliases of Bat Devil? | Batty (by Leech Devil) | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Bat_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Bat Devil? | `-` / `-` | 0 found, 6 missing; returned 0 |
| no | set | What are all the enemies of Bat Devil? | `Devils` / `exact` | 2 found, 4 missing; returned 88 |
| no | set | What are all the affiliations of Bat Devil? | `Devils (Affiliation)` / `exact` | 1 found, 1 missing; returned 88 |
| no | set | What are all the aliases of Bat Devil? | `Devils` / `exact` | 0 found, 1 missing; returned 88 |
| **yes** | fact | What are the kanji for Bat Devil's name? | `routed qa` / `-` | コウモリの悪魔 |
| **yes** | fact | What is the romaji of Bat Devil's name? | `routed qa` / `-` | Kōmori no Akuma |
| **yes** | fact | What is Bat Devil's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Bat Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Bat Devil's occupation? | `routed qa` / `-` | Wild Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
