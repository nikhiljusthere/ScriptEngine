# Page campaign csm/chapter_38 — 2026-09-17-0830

Batch `_csm_page_chapter_38.json`: 12 questions (0 set, 12 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.5s wall clock.

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
| **yes** | fact | What is Chapter 38's title? | `routed qa` / `-` | Easy Revenge! |
| **yes** | fact | In which volume does Chapter 38 appear? | `routed qa` / `-` | 5 |
| **yes** | fact | In which chapter does Chapter 38 appear? | `routed qa` / `-` | 38 |
| **yes** | fact | What is the Japanese title of Chapter 38? | `routed qa` / `-` | 気楽に復讐を! |
| **yes** | fact | What is the romaji title of Chapter 38? | `routed qa` / `-` | Kiraku ni Fukushū o! |
| **yes** | fact | On which page does Chapter 38 appear? | `routed qa` / `-` | 25 |
| **yes** | fact | What date is associated with Chapter 38? | `routed qa` / `-` | September 14, 2019 |
| **yes** | fact | What issue is Chapter 38 from? | `routed qa` / `-` | Issue 2019-42 |
| **yes** | fact | In which episode does Chapter 38 appear? | `routed qa` / `-` | Episode 12 Chainsaw Man – The Movie: Reze Arc |
| **yes** | fact | In which arc does Chapter 38 appear? | `routed qa` / `-` | Katana Man arc Bomb Girl arc |
| **yes** | fact | What comes before Chapter 38? | `routed qa` / `-` | Chapter 37 |
| **yes** | fact | What comes after Chapter 38? | `routed qa` / `-` | Chapter 39 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
