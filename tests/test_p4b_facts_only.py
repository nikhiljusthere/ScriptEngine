"""P4b: series-declared facts-only infoboxes (Marvel's Cite wrapper).

A facts-only box is parsed and its facts extracted like any infobox, but it
never types a subpage: a citation box is the page's apparatus, not its
subject, and the parent-derived subpage type is the real one. On a main page
the box still types (pre-P4 behaviour, kept so the pre-existing cite-typed
main pages stay put). Pinned here so the deferral cannot regress silently
when the box leaves the discovered vocabulary.
"""

from __future__ import annotations

from scriptengine.ingest.crawler import WikiCrawler
from scriptengine.ingest.ontology import (
    Ontology,
    declared_facts_only_infoboxes,
    discover_infoboxes,
)

CITE_BOX = (
    "{{cite|last=Smith|first=J|title=Marvel AR review|date=2020"
    "|accessdate=2024|url=https://example.com}}"
)
SUBJECT_BOX = "{{character|" + "|".join(f"field{i}=v{i}" for i in range(6)) + "}}"


def ontology_with_cite() -> Ontology:
    ontology = Ontology(wiki="marvel")
    ontology.infobox_types["cite"] = "cite"
    ontology.facts_only_infoboxes = {"cite", "cite web"}
    return ontology


def parse_for(title: str, wikitext: str = CITE_BOX) -> dict:
    return {
        "title": title,
        "wikitext": wikitext,
        "sections": [],
        "templates": [],
        "properties": None,
        "categories": [],
        "pageid": 1,
        "revid": 1,
        "redirects": [],
    }


class TestDeclaration:
    def test_the_helper_normalises_and_tolerates_absence(self):
        assert declared_facts_only_infoboxes(
            {"facts_only_infoboxes": ["Cite", "Cite web"]}
        ) == {"cite", "cite web"}
        assert declared_facts_only_infoboxes(None) == set()
        assert declared_facts_only_infoboxes({}) == set()

    def test_the_field_survives_a_round_trip(self):
        ontology = Ontology(wiki="marvel")
        ontology.facts_only_infoboxes = {"cite"}
        restored = Ontology.from_dict(ontology.to_dict())
        assert restored.facts_only_infoboxes == {"cite"}

    def test_a_legacy_manifest_has_no_facts_only_boxes(self):
        # Pre-P4b manifests never carry the key; an undeclared wiki has no
        # facts-only boxes, so the legacy fallback is the empty set.
        legacy = Ontology.from_dict({"wiki": "marvel"})
        assert legacy.facts_only_infoboxes == set()


class TestDiscovery:
    def test_a_declared_facts_only_box_still_enters_the_vocabulary(self):
        # It must stay discoverable: find_infobox uses the vocabulary to
        # locate the box for fact extraction. Withholding the type is not
        # withholding the facts.
        pages = [
            ("Edward Brock (Earth-616)/Expanded History", CITE_BOX),
            ("Some Other Prose Page", CITE_BOX),
        ]
        ontology = discover_infoboxes(
            "marvel", pages, {"facts_only_infoboxes": ["Cite", "Cite web"]}
        )
        assert "cite" in ontology.infobox_types
        assert ontology.facts_only_infoboxes == {"cite", "cite web"}


class TestSubpageTyping:
    def test_a_subpage_defers_to_its_parent_type_when_the_box_is_facts_only(self):
        crawler = WikiCrawler()
        ontology = ontology_with_cite()
        ontology.page_types["Edward Brock (Earth-616)"] = "character"
        page = crawler.build_page(
            parse_for("Edward Brock (Earth-616)/Expanded History"),
            "https://marvel.fandom.com",
            ontology,
        )
        assert page.page_type == "character_expanded_history"
        # The match is the subpage of the parent, as in the pre-P4 order —
        # the deferral lets the subpage branch take both type and match.
        assert page.infobox_template == "subpage of Edward Brock (Earth-616)"
        # The citation box's facts are still extracted.
        assert len(page.facts) >= 5

    def test_an_untyped_parent_falls_back_to_plain_subpage(self):
        crawler = WikiCrawler()
        ontology = ontology_with_cite()
        page = crawler.build_page(
            parse_for("Character Index/Earth-Unknown-J"),
            "https://marvel.fandom.com",
            ontology,
        )
        assert page.page_type == "subpage"

    def test_a_main_page_keeps_the_box_type(self):
        # Pre-P4 behaviour for the 23 existing cite-typed main pages: the
        # declaration only withholds the type on subpages.
        crawler = WikiCrawler()
        ontology = ontology_with_cite()
        page = crawler.build_page(
            parse_for("Marvel AR"), "https://marvel.fandom.com", ontology
        )
        assert page.page_type == "cite"
        assert page.infobox_template == "cite"
        assert len(page.facts) >= 5

    def test_without_the_declaration_p4_behaviour_stands(self):
        # The deferral is declared, not engine-wide: an undeclared wiki (or a
        # wiki that retracted the declaration) types the subpage from the box,
        # exactly as P4 does.
        crawler = WikiCrawler()
        ontology = ontology_with_cite()
        ontology.facts_only_infoboxes = set()
        ontology.page_types["Edward Brock (Earth-616)"] = "character"
        page = crawler.build_page(
            parse_for("Edward Brock (Earth-616)/Expanded History"),
            "https://marvel.fandom.com",
            ontology,
        )
        assert page.page_type == "cite"

    def test_a_real_subject_box_still_types_its_subpage(self):
        # P4's intended class (the gallery rows, 3,021 of them): a subpage
        # carrying a genuine subject infobox is typed from that box, not from
        # the parent — the deferral must not reach it.
        crawler = WikiCrawler()
        ontology = ontology_with_cite()
        ontology.infobox_types["character"] = "character"
        page = crawler.build_page(
            parse_for("X-Men/Gallery", SUBJECT_BOX),
            "https://marvel.fandom.com",
            ontology,
        )
        assert page.page_type == "character"