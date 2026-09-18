# Page campaign csm/aging_devil — 2026-09-18-0315

Batch `_csm_page_aging_devil.json`: 10 questions (4 set, 6 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 6.3s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **10/10** |
| set questions exact | 4/4 (100.0%) |
| canon items recovered | 15/15 (100.0%) |
| fact answers present | 6/6 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Aging Devil? | `Every named technique of Aging Devil` / `declared` | 7 found, 0 missing; returned 7 |
| **yes** | set | What are all the enemies of Aging Devil? | `Every enemy of Aging Devil` / `declared` | 6 found, 0 missing; returned 6 |
| **yes** | set | What are all the aliases of Aging Devil? | `Aging Devil's aliases` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | What are all the affiliations of Aging Devil? | `Aging Devil's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Aging Devil's name? | `routed qa` / `-` | 老いの悪魔 |
| **yes** | fact | What is the romaji of Aging Devil's name? | `routed qa` / `-` | Oi no Akuma |
| **yes** | fact | What is Aging Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Aging Devil? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Aging Devil's occupation? | `routed qa` / `-` | Primal Fear Wild Devil Contract Devil |
| **yes** | fact | How old is Aging Devil? | `routed qa` / `-` | 2,000+ |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
