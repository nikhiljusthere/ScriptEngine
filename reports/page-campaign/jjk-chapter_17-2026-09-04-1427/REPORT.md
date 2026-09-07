# Page campaign jjk/chapter_17 — 2026-09-04-1427

Batch `_jjk_page_chapter_17.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T14:06:10+00:00), 3.4s wall clock.

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
| **yes** | fact | What about Megumi's answer leaves Aoi unimpressed, prompting him to test his strength, per Chapter 17? | `routed qa` / `-` | Megumi's response of his type of women |
| **yes** | fact | What kind of people does Aoi hate, per Chapter 17? | `routed qa` / `-` | boring people |
| **yes** | fact | What does Mai pull out on Nobara during the scuffle, per Chapter 17? | `routed qa` / `-` | a gun |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
