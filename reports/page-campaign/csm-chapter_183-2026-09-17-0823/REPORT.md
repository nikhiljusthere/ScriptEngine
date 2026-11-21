# Page campaign csm/chapter_183 — 2026-09-17-0823

Batch `_csm_page_chapter_183.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 4.9s wall clock.

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
| **yes** | fact | What is Chapter 183's title? | `routed qa` / `-` | Barf, Head, Perv |
| **yes** | fact | In which volume does Chapter 183 appear? | `routed qa` / `-` | 20 |
| **yes** | fact | In which chapter does Chapter 183 appear? | `routed qa` / `-` | 183 |
| **yes** | fact | What is the Japanese title of Chapter 183? | `routed qa` / `-` | ゲロ・顔・エロ |
| **yes** | fact | What is the romaji title of Chapter 183? | `routed qa` / `-` | Gero, Kao, Ero |
| **yes** | fact | On which page does Chapter 183 appear? | `routed qa` / `-` | 15 |
| **yes** | fact | What date is associated with Chapter 183? | `routed qa` / `-` | November 13, 2024 |
| **yes** | fact | In which arc does Chapter 183 appear? | `routed qa` / `-` | Aging Devil arc |
| **yes** | fact | What comes before Chapter 183? | `routed qa` / `-` | Chapter 182 |
| **yes** | fact | What comes after Chapter 183? | `routed qa` / `-` | Chapter 184 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
