# Page campaign jjk/shoko_ieiri_synopsis — 2026-09-03-1747

Batch `_jjk_page_shoko_ieiri_synopsis.json`: 12 questions (0 set, 12 fact), scored against the live server (started 2026-09-03T17:28:02+00:00), 10.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **11/12** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 11/12 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | fact | Why did Shoko start smoking again during the Shibuya Incident? | she answered that she felt nostalgic about her student days | - | <sub>https://jujutsu-kaisen.fandom.com/wiki/Shoko_Ieiri/Synopsis</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | When did Shoko start at Tokyo Jujutsu High? | `routed qa` / `-` | In 2005, she enrolled in Tokyo Jujutsu High as a first-year student along with Satoru Gojo and Suguru Geto. |
| **yes** | fact | How did Shoko get her doctor's license? | `routed qa` / `-` | Shoko obtained her doctor's license by passing the national examination, although she faked the documents needed for exam eligibility. |
| **yes** | fact | What did Shoko warn Gojo about keeping his Infinity constantly active? | `routed qa` / `-` | Shoko said that Gojo would fry his brain if he kept the technique always active |
| **yes** | fact | Who took Geto's body after Gojo killed him? | `routed qa` / `-` | Kenjaku took advantage of this and stole Geto's body. |
| **yes** | fact | Why did Gojo ask Shoko to keep Yuji officially dead? | `routed qa` / `-` | Gojo requested that Shoko keep Yuji's status as deceased to prevent the higher-ups from targeting him again |
| **yes** | fact | What did Shoko tell Nanami about the transfigured humans? | `routed qa` / `-` | Shoko explained to Nanami that the transfigured humans could not be saved, and the best course of action was to kill them. |
| **yes** | fact | How did Shoko confirm the dead sorcerers were Mahito's victims? | `routed qa` / `-` | Shoko then examined the dead sorcerers to confirm if they were indeed Mahito's victims for her report to Ijichi. |
| **yes** | fact | Why did Nobara doubt Shoko could treat the students? | `routed qa` / `-` | Nobara questioned whether Shoko would be awake or even sober at the moment. |
| no | fact | Why did Shoko start smoking again during the Shibuya Incident? | `routed narrative` / `-` | answer absent |
| **yes** | fact | How did Shoko help Hana Kurusu unseal Gojo? | `routed qa` / `-` | she along with Yuta Okkotsu treated Hana Kurusu's injuries so she could unseal Gojo from the Prison Realm |
| **yes** | fact | How did Gojo's body reach Shoko after the battle? | `routed qa` / `-` | his corpse was teleported by Ui Ui to Shoko |
| **yes** | fact | Did Shoko object to Yuta's plan to take over Gojo's body? | `routed qa` / `-` | despite Gojo being a close friend, Shoko did not object to his plan. |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
