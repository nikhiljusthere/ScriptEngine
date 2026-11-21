# Page campaign csm/madoka — 2026-09-17-0842

Batch `_csm_page_madoka.json`: 6 questions (1 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.5s wall clock.

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
| `-` | set | What are all the affiliations of Madoka? | Public Safety Devil Hunters (formerly), Tokyo Special Division 4 (formerly) | - | <sub>https://chainsaw-man.fandom.com/wiki/Madoka</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the affiliations of Madoka? | `-` / `-` | 0 found, 2 missing; returned 0 |
| **yes** | fact | What are the kanji for Madoka's name? | `routed qa` / `-` | 円 |
| **yes** | fact | What is the romaji of Madoka's name? | `routed qa` / `-` | Madoka |
| **yes** | fact | What is Madoka's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Madoka? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Madoka's occupation? | `routed qa` / `-` | Public Safety Devil Hunter (formerly) |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
