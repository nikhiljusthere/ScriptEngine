# Page campaign csm/chapter_112 — 2026-09-17-1354

Batch `_csm_page_chapter_112.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T13:38:35+00:00), 11.3s wall clock.

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
| **yes** | fact | What is Chapter 112's title? | `routed qa` / `-` | Between Cat and Criminal |
| **yes** | fact | In which volume does Chapter 112 appear? | `routed qa` / `-` | 13 |
| **yes** | fact | In which chapter does Chapter 112 appear? | `routed qa` / `-` | 112 |
| **yes** | fact | What is the Japanese title of Chapter 112? | `routed qa` / `-` | 猫と犯罪者の間 |
| **yes** | fact | What is the romaji title of Chapter 112? | `routed qa` / `-` | Neko to Hanzai-sha no Aida |
| **yes** | fact | On which page does Chapter 112 appear? | `routed qa` / `-` | 27 |
| **yes** | fact | What date is associated with Chapter 112? | `routed qa` / `-` | November 23, 2022 |
| **yes** | fact | In which arc does Chapter 112 appear? | `routed qa` / `-` | Dating Denji arc |
| **yes** | fact | What comes before Chapter 112? | `routed qa` / `-` | Chapter 111 |
| **yes** | fact | What comes after Chapter 112? | `routed qa` / `-` | Chapter 113 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
