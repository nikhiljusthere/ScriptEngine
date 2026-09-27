# D2 — archetype depth floors (2026-09-27 gate day)

Measured against *populated in-scope sections* (the sections the series' chunker actually indexes) plus the infobox fact channel. Never raw page count (Plan_to_perfection §6, D2).

Declared floor (pre-registered, uniform): >= 50% of an archetype's pages deep (>= 1 populated channel) AND median infobox-fact count >= 1.

## marvel

| archetype | page_types | docs | prose% | facts% | deep% | med_facts | med_prose | channel | floor |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| character | character | 99591 | 5.8% | 100.0% | 100.0% | 15 | 0 | infobox-led | PASS |
| comic | comic | 71274 | 4.6% | 100.0% | 100.0% | 21.0 | 0.0 | infobox-led | PASS |
| event | event | 384 | 58.6% | 100.0% | 100.0% | 12.0 | 1.0 | infobox-led | PASS |
| film | film | 297 | 38.7% | 99.7% | 100.0% | 14 | 0 | infobox-led | PASS |
| series | series | 215 | 27.9% | 100.0% | 100.0% | 16 | 0 | infobox-led | PASS |
| episode | episode | 3986 | 1.0% | 100.0% | 100.0% | 10.0 | 0.0 | infobox-led | PASS |
| location | location | 10281 | 14.9% | 100.0% | 100.0% | 13 | 0 | infobox-led | PASS |

## mcu

| archetype | page_types | docs | prose% | facts% | deep% | med_facts | med_prose | channel | floor |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| character | character | 4804 | 100.0% | 100.0% | 100.0% | 7.0 | 4.0 | prose+infobox | PASS |
| comic | comic | 102 | 100.0% | 100.0% | 100.0% | 7.0 | 10.0 | prose+infobox | PASS |
| event | event | 454 | 100.0% | 100.0% | 100.0% | 9.0 | 3.0 | prose+infobox | PASS |
| film | movie | 52 | 100.0% | 100.0% | 100.0% | 10.0 | 16.0 | prose+infobox | PASS |
| series | tv_series,season | 106 | 100.0% | 100.0% | 100.0% | 5.0 | 6.0 | prose+infobox | PASS |
| episode | episode | 660 | 100.0% | 100.0% | 100.0% | 9.0 | 15.0 | prose+infobox | PASS |
| location | location | 1931 | 100.0% | 100.0% | 100.0% | 4 | 2 | prose+infobox | PASS |

## Finding (recorded, not hidden)
- **marvel is infobox-led** for character/comic/episode: the bulk of those pages are pure-infobox data pages (a 25-page sample of word_count=0 character pages had zero `==` headings on disk 2026-09-27 -- the parser dropped nothing; the wiki stores those characters as data, not narrative). Their depth is carried by infobox identity/affiliation/alias facts (median 10-21 keys/page) -- the C1 identity path and the C6 identity/affiliation/alias bank classes. Marvel character QA is therefore infobox-led by corpus fact, not a parser gap.
- **mcu is prose-led**: ~100% of pages carry narrative sections (median depth 2-16) in addition to the infobox.

Overall: ALL ARCHETYPES MEET THEIR FLOOR
