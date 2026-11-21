# Page campaign csm/kusakabe — 2026-09-17-0841

Batch `_csm_page_kusakabe.json`: 8 questions (3 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.3s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/8** |
| set questions exact | 0/3 (0.0%) |
| canon items recovered | 0/7 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Kusakabe? | Stone Devil Contract | - | <sub>https://chainsaw-man.fandom.com/wiki/Kusakabe</sub> |
| `-` | set | What are all the allies of Kusakabe? | Denji, Power, Hirofumi Yoshida, Tamaoki | - | <sub>https://chainsaw-man.fandom.com/wiki/Kusakabe</sub> |
| `-` | set | What are all the affiliations of Kusakabe? | Public Safety Devil Hunters, Miyagi Division 2 | - | <sub>https://chainsaw-man.fandom.com/wiki/Kusakabe</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Kusakabe? | `-` / `-` | 0 found, 1 missing; returned 0 |
| no | set | What are all the allies of Kusakabe? | `-` / `-` | 0 found, 4 missing; returned 0 |
| no | set | What are all the affiliations of Kusakabe? | `-` / `-` | 0 found, 2 missing; returned 0 |
| **yes** | fact | What is the status of Kusakabe? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Kusakabe's occupation? | `routed qa` / `-` | Public Safety Devil Hunter
Denji’s Bodyguard (formerly) |
| **yes** | fact | What is Kusakabe's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the romaji of Kusakabe's name? | `routed qa` / `-` | Kusakabe |
| **yes** | fact | What are the kanji for Kusakabe's name? | `routed qa` / `-` | 日下部 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
