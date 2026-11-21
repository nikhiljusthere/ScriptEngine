# Page campaign csm/stag_beetle_devil — 2026-09-17-0845

Batch `_csm_page_stag_beetle_devil.json`: 6 questions (1 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.4s wall clock.

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
| `exact` | set | What are all the affiliations of Stag Beetle Devil? | Public Safety Devil Hunters, Tokyo Special Division 6 | Yoru, Power, Leech Devil, Fire Devil, Guillotine Devil, Legs Devil, Teeth Devil, Justice Devil, Eternity Devil, Death Devil, Fami, Famine Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Stag_Beetle_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the affiliations of Stag Beetle Devil? | `Devils (Affiliation)` / `exact` | 0 found, 2 missing; returned 88 |
| **yes** | fact | What are the kanji for Stag Beetle Devil's name? | `routed qa` / `-` | クワガタの悪魔 |
| **yes** | fact | What is the romaji of Stag Beetle Devil's name? | `routed qa` / `-` | Kuwagata no Akuma |
| **yes** | fact | What is the status of Stag Beetle Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Stag Beetle Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Stag Beetle Devil's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
