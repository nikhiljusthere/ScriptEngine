# Page campaign csm/division_2_vice_captain — 2026-09-17-0837

Batch `_csm_page_division_2_vice_captain.json`: 8 questions (3 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.2s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/8** |
| set questions exact | 0/3 (0.0%) |
| canon items recovered | 0/4 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Division 2 Vice Captain? | Fox Devil Contract | - | <sub>https://chainsaw-man.fandom.com/wiki/Division_2_Vice_Captain</sub> |
| `-` | set | What are all the affiliations of Division 2 Vice Captain? | Public Safety Devil Hunters, Tokyo Division 2 | - | <sub>https://chainsaw-man.fandom.com/wiki/Division_2_Vice_Captain</sub> |
| `-` | set | What are all the aliases of Division 2 Vice Captain? | Vice Captain | - | <sub>https://chainsaw-man.fandom.com/wiki/Division_2_Vice_Captain</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Division 2 Vice Captain? | `-` / `-` | 0 found, 1 missing; returned 0 |
| no | set | What are all the affiliations of Division 2 Vice Captain? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the aliases of Division 2 Vice Captain? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What are the kanji for Division 2 Vice Captain's name? | `routed qa` / `-` | 対魔２課副隊長 |
| **yes** | fact | What is the romaji of Division 2 Vice Captain's name? | `routed qa` / `-` | Tai Ma 2-ka Fuku Taichō |
| **yes** | fact | What is Division 2 Vice Captain's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Division 2 Vice Captain? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Division 2 Vice Captain's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
