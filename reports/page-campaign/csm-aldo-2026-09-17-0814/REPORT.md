# Page campaign csm/aldo — 2026-09-17-0814

Batch `_csm_page_aldo.json`: 8 questions (3 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.6s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/8** |
| set questions exact | 0/3 (0.0%) |
| canon items recovered | 0/10 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Aldo? | Enhanced Durability, Enhanced Reflexes, Skin Devil Contract, Proficient Gunmanship | - | <sub>https://chainsaw-man.fandom.com/wiki/Aldo</sub> |
| `-` | set | What are all the enemies of Aldo? | Michiko Tendo, Hirofumi Yoshida, Quanxi, Long | - | <sub>https://chainsaw-man.fandom.com/wiki/Aldo</sub> |
| `-` | set | What are all the affiliations of Aldo? | United States of America, American Thugs | - | <sub>https://chainsaw-man.fandom.com/wiki/Aldo</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Aldo? | `-` / `-` | 0 found, 4 missing; returned 0 |
| no | set | What are all the enemies of Aldo? | `-` / `-` | 0 found, 4 missing; returned 0 |
| no | set | What are all the affiliations of Aldo? | `-` / `-` | 0 found, 2 missing; returned 0 |
| **yes** | fact | What is the status of Aldo? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Aldo's occupation? | `routed qa` / `-` | Private Devil Hunter |
| **yes** | fact | What is Aldo's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What are the kanji for Aldo's name? | `routed qa` / `-` | アルド |
| **yes** | fact | What is the romaji of Aldo's name? | `routed qa` / `-` | Arudo |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
