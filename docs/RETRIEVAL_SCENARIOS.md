# Ten scenarios, and what they found

Dragon Ball and One Piece were indexed but had never been asked a question a
script would actually ask. Ten enumeration topics were run against them (eight
probes and two controls per wiki) and scored against the wikis' own category
counts rather than by eye.

Eight of the ten were wrong. The cause was one defect, and it had been invisible
because the wiki it does not affect is the wiki everything was developed on.

## The result

| # | series | question | before | after |
|---|---|---|---|---|
| 1 | `db` | Every race in Dragon Ball | `Dragon Ball Z episodes`, **150 episode titles** | `Races`, **128** ✅ |
| 2 | `db` | All types of Dragon Balls | `Balls (Class)`, 17 | `Dragon Balls`, **17** ✅ |
| 3 | `db` | Every Dragon Ball movie | `Dragon Ball Z episodes`, **150 episode titles** | `Films`, **24** ✅ |
| 4 | `db` | All types of non-humans | `Dragon Ball Z episodes`, **150 episode titles** | `Races`, **128** ✅ |
| 5 | `db` | Every Saiyan transformation *(control)* | `Transformations`, 150 | `Transformations`, 150 ⚠️ |
| 6 | `onepiece` | Every race in One Piece | `One Piece Volumes`, **116 volumes** | `Races and Tribes`, **34** ✅ |
| 7 | `onepiece` | All officer ranks in the Marines | `Marine Officers`, **14 people** | `Marine Ranks`, **27 ranks, 3 divisions** ✅ |
| 8 | `onepiece` | Every One Piece movie | `One Piece Movies`, 16 | `Movies`, **16** ✅ |
| 9 | `onepiece` | Every type of Devil Fruit *(control)* | 3 | 3 ✅ |
| 10 | `onepiece` | Every Warlord of the Sea *(control)* | 12 | 12 ✅ |

Only 2, 8, 9 and 10 were right to begin with, and 8 was right by luck: the query
says "movie" and the category is literally `One Piece Movies`, so the defect
below happened to point at the correct answer.

## The defect: a query that names the series

Asked for "Every race in Dragon Ball", the engine returned the names of 150
Dragon Ball Z episodes. Asked for "Every race in One Piece", it returned 116
volumes.

Both wikis name most of their categories after themselves: `Dragon Ball Z
episodes`, `Dragon Ball media`, `One Piece Volumes`, `One Piece International`.
Discovery scores a category by how many of the query's words its name contains.
A query that says "in Dragon Ball" therefore hands two free words to every one
of those categories, and none to `Races`, which shares exactly one word with the
question and loses.

The proof is one character of difference:

```
"Every race"                 -> Races                  128 members   correct
"Every race in Dragon Ball"  -> Dragon Ball Z episodes 150 members   wrong
```

**Why it had never been seen.** `roster.py` already stripped these words, via
`_work_words`, which reads the titles of pages typed `series`, `anime`, `manga`,
`novel`, `game` or `stage_play`. Jujutsu Kaisen has 11 such pages, so JJK worked
and every eval passed. Dragon Ball types its works `animanga` and One Piece
types its main page `simple_box`; neither is on that list, so both stores return
**zero** work-typed pages and the strip was a no-op on exactly the two wikis
that needed it.

**And on `db`, the page was gone.** `Dragon Ball` and `Dragon Ball Super` are
not in the store at all: they were typed `unknown` and deleted by the prune
that removed video-game and soundtrack pages. Any mechanism that learns a
series' name from its own pages learns nothing there.

## The fix

Learn the name from the **manifest**, not from a page: the host
`dragonball.fandom.com` gives `dragonball`, which cannot be pruned. Then remove
that name from both sides of the comparison (the query and each candidate
category) so "Every race in Dragon Ball" scores the way "Every race" already
did.

Matching is on an exact run of words, and that detail is what keeps scenario 2
working: **"Dragon Balls" concatenates to `dragonballs`, not `dragonball`**, so
the series loses its name while the object keeps it. Stripping loosely would
have deleted the entire query.

Two approaches were tried and rejected first, both recorded in `roster.py`:

