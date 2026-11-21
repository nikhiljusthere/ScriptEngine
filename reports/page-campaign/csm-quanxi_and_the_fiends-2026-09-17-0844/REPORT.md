# Page campaign csm/quanxi_and_the_fiends — 2026-09-17-0844

Batch `_csm_page_quanxi_and_the_fiends.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 1.0s wall clock.

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
| `exact` | fact | Who are Quanxi and the Fiends's notable members? | Quanxi Pingtsi † Long † Cosmo † Tsugihagi † | - | <sub>https://chainsaw-man.fandom.com/wiki/Quanxi_and_the_Fiends</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What is Quanxi and the Fiends's allegiance? | `routed qa` / `-` | China |
| no | fact | Who are Quanxi and the Fiends's notable members? | `routed roster` / `exact` | answer absent |
| **yes** | fact | In which manga chapter does Quanxi and the Fiends first appear? | `routed qa` / `-` | Chapter 54 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
