"""Tests for type discovery.

The point of this module is that nothing in it knows about any particular
series. These tests use Jujutsu Kaisen and Marvel template names purely as
fixtures, so a change that makes one wiki work by naming it would fail here.
"""

from __future__ import annotations

from scriptengine.ingest.ontology import (
    Ontology,
    build_ontology,
    discover_infoboxes,
    learn_field_labels,
    slugify_type,
)

# The 20 infobox templates the Jujutsu Kaisen wiki actually publishes.
JJK_TEMPLATES = [
    "Template:Character Infobox", "Template:Battle Infobox",
    "Template:Episode Infobox", "Template:Technique Infobox",
    "Template:Story Arcs Infobox", "Template:Location Infobox",
    "Template:Organizations Infobox", "Template:Volume Infobox",
    "Template:Infobox Scroll box",  # structural, not a page type
    "Template:Ref", "Template:Nihongo", "Template:Navibox",
]


class TestSlugify:
    def test_naming_style_does_not_leak_into_type_ids(self):
        assert slugify_type("Character Infobox") == "character"
        assert slugify_type("Infobox_Character") == "character"
        assert slugify_type("Template:Character Infobox") == "character"

    def test_multiword_types_are_preserved(self):
        assert slugify_type("Story Arcs Infobox") == "story_arcs"


class TestBuildOntology:
    def test_types_come_from_the_wikis_own_templates(self):
        ontology = build_ontology("https://example.fandom.com", JJK_TEMPLATES)
        assert set(ontology.types) == {
            "character", "battle", "episode", "technique",
            "story_arcs", "location", "organizations", "volume",
        }

    def test_non_infobox_templates_are_ignored(self):
        ontology = build_ontology("https://example.fandom.com", JJK_TEMPLATES)
        assert "ref" not in ontology.types
        assert "nihongo" not in ontology.types

    def test_structural_infoboxes_are_not_page_types(self):
        ontology = build_ontology("https://example.fandom.com", JJK_TEMPLATES)
        assert "scroll_box" not in ontology.types

    def test_an_unrelated_wiki_yields_its_own_vocabulary(self):
        # Nothing carries over from the wiki above.
        ontology = build_ontology(
            "https://example.fandom.com",
            ["Template:Starship Infobox", "Template:Planet Infobox"],
        )
        assert set(ontology.types) == {"starship", "planet"}


class TestTypeAssignment:
    def setup_method(self):
        self.ontology = build_ontology("https://example.fandom.com", JJK_TEMPLATES)

    def test_a_page_is_typed_by_the_infobox_it_transcludes(self):
        type_id, matched = self.ontology.type_for_templates(
            ["Template:Ref", "Template:Character Infobox", "Template:Navibox"]
        )
        assert type_id == "character"
        assert matched == "character infobox"

    def test_an_unknown_infobox_still_yields_a_type_by_convention(self):
        # Fandom names infoboxes "... Infobox", so a wiki whose vocabulary scan
        # was truncated still degrades to something useful.
        type_id, _ = self.ontology.type_for_templates(["Template:Spaceship Infobox"])
        assert type_id == "spaceship"

    def test_lua_modules_never_name_a_type(self):
        # Marvel transcludes `Module:CharacterInfoboxOrigins`, which is an
        # implementation detail. Treating it as a type produced the nonsense
        # type `module_characterinfoboxorigins`.
        type_id, _ = self.ontology.type_for_templates(
            ["Module:CharacterInfoboxOrigins", "Module:PageType"]
        )
        assert type_id == "unknown"

    def test_a_page_with_no_infobox_is_unknown(self):
        assert self.ontology.type_for_templates(["Template:Ref"])[0] == "unknown"


