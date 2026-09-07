# Page campaign jjk/chapter_25 — 2026-09-04-0826

Batch `_jjk_page_chapter_25.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T08:23:53+00:00), 3.6s wall clock.

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
| **yes** | fact | Who is Junpei's mother, whose death leads him down the dark path of revenge, per Chapter 25? | `routed qa` / `-` | Nagi Yoshino |
| **yes** | fact | What was the cursed spirit that killed Nagi Yoshino attracted to, per Chapter 25? | `routed qa` / `-` | the Sukuna finger |
| **yes** | fact | What is Mahito's plan to force Yuji into a Binding Vow, per Chapter 25? | `routed qa` / `-` | use Junpei fight Sukuna's Vessel |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
