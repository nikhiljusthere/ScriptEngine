# Page campaign jjk/heart_catch — 2026-09-03-0800

Batch `_jjk_page_heart_catch.json`: 11 questions (1 set, 10 fact), scored against the live server (started 2026-09-03T07:35:43+00:00), 10.5s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **11/11** |
| set questions exact | 1/1 (100.0%) |
| canon items recovered | 1/1 (100.0%) |
| fact answers present | 10/10 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | Every battle involving Heart Catch | `Every battle involving Heart Catch` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Heart Catch's name? | `routed qa` / `-` | 人心掌握 |
| **yes** | fact | What is the romaji of Heart Catch's name? | `routed qa` / `-` | Hāto Kyatchi |
| **yes** | fact | In which manga chapter does Heart Catch first appear? | `routed qa` / `-` | Chapter 255 |
| **yes** | fact | What is the outcome of Jujutsu Sorcerers vs. Sukuna? | `routed qa` / `-` | The jujutsu sorcerers are victorious. |
| **yes** | fact | Where did Jujutsu Sorcerers vs. Sukuna take place? | `routed qa` / `-` | Shinjuku |
| **yes** | fact | When does Jujutsu Sorcerers vs. Sukuna take place? | `routed qa` / `-` | December 24, 2018 |
| **yes** | fact | In which manga chapter does Jujutsu Sorcerers vs. Sukuna begin? | `routed qa` / `-` | Chapter 244 |
| **yes** | fact | In which arc does Jujutsu Sorcerers vs. Sukuna take place? | `routed qa` / `-` | Shinjuku Showdown |
| **yes** | fact | What does Heart Catch manifest? | `routed qa` / `-` | Activating this technique manifests a large virtual hand that floats in the air near the user. |
| **yes** | fact | How strong is Heart Catch's virtual hand? | `routed qa` / `-` | The hand has enough force to crumble parts of a building when slammed against it. |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
