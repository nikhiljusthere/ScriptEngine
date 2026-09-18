# Page campaign csm/cosmo — 2026-09-18-0317

Batch `_csm_page_cosmo.json`: 8 questions (3 set, 5 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 5.7s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **8/8** |
| set questions exact | 3/3 (100.0%) |
| canon items recovered | 5/5 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Cosmo? | `Every named technique of Cosmo` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the enemies of Cosmo? | `Every enemy of Cosmo` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Cosmo? | `Cosmo's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Cosmo's name? | `routed qa` / `-` | コスモ |
| **yes** | fact | What is the romaji of Cosmo's name? | `routed qa` / `-` | Kosumo |
| **yes** | fact | What is the status of Cosmo? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Cosmo's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is Cosmo's occupation? | `routed qa` / `-` | Private Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
