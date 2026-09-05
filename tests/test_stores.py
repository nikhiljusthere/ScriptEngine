"""Tests for the fact store, graph traversal and lexical search."""

from __future__ import annotations

import pytest

from scriptengine.index.chunker import sentence_content_hash
from scriptengine.stores import lexical
from scriptengine.stores.facts import FactStore, ResetRefusedError


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


class TestPassagesForSubject:
    """The entity-anchored recall floor (R6): the subject page's own passages,
    in the wiki's section order, by title or alias lookup -- not by
    similarity. A subject that resolves to no document yields an empty list
    and the caller's ranked behaviour stands unchanged."""

    def test_a_title_resolution_returns_the_pages_passages_in_order(self, populated):
        rows = populated["store"].passages_for_subject("Aoi Todo")
        assert [row["text"] for row in rows] == [
            "Boogie Woogie lets Todo switch the positions of two targets by clapping."
        ]

    def test_case_and_spacing_do_not_break_the_title_lookup(self, populated):
        rows = populated["store"].passages_for_subject("  aoi todo ")
        assert [row["doc_title"] for row in rows] == ["Aoi Todo"]

    def test_an_alias_reaches_the_page(self, populated):
        # No document is titled `Todo`; the editor alias is the fallback.
        rows = populated["store"].passages_for_subject("Todo")
        assert [row["doc_title"] for row in rows] == ["Aoi Todo"]

    def test_a_subject_that_resolves_to_nothing_yields_nothing(self, populated):
        store = populated["store"]
        assert store.passages_for_subject("Never Crawled Page") == []
        assert store.passages_for_subject("") == []
        assert store.passages_for_subject(None) == []


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
# the fix: that it stays one query, and that one query still answers exactly
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
        # `Abilities` is the article skeleton: four of the five pages have it,
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
        # Only one of these two pages spells the heading literally. Inherited
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
            f" {for_one}: the per-heading scan is back"
        )
        assert counts["abilities"] == 4          # and the answer is still right
        assert counts["heading 7"] == 0
        assert len(counts) == len(many)


