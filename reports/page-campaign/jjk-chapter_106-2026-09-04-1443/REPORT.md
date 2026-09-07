# Page campaign jjk/chapter_106 — 2026-09-04-1443

Batch `_jjk_page_chapter_106.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T14:06:10+00:00), 3.3s wall clock.

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
| **yes** | fact | Whom does Nanami join up with to encounter Dagon in Shibuya Station, per Chapter 106? | `routed qa` / `-` | the Zenin Team |
| **yes** | fact | At what time do Nanami and the Zenins head toward B5F, per Chapter 106? | `routed qa` / `-` | 10:20 P.M. |
| **yes** | fact | What does Dagon vomit up after the impact severely injures him, per Chapter 106? | `routed qa` / `-` | the skeletal remains of the numerous non-sorcerers he ate |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
