# CSM 8-failure root-cause investigation (2026-09-17)

Investigation only — no files edited. Method: live repro of all 8 questions
(`build_context` + `route`, `/tmp/opencode/repro8.py`), `facts.db` chunks/node
checks, and source reads. Every "root cause" below was observed in the live
repro, not inferred.

## Scoring contract (shared by all 8)

- `page_campaign.py:104` → `canon_gold.score_facts` @219-254: `ask` → haystack
  (`canon_gold.py:123-146` = context + beats + passages + facts +
  `_members` reading each member's `name`/`title`); `accept` defaults to
  `"all"` (`questions.py:98/200`) — every gold item must be present.
- Roster bundle: `context.py` `_roster_context` @248 renders declared
  members as `as_dict()` payloads into `members`, so declared member names do
  reach the haystack. The `"did not narrow"` warning
  (`roster.py:439-444`, `RosterResult.warning`, `self.unverified`) is
  informational metadata (qualifier words nothing could be checked against),
  never a member drop.

## Findings

| # | slug | kind | gold → found | root cause (observed) | class | minimal fix |
|---|------|------|--------------|------------------------|-------|-------------|
| 1 | death_devil | set | 4 → 3 | `Fourth East High School` rejected by the type rule: CSM page type `establishment` → `LOCATION` (`semantics.py:77`), `LOCATION ∈ NEVER_MEMBERS` (`:143`), set majority is organizations (`expected_type` `:425`), reject at `roster.py:4218-4219` (live: `"a location, and this is a set of organizations"`) | B | `semantic_types: {establishment: organization}` in `series/csm/overrides.yaml` |
| 2 | fami | set | 4 → 3 | same rule, same member | B | same |
| 3 | devil_hunter_club | fact | 5 → 4 (no Fami) | no org roster; `"Devil Hunters"` category roster (YAML `@254`, match `devil hunter` ⊂ `devil hunter club`) answers with 74 category members; Fami has no page in that category | B | new roster `Devil Hunter Club`, 5 explicit members |
| 4 | four_horsemen | fact | 4 → 2 (Famine, Death) | `Four Horsemen` roster (YAML `@273`) reads `category: Four Horsemen` → 6 docs (298/334/337/406/427/531); the wiki has no `Control Devil`/`War Devil` pages, so they can never be category members | B | add explicit `members:` to the existing entry (members beat category, `roster.py:3282`); the count roster `@184` already declares the same 4 |
| 5 | quanxi_and_the_fiends | fact | 5 → 4 (no Quanxi) | discovery category `Fiends` (`kind='category'`, subject `Quanxi`); the `quanxi` qualifier rejected 9 members (`"not quanxi"`); Quanxi is the page's subject, not a member of her own category | B | new roster `Quanxi and the Fiends`, 5 explicit members |
| 6 | tokyo_devil_detention_center | fact | 5 → 0 | `"Devils"` category roster (YAML `@250`, match `devil` ⊂ `Tokyo Devil Detention Center`) answers with 88 devils; zero overlap with the 5 gold employees | B | new roster `Tokyo Devil Detention Center`, 5 explicit members |
| 7 | tokyo_special_division_5 | fact | 6 → 0 | `"The Public Safety special divisions"` (YAML `@128`) hijacks: `_number_flexible` (`roster.py:148`) makes every word's `s` optional, so its phrase `special divisions` matches the query's singular `special division`; its 5 members are division *names*, not TSD5 personnel | B | new roster `Tokyo Special Division 5`, 6 explicit members |
| 8 | weapon_devils | fact | 3 → 0 | `Weapon Devils` roster (YAML `@219`) matches correctly, but its members are the 7 hybrid *pages*; the gold is the 3 devil names the wiki's infobox `members` field lists (`Katana Devil Bomb Devil Bow Devil`). The 0 is a data gap, not a router/parser defect | B | extend members with the 3 devil names (10 total) |

All eight are **class B** (per-series YAML data). No engine `.py` gap: the
engine did exactly what its data says. No four-gate re-run is triggered
(Ruling 5e — class-B content).

## Why the new/edited rosters win (selection mechanism)

- `roster.py:1399`: `declared = max((d for d in registry if d.matches(query)), key=matches)`
  — the **longest declared phrase wins**; the declared branch (`@1625`) is
  evaluated *before* category/type discovery (`_choose_set` `@1710`).
- `matched_phrase` `@269-276` regex-searches each declared phrase (via
  `_number_flexible`, `s?` on every word) in `" query "`; `matches` `@278-284`
  returns its length.
- Lengths that decide: `devil hunter club` (17) > `devil hunter` (12);
  `tokyo devil detention center` (28) > `devil` (5); `quanxi and the fiends`
(20) > `fiends` (6); `tokyo special division 5` (22) > `special divisions`
   (17). No tie at 22: the `Tokyo Special Division 4` roster (`@198`) phrases
   all carry the digit `4`, and `_number_flexible` flexes only trailing `s`,
   never digits, so none match a `division 5` query. Q4/Q8 edit the
   already-matching entries in place.

## YAML patch (verbatim, `series/csm/overrides.yaml`)

Top level (key currently absent from CSM; JJK has none either → JJK untouched):

```yaml
semantic_types:
  establishment: organization
```

Four new rosters (append in the `rosters:` section; comments in house style):

```yaml
  # The wiki files these five under `Devil Hunters` (74 pages) or not at all;
  # `Fami` has no page in the category. Named from the `Devil Hunter Club` page.
  - name: Devil Hunter Club
    match: [devil hunter club]
    members: [Asa Mitaka, Yoru, Fami, Hirofumi Yoshida, Haruka Iseumi]

  # `Quanxi` is the set's namesake and has no member page of her own under the
  # `Fiends` category, so the category read can never return her.
  - name: Quanxi and the Fiends
    match: [quanxi and the fiends]
    members: [Quanxi, Pingtsi, Long, Cosmo, Tsugihagi]

  # Employees the wiki names on the facility page; `Unnamed *` and `Takagi`
  # have no dedicated pages and survive on chunk mentions alone.
  - name: Tokyo Devil Detention Center
    match: [tokyo devil detention center]
    members: [Unnamed Surgeons, Unnamed Devil Hunters, Unnamed Guards, Takagi,
              Quanxi]

  # The division page names its personnel; the `special divisions` roster lists
  # divisions, not people.
  - name: Tokyo Special Division 5
    match: [tokyo special division 5]
    members: [Makima, Katana Man, Reze, Quanxi, Barem Bridge, Miri Sugo]
```

Two edits to existing entries:

```yaml
  - name: Four Horsemen
    match: [four horsemen, horseman, horsemen]
    category: Four Horsemen
    # No wiki pages for Control/War Devil; the category read (6 docs) can never
    # return them. Members beat the category read (roster.py:3282). The count
    # roster @184 already declares this same list; keep the two in sync.
    members: [Control Devil, War Devil, Famine Devil, Death Devil]
```

```yaml
  - name: Weapon Devils
    match: [weapon devil, weapon devils]
    members: [Katana Man, Reze, Quanxi, Miri Sugo, Barem Bridge, Whip Hybrid,
              Spear Hybrid, Katana Devil, Bomb Devil, Bow Devil]
```

(the existing `# to the *human* each devil later fused with…` comment block
stays; the 3 devil names are the infobox `members` field the page campaign
scores against.)

## Verified facts behind the fix

- `facts.db` chunks: all 26 member strings of the six rosters are present —
  minimums: `Unnamed Surgeons` 1, `Unnamed Guards` 1, `Bow Devil` 6, `Cosmo` 79
  → every name passes the `_declared_members` gate
  (`store.node_by_name(name) or _mentioned_anywhere`, `roster.py:3297`).
- Gold daggers (`Pingtsi †`, `Takagi †`, …) are handled by the scorer's
  `norm` — Q5's live repro found the 4 daggered gold items 4/5 → plain member
  strings (no †) are correct.
- Q1/Q2: after `establishment → organization`, `Fourth East High School`
  passes the type rule (`roster.py:4208-4209`: organisations are never
  rejected) → 4/4.

## Risks / side effects

1. `establishment → organization` (CSM only): every CSM establishment page
   (Fourth East High School, and any other establishment-typed page) now reads
   as an organization in type rules. Semantically correct (schools/facilities
   are organizations); JJK and every other series are untouched (per-series key).
2. Q8 union: the bank "Every Weapon Devil" question golds the 7 hybrid names.
   If that bank question is set-kind with a closed accept, the 3 extra devil
   names could read as intruders — re-run it after the edit (offline, seconds).
   If fact-kind, extras are harmless (`accept=all`, presence-based).
3. Q4 side effect: any question matching `four horsemen/horseman/horsemen` now
    answers the 4 devils instead of the 6 category docs (Fami/Makima/Nayuta/
    Yoru drop out) — canonically more accurate; the count roster
    (`"How many members are in the Four Horsemen"`, YAML `@184`) is unaffected
    and already declares the same 4-member list, so the edit mirrors it.

## Verification plan (when the fix lands)

1. Re-run `/tmp/opencode/repro8.py`: all 8 bundles contain their gold members.
2. Re-run the 8 page-campaign questions: all 8 pass.
3. No-regression set: bank Weapon Devils question + the six passing campaign
   questions (`american_thugs`, `anti_makima_squad`, `chainsaw_man_church`,
   `family_burger_restaurant`, `prophecy_of_nostradamus`,
   `tokyo_special_division_4`).
4. Class B only → no four-gate re-run (Ruling 5e). If the `semantic_types`
   line is later treated as engine-adjacent, `pytest tests/ -q` is the only
   gate it could plausibly touch (pure YAML data, no `.py` change).