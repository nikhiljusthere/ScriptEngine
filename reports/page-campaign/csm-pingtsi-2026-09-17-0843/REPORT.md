# Page campaign csm/pingtsi — 2026-09-17-0843

Batch `_csm_page_pingtsi.json`: 8 questions (3 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.0s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/8** |
| set questions exact | 0/3 (0.0%) |
| canon items recovered | 0/8 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Pingtsi? | Magnifying Glass, Contract Perception, Bilingual | - | <sub>https://chainsaw-man.fandom.com/wiki/Pingtsi</sub> |
| `-` | set | What are all the enemies of Pingtsi? | Kishibe, Power, Tsugihagi, Quanxi | - | <sub>https://chainsaw-man.fandom.com/wiki/Pingtsi</sub> |
| `-` | set | What are all the affiliations of Pingtsi? | Quanxi and the Fiends | - | <sub>https://chainsaw-man.fandom.com/wiki/Pingtsi</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Pingtsi? | `-` / `-` | 0 found, 3 missing; returned 0 |
| no | set | What are all the enemies of Pingtsi? | `-` / `-` | 0 found, 4 missing; returned 0 |
| no | set | What are all the affiliations of Pingtsi? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What are the kanji for Pingtsi's name? | `routed qa` / `-` | ピンツイ |
| **yes** | fact | What is the romaji of Pingtsi's name? | `routed qa` / `-` | Pintsui |
| **yes** | fact | What is Pingtsi's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is the status of Pingtsi? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Pingtsi's occupation? | `routed qa` / `-` | Private Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
