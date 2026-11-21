# Page campaign csm/chapter_30 — 2026-09-17-0829

Batch `_csm_page_chapter_30.json`: 12 questions (0 set, 12 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.7s wall clock.

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
| **yes** | fact | What is Chapter 30's title? | `routed qa` / `-` | Bruised & Battered |
| **yes** | fact | In which volume does Chapter 30 appear? | `routed qa` / `-` | 4 |
| **yes** | fact | In which chapter does Chapter 30 appear? | `routed qa` / `-` | 30 |
| **yes** | fact | What is the Japanese title of Chapter 30? | `routed qa` / `-` | もっとボロボロ |
| **yes** | fact | What is the romaji title of Chapter 30? | `routed qa` / `-` | Motto Boroboro |
| **yes** | fact | On which page does Chapter 30 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 30? | `routed qa` / `-` | July 13, 2019 |
| **yes** | fact | What issue is Chapter 30 from? | `routed qa` / `-` | Issue 2019-33 |
| **yes** | fact | In which episode does Chapter 30 appear? | `routed qa` / `-` | Episode 10 |
| **yes** | fact | In which arc does Chapter 30 appear? | `routed qa` / `-` | Katana Man arc |
| **yes** | fact | What comes before Chapter 30? | `routed qa` / `-` | Chapter 29 |
| **yes** | fact | What comes after Chapter 30? | `routed qa` / `-` | Chapter 31 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
