# Receipt: census v2 authoring (census_dimensions_csm_v2.json)

Authoring subagent, 2026-09-10. Task: widen the CSM dimension census from
character pages only to all five remaining narrative page types.

## What was authored

- `reports/csm/census_dimensions_csm_v2.json` — the existing 60 items copied
  VERBATIM (byte-identical blocks verified) + 50 new items (10 per new class)
  + a `meta.widened` block. No other file was modified.
- This receipt.

Constraints honored: `series/csm/facts.db` opened read-only (`file:...?mode=ro`),
no census run or graded, no ML model loaded, no server started, all commands
< 15 s via `scriptengine/.venv/bin/python`.

## Top-level shape decision

`census_dimensions_csm.json` top level is a **dict** with keys `meta` +
`items` (60). Decision (per task rule for the dict case): keep both top-level
keys, extend `items` 60 → 110 (existing 60 first, unchanged), and add the new
meta block as `meta.widened` without touching any existing meta key (all 7
original keys preserved with identical values). Serialization matches the
original file's format exactly (`json.dumps(..., indent=1)`, no trailing
newline — proven by byte-round-trip of the original before writing), so the
60 carried items round-trip byte-identically; confirmed by extracting all 60
item blocks from the old file and verifying each is a verbatim substring of v2
(0 missing).

## Item shape and id convention

Existing items: `id` / `class` / `subject` / `q` / `expect[3]` / `source`;
ids follow `csm-dim-<abbr>-NN` (`arcn`, `state`, `abl`, `pers`, `appr`,
`caus`). New items mirror the shape exactly (verified: all 110 items have the
same key set) with source `{"page": <title>, "table": "facts"}`. New id
abbreviations: `chap` (chapter_box), `epis` (episode), `volu` (volume_box),
`sarcs` (story_arcs_box), `org` (organization).

## Per-class item counts

| class | v1 | v2 new | v2 total |
|---|---|---|---|
| arc-narrative | 10 | – | 10 |
| state-over-time | 10 | – | 10 |
| abilities | 10 | – | 10 |
| personality | 10 | – | 10 |
| appearance | 10 | – | 10 |
| causality | 10 | – | 10 |
| chapter_box | – | 10 | 10 |
| episode | – | 10 | 10 |
| volume_box | – | 10 | 10 |
| story_arcs_box | – | 10 | 10 |
| organization | – | 10 | 10 |
| **total** | **60** | **50** | **110** |

Subjects chosen for spread across the corpus: chapters 1/25/53/60/84/100/150/
191/232; episodes 1–12 (10 of 12); volumes 1/2/5/10/13/17/20/22/24 + the novel
`Chainsaw Man: Buddy Stories`; all 14 arcs (10 chosen, favoring span facts);
10 of 11 organizations (all except `Establishment`-type page; the 10 cover the
full notable-members/allegiance/debut fact shape).

## Page-type denominators (verified read-only)

`select page_type, count(*) from documents group by page_type` on
`series/csm/facts.db` returned exactly the task-expected counts:

- chapter_box **232** ✓
- episode **12** ✓
- volume_box **26** ✓
- story_arcs_box **14** ✓
- organization **11** ✓

(Also on disk: character 175, character_history 22, music 20, unknown 14,
blu_ray_dvd 4, establishment 3, anime 2, saga_box 2; total 537 documents.)

## Expect verification — exact query and row counts

Every one of the 150 new expect occurrences (127 unique terms) was verified
VERBATIM by this single read-only query per term (exact match, no LIKE):

```sql
select
  (select count(*) from facts where value = ?)
+ (select count(*) from relations where other = ?)
+ (select count(*) from nodes where name = ?)
+ (select count(*) from aliases where alias = ?)
+ (select count(*) from sections where title = ?)
+ (select count(*) from relations where era = ?);
```

**Result: 127/127 unique terms count ≥ 1, 0 failures** (the build script
refused to write v2 on any zero — it passed on the first attempt). Row counts
per unique term, grouped by class:

### chapter_box (26 unique)
| term | count |
|---|---|
| Dog & Chainsaw | 3 |
| Intro arc | 12 |
| Episode 1 | 13 |
| Ghost, Snake, Chainsaw | 1 |
| Katana Man arc | 101 |
| Gōsuto Hebi Chensō | 1 |
| In a Dream | 2 |
| International Assassins arc | 139 |
| January 3, 2020 | 1 |
| Quanxi and the Fiends' 49-Person Massacre | 1 |
| Issue 2020-14 | 1 |
| Hero of Hell | 1 |
| Control Devil arc | 66 |
| September 13, 2020 | 1 |
| How to Walk Shoeless | 1 |
| Justice Devil arc | 58 |
| July 27, 2022 | 1 |
| Dream's Next Stage | 1 |
| Chainsaw Man Church arc | 75 |
| December 6, 2023 | 1 |
| Cuz I'm a Devil | 1 |
| War Devil arc | 105 |
| January 29, 2025 | 1 |
| Thank You, Chainsaw Man | 1 |
| March 25, 2026 | 1 |
| Episode 8 Episode 9 | 1 |
| June 10, 2019 | 1 |

