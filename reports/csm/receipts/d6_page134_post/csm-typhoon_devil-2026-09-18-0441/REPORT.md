# Page campaign csm/typhoon_devil — 2026-09-18-0441

Batch `_csm_page_typhoon_devil.json`: 9 questions (4 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 6.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **9/9** |
| set questions exact | 4/4 (100.0%) |
| canon items recovered | 8/8 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Typhoon Devil? | `Every named technique of Typhoon Devil` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the allies of Typhoon Devil? | `Every ally of Typhoon Devil` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the enemies of Typhoon Devil? | `Every enemy of Typhoon Devil` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Typhoon Devil? | `Typhoon Devil's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Typhoon Devil's name? | `routed qa` / `-` | 台風の悪魔 |
| **yes** | fact | What is the romaji of Typhoon Devil's name? | `routed qa` / `-` | Taifū no Akuma |
| **yes** | fact | What is the status of Typhoon Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Typhoon Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Typhoon Devil's occupation? | `routed qa` / `-` | Wild Devil Contract Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
