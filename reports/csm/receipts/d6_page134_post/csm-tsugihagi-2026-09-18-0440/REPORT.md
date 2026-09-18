# Page campaign csm/tsugihagi — 2026-09-18-0440

Batch `_csm_page_tsugihagi.json`: 6 questions (1 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 4.2s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **6/6** |
| set questions exact | 1/1 (100.0%) |
| canon items recovered | 1/1 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the affiliations of Tsugihagi? | `Tsugihagi's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Tsugihagi's name? | `routed qa` / `-` | ツギハギ |
| **yes** | fact | What is the romaji of Tsugihagi's name? | `routed qa` / `-` | Tsugihagi |
| **yes** | fact | What is Tsugihagi's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is the status of Tsugihagi? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Tsugihagi's occupation? | `routed qa` / `-` | Private Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