class TestOverrides:
    """Series-specific handling belongs in YAML, never in Python."""

    def test_type_aliases_map_an_unusual_template_onto_a_type(self):
        ontology = build_ontology(
            "https://example.fandom.com",
            ["Template:Ref"],
            overrides={"type_aliases": {"Character Template": "character"}},
        )
        assert ontology.type_for_templates(["Template:Character Template"])[0] == (
            "character"
        )

    def test_skip_categories_are_honoured(self):
        ontology = build_ontology(
            "https://example.fandom.com",
            JJK_TEMPLATES,
            overrides={"skip_categories": ["Disambiguation Pages"]},
        )
        assert ontology.is_skippable(["Disambiguation Pages"])
        assert not ontology.is_skippable(["Characters"])

    def test_maintenance_categories_are_skipped_without_configuration(self):
        ontology = build_ontology("https://example.fandom.com", JJK_TEMPLATES)
        assert ontology.is_skippable(["Aoi Todo Images"])
        assert ontology.is_skippable(["Candidates for deletion"])
        assert not ontology.is_skippable(["Jujutsu Sorcerers"])

    def test_articles_needing_cleanup_does_not_skip_a_real_page(self):
        # The three main character pages carry "Articles needing cleanup";
        # skipping on a maintenance banner throws away the most-linked content.
        ontology = build_ontology("https://example.fandom.com", JJK_TEMPLATES)
        assert not ontology.is_skippable(["Articles needing cleanup"])
        assert not ontology.is_skippable(["Articles needing citation"])

    def test_the_default_skip_patterns_stand_without_configuration(self):
        ontology = build_ontology("https://example.fandom.com", JJK_TEMPLATES)
        assert ontology.skip_patterns is None
        assert ontology.is_skippable(["Disambiguation Pages"])

    def test_skip_patterns_declares_the_patterns_a_series_uses(self):
        # L2 (plan MARVEL_100_PLAN.md §1): the defaults drop the
        # disambiguation pages, which on the Marvel Database carry the wiki's
        # own alias graph and must land on disk. Declaring the list is full
        # ownership of the pattern behaviour: the declared patterns apply and
        # the built-ins do not.
        marvel = [
            "images", "gallery", "galleries", "candidates for deletion",
            "stubs", "blog posts", "browse", "site maintenance",
            "templates", "wiki",
        ]
        ontology = build_ontology(
            "https://marvel.fandom.com", [], overrides={"skip_patterns": marvel}
        )
        assert ontology.skip_patterns is not None
        assert not ontology.is_skippable(["Disambiguation Pages"])
        # The declared patterns keep working, and the exact `skip_categories`
        # list still applies on top.
        assert ontology.is_skippable(["Some Series Stubs"])
        assert not ontology.is_skippable(["Characters"])

    def test_an_empty_skip_patterns_list_switches_patterns_off(self):
        ontology = build_ontology(
            "https://example.fandom.com",
            JJK_TEMPLATES,
            overrides={"skip_patterns": []},
        )
        assert ontology.skip_patterns == ()
        assert not ontology.is_skippable(["Disambiguation Pages"])
        assert not ontology.is_skippable(["Aoi Todo Images"])

    def test_skip_patterns_survive_the_manifest_round_trip(self):
        ontology = build_ontology(
            "https://marvel.fandom.com",
            [],
            overrides={
                "skip_patterns": ["stubs"],
                "alias_fact_keys": ["CurrentAlias"],
            },
        )
        restored = Ontology.from_dict(ontology.to_dict())
        assert restored.skip_patterns == ("stubs",)
        assert restored.alias_fact_keys == ("currentalias",)
        # A manifest that predates the hooks stays on the defaults.
        legacy = Ontology.from_dict({"wiki": "example.fandom.com"})
        assert legacy.skip_patterns is None
        assert legacy.alias_fact_keys == ()

    def test_alias_fact_keys_are_declared_on_the_ontology(self):
        ontology = build_ontology(
            "https://marvel.fandom.com",
            [],
            overrides={"alias_fact_keys": ["CurrentAlias"]},
        )
        assert ontology.alias_fact_keys == ("currentalias",)
        assert build_ontology(
            "https://example.fandom.com", []
        ).alias_fact_keys == ()


class TestStructuralDiscovery:
    """Type discovery from page shape, which is what makes this wiki-agnostic."""

    CHARACTER_PAGE = (
        "{{Tabs|tab1 = Profile|tab2 = Synopsis|tab3 = Image Gallery}}\n"
        "{{Character|name = Denji|race = Human|age = 16|status = Alive"
        "|affiliation = [[Public Safety]]|debut = Chapter 1}}\n"
        "==Appearance==\nText.\n"
    )

    def test_an_infobox_without_the_word_infobox_is_found(self):
        # Chainsaw Man calls its infobox `Character`. Name matching finds
        # Jujutsu Kaisen's twenty types and nothing at all here.
        ontology = discover_infoboxes(
            "https://example.fandom.com",
            [("Denji", self.CHARACTER_PAGE), ("Power", self.CHARACTER_PAGE)],
        )
        assert "character" in ontology.types

    def test_layout_wrappers_are_not_elected(self):
        # `Tabs` wins the vote on any page lacking a real infobox, but peaks at
        # three parameters. Electing it let it shadow the actual infobox during
        # extraction and cost every character page its facts.
        layout_only = "{{Tabs|tab1 = A|tab2 = B|tab3 = C}}\n==Section==\nText."
        ontology = discover_infoboxes(
            "https://example.fandom.com",
            [("One", layout_only), ("Two", layout_only)],
        )
        assert "tabs" not in ontology.types

    def test_a_template_used_once_is_not_a_type(self):
        ontology = discover_infoboxes(
            "https://example.fandom.com", [("Denji", self.CHARACTER_PAGE)]
        )
        assert ontology.types == []

    def test_the_vote_tally_is_kept_for_the_audit(self):
        ontology = discover_infoboxes(
            "https://example.fandom.com",
            [("Denji", self.CHARACTER_PAGE), ("Power", self.CHARACTER_PAGE)],
        )
        assert ontology.infobox_votes.get("Character") == 2


