# Page campaign jjk/kurourushi_synopsis — 2026-09-03-1847

Batch `_jjk_page_kurourushi_synopsis.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-03T17:28:02+00:00), 2.5s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **3/3** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 3/3 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What kind of cursed spirit is Kurourushi? | `routed qa` / `-` | a cockroach cursed spirit born from humanity's fear towards cockroaches |
| **yes** | fact | Why was Kurourushi killing humans? | `routed qa` / `-` | it liked the taste of iron |
| **yes** | fact | What is Kurourushi's Festering Life Sword? | `routed qa` / `-` | an enchanted blade that mixes life and death |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
