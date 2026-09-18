# Page campaign csm/zombie_devil — 2026-09-18-0328

Batch `_csm_page_zombie_devil.json`: 10 questions (3 set, 7 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 7.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **10/10** |
| set questions exact | 3/3 (100.0%) |
| canon items recovered | 6/6 (100.0%) |
| fact answers present | 7/7 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Zombie Devil? | `Every named technique of Zombie Devil` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the creations of Zombie Devil? | `Every creation of Zombie Devil` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Zombie Devil? | `Zombie Devil's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What are the kanji for Zombie Devil's name? | `routed qa` / `-` | ゾンビの悪魔 |
| **yes** | fact | What is the romaji of Zombie Devil's name? | `routed qa` / `-` | Zonbi no Akuma |
| **yes** | fact | How old is Zombie Devil? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Zombie Devil's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Zombie Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Zombie Devil's occupation? | `routed qa` / `-` | Wild Devil
Contract Devil |
| **yes** | fact | What is Zombie Devil's birthday? | `routed qa` / `-` | Unknown |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
