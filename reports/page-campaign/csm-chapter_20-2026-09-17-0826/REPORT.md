# Page campaign csm/chapter_20 — 2026-09-17-0826

Batch `_csm_page_chapter_20.json`: 12 questions (0 set, 12 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.8s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **12/12** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 12/12 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What is Chapter 20's title? | `routed qa` / `-` | Drinking |
| **yes** | fact | In which volume does Chapter 20 appear? | `routed qa` / `-` | 3 |
| **yes** | fact | In which chapter does Chapter 20 appear? | `routed qa` / `-` | 20 |
| **yes** | fact | What is the Japanese title of Chapter 20? | `routed qa` / `-` | 飲み |
| **yes** | fact | What is the romaji title of Chapter 20? | `routed qa` / `-` | Nomi |
| **yes** | fact | On which page does Chapter 20 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 20? | `routed qa` / `-` | April 27, 2019 |
| **yes** | fact | What issue is Chapter 20 from? | `routed qa` / `-` | Issue 2019-22-23 |
| **yes** | fact | In which episode does Chapter 20 appear? | `routed qa` / `-` | Episode 7 |
| **yes** | fact | In which arc does Chapter 20 appear? | `routed qa` / `-` | Eternity Devil arc |
| **yes** | fact | What comes before Chapter 20? | `routed qa` / `-` | Chapter 19 |
| **yes** | fact | What comes after Chapter 20? | `routed qa` / `-` | Chapter 21 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
