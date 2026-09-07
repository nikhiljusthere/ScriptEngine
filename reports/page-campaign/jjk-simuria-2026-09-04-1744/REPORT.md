# Page campaign jjk/simuria — 2026-09-04-1744

Batch `_jjk_page_simuria.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-04T17:31:17+00:00), 4.1s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **4/4** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 4/4 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What is Simuria? | `routed qa` / `-` | an alien planet that closely resembles Earth in its overall geography |
| **yes** | fact | What do Simurians possess that earthlings do not? | `routed qa` / `-` | a third eye, an essential organ and the source of their Rolloluca |
| **yes** | fact | What is Mul? | `routed qa` / `-` | a special ore that can convert Rolloluca into all forms of energy |
| **yes** | fact | What did Maru and Cross use to construct the Naunax? | `routed qa` / `-` | a stash of high purity Mul |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
