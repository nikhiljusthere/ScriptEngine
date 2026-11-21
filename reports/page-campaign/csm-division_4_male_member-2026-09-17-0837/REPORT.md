# Page campaign csm/division_4_male_member — 2026-09-17-0837

Batch `_csm_page_division_4_male_member.json`: 6 questions (1 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.6s wall clock.

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
| `exact` | set | What are all the affiliations of Division 4 Male Member? | Tokyo Special Division 4 | Division 4 Male Member, Fake Chainsaw Man, Bucky, Furio, Haruka Iseumi, Nobana Higashiyama, Seigi Akoku, Tanaka, Kanbayashi, Barem Bridge, Miri Sugo, Spear Hybrid… | <sub>https://chainsaw-man.fandom.com/wiki/Division_4_Male_Member</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the affiliations of Division 4 Male Member? | `Male (Affiliation)` / `exact` | 0 found, 1 missing; returned 67 |
| **yes** | fact | What is Division 4 Male Member's gender? | `routed qa` / `-` | Male |
| **yes** | fact | How old is Division 4 Male Member? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Division 4 Male Member's birthday? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Division 4 Male Member? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Division 4 Male Member's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
