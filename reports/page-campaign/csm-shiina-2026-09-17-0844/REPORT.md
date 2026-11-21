# Page campaign csm/shiina — 2026-09-17-0844

Batch `_csm_page_shiina.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.2s wall clock.

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
| `-` | set | What are all the allies of Shiina? | Furuno, Kishibe | - | <sub>https://chainsaw-man.fandom.com/wiki/Shiina</sub> |
| `-` | set | What are all the affiliations of Shiina? | Police Force | - | <sub>https://chainsaw-man.fandom.com/wiki/Shiina</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the allies of Shiina? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the affiliations of Shiina? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What are the kanji for Shiina's name? | `routed qa` / `-` | 椎名 |
| **yes** | fact | What is the romaji of Shiina's name? | `routed qa` / `-` | Shiina |
| **yes** | fact | What is Shiina's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Shiina? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Shiina's occupation? | `routed qa` / `-` | Police Officer Riot Soldier |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
