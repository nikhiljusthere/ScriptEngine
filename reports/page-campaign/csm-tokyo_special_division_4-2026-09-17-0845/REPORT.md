# Page campaign csm/tokyo_special_division_4 — 2026-09-17-0845

Batch `_csm_page_tokyo_special_division_4.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 1.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **3/4** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 3/4 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `partial` | fact | Who are Tokyo Special Division 4's notable members? | Himeno Denji Aki Hayakawa Power | - | <sub>https://chainsaw-man.fandom.com/wiki/Tokyo_Special_Division_4</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What is Tokyo Special Division 4's allegiance? | `routed qa` / `-` | Public Safety Devil Hunters |
| no | fact | Who are Tokyo Special Division 4's notable members? | `routed roster` / `partial` | answer absent |
| **yes** | fact | Which series does Tokyo Special Division 4 belong to? | `routed qa` / `-` | Tokyo Special Division 4 |
| **yes** | fact | In which manga chapter does Tokyo Special Division 4 first appear? | `routed qa` / `-` | Chapter 5 (mentioned) |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
