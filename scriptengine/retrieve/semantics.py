"""What an entity *is*, as distinct from where the wiki filed it.

`Galactic Frieza Army` is a category with 230 pages in it: 121 characters, 37
races, 24 techniques, 23 factions, 18 planets and 6 battles. Asked for the
army's members, the engine returned all 230, because a category is a filing
decision and membership is a semantic one. A planet is not a member of an army.

The wiki already knows the difference and says so in the infobox it chose for
each page — the crawler stores that as `page_type`. What it does not do is
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

from scriptengine.stores.facts import FactStore

# The vocabulary an entity can be classified into.
CHARACTER = "character"
RACE = "race"
ORGANIZATION = "organization"
LOCATION = "location"
TECHNIQUE = "technique"
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
        POWER_UP, FUSION, ITEM, EVENT, MEDIA, UNKNOWN,
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
# whether the wiki filled in a `Class` field — so they must never be used to
# reject each other. Only `is_power_up_only`, reading the field directly, is
# allowed to separate them.
ABILITY_TYPES = frozenset({TECHNIQUE, TRANSFORMATION, POWER_UP, FUSION})

_WORD_SPLIT = re.compile(r"[^a-z0-9]+")


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

    A value naming both — "Power Up Transformation" — is read as the stronger
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
    """What `name` is, from its infobox first and its `Class` field second."""
    row = store.connection.execute(
        "SELECT page_type FROM documents WHERE title = ? COLLATE NOCASE", (name,)
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
    return from_page


def is_power_up_only(store: FactStore, name: str) -> bool:
    """True when the wiki calls this a power-up and never a transformation.

    Dark Dragon Ball Enhancement and Evil Aura are both `Class = Power Up`, sit
    in `Transformations`, and are not transformations of anything — they are
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
    # is a set the wiki keeps for a reason this cannot see.
    return best if count * 2 >= total else UNKNOWN


def article(semantic: str) -> str:
    """`a planet`, `an event` — for rejection messages that read like English."""
    return f"an {semantic}" if semantic[:1] in "aeiou" else f"a {semantic}"
