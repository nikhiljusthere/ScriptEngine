# Page campaign csm/famine_devil — 2026-09-18-0433

Batch `_csm_page_famine_devil.json`: 11 questions (5 set, 6 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 7.5s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **11/11** |
| set questions exact | 5/5 (100.0%) |
| canon items recovered | 17/17 (100.0%) |
| fact answers present | 6/6 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Famine Devil? | `Every named technique of Famine Devil` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the allies of Famine Devil? | `Every ally of Famine Devil` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the enemies of Famine Devil? | `Every enemy of Famine Devil` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the aliases of Famine Devil? | `Famine Devil's aliases` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | set | What are all the affiliations of Famine Devil? | `Famine Devil's affiliations` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | fact | What are the kanji for Famine Devil's name? | `routed qa` / `-` | キガちゃん |
| **yes** | fact | What is the romaji of Famine Devil's name? | `routed qa` / `-` | Kiga-chan |
| **yes** | fact | What is Famine Devil's gender? | `routed qa` / `-` | Female |
| **yes** | fact | How old is Famine Devil? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Famine Devil? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Famine Devil's occupation? | `routed qa` / `-` | High School Student (cover) Wild Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
