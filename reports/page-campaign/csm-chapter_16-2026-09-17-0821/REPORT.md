# Page campaign csm/chapter_16 — 2026-09-17-0821

Batch `_csm_page_chapter_16.json`: 12 questions (0 set, 12 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.6s wall clock.

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
| **yes** | fact | What is Chapter 16's title? | `routed qa` / `-` | First Taste |
| **yes** | fact | In which volume does Chapter 16 appear? | `routed qa` / `-` | 2 |
| **yes** | fact | In which chapter does Chapter 16 appear? | `routed qa` / `-` | 16 |
| **yes** | fact | What is the Japanese title of Chapter 16? | `routed qa` / `-` | はじめての味 |
| **yes** | fact | What is the romaji title of Chapter 16? | `routed qa` / `-` | Hajimete no Aji |
| **yes** | fact | On which page does Chapter 16 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 16? | `routed qa` / `-` | April 1, 2019 |
| **yes** | fact | What issue is Chapter 16 from? | `routed qa` / `-` | Issue 2019-18 |
| **yes** | fact | In which arc does Chapter 16 appear? | `routed qa` / `-` | Eternity Devil arc |
| **yes** | fact | In which episode does Chapter 16 appear? | `routed qa` / `-` | Episode 6 |
| **yes** | fact | What comes before Chapter 16? | `routed qa` / `-` | Chapter 15 |
| **yes** | fact | What comes after Chapter 16? | `routed qa` / `-` | Chapter 17 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
