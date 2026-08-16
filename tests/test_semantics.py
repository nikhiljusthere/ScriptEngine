"""Tests for what an entity is, as distinct from where the wiki filed it.

The failure these exist for: asked for the members of the Galactic Frieza Army,
the engine returned 230 pages: 121 characters, but also 37 races, 24
techniques, 18 planets and 6 battles. A planet is not a member of an army.
"""

from __future__ import annotations

import sqlite3

import pytest

from scriptengine.retrieve import semantics
from scriptengine.retrieve.semantics import (
    ensure_lookup_indexes,
    expected_type,
    request_cache,
    semantic_type,
    type_from_class,
    type_from_page_type,
)
from scriptengine.stores.facts import FactStore


class TestTypeFromPageType:
    @pytest.mark.parametrize(
        "page_type,expected",
        [
            # One vocabulary out of four wikis' spellings, matched on the tokens
            # inside the id rather than on a table of ids.
            ("character", semantics.CHARACTER),
            ("char_box", semantics.CHARACTER),
            ("hunterpedia_character", semantics.CHARACTER),
            ("bleach_wiki_character_arrancar", semantics.CHARACTER),
            ("race_infobox2", semantics.RACE),
            ("planet", semantics.LOCATION),
            ("island_box", semantics.LOCATION),
            ("faction", semantics.ORGANIZATION),
            ("crew_box", semantics.ORGANIZATION),
            ("bleach_wiki_zanpakut_technique", semantics.TECHNIQUE),
            ("weapon_box", semantics.ITEM),
            ("conflict", semantics.EVENT),
            ("bleach_wiki_episode", semantics.MEDIA),
            ("volume_box", semantics.MEDIA),
            ("", semantics.UNKNOWN),
            ("something_nobody_has_seen", semantics.UNKNOWN),
        ],
    )
    def test_a_wikis_own_infobox_name_folds_into_the_vocabulary(self, page_type, expected):
        assert type_from_page_type(page_type) == expected

    def test_a_series_can_declare_its_own(self):
        declared = {"semantic_types": {"weird_box": "item"}}
        assert type_from_page_type("weird_box", declared) == semantics.ITEM


class TestTypeFromClass:
    def test_it_separates_a_power_up_from_a_transformation(self):
        """Both sit in `Transformations`; only the `Class` field disagrees."""
        assert type_from_class("Power Up") == semantics.POWER_UP
        assert type_from_class("Transformation") == semantics.TRANSFORMATION

    def test_naming_both_reads_as_the_stronger(self):
        assert type_from_class("Power Up Transformation") == semantics.TRANSFORMATION
        assert type_from_class("Transformation/Power Up") == semantics.TRANSFORMATION


class TestExpectedType:
    def test_the_majority_is_what_the_set_is_made_of(self):
        types = {f"c{index}": semantics.CHARACTER for index in range(8)}
        types["p1"] = semantics.LOCATION
        types["r1"] = semantics.RACE
        assert expected_type(list(types), types) == semantics.CHARACTER

    def test_a_set_with_no_majority_is_left_alone(self):
        """Better to return a mixed set than to guess which half is wrong."""
        types = {"a": semantics.CHARACTER, "b": semantics.ITEM, "c": semantics.EVENT}
        assert expected_type(list(types), types) == semantics.UNKNOWN

    def test_unclassified_members_do_not_vote(self):
        types = {"a": semantics.CHARACTER, "b": semantics.UNKNOWN, "c": semantics.UNKNOWN}
        assert expected_type(list(types), types) == semantics.CHARACTER


# `_disagrees` lives in roster.py and is tested beside it, in
# tests/test_roster_validation.py, and importing it here made this module
# uncollectable at any commit before roster.py grew the function.


def _page(store, title, page_type, facts=()):
    document = store.add_document(
        title=title, url="", page_type=page_type, infobox_template="",
        lead=f"{title} is a thing.", word_count=4, revid=1, fetched_at="",
    )
    node = store.add_node(title, page_type, document)
    for label, value in facts:
        store.add_fact(
            node_id=node, key=label.lower(), label=label, value=value, citation=""
        )
    store.commit()


@pytest.fixture()
def facts_db(tmp_path):
    """A path with a store already written to it, ready to be opened again."""
    path = tmp_path / "facts.db"
    with FactStore(path) as store:
        store.initialise()
        _page(store, "Super Saiyan", "technique", [("Class", "Transformation")])
        _page(store, "Widget", "weird_box")
    return path


@pytest.fixture()
def store(facts_db):
    store = FactStore(facts_db)
    yield store
    store.close()


class Counter:
    """How many statements a connection actually ran."""

    def __init__(self, store):
        self.count = 0
        store.connection.set_trace_callback(self._seen)

    def _seen(self, _statement):
        self.count += 1