class TestDeclaredStructuralInfoboxes:
    """`structural_infoboxes:` — a series declares its own layout wrappers.

    mcu nests a collapsible `Infobox List` inside its subject infoboxes;
    the wrapper's longer name shadows the subject in the longest-name
    rule, and the declaration is what undoes it. A generic wiki stands in
    for mcu so the declaration, not a named series, is what is under test.
    """

    SUBJECT = "Template:Character Infobox"
    WRAPPER = "Template:Infobox Character List"  # 22 chars: beats the 17-char subject name

    def test_the_longer_wrapper_wins_without_a_declaration(self):
        # Documents the shadowing the declaration removes: the wrapper is
        # auto-detected (the word "infobox" in its name) and its longer
        # name wins the tiebreak.
        ontology = build_ontology(
            "https://example.fandom.com", [self.SUBJECT, self.WRAPPER]
        )
        type_id, matched = ontology.type_for_templates([self.SUBJECT, self.WRAPPER])
        assert (type_id, matched) == ("character_list", "infobox character list")

    def test_a_declared_wrapper_does_not_shadow_the_subject(self):
        ontology = build_ontology(
            "https://example.fandom.com",
            [self.SUBJECT, self.WRAPPER],
            {"structural_infoboxes": ["Infobox Character List"]},
        )
        type_id, matched = ontology.type_for_templates([self.SUBJECT, self.WRAPPER])
        assert (type_id, matched) == ("character", "character infobox")

    def test_the_declaration_reaches_structure_discovery(self):
        # A wrapper rich enough to win the shape vote on pages without a
        # subject box must not be elected when the series declares it.
        wrapper_rich = (
            "{{Infobox Character List|"
            + "|".join(f"entry{i} = x" for i in range(6))
            + "}}\n==Section==\nText."
        )
        declared = discover_infoboxes(
            "https://example.fandom.com",
            [("One", wrapper_rich), ("Two", wrapper_rich)],
            {"structural_infoboxes": ["Infobox Character List"]},
        )
        assert "infobox character list" not in declared.infobox_types
        plain = discover_infoboxes(
            "https://example.fandom.com",
            [("One", wrapper_rich), ("Two", wrapper_rich)],
        )
        assert "infobox character list" in plain.infobox_types

    def test_the_declaration_survives_serialisation(self):
        # A manifest written with the key restored must keep the wrapper
        # structural; one predating the key falls back to the engine-wide set.
        ontology = build_ontology(
            "https://example.fandom.com",
            [self.SUBJECT, self.WRAPPER],
            {"structural_infoboxes": ["Infobox Character List"]},
        )
        payload = ontology.to_dict()
        assert "infobox character list" in payload["structural_infoboxes"]
        restored = Ontology.from_dict(payload)
        assert restored.structural_infoboxes == ontology.structural_infoboxes
        payload.pop("structural_infoboxes")
        legacy = Ontology.from_dict(payload)
        assert legacy.structural_infoboxes == set(
            {"infobox scroll box", "infobox", "scroll box"}
        )


class TestFieldLabels:
    def test_labels_are_learned_from_the_portable_infobox_schema(self):
        # `class` alone is meaningless; the wiki calls it "Grade".
        ontology = Ontology()
        learn_field_labels(
            ontology,
            "character",
            {
                "infoboxes": (
                    '[{"metadata":[{"type":"data",'
                    '"sources":{"class":{"label":"Grade","primary":true}}}]}]'
                )
            },
        )
        assert ontology.labels_for("character")["class"] == "Grade"

    def test_a_wiki_without_portable_infoboxes_still_works(self):
        ontology = Ontology()
        learn_field_labels(ontology, "character", None)
        learn_field_labels(ontology, "character", {"infoboxes": "not json"})
        assert ontology.labels_for("character") == {}


class TestRoundTrip:
    def test_an_ontology_survives_serialisation(self):
        original = build_ontology("https://example.fandom.com", JJK_TEMPLATES)
        restored = Ontology.from_dict(original.to_dict())
        assert restored.types == original.types
        assert restored.wiki == original.wiki
