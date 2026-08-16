# What the query path filters out, per wiki

Measured against `reports/2026-08-14-1352`. Of **245 missed canon items**, the
store already knows about **92**. They are on the page, in the database, and
the query path drops them. Two filters do it, and neither is configurable today.

| filter | where | items lost |
|---|---|---:|
| the relation whitelist | `_BELONGS_RELATIONS`, `roster.py:1926` | **54** |
| the ability-kind filter | `abilities_of(character, kinds)` | **38** |
| n/a | store has never heard of them (crawl/extraction) | 121 |
| n/a | linked only to a non-subject node (alias hops, battle pages) | 32 |

`_BELONGS_RELATIONS` is seven names long and hardcoded:

```python
('user', 'users', 'wielder', 'wielders', 'practitioner', 'practitioners', 'owner')
```

Every relation below is one the wiki actually wrote, joining the question's
subject to the answer, that this list excludes.

## Direction matters

`store.owned_by(x, rels)` finds pages that **name** `x`. It walks *into* a
page. `store.linked_from(x, rels)` walks *out*. The roster path only ever calls
`owned_by` (`roster.py:904`), so an outward relation is invisible to it no
matter what the whitelist says.

- **`in`**: the edge runs `member -rel-> subject`. `owned_by` already finds
  these; the relation only needs whitelisting.
- **`out`**: the edge runs `subject -rel-> member`. Needs `linked_from`, which
  the roster path does not call. **This is a code change, not a declaration.**

## Per wiki

Counts are items each relation reaches. They **overlap**: Griffith is reachable
by `notable members`, `affiliations` and `founders` at once, so a column does
not sum to the 54 unique items.

### berserk: the worst affected, 26 distinct items

| relation | dir | items | verdict |
|---|---|---:|---|
| `notable members` | out | 24 | **take**: `Band of the Falcon -> Griffith, Guts, Casca, Judeau…` |
| `affiliations` | in | 17 | **take** |
| `key members` | out | 7 | **take**: the reborn Band |
| `founders` | out | 1 | **take** |
| `allies` | in | 10 | **reject**: an ally is not a member; this is the relation that would import noise |
| `purpose` | out | 1 | **reject**: not a membership field at all |
| `weapons` | out | 1 | **take** for equipment questions: `Serpico -> Sylph Sword` |

### csm: 17 distinct items

| relation | dir | items | verdict |
|---|---|---:|---|
| `affiliation` | in | 14 | **take**: `Makima -affiliation-> Tokyo Special Division 4` |
| `notable_members` | out | 4 | **take**: note the underscore; berserk spells it with a space |
| `contracted devils` | out | 3 | **take**: `Aki Hayakawa -> Fox Devil, Curse Devil, Future Devil` |
| `contracted humans` | in | 3 | **take**: the same fact written from the devil's side |

### bleach: 3 items

| relation | dir | items | verdict |
|---|---|---:|---|
| `previous team` | in | 3 | **take**: `Espada -> Tier Harribel, Grimmjow, Szayelaporro`. Former members, so it also needs the current/former distinction the roadmap already tracks |

### jjk: 3 items

| relation | dir | items | verdict |
|---|---|---:|---|
| `affiliation` | in | 3 | **take**: fixes `Every first-year student of Tokyo Jujutsu High`, the one "confident and wrong" answer in the whole run |

### db: 3 items, and a different mechanism

| relation | dir | items | verdict |
|---|---|---:|---|
| `aniname` | in | 2 | **not membership**: `Majin Buu -aniname-> Kid Buu` is an *alternate name*, not a member |
| `altname` | in | 1 | **not membership**: same |

These would work for `Every form of Majin Buu` by accident. An alias relation
belongs in identity resolution, not in the membership whitelist. Treating "is
also called X" as "contains X" will misfire the moment a page has an alias that
is not a form. Handle with the same mechanism that should resolve
`Atomic Samurai` ↔ `Kamikaze`.

### opm, hxh, onepiece: 0 items from relations

Their misses are kind-filter and extraction gaps, below. (Atomic Samurai's
disciples are reachable only through `relationship`, which also carries family
and rivals, and through a `Kamikaze` alias, so they are an identity problem,
not a whitelist one. Declare that roster instead.)

## The kind filter: 38 items

`abilities_of(character, kinds)` selects stored rows by `kind`, and a row filed
under a kind the question did not ask for is dropped even though it is the
right answer.

| stored kind | items | worst | examples |
|---|---:|---|---|
| `transformation` | 31 | jjk 13, bleach 9 | `Megumi Fushiguro: Toad` (a shikigami), `Ichigo: Blut Vene`, `Gon: Jajanken` |
| `item` | 6 | berserk 2 | `Serpico: Rapier`, `Kenpachi: Nozarashi`, `Sonic: Exploding Shuriken` |
| `technique` | 1 | bleach | `Ichigo: Final Getsuga Tenshō` asked as a *form* |

Two distinct problems:

1. **The label is wrong for the wiki.** Megumi's shikigami are stored as
   `transformation`; jjk already declares
   `ability_kinds: {technique: [shikigami, shikigamis]}`, so the mapping exists
   and the extraction pass did not apply it. Fixable per wiki via
   `ability_kinds`/`semantic_types`, no code.
2. **The question is broad and the filter is narrow.** "Every **ability** of X"
   should accept every kind; only "every technique" / "every form" should
   narrow. Worth checking whether the router distinguishes them before adding
   per-wiki mappings, because if it does not, one change fixes most of the 38.

`item` is the sharpest case: a shuriken, a rapier and a zanpakutō are equipment
to the wiki and abilities to the question. That is a judgement per question
type, not a data error.

## What to do, cheapest first

1. **Declare the four broken group rosters** (Band of the Falcon (×2), Tokyo
   Special Division 4, Atomic Samurai's disciples) in
   `series/<name>/overrides.yaml → rosters`. Pure data, no code, and it reuses
   the path already measuring ~87% precision. The seven zero-recall
   group-membership questions hold **55 canon items** between them: Band of the
   Falcon 14, Tokyo Special Division 4 14, reborn Band 10, Weapon Devils 7, Four
   Kings 4, JJK first-years 3, Atomic Samurai's disciples 3, out of 72 in all
   twelve zero-recall questions.
2. **Make the relation whitelist a per-wiki declaration** rather than a
   hardcoded tuple, seeded with the `take` rows above. Small code change,
   inherits the existing `owned_by` path for every `in` relation.
3. **Call `linked_from` for `out` relations** in the roster path. This is what
   `notable members` and `key members` need, and it is the only genuinely new
   retrieval behaviour on this page.
4. **Fix the kind labels** for jjk shikigami and check whether "every ability"
   questions can accept all kinds.

Nothing here needs a re-crawl. Everything here is the wiki already having said
it plainly.
