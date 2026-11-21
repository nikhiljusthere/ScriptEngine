# Page campaign csm/episode_1 — 2026-09-17-0838

Batch `_csm_page_episode_1.json`: 12 questions (0 set, 12 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 6.0s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **12/12** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 12/12 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | Which season does Episode 1 belong to? | `routed qa` / `-` | 1 |
| **yes** | fact | What is the episode number of Episode 1? | `routed qa` / `-` | 1 |
| **yes** | fact | What is the episode title associated with Episode 1? | `routed qa` / `-` | Dog & Chainsaw |
| **yes** | fact | What are the kanji for Episode 1's name? | `routed qa` / `-` | 犬とチェンソー |
| **yes** | fact | What is the romaji of Episode 1's name? | `routed qa` / `-` | Inu to Chensō |
| **yes** | fact | When did Episode 1 air? | `routed qa` / `-` | October 11, 2022 (Oct 12, at 00:00)
October 25, 2022 (English Dub) |
| **yes** | fact | What is Episode 1 adapted from? | `routed qa` / `-` | Chapter 1 |
| **yes** | fact | In which arc does Episode 1 appear? | `routed qa` / `-` | Introduction arc |
| **yes** | fact | What is the opening song of Episode 1? | `routed qa` / `-` | Kick Back |
| **yes** | fact | What is the ending song of Episode 1? | `routed qa` / `-` | Chainsaw Blood |
| **yes** | fact | What comes before Episode 1? | `routed qa` / `-` | N/A |
| **yes** | fact | What comes after Episode 1? | `routed qa` / `-` | Episode 2 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
