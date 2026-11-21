# Page campaign csm/chapter_5 — 2026-09-17-0832

Batch `_csm_page_chapter_5.json`: 12 questions (0 set, 12 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 6.0s wall clock.

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
| **yes** | fact | What is Chapter 5's title? | `routed qa` / `-` | A Way to Touch Some Boobs |
| **yes** | fact | In which volume does Chapter 5 appear? | `routed qa` / `-` | 1 |
| **yes** | fact | In which chapter does Chapter 5 appear? | `routed qa` / `-` | 5 |
| **yes** | fact | What is the Japanese title of Chapter 5? | `routed qa` / `-` | 胸を揉む方法 |
| **yes** | fact | What is the romaji title of Chapter 5? | `routed qa` / `-` | Munena Momu Hōhō |
| **yes** | fact | On which page does Chapter 5 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 5? | `routed qa` / `-` | January 7, 2019 |
| **yes** | fact | What issue is Chapter 5 from? | `routed qa` / `-` | Issue 2019-06-07 |
| **yes** | fact | In which episode does Chapter 5 appear? | `routed qa` / `-` | Episode 2 Episode 3 |
| **yes** | fact | In which arc does Chapter 5 appear? | `routed qa` / `-` | Bat Devil arc |
| **yes** | fact | What comes before Chapter 5? | `routed qa` / `-` | Chapter 4 |
| **yes** | fact | What comes after Chapter 5? | `routed qa` / `-` | Chapter 6 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
