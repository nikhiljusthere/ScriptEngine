# Page campaign csm/tanabe — 2026-09-17-0845

Batch `_csm_page_tanabe.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/7** |
| set questions exact | 0/2 (0.0%) |
| canon items recovered | 0/3 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Tanabe? | Mold Devil Contract | - | <sub>https://chainsaw-man.fandom.com/wiki/Tanabe</sub> |
| `-` | set | What are all the affiliations of Tanabe? | Public Safety Devil Hunters, Tokyo Division 2 | - | <sub>https://chainsaw-man.fandom.com/wiki/Tanabe</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Tanabe? | `-` / `-` | 0 found, 1 missing; returned 0 |
| no | set | What are all the affiliations of Tanabe? | `-` / `-` | 0 found, 2 missing; returned 0 |
| **yes** | fact | What are the kanji for Tanabe's name? | `routed qa` / `-` | 田辺 |
| **yes** | fact | What is the romaji of Tanabe's name? | `routed qa` / `-` | Tanabe |
| **yes** | fact | What is Tanabe's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Tanabe? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Tanabe's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
