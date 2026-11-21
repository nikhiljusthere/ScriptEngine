"""Resolver fixes from the 2026-09-29 JJK verification
(reports/jjk/VERIFY_2026-09-29.md): 35 stored rows filed a character's events
on a song page ("Akari") and a shikigami page ("Ryu"), and every bare "Gojo"
tied the character with a clan page that lists the clan names as aliases.

* an exact title the page never links to yields to the one other entity the
  page points at (its link, or the page itself / a subpage's base) -- never
  to a variant of the name, and never away from the page's own entity;
* where no link decides, the one candidate whose own title carries the name
  as a word owns it;
* a wiki's declared `events: participant_exclude_types:` never participate.
"""

from __future__ import annotations

import sqlite3

from scriptengine.ingest.events import participant_candidates, pick_candidate
from scriptengine.stores.facts import FactStore

SONG = (4, "Akari", None)
PERSON = (2, "Akari Nitta", None)


def test_an_unlinked_exact_title_yields_to_the_entity_the_page_links():
    pool = [SONG, PERSON]
    assert pick_candidate(pool, "Akari", None, {2}, "Some Arc") == PERSON
    # The exact page linked, or no pointing at all: the exact title stands.
    assert pick_candidate(pool, "Akari", None, {4, 2}, "Some Arc") == SONG
    assert pick_candidate(pool, "Akari", None, set(), "Some Arc") == SONG


def test_the_page_itself_and_a_subpage_base_point_at_their_entity():
    pool = [SONG, PERSON]
    assert pick_candidate(pool, "Akari", None, set(), "Akari Nitta") == PERSON
    assert pick_candidate(pool, "Akari", None, set(), "Akari Nitta/Synopsis") == PERSON


def test_the_exact_page_is_never_diverted_on_its_own_page():
    # A page never links to itself; its own name is still its own.
    pool = [(6, "Angel", None), (496, "Hana Kurusu", None)]
    assert pick_candidate(pool, "Angel", None, {496}, "Angel") == (6, "Angel", None)


def test_the_diversion_never_lands_on_a_variant_of_the_name():
    pool = [(21, "Sukuna", None), (22, "Sukuna/Synopsis", None)]
    assert pick_candidate(pool, "Sukuna", None, {22}, "Some Arc") == (21, "Sukuna", None)


def test_two_pointed_alternatives_leave_the_exact_title():
    pool = [SONG, PERSON, (3, "Akari Other", None)]
    assert pick_candidate(pool, "Akari", None, {2, 3}, "Some Arc") == SONG


def test_the_title_word_breaks_a_tie_no_link_breaks():
    clan = (822, "Sorcerer Clan", None)
    person = (791, "Satoru Gojo", None)
    pool = [clan, person]
    assert pick_candidate(pool, "Gojo", None, None) == person
    assert pick_candidate(pool, "Gojo", None, {822, 791}) == person
    # A single linked member is still the stronger signal.
    assert pick_candidate(pool, "Gojo", None, {822}) == clan
    # Two titles carrying the word: still a counted ambiguity.
    both = [(1, "Yuji Itadori", None), (2, "Yuji Itadori (Anime)", None)]
    assert pick_candidate(both, "Itadori", None, None) == {"ambiguous": both}


def _store(tmp_path, overrides: str) -> FactStore:
    (tmp_path / "overrides.yaml").write_text(overrides, encoding="utf-8")
    store = FactStore(tmp_path / "facts.db")
    store.initialise()
    conn: sqlite3.Connection = store.connection
    conn.execute("INSERT INTO documents (id, title, page_type) VALUES (1, 'Akari', 'music')")
    conn.execute("INSERT INTO documents (id, title, page_type) VALUES (2, 'Akari Nitta', 'character')")
    conn.execute("INSERT INTO nodes (id, name, label, document_id, is_resolved) VALUES (4, 'Akari', 'music', 1, 1)")
    conn.execute("INSERT INTO nodes (id, name, label, document_id, is_resolved) VALUES (2, 'Akari Nitta', 'character', 2, 1)")
    conn.execute("INSERT INTO aliases (alias, node_id) VALUES ('akari', 2)")
    conn.commit()
    return store


def test_declared_work_types_never_participate(tmp_path):
    with _store(tmp_path, "events:\n  participant_exclude_types: [music]\n") as store:
        pool = participant_candidates(store)["akari"]
    assert [c[0] for c in pool] == [2]


def test_an_undeclared_wiki_keeps_every_type(tmp_path):
    with _store(tmp_path, "{}\n") as store:
        pool = participant_candidates(store)["akari"]
    assert sorted(c[0] for c in pool) == [2, 4]


def test_a_name_part_resolves_through_the_page_link_or_the_page_itself():
    from scriptengine.ingest.events import name_pool

    kiyotaka = (10, "Kiyotaka Ijichi", None)
    synopsis = (11, "Kiyotaka Ijichi/Synopsis", None)
    yuji, jin = (12, "Yuji Itadori", None), (13, "Jin Itadori", None)
    known = {"kiyotaka ijichi": [kiyotaka], "kiyotaka ijichi/synopsis": [synopsis],
             "yuji itadori": [yuji], "jin itadori": [jin], "yuji": [yuji]}
    # A pooled name keeps its pool.
    assert name_pool(known, "Yuji", {13}) == [yuji]
    # A name part the page links.
    assert name_pool(known, "Kiyotaka", {10}) == [kiyotaka]
    # The page itself, and a subpage's base -- never the subpage.
    assert name_pool(known, "Kiyotaka", set(), "Kiyotaka Ijichi") == [kiyotaka]
    assert name_pool(known, "Kiyotaka", set(), "Kiyotaka Ijichi/Synopsis") == [kiyotaka]
    # Two linked owners stay two (pick_candidate counts the ambiguity).
    assert name_pool(known, "Itadori", {12, 13}) == [yuji, jin]
    # Not pointed at: nothing. Not a name: nothing.
    assert name_pool(known, "Kiyotaka", set(), "Some Arc") == []
    assert name_pool(known, "the curse", {10, 12}) == []


def test_a_subpage_names_its_base_before_any_linked_namesake():
    clan, person = (822, "Sorcerer Clan", None), (791, "Satoru Gojo", None)
    # The synopsis links the clan, never its own base page.
    assert pick_candidate([clan, person], "Gojo", None, {822}, "Satoru Gojo/Synopsis") == person
    # Elsewhere the single link still decides.
    assert pick_candidate([clan, person], "Gojo", None, {822}, "Some Arc") == clan
