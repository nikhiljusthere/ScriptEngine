"""Tests for wikitext parsing.

The cases here are drawn from real Jujutsu Kaisen markup, and most of them exist
because a plausible-looking implementation got them wrong first.
"""

from __future__ import annotations

from scriptengine.ingest.wikitext import (
    extract_citations,
    extract_links,
    facts_from_infobox,
    find_infobox,
    flatten_tables,
    split_params,
    split_sections,
    strip_markup,
)


class TestBalancedScanning:
    """Wikitext nests, so nothing here can be done with a flat regex."""

    def test_pipe_inside_a_link_does_not_split_a_parameter(self):
        # `body.split("|")` shatters this into two broken halves.
        params = split_params(
            "Character_Infobox|affiliation = [[Kyoto Metropolitan College|Kyoto High]]"
        )
        assert len(params) == 2
        assert params[1] == "affiliation = [[Kyoto Metropolitan College|Kyoto High]]"

    def test_pipe_inside_a_nested_template_does_not_split_a_parameter(self):
        params = split_params("Infobox|age = 18{{Ref|fan=Fanbook|page=36-37}}")
        assert len(params) == 2
        assert params[1] == "age = 18{{Ref|fan=Fanbook|page=36-37}}"

    def test_unclosed_construct_does_not_raise(self):
        # A malformed page must not stop a crawl of hundreds of pages.
        assert strip_markup("text {{Unclosed|foo") is not None
        assert extract_links("[[Unclosed") == []


class TestLinks:
    def test_target_and_display_are_both_kept(self):
        (link,) = extract_links("[[Kyoto Metropolitan College|Kyoto High]]")
        assert link.target == "Kyoto Metropolitan College"
        assert link.display == "Kyoto High"

    def test_bare_link_uses_target_as_display(self):
        (link,) = extract_links("[[Satoru Gojo]]")
        assert link.target == "Satoru Gojo"
        assert link.display == "Satoru Gojo"

    def test_section_anchor_is_dropped_from_the_target(self):
        (link,) = extract_links("[[Grade#Ranks|grade 1]]")
        assert link.target == "Grade"

    def test_category_and_file_links_are_not_relationships(self):
        assert extract_links("[[Category:Characters]] [[File:Todo.png|220px]]") == []

    def test_an_interwiki_link_is_not_a_relationship(self):
        assert extract_links("[[Wikipedia:Subaru Kimura|Subaru Kimura]]") == []

    def test_an_interwiki_links_text_is_still_kept(self):
        # It is not an edge, but it is prose: this is how the voice actor's name
        # appears on the page, and dropping it lost the answer to
        # "who voices Aoi Todo in Japanese?".
        assert strip_markup("[[Wikipedia:Subaru Kimura|Subaru Kimura]]") == (
            "Subaru Kimura"
        )

    def test_a_file_link_still_renders_nothing(self):
        assert strip_markup("[[File:Todo.png|220px]]") == ""


class TestCitations:
    def test_citation_parameters_are_kept_structured(self):
        (citation,) = extract_citations("Todo is tall.{{Ref|vol=5|page=26}}")
        assert citation.template == "Ref"
        assert citation.params["vol"] == "5"
        assert citation.params["page"] == "26"

    def test_citations_nested_in_a_parameter_are_found(self):
        citations = extract_citations("{{Infobox|age = 18{{Ref|chap=21|page=14}}}}")
        assert [c.params["chap"] for c in citations] == ["21"]

    def test_citations_never_reach_the_prose(self):
        # The previous pipeline expanded citations into the text and embedded
        # them, so a large share of every vector encoded bibliography.
        text = strip_markup("Todo is tall.{{Ref|vol=5|page=26}} He is strong.")
        assert "Ref" not in text and "vol=5" not in text
        assert text == "Todo is tall. He is strong."


class TestMarkupStripping:
    def test_no_raw_markup_survives(self):
        text = strip_markup(
            "'''Todo''' is a [[Jujutsu Sorcerer|sorcerer]].{{Ref|chap=16}}\n"
            "<!-- hidden --><br>He is [[Grade#Ranks|grade 1]]."
        )
        for token in ("{{", "}}", "[[", "]]", "<!--", "<br>", "'''"):
            assert token not in text

    def test_nihongo_keeps_the_english_name_not_the_japanese(self):
        # Picking the longest argument — which looks reasonable — returns the
        # kanji here, and produced section text reading "の: A binding vow...".
        assert strip_markup("{{Nihongo|Revealing One's Hand|情報の開示|Jōhō}}") == (
            "Revealing One's Hand"
        )

    def test_ruby_keeps_the_base_character_not_the_furigana(self):
        assert strip_markup("{{Ruby|情|じょう}}") == "情"

    def test_color_keeps_the_text_not_the_colour_name(self):
        assert strip_markup("{{Color|White|Binding Vows}}") == "Binding Vows"

    def test_external_link_keeps_only_its_label(self):
        assert strip_markup("[https://example.com the label]") == "the label"

    def test_gallery_contents_are_removed_not_just_its_tags(self):
        # Stripping only the tags leaves the payload: a gallery body is a list
        # of image files, and it surfaced verbatim inside a timeline beat as
        # "NanamiP.png|Kento Nanami|link=Kento Nanami".
        text = strip_markup(
            "Teams deployed.\n"
            "<gallery>\nNanamiP.png|Kento Nanami|link=Kento Nanami\n</gallery>\n"
            "The operation began."
        )
        assert "NanamiP.png" not in text
        assert "Teams deployed." in text and "The operation began." in text


