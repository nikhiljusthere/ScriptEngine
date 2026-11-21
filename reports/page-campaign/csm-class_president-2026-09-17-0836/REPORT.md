# Page campaign csm/class_president — 2026-09-17-0836

Batch `_csm_page_class_president.json`: 5 questions (2 set, 3 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 1.6s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **3/5** |
| set questions exact | 0/2 (0.0%) |
| canon items recovered | 0/6 (0.0%) |
| fact answers present | 3/3 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Class President? | Fire Devil Contract, Sharp Claws, Devil Transformation, Enhanced Strength, Enhanced Speed | - | <sub>https://chainsaw-man.fandom.com/wiki/Class_President</sub> |
| `-` | set | What are all the affiliations of Class President? | Fourth East High School | - | <sub>https://chainsaw-man.fandom.com/wiki/Class_President</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Class President? | `-` / `-` | 0 found, 5 missing; returned 0 |
| no | set | What are all the affiliations of Class President? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What is Class President's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is the status of Class President? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Class President's occupation? | `routed qa` / `-` | High School Student Class President |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
