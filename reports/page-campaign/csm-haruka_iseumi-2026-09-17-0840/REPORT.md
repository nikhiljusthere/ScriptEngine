# Page campaign csm/haruka_iseumi — 2026-09-17-0840

Batch `_csm_page_haruka_iseumi.json`: 11 questions (6 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.7s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/11** |
| set questions exact | 0/6 (0.0%) |
| canon items recovered | 0/19 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the allies of Haruka Iseumi? | Asa Mitaka, Fami, Nobana Higashiyama, Seigi Akoku, Denji, Yoru, Nail Fiend | - | <sub>https://chainsaw-man.fandom.com/wiki/Haruka_Iseumi</sub> |
| `-` | set | What are all the enemies of Haruka Iseumi? | Fami, Barem Bridge | - | <sub>https://chainsaw-man.fandom.com/wiki/Haruka_Iseumi</sub> |
| `-` | set | What are all the subordinates of Haruka Iseumi? | Asa Mitaka, Seigi Akoku | - | <sub>https://chainsaw-man.fandom.com/wiki/Haruka_Iseumi</sub> |
| `-` | set | What are all the superiors of Haruka Iseumi? | Fami, Barem Bridge | - | <sub>https://chainsaw-man.fandom.com/wiki/Haruka_Iseumi</sub> |
| `-` | set | What are all the affiliations of Haruka Iseumi? | Fourth East High School, Devil Hunter Club (president), Student Council (president), Chainsaw Man Church (formerly), "Fami" (formerly) | - | <sub>https://chainsaw-man.fandom.com/wiki/Haruka_Iseumi</sub> |
| `-` | set | What are all the aliases of Haruka Iseumi? | Chainsaw Man ( self-proclaimed ) | - | <sub>https://chainsaw-man.fandom.com/wiki/Haruka_Iseumi</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the allies of Haruka Iseumi? | `-` / `-` | 0 found, 7 missing; returned 0 |
| no | set | What are all the enemies of Haruka Iseumi? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the subordinates of Haruka Iseumi? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the superiors of Haruka Iseumi? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the affiliations of Haruka Iseumi? | `-` / `-` | 0 found, 5 missing; returned 0 |
| no | set | What are all the aliases of Haruka Iseumi? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What are the kanji for Haruka Iseumi's name? | `routed qa` / `-` | 伊勢海 ハルカ |
| **yes** | fact | What is the romaji of Haruka Iseumi's name? | `routed qa` / `-` | Iseumi Haruka |
| **yes** | fact | What is the status of Haruka Iseumi? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Haruka Iseumi's occupation? | `routed qa` / `-` | High School Student Devil Hunter Public Speaker |
| **yes** | fact | What is Haruka Iseumi's gender? | `routed qa` / `-` | Male |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
