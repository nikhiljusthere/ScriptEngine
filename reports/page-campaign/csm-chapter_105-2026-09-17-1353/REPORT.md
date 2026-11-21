# Page campaign csm/chapter_105 — 2026-09-17-1353

Batch `_csm_page_chapter_105.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T13:38:35+00:00), 12.4s wall clock.

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
| **yes** | fact | What is Chapter 105's title? | `routed qa` / `-` | Red Hot |
| **yes** | fact | In which volume does Chapter 105 appear? | `routed qa` / `-` | 13 |
| **yes** | fact | In which chapter does Chapter 105 appear? | `routed qa` / `-` | 105 |
| **yes** | fact | What is the Japanese title of Chapter 105? | `routed qa` / `-` | 灼熱 |
| **yes** | fact | What is the romaji title of Chapter 105? | `routed qa` / `-` | Shakunetsu |
| **yes** | fact | On which page does Chapter 105 appear? | `routed qa` / `-` | 21 |
| **yes** | fact | What date is associated with Chapter 105? | `routed qa` / `-` | September 28, 2022 |
| **yes** | fact | In which arc does Chapter 105 appear? | `routed qa` / `-` | Justice Devil arc |
| **yes** | fact | What comes before Chapter 105? | `routed qa` / `-` | Chapter 104 |
| **yes** | fact | What comes after Chapter 105? | `routed qa` / `-` | Chapter 106 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
