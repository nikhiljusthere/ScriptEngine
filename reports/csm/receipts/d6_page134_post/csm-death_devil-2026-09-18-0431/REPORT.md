# Page campaign csm/death_devil — 2026-09-18-0431

Batch `_csm_page_death_devil.json`: 14 questions (8 set, 6 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 8.7s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **14/14** |
| set questions exact | 8/8 (100.0%) |
| canon items recovered | 45/45 (100.0%) |
| fact answers present | 6/6 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Death Devil? | `Every named technique of Death Devil` / `declared` | 7 found, 0 missing; returned 7 |
| **yes** | set | What are all the allies of Death Devil? | `Every ally of Death Devil` / `declared` | 6 found, 0 missing; returned 6 |
| **yes** | set | What are all the enemies of Death Devil? | `Every enemy of Death Devil` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the families of Death Devil? | `Every family of Death Devil` / `declared` | 6 found, 0 missing; returned 6 |
| **yes** | set | What are all the subordinates of Death Devil? | `Every subordinate of Death Devil` / `declared` | 8 found, 0 missing; returned 8 |
| **yes** | set | What are all the superiors of Death Devil? | `Every superior of Death Devil` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the aliases of Death Devil? | `Death Devil's aliases` / `declared` | 7 found, 0 missing; returned 7 |
| **yes** | set | What are all the affiliations of Death Devil? | `Death Devil's affiliations` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | fact | What are the kanji for Death Devil's name? | `routed qa` / `-` | 死の悪魔 |
| **yes** | fact | What is the romaji of Death Devil's name? | `routed qa` / `-` | Shi no Akuma |
| **yes** | fact | What is Death Devil's gender? | `routed qa` / `-` | Female |
| **yes** | fact | How old is Death Devil? | `routed qa` / `-` | Unknown (eldest among the Horsemen) |
| **yes** | fact | What is the status of Death Devil? | `routed qa` / `-` | Erased (original timeline) Unknown (new timeline) |
| **yes** | fact | What is Death Devil's occupation? | `routed qa` / `-` | High School Student (cover) Primal Fear Leader of the Chainsaw Man Church School Festival Planning Committee |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
