# Page campaign csm/weapon_devils — 2026-09-18-0441

Batch `_csm_page_weapon_devils.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 2.7s wall clock.

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
| **yes** | fact | What is Weapon Devils's allegiance? | `routed qa` / `-` | Four Horsemen (formerly)
Hybrids (currently)
Chainsaw Man Church (via proxy) |
| **yes** | fact | Who are Weapon Devils's notable members? | `routed roster` / `partial` | Katana Devil, Bomb Devil, Bow Devil |
| **yes** | fact | In which manga chapter does Weapon Devils first appear? | `routed qa` / `-` | Chapter 87 (mentioned) |
| **yes** | fact | What type of song is Weapon Devils? | `routed qa` / `-` | Specific group of weapon-based Devils that worked under the Four Horsemen |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
