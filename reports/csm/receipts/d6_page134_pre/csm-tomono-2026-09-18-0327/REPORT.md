# Page campaign csm/tomono — 2026-09-18-0327

Batch `_csm_page_tomono.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 5.0s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **7/7** |
| set questions exact | 2/2 (100.0%) |
| canon items recovered | 5/5 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the allies of Tomono? | `Every ally of Tomono` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the friends of Tomono? | `Every friend of Tomono` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | fact | What are the kanji for Tomono's name? | `routed qa` / `-` | 友野 |
| **yes** | fact | What is the romaji of Tomono's name? | `routed qa` / `-` | Tomono |
| **yes** | fact | What is the status of Tomono? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Tomono's occupation? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Tomono's gender? | `routed qa` / `-` | Male |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
