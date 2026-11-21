# Page campaign csm/mysterious_man — 2026-09-17-0843

Batch `_csm_page_mysterious_man.json`: 8 questions (3 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.1s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/8** |
| set questions exact | 0/3 (0.0%) |
| canon items recovered | 0/3 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Mysterious Man? | Typhoon Devil Contract | - | <sub>https://chainsaw-man.fandom.com/wiki/Mysterious_Man</sub> |
| `-` | set | What are all the aliases of Mysterious Man? | Mohawk Man | - | <sub>https://chainsaw-man.fandom.com/wiki/Mysterious_Man</sub> |
| `-` | set | What are all the affiliations of Mysterious Man? | Unknown | - | <sub>https://chainsaw-man.fandom.com/wiki/Mysterious_Man</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Mysterious Man? | `-` / `-` | 0 found, 1 missing; returned 0 |
| no | set | What are all the aliases of Mysterious Man? | `-` / `-` | 0 found, 1 missing; returned 0 |
| no | set | What are all the affiliations of Mysterious Man? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What are the kanji for Mysterious Man's name? | `routed qa` / `-` | 謎の男 |
| **yes** | fact | What is the romaji of Mysterious Man's name? | `routed qa` / `-` | Nazo no Otoko |
| **yes** | fact | What is Mysterious Man's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Mysterious Man? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Mysterious Man's occupation? | `routed qa` / `-` | Private Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
