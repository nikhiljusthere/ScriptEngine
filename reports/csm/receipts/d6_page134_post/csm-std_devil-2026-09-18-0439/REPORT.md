# Page campaign csm/std_devil — 2026-09-18-0439

Batch `_csm_page_std_devil.json`: 6 questions (1 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 4.0s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **6/6** |
| set questions exact | 1/1 (100.0%) |
| canon items recovered | 1/1 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of STD Devil? | `Every named technique of STD Devil` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for STD Devil's name? | `routed qa` / `-` | 性病の悪魔 |
| **yes** | fact | What is the romaji of STD Devil's name? | `routed qa` / `-` | Seibyō no Akuma |
| **yes** | fact | What is STD Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of STD Devil? | `routed qa` / `-` | Alive |
| **yes** | fact | What is STD Devil's occupation? | `routed qa` / `-` | Contract Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
