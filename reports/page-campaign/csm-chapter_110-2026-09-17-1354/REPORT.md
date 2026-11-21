# Page campaign csm/chapter_110 — 2026-09-17-1354

Batch `_csm_page_chapter_110.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T13:38:35+00:00), 11.6s wall clock.

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
| **yes** | fact | What is Chapter 110's title? | `routed qa` / `-` | A Ring in the Night |
| **yes** | fact | In which volume does Chapter 110 appear? | `routed qa` / `-` | 13 |
| **yes** | fact | In which chapter does Chapter 110 appear? | `routed qa` / `-` | 110 |
| **yes** | fact | What is the Japanese title of Chapter 110? | `routed qa` / `-` | 夜のチャイム |
| **yes** | fact | What is the romaji title of Chapter 110? | `routed qa` / `-` | Yoru no Chaimu |
| **yes** | fact | On which page does Chapter 110 appear? | `routed qa` / `-` | 18 |
| **yes** | fact | What date is associated with Chapter 110? | `routed qa` / `-` | November 9, 2022 |
| **yes** | fact | In which arc does Chapter 110 appear? | `routed qa` / `-` | Justice Devil arc |
| **yes** | fact | What comes before Chapter 110? | `routed qa` / `-` | Chapter 109 |
| **yes** | fact | What comes after Chapter 110? | `routed qa` / `-` | Chapter 111 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
