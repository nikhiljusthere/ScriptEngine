# Page campaign csm/chapter_77 — 2026-09-17-0834

Batch `_csm_page_chapter_77.json`: 11 questions (0 set, 11 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 4.8s wall clock.

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
| **yes** | fact | What is Chapter 77's title? | `routed qa` / `-` | Ring Ring Ring |
| **yes** | fact | In which volume does Chapter 77 appear? | `routed qa` / `-` | 9 |
| **yes** | fact | In which chapter does Chapter 77 appear? | `routed qa` / `-` | 77 |
| **yes** | fact | What is the Japanese title of Chapter 77? | `routed qa` / `-` | チャイムチャイムチャイム |
| **yes** | fact | What is the romaji title of Chapter 77? | `routed qa` / `-` | Chaimu Chaimu Chaimu |
| **yes** | fact | On which page does Chapter 77 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 77? | `routed qa` / `-` | July 12, 2020 |
| **yes** | fact | What issue is Chapter 77 from? | `routed qa` / `-` | Issue 2020-32 |
| **yes** | fact | In which arc does Chapter 77 appear? | `routed qa` / `-` | Gun Devil arc |
| **yes** | fact | What comes before Chapter 77? | `routed qa` / `-` | Chapter 76 |
| **yes** | fact | What comes after Chapter 77? | `routed qa` / `-` | Chapter 78 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
