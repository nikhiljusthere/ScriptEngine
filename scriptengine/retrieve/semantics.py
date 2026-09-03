"""What an entity *is*, as distinct from where the wiki filed it.

`Galactic Frieza Army` is a category with 230 pages in it: 121 characters, 37
races, 24 techniques, 23 factions, 18 planets and 6 battles. Asked for the
army's members, the engine returned all 230, because a category is a filing
decision and membership is a semantic one. A planet is not a member of an army.

The wiki already knows the difference and says so in the infobox it chose for
each page, and the crawler stores that as `page_type`. What it does not do is
speak one vocabulary: a character is `character` on Dragon Ball, `char_box` on
One Piece, `hunterpedia_character` on Hunterpedia and
`bleach_wiki_character_arrancar` on Bleach. So the mapping is on the *tokens*
inside a discovered type id rather than on a table of ids, and a new wiki is
covered the moment it names its infoboxes in recognisable words.

Nothing here names a series. `series/<name>/overrides.yaml` can add
`semantic_types:` for a wiki whose vocabulary is genuinely its own.
"""

from __future__ import annotations

import re
import sqlite3
from weakref import WeakKeyDictionary

from scriptengine.stores.facts import FactStore

# The vocabulary an entity can be classified into.
CHARACTER = "character"
RACE = "race"
ORGANIZATION = "organization"
LOCATION = "location"
TECHNIQUE = "technique"
# A graded capability the wiki names but never gives a page:
# `Immense Strength`, `Great Tactical Intellect`, `Cursed Energy
# Capacity`. The bank counts these as abilities and not as
# techniques, and until this existed they were stored as
# `technique` and answered "Every cursed technique of X" wrongly.
TRAIT = "trait"
TRANSFORMATION = "transformation"
POWER_UP = "power_up"
FUSION = "fusion"
ITEM = "item"
EVENT = "event"
MEDIA = "media"
UNKNOWN = "unknown"

# Tokens that appear inside the type ids wikis actually choose, longest first so
# `character_synopsis` does not win on `character`. A page type is matched by
# containment, which is what makes `bleach_wiki_character_arrancar` a character
# without Bleach being mentioned anywhere.
_TYPE_TOKENS: tuple[tuple[str, str], ...] = (
    ("synopsis", MEDIA),
    ("character_history", MEDIA),
    ("devil_fruit", ITEM),
    ("greed_island_card", ITEM),
    ("zanpakut", TECHNIQUE),
    ("technique", TECHNIQUE),
    ("ability", TECHNIQUE),
    ("spell", TECHNIQUE),
    ("jutsu", TECHNIQUE),
    ("character", CHARACTER),
    ("char_", CHARACTER),
    ("fauna", RACE),
    ("race", RACE),
    ("species", RACE),
    ("organization", ORGANIZATION),
    ("faction", ORGANIZATION),
    ("crew", ORGANIZATION),
    ("group", ORGANIZATION),
    ("division", ORGANIZATION),
    ("clan", ORGANIZATION),
    ("guild", ORGANIZATION),
    ("planet", LOCATION),
    ("island", LOCATION),
    ("location", LOCATION),
    ("establishment", LOCATION),
    ("weapon", ITEM),
    ("object", ITEM),
    ("item", ITEM),
    ("ship", ITEM),
    ("vehicle", ITEM),
    ("battle", EVENT),
    # Before `fight`, which this contains. One Piece files 63 pages under
    # `fighting_style_box` and its variants -- Three Sword Style, Black Leg
    # Style, Foxfire Style, Art of Weather -- and `fight` was reading every one
    # of them as a battle. `event` is in `NEVER_MEMBERS`, so a fighting style
    # could not be a member of anything: Zoro's styles are gold for two bank
    # questions and Nami's `Art of Weather` for a third, and all of them were
    # dropped by `_owned_roster` before any filter got a say. Bleach's 192
    # genuine `fight` pages are battles and stay as they are.
    ("fighting_style", TECHNIQUE),
    ("fighting style", TECHNIQUE),
    ("fight", EVENT),
    ("combat", EVENT),
    ("conflict", EVENT),
    ("event", EVENT),
    ("episode", MEDIA),
    ("chapter", MEDIA),
    ("volume", MEDIA),
    ("film", MEDIA),
    ("movie", MEDIA),
    ("music", MEDIA),
    ("album", MEDIA),
    ("soundtrack", MEDIA),
    ("book", MEDIA),
    ("novel", MEDIA),
    ("game", MEDIA),
    ("anime", MEDIA),
    ("manga", MEDIA),
    ("arc", MEDIA),
    ("saga", MEDIA),
    ("story", MEDIA),
    ("year", MEDIA),
    ("cite", MEDIA),
    ("tab", UNKNOWN),
)

