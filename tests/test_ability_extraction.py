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
from typing import cast

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
        missed Godspeed, not because the model could not find it, but because
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


class TestGridWindows:
    """The passage loop reads the section on the index's sentence grid
    (2026-09-30 windowing council), not 4,000-character slices: each read
    is a whole-sentence span of one sub-topic, verbatim out of the section.
    """

    @staticmethod
    def _text() -> str:
        # Ten paragraphs of twelve named techniques each (~6,300 chars):
        # long enough that the old 4,000-char slice read it in two cuts
        # while the grid reads one window per sub-topic.
        paragraphs = []
        for block in range(10):
            paragraphs.append(
                " ".join(
                    f"In battle, Killua unleashes Godspeed {block * 12 + i}."
                    for i in range(1, 13)
                )
            )
        return "\n\n".join(paragraphs)

    class _Probe:
        """Records every prompt and answers with the names it was shown."""

        def __init__(self) -> None:
            self.prompts: list[str] = []

        def available(self) -> bool:
            return True

        def complete(self, prompt: str, system: str = "", temperature: float = 0.0,
                     max_tokens: int = 0, **_kwargs: object) -> str:
            import json
            import re

            self.prompts.append(prompt)
            names = sorted(set(re.findall(r"Godspeed \d+", prompt)))
            return json.dumps(
                {"abilities": [{"name": n, "kind": "technique"} for n in names]}
            )

    def test_a_long_section_is_read_as_grid_windows(self):
        from scriptengine.ingest.windows import CURRENT_GEN, build_windows

        section, text = "Nen", self._text()
        probe = self._Probe()
        found = A.extract_from_passages(
            probe, "hxh", "Killua Zoldyck", [(section, text)], {}
        )
        expected = build_windows("Killua Zoldyck", section, text, gen=CURRENT_GEN)
        # One call per grid window (10 sub-topics -> 10 windows, not the
        # old slice's 2), each carrying its window's verbatim text.
        assert len(probe.prompts) == len(expected) == 10
        for prompt, window in zip(probe.prompts, expected):
            assert window.text in prompt
        # And no technique falls between reads: every name the section
        # states is extracted.
        assert {entry["name"] for entry in found} == {
            f"Godspeed {i}" for i in range(1, 121)
        }

    def test_windows_are_verbatim_slices_of_the_section(self):
        from scriptengine.ingest.windows import CURRENT_GEN, build_windows

        section, text = "Nen", self._text()
        probe = self._Probe()
        A.extract_from_passages(
            probe, "hxh", "Killua Zoldyck", [(section, text)], {}
        )
        expected = build_windows("Killua Zoldyck", section, text, gen=CURRENT_GEN)
        for window in expected:
            # The read must be the section's own characters, so a quote
            # stated in it stays anchorable to this section.
            assert window.text in text


class TestGating:
    def test_a_series_declaring_no_sections_is_skipped(self):
        """Extraction is opt-in per wiki, and costs nothing where unasked.

        This used to assert that Dragon Ball declared none, which was true
        until its `Power and Abilities` subpages turned out to hold every
        Frieza form the engine was missing. The rule being tested is the
        gating, not which wikis happen to use it.
        """
        paths = series_paths("db")
        if not paths.facts_db.exists():
            pytest.skip("db is not indexed")
        with FactStore(paths.facts_db) as store:
            assert A.needs_extracting(store, {}) == []
            assert A.needs_extracting(store, {"ability_sections": {}}) == []

    def test_a_declared_series_finds_its_characters(self):
        paths = series_paths("db")
        if not paths.facts_db.exists():
            pytest.skip("db is not indexed")
        with FactStore(paths.facts_db) as store:
            found = A.needs_extracting(store, load_overrides(paths))
        # The three whose subpages hold the missing forms, ranked by prose.
        assert {"Goku", "Vegeta", "Frieza"} <= set(found[:5])

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
            state = store.extraction_state("Killua Zoldyck")
            assert state is not None
            assert state["prompt_version"] == "b"

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
    never says: `Fireball shooting`, `Sword fighting`, `Cero Barrage`,
    `Ghostly Wolf Summoning`, against opencode's 1. Several describe something
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


