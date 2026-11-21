# Page campaign csm/yakuza — 2026-09-17-0846

Batch `_csm_page_yakuza.json`: 6 questions (0 set, 6 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.7s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **6/6** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 6/6 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What is Yakuza's allegiance? | `routed qa` / `-` | Themselves
Zombie Devil (controlled)
Gun Devil (ruse) |
| **yes** | fact | Who are Yakuza's notable members? | `routed qa` / `-` | Unnamed boss †
Katana Man (formerly) |
| **yes** | fact | Which series does Yakuza belong to? | `routed qa` / `-` | Yakuza |
| **yes** | fact | In which manga chapter does Yakuza first appear? | `routed qa` / `-` | Chapter 1 |
| **yes** | fact | Who are Yakuza's affiliates? | `routed qa` / `-` | Denji's Father (formerly) † Denji (coerced; formerly) Akane Sawatari (formerly) † |
| **yes** | fact | What type of song is Yakuza? | `routed qa` / `-` | Criminal |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
