"""Extracting the abilities a wiki only writes as prose.

Half of what a character-scoped question asks for is not an entity anywhere:
47 of 113 canon items exist as pages, 20 more as section headings, and the
remaining 57 only inside a paragraph. Killua's Godspeed has no page, no
category, and no `users` field pointing at him.

Everything here runs without a model. The parsing, the windowing and the
gating decide whether a run is worth anything and are testable on their own;
what the model says about a given passage is not.
"""

from __future__ import annotations

import pytest

from scriptengine.config import load_overrides, series_paths
from scriptengine.ingest import abilities as A
from scriptengine.stores.facts import FactStore


class TestParsing:
    def test_reads_the_shape_it_asked_for(self):
        found = A.parse_response(
            '{"abilities": [{"name": "Godspeed", "kind": "technique",'
            ' "reason": "electrified body"}]}'
        )
        assert found == [
            {"name": "Godspeed", "kind": "technique", "reason": "electrified body"}
        ]

    def test_tolerates_the_fences_it_forbade(self):
        found = A.parse_response(
            'Here you go:\n```json\n{"abilities": [{"name": "Chain Jail",'
            ' "kind": "technique"}]}\n```'
        )
        assert [entry["name"] for entry in found] == ["Chain Jail"]

    def test_an_empty_answer_is_a_valid_answer(self):
        """A passage naming nothing must not look like a failure."""
        assert A.parse_response('{"abilities": []}') == []

    def test_junk_is_not_an_ability(self):
        assert A.parse_response("the model felt chatty today") == []
        assert A.parse_response("") == []

    def test_an_unknown_kind_falls_back_rather_than_vanishing(self):
        found = A.parse_response('{"abilities": [{"name": "X", "kind": "vibe"}]}')
        assert found[0]["kind"] == "technique"

    def test_a_sentence_is_not_a_name(self):
        found = A.parse_response(
            '{"abilities": [{"name": "%s", "kind": "technique"}]}' % ("a " * 60)
        )
        assert found == []

    @pytest.mark.parametrize(
        "name,kept",
        [
            ("Godspeed", True),
            ("Chain Jail", True),
            ("Speed of Lightning", True),
            ("Rhythm Echo", True),
            # What the model returned when told not to return descriptions.
            ("master swordsmanship", False),
            ("combat pragmatism", False),
            ("uses children to bait and distract enemies", False),
            ("electric aura", False),
        ],
    )
    def test_a_description_is_not_a_named_ability(self, name, kept):
        """Wikis capitalise what they have named; the model does not."""
        found = A.parse_response(
            '{"abilities": [{"name": %s, "kind": "technique"}]}' % repr(name).replace("'", '"')
        )
        assert bool(found) is kept


class TestWindows:
    def test_short_text_is_one_request(self):
        assert A._windows("a" * 100) == ["a" * 100]

    def test_a_long_section_is_read_whole(self):
        """Killua's `Abilities & Powers` is 17,672 characters.

        Sending the first 4,000 found Whirlwind and Speed of Lightning and
        missed Godspeed — not because the model could not find it, but because
        it was never shown it.
        """
        text = "x" * 17_672
        windows = A._windows(text)
        assert len(windows) > 1
        assert sum(len(window) for window in windows) >= len(text)

    def test_windows_overlap_so_nothing_falls_between_them(self):
        text = "".join(str(index % 10) for index in range(10_000))
        windows = A._windows(text, size=4000, overlap=300)
        assert windows[1].startswith(text[3700:3710])