### episode (24 unique; Katana Man arc / Eternity Devil arc / Bat Devil arc / Introduction arc shared with chapter_box)
| term | count |
|---|---|
| Introduction arc | 12 |
| Kick Back | 16 |
| Arrival in Tokyo | 2 |
| Chapter 2 (p.2-4, 19-25), 3, 4, 5 (p.1-10) | 1 |
| Bat Devil arc | 53 |
| Meowy's Whereabouts | 2 |
| Hawatari Nioku Centi | 5 |
| Gun Devil | 8 |
| Eternity Devil arc | 51 |
| In The Back Room | 6 |
| Kill Denji | 3 |
| Chapter 15 (p.11-21), 16, 17, 18 (p.1-12) | 1 |
| Denji o Korose | 3 |
| Gunfire | 2 |
| First Death | 5 |
| From Kyoto | 2 |
| Deep Down | 5 |
| Bruised & Battered | 2 |
| Dogland | 5 |
| Mission Start | 2 |
| Chapter 31 (p.19), 32, 33, 34, 35 (p.1-6) | 1 |
| Katana vs. Chainsaw | 2 |
| Chainsaw Man – The Movie: Reze Arc | 29 |
| Fight Song | 6 |

### volume_box (27 unique)
| term | count |
|---|---|
| Denji | 117 |
| March 4, 2019 | 2 |
| Chainsaw vs. Bat | 2 |
| Power | 39 |
| May 2, 2019 | 1 |
| Minor | 2 |
| Denji Katana Man | 1 |
| January 4, 2020 | 1 |
| A Dog's Feelings | 2 |
| Makima | 68 |
| April 5, 2022 | 1 |
| Spoiler | 2 |
| Yuko | 16 |
| December 5, 2023 | 1 |
| Guns, Nails, Katana | 2 |
| Hirofumi Yoshida | 29 |
| January 7, 2025 | 1 |
| Two Children | 2 |
| Asa Mitaka | 40 |
| March 3, 2026 | 1 |
| Enjoy Your Food | 2 |
| Asa Mitaka Yoru | 1 |
| October 13, 2026 | 1 |
| Ultimate Armor | 2 |
| June 4, 2026 | 1 |
| Chainsaw Man: Buddy Stories | 2 |
| July 25, 2023 | 1 |
| Denji Power | 1 |

### story_arcs_box (18 unique; the 6 arc-name terms are shared with chapter_box/episode rows above)
| term | count |
|---|---|
| Public Safety Saga | 178 |
| Academy Saga | 227 |
| Chapter 1 - 4 | 1 |
| Episode 1 - 2 | 1 |
| Chapter 5 - 13 | 1 |
| Episode 2 - 5 | 1 |
| Chapter 14 - 22 | 1 |
| Episode 5 - 7 | 1 |
| Chapter 23 - 38 | 1 |
| Episode 8 - 12 | 1 |
| Chapter 39 - 52 | 1 |
| Bomb Girl arc | 79 |
| Chapter 71 - 79 | 1 |
| Gun Devil arc | 38 |
| Chapter 80 - 97 | 1 |
| Chapter 98 - 111 | 1 |
| Chapter 121 - 131 | 1 |
| Chapter 191 - 232 | 1 |

### organization (29 unique)
| term | count |
|---|---|
| Himeno Denji Aki Hayakawa Power | 1 |
| Public Safety Devil Hunters | 10 |
| Chapter 5 (mentioned) | 1 |
| Makima Katana Man Reze Quanxi Barem Bridge Miri Sugo | 1 |
| Public Safety Devil Hunters Makima (formerly) | 1 |
| Chapter 86 | 8 |
| Control Devil War Devil Famine Devil Death Devil | 1 |
| Devils Weapon Devils (formerly) Themselves | 1 |
| Four Horsemen | 1 |
| United States of America | 2 |
| Aldo Joey Unnamed Brother | 1 |
| American Thugs | 1 |
| Criminal | 1 |
| Chapter 1 | 11 |
| Yakuza | 4 |
| Katana Devil Bomb Devil Bow Devil | 1 |
| Specific group of weapon-based Devils that worked under the Four Horsemen | 1 |
| Weapon Devils | 2 |
| Asa Mitaka Yoru Fami Hirofumi Yoshida Haruka Iseumi | 1 |
| High School Club | 1 |
| Chapter 99 | 5 |
| China | 8 |
| Quanxi Pingtsi † Long † Cosmo † Tsugihagi † | 1 |
| Chapter 54 | 11 |
| Kishibe Hell Devil | 1 |
| Chapter 83 | 7 |
| Anti-Makima Squad | 2 |
| Fake Chainsaw Man | 5 |
| Death Devil | 20 |

Note on arc-name case: some arcs store `name` with capital "Arc" (e.g.
`Bat Devil Arc`); where the expected term uses the page's canonical lowercase
form (`Bat Devil arc`), it verifies via `nodes.name` (the story_arcs_box page
node) and/or `relations.era`, both exact matches — no LIKE was needed anywhere.

## Swapped questions for grounding

**None.** Every planned question's expect terms grounded verbatim on the first
verification pass; no item was replaced. (Design note: all 50 questions target
infobox facts / node names / aliases / sections / era values that exist in the
store; multi-line fact values were never used as expect terms, and the one
zero-width-space value in the store — Episode 6's ending song `Rendezvous​` —
was deliberately avoided in favor of its romaji `Denji o Korose`.)

## v2 meta block added

`meta.widened` records: added date (2026-09-10), the note that the existing
60-item census covers character pages only, the five page-type denominators
(as verified above), the verification SQL provenance, and the
150-occurrences/127-unique verbatim-verification record. All 7 original meta
keys untouched.