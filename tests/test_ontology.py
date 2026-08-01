"""Tests for type discovery.

The point of this module is that nothing in it knows about any particular
series. These tests use Jujutsu Kaisen and Marvel template names purely as
fixtures — a change that makes one wiki work by naming it would fail here.
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
