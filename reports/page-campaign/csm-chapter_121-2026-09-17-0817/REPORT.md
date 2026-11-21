# Page campaign csm/chapter_121 — 2026-09-17-0817

Batch `_csm_page_chapter_121.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 4.8s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **10/10** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 10/10 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What is Chapter 121's title? | `routed qa` / `-` | Theory of Happiness |
| **yes** | fact | In which volume does Chapter 121 appear? | `routed qa` / `-` | 14 |
| **yes** | fact | In which chapter does Chapter 121 appear? | `routed qa` / `-` | 121 |
| **yes** | fact | What is the Japanese title of Chapter 121? | `routed qa` / `-` | 幸福論 |
| **yes** | fact | What is the romaji title of Chapter 121? | `routed qa` / `-` | Kōfuku-ron |
| **yes** | fact | On which page does Chapter 121 appear? | `routed qa` / `-` | 16 |
| **yes** | fact | What date is associated with Chapter 121? | `routed qa` / `-` | February 22, 2023 |
| **yes** | fact | In which arc does Chapter 121 appear? | `routed qa` / `-` | Falling Devil arc |
| **yes** | fact | What comes before Chapter 121? | `routed qa` / `-` | Chapter 120 |
| **yes** | fact | What comes after Chapter 121? | `routed qa` / `-` | Chapter 122 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
