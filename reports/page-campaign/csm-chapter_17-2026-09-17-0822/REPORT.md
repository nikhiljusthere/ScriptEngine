# Page campaign csm/chapter_17 — 2026-09-17-0822

Batch `_csm_page_chapter_17.json`: 12 questions (0 set, 12 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 6.4s wall clock.

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
| **yes** | fact | What is Chapter 17's title? | `routed qa` / `-` | Kill Denji |
| **yes** | fact | In which volume does Chapter 17 appear? | `routed qa` / `-` | 3 |
| **yes** | fact | In which chapter does Chapter 17 appear? | `routed qa` / `-` | 17 |
| **yes** | fact | What is the Japanese title of Chapter 17? | `routed qa` / `-` | デンジを殺せ |
| **yes** | fact | What is the romaji title of Chapter 17? | `routed qa` / `-` | Denji o Korose |
| **yes** | fact | On which page does Chapter 17 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 17? | `routed qa` / `-` | April 8, 2019 |
| **yes** | fact | What issue is Chapter 17 from? | `routed qa` / `-` | Issue 2019-19 |
| **yes** | fact | In which arc does Chapter 17 appear? | `routed qa` / `-` | Eternity Devil arc |
| **yes** | fact | In which episode does Chapter 17 appear? | `routed qa` / `-` | Episode 6 |
| **yes** | fact | What comes before Chapter 17? | `routed qa` / `-` | Chapter 16 |
| **yes** | fact | What comes after Chapter 17? | `routed qa` / `-` | Chapter 18 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
