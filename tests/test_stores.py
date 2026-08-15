"""Tests for the fact store, graph traversal and lexical search."""

from __future__ import annotations

import pytest

from scriptengine.stores import lexical
from scriptengine.stores.facts import FactStore


@pytest.fixture()
def store(tmp_path):
    store = FactStore(tmp_path / "facts.db")
    store.initialise()
    yield store
    store.close()


@pytest.fixture()
def populated(store):
    """A small graph: Todo studies at Kyoto High and befriends Yuji."""
    todo_doc = store.add_document(
        title="Aoi Todo", url="", page_type="character", infobox_template="Character Infobox",
        lead="Aoi Todo is a sorcerer.", word_count=4, revid=1, fetched_at="",
    )
    yuji_doc = store.add_document(
        title="Yuji Itadori", url="", page_type="character", infobox_template="Character Infobox",
        lead="Yuji Itadori is a sorcerer.", word_count=4, revid=1, fetched_at="",
    )

    todo = store.add_node("Aoi Todo", "character", todo_doc)
    yuji = store.add_node("Yuji Itadori", "character", yuji_doc)
    kyoto = store.add_node("Kyoto Metropolitan Curse Technical College", "location")

    store.add_aliases(todo, ["Aoi Todo", "Todo"])
    store.add_aliases(yuji, ["Yuji Itadori", "Yuji", "Itadori"])
    store.add_aliases(kyoto, ["Kyoto Metropolitan Curse Technical College", "Kyoto Jujutsu High"])

    store.add_edge(
        source_id=todo, relation="affiliation", target_id=kyoto,
        confidence=0.95, provenance="infobox", section="Affiliation",
    )
    store.add_edge(
        source_id=yuji, relation="affiliation", target_id=kyoto,
        confidence=0.95, provenance="infobox", section="Affiliation",
    )
    store.add_fact(node_id=todo, key="class", label="Grade", value="Grade 1", citation="")

    chunk = store.add_chunk(
        document_id=todo_doc, section_id=None, parent_id=None, level=2, ordinal=0,
        doc_title="Aoi Todo", breadcrumb="Abilities / Cursed Technique",
        text="Boogie Woogie lets Todo switch the positions of two targets by clapping.",
    )
    store.link_chunk_nodes(chunk, [todo])
    store.add_chunk(
        document_id=yuji_doc, section_id=None, parent_id=None, level=2, ordinal=0,
        doc_title="Yuji Itadori", breadcrumb="Abilities",
        text="Yuji Itadori has immense physical strength and hosts Sukuna.",
    )
    store.rebuild_fts()
    store.commit()
    return {"store": store, "todo": todo, "yuji": yuji, "kyoto": kyoto}


class TestSchema:
    def test_a_fresh_store_is_empty(self, store):
        assert store.counts()["documents"] == 0

    def test_reset_is_idempotent(self, populated):
        store = populated["store"]
        store.reset()
        assert store.counts()["nodes"] == 0


class TestNodes:
    def test_a_node_is_created_once(self, store):
        first = store.add_node("Aoi Todo", "character")
        assert store.add_node("Aoi Todo", "character") == first

    def test_a_later_bare_mention_does_not_erase_a_real_type(self, store):
        # A link target is often seen before the page backing it is indexed;
        # the reverse order must not downgrade what is already known.
        node = store.add_node("Aoi Todo", "character", document_id=None)
        store.add_node("Aoi Todo", "unknown")
        row = store.node_by_name("Aoi Todo")
        assert row["label"] == "character"
        assert row["id"] == node

    def test_an_unresolved_node_is_flagged(self, store):
        store.add_node("Some Uncrawled Page")
        assert store.node_by_name("Some Uncrawled Page")["is_resolved"] == 0


class TestEntityLinking:
    def test_an_alias_reaches_its_page(self, populated):
        found = populated["store"].link_entities("What grade is Todo?")
        assert "Aoi Todo" in {row["name"] for row in found}

    def test_a_multiword_alias_is_matched(self, populated):
        found = populated["store"].link_entities("Tell me about Kyoto Jujutsu High.")
        assert "Kyoto Metropolitan Curse Technical College" in {r["name"] for r in found}

    def test_matching_is_on_whole_words(self, populated):
        # The previous implementation asked `entity.lower() in text.lower()`,
        # so "Todo" matched inside "Todoroki" and the false tag then removed
        # correct chunks from the filtered vector search.
        found = populated["store"].link_entities("Shoto Todoroki is from another series.")
        assert "Aoi Todo" not in {row["name"] for row in found}

    def test_unrelated_text_links_nothing(self, populated):
        assert populated["store"].link_entities("completely unrelated sentence") == []


