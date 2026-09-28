# MCU bug-B re-resolution receipt (2026-09-28)

Commit piece: **bug B — exact title wins; hubs/disambiguation pages are
never participants; genuine ambiguities stay counted.**

## What the commit carries

- `scriptengine/ingest/events.py` (the bug-B hunks):
  `participant_candidates` builds exclusion-aware pools (the wiki's
  `participant_excludes` + disambiguation pages never enter a pool);
  `pick_candidate`: an exact title match wins over the wiki's variant
  forms, and a variant is a candidate only where the passage points at
  it (the page links to it, or the passage's own page is that variant) —
  a pool of unpointed variants alone resolves to nothing;
  `_is_variant_of` is case-insensitive; the live-path probe passes the
  page signals correctly; `re_resolve_participants` re-files under the
  exclusion-aware pools and re-points rows filed on excluded pages under
  the prefix-stripped name.
- `tests/test_events_link_resolution.py`, `tests/test_events_reality_config.py`
  (signature + rule pins, incl. the `link_broken` expectation under the
  new shape rule).
- The `participant_excludes` declaration itself committed with the
  overrides piece; this receipt records the store run.

## Store run (series/mcu/facts.db, untracked)

Final `re_resolve_participants` over the repaired store. Tally:
`moved=8,209` row-level re-points (incl. no-op re-affirmations of
already-correct rows), `link_broken=6` rows resolved by the exactly-one-
linked-member rule, `ambiguous_new=2` rows re-filed as counted
ambiguities, `unresolved_kept=35` name-pairs kept as filed (findings),
`merged=0`. Cross-check: the same run over a copy of the pre-run backup
reproduces the live ambiguous set exactly (62/62).

## Before → after

Before = the pre-repair store (the 23:13 backup, after the row-timeline
backfill); after = the live store after the 231-row pilot repair plus
this final `re_resolve_participants` run.

| | before | after (live) |
|---|---|---|
| rows | 6,339 | 6,326 (−13 duplicate rows) |
| placed (`arc_index`) | 6,110 | 6,097 |
| rows with a participant node on a `Hub:` page | 192 (128+108 sides) | 34 (27+18 sides, 11 rows both sides) |
| rows whose participant *name text* starts `Hub:` | 204 (250 sides) | 46 (59 sides = 45 node-hub + 14 NULL-node ambiguous rows) |
| stored-ambiguous rows | 60 | 62 (76 list sides) |

### The 62 ambiguous rows, class of each remaining list (the 62 report)

9 docs, 62 rows, 76 list sides. Under block 2's own rule (exactly one
listed member linked from the page = the wiki's answer):

| doc | rows | no-linked-member | several-linked-members | stale `Hub:` text |
|---|---|---|---|---|
| Assassination of Daniel Sousa | 1 | 0 | 1 | 0 |
| Attack on Arête Laboratories | 8 | 6 | 2 | 2 |
| Avengers: Infinity War | 12 | 11 | 1 | 4 |
| Battle of New York/Earth-828 | 1 | 1 | 0 | 0 |
| Captain America: The Winter Soldier - The Official Game | 10 | 10 | 0 | 1 |
| Daredevil: Born Again/Season One | 6 | 6 | 0 | 1 |
| Infinity War | 15 | 15 | 0 | 0 |
| Scars (Agents of S.H.I.E.L.D.) | 12 | 12 | 0 | 0 |
| Snap | 11 | 1 | 10 | 10 |
| **total** | **62 (76 sides)** | **62** | **14** | **18** |

- **no-linked-member (62 sides)**: the page links to *none* of the listed
  candidates — genuine ambiguity, kept counted by design (e.g.
  `Project Insight | Rocket Raccoon | Rocket/Good Samaritan Rocket |
  Rocket/Party Prince Thor` on *Infinity War*).
- **several-linked-members (14 sides)**: the page links to *several*
  listed candidates — the wiki itself never chose (e.g. *Snap*'s
  `Hub:Thanos | Thanos | Thanos/Age of Ultron | …`: 10 sides; the page
  links to many Thanos variants at once). Kept counted by design.
- **exactly-one**: 0 remaining — every such list the run could reach was
  re-pointed (`link_broken=6` rows).
- **stale `Hub:` text (18 sides)**: pilot-era list text still advertises
  the excluded `Hub:` candidate. Harmless — hubs are out of the
  exclusion-aware pools and can never be a hit — and rewritten with
  exclusion-aware text on the next `--force` re-extraction.

### The 46 remaining hub-name rows (59 sides; 34 carry a `Hub:` node)

Kept-as-filed findings, not silent mis-resolutions — the contract
"hubs are never participants" holds for every candidate set: **zero
remaining side has an exact bare page, or a pointed-at candidate, under
the stripped name** (a `pick_candidate` escape flag; both are 0). The
46 rows split into 34 rows whose participant *node* is a `Hub:` page
(45 sides) and 12 NULL-node stored-ambiguous rows whose list text still
advertises a `Hub:` member (14 sides).

Class of each of the 59 remaining sides under the resolver's own rules:

| class | sides | what it means |
|---|---|---|
| UNPOINTED (variant-only pool, page points at no member) | 22 | e.g. `Hub:Tafari` / `Hub:Kuda` / `Hub:Vanessa Fisk` on the Kudu-Tafari / Fogwell's Gym / Adam-murder docs: only variant subpages exist (`Tafari/Horde-Infested Earth`, …) and the page links none of them → `pick_candidate` returns None by the variant pointing rule |
| NO-NODE (no wiki node under the stripped name) | 37 | e.g. `Hub:Achilles` (Attack/Duel of Troy), `Hub:Ben Grimm` (Battle of New York/Earth-828): no bare page, no variants in the store → a finding, kept as filed |

- 11 of the 34 node-hub rows file both participants on hubs.
- The 14 NULL-node sides sit inside the 62 ambiguous rows above (their
  list text carries the stale `Hub:` member; 18 stale-hub-text sides
  overall, the rest on non-NULL-node rows).

Full per-row detail: `/tmp/se_p2/bug_b_lists.json` (list + rule class +
hub-row pool for every remaining side).

## Tests

`tests/test_events_link_resolution.py` + `tests/test_events_reality_config.py`
green; full suite at commit time `4 failed, 1,419 passed, 2 xpassed` (the 4
= known environmental set).