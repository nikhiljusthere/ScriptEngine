# Page campaign csm/chapter_70 — 2026-09-17-0833

Batch `_csm_page_chapter_70.json`: 11 questions (0 set, 11 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.3s wall clock.

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
| **yes** | fact | What is Chapter 70's title? | `routed qa` / `-` | Pinch |
| **yes** | fact | In which volume does Chapter 70 appear? | `routed qa` / `-` | 8 |
| **yes** | fact | In which chapter does Chapter 70 appear? | `routed qa` / `-` | 70 |
| **yes** | fact | What is the Japanese title of Chapter 70? | `routed qa` / `-` | 摘む |
| **yes** | fact | What is the romaji title of Chapter 70? | `routed qa` / `-` | Tsumu |
| **yes** | fact | On which page does Chapter 70 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 70? | `routed qa` / `-` | May 25, 2020 |
| **yes** | fact | What issue is Chapter 70 from? | `routed qa` / `-` | Issue 2020-25 |
| **yes** | fact | In which arc does Chapter 70 appear? | `routed qa` / `-` | International Assassins arc |
| **yes** | fact | What comes before Chapter 70? | `routed qa` / `-` | Chapter 69 |
| **yes** | fact | What comes after Chapter 70? | `routed qa` / `-` | Chapter 71 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
