# Page campaign csm/furio — 2026-09-17-0839

Batch `_csm_page_furio.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.8s wall clock.

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
| `-` | set | What are all the named techniques of Furio? | Marksmanship | - | <sub>https://chainsaw-man.fandom.com/wiki/Furio</sub> |
| `-` | set | What are all the affiliations of Furio? | Fourth East High School, Devil Hunter Club | - | <sub>https://chainsaw-man.fandom.com/wiki/Furio</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Furio? | `-` / `-` | 0 found, 1 missing; returned 0 |
| no | set | What are all the affiliations of Furio? | `-` / `-` | 0 found, 2 missing; returned 0 |
| **yes** | fact | What is the status of Furio? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Furio's occupation? | `routed qa` / `-` | High School Student Devil Hunter |
| **yes** | fact | What is Furio's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What are the kanji for Furio's name? | `routed qa` / `-` | フリオ |
| **yes** | fact | What is the romaji of Furio's name? | `routed qa` / `-` | Furio |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
