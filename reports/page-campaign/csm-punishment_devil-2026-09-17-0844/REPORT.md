# Page campaign csm/punishment_devil — 2026-09-17-0844

Batch `_csm_page_punishment_devil.json`: 5 questions (1 set, 4 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 1.8s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **4/5** |
| set questions exact | 0/1 (0.0%) |
| canon items recovered | 0/2 (0.0%) |
| fact answers present | 4/4 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `exact` | set | What are all the allies of Punishment Devil? | Yutaro Kurose, Michiko Tendo | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Punishment_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the allies of Punishment Devil? | `Devils` / `exact` | 0 found, 2 missing; returned 88 |
| **yes** | fact | What are the kanji for Punishment Devil's name? | `routed qa` / `-` | 罰の悪魔 |
| **yes** | fact | What is the romaji of Punishment Devil's name? | `routed qa` / `-` | Batsu no Akuma |
| **yes** | fact | What is the status of Punishment Devil? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Punishment Devil's occupation? | `routed qa` / `-` | Contract Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
