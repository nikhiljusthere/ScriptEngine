# Page campaign jjk/chapter_89 — 2026-09-04-1442

Batch `_jjk_page_chapter_89.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T14:06:10+00:00), 4.8s wall clock.

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
| **yes** | fact | How many transfigured humans are unleashed upon the Fukutoshin Line Platform, per Chapter 89? | `routed qa` / `-` | A thousand |
| **yes** | fact | How long is Satoru Gojo's all-or-nothing Domain Expansion, per Chapter 89? | `routed qa` / `-` | 0.2 seconds |
| **yes** | fact | Approximately how many Transfigured Humans were annihilated after the domain deactivated, per Chapter 89? | `routed narrative` / `-` | one thousand |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