class TestTables:
    """Tables carry content on a Fandom wiki, not decoration."""

    def test_table_content_is_kept(self):
        # Deleting tables with `\{\|.*?\|\}` silently dropped Todo's entire
        # Cursed Technique section — 185 words of the page's most factual prose.
        table = (
            '{| class="wikitable"\n'
            "! Technique !! Effect\n"
            "|-\n"
            "| Boogie Woogie || Switches the positions of two targets.\n"
            "|}"
        )
        result = flatten_tables(table)
        assert "Boogie Woogie" in result
        assert "Switches the positions of two targets." in result

    def test_nested_tables_are_flattened(self):
        nested = "{|\n| outer\n{|\n| inner\n|}\n|}"
        result = flatten_tables(nested)
        assert "outer" in result and "inner" in result

    def test_image_only_cells_leave_no_empty_column(self):
        table = "{|\n||[[File:Boogie.gif|220px]]||Real content\n|}"
        assert "—" not in flatten_tables(table)

    def test_unclosed_table_keeps_its_content(self):
        assert "content" in flatten_tables("{|\n| content")


class TestInfobox:
    INFOBOX = (
        "{{Character_Infobox\n"
        "|name = Aoi Todo\n"
        "|age = 18{{Ref|fan=Fanbook|page=36-37}}\n"
        "|affiliation = [[Kyoto Metropolitan College|Kyoto High]]\n"
        "|image = <gallery>Todo.png|Anime</gallery>\n"
        "}}\n"
        "Some prose."
    )

    def test_infobox_is_located_and_named(self):
        found = find_infobox(self.INFOBOX)
        assert found is not None
        assert found[0] == "Character Infobox"

    def test_parameters_become_facts_with_links_and_citations_attached(self):
        _, params = find_infobox(self.INFOBOX)
        facts = {f.key: f for f in facts_from_infobox(params)}

        assert facts["name"].value == "Aoi Todo"
        # The link target is canonical while the display name is what readers see.
        assert facts["affiliation"].value == "Kyoto High"
        assert facts["affiliation"].links[0].target == "Kyoto Metropolitan College"
        # The citation is captured but stripped out of the value.
        assert facts["age"].value == "18"
        assert facts["age"].citations[0].params["page"] == "36-37"

    def test_presentational_parameters_are_not_facts(self):
        _, params = find_infobox(self.INFOBOX)
        assert "image" not in {f.key for f in facts_from_infobox(params)}

    def test_known_vocabulary_wins_over_name_matching(self):
        found = find_infobox(
            "{{Character Sheet|name = X}}", known_templates={"Character Sheet"}
        )
        assert found is not None and found[0] == "Character Sheet"

    def test_the_richest_infobox_wins_not_the_first(self):
        # JJK character pages open with a layout wrapper and only then the real
        # infobox. Once `Tabs` entered the discovered vocabulary, taking the
        # first match returned its three parameters instead of the infobox's
        # twenty-one, and every character on the wiki lost its facts.
        page = (
            "{{Tabs|tab1 = Profile|tab2 = Synopsis|tab3 = Image Gallery}}\n"
            "{{Character_Infobox|name = Aoi Todo|class = Grade 1|race = Human"
            "|hair = Black|eye = Black|status = Alive}}\n"
            "Prose follows."
        )
        found = find_infobox(page, known_templates={"Tabs", "Character Infobox"})
        assert found is not None
        assert found[0] == "Character Infobox"
        assert "class" in found[1]

    def test_labels_from_the_wiki_schema_are_applied(self):
        _, params = find_infobox("{{Infobox|class = Grade 1}}")
        (fact,) = facts_from_infobox(params, labels={"class": "Grade"})
        assert fact.key == "class" and fact.label == "Grade"


class TestSections:
    PAGE = (
        "Lead paragraph.\n"
        "==Appearance==\n"
        "Todo is tall.\n"
        "==Abilities and Powers==\n"
        "=== [[Cursed Technique]] ===\n"
        "Boogie Woogie swaps positions.\n"
    )

    def test_sections_are_found_and_nested(self):
        lead, sections = split_sections(self.PAGE)
        assert lead == "Lead paragraph."
        assert [s.title for s in sections] == [
            "Appearance", "Abilities and Powers", "Cursed Technique",
        ]
        assert sections[2].breadcrumb == "Abilities and Powers / Cursed Technique"

    def test_a_heading_may_contain_a_wikilink(self):
        _, sections = split_sections(self.PAGE)
        assert sections[2].title == "Cursed Technique"

    def test_api_levels_override_markup_depth(self):
        # The API is authoritative about hierarchy.
        _, sections = split_sections(
            "==Appearance==\ntext\n",
            [{"line": "Appearance", "level": "3"}],
        )
        assert sections[0].level == 3

    def test_a_page_with_headings_never_collapses_to_one_section(self):
        # This is the regression guard for the bug that silently disabled the
        # previous pipeline: its detector matched a bare "appearance" while the
        # corpus contained "## Appearance", so every page became one section.
        _, sections = split_sections(self.PAGE)
        assert len(sections) > 1
