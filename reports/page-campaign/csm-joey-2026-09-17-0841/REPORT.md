# Page campaign csm/joey — 2026-09-17-0841

Batch `_csm_page_joey.json`: 8 questions (3 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/8** |
| set questions exact | 0/3 (0.0%) |
| canon items recovered | 0/6 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Joey? | Skin Devil Contract, Proficient Gunmanship | - | <sub>https://chainsaw-man.fandom.com/wiki/Joey</sub> |
| `-` | set | What are all the enemies of Joey? | Michiko Tendo, Hirofumi Yoshida | - | <sub>https://chainsaw-man.fandom.com/wiki/Joey</sub> |
| `-` | set | What are all the affiliations of Joey? | United States of America, American Thugs | - | <sub>https://chainsaw-man.fandom.com/wiki/Joey</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Joey? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the enemies of Joey? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the affiliations of Joey? | `-` / `-` | 0 found, 2 missing; returned 0 |
| **yes** | fact | What is the status of Joey? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Joey's occupation? | `routed qa` / `-` | Private Devil Hunter |
| **yes** | fact | What is Joey's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What are the kanji for Joey's name? | `routed qa` / `-` | ジョーイ |
| **yes** | fact | What is the romaji of Joey's name? | `routed qa` / `-` | Jōi |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
