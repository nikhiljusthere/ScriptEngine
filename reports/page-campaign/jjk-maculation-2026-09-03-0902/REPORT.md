# Page campaign jjk/maculation — 2026-09-03-0902

Batch `_jjk_page_maculation.json`: 10 questions (1 set, 9 fact), scored against the live server (started 2026-09-03T08:26:48+00:00), 9.1s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **10/10** |
| set questions exact | 1/1 (100.0%) |
| canon items recovered | 1/1 (100.0%) |
| fact answers present | 9/9 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | Every battle involving Maculation | `Every battle involving Maculation` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Maculation's name? | `routed qa` / `-` | 斑 |
| **yes** | fact | What is the romaji of Maculation's name? | `routed qa` / `-` | Madara |
| **yes** | fact | In which manga chapter does Maculation first appear? | `routed qa` / `-` | Modulo Chapter 5 |
| **yes** | fact | What is the outcome of Marulu Val Vol Yelvori vs. Tsurugi Okkotsu? | `routed qa` / `-` | Tsurugi allows Maru to win. |
| **yes** | fact | Where did Marulu Val Vol Yelvori vs. Tsurugi Okkotsu take place? | `routed qa` / `-` | Tokyo, Japan |
| **yes** | fact | When does Marulu Val Vol Yelvori vs. Tsurugi Okkotsu take place? | `routed qa` / `-` | January 14, 2087 |
| **yes** | fact | In which manga chapter does Marulu Val Vol Yelvori vs. Tsurugi Okkotsu begin? | `routed qa` / `-` | Chapter 14 |
| **yes** | fact | How does the user of Maculation activate the technique? | `routed qa` / `-` | The user crouches down and activates Simple Domain, which briefly manifests as several interconnected domains around them. |
| **yes** | fact | What does the attack interception program in Maculation do? | `routed qa` / `-` | This Simple Domain incorporates a fully automatic attack interception program that enables the user to automatically block or evade any attacks made against them by intruders in the domain while simultaneously counterattacking. This technique is highly effective when facing multiple opponents. |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
