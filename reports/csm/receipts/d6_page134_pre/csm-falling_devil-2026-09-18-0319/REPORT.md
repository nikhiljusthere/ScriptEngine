# Page campaign csm/falling_devil — 2026-09-18-0319

Batch `_csm_page_falling_devil.json`: 10 questions (4 set, 6 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 8.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **10/10** |
| set questions exact | 4/4 (100.0%) |
| canon items recovered | 29/29 (100.0%) |
| fact answers present | 6/6 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Falling Devil? | `Every named technique of Falling Devil` / `declared` | 19 found, 0 missing; returned 19 |
| **yes** | set | What are all the enemies of Falling Devil? | `Every enemy of Falling Devil` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the superiors of Falling Devil? | `Every superior of Falling Devil` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the affiliations of Falling Devil? | `Falling Devil's affiliations` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | fact | What are the kanji for Falling Devil's name? | `routed qa` / `-` | 落下の悪魔 |
| **yes** | fact | What is the romaji of Falling Devil's name? | `routed qa` / `-` | Rakka no Akuma |
| **yes** | fact | What is Falling Devil's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is the status of Falling Devil? | `routed qa` / `-` | Incapacitated |
| **yes** | fact | How old is Falling Devil? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Falling Devil's occupation? | `routed qa` / `-` | Primal Fear Wild Devil Hell's Chef Yoru's Pawn Death's Pawn (formally) |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
