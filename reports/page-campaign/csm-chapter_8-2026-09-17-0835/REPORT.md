# Page campaign csm/chapter_8 — 2026-09-17-0835

Batch `_csm_page_chapter_8.json`: 12 questions (0 set, 12 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.6s wall clock.

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
| **yes** | fact | What is Chapter 8's title? | `routed qa` / `-` | Chainsaw vs. Bat |
| **yes** | fact | In which volume does Chapter 8 appear? | `routed qa` / `-` | 2 |
| **yes** | fact | In which chapter does Chapter 8 appear? | `routed qa` / `-` | 8 |
| **yes** | fact | What is the Japanese title of Chapter 8? | `routed qa` / `-` | チェーンソーVSコウモリ |
| **yes** | fact | What is the romaji title of Chapter 8? | `routed qa` / `-` | Chēnsō Bāsasu Kōmori |
| **yes** | fact | On which page does Chapter 8 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 8? | `routed qa` / `-` | February 4, 2019 |
| **yes** | fact | What issue is Chapter 8 from? | `routed qa` / `-` | Issue 2019-10 |
| **yes** | fact | In which episode does Chapter 8 appear? | `routed qa` / `-` | Episode 3 |
| **yes** | fact | In which arc does Chapter 8 appear? | `routed qa` / `-` | Bat Devil arc |
| **yes** | fact | What comes before Chapter 8? | `routed qa` / `-` | Chapter 7 |
| **yes** | fact | What comes after Chapter 8? | `routed qa` / `-` | Chapter 9 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