class TestLeadSection:
    """A page's own opening paragraph is about the character by definition."""

    def test_the_lead_is_recognised(self):
        assert A._is_lead("Kurapika", "Kurapika")
        assert A._is_lead(" kurapika ", "Kurapika")

    def test_a_subsection_is_not_the_lead(self):
        assert not A._is_lead("Abilities & Powers / Nen", "Kurapika")
        assert not A._is_lead("Plot / Yorknew City arc", "Kurapika")
        assert not A._is_lead("", "Kurapika")

    def test_kurapikas_chains_are_reachable_now(self):
        """`Holy Chain`, `Steal Chain` and `Emperor Time` are named in his lead
        and nowhere else on any page of his: three of his six canon abilities
        sat outside every declared ability section."""
        paths = series_paths("hxh")
        if not paths.facts_db.exists():
            pytest.skip("hxh is not indexed")
        with FactStore(paths.facts_db) as store:
            prose = " ".join(
                text for _, text in A.passages(store, "Kurapika", load_overrides(paths))
            ).lower()
        for chain in ("holy chain", "steal chain", "emperor time"):
            assert chain in prose


class TestOwnedPages:
    """Techniques on the page a character owns, not on their own page.

    One Piece names the fighting *styles* on the character page and puts the
    techniques inside each style's page. `Every technique of Zoro` scored 10
    canon items with 1 found, and the rest sat in `Three Sword Style /
    Techniques`, a page nothing had read: extraction asks about characters, and
    that is a technique page.
    """

    def test_zoros_techniques_are_reachable_now(self):
        paths = series_paths("onepiece")
        if not paths.facts_db.exists():
            pytest.skip("onepiece is not indexed")
        with FactStore(paths.facts_db) as store:
            prose = " ".join(
                text for _, text in A.owned_passages(
                    store, "Roronoa Zoro", load_overrides(paths))
            ).lower()
        # Named on `Three Sword Style`, and on no page of Zoro's own.
        for technique in ("oni giri", "shishi sonson", "tatsumaki", "ashura"):
            assert technique in prose

    def test_the_page_is_named_in_the_section_label(self):
        """A stored row has to say where it was read from, so these stay
        tellable from rows read off the character's own page."""
        paths = series_paths("onepiece")
        if not paths.facts_db.exists():
            pytest.skip("onepiece is not indexed")
        with FactStore(paths.facts_db) as store:
            labels = [
                label for label, _ in A.owned_passages(
                    store, "Roronoa Zoro", load_overrides(paths))
            ]
        assert labels
        assert any(label.startswith("Three Sword Style / ") for label in labels)

    def test_a_series_that_does_not_declare_it_is_untouched(self):
        """Off by default. Most wikis keep the techniques on the character, and
        reading owned pages there would only add noise.

        Uses opm rather than jjk: jjk declared `ability_owner_sections` on
        2026-08-16 to reach `Great Serpent / Related Techniques`, so it is no
        longer an example of a series without the declaration.
        """
        paths = series_paths("opm")
        if not paths.facts_db.exists():
            pytest.skip("opm is not indexed")
        with FactStore(paths.facts_db) as store:
            assert A.owned_passages(
                store, "Saitama", load_overrides(paths)) == []

    def test_no_declaration_means_the_store_is_never_touched(self):
        """`None` as the store proves it: undeclared must not reach a query."""
        # The cast is deliberate: the point is that `None` is never dereferenced.
        assert A.owned_passages(cast("FactStore", None), "Anyone", {}) == []
        assert A.owned_passages(
            cast("FactStore", None), "Anyone", {"ability_owner_sections": {}}
        ) == []
