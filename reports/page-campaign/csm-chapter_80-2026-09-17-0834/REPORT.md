# Page campaign csm/chapter_80 — 2026-09-17-0834

Batch `_csm_page_chapter_80.json`: 11 questions (0 set, 11 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.2s wall clock.

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
| **yes** | fact | What is Chapter 80's title? | `routed qa` / `-` | A Dog's Feelings |
| **yes** | fact | In which volume does Chapter 80 appear? | `routed qa` / `-` | 10 |
| **yes** | fact | In which chapter does Chapter 80 appear? | `routed qa` / `-` | 80 |
| **yes** | fact | What is the Japanese title of Chapter 80? | `routed qa` / `-` | 犬の気持ち |
| **yes** | fact | What is the romaji title of Chapter 80? | `routed qa` / `-` | Inu no Kimochi |
| **yes** | fact | On which page does Chapter 80 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 80? | `routed qa` / `-` | August 10, 2020 |
| **yes** | fact | What issue is Chapter 80 from? | `routed qa` / `-` | Issue 2020-36-37 |
| **yes** | fact | In which arc does Chapter 80 appear? | `routed qa` / `-` | Control Devil arc |
| **yes** | fact | What comes before Chapter 80? | `routed qa` / `-` | Chapter 79 |
| **yes** | fact | What comes after Chapter 80? | `routed qa` / `-` | Chapter 81 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
