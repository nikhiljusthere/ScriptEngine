# Page campaign csm/punishment_devil — 2026-09-18-0325

Batch `_csm_page_punishment_devil.json`: 5 questions (1 set, 4 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 3.3s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/5** |
| set questions exact | 1/1 (100.0%) |
| canon items recovered | 2/2 (100.0%) |
| fact answers present | 4/4 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the allies of Punishment Devil? | `Every ally of Punishment Devil` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What are the kanji for Punishment Devil's name? | `routed qa` / `-` | 罰の悪魔 |
| **yes** | fact | What is the romaji of Punishment Devil's name? | `routed qa` / `-` | Batsu no Akuma |
| **yes** | fact | What is the status of Punishment Devil? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Punishment Devil's occupation? | `routed qa` / `-` | Contract Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