* **Demote publication categories** (episodes, volumes, films) unless the query
  asks for them. It fixed scenario 1 by promoting the next series-named category,
  `Dragon Ball media`, 150 members. Whack-a-mole: the list of packaging words
  can never cover every category a wiki names after itself. Kept anyway, as a
  narrower rule that is right on its own terms.
* **Extend `_WORK_TYPES`** to include `animanga`. It strips "dragon" and "ball"
  from every query, which breaks scenario 2 outright: the object's name *is*
  the series' name.

## What was config, and what was code

The architecture's claim is that per-wiki knowledge lives in
`series/<name>/overrides.yaml` and never in a `.py` file. That held for five of
the eight failures. Three needed code, and none of them names a series:

| failure | fix |
|---|---|
| series name hijacks discovery (1, 3, 4, 6) | **code**: learn the title from the manifest, strip it from both sides |
| ranks are not a category (7) | **code**: a new `sections_of:` source, plus config to use it |
| races span two categories (6) | **code**: a new `categories:` union, plus config to use it |
| "movie" does not reach `Films` (3) | config: `match:` vocabulary |
| "non-human" reached `Non-english dubs` (4) | config: `match:` vocabulary |

### `sections_of:`, the fourth way a wiki states a set

`roster.py` reads sets from a category, a page type, or an infobox field. The
Marine ranks are none of those: no rank has its own article, so asking by
category returns `Marine Officers`, fourteen people rather than the ladder. The
wiki writes all of them as sections of one page, grouped by division:

```yaml
- name: Marine Ranks
  match: [marine rank, officer rank, ranks in the marines]
  sections_of: Marine Ranks
```

The level carrying the most sections becomes the members and the heading above
them becomes the group, which recovers 27 ranks under Commissioned Marine
Officers, Infantry and Sailor Division, and Support Staff.

### `categories:`, a union rather than a grouping

`groups:` makes the groups *be* the members, which is right for "Every Nen Type"
(six types, not 111 users) and wrong for races: declaring races that way
returned **2**, the names of the two categories. `categories:` unions them
instead, giving 34.

## A mistake worth recording

Declaring the Dragon Balls set with a bare `match: [dragon ball]` made **every**
enumeration on that wiki resolve to it, because every question about the series
says the series' name. This is the same failure as the earlier Jujutsu Kaisen
registry hijack, reintroduced while fixing a different bug, and caught by
re-running the ten scenarios rather than by reasoning. Only the qualified
phrasings are declared now, and there is a test asserting that the greedy
version would have matched.

## Still open

**Scenario 5 is capped, not complete.** `Transformations` has 160 members and
`MAX_MEMBERS` is 150, so ten are missing and nothing says so. A capped roster
should announce itself.

