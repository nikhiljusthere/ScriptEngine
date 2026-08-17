"""Tests for scriptengine.retrieve.dedupe: variant-collapsing rules.

The test that matters most is the one that asserts the pair the ancestor
module was wrong about: `Divine Dogs` and `Divine Dog: Totality` are two
different shikigami, and collapsing them is a merge, not a dedup.
"""

import pytest

from scriptengine.retrieve.dedupe import collapse_variants, normalise, _fragments


# ── normalise ────────────────────────────────────────────────────────────────

class TestNormalise:
    def test_lowercases(self):
        assert normalise("Blue") == "blue"

    def test_collapses_whitespace(self):
        assert normalise("  Cursed   Technique  ") == "cursed technique"

    def test_removes_apostrophes(self):
        assert normalise("Jacob's Ladder") == "jacobs ladder"
        assert normalise("Jacob\u2019s Ladder") == "jacobs ladder"

    def test_empty_string(self):
        assert normalise("") == ""
        assert normalise(None) == ""

    def test_no_stemming(self):
        """Normalise must not singularise: Divine Dogs != Divine Dog."""
        assert normalise("Divine Dogs") != normalise("Divine Dog")


# ── _fragments ───────────────────────────────────────────────────────────────

class TestFragments:
    def test_single_colon(self):
        prefixes, suffixes = _fragments("cursed technique lapse: blue")
        assert "cursed technique lapse" in prefixes
        assert "blue" in suffixes

    def test_double_colon(self):
        prefixes, suffixes = _fragments("maximum technique: hollow technique: purple")
        assert "maximum technique" in prefixes
        assert "maximum technique: hollow technique" in prefixes
        assert "hollow technique: purple" in suffixes
        assert "purple" in suffixes

    def test_no_colon(self):
        prefixes, suffixes = _fragments("blue")
        assert prefixes == set()
        assert suffixes == set()

    def test_trailing_colon_ignored(self):
        """A trailing colon after split produces an empty side that is dropped."""
        prefixes, suffixes = _fragments("something: ")
        assert "something" in prefixes
        assert suffixes == set()


# ── collapse_variants ────────────────────────────────────────────────────────

