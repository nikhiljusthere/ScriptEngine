# Page campaign csm/chapter_113 — 2026-09-17-0816

Batch `_csm_page_chapter_113.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.3s wall clock.

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
| **yes** | fact | What is Chapter 113's title? | `routed qa` / `-` | I Wanna See Penguins! |
| **yes** | fact | In which volume does Chapter 113 appear? | `routed qa` / `-` | 14 |
| **yes** | fact | In which chapter does Chapter 113 appear? | `routed qa` / `-` | 113 |
| **yes** | fact | What is the Japanese title of Chapter 113? | `routed qa` / `-` | ペンギンが見たい！ |
| **yes** | fact | What is the romaji title of Chapter 113? | `routed qa` / `-` | Pengin ga mitai! |
| **yes** | fact | On which page does Chapter 113 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 113? | `routed qa` / `-` | December 7, 2022 |
| **yes** | fact | In which arc does Chapter 113 appear? | `routed qa` / `-` | Dating Denji arc |
| **yes** | fact | What comes before Chapter 113? | `routed qa` / `-` | Chapter 112 |
| **yes** | fact | What comes after Chapter 113? | `routed qa` / `-` | Chapter 114 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
