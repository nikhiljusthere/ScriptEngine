# Page campaign csm/princi — 2026-09-17-0843

Batch `_csm_page_princi.json`: 9 questions (3 set, 6 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.5s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **6/9** |
| set questions exact | 0/3 (0.0%) |
| canon items recovered | 0/6 (0.0%) |
| fact answers present | 6/6 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Princi? | Intangibility, Summoning | - | <sub>https://chainsaw-man.fandom.com/wiki/Princi</sub> |
| `-` | set | What are all the enemies of Princi? | Akane Sawatari, Darkness Devil | - | <sub>https://chainsaw-man.fandom.com/wiki/Princi</sub> |
| `-` | set | What are all the affiliations of Princi? | Public Safety Devil Hunters, Tokyo Special Division 4 | - | <sub>https://chainsaw-man.fandom.com/wiki/Princi</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Princi? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the enemies of Princi? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the affiliations of Princi? | `-` / `-` | 0 found, 2 missing; returned 0 |
| **yes** | fact | What are the kanji for Princi's name? | `routed qa` / `-` | プリンシ |
| **yes** | fact | What is the romaji of Princi's name? | `routed qa` / `-` | Purinshi |
| **yes** | fact | What is Princi's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is Princi's height? | `routed qa` / `-` | 180 cm (5'11") |
| **yes** | fact | What is the status of Princi? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Princi's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