**Scenario 5 also ignores its qualifier.** "Every Saiyan transformation" returns
all 150 transformations in the series, not the Saiyan ones. A declared set
deliberately beats a narrower reading (the same rule that makes "Every Cursed
Technique of Sukuna" work is what suppresses "Saiyan" here) so this is a
trade-off rather than a bug, but it is the wrong side of the trade for this
question.

**Scenario 3 renders 24 of 26.** The three film categories union to 26 pages;
two are dropped for having neither prose nor facts.

**`Dragon Ball` and `Dragon Ball Super` are still missing from the store**, along
with roughly a thousand other pages the prune removed as `unknown`. Removing
`unknown` from `db`'s `prune_types` and re-running `crawl --refresh` would
restore them; the crawl costs about three minutes, the reindex considerably more.

## A second pass: twenty-one probes for what still fails silently

The ten scenarios above were chosen to be answerable. A second round was chosen
to be awkward (nonsense sets, terms borrowed from another series, romanisations
the wiki may not use, near-name collisions) and run through the API rather than
in-process, because that is the path a script writer actually takes.

**Fixed by the work above.** These returned a confident wrong list before and
return the right answer, or honestly nothing, now:

| probe | before | after |
|---|---|---|
| Every zzzzz in Dragon Ball | `Dragon Ball Z episodes`, 39 | **0** |
| Every Devil Fruit in Dragon Ball | `Dragon Ball Z episodes`, 39 | **0** |
| Every Angel in Dragon Ball | `Dragon Ball Z episodes`, 39 | `Angels`, 21 |
| Every saga in Dragon Ball Z | `Dragon Ball Z episodes` | `Sagas`, 67 |
| Every Dragon Ball GT episode | `Dragon Ball Z episodes` | `Episodes`, 150 |
| Every Haki type | `Haki Users`, 8 people | `Haki Types`, 3 |
| every RACE in ONE PIECE | `One Piece Volumes`, 37 | `Races and Tribes`, 34 |

A nonsense query returning **0** rather than 39 episode titles is the single
clearest measure of the fix: the engine now declines instead of inventing.

**Still failing, and silently.** Every one of these returns HTTP 200 with a
plausible, populated set:

| probe | returns | what it actually is |
|---|---|---|
| Every Straw Hat Pirate | 14 | `Straw Hat Pirates' Creations`, the crew's *weapons* |
| Every admiral | 4 | Chichilisia, Mont Blanc Noland, Vinsmoke Judge, Z; no Akainu, no Kizaru |
| Every island in the Grand Line | 4 | there are hundreds |
| Every God of Destruction | 150 | all `Deities` |
| Every Saiyan in One Piece | 3 | `Rosward Family`, for a race that does not exist in One Piece |
| Every Saiyan transformation | 150 | all transformations; the qualifier is ignored |
| Every Frieza Race transformation | 150 | the same 150, two different questions with one answer |

And two that fail honestly, by returning nothing: `Every Yonko` and `Every
Kaioshin`, both romanisations the wikis do not use (`Four Emperors` returns 7
correctly). Those are a vocabulary gap, fixable with `match:`.

**The common cause.** `_choose_set` returns its best-scoring candidate and had
no way to express that the best was weak. One incidental word ("pirate" in
`Straw Hat Pirates' Creations`) is enough to win when nothing better exists,
and the caller could not tell that answer apart from `Races` matching 128
members exactly.

### What was done about it

Rejecting weak matches outright was the wrong fix: on a wiki whose only category
for something is oddly named, a partial match is still the answer, and the
engine is not the thing that knows. So the match is now **rated and reported**
rather than enforced. Every roster carries `confidence`: `declared`, `exact`,
`partial`, `weak`, plus `unmatched`, the words of the set's name the topic
never asked for, and a `warning` in words. `cli query` prints it; `/context`
returns it.

| probe | confidence | warning |
|---|---|---|
| Every race in Dragon Ball | `declared` | n/a |
| Every Straw Hat Pirate | **`partial`** | *"narrower than the topic: creations was not asked for"* |
| Every Saiyan in One Piece | **`weak`** | *"matched nothing the topic asked for"* |

The two failures that were pure name-mismatch now announce themselves. That is
the whole of what this rating can do.

### What it still cannot see

**An incomplete set.** `Every admiral` → `Admirals` and `Every island in the
Grand Line` → `Grand Line Islands` both report **`exact`**, because the set's
name really is what was asked for. The wiki simply files four members there and
the rest elsewhere. Nothing in the name says so, so the count is the only
signal: **check `members_available` against the size you expect.**

**A declared set swallowing a qualifier.** `Every God of Destruction` returns
all 150 `Deities`, and `Every Saiyan transformation` all 150 transformations,
both reporting `declared`. This is the rule that makes "Every Cursed Technique
of Sukuna" work, applied where it is unhelpful. Neither wiki has a category for
the narrower set, so there is no right answer available to return.

**A vocabulary gap.** `Every Yonko` and `Every Kaioshin` return nothing, which
is honest but unhelpful. Both are fixable with `match:` on a declared set.

## Reproducing

```powershell
python -m scriptengine.cli eval --series db          # 5/5
python -m scriptengine.cli eval --series onepiece    # 5/5
python -m scriptengine.cli eval --series jjk         # 24/24, unchanged
```

All ten scenarios are now permanent eval cases in `scriptengine/eval/gold_db.json`
and `gold_onepiece.json`, with `expect_min_members` taken from the wiki's own
category counts rather than from what the engine returned; otherwise the eval
would lock in today's behaviour instead of the truth.
