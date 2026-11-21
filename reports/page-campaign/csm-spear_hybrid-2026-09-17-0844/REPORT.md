# Page campaign csm/spear_hybrid — 2026-09-17-0844

Batch `_csm_page_spear_hybrid.json`: 7 questions (4 set, 3 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 1.5s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **3/7** |
| set questions exact | 0/4 (0.0%) |
| canon items recovered | 4/13 (30.8%) |
| fact answers present | 3/3 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Spear Hybrid? | Hybrid Transformation, Augmented Body, Spear Generation, Blood Consumption, Nigh-Immortality | - | <sub>https://chainsaw-man.fandom.com/wiki/Spear_Hybrid</sub> |
| `exact` | set | What are all the allies of Spear Hybrid? | - | Barem Bridge, Denji, Katana Man, Miri Sugo, Quanxi, Reze, Spear Hybrid, Whip Hybrid | <sub>https://chainsaw-man.fandom.com/wiki/Spear_Hybrid</sub> |
| `exact` | set | What are all the superiors of Spear Hybrid? | Makima | Barem Bridge, Denji, Katana Man, Miri Sugo, Quanxi, Reze, Spear Hybrid, Whip Hybrid | <sub>https://chainsaw-man.fandom.com/wiki/Spear_Hybrid</sub> |
| `exact` | set | What are all the affiliations of Spear Hybrid? | Makima (brainwashed), Tokyo Special Division 5 (formerly), Chainsaw Man Church | Barem Bridge, Denji, Katana Man, Miri Sugo, Quanxi, Reze, Spear Hybrid, Whip Hybrid | <sub>https://chainsaw-man.fandom.com/wiki/Spear_Hybrid</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Spear Hybrid? | `-` / `-` | 0 found, 5 missing; returned 0 |
| no | set | What are all the allies of Spear Hybrid? | `Hybrids` / `exact` | 3 found, 0 missing; returned 8 |
| no | set | What are all the superiors of Spear Hybrid? | `Hybrids` / `exact` | 1 found, 1 missing; returned 8 |
| no | set | What are all the affiliations of Spear Hybrid? | `Hybrids` / `exact` | 0 found, 3 missing; returned 8 |
| **yes** | fact | What is the status of Spear Hybrid? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Spear Hybrid's occupation? | `routed qa` / `-` | Public Safety Devil Hunter (brainwashed) |
| **yes** | fact | What is Spear Hybrid's gender? | `routed qa` / `-` | Male |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
