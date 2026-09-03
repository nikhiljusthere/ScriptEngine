"""Tests for chunking."""

from __future__ import annotations

from scriptengine.index.chunker import (
    chunk_page,
    embeddable,
    render_document_card,
    split_passage,
    split_sentences,
)
from scriptengine.ingest.documents import Fact, Link, Section, WikiPage


def make_page(sections: list[Section] | None = None, facts: list[Fact] | None = None) -> WikiPage:
    return WikiPage(
        title="Aoi Todo",
        url="https://example.fandom.com/wiki/Aoi_Todo",
        page_type="character",
        lead="Aoi Todo is a third-year student at Kyoto Jujutsu High.",
        sections=sections or [],
        facts=facts or [],
    )


def section(title: str, text: str, level: int = 2, path: list[str] | None = None) -> Section:
    # `word_count` is a property on Section, derived from `text`.
    return Section(title=title, level=level, index="1", path=path or [], text=text)


class TestSentences:
    def test_sentences_are_separated(self):
        assert len(split_sentences("Todo is tall. He is strong. He claps.")) == 3

    def test_abbreviations_do_not_split_a_sentence(self):
        # Wiki prose is dense with "Vol. 5", "Ch. 12", "9:15 P.M.".
        assert len(split_sentences("He appears in Vol. 5 of the manga.")) == 1

    def test_a_citation_marker_does_not_glue_two_sentences_together(self):
        # The locator sits between the full stop and the space, so the split
        # never fired and two sentences merged into one chunk, and into one
        # citation, which loses which sentence the reference actually covers.
        parts = split_sentences(
            "He took the body.(Chapter 145, Episode 50) Now known as Pseudo-Geto."
        )
        assert len(parts) == 2
        assert parts[0].endswith("(Chapter 145, Episode 50)")

    def test_the_marker_stays_with_the_sentence_it_cites(self):
        parts = split_sentences("Alpha.(Chapter 10) Beta.(Chapter 20)")
        assert parts == ["Alpha.(Chapter 10)", "Beta.(Chapter 20)"]


class TestPassageSplitting:
    def test_short_text_stays_whole(self):
        assert split_passage("One short sentence here.", 350, 60, 20) == [
            "One short sentence here."
        ]

    def test_long_text_is_split(self):
        text = " ".join(f"This is sentence number {i}." for i in range(120))
        passages = split_passage(text, 100, 20, 10)
        assert len(passages) > 1
        assert all(len(p.split()) <= 160 for p in passages)

    def test_passages_never_begin_mid_sentence(self):
        # Overlap carries whole sentences: a chunk starting "of his hands, Todo
        # can swap" embeds poorly and reads worse when quoted in a script.
        text = " ".join(f"Sentence {i} has several words in it." for i in range(60))
        for passage in split_passage(text, 60, 20, 10):
            assert passage.startswith("Sentence")

    def test_consecutive_passages_overlap(self):
        text = " ".join(f"Sentence number {i} appears here." for i in range(60))
        passages = split_passage(text, 50, 20, 10)
        first_words = set(passages[0].split())
        assert first_words & set(passages[1].split())

    def test_a_trailing_fragment_is_absorbed(self):
        text = " ".join(f"Sentence {i} is here with words." for i in range(41))
        passages = split_passage(text, 60, 10, 25)
        assert all(len(p.split()) >= 25 for p in passages)

    def test_empty_text_yields_nothing(self):
        assert split_passage("", 350, 60, 20) == []


class TestDocumentCard:
    def test_facts_are_rendered_so_search_can_reach_them(self):
        # Facts live in SQLite for exact lookup and here for semantic search.
        # Storing them twice is deliberate: one form is exact, one searchable.
        page = make_page(facts=[
            Fact(key="class", value="Grade 1", label="Grade"),
            Fact(key="hair", value="Black", label="Hair Color"),
        ])
        card = render_document_card(page)
        assert "Grade: Grade 1" in card
        assert "Hair Color: Black" in card

    def test_the_wikitext_key_is_used_when_no_label_exists(self):
        page = make_page(facts=[Fact(key="hair", value="Black")])
        assert "Hair: Black" in render_document_card(page)

    def test_the_card_names_the_page_and_its_type(self):
        card = render_document_card(make_page())
        assert card.startswith("Aoi Todo")
        assert "Type: character" in card


