# Suguru Geto — character-page prose pass (character 3 of 132)

- Date: 2026-08-25 (local 18:14)
- Page: **Suguru Geto** (slug `suguru_geto`, https://jujutsu-kaisen.fandom.com/wiki/Suguru_Geto)
- Batch: `questions/_jjk_page_suguru_geto.json` (54 page-gen → **94** after this pass)

## Final page-run (authoritative gate, facts beam top_k=50)

**NOT COMPLETE: 90/94 questions passed**

- set questions exact: **10/10 (100.0%)**
- fact answers present in the bundle: **80/84**
- All 4 remaining failures are **documented router gaps** (below). No gold errors remain.
- The 40 authored prose questions: 36 pass, 4 are the documented router gaps (065, 069, 073, 078).

## Triples authored

**40 prose triples** added, ids `jjk-pg-suguru_geto-055` … `jjk-pg-suguru_geto-094`
(batch 54 → 94; marked `prose:`, `expect_mode: qa`). Every answer verified as a
whitespace-collapsed + NFKC substring of the stored page text before bulk-add.

Previously-uncovered factual prose sections covered:

| section | # | content |
|---|---|---|
| Appearance | 6 | build/hair, eyes, 2006 hair, post-2007 hair, student uniform, priest attire (kāṣāya/yukata) |
| Abilities and Powers / Overview | 10 | one of four special-grade, "the strongest" w/ Gojo, short work of curse users, spirit-collection variety, curse-independence/CQ fighter, religious-group lure, decade threat, war on Jujutsu High, Night Parade true goal, Kyoto/Shinjuku split |
| Abilities and Powers / Cursed Technique | 8 | CSM control, orb ingestion, two-grade absorption, absorbing other sorcerers' curses, maximum technique, 4000-curse climax, Curtain definition, Curtain over a weaker barrier |
| Equipment | 2 | Playful Cloud (special-grade tool), Playful Cloud vs. both adversaries |
| Trivia | 14 | surname kanji, first-name meaning, 4 Popularity Polls, enrollment, specialty, favorite/least food, stress, most-popular male, attire real name, five-stripe reference |

## Gold errors fixed in-lane (2)

The **served** Trivia chunks carry inline CJK kanji + readings that the clean
`sections[].text` field (what `prose_dump` authors against) strips. Two authored
answers were therefore not verbatim against what the engine actually serves. Per
method class (1), the **answers** (not the questions) were corrected to exact
substrings of the served chunk text:

- **`jjk-pg-suguru_geto-081`** (What kanji make up Suguru Geto's surname?)
  → `Suguru's surname contains the kanji for "summer" 夏 ge and "oil" 油 tō`
  (kanji 夏/油 + readings ge/tō as served). Now passing.
- **`jjk-pg-suguru_geto-093`** (What is the real name of the attire Suguru Geto wears as a priest?)
  → `The real name of Suguru's attire is called Gojō kāṣāya 五袈裟 Gojō-kesa`
  (kanji 五袈裟 + romaji Gojō-kesa as served). Now passing.

Root-cause note (flagged, not an engine code change per method): this is genuine
wiki content, not corruption — the JJK Trivia section really shows the kanji +
readings. But `prose_dump` authors against the kanji-stripped `sections[].text`,
which silently diverges from the served chunk text for any section containing
inline CJK/ruby. Worth an engine review so authoring and serving agree.

## Retires

**None.** 078 was a cross-page candidate (the dedicated "Curtain" technique page
is served for it), but the Curtain page carries a *different* trapping claim
("trapping non-sorcerers" via binding vows) and not the Geto-specific "trapping
sorcerers over a weaker sorcerer's barrier" sentence — so 078 is a router gap,
not a cross-page fact, and stays in the batch.

## Engine (router) gaps documented (4)

Per method: not rephrased, engine code untouched. id · question · expected
verbatim answer (Geto page) · routing evidence · class.

- **`jjk-pg-suguru_geto-065`** — *Was Suguru Geto dependent on his curses in battle?*
  Expected: `Suguru was not overly dependent on his curses and was a highly capable close-quarters fighter as well.`
  Evidence: routed `mode=narrative`, 87 beats, **all** battle/event docs (Culling Game, Shibuya Incident, Satoru Gojo vs. Sukuna, Jujutsu Sorcerers vs. Kenjaku & Uraume, …); Geto character page **not** in bundle.
  Class: scope-word "in battle" pulls the question into the narrative battle route (G1/scope-word family).

- **`jjk-pg-suguru_geto-069`** — *What was the true goal of the Night Parade of a Hundred Demons?*
  Expected: `The true goal of the Night Parade of a Hundred Demons was to kill Yuta and steal special grade vengeful spirit Rika Orimoto from him.`
  Evidence: routed `mode=narrative`, 11 beats, **all** chapter/episode summaries (Ch 0-3, 0-4, 17, 101, 133, 173, Ep 46, 50, Vol 0 + one battle page); Geto page **not** in bundle.
  Class: event-name "Night Parade of a Hundred Demons" pulls the question into the narrative chapter-summary route (scope-word, new trigger).

- **`jjk-pg-suguru_geto-073`** — *Under what condition can Suguru Geto absorb a curse with no consequences?*
  Expected: `If the difference in grade is around two levels or higher, Suguru can absorb a curse with no consequences.`
  Evidence: routed `mode=roster`, `basis="Suguru Geto Techniques"`, **n_beats=0**, members=3 (Cursed Spirit Manipulation, Curtain, Maximum: Uzumaki), `confidence=partial`, warning: *"'under','condition','can','absorb','curse','consequences' did not narrow this set; every member was kept"*.
  Class: a condition/technique-mechanics question misroutes to the bare technique roster (G6 bare-roster family, new trigger "absorb a curse").

- **`jjk-pg-suguru_geto-078`** — *Can Suguru Geto cast Curtain over a weaker sorcerer's barrier?*
  Expected: `Suguru can cast curtains capable of trapping sorcerers inside of it and can do so over another weaker sorcerer's barrier as well.`
  Evidence: routed `mode=narrative`, 55 beats; bundle contains the dedicated technique pages **"Curtain"** + **"Cursed Spirit Manipulation"** plus battle pages; Geto character page **not** in bundle. The Geto-specific sentence is unique to the Geto page (Curtain page says "trapping non-sorcerers").
  Class: a technique-capability question is served the dedicated "Curtain" page bundle instead of the Geto character page.

## Notes

- The faithful triage replica (mode=auto, token_budget=60000) additionally flagged
  **079** (*What is the Playful Cloud?*) and **087** (*How was Suguru Geto enrolled at jujutsu high?*)
  as fails, but both **pass** the authoritative page-run gate — beam
  non-determinism / threshold difference between the replica and the facts beam. No action.
- Batch written back preserving the on-disk format (indent=1, `ensure_ascii=False`);
  CJK in the two fixed answers is stored as real UTF-8 codepoints (sliced directly
  from the served bundle text).
- Auto page-run reports (engine-generated) also at `jjk-suguru_geto-2026-08-25-1231`
  and `jjk-suguru_geto-2026-08-25-1242`.