class TestEventsForeignKeys:
    """The events table is a child of the graph, so it dies with it."""

    # One section, shared by the remap tests: the text and the quote are the
    # same pair `remap_derived` re-checks, so a row survives a rebuild only
    # while the section still says what the row says.
    SECTION_TEXT = "Aoi Todo arrived in the courtyard and faced the curse head on."
    QUOTE = "Aoi Todo arrived in the courtyard"

    def _section(self, store, document_id, text=SECTION_TEXT):
        return store.add_section(
            document_id=document_id, title="History", breadcrumb="History",
            level=1, ordinal=0, text=text, word_count=len(text.split()),
        )

    def _document(self, store, title):
        return store.connection.execute(
            "SELECT id FROM documents WHERE title = ?", (title,)
        ).fetchone()[0]

    def _save(self, store, todo, yuji, section_id, time_rank=1.0, quote=QUOTE, revid=1):
        return store.save_events(
            "Test Arc",
            [{
                "subject_node": todo, "subject_name": "Aoi Todo",
                "object_node": yuji, "object_name": "Yuji Itadori",
                "verb": "fights", "section_id": section_id, "time_rank": time_rank,
                "quote": quote,
            }],
            revid=revid, prompt_version="test", model="test",
        )

    def _rebuild(self, store, revid=1, section_text=SECTION_TEXT, add_nodes=True):
        """Re-run the base load after a reset: same doc / section /
        participants, fresh ids. ``section_text`` lets a test move the
        section's content under a parser fix."""
        new_document_id = store.add_document(
            title="Aoi Todo", url="", page_type="character",
            infobox_template="Character Infobox", lead="Aoi Todo is a sorcerer.",
            word_count=4, revid=revid, fetched_at="",
        )
        new_section_id = self._section(store, new_document_id, text=section_text)
        nodes = {}
        if add_nodes:
            nodes["todo"] = store.add_node("Aoi Todo", "character", new_document_id)
            nodes["yuji"] = store.add_node("Yuji Itadori", "character")
        return new_document_id, new_section_id, nodes

    def test_a_fresh_table_references_nodes_and_sections(self, store):
        assert store.ensure_events() == 0
        refs = {
            (row["table"], row["from"], row["on_delete"])
            for row in store.connection.execute("PRAGMA foreign_key_list(events)")
        }
        assert ("nodes", "subject_node", "CASCADE") in refs
        assert ("nodes", "object_node", "CASCADE") in refs
        assert ("sections", "section_id", "CASCADE") in refs

    def test_rebuilding_the_graph_drops_the_events(self, populated):
        # The exact hazard: an `index` run renumbers `sections`; without the
        # FK the events would keep pointing at the old ids.
        store = populated["store"]
        section_id = self._section(store, self._document(store, "Aoi Todo"))
        assert self._save(store, populated["todo"], populated["yuji"], section_id) == 1
        store.connection.execute("DROP TABLE sections")
        assert (
            store.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
            == 0
        )

    def test_reset_drops_the_events(self, populated):
        # A bare reset() drops the events table (returning its rows as a
        # snapshot, for `remap_derived` to re-key onto a new build) and brings
        # the table back with the schema, FKs and all, so the unguarded readers
        # keep working. A real `index` rebuild (build_index) does the snapshot
        # + remap, so the rows survive -- see the remap test below.
        store = populated["store"]
        section_id = self._section(store, self._document(store, "Aoi Todo"))
        assert self._save(store, populated["todo"], populated["yuji"], section_id) == 1
        store.reset()
        assert (
            store.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
            == 0
        )
        assert store.connection.execute(
            "PRAGMA foreign_key_list(events)"
        ).fetchall()
        # and the next `ensure_events` sees an FK table and migrates nothing
        assert store.ensure_events() == 0

    def test_require_rebuild_refuses_a_non_forced_rebuild(self, populated):
        # The 0B guard: a non-forced rebuild is refused while `events` is
        # non-empty, so a reflexive `index` never destroys the extraction pass.
        store = populated["store"]
        section_id = self._section(store, self._document(store, "Aoi Todo"))
        assert self._save(store, populated["todo"], populated["yuji"], section_id) == 1
        with pytest.raises(ResetRefusedError):
            store.require_rebuild()
        # An empty derived layer passes the guard.
        store.connection.execute("DELETE FROM events")
        assert store.require_rebuild() is None

    def test_a_forced_rebuild_remaps_the_events(self, populated):
        # The 0C durable key: a rebuild renumbers the section/node ids, but the
        # events' durable key (doc_title, section_ordinal, participant names)
        # still resolves, so the row survives re-keyed onto the new graph.
        store = populated["store"]
        section_id = self._section(store, self._document(store, "Aoi Todo"))
        assert self._save(store, populated["todo"], populated["yuji"], section_id) == 1

        store.require_rebuild(force=True)
        snapshot = store.reset()
        assert len(snapshot["events"]) == 1

        # Simulate the rebuild: the same document / section / participants come
        # back under fresh ids, the document's revid unchanged (not stale), and
        # the section's text unchanged (verified).
        _, new_section_id, nodes = self._rebuild(store)

        report = store.remap_derived(snapshot)
        assert report["events"] == {
            "before": 1, "remapped": 1, "stale": 0, "orphaned": 0,
            "unverified": 0,
        }
        row = store.connection.execute(
            "SELECT section_id, subject_node, object_node,"
            " subject_name, object_name FROM events"
        ).fetchone()
        assert row["section_id"] == new_section_id
        assert row["subject_node"] == nodes["todo"]
        assert row["object_node"] == nodes["yuji"]
        assert row["subject_name"] == "Aoi Todo"
        assert row["object_name"] == "Yuji Itadori"

    def test_remap_drops_a_row_its_document_revid_changed(self, populated):
        # The stale branch: the source document was re-crawled since the
        # extraction, so its revid moved. The row's text no longer matches and
        # it is dropped, not re-keyed onto a document it was never read from.
        store = populated["store"]
        section_id = self._section(store, self._document(store, "Aoi Todo"))
        assert self._save(store, populated["todo"], populated["yuji"], section_id) == 1

        store.require_rebuild(force=True)
        snapshot = store.reset()
        self._rebuild(store, revid=2)

        report = store.remap_derived(snapshot)
        assert report["events"] == {
            "before": 1, "remapped": 0, "stale": 1, "orphaned": 0,
            "unverified": 0,
        }
        assert store.connection.execute(
            "SELECT COUNT(*) FROM events"
        ).fetchone()[0] == 0

    def test_a_null_revid_row_survives_a_rebuild(self, populated):
        # The live shape: a crawl revid of 0 is stored as NULL, so every JJK
        # row carries a NULL revid. The stale check must skip such a row --
        # there is no recorded revid that could have moved, and the
        # unverified check (the quote must still sit in the section) is what
        # guards it. Without the NULL guard, the first forced rebuild after
        # any re-crawl would mark the whole layer stale and wipe it.
        store = populated["store"]
        section_id = self._section(store, self._document(store, "Aoi Todo"))
        assert self._save(
            store, populated["todo"], populated["yuji"], section_id, revid=None
        ) == 1
        assert (
            store.connection.execute("SELECT revid FROM events").fetchone()[0]
            is None
        )

        store.require_rebuild(force=True)
        snapshot = store.reset()
        self._rebuild(store, revid=2)

        report = store.remap_derived(snapshot)
        assert report["events"] == {
            "before": 1, "remapped": 1, "stale": 0, "orphaned": 0,
            "unverified": 0,
        }

    def test_remap_drops_a_row_whose_section_vanished(self, populated):
        # The orphaned branch: the rebuild kept no "Aoi Todo" page at all, so
        # the durable key (doc_title, section_ordinal) resolves to nothing and
        # the row has nowhere to sit.
        store = populated["store"]
        section_id = self._section(store, self._document(store, "Aoi Todo"))
        assert self._save(store, populated["todo"], populated["yuji"], section_id) == 1

        store.require_rebuild(force=True)
        snapshot = store.reset()
        # The rebuild dropped the page: a different document comes back instead.
        other_document_id = store.add_document(
            title="Sukuna", url="", page_type="character",
            infobox_template="Character Infobox", lead="Sukuna is a curse.",
            word_count=4, revid=1, fetched_at="",
        )
        self._section(store, other_document_id)

        report = store.remap_derived(snapshot)
        assert report["events"] == {
            "before": 1, "remapped": 0, "stale": 0, "orphaned": 1,
            "unverified": 0,
        }
        assert store.connection.execute(
            "SELECT COUNT(*) FROM events"
        ).fetchone()[0] == 0

    def test_remap_drops_a_row_its_section_no_longer_says_it(self, populated):
        # The unverified branch: the section resolved -- same doc, same
        # ordinal, even the same revid -- but a parser fix moved its content,
        # so the row's quote no longer occurs in it. Ordinals are assigned by
        # enumeration, so this shift costs no revid change: the quote is the
        # only thing that proves the row still belongs here. It does not, so
        # the row is dropped for re-extraction, never re-attributed to text
        # that does not say it.
        store = populated["store"]
        section_id = self._section(store, self._document(store, "Aoi Todo"))
        assert self._save(store, populated["todo"], populated["yuji"], section_id) == 1

        store.require_rebuild(force=True)
        snapshot = store.reset()
        self._rebuild(store, section_text="The battle raged through the night.")

        report = store.remap_derived(snapshot)
        assert report["events"] == {
            "before": 1, "remapped": 0, "stale": 0, "orphaned": 0,
            "unverified": 1,
        }
        assert store.connection.execute(
            "SELECT COUNT(*) FROM events"
        ).fetchone()[0] == 0

    def test_remap_drops_a_row_with_no_quote(self, populated):
        # A row stored without a verbatim quote cannot be re-verified against
        # any section, so a rebuild drops it rather than guess its section.
        store = populated["store"]
        section_id = self._section(store, self._document(store, "Aoi Todo"))
        assert self._save(
            store, populated["todo"], populated["yuji"], section_id, quote=""
        ) == 1

        store.require_rebuild(force=True)
        snapshot = store.reset()
        self._rebuild(store)

        report = store.remap_derived(snapshot)
        assert report["events"]["unverified"] == 1
        assert store.connection.execute(
            "SELECT COUNT(*) FROM events"
        ).fetchone()[0] == 0

    def test_a_crashed_rebuild_recovers_the_rows_from_the_snapshot_file(self, populated):
        # The crash-recovery path: a build that dies between `reset` (which has
        # already dropped the derived tables) and the remap used to wipe the
        # extraction rows for good. `reset` writes the snapshot to a file
        # beside the database, and a re-run -- which finds the derived layers
        # empty, so the guard lets it through, and whose own reset must not
        # clobber the file -- recovers the rows from it.
        store = populated["store"]
        section_id = self._section(store, self._document(store, "Aoi Todo"))
        assert self._save(store, populated["todo"], populated["yuji"], section_id) == 1

        store.require_rebuild(force=True)
        store.reset()  # drops the tables, writes the snapshot file
        # -- the build dies here; the base load and the remap never ran --

        # The re-run: the guard passes on the empty layers, and its own reset
        # must leave the crash snapshot in place.
        store.require_rebuild()
        store.reset()
        assert store._snapshot_path().exists()

        self._rebuild(store)
        report = store.remap_derived()  # no in-memory snapshot: the file

        assert report["events"] == {
            "before": 1, "remapped": 1, "stale": 0, "orphaned": 0,
            "unverified": 0,
        }
        assert not store._snapshot_path().exists()

    def test_a_legacy_table_backfills_a_dangling_section(self, populated):
        # D3: a pre-durable-key table carries a row whose section no longer
        # resolves. The backfill must keep its NOT NULL columns honest through
        # the dangling section (the COALESCE holds the defaults; a bare
        # subquery would assign NULL, raise IntegrityError and block the
        # rebuild), and hand the row to the FK migration, which drops it as
        # orphaned -- the same fate its dangling ref already gave it.
        store = populated["store"]
        todo, yuji = populated["todo"], populated["yuji"]
        section_id = self._section(store, self._document(store, "Aoi Todo"))
        store.connection.execute("DROP TABLE events")
        store.connection.execute(
            "CREATE TABLE events ("
            " subject_node INTEGER, subject_name TEXT, object_node INTEGER,"
            " object_name TEXT, verb TEXT, arc_key TEXT, section_id INTEGER,"
            " quote TEXT, temporal INTEGER, time_rank REAL, arc_index INTEGER,"
            " revid INTEGER, prompt_version TEXT, model TEXT, extracted_at TEXT,"
            " PRIMARY KEY (subject_node, verb, object_node, section_id, time_rank))"
        )
        for time_rank, section in ((1.0, section_id), (2.0, 999999)):
            store.connection.execute(
                "INSERT INTO events"
                " (subject_node, subject_name, object_node, object_name, verb,"
                "  arc_key, section_id, temporal, time_rank, revid, prompt_version,"
                "  model, extracted_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, 1, 'test', 'test', '')",
                (todo, "Aoi Todo", yuji, "Yuji Itadori", "fights",
                 "Test Arc", section, time_rank),
            )
        assert store.ensure_events() == 1
        row = store.connection.execute(
            "SELECT section_id, doc_title, section_ordinal FROM events"
        ).fetchone()
        assert row["section_id"] == section_id
        assert row["doc_title"] == "Aoi Todo"
        assert row["section_ordinal"] == 0