# The `Class` field distinguishes what a category cannot: the Dragon Ball wiki
# writes `Class = Power Up` on Kaio-ken and `Class = Transformation` on Super
# Saiyan, and both sit in `Transformations`.
_CLASS_TOKENS: tuple[tuple[str, str], ...] = (
    ("fusion", FUSION),
    ("transformation", TRANSFORMATION),
    ("power up", POWER_UP),
    ("power-up", POWER_UP),
)

# The whole vocabulary, for anything that has to validate a type name.
ALL_TYPES = frozenset(
    {
        CHARACTER, RACE, ORGANIZATION, LOCATION, TECHNIQUE, TRANSFORMATION,
        POWER_UP, FUSION, ITEM, EVENT, MEDIA, TRAIT, UNKNOWN,
    }
)

# Which types can be a *member* of something. An army has people in it; the
# planets it conquered and the armour it issues are related, not members.
MEMBER_TYPES = frozenset({CHARACTER, ORGANIZATION})

# Types that are never a member of anything, whatever the set is made of: a
# volume, a battle and a planet are setting and packaging, not membership.
NEVER_MEMBERS = frozenset({MEDIA, EVENT, LOCATION})

# Abilities are one family. `technique`, `transformation`, `power_up` and
# `fusion` are distinctions *within* it, and which one a page gets depends on
# whether the wiki filled in a `Class` field, so they must never be used to
# reject each other. Only `is_power_up_only`, reading the field directly, is
# allowed to separate them.
ABILITY_TYPES = frozenset({TECHNIQUE, TRANSFORMATION, POWER_UP, FUSION, TRAIT})

_WORD_SPLIT = re.compile(r"[^a-z0-9]+")


# Classification is asked the same question twice within one request. Building
# "Every form of Goku" classifies each page Goku owns, classifies the survivors
# again inside `apply_constraints`, and profiles several of them more than once:
# measured, 233 calls to `semantic_type` for 216 distinct names and 75 calls to
# `roster._profile` for 44. The repeats are worth removing on their own, and the
# memo is also what makes the *distinct* calls affordable to batch later.
#
# *Where* the memo lives is the part that matters. A dict keyed on the database
# path would be wrong: the path outlives the data, `index` rewrites `documents`
# and `facts` from scratch, and the next request would be answered out of the
# previous corpus, silently, and for as long as the process ran. Keyed on the
# `FactStore` instance it cannot. Retrieval opens one store per request
# (`build_roster` and `_qa_context` both do `with FactStore(paths.facts_db) as
# store:`) and closes it on the way out, so an entry's life is bounded by the
# connection it was read through, and nothing cached can be older than the
# request that cached it.
#
# The keys are weak, and the store holds nothing on this module's behalf, so
# `FactStore` needs no knowledge that its readers memoise and a closed store's
# memo is collected with it rather than pinned here.
_STORE_CACHES: "WeakKeyDictionary[FactStore, dict[str, dict]]" = WeakKeyDictionary()


def request_cache(store: FactStore, bucket: str) -> dict:
    """A named memo dict whose lifetime is exactly `store`'s.

    Shared with `retrieve/roster.py`, which memoises `_profile` on the same
    terms. Only ever for values derived from the store by reading: anything
    that writes to it invalidates every bucket, and nothing here is told when
    that happens.
    """
    caches = _STORE_CACHES.get(store)
    if caches is None:
        caches = {}
        _STORE_CACHES[store] = caches
    return caches.setdefault(bucket, {})


# `documents.title` is `TEXT NOT NULL UNIQUE`, which builds a BINARY index that a
# `COLLATE NOCASE` comparison cannot use, so the lookup in `_classify` is a
# `SCAN documents`, 1.5ms apiece on `series/db/facts.db`, spent proving over and
# over that 7,205 rows are not the one wanted. With this index EXPLAIN QUERY PLAN
# reports `SEARCH documents USING INDEX idx_documents_title_nocase (title=?)` and
# the lookup no longer measures.
#
# Adding an index rather than dropping the collation is the whole point. Dropping
# `COLLATE NOCASE` would turn a case-insensitive lookup into a case-sensitive one
# and silently stop matching wherever a caller's spelling differs from the stored
# title. An index changes the plan and cannot change the answer, but "cannot"
# was checked rather than assumed, because a plan change *can* reorder a query
# that never said what order it wanted. Every `COLLATE NOCASE` query against
# `documents` in this codebase (this one, `document_lead`, `categories_of`,
# `sections_of`) was run over every title in all eight series with the index and
# without it: identical, to the row. It is safe here because no wiki holds two
# titles differing only in case, so there is one candidate row either way.
#
# The matching index on `nodes(name COLLATE NOCASE)` is deliberately *not* here,
# though `facts_for` wants it far more badly: a `SCAN facts` at 4.2ms a call,
# the single largest cost left in a roster. Bleach has two nodes called
# `Memories in the Rain` and `Memories in the rain`, and with the index the
# unordered `SELECT DISTINCT` in `owned_by` visits them the other way round and
# hands back the same four names in a different order. `roster.classify` reads
# `users[:12]`, so that is an answer change, not a plan change. Making it safe
# means giving those queries the ORDER BY they always implied, which is
# `stores/facts.py` and not this file.
#
# The permanent home for this one is `stores/schema.sql`, so that a store is born
# with it. Created here as well, and idempotently, because every store that
# already exists was not. `ensure_semantics` and `ensure_abilities` are the same
# pattern, a schema addition an existing store has to grow in place.
_LOOKUP_INDEXES = (
    "CREATE INDEX IF NOT EXISTS idx_documents_title_nocase"
    " ON documents(title COLLATE NOCASE)",
)


