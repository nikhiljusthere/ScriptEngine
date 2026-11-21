# Page campaign csm/seigi_akoku — 2026-09-17-0844

Batch `_csm_page_seigi_akoku.json`: 8 questions (3 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.1s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/8** |
| set questions exact | 0/3 (0.0%) |
| canon items recovered | 0/13 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Seigi Akoku? | Hand-to-Hand Combat | - | <sub>https://chainsaw-man.fandom.com/wiki/Seigi_Akoku</sub> |
| `-` | set | What are all the allies of Seigi Akoku? | Asa Mitaka, Hirofumi Yoshida, Denji, Nayuta, Yoru, Nail Fiend, Fami, Haruka Iseumi, Nobana Higashiyama | - | <sub>https://chainsaw-man.fandom.com/wiki/Seigi_Akoku</sub> |
| `-` | set | What are all the affiliations of Seigi Akoku? | Fourth East High School, Devil Hunter Club, Chainsaw Man Church (formerly) | - | <sub>https://chainsaw-man.fandom.com/wiki/Seigi_Akoku</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Seigi Akoku? | `-` / `-` | 0 found, 1 missing; returned 0 |
| no | set | What are all the allies of Seigi Akoku? | `-` / `-` | 0 found, 9 missing; returned 0 |
| no | set | What are all the affiliations of Seigi Akoku? | `-` / `-` | 0 found, 3 missing; returned 0 |
| **yes** | fact | What is the status of Seigi Akoku? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Seigi Akoku's occupation? | `routed qa` / `-` | High School Student Devil Hunter |
| **yes** | fact | What is Seigi Akoku's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What are the kanji for Seigi Akoku's name? | `routed qa` / `-` | 亜国 セイギ |
| **yes** | fact | What is the romaji of Seigi Akoku's name? | `routed qa` / `-` | Akoku Seigi |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