class TestChunkPage:
    def test_all_three_levels_are_produced(self):
        page = make_page(
            sections=[section("Appearance", "Todo is tall. " * 40)],
            facts=[Fact(key="class", value="Grade 1")],
        )
        levels = {chunk.level for chunk in chunk_page(page)}
        assert levels == {0, 1, 2}

    def test_every_chunk_carries_a_real_breadcrumb(self):
        # The regression guard for the previous chunker, whose heading rule
        # never matched: every page became one unnamed section, so no chunk
        # could say where it came from.
        page = make_page(sections=[
            section("Cursed Technique", "Boogie Woogie swaps positions. " * 30,
                    level=3, path=["Abilities and Powers"]),
        ])
        for chunk in chunk_page(page):
            assert chunk.breadcrumb
        deep = [c for c in chunk_page(page) if c.level == 2]
        assert deep[0].breadcrumb == "Abilities and Powers / Cursed Technique"

    def test_passages_point_at_their_section_parent(self):
        page = make_page(sections=[section("Appearance", "Todo is tall. " * 60)])
        chunks = chunk_page(page)
        parents = {c.ordinal for c in chunks if c.level == 1}
        for chunk in (c for c in chunks if c.level == 2):
            assert chunk.parent_ordinal in parents

    def test_ordinals_follow_page_order(self):
        page = make_page(sections=[
            section("First", "Alpha content here. " * 30),
            section("Second", "Beta content here. " * 30),
        ])
        chunks = chunk_page(page)
        assert [c.ordinal for c in chunks] == sorted(c.ordinal for c in chunks)
        firsts = [c for c in chunks if c.breadcrumb == "First"]
        seconds = [c for c in chunks if c.breadcrumb == "Second"]
        assert max(c.ordinal for c in firsts) < min(c.ordinal for c in seconds)

    def test_navigation_sections_are_dropped(self):
        page = make_page(sections=[
            section("References", "Reference text here. " * 30),
            section("Navigation", "Navigation text here. " * 30),
            section("Appearance", "Todo is tall. " * 30),
        ])
        assert {c.breadcrumb for c in chunk_page(page) if c.level == 1} == {"Appearance"}

    def test_a_short_factual_section_is_chunked_not_dropped(self):
        # G15 (2026-08-27): the old 20-word floor silently dropped whole
        # sections -- Kaito Yuki's 19-word Personality section ("Kaito values
        # discipline, and is hostile to Yuji Itadori, whose existence he
        # believes goes against the rules of Jujutsu.") indexed zero chunks
        # and no retrieval path could reach it; 1,660 corpus sections sat
        # under the floor. Only sections with no text of their own are
        # skipped now.
        page = make_page(sections=[
            section("Personality",
                    "Kaito values discipline, and is hostile to Yuji Itadori,"
                    " whose existence he believes goes against the rules of Jujutsu."),
            section("Empty", ""),
        ])
        level1 = [c for c in chunk_page(page) if c.level == 1]
        assert [c.breadcrumb for c in level1] == ["Personality"]
        assert level1[0].text.startswith("Kaito values discipline")

    def test_a_short_trivia_bullet_still_yields_a_passage(self):
        # The 7-word bullet from the 2026-08-25 correction's example must
        # survive as its own level-2 passage.
        page = make_page(sections=[section("Trivia", "His maternal grandfather is Danish.")])
        level2 = [c for c in chunk_page(page) if c.level == 2]
        assert [c.text for c in level2] == ["His maternal grandfather is Danish."]

    def test_entities_are_carried_onto_chunks(self):
        sec = section("Appearance", "Todo stands as tall as Gojo. " * 30)
        sec.links = [Link(target="Satoru Gojo", display="Gojo")]
        page = make_page(sections=[sec])
        assert all(
            "Satoru Gojo" in chunk.entities
            for chunk in chunk_page(page)
            if chunk.level in (1, 2)
        )

    def test_a_page_with_no_sections_still_yields_a_card(self):
        chunks = chunk_page(make_page(facts=[Fact(key="class", value="Grade 1")]))
        assert [c.level for c in chunks] == [0]

    def test_only_levels_zero_and_two_are_embedded(self):
        page = make_page(sections=[section("Appearance", "Todo is tall. " * 40)])
        assert {c.level for c in embeddable(chunk_page(page))} == {0, 2}
