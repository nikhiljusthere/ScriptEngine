# Page campaign csm/chapter_97 — 2026-09-17-0836

Batch `_csm_page_chapter_97.json`: 11 questions (0 set, 11 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.2s wall clock.

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
| **yes** | fact | What is Chapter 97's title? | `routed qa` / `-` | I, Love, Chainsaw |
| **yes** | fact | In which volume does Chapter 97 appear? | `routed qa` / `-` | 11 |
| **yes** | fact | In which chapter does Chapter 97 appear? | `routed qa` / `-` | 97 |
| **yes** | fact | What is the Japanese title of Chapter 97? | `routed qa` / `-` | 愛・ラブ・チェンソー |
| **yes** | fact | What is the romaji title of Chapter 97? | `routed qa` / `-` | Ai Rabu Chensō |
| **yes** | fact | On which page does Chapter 97 appear? | `routed qa` / `-` | 23 |
| **yes** | fact | What date is associated with Chapter 97? | `routed qa` / `-` | December 14, 2020 |
| **yes** | fact | What issue is Chapter 97 from? | `routed qa` / `-` | Issue 2021-2 |
| **yes** | fact | In which arc does Chapter 97 appear? | `routed qa` / `-` | Control Devil arc |
| **yes** | fact | What comes before Chapter 97? | `routed qa` / `-` | Chapter 96 |
| **yes** | fact | What comes after Chapter 97? | `routed qa` / `-` | Chapter 98 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
