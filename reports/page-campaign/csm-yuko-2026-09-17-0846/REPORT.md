# Page campaign csm/yuko — 2026-09-17-0846

Batch `_csm_page_yuko.json`: 9 questions (4 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.7s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/9** |
| set questions exact | 0/4 (0.0%) |
| canon items recovered | 0/17 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Yuko? | Fire Devil Contract, Mind Reading, Sharp Claws, Devil Transformation, Enhanced Strength, Enhanced Speed | - | <sub>https://chainsaw-man.fandom.com/wiki/Yuko</sub> |
| `-` | set | What are all the enemies of Yuko? | Yoru, Denji, Asa Mitaka, Fake Chainsaw Man, Seigi Akoku, Bat Devil, Furio | - | <sub>https://chainsaw-man.fandom.com/wiki/Yuko</sub> |
| `-` | set | What are all the families of Yuko? | Death Devil, Fami | - | <sub>https://chainsaw-man.fandom.com/wiki/Yuko</sub> |
| `-` | set | What are all the affiliations of Yuko? | Fourth East High School, Devil Hunter Club | - | <sub>https://chainsaw-man.fandom.com/wiki/Yuko</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Yuko? | `-` / `-` | 0 found, 6 missing; returned 0 |
| no | set | What are all the enemies of Yuko? | `-` / `-` | 0 found, 7 missing; returned 0 |
| no | set | What are all the families of Yuko? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the affiliations of Yuko? | `-` / `-` | 0 found, 2 missing; returned 0 |
| **yes** | fact | What are the kanji for Yuko's name? | `routed qa` / `-` | ユウコ |
| **yes** | fact | What is the romaji of Yuko's name? | `routed qa` / `-` | Yūko |
| **yes** | fact | What is Yuko's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is the status of Yuko? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Yuko's occupation? | `routed qa` / `-` | High School Student Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
