# Page campaign csm/fami — 2026-09-17-1341

Batch `_csm_page_fami.json`: 12 questions (6 set, 6 fact), scored against the live server (started 2026-09-17T13:38:35+00:00), 7.7s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **11/12** |
| set questions exact | 5/6 (83.3%) |
| canon items recovered | 33/34 (97.1%) |
| fact answers present | 6/6 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `declared` | set | What are all the affiliations of Fami? | Fourth East High School | Chainsaw Man Church, Devil Hunter Club (formerly), Four Horsemen | <sub>https://chainsaw-man.fandom.com/wiki/Fami</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the allies of Fami? | `Every ally of Fami` / `declared` | 12 found, 0 missing; returned 12 |
| **yes** | set | What are all the enemies of Fami? | `Every enemy of Fami` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | set | What are all the families of Fami? | `Every family of Fami` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | set | What are all the subordinates of Fami? | `Every subordinate of Fami` / `declared` | 5 found, 0 missing; returned 5 |
| no | set | What are all the affiliations of Fami? | `Fami's affiliations` / `declared` | 3 found, 1 missing; returned 3 |
| **yes** | set | What are all the aliases of Fami? | `Fami's aliases` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | fact | What are the kanji for Fami's name? | `routed qa` / `-` | キガ |
| **yes** | fact | What is the romaji of Fami's name? | `routed qa` / `-` | Kiga |
| **yes** | fact | What is Fami's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is the status of Fami? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Fami's occupation? | `routed qa` / `-` | High School Student (cover) Wild Devil |
| **yes** | fact | How old is Fami? | `routed qa` / `-` | Unknown |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
