# Page campaign jjk/gachinko_fight_club — 2026-09-04-1744

Batch `_jjk_page_gachinko_fight_club.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-04T17:31:17+00:00), 4.9s wall clock.

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
| **yes** | fact | Where does the Gachinko Fight Club operate? | `routed qa` / `-` | inside an abandoned multistory parking garage in Tochigi |
| **yes** | fact | What are the two rules for fighters at the Gachinko Fight Club? | `routed qa` / `-` | no jujutsu and no retreating |
| **yes** | fact | Why are the two rules for fighters there? | `routed qa` / `-` | Non-sorcerers can't see jujutsu and the fight needs to be where the spectators can see |
| **yes** | fact | Where is Hakari located during the fights? | `routed qa` / `-` | inside the monitor room on the roof of the building |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
