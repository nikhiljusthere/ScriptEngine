# Page campaign csm/chapter_173 — 2026-09-17-0822

Batch `_csm_page_chapter_173.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.2s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **10/10** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 10/10 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What is Chapter 173's title? | `routed qa` / `-` | Hard of Hearing |
| **yes** | fact | In which volume does Chapter 173 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | In which chapter does Chapter 173 appear? | `routed qa` / `-` | 173 |
| **yes** | fact | What is the Japanese title of Chapter 173? | `routed qa` / `-` | 少し聞こえてる |
| **yes** | fact | What is the romaji title of Chapter 173? | `routed qa` / `-` | Sukoshi Kikoe Teru |
| **yes** | fact | On which page does Chapter 173 appear? | `routed qa` / `-` | 15 |
| **yes** | fact | What date is associated with Chapter 173? | `routed qa` / `-` | August 7, 2024 |
| **yes** | fact | In which arc does Chapter 173 appear? | `routed qa` / `-` | Aging Devil arc |
| **yes** | fact | What comes before Chapter 173? | `routed qa` / `-` | Chapter 172 |
| **yes** | fact | What comes after Chapter 173? | `routed qa` / `-` | Chapter 174 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
