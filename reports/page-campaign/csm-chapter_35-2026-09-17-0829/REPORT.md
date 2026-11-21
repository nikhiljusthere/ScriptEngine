# Page campaign csm/chapter_35 — 2026-09-17-0829

Batch `_csm_page_chapter_35.json`: 12 questions (0 set, 12 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 6.3s wall clock.

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
| **yes** | fact | What is Chapter 35's title? | `routed qa` / `-` | Minor |
| **yes** | fact | In which volume does Chapter 35 appear? | `routed qa` / `-` | 5 |
| **yes** | fact | In which chapter does Chapter 35 appear? | `routed qa` / `-` | 35 |
| **yes** | fact | What is the Japanese title of Chapter 35? | `routed qa` / `-` | 未成年 |
| **yes** | fact | What is the romaji title of Chapter 35? | `routed qa` / `-` | Miseinen |
| **yes** | fact | On which page does Chapter 35 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 35? | `routed qa` / `-` | August 26, 2019 |
| **yes** | fact | What issue is Chapter 35 from? | `routed qa` / `-` | Issue 2019-39 |
| **yes** | fact | In which episode does Chapter 35 appear? | `routed qa` / `-` | Episode 11 Episode 12 |
| **yes** | fact | In which arc does Chapter 35 appear? | `routed qa` / `-` | Katana Man arc |
| **yes** | fact | What comes before Chapter 35? | `routed qa` / `-` | Chapter 34 |
| **yes** | fact | What comes after Chapter 35? | `routed qa` / `-` | Chapter 36 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
