# Page campaign csm/chapter_218 — 2026-09-17-0826

Batch `_csm_page_chapter_218.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.6s wall clock.

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
| **yes** | fact | What is Chapter 218's title? | `routed qa` / `-` | Eat Me |
| **yes** | fact | In which volume does Chapter 218 appear? | `routed qa` / `-` | 23 |
| **yes** | fact | In which chapter does Chapter 218 appear? | `routed qa` / `-` | 218 |
| **yes** | fact | What is the Japanese title of Chapter 218? | `routed qa` / `-` | 私を食べて |
| **yes** | fact | What is the romaji title of Chapter 218? | `routed qa` / `-` | Watashi wo Tabete |
| **yes** | fact | On which page does Chapter 218 appear? | `routed qa` / `-` | 14 |
| **yes** | fact | What date is associated with Chapter 218? | `routed qa` / `-` | October 29, 2025 |
| **yes** | fact | In which arc does Chapter 218 appear? | `routed qa` / `-` | War Devil arc |
| **yes** | fact | What comes before Chapter 218? | `routed qa` / `-` | Chapter 217 |
| **yes** | fact | What comes after Chapter 218? | `routed qa` / `-` | Chapter 219 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
