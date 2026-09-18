# Page campaign csm/justice_devil — 2026-09-18-0321

Batch `_csm_page_justice_devil.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 5.1s wall clock.

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
| **yes** | set | What are all the named techniques of Justice Devil? | `Every named technique of Justice Devil` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the affiliations of Justice Devil? | `Justice Devil's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Justice Devil's name? | `routed qa` / `-` | 正義の悪魔 |
| **yes** | fact | What is the romaji of Justice Devil's name? | `routed qa` / `-` | Seigi no Akuma |
| **yes** | fact | What is Justice Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Justice Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Justice Devil's occupation? | `routed qa` / `-` | Wild Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
