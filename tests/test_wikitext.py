"""Tests for wikitext parsing.

The cases here are drawn from real Jujutsu Kaisen markup, and most of them exist
because a plausible-looking implementation got them wrong first.
"""

from __future__ import annotations

from scriptengine.ingest.wikitext import (
    CitationGrammar,
    collect_ref_definitions,
    extract_citations,
    is_page_param,
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

    def test_escaped_category_link_is_not_a_relationship(self):
        # A leading colon makes the category render as text on the page, but it
        # still points at a Category page — not an article. These produced
        # 845 junk ':Category:...' edges on Jujutsu Kaisen.
        assert extract_links(
            "[[:Category:Megumi Fushiguro Techniques|'''Megumi's Techniques''']]"
        ) == []

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

    def test_citations_inline_a_compact_locator(self):
        # Citations keep a short locator — (Volume 5) — not the verbose
        # bibliography the old pipeline embedded, and not nothing: the chapter
        # annotation rules need the locator in prose.
        text = strip_markup("Todo is tall.{{Ref|vol=5|page=26}} He is strong.")
        assert "Ref" not in text and "vol=5" not in text
        assert text == "Todo is tall.(Volume 5) He is strong."

    def test_citation_locator_prefers_chapter_and_episode(self):
        assert strip_markup("{{Ref|chap=143|page=3-5}}") == "(Chapter 143)"
        assert strip_markup("{{Ref|chap=64|page=16-17|ep=30}}") == (
            "(Chapter 64, Episode 30)"
        )
        assert strip_markup("{{Ref|fan=Fanbook|page=4-7}}") == "(Fanbook)"

    def test_named_citation_without_locator_stays_silent(self):
        # `{{Ref|name=fan2}}` reuses a locator printed elsewhere; the prose
        # must not invent one.
        text = strip_markup("Todo is tall.{{Ref|name=fan2}}")
        assert text == "Todo is tall."


class TestNamedReferences:
    # MediaWiki cites a source once and reuses it by name. 538 of the Jujutsu
    # Kaisen corpus's references are name-only, and each one used to render as
    # nothing at all, leaving the line it cited unsourced.

    def test_a_definition_is_collected_by_name(self):
        found = collect_ref_definitions("Text{{Ref|name=c145|chap=145|ep=50}}")
        assert found["c145"]["chap"] == "145"

    def test_a_reuse_is_not_mistaken_for_a_definition(self):
        assert collect_ref_definitions("Text{{Ref|name=c145}}") == {}

    def test_a_reuse_renders_the_locator_it_points_at(self):
        page = (
            "Intro.{{Ref|name=c145|chap=145|ep=50}}\n\n"
            "==One==\nHe did a thing.{{Ref|name=c145}}\n"
        )
        _, sections = split_sections(page)
        assert sections[0].text == "He did a thing.(Chapter 145, Episode 50)"

    def test_a_definition_in_another_section_still_resolves(self):
        # The definition and its reuses routinely sit in different sections, so
        # the map has to be built from the whole page.
        page = (
            "==One==\nFirst.{{Ref|name=c9|chap=9}}\n\n"
            "==Two==\nSecond.{{Ref|name=c9}}\n"
        )
        _, sections = split_sections(page)
        assert "(Chapter 9)" in sections[1].text

    def test_a_reused_citation_carries_the_locator_as_structured_data(self):
        page = "Intro.{{Ref|name=c9|chap=9}}\n\n==One==\nHe did.{{Ref|name=c9}}\n"
        _, sections = split_sections(page)
        assert sections[0].citations[0].params["chap"] == "9"

    def test_an_unknown_name_renders_nothing_rather_than_guessing(self):
        assert strip_markup("He did.{{Ref|name=missing}}") == "He did."


class TestCitationGrammar:
    # A sequel numbers its chapters from 1 again. The wiki says which work a
    # reference means; dropping that rendered `{{Ref|modulo=y|chap=16}}` as
    # "(Chapter 16)", the same string as the main series' Chapter 16, on 427
    # references — a wrong chapter number available to every script.

    works = CitationGrammar.from_overrides({
        "citation_works": {"modulo": "Modulo"},
        "citation_instalments": {"movie": "Movie"},
    })

    def test_a_sequel_chapter_says_which_manga_it_is(self):
        text = strip_markup("She fell.{{Ref|modulo=y|chap=15|page=10}}", works=self.works)
        assert text == "She fell.(Modulo Chapter 15)"

    def test_the_main_series_is_unprefixed(self):
        text = strip_markup("He won.{{Ref|chap=119|ep=41}}", works=self.works)
        assert text == "He won.(Chapter 119, Episode 41)"

    def test_any_truthy_flag_value_counts(self):
        for flag in ("y", "yes", "true", "1"):
            text = strip_markup(f"X.{{{{Ref|modulo={flag}|chap=24}}}}", works=self.works)
            assert text == "X.(Modulo Chapter 24)"

    def test_a_qualifier_that_is_itself_the_instalment(self):
        # `{{Ref|movie=0}}` cites the film, which has no chapter. It used to
        # render nothing at all, leaving the line it cited unsourced.
        assert strip_markup("X.{{Ref|movie=0}}", works=self.works) == "X.(Movie 0)"

    def test_an_unmapped_wiki_is_left_as_it_was(self):
        # No overrides means no qualifiers, which is the previous behaviour —
        # a wiki without a sequel loses nothing.
        assert strip_markup("X.{{Ref|modulo=y|chap=16}}") == "X.(Chapter 16)"

    def test_page_typos_are_not_dropped_facts(self):
        assert is_page_param("pages") and is_page_param("pagse") and is_page_param("pagess")
        assert not is_page_param("modulo")


class TestPositionalCitations:
    # Chainsaw Man writes every reference positionally: {{Ref|m|216|3-4}} means
    # manga, chapter 216, pages 3-4. All 2,946 of them rendered nothing until
    # the grammar could read them, and the series scored 0.0% sourced prose.

    grammar = CitationGrammar.from_overrides({
        "citation_positional": {
            "select": 0, "number": 1,
            "mediums": {"m": {"as": "chapter"}, "a": {"as": "episode"}},
        }
    })

    def test_the_medium_picks_what_the_number_means(self):
        assert strip_markup("A.{{Ref|m|216|3-4}}", works=self.grammar) == "A.(Chapter 216)"
        assert strip_markup("B.{{Ref|a|12|1}}", works=self.grammar) == "B.(Episode 12)"

    def test_a_reference_without_pages_still_locates(self):
        assert strip_markup("C.{{Ref|m|180}}", works=self.grammar) == "C.(Chapter 180)"

    def test_an_unknown_medium_renders_nothing_rather_than_guessing(self):
        assert strip_markup("D.{{Ref|x|9}}", works=self.grammar) == "D."

    def test_a_wiki_without_the_schema_is_unaffected(self):
        assert strip_markup("E.{{Ref|m|216|3-4}}") == "E."


class TestAlternateParamNames:
    # One-Punch Man exists as a webcomic and as a manga with separate numbering,
    # and the wiki keeps them apart on the reference itself.

    grammar = CitationGrammar.from_overrides({
        "citation_params": {
            "ch": {"as": "chapter"},
            "wch": {"as": "chapter", "work": "Webcomic"},
            "p": {"as": "page"},
        }
    })

    def test_a_wikis_own_parameter_name_is_read(self):
        assert strip_markup("A.{{ref|ch = 20|p = 27}}", works=self.grammar) == (
            "A.(Chapter 20)"
        )

    def test_a_second_numbering_says_which_work_it_is(self):
        assert strip_markup("B.{{ref|wch = 44}}", works=self.grammar) == (
            "B.(Webcomic Chapter 44)"
        )

    def test_a_page_parameter_never_reaches_the_prose(self):
        # A page number is retrieval noise inside a sentence.
        assert "27" not in strip_markup("C.{{ref|ch = 20|p = 27}}", works=self.grammar)


class TestRefTagCitations:
    # Bleach, Hunterpedia and Berserk put the locator in prose inside an HTML
    # <ref> tag. Until it is read and replaced, `_HTML_TAG` deletes the tags and
    # leaves the bibliography sitting inside the sentence it was citing.

    grammar = CitationGrammar.from_overrides({
        "citation_ref_tags": [
            {"match": r"anime,?\s*Episode\s+([\d.\-]+)", "as": "episode"},
            {"match": r"Chapter\s+([\d.\-]+)", "as": "chapter"},
        ]
    })

    def test_a_prose_locator_becomes_a_marker(self):
        text = strip_markup(
            "Ichigo fights.<ref>''Bleach'' manga; Chapter 686, pages 4-5</ref>",
            works=self.grammar,
        )
        assert text == "Ichigo fights.(Chapter 686)"

    def test_the_bibliography_never_lands_in_the_sentence(self):
        # The regression guard: this used to read
        # "Ichigo fights. Bleach anime, Episode 179 He wins."
        page = (
            "==S==\nIchigo fights.<ref name=\"e179\">''Bleach'' anime, "
            "Episode 179</ref> He wins.\n"
        )
        _, sections = split_sections(page, works=self.grammar)
        assert sections[0].text == "Ichigo fights.(Episode 179) He wins."
        assert "Bleach" not in sections[0].text

    def test_a_name_only_reuse_resolves_to_its_definition(self):
        # Hunterpedia reuses 243 times against 141 definitions; reading only the
        # definition sites would leave most cited lines unsourced.
        page = (
            "==S==\nOne.<ref name=\"c1\">''Bleach'' manga; Chapter 1</ref> "
            "Two.<ref name=\"c1\"/> Three.<ref name=\"c1\"></ref>\n"
        )
        _, sections = split_sections(page, works=self.grammar)
        assert sections[0].text == "One.(Chapter 1) Two.(Chapter 1) Three.(Chapter 1)"

    def test_a_reference_that_locates_nothing_renders_nothing(self):
        # Cover art, interviews and shop listings carry no chapter, and their
        # text is not content.
        text = strip_markup(
            "Art.<ref>[[:File:Cover.png|Volume 23 cover art]]</ref>",
            works=self.grammar,
        )
        assert text == "Art."

    def test_ref_tags_are_removed_even_without_a_grammar(self):
        assert strip_markup("A.<ref>''Bleach'' manga; Chapter 686</ref> B.") == "A. B."


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
