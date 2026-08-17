"""Resolving the curated lists a wiki keeps inside a transclusion.

The crawler never fetches the `Template:` namespace, so a page whose whole
list section is a bare `{{Ten Shadows Shikigami}}` is stored as twenty-eight
characters holding no links at all. Measured on Jujutsu Kaisen, 738 of its
7,601 stored sections are a single template call that renders to nothing, and
the one above expands to 14,248 characters naming all ten of Megumi's
shikigami -- a list the index could not see and no question could reach.

Everything here runs without the network. What `expandtemplates` returns is
the wiki's business; whether the right transclusions are found, replaced, and
left alone on a second pass is this module's, and that is what these cover.
"""

from __future__ import annotations

import json

import pytest

from scriptengine.ingest.templates import (
    TemplateCache,
    declared_lists,
    find_unresolved,
    splice,
)

DECLARED = ("Ten Shadows Shikigami", "Cursed Techniques")


class TestDeclaredLists:
    def test_reads_the_allowlist_in_order(self):
        """Order is kept because a wiki declares its own preference."""
        assert declared_lists(
            {"template_lists": ["Ten Shadows Shikigami", "Cursed Techniques"]}
        ) == DECLARED

    @pytest.mark.parametrize("overrides", [None, {}, {"template_lists": []}])
    def test_a_series_declaring_nothing_resolves_nothing(self, overrides):
        """Off unless asked for: expanding every template would splice
        navboxes, infoboxes and reference lists into the prose."""
        assert declared_lists(overrides) == ()

    def test_blank_entries_are_dropped(self):
        assert declared_lists({"template_lists": ["  ", "X", ""]}) == ("X",)


class TestFindUnresolved:
    def test_finds_a_declared_transclusion(self):
        found = find_unresolved("intro {{Ten Shadows Shikigami}} tail", DECLARED)
        assert [name for name, _s, _e in found] == ["Ten Shadows Shikigami"]

    def test_ignores_a_template_nobody_declared(self):
        """`{{Scroll box}}` appears 318 times on this wiki and is furniture."""
        assert find_unresolved("a {{Scroll box}} b", DECLARED) == []

    def test_the_namespace_prefix_is_stripped(self):
        found = find_unresolved("{{Template:Ten Shadows Shikigami}}", DECLARED)
        assert [name for name, _s, _e in found] == ["Template:Ten Shadows Shikigami".split(":")[-1]]

    def test_case_folds(self):
        """MediaWiki capitalises the first letter, so editors write both."""
        found = find_unresolved("{{ten shadows shikigami}}", DECLARED)
        assert len(found) == 1

    def test_the_span_covers_the_whole_call(self):
        text = "before {{Ten Shadows Shikigami}} after"
        (_name, start, end), = find_unresolved(text, DECLARED)
        assert text[start:end] == "{{Ten Shadows Shikigami}}"


class TestSplice:
    def test_replaces_the_call_with_its_expansion(self):
        out = splice("a {{Ten Shadows Shikigami}} b", {"Ten Shadows Shikigami": "LIST"})
        assert out == "a LIST b"

    def test_lookup_folds_case_like_the_match_does(self):
        """The two disagreed, and a real page raised `KeyError` for it.

        `find_unresolved` matched `{{ten shadows shikigami}}` against the
        declaration and `splice` then looked the name up unfolded, so any page
        spelling a template differently from the declaration crashed the run
        rather than skipping.
        """
        out = splice("a {{ten shadows shikigami}} b", {"Ten Shadows Shikigami": "LIST"})
        assert out == "a LIST b"

    def test_several_calls_all_resolve(self):
        """Spliced last-to-first, so the earlier offset survives the first
        replacement growing the text."""
        out = splice(
            "{{Ten Shadows Shikigami}} mid {{Cursed Techniques}}",
            {"Ten Shadows Shikigami": "A" * 50, "Cursed Techniques": "B"},
        )
        assert out == "A" * 50 + " mid B"

    def test_an_undeclared_template_is_left_alone(self):
        text = "a {{Scroll box}} b"
        assert splice(text, {"Ten Shadows Shikigami": "LIST"}) == text

    def test_resolving_twice_changes_nothing(self):
        """Idempotence is what makes a re-run cheap: once the bare `{{Name}}`
        is gone, there is nothing left to find."""
        once = splice("a {{Ten Shadows Shikigami}} b", {"Ten Shadows Shikigami": "LIST"})
        twice = splice(once, {"Ten Shadows Shikigami": "LIST"})
        assert once == twice
        assert find_unresolved(once, DECLARED) == []


class TestTemplateCache:
    def test_round_trips(self, tmp_path):
        path = tmp_path / "template_cache.json"
        TemplateCache({"Ten Shadows Shikigami": {"wikitext": "LIST"}}).save(path)
        assert TemplateCache.load(path).entries == {
            "Ten Shadows Shikigami": {"wikitext": "LIST"}
        }

    def test_a_missing_cache_is_an_empty_one(self, tmp_path):
        assert TemplateCache.load(tmp_path / "nothing.json").entries == {}

    def test_a_corrupt_cache_is_an_empty_one(self, tmp_path):
        """A half-written cache must cost one re-fetch, never a failed run."""
        path = tmp_path / "template_cache.json"
        path.write_text("{not json", encoding="utf-8")
        assert TemplateCache.load(path).entries == {}

    def test_a_cache_holding_the_wrong_shape_is_discarded(self, tmp_path):
        path = tmp_path / "template_cache.json"
        path.write_text(json.dumps(["not", "a", "dict"]), encoding="utf-8")
        assert TemplateCache.load(path).entries == {}