class TestMemoisation:
    """Classification is asked the same question repeatedly inside one request.

    `roster.build_roster` classifies every page a character owns, then classifies
    the survivors again inside `apply_constraints`. The answers are memoised per
    store. The tests that matter are the ones about *when the memo dies*, since
    a classification that outlives its corpus is a wrong answer served
    confidently.
    """

    def test_the_second_answer_is_the_first_one(self, store):
        first = semantic_type(store, "Super Saiyan")
        counter = Counter(store)
        second = semantic_type(store, "Super Saiyan")
        assert first == second == semantics.TRANSFORMATION
        assert counter.count == 0, "a memoised answer must not query again"

    def test_a_reopened_store_reads_the_corpus_again(self, facts_db):
        """The guard against a memo outliving the data it was read from.

        `index` rewrites `documents` and `facts` wholesale. A cache keyed on the
        database path would answer the next request out of the previous corpus;
        keyed on the store instance it cannot, because the instance is gone.
        """
        with FactStore(facts_db) as store:
            assert semantic_type(store, "Widget") == semantics.UNKNOWN

        with FactStore(facts_db) as store:
            store.connection.execute(
                "UPDATE documents SET page_type = 'planet' WHERE title = 'Widget'"
            )
            store.commit()

        with FactStore(facts_db) as store:
            assert semantic_type(store, "Widget") == semantics.LOCATION

    def test_two_stores_do_not_share_a_memo(self, facts_db, tmp_path):
        other = tmp_path / "other.db"
        with FactStore(other) as store:
            store.initialise()
            _page(store, "Widget", "planet")

        with FactStore(facts_db) as first, FactStore(other) as second:
            assert semantic_type(first, "Widget") == semantics.UNKNOWN
            assert semantic_type(second, "Widget") == semantics.LOCATION
            assert semantic_type(first, "Widget") == semantics.UNKNOWN

    def test_a_declared_vocabulary_is_part_of_the_question(self, store):
        """Two callers, two `overrides`, two answers, not whichever asked first."""
        declared = {"semantic_types": {"weird_box": "item"}}
        assert semantic_type(store, "Widget") == semantics.UNKNOWN
        assert semantic_type(store, "Widget", declared) == semantics.ITEM
        assert semantic_type(store, "Widget") == semantics.UNKNOWN

    def test_the_same_declaration_written_twice_is_one_question(self, store):
        """Keyed on what the overrides say, not on which dict object said it."""
        assert semantic_type(store, "Widget", {"semantic_types": {"weird_box": "item"}})
        counter = Counter(store)
        assert semantic_type(
            store, "Widget", {"semantic_types": {"Weird_Box": "item"}}
        ) == semantics.ITEM
        assert counter.count == 0

    def test_buckets_do_not_collide(self, store):
        """`roster._profile` keeps its own memo in the same store's cache."""
        request_cache(store, "one")["k"] = 1
        assert request_cache(store, "two") == {}
        assert request_cache(store, "one") == {"k": 1}


class TestLookupIndexes:
    """`title = ? COLLATE NOCASE` against a BINARY unique index is a full scan.

    Measured on `series/db/facts.db`: 1.5ms a lookup across 7,205 rows, and a
    roster asks for hundreds. The collation stays: dropping it would silently
    stop matching a caller whose spelling differs from the stored title, and
    the index is what lets the same query use one.
    """

    def test_an_existing_store_grows_the_index(self, store):
        ensure_lookup_indexes(store)
        names = {
            row[0]
            for row in store.connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'index'"
            )
        }
        assert "idx_documents_title_nocase" in names

    def test_the_query_actually_uses_it(self, store):
        ensure_lookup_indexes(store)
        plan = " ".join(
            str(row[3])
            for row in store.connection.execute(
                "EXPLAIN QUERY PLAN"
                " SELECT page_type FROM documents WHERE title = ? COLLATE NOCASE",
                ("Widget",),
            )
        )
        assert "idx_documents_title_nocase" in plan
        assert "SCAN" not in plan

    def test_it_is_attempted_once_and_is_idempotent(self, store):
        ensure_lookup_indexes(store)
        counter = Counter(store)
        ensure_lookup_indexes(store)
        assert counter.count == 0
        # And creating it on a store that already has it is not an error either.
        with FactStore(store.path) as again:
            ensure_lookup_indexes(again)

    def test_a_store_that_cannot_be_written_still_answers(self, store):
        """A read-only or locked store gets the slow answer, never no answer."""
        store.connection.close()
        store.connection = sqlite3.connect(f"file:{store.path}?mode=ro", uri=True)
        store.connection.row_factory = sqlite3.Row
        assert semantic_type(store, "Super Saiyan") == semantics.TRANSFORMATION


