# Page campaign csm/world_war_ii_devil — 2026-09-18-0441

Batch `_csm_page_world_war_ii_devil.json`: 5 questions (1 set, 4 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 3.5s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/5** |
| set questions exact | 1/1 (100.0%) |
| canon items recovered | 1/1 (100.0%) |
| fact answers present | 4/4 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the affiliations of World War II Devil? | `World War II Devil's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for World War II Devil's name? | `routed qa` / `-` | 第二次世界大戦の悪魔の悪魔 |
| **yes** | fact | What is the romaji of World War II Devil's name? | `routed qa` / `-` | Dainiji Sekai Taisen no Akuma |
| **yes** | fact | What is World War II Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of World War II Devil? | `routed qa` / `-` | Erased (original timeline) |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
