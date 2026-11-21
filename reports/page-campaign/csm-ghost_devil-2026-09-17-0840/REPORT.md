# Page campaign csm/ghost_devil — 2026-09-17-0840

Batch `_csm_page_ghost_devil.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.5s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/7** |
| set questions exact | 0/2 (0.0%) |
| canon items recovered | 0/6 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Ghost Devil? | Enhanced Strength, Ghost Physiology, Fear Perception, Near Lack of Senses | - | <sub>https://chainsaw-man.fandom.com/wiki/Ghost_Devil</sub> |
| `exact` | set | What are all the superiors of Ghost Devil? | Himeno, Akane Sawatari | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Ghost_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Ghost Devil? | `-` / `-` | 0 found, 4 missing; returned 0 |
| no | set | What are all the superiors of Ghost Devil? | `Devils` / `exact` | 0 found, 2 missing; returned 88 |
| **yes** | fact | What are the kanji for Ghost Devil's name? | `routed qa` / `-` | 幽霊の悪魔 |
| **yes** | fact | What is the romaji of Ghost Devil's name? | `routed qa` / `-` | Yūrei no Akuma |
| **yes** | fact | What is Ghost Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Ghost Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Ghost Devil's occupation? | `routed qa` / `-` | Wild Contract Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
