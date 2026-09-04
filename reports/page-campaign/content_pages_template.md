# JJK content-pages campaign — section census & authoring template

> Authoring plan for the 53 in-scope content pages (item, location, occupation,
> organizations, simple_box, species + `Jujutsu Regulations`). Source:
> `series/jjk/facts.db` (`documents` x `sections`), census snapshot 2026-09-04.
> Companion to `COVERAGE.md` (the live done/remaining tracker): this file is the
> **what to author**; `COVERAGE.md` is regenerated after every batch commit.

## Scope

53 pages, 6 content page types + 1 `unknown` page (`Jujutsu Regulations`). All are
currently **0% covered** (no committed base batch). Media / nav / release types
(volume, blu_ray_dvd, music, game, series, anime, novel, stage_play) and the
remaining `unknown` list/author/promo pages are **out of scope** (see COVERAGE.md).

**In-scope prose sections** = every section that carries prose, **excluding the two
boilerplate sections present on every page**: `References` (always empty) and
`Navigation` (the interwiki-link box). Section names below show their breadcrumb
path (e.g. `Usage > Suguru Geto` is the L3 under `Usage`). The `lead` (prose before
the first `##` heading) is a separate carrier; on thin content pages it often holds
most of the text, so a large `lead` column means more groundable prose than the
section count alone suggests.

## Section-reader verification (4 thinnest pages)

Confirmed the prose is present, readable, and carries inline `(Chapter N, Episode M)`
citations the `sourced:` resolver reads (numbers looked up, never inferred):

- **Fly Heads** (114w) — lead 16w + `Description` 95w. Groundable.
- **Renchoku Girls' Junior High** (140w) — lead 23w + `Description` 25w + `History` 89w.
  (`Faculty, Students, and Alumni` is a 1w empty table → skip.)
- **Hiten** (149w) — lead 24w + `Description` 22w + `Usage` 50w + `Trivia` 51w.
- **Q** (196w) — lead 27w + `History > Gojo's Past Arc` 166w. `Known Members` 0w → skip.

Reader holds on every thin page: no page is empty. Two rules for the authoring pass:
1. An L2 shell can be empty while its **L3 child carries the prose** (Q → `History
   > Gojo's Past Arc`); read L3 sections and attribute them to their parent.
2. Skip empty / boilerplate sections (0w, or a bare table) — there is nothing to
   ground a verbatim fact-like entry in.

## Census (53 pages · 246 prose sections · ~382 questions at 1.5/section)

### item (20 pages)

| page | wc | lead | in-scope sections (breadcrumb) | est Q |
|---|---:|---:|---|---:|
| Black Rope | 443 | 33 | Description, Usage, Trivia | 5 |
| Chain of a Thousand Miles | 316 | 45 | Description, Usage | 3 |
| Cursed Corpse | 853 | 39 | Description, Usage, List of Cursed Corpses | 5 |
| Cursed Tool | 1410 | 20 | Description, List of Cursed Tools | 3 |
| Cursed Womb: Death Painting | 809 | 36 | History, Description, Known Death Paintings, Trivia | 6 |
| Dragon-Bone | 383 | 28 | Description, Usage | 3 |
| Festering Life Sword | 408 | 18 | Description, Usage | 3 |
| Hiten | 149 | 24 | Description, Usage, Trivia | 5 |
| Honoyagi | 232 | 11 | Description, Usage, Trivia | 5 |
| Inverted Spear of Heaven | 644 | 19 | Description, Usage, Trivia | 5 |
| Kamutoke | 412 | 41 | Description, Usage, Trivia | 5 |
| Mode: Absolute | 866 | 25 | Description, Usage, Related Techniques | 5 |
| Playful Cloud | 699 | 16 | Description, Usage, Usage > Suguru Geto, Usage > Maki Zenin & Megumi Fushiguro, Usage > Aoi Todo, Usage > Toji Fushiguro | 9 |
| Prison Realm | 747 | 26 | Description, Description > Back Gate, Usage | 5 |
| Ryomen Sukuna's Fingers | 1788 | 43 | Description, History, History > Fearsome Womb Arc, History > Vs. Mahito Arc, History > Kyoto Goodwill Event Arc, History > Death Painting Arc, History > Shibuya Incident Arc, History > Shinjuku Showdown Arc, Trivia | 14 |
| Slaughter Demon | 267 | 28 | Description, Usage | 3 |
| Split Soul Katana | 688 | 69 | Description, Usage > Toji Fushiguro, Usage > Maki Zenin, Usage > Tsurugi Okkotsu | 6 |
| Sword of Extermination | 316 | 44 | Description, Usage, Trivia | 5 |
| Talisman | 431 | 59 | Usage | 2 |
| Ultimate Mechamaru | 638 | 49 | Description, Usage, Related Techniques | 5 |

*20 pages · 64 prose sections · ~102 questions*