def ensure_lookup_indexes(store: FactStore) -> None:
    """Give an existing store the case-insensitive index its lookups need.

    Attempted once per store and never again, whether or not it worked. A
    failure is not an error: the store may be open read-only, or `index` may
    hold the write lock, and in both cases the right behaviour is the slow
    answer rather than no answer.

    Deliberately does not commit. A read path that commits would commit whatever
    the caller happened to have pending, and DDL outside a transaction is
    durable without it.
    """
    done = request_cache(store, "lookup_indexes")
    if done:
        return
    done["attempted"] = True
    for statement in _LOOKUP_INDEXES:
        try:
            store.connection.execute(statement)
        except sqlite3.DatabaseError:
            return


def _declared_types(overrides: dict | None) -> tuple[tuple[str, str], ...]:
    """The only part of `overrides` that can change a classification.

    Part of the memo key rather than the identity of the dict: `id()` is reused
    the moment a temporary is freed, and a caller passing one literal and then
    another is exactly the shape a test has.
    """
    declared = (overrides or {}).get("semantic_types") or {}
    if not isinstance(declared, dict):
        return ()
    return tuple(
        sorted((str(key).lower(), str(value)) for key, value in declared.items())
    )


def type_from_page_type(page_type: str, overrides: dict | None = None) -> str:
    """Fold a wiki's own infobox name into the shared vocabulary."""
    lowered = (page_type or "").strip().lower()
    if not lowered:
        return UNKNOWN

    declared = (overrides or {}).get("semantic_types") or {}
    if lowered in {str(key).lower() for key in declared}:
        return str(declared[lowered]).strip().lower()

    for token, semantic in _TYPE_TOKENS:
        if token in lowered:
            return semantic
    return UNKNOWN


def type_from_class(value: str) -> str:
    """`Class = Power Up` is a different thing from `Class = Transformation`.

    A value naming both ("Power Up Transformation") is read as the stronger
    of the two, because the page is still a form; `Powerhouse` writes
    "Transformation/Power Up" and means the same.
    """
    lowered = (value or "").strip().lower()
    if not lowered:
        return UNKNOWN
    for token, semantic in _CLASS_TOKENS:
        if token in lowered:
            return semantic
    return UNKNOWN


def semantic_type(store: FactStore, name: str, overrides: dict | None = None) -> str:
    """What `name` is, from its infobox first and its `Class` field second.

    Memoised for the life of `store`; see `request_cache`. The name is keyed
    verbatim rather than case-folded: the lookup below matches `COLLATE NOCASE`,
    which folds ASCII only, and `str.lower()` folds more than that. Two spellings
    of one title cost two lookups; they never share a wrong answer.
    """
    ensure_lookup_indexes(store)
    memo = request_cache(store, "semantic_type")
    key = (name, _declared_types(overrides))
    if key not in memo:
        memo[key] = _classify(store, name, overrides)
    return memo[key]


def _classify(store: FactStore, name: str, overrides: dict | None) -> str:
    row = store.connection.execute(
        "SELECT id, page_type FROM documents WHERE title = ? COLLATE NOCASE", (name,)
    ).fetchone()
    from_page = type_from_page_type(row["page_type"] if row else "", overrides)

    # A technique page that declares itself a transformation is a transformation:
    # the infobox is shared, the field is specific.
    if from_page in {TECHNIQUE, UNKNOWN}:
        for fact in store.facts_for(name):
            label = (fact["label"] or fact["key"] or "").strip().lower()
            if label in {"class", "type", "kind"}:
                refined = type_from_class(fact["value"] or "")
                if refined != UNKNOWN:
                    return refined

    if from_page == UNKNOWN and row is not None:
        refined = _from_categories(store, row["id"], name)
        if refined != UNKNOWN:
            return refined
    return from_page


