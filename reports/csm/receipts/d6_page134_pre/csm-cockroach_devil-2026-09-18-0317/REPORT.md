# Page campaign csm/cockroach_devil — 2026-09-18-0317

Batch `_csm_page_cockroach_devil.json`: 9 questions (2 set, 7 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 5.5s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **9/9** |
| set questions exact | 2/2 (100.0%) |
| canon items recovered | 5/5 (100.0%) |
| fact answers present | 7/7 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Cockroach Devil? | `Every named technique of Cockroach Devil` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the enemies of Cockroach Devil? | `Every enemy of Cockroach Devil` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What are the kanji for Cockroach Devil's name? | `routed qa` / `-` | ゴキブリの悪魔 |
| **yes** | fact | What is the romaji of Cockroach Devil's name? | `routed qa` / `-` | Gokiburi no Akuma |
| **yes** | fact | How old is Cockroach Devil? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Cockroach Devil's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Cockroach Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Cockroach Devil's occupation? | `routed qa` / `-` | Wild Devil |
| **yes** | fact | What is Cockroach Devil's birthday? | `routed qa` / `-` | Unknown |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
