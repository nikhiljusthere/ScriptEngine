# Page campaign csm/pingtsi — 2026-09-18-0325

Batch `_csm_page_pingtsi.json`: 8 questions (3 set, 5 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 4.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **8/8** |
| set questions exact | 3/3 (100.0%) |
| canon items recovered | 8/8 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Pingtsi? | `Every named technique of Pingtsi` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the enemies of Pingtsi? | `Every enemy of Pingtsi` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the affiliations of Pingtsi? | `Pingtsi's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Pingtsi's name? | `routed qa` / `-` | ピンツイ |
| **yes** | fact | What is the romaji of Pingtsi's name? | `routed qa` / `-` | Pintsui |
| **yes** | fact | What is Pingtsi's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is the status of Pingtsi? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Pingtsi's occupation? | `routed qa` / `-` | Private Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
