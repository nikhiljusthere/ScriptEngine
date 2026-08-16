"""Which works a series counts, applied at index time.

`non_canon_works:` in `series/<name>/overrides.yaml` has always existed, but it
was only read on the query path: a game page was filtered out of a roster and
still sat in the index, reachable by search, by a citation, or by any caller
that did not ask for canon. Dragon Ball carries 40 `Xeno*` pages, 23 `Heroes`
pages, 169 rows of `Dragon Ball Heroes` categories, and 967 chunks that are
Super Dragon Ball Heroes *sections inside otherwise canon pages*: `Goku/
Biography` has a seven-saga SDBH subtree.

Dropping them here means they never reach `documents`, `sections`, `chunks`,
`nodes`, `edges` or the BM25 index, so nothing can return them by any route.
It is reversible: indexing rebuilds every one of those tables from the wikitext
on disk, which the crawl still holds.

Nothing in this module names a series.
"""

from __future__ import annotations

from typing import Any, Iterable

from scriptengine.ingest.documents import Section, WikiPage

# Edge relations that say where something first appeared. A page whose every
# debut is a discounted work belongs to that work.
_DEBUT_KEYS = ("debut", "first appearance")


def discounted_works(overrides: dict[str, Any] | None) -> tuple[str, ...]:
    """The works this series does not count, lowercased."""
    declared = (overrides or {}).get("non_canon_works") or []
    return tuple(
        str(work).strip().lower() for work in declared if str(work).strip()
    )


def _names_a_work(value: str, works: Iterable[str]) -> bool:
    """Whether a string is one of these works, or something inside one.

    Whole string or prefix, never a bare substring. `Dr. Hedo` debuts in
    *Super Heroes are Born*, a Dragon Ball Super chapter, and a substring test
    threw him out of the Red Ribbon Army along with `Gamma 1` and `Cell Max`.
    """
    folded = (value or "").strip().lower()
    if not folded:
        return False
    return any(folded == work or folded.startswith(work) for work in works)


def page_is_discounted(
    page: WikiPage,
    works: tuple[str, ...],
    categories_by_title: dict[str, list[str]] | None = None,
) -> bool:
    """Whether this whole page belongs only to a work the series discounts.

    Read from the debut **edges**, not from the `Debut` fact. The fact is one
    free-text string naming every medium at once: `Super Saiyan (Berserk)`
    reads `Game: Dragon Ball Heroes Manga: "Evil Saiyan" Anime: "Goku Goes
    Berserk!..."`, because Heroes has its own manga and its own promotional
    anime, so it looks canon on two counts of three. The edges name one work
    each and can be judged one at a time.
    """
    if not works:
        return False
    if _names_a_work(page.title, works):
        return True

    targets = [
        (edge.target or "").strip()
        for edge in page.edges
        if any(key in (edge.relation or "").lower() for key in _DEBUT_KEYS)
    ]
    targets = [target for target in targets if target]

    if targets:
        # Every debut, not any. `Super Saiyan Blue` names Dragon Ball Heroes
        # among its four and first appeared in *Resurrection 'F'*; an any-test
        # would throw away half of Goku's canon forms to catch the Heroes ones.
        return all(
            _target_is_discounted(target, works, categories_by_title or {})
            for target in targets
        )

    # Only where the page says nothing about its own debut. A category means
    # "appears in", not "belongs to": `Super Dragon Ball` is filed under both
    # `Dragon Ball Super` and `Dragon Ball Heroes`, and judging it on its
    # categories deleted a canon object out of "All types of Dragon Balls".
    # Pages with no debut at all are the game's own episodes and chapters,
    # where the category is the only thing there is to read.
    return any(_names_a_work(category, works) for category in page.categories)


def _target_is_discounted(
    target: str, works: tuple[str, ...], categories_by_title: dict[str, list[str]]
) -> bool:
    """Whether one debut target belongs to a discounted work.

    The category hop is what reaches `Evil Saiyan (chapter)`, a page whose own
    title says nothing and which is filed under `Dragon Ball Heroes manga
    chapters`.
    """
    if _names_a_work(target, works):
        return True
    return any(
        _names_a_work(category, works)
        for category in categories_by_title.get(target.lower(), ())
    )


def keep_sections(
    sections: Iterable[Section],
    works: tuple[str, ...],
    dropped: set[str] | None = None,
) -> list[Section]:
    """The sections that are not a discounted work's corner of a kept page.

    Two shapes. `Goku/Biography` is canon and its `Super Dragon Ball Heroes`
    subtree is not, matched on the breadcrumb, so a child goes with its
    parent. And a heading may name a page that was itself dropped:
    `Goku/Power and Abilities` lists `;Super Saiyan (Berserk)` among his forms,
    and once the marker is a heading that is a member of "Every form of Goku".
    The page is gone, so nothing downstream can tell it was ever a game's,
    the only moment that knows is this one.
    """
    sections = list(sections)
    if not works:
        return sections
    gone = {title.strip().lower() for title in (dropped or set())}
    return [
        section
        for section in sections
        if not any(
            _names_a_work(part, works)
            for part in (*section.path, section.title)
        )
        and section.title.strip().lower() not in gone
        and not any(part.strip().lower() in gone for part in section.path)
    ]
