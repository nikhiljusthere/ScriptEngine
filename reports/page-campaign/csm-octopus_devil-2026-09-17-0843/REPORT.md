# Page campaign csm/octopus_devil — 2026-09-17-0843

Batch `_csm_page_octopus_devil.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.6s wall clock.

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
| `-` | set | What are all the named techniques of Octopus Devil? | Enhanced Strength, Ink Cloud | - | <sub>https://chainsaw-man.fandom.com/wiki/Octopus_Devil</sub> |
| `exact` | set | What are all the aliases of Octopus Devil? | Octopus | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Octopus_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Octopus Devil? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the aliases of Octopus Devil? | `Devils` / `exact` | 0 found, 1 missing; returned 88 |
| **yes** | fact | What are the kanji for Octopus Devil's name? | `routed qa` / `-` | 蛸の悪魔 |
| **yes** | fact | What is the romaji of Octopus Devil's name? | `routed qa` / `-` | Tako no Akuma |
| **yes** | fact | What is the status of Octopus Devil? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Octopus Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Octopus Devil's occupation? | `routed qa` / `-` | Contract Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
