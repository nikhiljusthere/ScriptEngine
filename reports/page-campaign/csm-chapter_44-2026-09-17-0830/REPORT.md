# Page campaign csm/chapter_44 — 2026-09-17-0830

Batch `_csm_page_chapter_44.json`: 12 questions (0 set, 12 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.6s wall clock.

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
| **yes** | fact | What is Chapter 44's title? | `routed qa` / `-` | Boom Boom Boom |
| **yes** | fact | In which volume does Chapter 44 appear? | `routed qa` / `-` | 6 |
| **yes** | fact | In which chapter does Chapter 44 appear? | `routed qa` / `-` | 44 |
| **yes** | fact | What is the Japanese title of Chapter 44? | `routed qa` / `-` | バン バン バン |
| **yes** | fact | What is the romaji title of Chapter 44? | `routed qa` / `-` | Ban Ban Ban |
| **yes** | fact | On which page does Chapter 44 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 44? | `routed qa` / `-` | October 28, 2019 |
| **yes** | fact | What issue is Chapter 44 from? | `routed qa` / `-` | Issue 2019-48 |
| **yes** | fact | In which episode does Chapter 44 appear? | `routed qa` / `-` | Chainsaw Man – The Movie: Reze Arc |
| **yes** | fact | In which arc does Chapter 44 appear? | `routed qa` / `-` | Bomb Girl arc |
| **yes** | fact | What comes before Chapter 44? | `routed qa` / `-` | Chapter 43 |
| **yes** | fact | What comes after Chapter 44? | `routed qa` / `-` | Chapter 45 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
