# Page campaign csm/eternity_devil — 2026-09-17-0839

Batch `_csm_page_eternity_devil.json`: 9 questions (4 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/9** |
| set questions exact | 0/4 (0.0%) |
| canon items recovered | 4/12 (33.3%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Eternity Devil? | Pocket Reality Creation, Time Stop, Looped Environment, Avatar Creation | - | <sub>https://chainsaw-man.fandom.com/wiki/Eternity_Devil</sub> |
| `exact` | set | What are all the allies of Eternity Devil? | - | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Eternity_Devil</sub> |
| `exact` | set | What are all the enemies of Eternity Devil? | Denji, Himeno, Asa Mitaka, Hirofumi Yoshida | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Eternity_Devil</sub> |
| `exact` | set | What are all the affiliations of Eternity Devil? | - | Yoru, Power, Leech Devil, Fire Devil, Guillotine Devil, Legs Devil, Teeth Devil, Justice Devil, Eternity Devil, Death Devil, Fami, Famine Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Eternity_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Eternity Devil? | `-` / `-` | 0 found, 4 missing; returned 0 |
| no | set | What are all the allies of Eternity Devil? | `Devils` / `exact` | 2 found, 0 missing; returned 88 |
| no | set | What are all the enemies of Eternity Devil? | `Devils` / `exact` | 1 found, 4 missing; returned 88 |
| no | set | What are all the affiliations of Eternity Devil? | `Devils (Affiliation)` / `exact` | 1 found, 0 missing; returned 88 |
| **yes** | fact | What are the kanji for Eternity Devil's name? | `routed qa` / `-` | 永遠の悪魔 |
| **yes** | fact | What is the romaji of Eternity Devil's name? | `routed qa` / `-` | Eien no Akuma |
| **yes** | fact | What is Eternity Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Eternity Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Eternity Devil's occupation? | `routed qa` / `-` | Wild Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
