# Page campaign csm/yuko — 2026-09-18-0328

Batch `_csm_page_yuko.json`: 9 questions (4 set, 5 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 5.0s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **9/9** |
| set questions exact | 4/4 (100.0%) |
| canon items recovered | 17/17 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Yuko? | `Every named technique of Yuko` / `declared` | 6 found, 0 missing; returned 6 |
| **yes** | set | What are all the enemies of Yuko? | `Every enemy of Yuko` / `declared` | 7 found, 0 missing; returned 7 |
| **yes** | set | What are all the families of Yuko? | `Every family of Yuko` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Yuko? | `Yuko's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What are the kanji for Yuko's name? | `routed qa` / `-` | ユウコ |
| **yes** | fact | What is the romaji of Yuko's name? | `routed qa` / `-` | Yūko |
| **yes** | fact | What is Yuko's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is the status of Yuko? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Yuko's occupation? | `routed qa` / `-` | High School Student Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