### location (14 pages)

| page | wc | lead | in-scope sections (breadcrumb) | est Q |
|---|---:|---:|---|---:|
| Culling Game/Colonies | 806 | 46 | Description, History, Landmarks, Landmarks > Tokyo No. 1 Colony, Landmarks > Tokyo No. 2 Colony, Landmarks > Sendai Colony, Landmarks > Sakurajima Colony, Landmarks > Lake Gosho Colony | 12 |
| Gachinko Fight Club | 1275 | 34 | Description, Members, History > Culling Game Arc, Fights | 6 |
| Kawasaki City | 564 | 27 | Description, Synopsis > Vs. Mahito Arc, Landmarks > Kinema Cinema, Landmarks > Satozakura High School, Landmarks > Mahito's Underground Lair, Landmarks > Tokyo Municipal Shūei High School Detached Office, Inhabitants | 11 |
| Kyoto Metropolitan Curse Technical College | 202 | 47 | Description, Description > Location, School Traditions, Staff & Students, Trivia | 8 |
| Okinawa | 224 | 20 | Description, History > Gojo's Past Arc, Landmarks > Naha Airport | 5 |
| Renchoku Girls' Junior High | 140 | 23 | Description, History, Faculty, Students, and Alumni | 5 |
| Saitama Urami East Junior High | 138 | 26 | Description, Faculty, Students, and Alumni | 3 |
| Sendai City | 490 | 30 | Description, History > Fearsome Womb Arc, History > Culling Game Arc, Landmarks > Sugisawa Municipal High School #3, Landmarks > Sugisawa Hospital | 8 |
| Shibuya | 1721 | 31 | Description, History, Landmarks > Bunkamura Way, Dogenzaka, Landmarks > Aoyama Cemetery, Harajuku, Landmarks > Shibuya C Tower, Landmarks > Metropolitan Expressway, Route No. 3: Shibuya Line, Landmarks > Shoto Bunkamura Street, Landmarks > Dogenzaka Alley, Landmarks > Commercial District | 14 |
| Shibuya/Tokyo Metro | 1490 | 45 | Description, Landmarks > Shibuya Station, Landmarks > Jr. Shibuya Station, Landmarks > Hikarie Building, Landmarks > Fukutoshin Line Platform, Landmarks > Meiji-Jingumae Station, Landmarks > Bunkamura Station, Trivia | 12 |
| Shinjuku | 293 | 31 | Description, History > Gojo's Past Arc, History > Cursed Child Arc, History > Shinjuku Showdown Arc | 6 |
| Simuria | 1100 | 20 | Description, Species, Resources, Tribes > Rumel, Tribes > Deskunte, History, Abilities and Powers, List of Simurians | 12 |
| Tokyo Metropolitan Curse Technical College | 1682 | 53 | Description, Description > Location, Description > Administration, Description > Rules and Security, Curriculum, Uniforms, School Events, Landmarks, Landmarks > Tombs of the Star, Staff & Students | 15 |
| Yasohachi Bridge | 358 | 44 | Description, History | 3 |

*14 pages · 78 prose sections · ~120 questions*

### occupation (2 pages)

| page | wc | lead | in-scope sections (breadcrumb) | est Q |
|---|---:|---:|---|---:|
| Assistant Manager | 216 | 20 | Overview, List of Assistant Managers, Trivia | 5 |
| Curse User | 661 | 47 | Overview, List of Curse Users | 3 |

*2 pages · 5 prose sections · ~8 questions*

### organizations (6 pages)

| page | wc | lead | in-scope sections (breadcrumb) | est Q |
|---|---:|---:|---|---:|
| Jujutsu Headquarters | 1304 | 79 | Overview, Overview > Conservative Faction, History > Cursed Child Arc, History > Fearsome Womb Arc, History > Shibuya Incident Arc, History > Culling Game Arc, History > Jujutsu Kaisen Modulo, Trivia | 12 |
| Jujutsu Sorcerer | 1608 | 88 | Overview > History, Overview > Biology, Overview > Profession, Overview > Stigma, Sorcerer Families, Ranks, Abilities and Powers, List of Jujutsu Sorcerers > Tokyo Jujutsu High, List of Jujutsu Sorcerers > Kyoto Jujutsu High, List of Jujutsu Sorcerers > Other Sorcerers | 15 |
| Q | 196 | 27 | History > Gojo's Past Arc | 2 |
| Sorcerer Clan | 2464 | 27 | Big Three Families, Sorcerer Clans, Sorcerer Clans > Zenin Clan, Sorcerer Clans > Zenin Clan > Members, Sorcerer Clans > Zenin Clan > Inherited Techniques, Sorcerer Clans > Gojo Clan, Sorcerer Clans > Gojo Clan > Members, Sorcerer Clans > Gojo Clan > Inherited Techniques, Sorcerer Clans > Kamo Clan, Sorcerer Clans > Kamo Clan > Members, Sorcerer Clans > Kamo Clan > Inherited Techniques, Sorcerer Clans > Inumaki Clan, Sorcerer Clans > Inumaki Clan > Members, Sorcerer Clans > Inumaki Clan > Inherited Techniques, Sorcerer Clans > Fujiwara Clan, Sorcerer Clans > Fujiwara Clan > Members, Sorcerer Clans > Abe Clan, Sorcerer Clans > Abe Clan > Members | 27 |
| Sorcerer Clan/Zenin Clan | 1438 | 66 | History, History > Culling Game Arc, Base of Operations, Members, Units > Hei, Units > Kukuru Unit, Units > Akashi, Trivia | 12 |
| Time Vessel Association | 693 | 39 | History, History > Gojo's Past Arc, Base of Operations, Known Members, Trivia | 8 |

