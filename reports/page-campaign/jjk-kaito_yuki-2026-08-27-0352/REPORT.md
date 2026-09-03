# Page campaign jjk/kaito_yuki — 2026-08-27-0352

Batch `_jjk_page_kaito_yuki.json`: 51 questions (3 set, 48 fact), scored against the live server (started 2026-08-27T01:56:08+00:00), 114.1s wall clock.

## Prose pass summary

**Character:** Kaito Yuki, slug `kaito_yuki`. Batch went 25 → 51 questions (structured-pass 25 preserved, +26 prose, ids `jjk-pg-kaito_yuki-026`..`051`).

**Sections covered (Cursed Technique + Appearance):**
- `Appearance` (5 questions) — hair, ahoge, uniform, boots, sleeve coloring.
- `Abilities and Powers / Cursed Technique` (21 questions) — Prayer Formation Technique (barrier/cornerstone mechanic, binding vow, Kensuke Nagino's false name), Night Hunt, Prayer to Palm Strike. Includes the required adversarial forms: yes/no (`Can Kaito Yuki boost himself with his own Prayer Formation Technique?`), counterfactual (`What would have happened to someone inside Kaito Yuki's barrier if they had not been holding the cornerstone?`), comparative (`Which of Kaito Yuki's two extension techniques amplifies the force of a punch instead of confining cursed spirits?`).

**Sections skipped (no prose to author):**
- `Synopsis` and `Synopsis / Phantom Parade` — both listed as uncovered in the coverage ledger, but the wiki page's raw JSON (`series/jjk/wikitext/Kaito Yuki.json`) has **empty text** for both (`Synopsis` section text is `""`; `Phantom Parade` subsection wikitext is only `{{Section stub}}`). Nothing factual exists to gold here; this is a page-content gap (an un-filled wiki stub), not an engine or authoring gap.

**Gold errors fixed:** none — all 26 authored answers were verified as verbatim wiki substrings before bulk-add (`precheck.py` against the raw `lead`+`sections[].text`+`sections[].wikitext`), and one kanji-only gold (`祈陣呪法` for "What are the kanji for Kaito Yuki's Prayer Formation Technique?") followed house precedent (Kenjaku/Tengen/Hanami) for `{{Nihongo}}`-rendered chunks — verified present in the live served bundle before adding.

**Retires:** none.

**Documented gaps:** none — the run was clean, 51/51 (48/48 facts, 3/3 sets) on the first `page-run`, no `prose_triage.py` failures to root-cause.

## Flagged finding (out of my scope — documenting only, no engine edit)

**Personality-section chunker defect (word-count boundary drop).** While dumping sections I initially mistook `Personality` for part of my uncovered-section list; it is **not** — the coverage ledger already marks it `covered_by` a set of `page-gen:battle:...` tags (a pre-existing, unrelated-content coverage quirk, not something I touched). I removed the 2 Personality triples I had drafted before bulk-add, so nothing was authored against it.

However, while investigating I confirmed a genuine, separate indexing defect worth flagging to the engine owner (opencode):

- Kaito Yuki's wiki page **does** have a real `Personality` section with real prose: *"Kaito values discipline, and is hostile to Yuji Itadori, whose existence he believes goes against the rules of Jujutsu."* (confirmed verbatim in `series/jjk/wikitext/Kaito Yuki.json` → `sections[]`, and in `facts.db` → `sections` table, row id 4500, `word_count=19`).
- That section has **zero chunks** in `facts.db` → `chunks` table for `doc_title='Kaito Yuki'` (only 7 chunks exist: the level-0 card, 2×`Appearance`, 4×`Abilities and Powers / Cursed Technique` — no `Personality` chunk at any level).
- Root cause (read, not edited): `scriptengine/index/chunker.py` `chunk_page()`, the section-drop guard:
  ```python
  if section.word_count < min_words and not getattr(section, "is_item", False):
      continue
  ```
  with `min_words: int = 20` (default). The `Personality` section's `word_count` is **19** — one word under the floor — so the whole section (including its level-1 chunk, which normally survives regardless of the target-word passage split) is silently dropped from the index. This is a **boundary-condition bug in the chunker**, not a ranking/retrieval-quality issue: the text is not merely ranked low, it was never indexed at all. Live-probed on the running server (`/context`, `mode=auto`, `subject=Kaito Yuki`) for `"What does Kaito Yuki value?"` and `"Why is Kaito Yuki hostile toward Yuji Itadori?"` — both return 8 beats, none containing "discipline" or the personality sentence, confirming the gap end-to-end.
- Scope note: this is unrelated to my assigned uncovered sections (Appearance/Synopsis/Phantom Parade/Cursed Technique) and I made no engine-code changes. Documenting only, per the no-engine-edits constraint. Likely affects any other character whose short prose section (Personality or otherwise) lands at word_count 15–19.

## Headline

| | |
|---|---:|
| **questions passed** | **51/51** |
| set questions exact | 3/3 (100.0%) |
| canon items recovered | 6/6 (100.0%) |
| fact answers present | 48/48 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Kaito Yuki? | `Every named technique of Kaito Yuki` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the affiliations of Kaito Yuki? | `Kaito Yuki's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | Every battle involving Kaito Yuki | `Every battle involving Kaito Yuki` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What are the kanji for Kaito Yuki's name? | `routed qa` / `-` | 結木海斗 |
| **yes** | fact | What is the romaji of Kaito Yuki's name? | `routed qa` / `-` | Yūki Kaito |
| **yes** | fact | What is Kaito Yuki's race? | `routed qa` / `-` | Human |
| **yes** | fact | What is Kaito Yuki's gender? | `routed qa` / `-` | Male |
| **yes** | fact | How old is Kaito Yuki? | `routed qa` / `-` | 16 |
| **yes** | fact | What is Kaito Yuki's birthday? | `routed qa` / `-` | May 5, 2002 |
| **yes** | fact | What is the status of Kaito Yuki? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Kaito Yuki's occupation? | `routed qa` / `-` | Jujutsu Sorcerer Student |
| **yes** | fact | Who is Kaito Yuki's Japanese voice actor? | `routed qa` / `-` | Koutaro Nishiyama |
| **yes** | fact | What is the outcome of Jujutsu Sorcerers vs. Kenjaku & Uraume? | `routed qa` / `-` | Yuki interrupts the battle. Kenjaku escapes with Prison Realm. |
| **yes** | fact | Where did Jujutsu Sorcerers vs. Kenjaku & Uraume take place? | `routed qa` / `-` | Shibuya Police Station, Udagawa Police Box |
| **yes** | fact | When does Jujutsu Sorcerers vs. Kenjaku & Uraume take place? | `routed qa` / `-` | October 31, 2018 |
| **yes** | fact | In which manga chapter does Jujutsu Sorcerers vs. Kenjaku & Uraume begin? | `routed qa` / `-` | Chapter 133 |
| **yes** | fact | In which episode is Jujutsu Sorcerers vs. Kenjaku & Uraume depicted? | `routed qa` / `-` | Episode 46 |
| **yes** | fact | In which arc does Jujutsu Sorcerers vs. Kenjaku & Uraume take place? | `routed qa` / `-` | Shibuya Incident |
| **yes** | fact | Which techniques did Kaito Yuki use in Jujutsu Sorcerers vs. Kenjaku & Uraume? | `routed qa` / `-` | Garuda |
| **yes** | fact | What is the outcome of Yuki Tsukumo & Choso vs. Kenjaku? | `routed qa` / `-` | Kenjaku is victorious. |
| **yes** | fact | Where did Yuki Tsukumo & Choso vs. Kenjaku take place? | `routed qa` / `-` | Tombs of the Star |
| **yes** | fact | When does Yuki Tsukumo & Choso vs. Kenjaku take place? | `routed qa` / `-` | November 16, 2018 |
| **yes** | fact | In which manga chapter does Yuki Tsukumo & Choso vs. Kenjaku begin? | `routed qa` / `-` | Chapter 203 |
| **yes** | fact | In which arc does Yuki Tsukumo & Choso vs. Kenjaku take place? | `routed qa` / `-` | Culling Game |
| **yes** | fact | Which techniques did Kaito Yuki use in Yuki Tsukumo & Choso vs. Kenjaku? | `routed qa` / `-` | Star Rage, Garuda, Reverse Cursed Technique, Simple Domain |
| **yes** | fact | What does Kaito Yuki's hair look like? | `routed qa` / `-` | short and messy black hair |
| **yes** | fact | What small tuft of hair does Kaito Yuki have? | `routed qa` / `-` | a short ahoge |
| **yes** | fact | What kind of uniform does Kaito Yuki wear? | `routed qa` / `-` | a modified jujutsu uniform |
| **yes** | fact | What footwear does Kaito Yuki wear with his uniform? | `routed qa` / `-` | knee-high boots |
| **yes** | fact | What color are the sleeves of Kaito Yuki's outfit? | `routed qa` / `-` | white sleeves with a black line on them |
| **yes** | fact | What is the name of Kaito Yuki's innate technique? | `routed qa` / `-` | Prayer Formation Technique |
| **yes** | fact | What are the kanji for Kaito Yuki's Prayer Formation Technique? | `routed qa` / `-` | 祈陣呪法 |
| **yes** | fact | What does Kaito Yuki's Prayer Formation Technique use as the core of its barrier? | `routed qa` / `-` | cornerstone |
| **yes** | fact | What does the barrier from Kaito Yuki's technique do to the people trapped inside it? | `routed qa` / `-` | places a curse on those inside it, forcing them to fight |
| **yes** | fact | What does the forced fighting inside Kaito Yuki's barrier amplify? | `routed qa` / `-` | the cursed energy within it |
| **yes** | fact | What kind of vow binds Kaito Yuki's Prayer Formation Technique? | `routed qa` / `-` | a pre-established binding vow |
| **yes** | fact | Can Kaito Yuki boost himself with his own Prayer Formation Technique? | `routed qa` / `-` | the technique cannot affect Yuki himself |
| **yes** | fact | What else does the binding on Kaito Yuki's technique apply to besides Kaito? | `routed qa` / `-` | which carries his cursed energy |
| **yes** | fact | Who inside Kaito Yuki's barrier is left unaffected by his technique? | `routed qa` / `-` | anyone within the barrier who possesses the stone |
| **yes** | fact | Who falsely named Kaito Yuki's technique? | `routed qa` / `-` | Kensuke Nagino |
| **yes** | fact | What false name did Kensuke Nagino give to Kaito Yuki's technique? | `routed qa` / `-` | Cursed Technique Boost |
| **yes** | fact | Why did Kensuke Nagino give Kaito Yuki's technique a false name? | `routed qa` / `-` | to conceal its true nature |
| **yes** | fact | What would have happened to someone inside Kaito Yuki's barrier if they had not been holding the cornerstone? | `routed qa` / `-` | places a curse on those inside it, forcing them to fight |
| **yes** | fact | What does Kaito Yuki's Night Hunt create? | `routed qa` / `-` | a barrier that confines cursed spirits |
| **yes** | fact | What is Kaito Yuki's Night Hunt similar to in function? | `routed qa` / `-` | a curtain |
| **yes** | fact | What does Kaito Yuki's Night Hunt do to the humans caught in its barrier? | `routed qa` / `-` | amplifies the cursed energy of humans within the barrier |
| **yes** | fact | How does Kaito Yuki's Night Hunt change the way humans inside it move? | `routed qa` / `-` | making their bodies feel lighter and easier to move |
| **yes** | fact | What shape is the barrier that Kaito Yuki's Prayer to Palm Strike creates? | `routed qa` / `-` | a spherical barrier around Yuki's fist |
| **yes** | fact | What is Kaito Yuki holding in his fist when he uses Prayer to Palm Strike? | `routed qa` / `-` | the barrier's cornerstone |
| **yes** | fact | What happens when Kaito Yuki punches an opponent with Prayer to Palm Strike? | `routed qa` / `-` | shatters the barrier and amplifies the force of the punch |
| **yes** | fact | Which of Kaito Yuki's two extension techniques amplifies the force of a punch instead of confining cursed spirits? | `routed qa` / `-` | Prayer to Palm Strike |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).
