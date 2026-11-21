# Page campaign csm/hybrid — 2026-09-17-0840

Batch `_csm_page_hybrid.json`: 1 questions (1 set, 0 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 0.1s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **0/1** |
| set questions exact | 0/1 (0.0%) |
| canon items recovered | 0/1 (0.0%) |
| fact answers present | 0/0 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `partial` | set | What are all the affiliations of Hybrid? | Devil Hunters Weapon Devils Chainsaw Man Church | Barem Bridge, Denji, Katana Man, Miri Sugo, Quanxi, Reze, Spear Hybrid, Whip Hybrid | <sub>https://chainsaw-man.fandom.com/wiki/Hybrid</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the affiliations of Hybrid? | `Hybrids` / `partial` | 0 found, 1 missing; returned 8 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
