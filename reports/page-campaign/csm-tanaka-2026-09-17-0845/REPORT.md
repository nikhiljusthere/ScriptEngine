# Page campaign csm/tanaka — 2026-09-17-0845

Batch `_csm_page_tanaka.json`: 6 questions (1 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.7s wall clock.

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
| `-` | set | What are all the affiliations of Tanaka? | Fourth East High School | - | <sub>https://chainsaw-man.fandom.com/wiki/Tanaka</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the affiliations of Tanaka? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What is Tanaka's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Tanaka? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Tanaka's occupation? | `routed qa` / `-` | Teacher |
| **yes** | fact | What are the kanji for Tanaka's name? | `routed qa` / `-` | 田中 |
| **yes** | fact | What is the romaji of Tanaka's name? | `routed qa` / `-` | Tanaka |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
