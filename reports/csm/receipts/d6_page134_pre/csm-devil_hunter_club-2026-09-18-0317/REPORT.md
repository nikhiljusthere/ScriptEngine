# Page campaign csm/devil_hunter_club — 2026-09-18-0317

Batch `_csm_page_devil_hunter_club.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 3.7s wall clock.

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
| **yes** | fact | What is Devil Hunter Club's title? | `routed qa` / `-` | Devil Hunter Club |
| **yes** | fact | Who are Devil Hunter Club's notable members? | `routed roster` / `partial` | Asa Mitaka, Yoru, Fami, Hirofumi Yoshida, Haruka Iseumi |
| **yes** | fact | In which manga chapter does Devil Hunter Club first appear? | `routed qa` / `-` | Chapter 99 |
| **yes** | fact | What type of song is Devil Hunter Club? | `routed qa` / `-` | High School Club |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
