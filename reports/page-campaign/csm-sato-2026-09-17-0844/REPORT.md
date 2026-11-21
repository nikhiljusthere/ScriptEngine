# Page campaign csm/sato — 2026-09-17-0844

Batch `_csm_page_sato.json`: 6 questions (1 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.0s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/6** |
| set questions exact | 0/1 (0.0%) |
| canon items recovered | 0/1 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the affiliations of Sato? | Public Safety Devil Hunters | - | <sub>https://chainsaw-man.fandom.com/wiki/Sato</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the affiliations of Sato? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What are the kanji for Sato's name? | `routed qa` / `-` | 佐藤 |
| **yes** | fact | What is the romaji of Sato's name? | `routed qa` / `-` | Satō |
| **yes** | fact | What is Sato's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Sato? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Sato's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
