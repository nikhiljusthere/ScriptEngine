# Page campaign csm/chapter_91 — 2026-09-17-0835

Batch `_csm_page_chapter_91.json`: 11 questions (0 set, 11 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.4s wall clock.

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
| **yes** | fact | What is Chapter 91's title? | `routed qa` / `-` | Power, Power, Power |
| **yes** | fact | In which volume does Chapter 91 appear? | `routed qa` / `-` | 11 |
| **yes** | fact | In which chapter does Chapter 91 appear? | `routed qa` / `-` | 91 |
| **yes** | fact | What is the Japanese title of Chapter 91? | `routed qa` / `-` | パワー・パワー・パワー |
| **yes** | fact | What is the romaji title of Chapter 91? | `routed qa` / `-` | Pawā Pawā Pawā |
| **yes** | fact | On which page does Chapter 91 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 91? | `routed qa` / `-` | November 2, 2020 |
| **yes** | fact | What issue is Chapter 91 from? | `routed qa` / `-` | Issue 2020-48 |
| **yes** | fact | In which arc does Chapter 91 appear? | `routed qa` / `-` | Control Devil arc |
| **yes** | fact | What comes before Chapter 91? | `routed qa` / `-` | Chapter 90 |
| **yes** | fact | What comes after Chapter 91? | `routed qa` / `-` | Chapter 92 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
