# Technique Prose Template — JJK (149 pages)

Prepared for the **techniques** wave of the prose pass (after the 146 characters,
59 episodes and 90 battles). Study of all 149 technique pages in
`series/jjk/wikitext/` (full-corpus census 2026-09-02: section inventory,
infobox fact keys, Refs stats; spot-read *Boogie Woogie* and *Binding Vow* in
depth, six scaffold batches inventoried).

## Page anatomy

- `page_type = technique`; infobox `technique infobox` (142) /
  `Technique Infobox` (7, casing variant) — the discovery is structural, casing
  is not an issue.
- **Infobox facts (structured gold, not prose), presence of 149:** `user` 149,
  `debut` 148, `name` 145, `kanji` 145, `romaji` 145, `type` 138,
  `capabilities` 130, `anime debut` 121, `move range` 76, `derived ability` 67,
  `derived item` 14, `other` 7, `viz` 1, `voice` 1.
- **Lead: 149/149 non-empty** (median 113 ch; max ~755, *Jujutsu*).
- **Refs: min 1 / median 7 / max 91 — no zero-Ref page.** Citations are written
  *inline in the prose* as `(Chapter N, Episode M)` markers; the `References`
  section body is usually empty.

### Section layout and presence (of 149)

| section | present / non-empty | body size | role in the pass |
|---|---:|---|---|
| Description | 144 / 132 | 1–2 KB, med 551 ch | 2–4 entries (activation, effect, limits) |
| Usage | 138 / 98 | med 726 ch, max 8,748 | **user-scoped entries** (below) |
| Trivia | 61 / 55 | 48–809 ch | 1–2 bullet entries, subject named |
| Related Techniques | 32 | 221–2,102 ch | per-extension-technique entries |
| Domain Expansion (L2) | 11 | — | the technique *is* a domain; 1–3 entries |
| History / Overview | 3 / 2 | short | 1–3 entries |
| one-off L2s (15 names × 1 page) | 15 | short | 1–3 each, subject named |
| References | 146 | empty | the only `{{Ref}}`-carrying section |
| Navigation / See Also | 149 | navbox | skip |

The 15 one-off L2s (one page each): `Cursed Energy Detection`,
`Cursed Restrictions`, `Commands`, `Technique Activation`, `Innate Techniques`,
`Non-Innate Techniques`, `Drawbacks`, `Countermeasures`, `Battles & Events`,
`Descriptions`, `Taido Martial Arts`, `Glossary`, `Advanced Techniques`,
`New Shadow Style Techniques`, `Shikigami Combinations`.

**Usage anatomy:** its L3 subsections are named after *users* (Sukuna ×10,
Yuta Okkotsu ×8, Yuji Itadori / Megumi Fushiguro / Choso ×6, Satoru Gojo ×5,
Noritoshi Kamo / Atsuya Kusakabe ×5 …). Usage prose answers "how does *this
user* apply the technique", so Usage questions are user-scoped
("How does Sukuna use X?"), one per user subsection (1–3 each); the five
heavy pages (Kogane 9.6 KB, Boogie Woogie 9.4, Malevolent Shrine 8.9, Cursed
Energy 8.6, Idle Death Gamble 7.6 KB total) need scene-beat entries inside
their Usage subsections, not one "how is it used" question.

## Sourcing: route one (inline markers)

Technique prose is densely footnoted — the inline `(Chapter N, Episode M)`
markers resolve chapter→episode through the graph (route one, the character-
wave shape). `cli audit` on technique pages: expect `sentences w/ chapter` and
`sentences w/ episode` both high. Do not "fix" that.

## What to author, per section

1. **Lead** (149/149) — 1–2 entries: what the technique is, who uses it, what
   it does. "Who uses X?" may be authored **at most once** and only when the
   user's name (or the generic `user` value) appears verbatim in the lead;
   the infobox `user` fact is the source of truth, not a prose answer.
2. **Description** (132) — 2–4: how it activates, what it does, its
   limitations/cost.
3. **Usage** (98) — user-scoped, per the anatomy note above.
4. **Trivia** (55) — bullet entries naming the bullet's subject.
   **Known open chunking gap** (HANDOFF open gaps): a generic question does not
   serve a Trivia bullet — author questions that name the bullet's subject, and
   if a miss appears, diagnose the gap, don't rephrase.