class TestGraph:
    def test_one_hop_finds_a_direct_relation(self, populated):
        neighbours = populated["store"].neighbours([populated["todo"]], depth=1)
        assert "Kyoto Metropolitan Curse Technical College" in {
            row["name"] for row in neighbours
        }

    def test_two_hops_finds_a_shared_affiliation(self, populated):
        # Todo -> Kyoto High <- Yuji. This is the traversal the previous code
        # could never perform: its Cypher used `[r*1..$depth]`, which Neo4j
        # rejects, so graph retrieval failed at runtime.
        neighbours = populated["store"].neighbours([populated["todo"]], depth=2)
        names = {row["name"] for row in neighbours}
        assert "Yuji Itadori" in names

    def test_traversal_is_bidirectional(self, populated):
        neighbours = populated["store"].neighbours([populated["kyoto"]], depth=1)
        assert "Aoi Todo" in {row["name"] for row in neighbours}

    def test_hop_count_is_reported(self, populated):
        by_name = {
            row["name"]: row["hops"]
            for row in populated["store"].neighbours([populated["todo"]], depth=2)
        }
        assert by_name["Kyoto Metropolitan Curse Technical College"] == 1
        assert by_name["Yuji Itadori"] == 2

    def test_weak_edges_can_be_excluded(self, populated):
        store = populated["store"]
        loose = store.add_node("Passing Mention")
        store.add_edge(
            source_id=populated["todo"], relation="mentions", target_id=loose,
            confidence=0.4, provenance="prose", section="Trivia",
        )
        store.commit()
        strong = store.neighbours([populated["todo"]], depth=1, min_confidence=0.9)
        assert "Passing Mention" not in {row["name"] for row in strong}

    def test_no_seed_entities_returns_nothing(self, populated):
        assert populated["store"].neighbours([], depth=2) == []


class TestFacts:
    def test_a_fact_lookup_is_exact(self, populated):
        facts = {row["key"]: row["value"] for row in populated["store"].facts_for("Aoi Todo")}
        assert facts["class"] == "Grade 1"

    def test_the_wikis_own_label_is_kept(self, populated):
        (fact,) = populated["store"].facts_for("Aoi Todo")
        assert fact["label"] == "Grade"


class TestLexicalSearch:
    def test_a_technique_name_is_found(self, populated):
        results = lexical.search(populated["store"], "Boogie Woogie", limit=5)
        assert results and results[0]["doc_title"] == "Aoi Todo"

    def test_scores_are_higher_is_better(self, populated):
        # FTS5's bm25() is negative-is-better; every retriever in this system
        # must agree on direction or fusion has to special-case one of them.
        results = lexical.search(populated["store"], "Boogie Woogie", limit=5)
        assert results[0]["lexical_score"] > 0

    def test_query_punctuation_does_not_raise(self, populated):
        # Unescaped, this is an FTS5 syntax error rather than a search.
        assert lexical.search(populated["store"], 'Sukuna\'s "Domain" (expansion)') is not None

    def test_partial_matches_still_return(self, populated):
        results = lexical.search(populated["store"], "who can switch positions of targets")
        assert any(r["doc_title"] == "Aoi Todo" for r in results)

    def test_an_empty_query_returns_nothing(self, populated):
        assert lexical.search(populated["store"], "   ") == []

    def test_only_the_requested_level_is_searched(self, populated):
        assert lexical.search(populated["store"], "Boogie Woogie", level=0) == []


# `pages_per_section` used to issue one query per heading, each of them a full
# scan because `LOWER(TRIM(breadcrumb))` hides the column from every index: 64
# headings cost 3.9s on the Dragon Ball store. These tests hold both halves of
# the fix — that it stays one query, and that one query still answers exactly
# what the per-heading pair of predicates answered.
_PER_HEADING_SQL = (
    "SELECT COUNT(DISTINCT c.document_id) AS pages FROM chunks c"
    " WHERE LOWER(TRIM(c.breadcrumb)) = ?"
    "    OR LOWER(TRIM(c.breadcrumb)) LIKE ?"
)

# Breadcrumbs chosen to exercise what makes this query awkward: a heading shared
# by many pages, one repeated within a page, nesting deeper than one level, a
# LIKE wildcard inside a real heading, and a capital SQLite's LOWER cannot fold.
_BREADCRUMBS = {
    "Goku": [
        "Abilities",
        "Abilities / Physical Abilities",
        "Abilities / Physical Abilities",   # twice on one page: still one page
        "Abilities / Forms / Super Saiyan Blue",
        "Trivia",
    ],
    "Vegeta": [
        "Abilities",
        "Abilities / Physical Abilities",
        "Abilities / Forms / Super Saiyan Blue",
    ],
    "Frieza": [
        "Abilities",
        "Abilities / Forms and Transformations / 100% Full Power",
    ],
    "Cooler": [
        "Abilities / Forms and Transformations / 100 Percent, Full Power",
    ],
    "Ichigo": [
        "Zanpakutō",
        "Powers / Zanpakutō",
        "Staff / Hiroshi Ōtake",
    ],
    "Krillin": ["Abilities", "Trivia"],
}


@pytest.fixture()
def sectioned(store):
    """Five pages whose section headings repeat the way a wiki's do."""
    for ordinal, (title, breadcrumbs) in enumerate(_BREADCRUMBS.items()):
        document = store.add_document(
            title=title, url="", page_type="character", infobox_template="",
            lead="", word_count=0, revid=1, fetched_at="",
        )
        for position, breadcrumb in enumerate(breadcrumbs):
            store.add_chunk(
                document_id=document, section_id=None, parent_id=None,
                level=2, ordinal=position, doc_title=title,
                breadcrumb=breadcrumb, text=f"{title} {breadcrumb}",
            )
    store.commit()
    return store