class TestStatedCount:
    """A set whose name counts itself is a free assertion to check.

    Most of what it finds is not a defect: `Gotei 13` holds 127 because the 13
    counts divisions, and `Seven Warlords` holds 12 because twelve people held
    seven seats. The check earns its place anyway: it also finds duplicate pages
    for one entity, which is a real error.
    """

    def test_it_reads_digits_and_words(self):
        from scriptengine.cli import _stated_count

        assert _stated_count("Gotei 13") == 13
        assert _stated_count("Seven Warlords of the Sea") == 7
        assert _stated_count("Zodiac Twelve") == 12

    def test_a_number_inside_a_word_is_not_a_count(self):
        """`Extension Techniques` contains "ten" and states nothing."""
        from scriptengine.cli import _stated_count

        assert _stated_count("Extension Techniques") is None
        assert _stated_count("Transformations") is None


class TestCategoryFallback:
    """One Punch Man wraps character pages in a tabber, so the infobox the
    crawler finds is the tab container and `page_type` is `parent_tab`.

    271 pages are like that, Saitama and Garou among them, and everything
    filtering on "is this a character" dropped the entire main cast:
    `Monster Association Arc` returned 119 names with no Saitama in it.
    """

    def paths_for(self, series):
        from scriptengine.config import series_paths

        paths = series_paths(series)
        if not paths.facts_db.exists():
            pytest.skip(f"{series} is not indexed")
        return paths

    @pytest.mark.parametrize(
        "name", ["Saitama", "Garou", "Genos", "Bang", "Tatsumaki", "King"]
    )
    def test_tabbed_character_pages_are_characters(self, name):
        from scriptengine.config import load_overrides
        from scriptengine.retrieve import semantics as ontology
        from scriptengine.stores.facts import FactStore

        paths = self.paths_for("opm")
        with FactStore(paths.facts_db) as store:
            assert ontology.semantic_type(store, name, load_overrides(paths)) == (
                ontology.CHARACTER
            )

    @pytest.mark.parametrize("name", ["Audiobooks", "Awakened Garou vs. S-Class Heroes (Webcomic)"])
    def test_other_tabbed_pages_are_not_promoted(self, name):
        """`Audiobooks` is in `Audiobooks`; the fight pages are in `Fights`."""
        from scriptengine.config import load_overrides
        from scriptengine.retrieve import semantics as ontology
        from scriptengine.stores.facts import FactStore

        paths = self.paths_for("opm")
        with FactStore(paths.facts_db) as store:
            assert ontology.semantic_type(store, name, load_overrides(paths)) != (
                ontology.CHARACTER
            )

    @pytest.mark.parametrize(
        "series, title",
        [
            ("jjk", "List of Characters"),
            ("bleach", "Characters/Arrancar"),
            ("berserk", "Miscellaneous Characters"),
        ],
    )
    def test_an_index_of_characters_is_not_a_character(self, series, title):
        """These sit in `Characters` and are indexes, not people.

        A character page is not named after its own category, which is the
        whole discriminator.
        """
        from scriptengine.config import load_overrides
        from scriptengine.retrieve import semantics as ontology
        from scriptengine.stores.facts import FactStore

        paths = self.paths_for(series)
        with FactStore(paths.facts_db) as store:
            assert ontology.semantic_type(store, title, load_overrides(paths)) != (
                ontology.CHARACTER
            )


class TestIndexPagesAreNotPeople:
    """An index is named after the group it indexes.

    `Heroes` is filed under `Characters` and is the list of every hero. It is
    also a category on that wiki, which is what tells it apart from
    `Empty Void` and `Beaut`, real characters filed exactly the same way.
    """

    def paths_for(self, series):
        from scriptengine.config import series_paths

        paths = series_paths(series)
        if not paths.facts_db.exists():
            pytest.skip(f"{series} is not indexed")
        return paths

    def test_a_page_named_after_a_category_is_an_index(self):
        from scriptengine.config import load_overrides
        from scriptengine.retrieve import semantics as ontology
        from scriptengine.stores.facts import FactStore

        paths = self.paths_for("opm")
        with FactStore(paths.facts_db) as store:
            overrides = load_overrides(paths)
            assert ontology.semantic_type(store, "Heroes", overrides) != (
                ontology.CHARACTER
            )
            # Filed the same way, not named after a category, and real people.
            for name in ("Empty Void", "Beaut"):
                assert ontology.semantic_type(store, name, overrides) == (
                    ontology.CHARACTER
                )

    def test_an_index_is_not_in_an_arc_cast(self):
        from scriptengine.config import load_overrides
        from scriptengine.retrieve import chronology
        from scriptengine.stores.facts import FactStore

        paths = self.paths_for("opm")
        with FactStore(paths.facts_db) as store:
            who = chronology.cast(
                store, "Monster Association Arc", load_overrides(paths)
            )
        assert "Heroes" not in who
        assert "Saitama" in who and "Garou" in who
