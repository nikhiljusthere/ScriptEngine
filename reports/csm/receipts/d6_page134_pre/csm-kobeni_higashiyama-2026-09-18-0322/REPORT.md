# Page campaign csm/kobeni_higashiyama — 2026-09-18-0322

Batch `_csm_page_kobeni_higashiyama.json`: 13 questions (6 set, 7 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 8.0s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **13/13** |
| set questions exact | 6/6 (100.0%) |
| canon items recovered | 33/33 (100.0%) |
| fact answers present | 7/7 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Kobeni Higashiyama? | `Every named technique of Kobeni Higashiyama` / `declared` | 6 found, 0 missing; returned 6 |
| **yes** | set | What are all the allies of Kobeni Higashiyama? | `Every ally of Kobeni Higashiyama` / `declared` | 10 found, 0 missing; returned 10 |
| **yes** | set | What are all the enemies of Kobeni Higashiyama? | `Every enemy of Kobeni Higashiyama` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | set | What are all the subordinates of Kobeni Higashiyama? | `Every subordinate of Kobeni Higashiyama` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the superiors of Kobeni Higashiyama? | `Every superior of Kobeni Higashiyama` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | set | What are all the affiliations of Kobeni Higashiyama? | `Kobeni Higashiyama's affiliations` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | fact | What are the kanji for Kobeni Higashiyama's name? | `routed qa` / `-` | 東山 コベニ |
| **yes** | fact | What is the romaji of Kobeni Higashiyama's name? | `routed qa` / `-` | Higashiyama Kobeni |
| **yes** | fact | How old is Kobeni Higashiyama? | `routed qa` / `-` | 20 (Chapter 10-???) |
| **yes** | fact | What is Kobeni Higashiyama's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is Kobeni Higashiyama's height? | `routed qa` / `-` | 155 cm (5'1") |
| **yes** | fact | What is the status of Kobeni Higashiyama? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Kobeni Higashiyama's occupation? | `routed qa` / `-` | Public Safety Devil Hunter (formerly) Waitress (formerly) |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
