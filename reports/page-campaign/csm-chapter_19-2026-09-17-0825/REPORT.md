# Page campaign csm/chapter_19 — 2026-09-17-0825

Batch `_csm_page_chapter_19.json`: 12 questions (0 set, 12 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 6.1s wall clock.

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
| **yes** | fact | What is Chapter 19's title? | `routed qa` / `-` | Nobel Prize |
| **yes** | fact | In which volume does Chapter 19 appear? | `routed qa` / `-` | 3 |
| **yes** | fact | In which chapter does Chapter 19 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What is the Japanese title of Chapter 19? | `routed qa` / `-` | ノーベル賞 |
| **yes** | fact | What is the romaji title of Chapter 19? | `routed qa` / `-` | Nōberu-shō |
| **yes** | fact | On which page does Chapter 19 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 19? | `routed qa` / `-` | April 22, 2019 |
| **yes** | fact | What issue is Chapter 19 from? | `routed qa` / `-` | Issue 2019-21 |
| **yes** | fact | In which episode does Chapter 19 appear? | `routed qa` / `-` | Episode 7 |
| **yes** | fact | In which arc does Chapter 19 appear? | `routed qa` / `-` | Eternity Devil arc |
| **yes** | fact | What comes before Chapter 19? | `routed qa` / `-` | Chapter 18 |
| **yes** | fact | What comes after Chapter 19? | `routed qa` / `-` | Chapter 20 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