class TestPagesPerSection:
    def test_a_template_heading_counts_every_page_carrying_it(self, sectioned):
        # `Abilities` is the article skeleton — four of the five pages have it,
        # which is the signal `_drop_templates` reads.
        assert sectioned.pages_per_section(["Abilities"]) == {"abilities": 4}

    def test_a_heading_is_counted_once_per_page_not_once_per_chunk(self, sectioned):
        # Goku carries `Physical Abilities` on two chunks. Counting rows rather
        # than pages would say three.
        assert sectioned.pages_per_section(["Physical Abilities"]) == {
            "physical abilities": 2
        }

    def test_a_heading_matches_at_any_depth(self, sectioned):
        assert sectioned.pages_per_section(["Super Saiyan Blue"]) == {
            "super saiyan blue": 2
        }

    def test_headings_are_matched_case_and_space_insensitively(self, sectioned):
        assert sectioned.pages_per_section(["  ABILITIES  "]) == {"abilities": 4}

    def test_a_heading_absent_from_the_store_is_still_keyed(self, sectioned):
        # `_drop_templates` reads the count back by name, so a missing heading
        # has to come back as zero rather than not come back at all.
        assert sectioned.pages_per_section(["Nen"]) == {"nen": 0}

    def test_no_headings_asks_nothing(self, sectioned):
        assert sectioned.pages_per_section([]) == {}
        assert sectioned.pages_per_section(["", "   "]) == {}

    def test_a_percent_in_a_heading_keeps_its_LIKE_meaning(self, sectioned):
        # `100% Full Power` is a real Frieza form, and `%` is a LIKE wildcard, so
        # the query this replaced reached Cooler's `100 Percent, Full Power` too
        # — only one of these two pages spells the heading literally. Inherited
        # behaviour, pinned here because the obvious way to write the
        # replacement, a plain `endswith`, would answer 1 instead.
        assert sectioned.pages_per_section(["100% Full Power"]) == {
            "100% full power": 2
        }

    def test_case_folding_stays_ASCII_only(self, sectioned):
        # SQLite's LOWER folds ASCII and stops, so the stored `Hiroshi Ōtake`
        # normalises to `hiroshi Ōtake` and a Python-lowered `ōtake` does not
        # reach it. Folding the crumb in Python would silently change the count.
        assert sectioned.pages_per_section(["Hiroshi Ōtake"]) == {
            "hiroshi ōtake": 0
        }
        # Ichigo carries `Zanpakutō` bare and again under `Powers`; the two arms
        # of the predicate hit the same page, and it counts once.
        assert sectioned.pages_per_section(["Zanpakutō"]) == {"zanpakutō": 1}

    @pytest.mark.parametrize(
        "heading",
        [
            "Abilities", "abilities", "Physical Abilities", "Super Saiyan Blue",
            "Forms", "Forms and Transformations", "100% Full Power", "100% Power",
            "Zanpakutō", "Hiroshi Ōtake", "Trivia", "Staff", "Nen",
            "Powers / Zanpakutō", "%", "_", "a_b", "Goku",
        ],
    )
    def test_it_answers_what_the_per_heading_query_answered(self, sectioned, heading):
        """The old loop, run one heading at a time, is the oracle.

        Keeping it here means the aggregation cannot drift away from the SQL it
        replaced without a test naming the heading where it happened.
        """
        leaf = heading.strip().lower()
        expected = sectioned.connection.execute(
            _PER_HEADING_SQL, (leaf, f"%/ {leaf}")
        ).fetchone()["pages"]
        assert sectioned.pages_per_section([heading]) == {leaf: expected}

    def test_the_work_does_not_grow_with_the_number_of_headings(self, sectioned):
        """One query for one heading, and the same one query for two hundred.

        This is the regression that matters. The implementation this replaced
        was correct and unusably slow: it scanned all 68,904 chunk rows once per
        heading, so a 64-heading roster spent 4.6 seconds of a 7.5 second
        request here. Anything that reintroduces a per-heading query fails here
        long before it reaches a profiler.
        """
        statements: list[str] = []
        sectioned.connection.set_trace_callback(statements.append)
        try:
            sectioned.pages_per_section(["Abilities"])
            for_one = len(statements)

            statements.clear()
            many = [f"Heading {index}" for index in range(200)] + ["Abilities"]
            counts = sectioned.pages_per_section(many)
            for_many = len(statements)
        finally:
            sectioned.connection.set_trace_callback(None)

        assert for_one == 1, f"one heading should be one query, got {statements}"
        assert for_many == for_one, (
            f"{len(many)} headings issued {for_many} queries, one heading issued"
            f" {for_one} — the per-heading scan is back"
        )
        assert counts["abilities"] == 4          # and the answer is still right
        assert counts["heading 7"] == 0
        assert len(counts) == len(many)
