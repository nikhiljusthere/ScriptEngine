# Page campaign csm/division_2_vice_captain — 2026-09-18-0318

Batch `_csm_page_division_2_vice_captain.json`: 8 questions (3 set, 5 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 7.8s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **8/8** |
| set questions exact | 3/3 (100.0%) |
| canon items recovered | 4/4 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Division 2 Vice Captain? | `Every named technique of Division 2 Vice Captain` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | What are all the affiliations of Division 2 Vice Captain? | `Division 2 Vice Captain's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the aliases of Division 2 Vice Captain? | `Division 2 Vice Captain's aliases` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Division 2 Vice Captain's name? | `routed qa` / `-` | 対魔２課副隊長 |
| **yes** | fact | What is the romaji of Division 2 Vice Captain's name? | `routed qa` / `-` | Tai Ma 2-ka Fuku Taichō |
| **yes** | fact | What is Division 2 Vice Captain's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Division 2 Vice Captain? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Division 2 Vice Captain's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
