# Page campaign csm/chapter_10 — 2026-09-17-1351

Batch `_csm_page_chapter_10.json`: 12 questions (0 set, 12 fact), scored against the live server (started 2026-09-17T13:38:35+00:00), 11.3s wall clock.

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
| **yes** | fact | What is Chapter 10's title? | `routed qa` / `-` | Kon |
| **yes** | fact | In which volume does Chapter 10 appear? | `routed qa` / `-` | 2 |
| **yes** | fact | In which chapter does Chapter 10 appear? | `routed qa` / `-` | 10 |
| **yes** | fact | What is the Japanese title of Chapter 10? | `routed qa` / `-` | コン |
| **yes** | fact | What is the romaji title of Chapter 10? | `routed qa` / `-` | Kon |
| **yes** | fact | On which page does Chapter 10 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 10? | `routed qa` / `-` | February 18, 2019 |
| **yes** | fact | What issue is Chapter 10 from? | `routed qa` / `-` | Issue 2019-12 |
| **yes** | fact | In which episode does Chapter 10 appear? | `routed qa` / `-` | Episode 4 |
| **yes** | fact | What comes before Chapter 10? | `routed qa` / `-` | Chapter 9 |
| **yes** | fact | What comes after Chapter 10? | `routed qa` / `-` | Chapter 11 |
| **yes** | fact | In which arc does Chapter 10 appear? | `routed qa` / `-` | Bat Devil arc |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