class TestMeaningRemap:
    """The `meaning` layer is a child of the graph too: its durable key plus
    the sentence's content hash carry it across a rebuild."""

    TEXT = "Aoi Todo arrived in the courtyard. He faced the curse head on."
    REVERSED = "He faced the curse head on. Aoi Todo arrived in the courtyard."

    def _section(self, store, document_id, text=TEXT):
        return store.add_section(
            document_id=document_id, title="History", breadcrumb="History",
            level=1, ordinal=0, text=text, word_count=len(text.split()),
        )

    def _document(self, store, title):
        return store.connection.execute(
            "SELECT id FROM documents WHERE title = ?", (title,)
        ).fetchone()[0]

    def _meaning(self, store, section_id, sentence_ordinal, sentence, revid=1):
        store.connection.execute(
            "INSERT INTO meaning (section_id, sentence_ordinal, content_hash,"
            " class, is_event, participants, arc_index, chapter,"
            " doc_title, section_ordinal, revid, prompt_version, model, extracted_at)"
            " VALUES (?, ?, ?, 'trivia', 0, NULL, NULL, NULL,"
            " 'Aoi Todo', 0, ?, 'test', 'test', '')",
            (section_id, sentence_ordinal, sentence_content_hash(sentence), revid),
        )

    def _rebuild(self, store, revid=1, text=TEXT):
        document_id = store.add_document(
            title="Aoi Todo", url="", page_type="character",
            infobox_template="Character Infobox", lead="Aoi Todo is a sorcerer.",
            word_count=4, revid=revid, fetched_at="",
        )
        return self._section(store, document_id, text=text)

    def test_a_forced_rebuild_remaps_a_meaning_row(self, populated):
        # Unchanged section, unchanged revid: the sentence's hash sits at the
        # same ordinal it was read from, so the row survives re-keyed.
        store = populated["store"]
        section_id = self._section(store, self._document(store, "Aoi Todo"))
        self._meaning(store, section_id, 1, "He faced the curse head on.")

        store.require_rebuild(force=True)
        snapshot = store.reset()
        assert len(snapshot["meaning"]) == 1
        self._rebuild(store)

        report = store.remap_derived(snapshot)
        assert report["meaning"] == {
            "before": 1, "remapped": 1, "stale": 0, "orphaned": 0,
            "unverified": 0,
        }
        row = store.connection.execute(
            "SELECT sentence_ordinal, content_hash FROM meaning"
        ).fetchone()
        assert row["sentence_ordinal"] == 1
        assert row["content_hash"] == sentence_content_hash("He faced the curse head on.")

    def test_remap_drops_a_meaning_row_its_document_revid_changed(self, populated):
        store = populated["store"]
        section_id = self._section(store, self._document(store, "Aoi Todo"))
        self._meaning(store, section_id, 1, "He faced the curse head on.")

        store.require_rebuild(force=True)
        snapshot = store.reset()
        self._rebuild(store, revid=2)

        report = store.remap_derived(snapshot)
        assert report["meaning"] == {
            "before": 1, "remapped": 0, "stale": 1, "orphaned": 0,
            "unverified": 0,
        }

    def test_remap_drops_a_meaning_row_whose_section_vanished(self, populated):
        store = populated["store"]
        section_id = self._section(store, self._document(store, "Aoi Todo"))
        self._meaning(store, section_id, 1, "He faced the curse head on.")

        store.require_rebuild(force=True)
        snapshot = store.reset()
        other_document_id = store.add_document(
            title="Sukuna", url="", page_type="character",
            infobox_template="Character Infobox", lead="Sukuna is a curse.",
            word_count=4, revid=1, fetched_at="",
        )
        self._section(store, other_document_id)

        report = store.remap_derived(snapshot)
        assert report["meaning"]["orphaned"] == 1

    def test_remap_drops_a_meaning_row_its_sentence_moved(self, populated):
        # The section's content changed, so the stored sentence's hash no
        # longer occurs in it: the row is unverified and dropped for
        # re-extraction, never re-anchored to text that no longer says it.
        store = populated["store"]
        section_id = self._section(store, self._document(store, "Aoi Todo"))
        self._meaning(store, section_id, 1, "He faced the curse head on.")

        store.require_rebuild(force=True)
        snapshot = store.reset()
        self._rebuild(store, text="The battle raged through the night.")

        report = store.remap_derived(snapshot)
        assert report["meaning"] == {
            "before": 1, "remapped": 0, "stale": 0, "orphaned": 0,
            "unverified": 1,
        }

    def test_remap_rekeys_a_meaning_rows_sentence_ordinal(self, populated):
        # The section's sentences were reflowed but this one survived: its
        # ordinal follows the sentence (now first, where it was second), not
        # the old number.
        store = populated["store"]
        section_id = self._section(store, self._document(store, "Aoi Todo"))
        self._meaning(store, section_id, 0, "Aoi Todo arrived in the courtyard.")

        store.require_rebuild(force=True)
        snapshot = store.reset()
        self._rebuild(store, text=self.REVERSED)

        report = store.remap_derived(snapshot)
        assert report["meaning"]["remapped"] == 1
        row = store.connection.execute(
            "SELECT sentence_ordinal FROM meaning"
        ).fetchone()
        assert row["sentence_ordinal"] == 1

    def test_remap_keeps_two_rows_for_a_sentence_that_appears_twice(self, populated):
        # The section holds one sentence twice, so two rows share one content
        # hash. An ordinal shift must keep BOTH rows (k-th stored row takes
        # the k-th occurrence); the (section, ordinal) primary key would
        # otherwise collapse them into one silently via INSERT OR REPLACE.
        store = populated["store"]
        duplicated = (
            "He faced the curse head on. Aoi Todo arrived in the courtyard."
            " He faced the curse head on."
        )
        section_id = self._section(
            store, self._document(store, "Aoi Todo"), text=duplicated
        )
        self._meaning(store, section_id, 0, "He faced the curse head on.")
        self._meaning(store, section_id, 2, "He faced the curse head on.")

        store.require_rebuild(force=True)
        snapshot = store.reset()
        self._rebuild(store, text="The bell rang. " + duplicated)

        report = store.remap_derived(snapshot)
        assert report["meaning"] == {
            "before": 2, "remapped": 2, "stale": 0, "orphaned": 0,
            "unverified": 0,
        }
        rows = store.connection.execute(
            "SELECT sentence_ordinal FROM meaning ORDER BY sentence_ordinal"
        ).fetchall()
        assert [r["sentence_ordinal"] for r in rows] == [1, 3]

    def test_a_pre_fk_table_migrates_dropping_dangling_rows(self, populated):
        # A store that predates the FKs: one row still resolvable, one whose
        # subject no longer exists. The migration keeps the first and drops
        # the second, reporting how many it dropped.
        store = populated["store"]
        todo, yuji = populated["todo"], populated["yuji"]
        section_id = self._section(store, self._document(store, "Aoi Todo"))
        store.connection.execute("DROP TABLE events")
        store.connection.execute(
            "CREATE TABLE events ("
            " subject_node INTEGER, subject_name TEXT, object_node INTEGER,"
            " object_name TEXT, verb TEXT, arc_key TEXT, section_id INTEGER,"
            " quote TEXT, temporal INTEGER, time_rank REAL, arc_index INTEGER,"
            " revid INTEGER, prompt_version TEXT, model TEXT, extracted_at TEXT,"
            " PRIMARY KEY (subject_node, verb, object_node, section_id, time_rank))"
        )
        for time_rank, subject_node in ((1.0, todo), (2.0, 999999)):
            store.connection.execute(
                "INSERT INTO events"
                " (subject_node, subject_name, object_node, object_name, verb,"
                "  arc_key, section_id, temporal, time_rank, revid, prompt_version,"
                "  model, extracted_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, 1, 'test', 'test', '')",
                (subject_node, "Aoi Todo", yuji, "Yuji Itadori", "fights",
                 "Test Arc", section_id, time_rank),
            )
        assert store.ensure_events() == 1
        assert (
            store.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
            == 1
        )
        assert store.connection.execute(
            "PRAGMA foreign_key_list(events)"
        ).fetchall()
        # a second pass sees an FK table and migrates nothing
        assert store.ensure_events() == 0
