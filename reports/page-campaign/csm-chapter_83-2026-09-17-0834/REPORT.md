# Page campaign csm/chapter_83 — 2026-09-17-0834

Batch `_csm_page_chapter_83.json`: 11 questions (0 set, 11 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.0s wall clock.

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
| **yes** | fact | What is Chapter 83's title? | `routed qa` / `-` | Death, Resurrection, Chainsaw |
| **yes** | fact | In which volume does Chapter 83 appear? | `routed qa` / `-` | 10 |
| **yes** | fact | In which chapter does Chapter 83 appear? | `routed qa` / `-` | 83 |
| **yes** | fact | What is the Japanese title of Chapter 83? | `routed qa` / `-` | 死・復活・チェンソー |
| **yes** | fact | What is the romaji title of Chapter 83? | `routed qa` / `-` | Shi Fukkatsu Chensō |
| **yes** | fact | On which page does Chapter 83 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 83? | `routed qa` / `-` | September 6, 2020 |
| **yes** | fact | What issue is Chapter 83 from? | `routed qa` / `-` | Issue 2020-40 |
| **yes** | fact | In which arc does Chapter 83 appear? | `routed qa` / `-` | Control Devil arc |
| **yes** | fact | What comes before Chapter 83? | `routed qa` / `-` | Chapter 82 |
| **yes** | fact | What comes after Chapter 83? | `routed qa` / `-` | Chapter 84 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
