# Page campaign csm/division_4_female_member — 2026-09-17-0837

Batch `_csm_page_division_4_female_member.json`: 6 questions (1 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.4s wall clock.

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
| `exact` | set | What are all the affiliations of Division 4 Female Member? | Tokyo Special Division 4 | Akane Sawatari, Asa Mitaka, Asa Mitaka's Mother, Asa Mitaka's caretaker, Class President, Cosmo, Death Devil, Division 4 Female Member, Falling Devil, Fami, Famine Devil, Fumiko Mifune… | <sub>https://chainsaw-man.fandom.com/wiki/Division_4_Female_Member</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the affiliations of Division 4 Female Member? | `Female` / `exact` | 0 found, 1 missing; returned 31 |
| **yes** | fact | What is Division 4 Female Member's gender? | `routed qa` / `-` | Female |
| **yes** | fact | How old is Division 4 Female Member? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Division 4 Female Member's birthday? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Division 4 Female Member? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Division 4 Female Member's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
