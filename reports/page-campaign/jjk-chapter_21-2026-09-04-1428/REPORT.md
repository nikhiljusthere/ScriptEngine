# Page campaign jjk/chapter_21 — 2026-09-04-1428

Batch `_jjk_page_chapter_21.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T14:06:10+00:00), 3.2s wall clock.

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
| **yes** | fact | What do Yuji, Nanami, and Ijichi plan to investigate throughout the city, per Chapter 21? | `routed qa` / `-` | the disfiguration cases |
| **yes** | fact | What does Mahito show Junpei to test how big and small he can make humans, per Chapter 21? | `routed qa` / `-` | deformed humans |
| **yes** | fact | According to Mahito, what is separate from the heart and is where emotions come from, per Chapter 21? | `routed qa` / `-` | a soul |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
