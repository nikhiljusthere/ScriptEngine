# Page campaign csm/asa_mitaka_s_caretaker — 2026-09-18-0430

Batch `_csm_page_asa_mitaka_s_caretaker.json`: 5 questions (1 set, 4 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 3.5s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/5** |
| set questions exact | 1/1 (100.0%) |
| canon items recovered | 1/1 (100.0%) |
| fact answers present | 4/4 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the affiliations of Asa Mitaka's caretaker? | `Asa Mitaka's caretaker's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What is Asa Mitaka's caretaker's gender? | `routed qa` / `-` | Female |
| **yes** | fact | How old is Asa Mitaka's caretaker? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Asa Mitaka's caretaker? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Asa Mitaka's caretaker's occupation? | `routed qa` / `-` | Caretaker |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
