# Page campaign csm/locust_devil — 2026-09-17-0842

Batch `_csm_page_locust_devil.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.7s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/7** |
| set questions exact | 0/2 (0.0%) |
| canon items recovered | 1/5 (20.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Locust Devil? | Swarm Manifestation, Immense Durability, Immense Strength | - | <sub>https://chainsaw-man.fandom.com/wiki/Locust_Devil</sub> |
| `exact` | set | What are all the enemies of Locust Devil? | Denji | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Locust_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Locust Devil? | `-` / `-` | 0 found, 3 missing; returned 0 |
| no | set | What are all the enemies of Locust Devil? | `Devils` / `exact` | 1 found, 1 missing; returned 88 |
| **yes** | fact | What are the kanji for Locust Devil's name? | `routed qa` / `-` | バッタの悪魔 |
| **yes** | fact | What is the romaji of Locust Devil's name? | `routed qa` / `-` | Batta no Akuma |
| **yes** | fact | What is the status of Locust Devil? | `routed qa` / `-` | Erased (original timeline) Unknown (new timeline) |
| **yes** | fact | What is Locust Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Locust Devil's occupation? | `routed qa` / `-` | Wild Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
