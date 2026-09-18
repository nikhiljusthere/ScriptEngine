# Page campaign csm/doll_devil — 2026-09-18-0432

Batch `_csm_page_doll_devil.json`: 8 questions (1 set, 7 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 5.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **8/8** |
| set questions exact | 1/1 (100.0%) |
| canon items recovered | 1/1 (100.0%) |
| fact answers present | 7/7 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the affiliations of Doll Devil? | `Doll Devil's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Doll Devil's name? | `routed qa` / `-` | 人形の悪魔 |
| **yes** | fact | What is the romaji of Doll Devil's name? | `routed qa` / `-` | Ningyō no Akuma |
| **yes** | fact | What is the status of Doll Devil? | `routed qa` / `-` | Alive |
| **yes** | fact | How old is Doll Devil? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Doll Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Doll Devil's birthday? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Doll Devil's occupation? | `routed qa` / `-` | Contract Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
