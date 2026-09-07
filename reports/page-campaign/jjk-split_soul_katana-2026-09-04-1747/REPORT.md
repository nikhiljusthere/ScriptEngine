# Page campaign jjk/split_soul_katana — 2026-09-04-1747

Batch `_jjk_page_split_soul_katana.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-04T17:31:17+00:00), 4.2s wall clock.

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
| **yes** | fact | What is the Split Soul Katana? | `routed qa` / `-` | a large, curved Japanese broadsword with a distinctive feature: a fur-wrapped tsuba (hand guard) |
| **yes** | fact | What does the Split Soul Katana ignore to cut through? | `routed qa` / `-` | all physical toughness |
| **yes** | fact | How much is the Split Soul Katana worth? | `routed qa` / `-` | 500 million yen |
| **yes** | fact | What did Maki destroy using the Split Soul Katana? | `routed qa` / `-` | the entire Zenin Clan |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
