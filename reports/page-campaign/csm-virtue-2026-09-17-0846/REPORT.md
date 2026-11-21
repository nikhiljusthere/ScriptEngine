# Page campaign csm/virtue — 2026-09-17-0846

Batch `_csm_page_virtue.json`: 6 questions (1 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.6s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/6** |
| set questions exact | 0/1 (0.0%) |
| canon items recovered | 0/1 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the affiliations of Virtue? | Public Safety Devil Hunters | - | <sub>https://chainsaw-man.fandom.com/wiki/Virtue</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the affiliations of Virtue? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What are the kanji for Virtue's name? | `routed qa` / `-` | ヴァーチェ |
| **yes** | fact | What is the romaji of Virtue's name? | `routed qa` / `-` | Vāche |
| **yes** | fact | What is Virtue's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Virtue? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Virtue's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
