# Page campaign csm/furuno — 2026-09-17-0840

Batch `_csm_page_furuno.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/7** |
| set questions exact | 0/2 (0.0%) |
| canon items recovered | 0/4 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the allies of Furuno? | Shiina, Kishibe | - | <sub>https://chainsaw-man.fandom.com/wiki/Furuno</sub> |
| `-` | set | What are all the affiliations of Furuno? | Public Safety Devil Hunters, Tokyo Division 2 | - | <sub>https://chainsaw-man.fandom.com/wiki/Furuno</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the allies of Furuno? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the affiliations of Furuno? | `-` / `-` | 0 found, 2 missing; returned 0 |
| **yes** | fact | What are the kanji for Furuno's name? | `routed qa` / `-` | 古野 |
| **yes** | fact | What is the romaji of Furuno's name? | `routed qa` / `-` | Furuno |
| **yes** | fact | What is Furuno's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Furuno? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Furuno's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
