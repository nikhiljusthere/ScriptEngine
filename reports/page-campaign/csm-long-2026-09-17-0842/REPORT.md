# Page campaign csm/long — 2026-09-17-0842

Batch `_csm_page_long.json`: 10 questions (5 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.5s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/10** |
| set questions exact | 0/5 (0.0%) |
| canon items recovered | 0/8 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Long? | Hand-to-Hand Combat | - | <sub>https://chainsaw-man.fandom.com/wiki/Long</sub> |
| `-` | set | What are all the allies of Long? | Quanxi, Power | - | <sub>https://chainsaw-man.fandom.com/wiki/Long</sub> |
| `-` | set | What are all the enemies of Long? | Aldo, Quanxi | - | <sub>https://chainsaw-man.fandom.com/wiki/Long</sub> |
| `-` | set | What are all the subordinates of Long? | Power, Quanxi | - | <sub>https://chainsaw-man.fandom.com/wiki/Long</sub> |
| `-` | set | What are all the affiliations of Long? | Quanxi and the Fiends | - | <sub>https://chainsaw-man.fandom.com/wiki/Long</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Long? | `-` / `-` | 0 found, 1 missing; returned 0 |
| no | set | What are all the allies of Long? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the enemies of Long? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the subordinates of Long? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the affiliations of Long? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What are the kanji for Long's name? | `routed qa` / `-` | ロン |
| **yes** | fact | What is the romaji of Long's name? | `routed qa` / `-` | Ron |
| **yes** | fact | What is the status of Long? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Long's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is Long's occupation? | `routed qa` / `-` | Private Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
