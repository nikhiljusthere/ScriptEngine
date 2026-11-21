# Page campaign csm/debt_collector — 2026-09-17-0837

Batch `_csm_page_debt_collector.json`: 4 questions (1 set, 3 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 1.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **3/4** |
| set questions exact | 0/1 (0.0%) |
| canon items recovered | 0/1 (0.0%) |
| fact answers present | 3/3 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the affiliations of Debt Collector? | Yakuza | - | <sub>https://chainsaw-man.fandom.com/wiki/Debt_Collector</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the affiliations of Debt Collector? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What is Debt Collector's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Debt Collector? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Debt Collector's occupation? | `routed qa` / `-` | Yakuza Boss |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
