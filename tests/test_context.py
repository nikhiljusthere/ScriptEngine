"""Tests for context bundle assembly and rendering."""

from __future__ import annotations

from scriptengine.api.context import (
    MAX_PARTICIPANTS,
    estimate_tokens,
    render_prompt,
)


def bundle(**overrides) -> dict:
    base = {
        "series": "jjk",
        "mode": "narrative",
        "subject": "Shibuya Incident",
        "beats": [
            {
                "order": 1, "title": "Prologue", "doc_title": "Shibuya Incident",
                "breadcrumb": "Prologue", "text": "Kenjaku sought the Prison Realm.",
            },
            {
                "order": 2, "title": "7:00 P.M. Shibuya", "doc_title": "Shibuya Incident",
                "breadcrumb": "Event / Early Stages", "time": "7:00 PM",
                "text": "A curtain is cast around Shibuya.",
            },
        ],
        "participants": ["Satoru Gojo", "Kento Nanami"],
        "facts": [
            {
                "entity": "Aoi Todo", "field": "Grade", "value": "Grade 1",
                "citation": "Ref vol=5 page=26",
            }
        ],
        "truncated": False,
        "beats_available": 2,
        "tokens_used": 100,
    }
    base.update(overrides)
    return base


class TestTokenEstimate:
    def test_longer_text_costs_more(self):
        assert estimate_tokens("a" * 400) > estimate_tokens("a" * 40)

    def test_empty_text_is_never_free(self):
        # Returning 0 would let an unbounded number of empty beats through.
        assert estimate_tokens("") >= 1


class TestRenderPrompt:
    def test_beats_render_in_order(self):
        text = render_prompt(bundle())
        assert text.index("[1] Prologue") < text.index("[2] 7:00 P.M. Shibuya")

    def test_a_time_is_shown_when_known(self):
        assert "(7:00 PM)" in render_prompt(bundle())

    def test_facts_carry_their_citation(self):
        # A script whose claims cannot be traced back is one you fact-check by
        # hand, which defeats the point of the whole pipeline.
        text = render_prompt(bundle())
        assert "Grade: Grade 1" in text
        assert "Ref vol=5 page=26" in text

    def test_each_beat_names_its_source_page(self):
        assert "source: Shibuya Incident" in render_prompt(bundle())

    def test_truncation_is_stated_rather_than_silent(self):
        text = render_prompt(bundle(truncated=True, beats_available=17))
        assert "truncated" in text and "17" in text

    def test_qa_mode_labels_its_section_differently(self):
        assert "## Sources" in render_prompt(bundle(mode="qa"))
        assert "## Events in order" in render_prompt(bundle(mode="narrative"))

    def test_a_bundle_with_no_facts_still_renders(self):
        text = render_prompt(bundle(facts=[]))
        assert "Established facts" not in text
        assert "[1] Prologue" in text


class TestBudgeting:
    def test_the_cast_list_is_capped(self):
        # The Shibuya Incident lists 42 participants; rendering all of them
        # spends budget on a cast list before describing a single event.
        assert MAX_PARTICIPANTS <= 25

    def test_everything_rendered_is_countable(self):
        # Whatever render_prompt emits must be something _narrative_context
        # charged for, or `tokens_used` understates the real prompt.
        text = render_prompt(bundle())
        for participant in bundle()["participants"]:
            assert participant in text
