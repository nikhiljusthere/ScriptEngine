# Page campaign csm/chapter_21 — 2026-09-17-0827

Batch `_csm_page_chapter_21.json`: 12 questions (0 set, 12 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 6.1s wall clock.

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
| **yes** | fact | What is Chapter 21's title? | `routed qa` / `-` | Taste of a Kiss |
| **yes** | fact | In which volume does Chapter 21 appear? | `routed qa` / `-` | 3 |
| **yes** | fact | In which chapter does Chapter 21 appear? | `routed qa` / `-` | 21 |
| **yes** | fact | What is the Japanese title of Chapter 21? | `routed qa` / `-` | キスのお味 |
| **yes** | fact | What is the romaji title of Chapter 21? | `routed qa` / `-` | Kisu no Oaji |
| **yes** | fact | On which page does Chapter 21 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 21? | `routed qa` / `-` | May 13, 2019 |
| **yes** | fact | What issue is Chapter 21 from? | `routed qa` / `-` | Issue 2019-24 |
| **yes** | fact | In which episode does Chapter 21 appear? | `routed qa` / `-` | Episode 7 |
| **yes** | fact | In which arc does Chapter 21 appear? | `routed qa` / `-` | Eternity Devil arc |
| **yes** | fact | What comes before Chapter 21? | `routed qa` / `-` | Chapter 20 |
| **yes** | fact | What comes after Chapter 21? | `routed qa` / `-` | Chapter 22 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
