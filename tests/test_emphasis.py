"""What a page names, as against what it mentions.

`Every cursed technique of Sukuna` returned 16 for an answer of 10, and the six
extras -- `Metamorphosis`, `Enchain`, `Enma`, `Totality`, `Incarnation`,
`Cursed Energy Reinforcement` -- are all names his page uses in passing rather
than names it gives him. No field separates them: none has a page of its own,
so `type` and `user` are both silent.

The wiki separates them by formatting. Every technique it credits him with is
written either as a bolded wikilink or as the bolded first argument of
`{{Nihongo}}`, the template it uses to gloss a name in Japanese.

**Plain `'''bold'''` is not the signal**, and that is the trap these tests
exist for. Measured on Sukuna's page, plain bold matches 59 strings and
catches four of the six intruders, because a wiki bolds for emphasis
mid-sentence too. The two formal naming forms match 0 of the 6.

Nor is "has a page of its own" the same signal.
`Cursed Technique Lapse - Maximum Cursed Energy Output: Blue` has no page
anywhere on this wiki and is named in bold on Gojo's, so a page-existence rule
would delete a real technique.
"""

from __future__ import annotations

import pytest

from scriptengine.ingest.wikitext import emphasised_names


def folded(text: str) -> set[str]:
    return {name.lower() for name in emphasised_names(text)}


class TestTheNamingForms:
    def test_a_bolded_wikilink_is_a_name(self):
        assert "cleave" in folded("He follows with '''[[Cleave]]''' at range.")

    def test_a_bolded_nihongo_argument_is_a_name(self):
        text = "{{Nihongo|'''[[Malevolent Shrine]]'''|伏魔御廚子|Fukuma Mizushi}}"
        assert "malevolent shrine" in folded(text)

    def test_a_nihongo_name_with_no_page_is_still_a_name(self):
        """The case a page-existence rule would get wrong."""
        text = (
            "{{Nihongo|'''Cursed Technique Lapse - Maximum Cursed Energy Output:"
            " Blue'''|術式順転『蒼』最大出力|...}}"
        )
        assert "cursed technique lapse - maximum cursed energy output: blue" in folded(text)

    def test_a_piped_link_yields_both_target_and_label(self):
        """The bank spells some entries as the target and some as the label."""
        names = folded("'''[[Cursed Womb: Death Painting|Death Painting]]'''")
        assert "cursed womb: death painting" in names
        assert "death painting" in names

    def test_bold_italic_counts(self):
        assert "shrine" in folded("'''''[[Shrine]]'''''")


class TestWhatIsNotAName:
    def test_plain_bold_is_emphasis_not_a_name(self):
        """The whole reason this is narrower than `'''bold'''`.

        Sukuna's page bolds `Enma` and `Metamorphosis` mid-sentence; plain bold
        would admit four of the six intruders this signal exists to remove.
        """
        assert folded("his '''metamorphosis''' was complete") == set()

    def test_an_unbolded_link_is_a_mention(self):
        assert folded("undone by [[Cursed Energy Reinforcement]] alone") == set()

    def test_a_bolded_clause_is_not_a_name(self):
        """A sentence in bold is emphasis. The longest real name measured is
        eight words, so the cap only excludes prose."""
        long = " ".join(["word"] * 20)
        assert folded(f"'''[[{long}]]'''") == set()

    def test_empty_and_unformatted_text_name_nothing(self):
        assert emphasised_names("") == []
        assert emphasised_names("no markup here at all") == []


class TestShape:
    def test_names_are_deduplicated_case_insensitively(self):
        text = "'''[[Shrine]]''' ... later '''[[shrine]]''' again"
        assert len(emphasised_names(text)) == 1

    def test_order_is_the_page_order(self):
        text = "'''[[Cleave]]''' then '''[[Dismantle]]''' then '''[[Spiderweb]]'''"
        assert emphasised_names(text) == ["Cleave", "Dismantle", "Spiderweb"]

    @pytest.mark.parametrize(
        "markup", ["'''[[  Cleave  ]]'''", "'''[[Cleave]]'''", "''' [[Cleave]] '''"]
    )
    def test_whitespace_is_trimmed(self, markup):
        assert "cleave" in folded(markup)