class TestGating:
    def test_a_series_declaring_no_sections_is_skipped(self):
        """Dragon Ball records ownership as edges and needs no inference."""
        paths = series_paths("db")
        if not paths.facts_db.exists():
            pytest.skip("db is not indexed")
        with FactStore(paths.facts_db) as store:
            assert A.needs_extracting(store, load_overrides(paths)) == []
            assert A.needs_extracting(store, {}) == []

    def test_the_characters_that_matter_come_first(self):
        """`--limit` must not mean "the first few alphabetically".

        Ordered by name, Hunterpedia offers `288th Hunter Exam's 1st Phase
        Examiner`, `Abaki` and `Abengane` before anyone a question is about.
        """
        paths = series_paths("hxh")
        if not paths.facts_db.exists():
            pytest.skip("hxh is not indexed")
        with FactStore(paths.facts_db) as store:
            found = A.needs_extracting(store, load_overrides(paths))
        assert "Killua Zoldyck" in found[:10]
        assert "Kurapika" in found[:10]

    def test_a_heading_with_nothing_under_it_is_not_a_passage(self):
        paths = series_paths("hxh")
        if not paths.facts_db.exists():
            pytest.skip("hxh is not indexed")
        with FactStore(paths.facts_db) as store:
            for _, text in A.passages(store, "Killua Zoldyck", load_overrides(paths)):
                assert len(text) >= 120


class TestStorage:
    def test_a_rerun_replaces_rather_than_unions(self, tmp_path):
        """Two prompts' opinions must never be merged into one answer."""
        with FactStore(tmp_path / "facts.db") as store:
            store.ensure_abilities()
            store.save_abilities(
                "Killua Zoldyck",
                [{"name": "Godspeed", "kind": "technique"},
                 {"name": "Whirlwind", "kind": "technique"}],
                revid=1, prompt_version="a", model="m",
            )
            store.save_abilities(
                "Killua Zoldyck",
                [{"name": "Godspeed", "kind": "technique"}],
                revid=2, prompt_version="b", model="m",
            )
            rows = store.abilities_of("Killua Zoldyck")
            assert [row["name"] for row in rows] == ["Godspeed"]
            assert store.extraction_state("Killua Zoldyck")["prompt_version"] == "b"

    def test_kinds_filter_the_read(self, tmp_path):
        with FactStore(tmp_path / "facts.db") as store:
            store.ensure_abilities()
            store.save_abilities(
                "Guts",
                [{"name": "Berserker Armor", "kind": "item"},
                 {"name": "Dragon Slayer", "kind": "item"},
                 {"name": "Sword Skill", "kind": "technique"}],
                revid=1, prompt_version="a", model="m",
            )
            assert len(store.abilities_of("Guts", ["item"])) == 2
            assert len(store.abilities_of("Guts")) == 3

    def test_a_store_without_the_table_answers_none(self, tmp_path):
        """Retrieval must survive a store built before extraction existed."""
        with FactStore(tmp_path / "facts.db") as store:
            assert store.abilities_of("Anyone") == []
            assert store.extraction_state("Anyone") is None


class TestGroundedness:
    """A name the passage never uses cannot be cited.

    Audited over 2,841 stored rows: a local model named 91 things its source
    never says — `Fireball shooting`, `Sword fighting`, `Cero Barrage`,
    `Ghostly Wolf Summoning` — against opencode's 1. Several describe something
    the character really does. None is what the wiki calls it.
    """

    def test_a_name_in_the_prose_passes(self):
        assert A._grounded_in("Godspeed", "Killua devised Godspeed in combat.", "Nen")

    def test_a_name_only_in_the_heading_passes(self):
        """`Equipment / Cannon Arm` names the thing its paragraph describes."""
        assert A._grounded_in("Cannon Arm", "Rickert built it for him.", "Equipment / Cannon Arm")

    def test_a_name_the_passage_never_uses_fails(self):
        assert not A._grounded_in("Ghostly Wolf Summoning", "Starrk splits his soul.", "Abilities")

    def test_matching_ignores_case_and_accents(self):
        assert A._grounded_in("Getsuga Tensho", "he fires a Getsugā Tenshō", "Powers")

    def test_punctuation_does_not_block_a_match(self):
        assert A._grounded_in("Bang! (バン！)", "she says Bang and they die", "Abilities")
