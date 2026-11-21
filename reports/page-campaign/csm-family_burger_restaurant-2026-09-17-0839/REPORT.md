# Page campaign csm/family_burger_restaurant — 2026-09-17-0839

Batch `_csm_page_family_burger_restaurant.json`: 5 questions (0 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/5** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What type of song is Family Burger Restaurant? | `routed qa` / `-` | Restaurant |
| **yes** | fact | What services does Family Burger Restaurant provide? | `routed qa` / `-` | Fast Food |
| **yes** | fact | Who are Family Burger Restaurant's employees? | `routed qa` / `-` | Unnamed Employees Unnamed Two Employees † Unnamed Mascot † Kobeni Higashiyama (formerly) |
| **yes** | fact | In which manga chapter does Family Burger Restaurant first appear? | `routed qa` / `-` | Chapter 85 |
| **yes** | fact | In which anime episode is Family Burger Restaurant first depicted? | `routed qa` / `-` | Chainsaw Man – The Movie: Reze Arc |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
