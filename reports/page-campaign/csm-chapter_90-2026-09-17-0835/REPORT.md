# Page campaign csm/chapter_90 — 2026-09-17-0835

Batch `_csm_page_chapter_90.json`: 11 questions (0 set, 11 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 6.1s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **11/11** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 11/11 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What is Chapter 90's title? | `routed qa` / `-` | Super Power |
| **yes** | fact | In which volume does Chapter 90 appear? | `routed qa` / `-` | 11 |
| **yes** | fact | In which chapter does Chapter 90 appear? | `routed qa` / `-` | 90 |
| **yes** | fact | What is the Japanese title of Chapter 90? | `routed qa` / `-` | 超パワー |
| **yes** | fact | What is the romaji title of Chapter 90? | `routed qa` / `-` | Chō Pawā |
| **yes** | fact | On which page does Chapter 90 appear? | `routed qa` / `-` | 21 |
| **yes** | fact | What date is associated with Chapter 90? | `routed qa` / `-` | October 26, 2020 |
| **yes** | fact | What issue is Chapter 90 from? | `routed qa` / `-` | Issue 2020-47 |
| **yes** | fact | In which arc does Chapter 90 appear? | `routed qa` / `-` | Control Devil arc |
| **yes** | fact | What comes before Chapter 90? | `routed qa` / `-` | Chapter 89 |
| **yes** | fact | What comes after Chapter 90? | `routed qa` / `-` | Chapter 91 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
