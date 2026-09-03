"""Tests for sourcing a script that already exists.

The first class is the one that matters. Everything else here is behaviour;
that one is a promise, and it is the only thing standing between this feature
and quietly rewriting someone's finished script.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from scriptengine.retrieve.annotate import (
    Annotated,
    Block,
    _agree,
    annotate,
    split_blocks,
    unannotate,
)
from scriptengine.retrieve.citations import EpisodeIndex

SCRIPT = """\
**Every Fight Mahoraga Has Ever Been In**

There is a rule in Jujutsu Kaisen that nobody says out loud. If you beat
Mahoraga, you are the strongest, and three fighters have managed it.

* **The Shikigami Nobody Could Tame**

Start with the name, because the name is a warning label. It is the most
powerful shikigami the Ten Shadows Technique can summon, and the only one that
comes with a catch.

Short line.

*References:*
Episode 41
"""


@dataclass
class FakePassage:
    """Enough of `hybrid.Passage` to exercise agreement."""

    text: str = ""
    parent_text: str = ""
    doc_title: str = "Shibuya Incident"
    score: float = 1.0


class TestTheWordsNeverChange:
    """The guarantee. If this class fails, the feature is unshippable."""

    def test_a_cited_script_reduces_back_to_the_original(self):
        blocks = split_blocks(SCRIPT)
        for block in blocks:
            if block.kind == "prose":
                block.tag = "(Chapter 118, Episode 41)"
        assert unannotate(Annotated(blocks=blocks).text) == SCRIPT

    def test_splitting_alone_loses_nothing(self):
        blocks = split_blocks(SCRIPT)
        assert "\n".join(b.text for b in blocks) == SCRIPT

    def test_blank_lines_and_spacing_survive(self):
        script = "One\n\n\nTwo\n   \nThree"
        assert "\n".join(b.text for b in split_blocks(script)) == script

    def test_untagged_blocks_are_returned_byte_for_byte(self):
        blocks = split_blocks(SCRIPT)          # no tags assigned at all
        assert Annotated(blocks=blocks).text == SCRIPT

    def test_unannotate_leaves_a_writers_own_tag_alone(self):
        # A tag inside the prose, not appended at the end, is the writer's.
        line = "He was sealed (Chapter 90, Episode 35) and then freed."
        assert unannotate(line) == line

    def test_unannotate_removes_only_the_trailing_tag(self):
        line = "He was sealed (Chapter 90) and freed. (Chapter 221, Episode 60)"
        assert unannotate(line) == "He was sealed (Chapter 90) and freed."


class TestBlockSplitting:
    def test_the_title_is_not_prose(self):
        assert split_blocks("**A Title**")[0].kind == "heading"

    def test_a_section_heading_is_not_prose(self):
        assert split_blocks("* **The Wheel**")[0].kind == "heading"

    def test_a_references_block_is_not_prose(self):
        assert split_blocks("*References:*")[0].kind == "heading"

    def test_narration_is_prose(self):
        blocks = [b for b in split_blocks(SCRIPT) if b.kind == "prose"]
        assert any("warning label" in b.text for b in blocks)


class TestAgreement:
    index = EpisodeIndex({"118": "41"})

    def passages(self, *bodies):
        return [FakePassage(parent_text=b) for b in bodies]

    def test_a_locator_two_passages_agree_on_is_used(self):
        tag, sources = _agree(
            self.passages("He fought.(Chapter 118)", "It healed.(Chapter 118)"),
            self.index, min_agreement=2, min_score=None,
        )
        assert tag == "(Chapter 118, Episode 41)"
        assert sources == ["Shibuya Incident"]

    def test_one_passage_alone_is_not_agreement(self):
        tag, _ = _agree(
            self.passages("He fought.(Chapter 118)", "Unrelated prose."),
            self.index, min_agreement=2, min_score=None,
        )
        assert tag == ""

    def test_hits_that_disagree_produce_nothing(self):
        # Four passages naming four chapters is a block this cannot source, and
        # an untagged line is honest where a guessed chapter is not.
        tag, _ = _agree(
            self.passages(
                "A.(Chapter 10)", "B.(Chapter 55)", "C.(Chapter 90)", "D.(Chapter 200)"
            ),
            self.index, min_agreement=2, min_score=None,
        )
        assert tag == ""

    def test_a_span_is_rendered_when_several_tie(self):
        # `attribute` credits one locator per sentence, so a tie needs the
        # chapters in separate sentences rather than side by side.
        tag, _ = _agree(
            self.passages(
                "A.(Chapter 118) B.(Chapter 119)", "C.(Chapter 118) D.(Chapter 119)"
            ),
            self.index, min_agreement=2, min_score=None,
        )
        assert tag == "(Chapters 118 and 119, Episode 41)"

    def test_low_scoring_passages_are_ignored(self):
        weak = [FakePassage(parent_text="A.(Chapter 118)", score=0.1) for _ in range(3)]
        tag, _ = _agree(weak, self.index, min_agreement=2, min_score=0.5)
        assert tag == ""

    def test_nothing_retrieved_is_not_an_error(self):
        assert _agree([], self.index, min_agreement=2, min_score=None) == ("", [])


class TestBlocksLeftAlone:
    def test_a_block_that_already_cites_itself_is_untouched(self):
        from scriptengine.retrieve.annotate import _is_taggable

        block = Block(
            text="He took the body.(Chapter 145, Episode 50) " + "word " * 20,
            kind="prose",
        )
        assert not _is_taggable(block)

    def test_a_short_line_is_not_retrieved_against(self):
        from scriptengine.retrieve.annotate import _is_taggable

        assert not _is_taggable(Block(text="Short line.", kind="prose"))

    def test_a_real_paragraph_is(self):
        from scriptengine.retrieve.annotate import _is_taggable

        assert _is_taggable(Block(text="word " * 30, kind="prose"))


class TestSummary:
    def test_counts_describe_what_happened(self):
        blocks = split_blocks(SCRIPT)
        for block in blocks:
            if block.kind == "prose":
                block.tag = "(Chapter 1)"
                break
        summary = Annotated(blocks=blocks).summary()
        assert summary["tagged"] == 1
        assert summary["untagged"] == summary["prose_blocks"] - 1
