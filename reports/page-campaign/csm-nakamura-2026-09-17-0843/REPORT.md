# Page campaign csm/nakamura — 2026-09-17-0843

Batch `_csm_page_nakamura.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.0s wall clock.

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
| `-` | set | What are all the named techniques of Nakamura? | Fox Devil Contract | - | <sub>https://chainsaw-man.fandom.com/wiki/Nakamura</sub> |
| `-` | set | What are all the affiliations of Nakamura? | Public Safety Devil Hunters, Tokyo Division 2 | - | <sub>https://chainsaw-man.fandom.com/wiki/Nakamura</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Nakamura? | `-` / `-` | 0 found, 1 missing; returned 0 |
| no | set | What are all the affiliations of Nakamura? | `-` / `-` | 0 found, 2 missing; returned 0 |
| **yes** | fact | What is the status of Nakamura? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Nakamura's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |
| **yes** | fact | What is Nakamura's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What are the kanji for Nakamura's name? | `routed qa` / `-` | 中村 |
| **yes** | fact | What is the romaji of Nakamura's name? | `routed qa` / `-` | Nakamura |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
