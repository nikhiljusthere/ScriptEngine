# Page campaign csm/grape_devil — 2026-09-17-0840

Batch `_csm_page_grape_devil.json`: 6 questions (1 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/6** |
| set questions exact | 0/1 (0.0%) |
| canon items recovered | 0/2 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `exact` | set | What are all the enemies of Grape Devil? | Galgali, Kobeni Higashiyama | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Grape_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the enemies of Grape Devil? | `Devils` / `exact` | 0 found, 2 missing; returned 88 |
| **yes** | fact | What are the kanji for Grape Devil's name? | `routed qa` / `-` | ブドウの悪魔 |
| **yes** | fact | What is the romaji of Grape Devil's name? | `routed qa` / `-` | Budō no Akuma |
| **yes** | fact | What is the status of Grape Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Grape Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Grape Devil's occupation? | `routed qa` / `-` | Wild Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