5. **Related Techniques** (32) — the section is prose, not a link list: each
   extension technique is named and described (some with Refs). Author one
   entry per described extension ("What is Kaichi, the Auspicious Beast
   Number One?"). Do **not** author a closed-set "what are all the extensions
   of X?" question — no roster is declared for it; that is a structured-layer
   gap, not a prose question (record it, don't invent the answer set).
6. **Domain Expansion** L2 (11: *Construction, Copy, Disaster Flames / Plants
   / Tides, Idle Transfiguration, Innate Domain, Light, Projection Sorcery,
   Shrine, Ten Shadows Technique*) — 1–3: the domain's name/effect/activation.
7. **History / Overview / one-off L2s** — 1–3 each, subject named. The one
   `Battles & Events` L2 (single page) is battle-list-shaped: author only if it
   carries descriptive prose; its list content is the structured layer's.
8. **Infobox-only values** (`type`, `capabilities`, `move range`,
   `derived ability/item`) — author an entry **only when the value appears
   verbatim** in the lead or Description. Numbers/facts are looked up, never
   inferred into a section that doesn't state them.

## Structured half (already in the batches — do not re-author)

All 149 scaffold batches exist (`questions/_jjk_page_<slug>.json`, page-gen
2026-08-24, 0 hand-authored, 0 retired), carrying:

- `page-gen:identity` ×4 — kanji, romaji, manga debut chapter, anime debut
  episode.
- `page-gen:battle` ×5 per battle the technique appears in (outcome / where /
  when / chapter / arc): 0–234 per page (*cursed energy* 230, *boogie woogie*
  234, *domain expansion* 134, *black flash* 32, *binding vow* 10,
  *heavenly restriction* 0). Answers are sourced from the **battle pages**
  (`extra_sources`) — the technique-side mirror of the battles' `powers1/2`
  lists. **G23/R6-181 guard: never author battle-outcome or battle-listing
  prose on the technique page; a miss on one of these is diagnosed on the
  battle page** (the battle wave verified those same questions at 100%).
- `page-gen:battles` ×1 — roster "Every battle involving X".
- `page-gen:techniques` ("Every named technique of X") fires on **7 of 149**
  technique pages: *Copy, Eight-Handled Sword Divergent Sila Divine General
  Mahoraga, Idle Death Gamble, Jujutsu, Maximum: Uzumaki, Merged Beast Agito,
  Round Deer*. These pages' `user`/ability edges name other techniques (Copy →
  Yuji Itadori's 8-technique set; Jujutsu → [Binding Vow]; Maximum: Uzumaki →
  [Idle Transfiguration]), so page-gen declared a **closed roster** in
  `overrides.yaml` plus a roster question. **On those 7 pages the prose
  entries are additive: never author a question that re-asks the closed set of
  named techniques** — that answer belongs to the roster. *Jujutsu* has no
  Related Techniques section (it carries History + Glossary instead); its
  Glossary/History entries are fine as long as they don't re-ask the roster.
  The other 142 pages carry no such roster — the prose pass owns them
  outright. (Census correction, 2026-09-02: the first draft said "never
  fires" after checking only the `abilities` fallback table and six batches
  that happened to miss all seven.)

**Display-form gold rule (learned on Episode 1, applies here too):** where a
section renders a wikilink's display text rather than the target title, author
the gold item from the display text the page actually shows.

## Special cases

- **8 sparse pages** (L2 prose < 400 ch): *Batto Sword Drawing, Hazy Moon,
  Kappa Rokujushi, Miracle Cannon, Piercing Blood, Slicing Exorcism,
  Ultra Shield, Ultra Spin*. Expect 2–4 entries (lead + whatever exists). Do
  not fabricate prose to fill the gap.
- **9 titles contain colons** (*Cursed Technique Lapse: Blue*, *Divine Dog:
  Totality*, *Maximum: Meteor/Uzumaki/Wing King*, *Mode: Albatross*,
  *Hollow Technique: Purple*, *Otherworld Between Darkness and Light: Reverse
  Transcendence* …) — the batch slug replaces the colon with `_`; the wikitext
  filename does the same. Look both up by slug, never by title.
- **Counterfactuals** ("What would happen if the binding vow were broken?")
  route to `qa` — but the answer must still be verbatim on the page; if the
  page states no hypothetical outcome, RETIRE with the standard "not stated on
  the page" reason.

## Batch shape and loop

- Batches exist; prose is appended with `add_prose.py` (verbatim gate:
  `find_exact` + TRANSLATE normalization; `kind "fact"`, `expect_mode "qa"`,
  no `scope`, `note "prose: <Section>"`, single Fandom source, `verified` =
  authored date).
- Per-page FAST loop (same as the other waves): `dump_prose.py` → author
  verbatim triples → bulk-add → `page-run --batch <slug>` → faithful triage
  (diagnose the gap; never rephrase the question to dodge it).
- The first `page-run` of a technique batch also verifies its structured half
  (up to ~235 battle questions). Those answers live on battle pages the battle
  wave already verified 100% — a miss there is a battle-page gap, fixed on the
  battle page, never by editing the technique question.
- R5 volume additions, per page: at least one yes/no, one comparative, one
  counterfactual against the page's own facts; authoring lint before
  `page-run` (reject answers contained in the question, reject leading
  wh-words, require numeric answers to "how many").
- Server: G24 build (PID 29104) is current; no engine code change is expected
  in the wave — no restart unless a triage gap forces one.

## Ordering

1. **Wave 1 = the five heaviest pages** (by prose volume): *Kogane,
   Boogie Woogie, Malevolent Shrine, Cursed Energy, Jujutsu* — shakes out
   chunking gaps (huge Usage bodies, one-off L2s) before the long tail.
2. Then **alphabetical slug order**, waves of 5 pages per checkpoint
   (checkpoint only on a new engine finding, per standing rule).
3. The 8 sparse pages ride along in alphabetical order; expect them to be
   short.

## Numbers to expect

| page class | count | entries/page (typical) |
|---|---:|---|
| heavy (Usage ≥ 4 KB or related/one-off sections) | ~15 | 12–20 |
| typical (lead + Description + Usage ± Trivia) | ~120 | 6–12 |
| sparse (L2 prose < 400 ch) | 8 | 2–4 |

Rough total: **~1,200–1,700 prose entries** for the wave (ceiling estimate
1,745), on top of the ~3,400 structured questions the batches already carry.