# Page campaign csm/four_horsemen — 2026-09-17-0839

Batch `_csm_page_four_horsemen.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 1.0s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **2/3** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 2/3 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `partial` | fact | Who are Four Horsemen's notable members? | Control Devil War Devil Famine Devil Death Devil | - | <sub>https://chainsaw-man.fandom.com/wiki/Four_Horsemen</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What is Four Horsemen's allegiance? | `routed qa` / `-` | Devils Weapon Devils (formerly) Themselves |
| no | fact | Who are Four Horsemen's notable members? | `routed roster` / `partial` | answer absent |
| **yes** | fact | In which manga chapter does Four Horsemen first appear? | `routed qa` / `-` | Chapter 84 (Mentioned as a group)
Chapter 1 (Previous Control Devil's debut)
Chapter 97 (Previous Control Devil's debut)
Chapter 98 (War Devil's debut)
Chapter 108 (Death Devil's debut)
Chapter 195 (Famine Devil's debut) |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
