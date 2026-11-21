# Page campaign csm/chapter_7 — 2026-09-17-0834

Batch `_csm_page_chapter_7.json`: 12 questions (0 set, 12 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.8s wall clock.

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
| **yes** | fact | What is Chapter 7's title? | `routed qa` / `-` | Meowy's Whereabouts |
| **yes** | fact | In which volume does Chapter 7 appear? | `routed qa` / `-` | 1 |
| **yes** | fact | In which chapter does Chapter 7 appear? | `routed qa` / `-` | 7 |
| **yes** | fact | What is the Japanese title of Chapter 7? | `routed qa` / `-` | ニャーコの行方 |
| **yes** | fact | What is the romaji title of Chapter 7? | `routed qa` / `-` | Nyāko no Yukue |
| **yes** | fact | On which page does Chapter 7 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 7? | `routed qa` / `-` | January 28, 2019 |
| **yes** | fact | What issue is Chapter 7 from? | `routed qa` / `-` | Issue 2019-09 |
| **yes** | fact | In which episode does Chapter 7 appear? | `routed qa` / `-` | Episode 3 |
| **yes** | fact | In which arc does Chapter 7 appear? | `routed qa` / `-` | Bat Devil arc |
| **yes** | fact | What comes before Chapter 7? | `routed qa` / `-` | Chapter 6 |
| **yes** | fact | What comes after Chapter 7? | `routed qa` / `-` | Chapter 8 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
