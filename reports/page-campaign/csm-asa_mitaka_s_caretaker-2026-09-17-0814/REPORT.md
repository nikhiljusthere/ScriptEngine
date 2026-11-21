# Page campaign csm/asa_mitaka_s_caretaker — 2026-09-17-0814

Batch `_csm_page_asa_mitaka_s_caretaker.json`: 5 questions (1 set, 4 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **4/5** |
| set questions exact | 0/1 (0.0%) |
| canon items recovered | 0/1 (0.0%) |
| fact answers present | 4/4 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the affiliations of Asa Mitaka's caretaker? | Unnamed orphanage | - | <sub>https://chainsaw-man.fandom.com/wiki/Asa_Mitaka's_caretaker</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the affiliations of Asa Mitaka's caretaker? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What is Asa Mitaka's caretaker's gender? | `routed qa` / `-` | Female |
| **yes** | fact | How old is Asa Mitaka's caretaker? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Asa Mitaka's caretaker? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Asa Mitaka's caretaker's occupation? | `routed qa` / `-` | Caretaker |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
