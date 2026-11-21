# Page campaign csm/chapter_131 — 2026-09-17-0818

Batch `_csm_page_chapter_131.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 4.9s wall clock.

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
| **yes** | fact | What is Chapter 131's title? | `routed qa` / `-` | Taste of Crap |
| **yes** | fact | In which volume does Chapter 131 appear? | `routed qa` / `-` | 15 |
| **yes** | fact | In which chapter does Chapter 131 appear? | `routed qa` / `-` | 131 |
| **yes** | fact | What is the Japanese title of Chapter 131? | `routed qa` / `-` | 糞の味 |
| **yes** | fact | What is the romaji title of Chapter 131? | `routed qa` / `-` | Kuso no Aji |
| **yes** | fact | On which page does Chapter 131 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 131? | `routed qa` / `-` | May 31, 2023 |
| **yes** | fact | In which arc does Chapter 131 appear? | `routed qa` / `-` | Falling Devil arc |
| **yes** | fact | What comes before Chapter 131? | `routed qa` / `-` | Chapter 130 |
| **yes** | fact | What comes after Chapter 131? | `routed qa` / `-` | Chapter 132 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
