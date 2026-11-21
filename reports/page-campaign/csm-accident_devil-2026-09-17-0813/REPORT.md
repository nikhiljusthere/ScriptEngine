# Page campaign csm/accident_devil — 2026-09-17-0813

Batch `_csm_page_accident_devil.json`: 6 questions (1 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.3s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/6** |
| set questions exact | 0/1 (0.0%) |
| canon items recovered | 1/1 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `exact` | set | What are all the affiliations of Accident Devil? | - | Yoru, Power, Leech Devil, Fire Devil, Guillotine Devil, Legs Devil, Teeth Devil, Justice Devil, Eternity Devil, Death Devil, Fami, Famine Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Accident_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the affiliations of Accident Devil? | `Devils (Affiliation)` / `exact` | 1 found, 0 missing; returned 88 |
| **yes** | fact | What are the kanji for Accident Devil's name? | `routed qa` / `-` | 事故の悪魔 |
| **yes** | fact | What is the romaji of Accident Devil's name? | `routed qa` / `-` | Jiko no Akuma |
| **yes** | fact | What is the status of Accident Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Accident Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Accident Devil's occupation? | `routed qa` / `-` | Wild Devil
Yoru's Pawn |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
