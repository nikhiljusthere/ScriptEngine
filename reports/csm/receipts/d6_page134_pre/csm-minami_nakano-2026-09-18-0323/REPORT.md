# Page campaign csm/minami_nakano — 2026-09-18-0323

Batch `_csm_page_minami_nakano.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 5.2s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **7/7** |
| set questions exact | 2/2 (100.0%) |
| canon items recovered | 3/3 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the aliases of Minami Nakano? | `Minami Nakano's aliases` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Minami Nakano? | `Minami Nakano's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What is the Japanese spelling of Minami Nakano's name? | `routed qa` / `-` | ナカノミナミ |
| **yes** | fact | What is the romaji of Minami Nakano's name? | `routed qa` / `-` | Nakano Minami |
| **yes** | fact | What is Minami Nakano's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is the status of Minami Nakano? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Minami Nakano's occupation? | `routed qa` / `-` | Public Safety Devil Hunter (formerly) |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
