# Page campaign csm/quanxi_and_the_fiends — 2026-09-18-0439

Batch `_csm_page_quanxi_and_the_fiends.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 2.1s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **3/3** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 3/3 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What is Quanxi and the Fiends's allegiance? | `routed qa` / `-` | China |
| **yes** | fact | Who are Quanxi and the Fiends's notable members? | `routed roster` / `partial` | Quanxi, Pingtsi †, Long †, Cosmo †, Tsugihagi † |
| **yes** | fact | In which manga chapter does Quanxi and the Fiends first appear? | `routed qa` / `-` | Chapter 54 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
