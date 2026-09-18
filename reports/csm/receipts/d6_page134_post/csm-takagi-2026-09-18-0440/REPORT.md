# Page campaign csm/takagi — 2026-09-18-0440

Batch `_csm_page_takagi.json`: 9 questions (3 set, 6 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 6.0s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **9/9** |
| set questions exact | 3/3 (100.0%) |
| canon items recovered | 10/10 (100.0%) |
| fact answers present | 6/6 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the enemies of Takagi? | `Every enemy of Takagi` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the subordinates of Takagi? | `Every subordinate of Takagi` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the affiliations of Takagi? | `Takagi's affiliations` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | fact | What are the kanji for Takagi's name? | `routed qa` / `-` | 高木 |
| **yes** | fact | What is the romaji of Takagi's name? | `routed qa` / `-` | Takagi |
| **yes** | fact | How old is Takagi? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Takagi's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Takagi? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Takagi's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
