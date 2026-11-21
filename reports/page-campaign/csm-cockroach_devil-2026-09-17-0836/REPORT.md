# Page campaign csm/cockroach_devil — 2026-09-17-0836

Batch `_csm_page_cockroach_devil.json`: 9 questions (2 set, 7 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.0s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **7/9** |
| set questions exact | 0/2 (0.0%) |
| canon items recovered | 2/5 (40.0%) |
| fact answers present | 7/7 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `exact` | set | What are all the named techniques of Cockroach Devil? | Enhanced Strength, Enhanced Speed, Enhanced Durability | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Cockroach_Devil</sub> |
| `exact` | set | What are all the enemies of Cockroach Devil? | - | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Cockroach_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Cockroach Devil? | `Devils` / `exact` | 0 found, 3 missing; returned 88 |
| no | set | What are all the enemies of Cockroach Devil? | `Devils` / `exact` | 2 found, 0 missing; returned 88 |
| **yes** | fact | What are the kanji for Cockroach Devil's name? | `routed qa` / `-` | ゴキブリの悪魔 |
| **yes** | fact | What is the romaji of Cockroach Devil's name? | `routed qa` / `-` | Gokiburi no Akuma |
| **yes** | fact | How old is Cockroach Devil? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Cockroach Devil's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Cockroach Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Cockroach Devil's occupation? | `routed qa` / `-` | Wild Devil |
| **yes** | fact | What is Cockroach Devil's birthday? | `routed qa` / `-` | Unknown |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
