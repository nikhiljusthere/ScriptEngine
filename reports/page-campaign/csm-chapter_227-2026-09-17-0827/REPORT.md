# Page campaign csm/chapter_227 — 2026-09-17-0827

Batch `_csm_page_chapter_227.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.5s wall clock.

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
| **yes** | fact | What is Chapter 227's title? | `routed qa` / `-` | The Taste of Shrimp and Blood |
| **yes** | fact | In which volume does Chapter 227 appear? | `routed qa` / `-` | 24 |
| **yes** | fact | In which chapter does Chapter 227 appear? | `routed qa` / `-` | 227 |
| **yes** | fact | What is the Japanese title of Chapter 227? | `routed qa` / `-` | エビと血の味 |
| **yes** | fact | What is the romaji title of Chapter 227? | `routed qa` / `-` | Ebi to Chi no Aji |
| **yes** | fact | On which page does Chapter 227 appear? | `routed qa` / `-` | 15 |
| **yes** | fact | What date is associated with Chapter 227? | `routed qa` / `-` | January 21, 2026 |
| **yes** | fact | In which arc does Chapter 227 appear? | `routed qa` / `-` | War Devil arc |
| **yes** | fact | What comes before Chapter 227? | `routed qa` / `-` | Chapter 226 |
| **yes** | fact | What comes after Chapter 227? | `routed qa` / `-` | Chapter 228 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
