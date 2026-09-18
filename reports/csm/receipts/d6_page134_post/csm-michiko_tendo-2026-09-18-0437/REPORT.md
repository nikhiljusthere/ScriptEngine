# Page campaign csm/michiko_tendo — 2026-09-18-0437

Batch `_csm_page_michiko_tendo.json`: 9 questions (3 set, 6 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 5.7s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **9/9** |
| set questions exact | 3/3 (100.0%) |
| canon items recovered | 9/9 (100.0%) |
| fact answers present | 6/6 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the allies of Michiko Tendo? | `Every ally of Michiko Tendo` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the enemies of Michiko Tendo? | `Every enemy of Michiko Tendo` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Michiko Tendo? | `Michiko Tendo's affiliations` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | fact | What are the kanji for Michiko Tendo's name? | `routed qa` / `-` | 天童 ミチコ |
| **yes** | fact | What is the romaji of Michiko Tendo's name? | `routed qa` / `-` | Tendō Michiko |
| **yes** | fact | What is Michiko Tendo's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is Michiko Tendo's height? | `routed qa` / `-` | 175 cm (5'9") |
| **yes** | fact | What is the status of Michiko Tendo? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Michiko Tendo's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
