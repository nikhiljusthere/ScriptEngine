# Page campaign csm/aging_devil_s_victim — 2026-09-18-0430

Batch `_csm_page_aging_devil_s_victim.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 4.8s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **7/7** |
| set questions exact | 2/2 (100.0%) |
| canon items recovered | 2/2 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Aging Devil's Victim? | `Every named technique of Aging Devil's Victim` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | What are all the affiliations of Aging Devil's Victim? | `Aging Devil's Victim's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What is Aging Devil's Victim's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is Aging Devil's Victim's birthday? | `routed qa` / `-` | Before 1917 |
| **yes** | fact | What is the status of Aging Devil's Victim? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Aging Devil's Victim's occupation? | `routed qa` / `-` | Public Safety Devil Hunter (formerly)
Construction Worker |
| **yes** | fact | How old is Aging Devil's Victim? | `routed qa` / `-` | 82+ |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
