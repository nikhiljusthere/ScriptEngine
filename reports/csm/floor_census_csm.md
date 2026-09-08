# CSM D5 floor census — the 775 excluded sub-6-word lines (2026-09-08, CSM-3b)

Council COUNCIL_csm-3 Ruling 5b: the <6-word floor's exclusion must be
receipted with a section histogram, because "all chapter/volume-list rows"
is loose — the census includes Summary and poll rows. This is the durable
receipt; the decision itself lives in `series/csm/overrides.yaml`
(D5 floor decision, ruling 4b — decide *before* panel pinning).

**Numbers (current tree, `series/csm/facts.db`, regenerated 2026-09-08):**

- 775 sub-6-word lines in non-boilerplate sections, **all tier-0-eligible**
  (each sits whole inside a chunk), all excluded from the pinned panel.
- The panel holds **17,381 unique rows** (17,181 sweep + 200 held-out);
  **17,382** is the tier-0 *occurrence* count — one line duplicates inside
  its section (COUNCIL_csm-3 clash 5, chair re-derived).
- Word-length distribution of the 775: 1-word 110 · 2-word 73 · 3-word 146
  · 4-word 211 · 5-word 235.

**Section histogram (top):**

| lines | section |
|---:|---|
| 133 | Manga Chapters |
| 114 | Chapters |
| 46 | Part 2 – Academy Saga / War Devil arc |
| 44 | Summary |
| 41 | 3rd Popularity Poll |
| 37 | Part 2 – Academy Saga / Aging Devil arc |
| 29 | 1st Popularity Poll |
| 29 | 2nd Popularity Poll |
| 23 | Part 2 – Academy Saga / Chainsaw Man Church arc |
| 22 | Characters |
| 18 | Anime Episodes |
| 16 | Part 1 – Public Safety Saga / Katana Man arc |
| 14 | Part 1 – Public Safety Saga / Control Devil arc |
| 12 | Part 2 – Academy Saga / Justice Devil arc |
| 12 | Part 2 – Academy Saga / Falling Devil arc |
| 11 | Trivia (+ seven arc list sections at 10–11 each) |
| … | a long tail of 1–10 rows across arc/synopsis/poll sub-lists |

Shape of the exclusion: list-shaped rows (chapter/volume/episode lists, arc
lists, poll rankings) plus 44 Summary rows and 99 poll rows — rows like
"College Fund 158.", "156.", "Aging's World 181.". They carry too little
signal to query with; their misses would be ranking noise, not
reachability defects (ruling 4b: *record the exclusion, not include it*).

The floor is a dial, not a wall: `build_panel(min_words=…)` re-includes any
sub-floor lines on re-pin with zero code; the panel metadata stamps the
floor it was pinned at.