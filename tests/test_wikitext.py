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
    infobox_candidates,
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
        # still points at a Category page, not an article. These produced
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
        # Citations keep a short locator, (Volume 5), not the verbose
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
    # references: a wrong chapter number available to every script.

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
        # No overrides means no qualifiers, which is the previous behaviour,
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

    def test_nihongo_keeps_every_argument_english_kanji_and_romaji(self):
        # Keep-all (not longest, not first): the romaji (third position) is the
        # locator a script cites the name by, and dropping it made "What is the
        # romaji of X?" unservable. Longest-arg would have returned the kanji.
        assert strip_markup("{{Nihongo|Revealing One's Hand|情報の開示|Jōhō}}") == (
            "Revealing One's Hand 情報の開示 Jōhō"
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


class TestScrollBox:
    """`{{Scroll box}}` is a transparent template: its character list is prose.

    The list arrives either positionally or as a named `|content=` argument. The
    named form used to route into `named`, leaving `positional` empty, so the
    whole list was dropped -- 83 chapter "Characters in Order of Appearance"
    sections (~830 names) vanished at index time. These pin the fix and its
    scoping (a box's height/width/name are layout and must not reach prose).
    """

    def test_a_named_content_list_is_kept(self):
        # The bug: `|content=` left `positional` empty, so nothing was kept.
        assert strip_markup(
            "{{Scroll box\n|content=\n*[[Megumi Fushiguro]]\n*[[Sukuna]]\n}}"
        ) == "Megumi Fushiguro\nSukuna"

    def test_a_positional_list_is_still_kept(self):
        assert strip_markup(
            "{{Scroll box| *[[Megumi Fushiguro]] *[[Sukuna]] }}"
        ) == "Megumi Fushiguro *Sukuna"

    def test_layout_parameters_never_reach_the_prose(self):
        out = strip_markup(
            "{{Scroll box|content= *[[Megumi Fushiguro]]\n|height=200px\n|width=100px}}"
        )
        assert out == "Megumi Fushiguro"
        for junk in ("200px", "100px", "height", "width"):
            assert junk not in out

    def test_a_bare_scroll_box_still_yields_nothing(self):
        # The existing contract: a box carrying no list is furniture, whether or
        # not it also sets layout parameters.
        assert strip_markup("{{Scroll box}}") == ""
        assert (
            strip_markup("{{Scroll box|height=200px|width=100px|name=Chapter 59}}")
            == ""
        )


class TestTables:
    """Tables carry content on a Fandom wiki, not decoration."""

    def test_table_content_is_kept(self):
        # Deleting tables with `\{\|.*?\|\}` silently dropped Todo's entire
        # Cursed Technique section: 185 words of the page's most factual prose.
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
        assert " | " not in flatten_tables(table)

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
        found = find_infobox(self.INFOBOX)
        assert found is not None
        _, params = found
        facts = {f.key: f for f in facts_from_infobox(params)}

        assert facts["name"].value == "Aoi Todo"
        # The link target is canonical while the display name is what readers see.
        assert facts["affiliation"].value == "Kyoto High"
        assert facts["affiliation"].links[0].target == "Kyoto Metropolitan College"
        # The citation is captured but stripped out of the value.
        assert facts["age"].value == "18"
        assert facts["age"].citations[0].params["page"] == "36-37"

    def test_presentational_parameters_are_not_facts(self):
        found = find_infobox(self.INFOBOX)
        assert found is not None
        _, params = found
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
        found = find_infobox("{{Infobox|class = Grade 1}}")
        assert found is not None
        _, params = found
        (fact,) = facts_from_infobox(params, labels={"class": "Grade"})
        assert fact.key == "class" and fact.label == "Grade"


class TestColonFoldedTemplateNames:
    """F1 (plan MARVEL_100_PLAN.md §1 L7): the space after a namespace colon.

    The Marvel Database writes `{{Marvel Database: Character Template}}` with
    a space after the colon, while the override alias key and the API title
    carry none. MediaWiki folds the space, so both spellings are one template
    and the lookup must not split on it. Measured 2026-09-25: character
    pages stored `type=character, facts=0` while the closed-box types
    (comic 25 facts, event 24) extracted fine.
    """

    PAGE = (
        "{{Marvel Database: Character Template\n"
        "|Name = Peter Parker\n"
        "|CurrentAlias = Spider-Man\n"
        "|Affiliation = Earth-616\n"
        "}}\n"
        "Prose follows."
    )

    def test_the_text_side_matches_the_unspaced_alias_key(self):
        found = find_infobox(
            self.PAGE, known_templates={"Marvel Database:Character Template"}
        )
        assert found is not None
        assert found[0] == "Marvel Database:Character Template"
        assert found[1]["name"] == "Peter Parker"

    def test_the_spaced_alias_key_matches_too(self):
        found = find_infobox(
            self.PAGE, known_templates={"Marvel Database: Character Template"}
        )
        assert found is not None and found[0] == "Marvel Database:Character Template"

    def test_candidates_are_returned_in_folded_form(self):
        page = (
            "{{Marvel Database: Character Template\n"
            "|Name = A\n"
            "|Age = 1\n"
            "|Race = Human\n"
            "}}\n"
        )
        assert infobox_candidates(page) == [
            ("Marvel Database:Character Template", 3)
        ]

    def test_the_plain_template_prefix_still_strips(self):
        # Folding must not break the existing `Template:X` namespace handling.
        found = find_infobox(
            "{{Template: Character Infobox|name = A|class = 1|race = Human}}",
            known_templates={"Character Infobox"},
        )
        assert found is not None and found[0] == "Character Infobox"


class TestUnclosedLead:
    """F2 (plan MARVEL_100_PLAN.md §1 L7): the narrative wrapped in the box.

    The character templates open at the top of the page and close at the page
    end, so the lead's first top-level template never closes inside the lead
    and its `History` parameter carries the narrative. The stored lead is that
    parameter's pre-heading text, not the raw parameter block. The branch only
    fires on the unclosed shape, so closed-box wikis (JJK/CSM) are untouched.
    """

    PAGE = (
        "{{Marvel Database: Character Template\n"
        "|Name = Peter Parker\n"
        "|History = Peter Parker is the abridged history note.\n"
        "==Civil War (Event)==\n"
        "Peter fights the battle.\n"
        "}}\n"
    )

    def test_the_lead_is_the_narrative_parameters_pre_heading_text(self):
        lead, sections = split_sections(self.PAGE)
        assert lead == "Peter Parker is the abridged history note."
        assert [s.title for s in sections] == ["Civil War (Event)"]

    def test_the_history_key_is_case_insensitive(self):
        page = (
            "{{Some Template|Name = X\n"
            "|history = The lead note.\n"
            "==Appearance==\n"
            "Tall.\n"
            "}}\n"
        )
        lead, _ = split_sections(page)
        assert lead == "The lead note."

    def test_a_closed_box_is_untouched(self):
        # The JJK/CSM shape: the infobox closes inside the lead, so the lead
        # is exactly what it always was.
        page = (
            "{{Character_Infobox|name = Aoi Todo|class = Grade 1|race = Human}}\n"
            "Lead prose.\n"
            "==Appearance==\n"
            "Tall.\n"
        )
        lead, _ = split_sections(page)
        assert lead == "Lead prose."

    def test_an_unclosed_box_without_a_history_parameter_keeps_the_raw_lead(self):
        # The branch needs the narrative parameter; a malformed page without
        # one falls back to the raw lead exactly as before.
        page = (
            "{{Some Box|name = X\n"
            "==Appearance==\n"
            "Tall.\n"
            "}}\n"
        )
        lead, _ = split_sections(page)
        assert "Some Box" in lead

    def test_an_unclosed_box_on_a_page_without_headings(self):
        page = "{{Some Box|History = Only prose.\n"
        lead, sections = split_sections(page)
        assert lead == "Only prose."
        assert sections == []


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


class TestItemMarkers:
    """Headings a wiki writes without writing a heading.

    `Goku/Power and Abilities` has three `==` headings and names seventy-five
    forms as `;Kaio-ken` definition terms inside one of them. The markers were
    stripped by `_LIST_PREFIX`/`_QUOTES`, so every form was an unmarked line in
    a 113,000-character section and "Every form of Goku" had nothing to read.
    """

    ABILITIES = (
        "==Abilities==\n"
        "He fights well.\n"
        "<center>'''<big>Techniques</big>'''</center>\n"
        ";Kamehameha\nA blue energy blast.\n"
        ";Kaio-ken\nA multiplier learned from King Kai.\n"
        ";Spirit Bomb\nBorrowed energy.\n"
        "<center>'''<big>Forms and Transformations</big>'''</center>\n"
        ";Super Saiyan\nGolden hair.\n"
        ";Super Saiyan 4\nRed fur.\n"
    )

    def _split(self, text, title="Goku/Power and Abilities"):
        from scriptengine.ingest.wikitext import split_sections

        return split_sections(
            text, [], None, item_sections={"power and abilities"}, title=title
        )

    def test_definition_terms_become_sections(self):
        _, sections = self._split(self.ABILITIES)
        titles = [section.title for section in sections]
        assert "Kamehameha" in titles
        assert "Kaio-ken" in titles
        assert "Super Saiyan 4" in titles

    def test_the_group_marker_becomes_the_parent(self):
        _, sections = self._split(self.ABILITIES)
        crumbs = {s.title: s.breadcrumb for s in sections}
        assert crumbs["Kaio-ken"] == "Abilities / Techniques / Kaio-ken"
        assert crumbs["Super Saiyan 4"] == (
            "Abilities / Forms and Transformations / Super Saiyan 4"
        )

    def test_the_parent_keeps_only_its_preamble(self):
        """Otherwise every item's text is stored twice, once under its own
        heading and once under the section it came from."""
        _, sections = self._split(self.ABILITIES)
        abilities = next(s for s in sections if s.title == "Abilities")
        assert "He fights well" in abilities.text
        assert "Golden hair" not in abilities.text

    def test_items_are_marked_so_the_chunker_keeps_them(self):
        _, sections = self._split(self.ABILITIES)
        assert all(s.is_item for s in sections if s.title == "Kaio-ken")
        assert not next(s for s in sections if s.title == "Abilities").is_item

    def test_a_section_the_series_did_not_declare_is_untouched(self):
        """One Piece writes 7,491 of these markers, and its heaviest pages are
        `Chapter 1161` and `Chapters and Volumes`: listings, not abilities."""
        _, sections = self._split(self.ABILITIES, title="Chapter 1161")
        assert [s.title for s in sections] == ["Abilities"]

    def test_one_marker_is_emphasis_rather_than_a_list(self):
        text = "==Abilities==\nHe is strong.\n;Note\nA single stray term.\n"
        _, sections = self._split(text)
        assert [s.title for s in sections] == ["Abilities"]

    def test_a_long_marker_line_is_not_an_ability(self):
        text = (
            "==Abilities==\nLead.\n"
            ";This is a whole sentence someone chose to emphasise for effect\n"
            "Body.\n;Also\nBody.\n;Third\nBody.\n"
        )
        _, sections = self._split(text)
        assert "This is a whole sentence someone chose to emphasise for effect" not in [
            s.title for s in sections
        ]

    def test_standalone_bold_lines_are_items_too(self):
        """Bleach and One-Punch Man use `'''Bold'''` where Dragon Ball uses `;`."""
        text = (
            "==Powers & Abilities==\nLead.\n"
            "'''Getsuga Tensho'''\nA crescent of energy.\n"
            "'''[[Shunpo]]'''\nFlash step.\n"
            "'''Blut Vene'''\nQuincy defence.\n"
        )
        _, sections = split_sections_for_bleach(text)
        titles = [s.title for s in sections]
        assert "Getsuga Tensho" in titles
        assert "Shunpo" in titles
        assert "Blut Vene" in titles


def split_sections_for_bleach(text):
    from scriptengine.ingest.wikitext import split_sections

    return split_sections(
        text, [], None, item_sections={"powers & abilities"}, title="Ichigo Kurosaki"
    )


class TestItemMarkersKeepTheText:
    """Splitting must move text, never lose it.

    The first version skipped the group marker's own span, which dropped
    whatever sat between `'''<big>Techniques</big>'''` and the first `;item`
    under it: 144,345 characters, a fifth of the text, across Dragon Ball's
    23 `Power and Abilities` pages. Citations went with it.
    """

    BODY = (
        "==Abilities==\nLead sentence.\n"
        "<center>'''<big>Techniques</big>'''</center>\n"
        "A paragraph that belongs to the group and not to any item.\n"
        ";Kamehameha\nBlue blast.\n"
        ";Kaio-ken\nA multiplier.\n"
        ";Spirit Bomb\nBorrowed energy.\n"
    )

    def test_no_prose_is_dropped(self):
        from scriptengine.ingest.wikitext import split_sections

        _, plain = split_sections(self.BODY, [], None)
        _, split = split_sections(
            self.BODY, [], None,
            item_sections={"abilities"}, title="Goku/Power and Abilities",
        )
        joined = " ".join(section.text for section in split)
        assert "A paragraph that belongs to the group" in joined
        assert "Borrowed energy" in joined
        assert "Lead sentence" in joined
        # Only the marker lines themselves become titles rather than body text.
        assert len(" ".join(s.text for s in plain)) - len(joined) < 60
