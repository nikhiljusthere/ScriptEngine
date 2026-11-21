# Page campaign csm/chapter_11 — 2026-09-17-1353

Batch `_csm_page_chapter_11.json`: 12 questions (0 set, 12 fact), scored against the live server (started 2026-09-17T13:38:35+00:00), 12.6s wall clock.

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
| **yes** | fact | What is Chapter 11's title? | `routed qa` / `-` | Rescue |
| **yes** | fact | In which volume does Chapter 11 appear? | `routed qa` / `-` | 2 |
| **yes** | fact | In which chapter does Chapter 11 appear? | `routed qa` / `-` | 11 |
| **yes** | fact | What is the Japanese title of Chapter 11? | `routed qa` / `-` | 妥協 |
| **yes** | fact | What is the romaji title of Chapter 11? | `routed qa` / `-` | Dakyō |
| **yes** | fact | On which page does Chapter 11 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 11? | `routed qa` / `-` | February 25, 2019 |
| **yes** | fact | What issue is Chapter 11 from? | `routed qa` / `-` | Issue 2019-13 |
| **yes** | fact | In which episode does Chapter 11 appear? | `routed qa` / `-` | Episode 4 |
| **yes** | fact | In which arc does Chapter 11 appear? | `routed qa` / `-` | Bat Devil arc |
| **yes** | fact | What comes before Chapter 11? | `routed qa` / `-` | Chapter 10 |
| **yes** | fact | What comes after Chapter 11? | `routed qa` / `-` | Chapter 12 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
