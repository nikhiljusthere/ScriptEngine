# Page campaign csm/nobana_higashiyama — 2026-09-17-0843

Batch `_csm_page_nobana_higashiyama.json`: 9 questions (4 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.6s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/9** |
| set questions exact | 0/4 (0.0%) |
| canon items recovered | 0/14 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the allies of Nobana Higashiyama? | Asa Mitaka, Miri Sugo, Haruka Iseumi, Denji, Seigi Akoku, Fami, Yoru, Nail Fiend | - | <sub>https://chainsaw-man.fandom.com/wiki/Nobana_Higashiyama</sub> |
| `-` | set | What are all the enemies of Nobana Higashiyama? | Quanxi, Barem Bridge | - | <sub>https://chainsaw-man.fandom.com/wiki/Nobana_Higashiyama</sub> |
| `-` | set | What are all the affiliations of Nobana Higashiyama? | Fourth East High School, Devil Hunter Club, Chainsaw Man Church (formerly) | - | <sub>https://chainsaw-man.fandom.com/wiki/Nobana_Higashiyama</sub> |
| `-` | set | What are all the aliases of Nobana Higashiyama? | Glass Licker (by Denji) | - | <sub>https://chainsaw-man.fandom.com/wiki/Nobana_Higashiyama</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the allies of Nobana Higashiyama? | `-` / `-` | 0 found, 8 missing; returned 0 |
| no | set | What are all the enemies of Nobana Higashiyama? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the affiliations of Nobana Higashiyama? | `-` / `-` | 0 found, 3 missing; returned 0 |
| no | set | What are all the aliases of Nobana Higashiyama? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What are the kanji for Nobana Higashiyama's name? | `routed qa` / `-` | 東山 ノバナ |
| **yes** | fact | What is the romaji of Nobana Higashiyama's name? | `routed qa` / `-` | Higashiyama Nobana |
| **yes** | fact | What is Nobana Higashiyama's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Nobana Higashiyama? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Nobana Higashiyama's occupation? | `routed qa` / `-` | High School Student Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
