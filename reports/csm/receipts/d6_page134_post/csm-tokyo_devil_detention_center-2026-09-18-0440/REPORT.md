# Page campaign csm/tokyo_devil_detention_center — 2026-09-18-0440

Batch `_csm_page_tokyo_devil_detention_center.json`: 5 questions (0 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 3.2s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/5** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | Which series does Tokyo Devil Detention Center belong to? | `routed qa` / `-` | Tokyo Devil Detention Center |
| **yes** | fact | What type of song is Tokyo Devil Detention Center? | `routed qa` / `-` | Detention Center |
| **yes** | fact | What services does Tokyo Devil Detention Center provide? | `routed qa` / `-` | Public Security |
| **yes** | fact | Who are Tokyo Devil Detention Center's employees? | `routed roster` / `partial` | Unnamed Surgeons, Unnamed Devil Hunters, Unnamed Guards, Takagi †, Quanxi |
| **yes** | fact | In which manga chapter does Tokyo Devil Detention Center first appear? | `routed qa` / `-` | Chapter 156 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
