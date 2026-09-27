# GATE C evidence — `unknown`-type residue report
_generated 2026-09-27 by `tools/marvel/unknown_residue.py` (zero egress; read-only facts.db; writes this receipt only)._ 

**What the class is.** `page_type='unknown'` = the builder mapped no archetype for the page (its infobox template is absent or unmapped). The document stays in the store — indexed, chunked, queryable — only its archetype label is the generic `unknown`. Recorded residue, never a silent drop.

## marvel: 529/236720 (0.223%)

- infobox-template distribution among the unknowns: {'<none>': 528, 'Infobox Episode': 1}
- named edges (a known template that still fell through the mapping — each bounded and listed, never aggregated away): `Marvel's Spidey and His Amazing Friends Season 4 39`
- sample: `2001 Comic Books`, `20th Century Studios`, `A Gazetteer of the Hyborian Age`, `A Year of Marvels`, `A-Force Comic Books`, `Abomination Comic Books`, `Adam Warlock Comic Books`, `After Daak`, `Age of Apocalypse Comic Books`, `Agents of Atlas Comic Books`, `Alien Comic Books`, `Alien Legion Comic Books`, `Alpha Flight Comic Books`, `Amadeus Cho Comic Books`, `Amalgam Comics (Trading Cards)`
- cause: pages with no infobox — a corpus shape, not a parser gap; the detail rule keeps them as `unknown` facts instead of inventing an archetype (`Comic Books` collection aggregates, studios, hubs).

## mcu: 616/35234 (1.748%)

- infobox-template distribution among the unknowns: {'<none>': 616}
- sample: `1900s`, `1910s`, `1920s`, `1930s`, `1940s`, `1950s`, `1960s`, `1970s`, `1980s`, `1990s`, `2000s`, `2010`, `2011`, `2012`, `2013`
- cause: pages with no infobox — a corpus shape, not a parser gap; the detail rule keeps them as `unknown` facts instead of inventing an archetype (decade/year pages, studios, production hubs).

## Drift vs the recorded baseline

- G6-final / D3-recorded baseline: marvel 529, mcu 616
- last receipt on disk: marvel 529, mcu 616
- live counts agree with the baseline — no drift.
