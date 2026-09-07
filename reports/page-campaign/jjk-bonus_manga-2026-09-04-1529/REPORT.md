# Page campaign jjk/bonus_manga — 2026-09-04-1529

Batch `_jjk_page_bonus_manga.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-04T14:06:10+00:00), 4.7s wall clock.

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
| **yes** | fact | What do the Jujutsu High first-years work at as part-time jobs, per Bonus Manga? | `routed qa` / `-` | a cosmetics shop |
| **yes** | fact | At which shop do the first-years work, per Bonus Manga? | `routed qa` / `-` | Tamatina Castle |
| **yes** | fact | Which customer arrives at the shop wanting to redeem a coupon, per Bonus Manga? | `routed qa` / `-` | Utahime |
| **yes** | fact | What release was this chapter made to celebrate, per Bonus Manga? | `routed qa` / `-` | Jujutsu Kaisen 0: The Movie |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