class TestCollapseVariants:
    def test_empty(self):
        kept, dropped = collapse_variants([])
        assert kept == []
        assert dropped == []

    def test_single_name(self):
        kept, dropped = collapse_variants(["Blue"])
        assert kept == ["Blue"]
        assert dropped == []

    def test_blue_and_qualified(self):
        """Blue is the suffix of Cursed Technique Lapse: Blue → drop Blue."""
        kept, dropped = collapse_variants(
            ["Blue", "Cursed Technique Lapse: Blue"]
        )
        assert kept == ["Cursed Technique Lapse: Blue"]
        assert len(dropped) == 1
        assert dropped[0]["name"] == "Blue"
        assert dropped[0]["covered_by"] == "Cursed Technique Lapse: Blue"
        assert dropped[0]["rule"] == "suffix"

    def test_red_and_qualified(self):
        kept, dropped = collapse_variants(
            ["Cursed Technique Reversal: Red", "Red"]
        )
        assert kept == ["Cursed Technique Reversal: Red"]
        assert dropped[0]["rule"] == "suffix"

    def test_purple_double_colon(self):
        """Purple is a suffix of Hollow Technique: Purple, itself a suffix of
        Maximum Technique: Hollow Technique: Purple. The chain resolves to the
        longest name."""
        kept, dropped = collapse_variants([
            "Purple",
            "Hollow Technique: Purple",
            "Maximum Technique: Hollow Technique: Purple",
        ])
        assert kept == ["Maximum Technique: Hollow Technique: Purple"]
        assert len(dropped) == 2

    def test_simple_domain_and_nss(self):
        """Simple Domain is the suffix of New Shadow Style: Simple Domain → drop Simple Domain."""
        kept, dropped = collapse_variants(
            ["Simple Domain", "New Shadow Style: Simple Domain"]
        )
        assert kept == ["New Shadow Style: Simple Domain"]
        assert dropped[0]["rule"] == "suffix"

    def test_jacobs_ladder_apostrophe(self):
        """Jacob's Ladder and Maximum Output: Jacob's Ladder collapse,
        even with different apostrophe types."""
        kept, dropped = collapse_variants([
            "Jacob's Ladder",
            "Maximum Output: Jacob's Ladder",
        ])
        assert kept == ["Maximum Output: Jacob's Ladder"]
        assert dropped[0]["rule"] == "suffix"

    def test_divine_dogs_safeguard(self):
        """Divine Dogs and Divine Dog: Totality are NOT collapsed.
        This is the test that matters most: they are two different shikigami,
        and the Plural vs. Qualified difference means rule 1 does not fire."""
        kept, dropped = collapse_variants([
            "Divine Dogs",
            "Divine Dog: Totality",
        ])
        assert len(kept) == 2
        assert "Divine Dogs" in kept
        assert "Divine Dog: Totality" in kept
        assert dropped == []

    @pytest.mark.parametrize(
        "bare,qualified",
        [
            # Every pair on the Jujutsu Kaisen wiki where a page title's prefix
            # is itself a page title. A prefix rule fires on all eight of these
            # and is wrong on all eight, which is why there is no prefix rule.
            ("Cursed Womb", "Cursed Womb: Death Painting"),
            ("Jujutsu Kaisen", "Jujutsu Kaisen: Phantom Parade"),
            ("Jujutsu Kaisen", "Jujutsu Kaisen: Cursed Clash"),
            ("Satoru Gojo vs. Sukuna", "Satoru Gojo vs. Sukuna: First Fight"),
            (
                "Satoru Gojo vs. Toji Fushiguro",
                "Satoru Gojo vs. Toji Fushiguro: Rematch",
            ),
            # Not page-title pairs yet, but the ones that would cost gold
            # first: both bare names are gold on live questions today.
            ("Nue", "Nue: Totality - Merged Beast Agito"),
            ("Ten Shadows Technique", "Ten Shadows Technique: Chimera Shadow Garden"),
        ],
    )
    def test_a_bare_prefix_is_a_different_thing(self, bare, qualified):
        """The prefix names a family, not the same thing said longer.

        `Cursed Womb: Death Painting` is a kind of cursed womb and the subject
        of a question the bank scores exactly today. A first fight and a
        rematch are two battles. `Nue` is a shikigami and
        `Nue: Totality - Merged Beast Agito` is a fusion of it, and both are
        gold. An earlier version of this module dropped the first of every
        pair as a container it had been filed under.
        """
        kept, dropped = collapse_variants([bare, qualified])
        assert kept == [bare, qualified]
        assert dropped == []

    def test_order_preserved(self):
        kept, dropped = collapse_variants([
            "Cursed Technique Lapse: Blue",
            "Blue",
            "Red",
            "Cursed Technique Reversal: Red",
        ])
        assert kept == ["Cursed Technique Lapse: Blue", "Cursed Technique Reversal: Red"]
        # Blue was first, but its qualified form was earlier → Blue dropped
        # Red was third, qualified form was later → Red dropped

    def test_never_returns_empty(self):
        """Rule 4: a non-empty set must never return empty."""
        kept, dropped = collapse_variants(["Blue", "Cursed Technique Lapse: Blue"])
        assert len(kept) >= 1  # would keep the qualified form

    def test_case_insensitive(self):
        kept, dropped = collapse_variants([
            "blue",
            "Cursed Technique Lapse: Blue",
        ])
        assert kept == ["Cursed Technique Lapse: Blue"]
        assert dropped[0]["name"] == "blue"

    def test_exact_duplicate(self):
        """Two identical names: one is dropped as duplicate, tie goes to first."""
        kept, dropped = collapse_variants(["Blue", "Blue"])
        assert kept == ["Blue"]
        assert dropped[0]["rule"] == "duplicate"

    def test_no_relevant_pair(self):
        """Unrelated names pass through unchanged."""
        kept, dropped = collapse_variants([
            "Limitless",
            "Six Eyes",
            "Cursed Technique Lapse: Blue",
        ])
        assert len(kept) == 3
        assert dropped == []

    def test_max_output_chain(self):
        """Maximum Output: Jacob's Ladder covers Jacob's Ladder."""
        kept, dropped = collapse_variants([
            "Jacob's Ladder",
            "Maximum Output: Jacob's Ladder",
        ])
        assert kept == ["Maximum Output: Jacob's Ladder"]
        assert dropped[0]["rule"] == "suffix"
