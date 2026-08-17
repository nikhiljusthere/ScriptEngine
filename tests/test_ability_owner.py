"""Whose ability it is, settled on the ability's own page.

`ingest/abilities.py` reads a character's declared ability sections, and
`_extracted_roster` assumes what it finds there is therefore that character's.
For 28 of this wiki's 602 rows it is not. Every row whose `section` ends in
`Related Techniques` was harvested from a *technique* page rather than a
character page, and attributed to everyone listed as a user of the parent
technique -- so Yuka Okkotsu's `Savage Jaw Strike` and `Biting Twist`, both
read off the `Divine Dogs` page, arrived as Sukuna's and as Megumi's, and
Choso's `Supernova` arrived as Noritoshi Kamo's.

The wiki settles it. `Savage Jaw Strike` carries `user = Yuka Okkotsu` and says
nothing about either of them.

The rule is the same one the class filter follows: **reject only on positive
evidence**. Most abilities on most of these wikis have no page, and four of the
eight wikis give abilities no pages at all, so a gate that required a `user`
field would delete the answer rather than clean it.
"""

from __future__ import annotations

import pytest

from scriptengine.retrieve.roster import drop_off_owner, stated_users
from scriptengine.stores.facts import FactStore

# name -> the `user` field on its page, or None for "has no page at all"
ABILITIES = {
    "Savage Jaw Strike": "Yuka Okkotsu",
    "Biting Twist": "Yuka Okkotsu",
    "Shrine": "Ryomen Sukuna Yuta Okkotsu (Copied) Yuji Itadori",
    # Nineteen users on the real page, including Megumi. It stays because the
    # field says so, not because anything special-cased it.
    "Domain Expansion": "Megumi Fushiguro Satoru Gojo Sukuna",
    "Dismantle": None,
    "Hometown Domain": None,
}


@pytest.fixture()
def store(tmp_path):
    with FactStore(tmp_path / "facts.db") as opened:
        opened.connection.executescript(
            "CREATE TABLE IF NOT EXISTS nodes"
            " (id INTEGER PRIMARY KEY, name TEXT, label TEXT,"
            "  document_id INTEGER, is_resolved INTEGER);"
            "CREATE TABLE IF NOT EXISTS facts"
            " (id INTEGER PRIMARY KEY, node_id INTEGER, key TEXT,"
            "  label TEXT, value TEXT, citation TEXT);"
        )
        for index, (name, users) in enumerate(ABILITIES.items(), start=1):
            opened.connection.execute(
                "INSERT INTO nodes (id, name) VALUES (?, ?)", (index, name)
            )
            if users is not None:
                opened.connection.execute(
                    "INSERT INTO facts (node_id, key, value) VALUES (?, 'user', ?)",
                    (index, users),
                )
        opened.connection.commit()
        yield opened


class TestStatedUsers:
    def test_reads_the_field(self, store):
        assert stated_users(store, "Savage Jaw Strike") == "Yuka Okkotsu"

    def test_an_ability_with_no_page_states_nobody(self, store):
        """The common case, and it must stay usable as an answer."""
        assert stated_users(store, "Dismantle") == ""
        assert stated_users(store, "Nothing At All") == ""


class TestDropOffOwner:
    def test_an_ability_the_wiki_gives_to_someone_else_is_dropped(self, store):
        kept, rejected = drop_off_owner(
            store, ["Shrine", "Savage Jaw Strike"], "Sukuna", None
        )
        assert kept == ["Shrine"]
        assert [r["name"] for r in rejected] == ["Savage Jaw Strike"]
        assert rejected[0]["rule"] == "owner"

    def test_the_reason_names_the_users_the_wiki_recorded(self, store):
        """A member vanishing with no reason attached is how a list of 160
        quietly became a list of 150."""
        _kept, rejected = drop_off_owner(
            store, ["Dismantle", "Biting Twist"], "Megumi Fushiguro", None
        )
        assert "Yuka Okkotsu" in rejected[0]["reason"]

    def test_an_ability_with_no_stated_user_is_kept(self, store):
        """`Dismantle`, `Cleave` and `Hometown Domain` have no page anywhere on
        this wiki, so there is no field to fail."""
        kept, rejected = drop_off_owner(
            store, ["Dismantle", "Hometown Domain"], "Yuji Itadori", None
        )
        assert kept == ["Dismantle", "Hometown Domain"]
        assert rejected == []

    def test_one_of_several_stated_users_is_enough(self, store):
        """`Shrine` is Sukuna's, Yuta's by copy, and Yuji's by engraving."""
        for who in ("Sukuna", "Yuji Itadori"):
            kept, _ = drop_off_owner(store, ["Shrine"], who, None)
            assert kept == ["Shrine"]

    def test_a_widely_held_ability_survives_by_the_field(self, store):
        kept, rejected = drop_off_owner(
            store, ["Domain Expansion"], "Megumi Fushiguro", None
        )
        assert kept == ["Domain Expansion"]
        assert rejected == []

    def test_it_never_empties_a_non_empty_set(self, store):
        """The guarantee `apply_constraints` gives, for the same reason."""
        kept, rejected = drop_off_owner(
            store, ["Savage Jaw Strike", "Biting Twist"], "Sukuna", None
        )
        assert kept == ["Savage Jaw Strike", "Biting Twist"]
        assert rejected == []

    def test_no_subject_means_no_opinion(self, store):
        names = ["Savage Jaw Strike", "Shrine"]
        assert drop_off_owner(store, names, "", None) == (names, [])


class TestCopied:
    """A qualifier after a user's name says how they came by the technique.

    Yuta Okkotsu's innate technique *is* copying, so the wiki lists him as a
    user of six techniques that are not his and marks each one in the field.
    """

    def test_a_copied_user_does_not_own_it(self, store):
        kept, rejected = drop_off_owner(
            store, ["Shrine", "Dismantle"], "Yuta Okkotsu", None
        )
        assert kept == ["Dismantle"]
        assert rejected[0]["rule"] == "copied"

    def test_the_marker_belongs_to_the_name_it_follows(self, store):
        """`Shrine` is `Ryomen Sukuna Yuta Okkotsu (Copied) Yuji Itadori`.

        The `(Copied)` is Yuta's. Asking whether the field contains it
        anywhere would disown the technique from Sukuna, whose it is.
        """
        kept, rejected = drop_off_owner(store, ["Shrine"], "Sukuna", None)
        assert kept == ["Shrine"]
        assert rejected == []

    @pytest.mark.parametrize("qualifier", ["(via Megumi)", "(Formerly)", "(Anime)"])
    def test_only_an_outright_copy_disowns(self, store, qualifier):
        """Measured, not assumed. `Ten Shadows Technique` reads
        `... Yuka Okkotsu Sukuna (via Megumi)` and is gold on
        `Every cursed technique of Sukuna` -- using a technique through the
        body he has taken is still him using it. Treating `via` as a copy cost
        that canon item on two questions.
        """
        store.connection.execute(
            "INSERT INTO nodes (id, name) VALUES (50, 'Ten Shadows Technique')"
        )
        store.connection.execute(
            "INSERT INTO facts (node_id, key, value) VALUES (50, 'user', ?)",
            (f"Megumi Fushiguro Sukuna {qualifier}",),
        )
        store.connection.commit()
        kept, rejected = drop_off_owner(
            store, ["Ten Shadows Technique", "Dismantle"], "Sukuna", None
        )
        assert "Ten Shadows Technique" in kept
        assert rejected == []
