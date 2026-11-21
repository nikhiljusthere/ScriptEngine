# Page campaign csm/chapter_3 — 2026-09-17-0830

Batch `_csm_page_chapter_3.json`: 12 questions (0 set, 12 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.4s wall clock.

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
| **yes** | fact | What is Chapter 3's title? | `routed qa` / `-` | Arrival in Tokyo |
| **yes** | fact | In which volume does Chapter 3 appear? | `routed qa` / `-` | 1 |
| **yes** | fact | In which chapter does Chapter 3 appear? | `routed qa` / `-` | 3 |
| **yes** | fact | What is the Japanese title of Chapter 3? | `routed qa` / `-` | 東京到着 |
| **yes** | fact | What is the romaji title of Chapter 3? | `routed qa` / `-` | Tōkyō Tōchaku |
| **yes** | fact | On which page does Chapter 3 appear? | `routed qa` / `-` | 23 |
| **yes** | fact | What date is associated with Chapter 3? | `routed qa` / `-` | December 17, 2018 |
| **yes** | fact | What issue is Chapter 3 from? | `routed qa` / `-` | Issue 2019-03 |
| **yes** | fact | In which episode does Chapter 3 appear? | `routed qa` / `-` | Episode 2 |
| **yes** | fact | In which arc does Chapter 3 appear? | `routed qa` / `-` | Intro arc |
| **yes** | fact | What comes before Chapter 3? | `routed qa` / `-` | Chapter 2 |
| **yes** | fact | What comes after Chapter 3? | `routed qa` / `-` | Chapter 4 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
