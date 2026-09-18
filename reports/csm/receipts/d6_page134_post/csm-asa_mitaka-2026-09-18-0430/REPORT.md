# Page campaign csm/asa_mitaka — 2026-09-18-0430

Batch `_csm_page_asa_mitaka.json`: 16 questions (10 set, 6 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 9.3s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **16/16** |
| set questions exact | 10/10 (100.0%) |
| canon items recovered | 64/64 (100.0%) |
| fact answers present | 6/6 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Asa Mitaka? | `Every named technique of Asa Mitaka` / `declared` | 10 found, 0 missing; returned 10 |
| **yes** | set | What are all the allies of Asa Mitaka? | `Every ally of Asa Mitaka` / `declared` | 13 found, 0 missing; returned 13 |
| **yes** | set | What are all the enemies of Asa Mitaka? | `Every enemy of Asa Mitaka` / `declared` | 15 found, 0 missing; returned 15 |
| **yes** | set | What are all the families of Asa Mitaka? | `Every family of Asa Mitaka` / `declared` | 6 found, 0 missing; returned 6 |
| **yes** | set | What are all the friends of Asa Mitaka? | `Every friend of Asa Mitaka` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the rivals of Asa Mitaka? | `Every rival of Asa Mitaka` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the romantics of Asa Mitaka? | `Every romantic of Asa Mitaka` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | set | What are all the superiors of Asa Mitaka? | `Every superior of Asa Mitaka` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the aliases of Asa Mitaka? | `Asa Mitaka's aliases` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | What are all the affiliations of Asa Mitaka? | `Asa Mitaka's affiliations` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | fact | What are the kanji for Asa Mitaka's name? | `routed qa` / `-` | 三鷹 アサ |
| **yes** | fact | What is the romaji of Asa Mitaka's name? | `routed qa` / `-` | Mitaka Asa |
| **yes** | fact | What is Asa Mitaka's gender? | `routed qa` / `-` | Female |
| **yes** | fact | How old is Asa Mitaka? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Asa Mitaka? | `routed qa` / `-` | Unknown (original timeline) Alive (new timeline) |
| **yes** | fact | What is Asa Mitaka's occupation? | `routed qa` / `-` | High School Student
Private Devil Hunter (formerly)
Wild Fiend Host (formerly) |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