*6 pages · 50 prose sections · ~76 questions*

### simple_box (5 pages)

| page | wc | lead | in-scope sections (breadcrumb) | est Q |
|---|---:|---:|---|---:|
| Bath | 278 | 42 | Description, Usage, Trivia | 5 |
| Cursed Human | 253 | 34 | Description | 2 |
| Cursed Object | 990 | 45 | Description, Incarnation, Incarnation > Incarnated Individuals, List of Cursed Objects | 6 |
| Cursed Womb | 392 | 29 | Description, Cursed Womb: Death Painting, List of Cursed Wombs, Trivia | 6 |
| Grade | 609 | 39 | Description, Description > Ranks, Description > Promotions, Grade Registry | 6 |

*5 pages · 16 prose sections · ~25 questions*

### species (5 pages)

| page | wc | lead | in-scope sections (breadcrumb) | est Q |
|---|---:|---:|---|---:|
| Cursed Spirit | 1610 | 57 | History, Description > Creation Process, Description > Characteristics, Description > Exorcism, Classifications > Vengeful Cursed Spirit, Classifications > Vengeful Cursed Spirit > Imaginary Vengeful Cursed Spirit, Classifications > Disease Cursed Spirit, Powers and Abilities, List of Cursed Spirits, See Also | 15 |
| Finger Bearer | 573 | 34 | Overview > Creation, Overview > Characteristics, Occurrences > Fearsome Womb Arc, Occurrences > Death Painting Arc | 6 |
| Fly Heads | 114 | 16 | Description | 2 |
| Kalyan | 587 | 42 | History, Description, Abilities and Powers, Trivia, See Also | 8 |
| Transfigured Human | 828 | 28 | Description, Usage | 3 |

*5 pages · 22 prose sections · ~34 questions*

### unknown (1 pages)

| page | wc | lead | in-scope sections (breadcrumb) | est Q |
|---|---:|---:|---|---:|
| Jujutsu Regulations | 724 | 88 | Memorandum Regarding Sorcerer Duties, Memorandum Regarding Sorcerer Duties > 1. Mission, Memorandum Regarding Sorcerer Duties > 2. Jujutsu Headquarters, Memorandum Regarding Sorcerer Duties > 3. Jujutsu High Schools, Memorandum Regarding Sorcerer Duties > 4. Sorcerer Ranks, Memorandum Regarding Sorcerer Duties > 5. Discipline, Memorandum Regarding Sorcerer Duties > 6. Retirement, Memorandum Regarding Sorcerer Duties > 7. Handling of Threats, Memorandum Regarding Sorcerer Duties > 8. Sensitive Information, Memorandum Regarding Sorcerer Duties > 9. Protection of Non-Sorcerers, Revisions | 17 |

*1 pages · 11 prose sections · ~17 questions*

**Total: 53 pages · 246 prose sections · ~382 questions** (a floor — large `lead`s add more once authored).

## Authoring pass (waves 2-6 model)

Author continuously per page type (item → location → occupation → organizations →
simple_box → species → `Jujutsu Regulations`); **do not stop on a failure**:

- Each in-scope section (and the `lead`) becomes sentence-level fact-like entries —
  a natural question with a **verbatim** answer grounded in that section's text; keep
  the inline `(Chapter N, Episode M)` citation so the `sourced:` tag resolves.
- Mandatory **3-phrasing probe** before any rephrase: if 2 of 3 phrasings pass and one
  stilted phrasing fails, it is an authoring issue (fix the question); if most fail, it is
  an engine gap — **leave it failing, never dodge by rephrase**, and file it to
  `reports/page-campaign/CONTENT_PAGES_TRIAGE.md` (G##).
- `scriptengine/` and `series/jjk/overrides.yaml` stay **execution-forbidden** during the
  campaign; engine fixes come back as one proposed-and-approved batch at the end.
- Commit per page type; run `tools/coverage_report.py` after each commit; run the gate
  triple (`eval jjk`, `canon-run opm`, `pytest`) once at the end.
