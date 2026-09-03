# JJK Prose Pass - Hanako of the Toilet

Slug: `hanako_of_the_toilet` | Batch: `questions/_jjk_page_hanako_of_the_toilet.json`
Wiki: `series/jjk/wikitext/Hanako of the Toilet.json` | Pre-existing batch: 7 page-gen
questions (ids 001-007, all infobox facts), max_id 7, order[145].

## Sections covered

All 5 uncovered factual sections from the coverage ledger were authored:

| Section | Questions authored |
|---|---|
| `Appearance` | 1 (`008`) |
| `History / Phantom Parade` | 11 (`009`-`019`) |
| `Abilities and Powers` | 3 (`020`-`022`) |
| `Trivia` | 1 (`023`) |
| `History` (parent heading, no own text) | 0 - empty section, nothing to author |

Skipped per instructions: `References`, `Navigation` (boilerplate, already retired
in the coverage ledger). No "Quotes" or "Battles & Events" sections exist on this
page.

Adversarial forms included per the R5 mandate: yes/no (`020` "Does Hanako of the
Toilet have any known abilities?", `021` "Has Hanako of the Toilet appeared
directly in the series?"), counterfactual (`018` "What would have happened if
Yuji, Megumi, and Nobara had encountered Hanako of the Toilet?"). This page has
no numeric/comparable facts to anchor a natural comparative question against
(it is a two-paragraph stub about a character who never appears on-page), so no
comparative form was authored - noted rather than forced onto an unnatural
question.

## Triples authored (16, ids 008-023)

All 16 answers verified as verbatim substrings of the wiki `text`/`wikitext`
fields before bulk-add (script `C:\Users\Nikhil\.claude\jobs\3b511348\tmp\verify_verbatim.py`,
0 lint failures: no answer-in-question, all wh-words fronted, no misused
"how many").

| id | section | question | answer |
|---|---|---|---|
| 008 | Appearance | What is known about Hanako of the Toilet's appearance? | Hanako's appearance is unknown |
| 009 | History / Phantom Parade | When was Hanako of the Toilet first mentioned? | a few days after the Kyoto Sister-School Goodwill Event |
| 010 | History / Phantom Parade | Who was sent on the mission where Hanako of the Toilet was first mentioned? | Yuji Itadori, Megumi Fushiguro, and Nobara Kugisaki |
| 011 | History / Phantom Parade | Where were Yuji, Megumi, and Nobara sent on their mission? | an abandoned school on the outskirts of Tokyo |
| 012 | History / Phantom Parade | Why were Yuji, Megumi, and Nobara sent to the abandoned school? | to exorcise cursed spirits |
| 013 | History / Phantom Parade | What did Yuji remark about the abandoned school upon arrival? | the place feels weird |
| 014 | History / Phantom Parade | What did Yuji joke they were more likely to encounter at the abandoned school than a cursed spirit? | a ghost |
| 015 | History / Phantom Parade | What did Yuji mention when Nobara brought up Hanako as an example? | a portrait of Beethoven in the music room |
| 016 | History / Phantom Parade | What does the portrait of Beethoven in the music room supposedly do? | stares as people |
| 017 | History / Phantom Parade | What did Megumi say Hanako actually is? | a legitimate curse classified as special grade |
| 018 | History / Phantom Parade | What would have happened if Yuji, Megumi, and Nobara had encountered Hanako of the Toilet? | they would be in serious danger if they encountered her |
| 019 | History / Phantom Parade | What did Yuji jokingly reply after Megumi's warning about Hanako? | he will stay away from the toilet |
| 020 | Abilities and Powers | What does Hanako of the Toilet's special grade rank imply about her? | immense power |
| 021 | Abilities and Powers | Does Hanako of the Toilet have any known abilities? | her abilities remain unknown |
| 022 | Abilities and Powers | Has Hanako of the Toilet appeared directly in the series? | has only been mentioned and has not appeared directly |
| 023 | Trivia | What is Hanako of the Toilet based on? | the Japanese urban legend of the same name |

(Written ids are `jjk-pg-hanako_of_the_toilet-008` through `-023`, confirmed by
`prose_bulk_add.py` output: "Batch now: 23 questions (IDs up to
jjk-pg-hanako_of_the_toilet-023)".)

## Score

`page-run --series jjk --batch hanako_of_the_toilet` (server started
2026-08-27T01:56:08Z, cuda, health OK): **21/23 fact answers present** (0/0
sets). Auto-generated headline table is in this same directory (tool output).

All 7 pre-existing page-gen questions (001-007) still pass. 14 of 16 added
prose questions pass. 2 fail - both triaged below as the same
retrieval/chunking gap, documented per method (not rephrased, not retired).

## Gold errors fixed

None. All 16 answers were verbatim on first authoring (verified pre-bulk-add
against the wiki JSON's `text` and `wikitext` fields).

## Retires

None.

## Documented gaps (2)

Both failures triaged with `prose_triage.py` (faithful scorer replica:
mode=auto, token_budget=60000, subject hint, norm + word-boundary) and
confirmed with a raw `/context` probe dump of all served beats.

### Gap 1 - `jjk-pg-hanako_of_the_toilet-008`
- Question: "What is known about Hanako of the Toilet's appearance?"
- Answer (verbatim): "Hanako's appearance is unknown"
- Routed basis: qa, correctly on the Hanako of the Toilet page (subject hint honored)
- n_beats served: 8 - beats 0 (infobox card), 1/3/4 (Phantom Parade
  paragraphs), 2 (Abilities and Powers), plus 3 unrelated cross-page beats
  (Zenin estate Plot Details, Shibuya Event, Miyaguni Appearance) filling out
  the beam. The Hanako `Appearance` section itself is never in the beam - not
  merely low-ranked, it is absent from the index entirely (see Flagged Defect
  below).
- Absent words: none individually flagged (all are common short words), but
  the exact phrase never appears anywhere in the served bundle.
- Class: Retrieval/chunking gap (right page, but the section is never
  chunked at all - stronger than "not served," since no query rephrasing can
  retrieve a chunk that was never written to the index).

### Gap 2 - `jjk-pg-hanako_of_the_toilet-023`
- Question: "What is Hanako of the Toilet based on?"
- Answer (verbatim): "the Japanese urban legend of the same name"
- Routed basis: qa, correctly on the Hanako of the Toilet page
- n_beats served: 8 - same shape as Gap 1: infobox + 3 Phantom Parade beats +
  Abilities and Powers + 3 unrelated cross-page beats (Zenin estate,
  Megumi/Culling Game synopsis, Hanami synopsis). The Hanako `Trivia` section
  is never in the beam.
- Absent words: `Japanese`, `same` (triage tool's >3-letter word check; the
  full phrase is absent).
- Class: Retrieval/chunking gap, same root cause as Gap 1.

Neither gap is retriable (no cross-page fact - both sentences are native to
this page) and neither is a router gap (routing to qa on the right page is
already correct). Per the METHOD CORRECTION, these are left failing and
documented rather than rephrased or retired.

## FLAGGED DEFECT (root cause of both gaps - documented only, NOT fixed, no
`scriptengine/` edits made per mandate)

**Root cause:** `scriptengine/index/chunker.py::chunk_page`, around line 299:

    if section.word_count < min_words and not getattr(section, "is_item", False):
        continue

`min_words` defaults to 20. Any section under the 20-word floor that is not an
item-marker section (`is_item`) is silently dropped and never written to the
`chunks` table - not merely down-ranked. Confirmed directly against
`series/jjk/facts.db`: the `sections` table holds full text for Hanako's
`Appearance` (id 3993, 4 words: "Hanako's appearance is unknown.") and
`Trivia` (id 3997, 15 words: "Hanako of the Toilet is based on the Japanese
urban legend of the same name."), but neither `section_id` appears anywhere
in the `chunks` table for this document (only 7 chunks total for doc_id 498,
covering the infobox card, the two `History / Phantom Parade` sub-paragraphs,
and `Abilities and Powers`, which is 26 words and clears the floor).

**Corpus-wide impact (jjk series only):** of 5,416 sections with any text,
1,662 (~31%) are under the 20-word floor and have zero chunks. The large
majority are legitimately-excluded roster/boilerplate sections (`Locations`
346, `Navigation` 335, `Battles & Events` 332, `Jujutsu` 209, character
appearance-order lists 154, `Featured Characters` 31, song-lyric `TV/Full
Version` blocks, etc. - filtering these out is intentional and correct). But
**198 are genuine prose-bearing sections silently and permanently
unretrievable**, concentrated in short `Trivia` (42 pages), `Author Quote`
(25), `Summary` (11), `Personality` (4), `Abilities and Powers` (4),
`Appearance`, and `History` sections across many character/song/media pages -
including Hanako of the Toilet (this batch), Jin Itadori, Kaito Yuki, Kaori
Itadori, Kensuke Nagino, Nobuaki Zenin, Sorcerer Clan/Zenin Clan, and roughly
40 more pages' worth of short Trivia/Personality/Abilities blurbs.

This is a hard availability gap, distinct from the existing G5/G11/G13
retrieval-ranking family (where the chunk exists but ranks below top-k for a
given phrasing): no query phrasing, subject hint, or router fix can surface
text that was never indexed. Fix would be either (a) lowering/removing the
`min_words` floor for non-boilerplate section titles, or (b) merging a short
trailing section into its neighboring chunk instead of dropping it outright,
so short-but-real prose survives while true boilerplate (`Navigation`,
`References`, roster lists) is still excluded by title. This finding is
handed to the engine team (opencode) for a possible new G-n gate item; no
`scriptengine/` files were modified as part of this task.

## Verification queries run (read-only)

- `/context` probes for both failing questions with `subject=Hanako of the
  Toilet` (raw beat dump via a temp probe script, confirmed correct page
  routing and confirmed both short sections are absent from the served beam).
- Corpus-wide SQL against `series/jjk/facts.db` (`sections` vs `chunks` join
  on `section_id`) to establish the 1,662 / 198 figures above.
