# Page campaign csm/chapter_26 — 2026-09-17-0828

Batch `_csm_page_chapter_26.json`: 12 questions (0 set, 12 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.7s wall clock.

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
| **yes** | fact | What is Chapter 26's title? | `routed qa` / `-` | The Gun is Mightier |
| **yes** | fact | In which volume does Chapter 26 appear? | `routed qa` / `-` | 4 |
| **yes** | fact | In which chapter does Chapter 26 appear? | `routed qa` / `-` | 26 |
| **yes** | fact | What is the Japanese title of Chapter 26? | `routed qa` / `-` | 銃は強し |
| **yes** | fact | What is the romaji title of Chapter 26? | `routed qa` / `-` | Jū wa tsuyoshi |
| **yes** | fact | On which page does Chapter 26 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 26? | `routed qa` / `-` | June 17, 2019 |
| **yes** | fact | What issue is Chapter 26 from? | `routed qa` / `-` | Issue 2019-29 |
| **yes** | fact | In which episode does Chapter 26 appear? | `routed qa` / `-` | Episode 9 |
| **yes** | fact | In which arc does Chapter 26 appear? | `routed qa` / `-` | Katana Man arc |
| **yes** | fact | What comes before Chapter 26? | `routed qa` / `-` | Chapter 25 |
| **yes** | fact | What comes after Chapter 26? | `routed qa` / `-` | Chapter 27 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
