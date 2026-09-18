# Page campaign csm/yutaro_kurose — 2026-09-18-0328

Batch `_csm_page_yutaro_kurose.json`: 8 questions (2 set, 6 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 5.1s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **8/8** |
| set questions exact | 2/2 (100.0%) |
| canon items recovered | 9/9 (100.0%) |
| fact answers present | 6/6 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the allies of Yutaro Kurose? | `Every ally of Yutaro Kurose` / `declared` | 6 found, 0 missing; returned 6 |
| **yes** | set | What are all the affiliations of Yutaro Kurose? | `Yutaro Kurose's affiliations` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | fact | What are the kanji for Yutaro Kurose's name? | `routed qa` / `-` | 黒瀬 ユウタロウ |
| **yes** | fact | What is the romaji of Yutaro Kurose's name? | `routed qa` / `-` | Kurose Yūtarō |
| **yes** | fact | What is Yutaro Kurose's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is Yutaro Kurose's height? | `routed qa` / `-` | 165 cm (5'5") |
| **yes** | fact | What is the status of Yutaro Kurose? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Yutaro Kurose's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
