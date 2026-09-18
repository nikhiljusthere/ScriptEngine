# Page campaign csm/tolka — 2026-09-18-0440

Batch `_csm_page_tolka.json`: 8 questions (3 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 4.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **8/8** |
| set questions exact | 3/3 (100.0%) |
| canon items recovered | 7/7 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the enemies of Tolka? | `Every enemy of Tolka` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the superiors of Tolka? | `Every superior of Tolka` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Tolka? | `Tolka's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What are the kanji for Tolka's name? | `routed qa` / `-` | トーリカ |
| **yes** | fact | What is the romaji of Tolka's name? | `routed qa` / `-` | Tōrika |
| **yes** | fact | What is the status of Tolka? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Tolka's occupation? | `routed qa` / `-` | Private Devil Hunter |
| **yes** | fact | What is Tolka's gender? | `routed qa` / `-` | Male |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
