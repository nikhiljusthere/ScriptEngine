# Page campaign jjk/culling_game_colonies — 2026-09-04-1744

Batch `_jjk_page_culling_game_colonies.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-04T17:31:17+00:00), 4.2s wall clock.

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
| **yes** | fact | How are the ten colonies across Japan sealed off? | `routed qa` / `-` | sealed off by barriers that connect to one another and form a line directly down the archipelago |
| **yes** | fact | What is the purpose of the colonies? | `routed qa` / `-` | to send Japanese people to "the other side" once the Culling Game has been completed |
| **yes** | fact | How did Kenjaku create the colonies? | `routed qa` / `-` | Kenjaku created the colonies using bon barriers, taking advantage of Tengen's pure barriers as their foundation |
| **yes** | fact | Where are the other five colonies located? | `routed qa` / `-` | the Aomori, Aichi, Osaka, Kyoto, and Hiroshima Prefectures |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
