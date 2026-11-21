# Page campaign csm/future_devil — 2026-09-17-0840

Batch `_csm_page_future_devil.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.6s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/7** |
| set questions exact | 0/2 (0.0%) |
| canon items recovered | 0/2 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Future Devil? | Precognition | - | <sub>https://chainsaw-man.fandom.com/wiki/Future_Devil</sub> |
| `exact` | set | What are all the affiliations of Future Devil? | Public Safety Devil Hunters | Yoru, Power, Leech Devil, Fire Devil, Guillotine Devil, Legs Devil, Teeth Devil, Justice Devil, Eternity Devil, Death Devil, Fami, Famine Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Future_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Future Devil? | `-` / `-` | 0 found, 1 missing; returned 0 |
| no | set | What are all the affiliations of Future Devil? | `Devils (Affiliation)` / `exact` | 0 found, 1 missing; returned 88 |
| **yes** | fact | What are the kanji for Future Devil's name? | `routed qa` / `-` | 未来の悪魔 |
| **yes** | fact | What is the romaji of Future Devil's name? | `routed qa` / `-` | Mirai no Akuma |
| **yes** | fact | What is the status of Future Devil? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Future Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Future Devil's occupation? | `routed qa` / `-` | Wild Devil (formerly) Contract Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