# Category names a wiki files its people under. Matched whole, never as a
# substring: `Monster Association Arc Fights` contains "arc" and is a fight.
_CHARACTER_CATEGORIES = frozenset({"characters"})


def _from_categories(store: FactStore, document_id: int, title: str) -> str:
    """Last resort when the infobox says nothing, read from the categories.

    One Punch Man wraps its character pages in a tabber -- Manga, Anime,
    Webcomic -- so the infobox the crawler finds is the tab container and
    `page_type` comes back `parent_tab`. 271 pages are like that, including
    Saitama, Garou, Genos, Bang, Tatsumaki and King: every major character in
    the series classified `unknown`. Anything filtering on "is this a
    character" silently dropped the entire main cast, which is how
    `Monster Association Arc` returned a 119-name roster with no Saitama in it.

    The categories are unambiguous where the infobox is not: Saitama is in
    `Characters`, `Heroes`, `A-Class`; `Audiobooks` is in `Audiobooks`; the
    fight pages are in `Fights`.

    Deliberately narrow. Only `Characters` is trusted, and only when the page is
    not itself an index of them. Three kinds of index sit in that category
    across these wikis and none is a person:

    * **The page is named after a category this wiki has.** `Heroes` is filed
      under `Characters` and is the list of every hero; `Heroes` is also a
      category here. Saitama is not a category, and neither is `Empty Void` or
      `Beaut`, which are real characters filed the same way. This is the general
      test -- an index is named after the group it indexes.
    * **`List of ...`**, which says so.
    * **Anything still naming `character`** -- `Miscellaneous Characters`,
      `Characters/Arrancar` -- kept as a backstop for wikis whose index pages
      are not categories.

    Measured across the eight wikis, this types 84 One Punch Man pages and
    leaves every other wiki untouched.
    """
    lowered = title.strip().lower()
    if "character" in lowered or lowered.startswith("list of "):
        return UNKNOWN
    found = {
        (row["category"] or "").strip().lower()
        for row in store.connection.execute(
            "SELECT category FROM categories WHERE document_id = ?", (document_id,)
        )
    }
    if not found & _CHARACTER_CATEGORIES:
        return UNKNOWN
    # An index is named after the group it indexes. Checked against this wiki's
    # own category names rather than a word list, so it needs no upkeep.
    if _is_a_category(store, lowered) or _is_a_category(store, lowered.split("/")[0]):
        return UNKNOWN
    return CHARACTER


def _is_a_category(store: FactStore, name: str) -> bool:
    """Whether this wiki has a category by exactly this name."""
    if not name:
        return False
    return (
        store.connection.execute(
            "SELECT 1 FROM categories WHERE category = ? COLLATE NOCASE LIMIT 1",
            (name,),
        ).fetchone()
        is not None
    )


def is_power_up_only(store: FactStore, name: str) -> bool:
    """True when the wiki calls this a power-up and never a transformation.

    Dark Dragon Ball Enhancement and Evil Aura are both `Class = Power Up`, sit
    in `Transformations`, and are not transformations of anything; they are
    granted from outside and stack on whatever form you already had.
    """
    for fact in store.facts_for(name):
        label = (fact["label"] or fact["key"] or "").strip().lower()
        if label not in {"class", "type", "kind"}:
            continue
        lowered = (fact["value"] or "").lower()
        if "power" in lowered and "transformation" not in lowered:
            return True
    return False


def expected_type(candidates: list[str], types: dict[str, str]) -> str:
    """What this set is mostly made of, so the rest can be measured against it.

    Taken from the candidates themselves rather than declared: a set is whatever
    the wiki filled it with, and the exceptions are what need catching. Returns
    `unknown` when no type holds a clear majority, which leaves the set alone.
    """
    counts: dict[str, int] = {}
    for name in candidates:
        semantic = types.get(name, UNKNOWN)
        if semantic != UNKNOWN:
            counts[semantic] = counts.get(semantic, 0) + 1
    if not counts:
        return UNKNOWN

    total = sum(counts.values())
    best, count = max(counts.items(), key=lambda item: item[1])
    # A bare plurality is not enough: `Galactic Frieza Army` is 121 characters
    # out of 230 classified, and that is the answer, but a set split three ways
    # is a set the wiki keeps for a reason this cannot see. Strict majority, so
    # a two-member set one way (an organisation and the location it sits in)
    # reads as no majority at all: with `>=` the tie broke on candidate order,
    # and `Yoshinobu Gakuganji Affiliations` lost its second member to the
    # type rule as "a location, and this is a set of organizations".
    return best if count * 2 > total else UNKNOWN


def article(semantic: str) -> str:
    """`a planet`, `an event`, for rejection messages that read like English."""
    return f"an {semantic}" if semantic[:1] in "aeiou" else f"a {semantic}"
