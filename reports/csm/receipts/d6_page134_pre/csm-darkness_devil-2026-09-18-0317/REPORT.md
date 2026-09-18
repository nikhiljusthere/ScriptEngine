# Page campaign csm/darkness_devil — 2026-09-18-0317

Batch `_csm_page_darkness_devil.json`: 8 questions (2 set, 6 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 5.6s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **8/8** |
| set questions exact | 2/2 (100.0%) |
| canon items recovered | 12/12 (100.0%) |
| fact answers present | 6/6 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Darkness Devil? | `Every named technique of Darkness Devil` / `declared` | 10 found, 0 missing; returned 10 |
| **yes** | set | What are all the enemies of Darkness Devil? | `Every enemy of Darkness Devil` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What are the kanji for Darkness Devil's name? | `routed qa` / `-` | 闇の悪魔 |
| **yes** | fact | What is the romaji of Darkness Devil's name? | `routed qa` / `-` | Yami no Akuma |
| **yes** | fact | What is the status of Darkness Devil? | `routed qa` / `-` | Alive |
| **yes** | fact | How old is Darkness Devil? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Darkness Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Darkness Devil's occupation? | `routed qa` / `-` | Primal Fear Wild Contract Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
