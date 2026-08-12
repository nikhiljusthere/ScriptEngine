"""Dropping the works a series does not count, at index time.

`non_canon_works:` was read only on the query path, so a game page was filtered
out of a roster and still sat in the index — reachable by search, by a citation,
or by any caller that did not ask for canon.

Everything here runs without a store or a network.
"""

from __future__ import annotations

import pytest

from scriptengine.ingest.canon import (
    discounted_works,
    keep_sections,
    page_is_discounted,
)
from scriptengine.ingest.documents import Edge, Section, WikiPage

WORKS = discounted_works(
    {
        "non_canon_works": [
            "Dragon Ball Heroes",
            "Super Dragon Ball Heroes",
            "Dragon Ball Xenoverse",
            "Dragon Ball Z: Dokkan Battle",
        ]
    }
)


def page(title, categories=(), debuts=()):
    """A page with debut *edges*, which is what the predicate reads.

    The `Debut` fact is one free-text string naming every medium at once —
    `Game: Dragon Ball Heroes Manga: "..." Anime: "..."` — so a page belonging
    wholly to Heroes reads canon on two counts of three. One edge per work is
    the only shape that can be judged.
    """
    return WikiPage(
        title=title,
        url="",
        categories=list(categories),
        edges=[
            Edge(source=title, relation="debut", target=target)
            for target in debuts
        ],
    )


class TestWorks:
    def test_the_declaration_is_read_and_folded(self):
        assert "super dragon ball heroes" in WORKS
        assert "dragon ball xenoverse" in WORKS

    def test_a_series_declaring_none_discounts_none(self):
        assert discounted_works({}) == ()
        assert discounted_works(None) == ()


class TestPages:
    def test_a_page_titled_for_a_discounted_work_goes(self):
        assert page_is_discounted(page("Super Dragon Ball Heroes"), WORKS)

    def test_a_title_prefix_counts(self):
        assert page_is_discounted(
            page("Dragon Ball Heroes: Victory Mission"), WORKS
        )

    def test_a_category_is_enough(self):
        assert page_is_discounted(
            page("Evil Saiyan (chapter)", ["Dragon Ball Heroes manga chapters"]),
            WORKS,
        )

    def test_a_page_debuting_only_in_a_discounted_work_goes(self):
        assert page_is_discounted(
            page("Xeno Goku", debuts=["Dragon Ball Heroes"]),
            WORKS,
        )

    def test_every_debut_not_any(self):
        """`Super Saiyan Blue` names Dragon Ball Heroes among its debuts and
        first appeared in *Resurrection 'F'*. An any-test threw away half of
        Goku's canon forms to catch the Heroes ones."""
        assert not page_is_discounted(
            page(
                "Super Saiyan Blue",
                debuts=["Dragon Ball Heroes", "Resurrection 'F'"],
            ),
            WORKS,
        )

    def test_a_substring_is_never_enough(self):
        """`Dr. Hedo` debuts in *Super Heroes are Born*, a Dragon Ball Super
        chapter. A bare "heroes" test took him out along with `Gamma 1` and
        `Cell Max`."""
        assert not page_is_discounted(
            page("Dr. Hedo", debuts=["Super Heroes are Born"]),
            WORKS,
        )

    def test_a_canon_page_with_no_debut_stays(self):
        assert not page_is_discounted(page("Goku"), WORKS)

    def test_a_series_declaring_nothing_keeps_everything(self):
        assert not page_is_discounted(page("Super Dragon Ball Heroes"), ())


class TestSections:
    def test_a_discounted_subtree_is_dropped_from_a_kept_page(self):
        """`Goku/Biography` is canon and its Super Dragon Ball Heroes subtree,
        seven sagas deep, is not."""
        sections = [
            Section(title="Biography", level=2, index="1"),
            Section(title="Dragon Ball Z", level=3, index="2", path=["Biography"]),
            Section(title="Super Dragon Ball Heroes", level=2, index="3"),
            Section(
                title="Universe Creation Saga",
                level=3,
                index="4",
                path=["Super Dragon Ball Heroes"],
            ),
        ]
        kept = [section.title for section in keep_sections(sections, WORKS)]
        assert kept == ["Biography", "Dragon Ball Z"]

    def test_nothing_is_dropped_without_a_declaration(self):
        sections = [Section(title="Super Dragon Ball Heroes", level=2, index="1")]
        assert len(keep_sections(sections, ())) == 1


class TestCategoriesAreTheLastResort:
    """A category means "appears in", not "belongs to".

    `Super Dragon Ball` is filed under both `Dragon Ball Super` and
    `Dragon Ball Heroes`. Judging a page on its categories deleted it, and
    `All types of Dragon Balls` lost a canon object — db eval 11/11 to 10/11.
    """

    def test_a_debut_outranks_a_category(self):
        assert not page_is_discounted(
            page(
                "Super Dragon Ball",
                categories=["Objects", "Dragon Ball Super", "Dragon Ball Heroes"],
                debuts=["Tournament Preparation", "Dragon Ball Heroes"],
            ),
            WORKS,
        )

    def test_a_page_with_no_debut_falls_back_to_its_categories(self):
        """The game's own episodes and chapters say nothing about a debut,
        so the category is the only thing there is to read."""
        assert page_is_discounted(
            page(
                "A Creeping Shadow! The Mysterious Dr. W!",
                categories=["Dragon Ball Heroes episodes"],
            ),
            WORKS,
        )
