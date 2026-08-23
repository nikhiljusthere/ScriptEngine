"""Tests for context bundle assembly and rendering."""

from __future__ import annotations

from scriptengine.api.context import (
    MAX_BEAT_CHARS,
    MAX_PARTICIPANTS,
    _capped_beats,
    estimate_tokens,
    render_prompt,
)
from scriptengine.api.rules import writing_rules
from scriptengine.retrieve.citations import EpisodeIndex


def bundle(**overrides) -> dict:
    base = {
        "series": "jjk",
        "mode": "narrative",
        "subject": "Shibuya Incident",
        "beats": [
            {
                "order": 1, "title": "Prologue", "doc_title": "Shibuya Incident",
                "breadcrumb": "Prologue", "text": "Kenjaku sought the Prison Realm.",
                "source_span": "Chapter 145, Episode 50",
            },
            {
                "order": 2, "title": "7:00 P.M. Shibuya", "doc_title": "Shibuya Incident",
                "breadcrumb": "Event / Early Stages", "time": "7:00 PM",
                "text": "A curtain is cast around Shibuya.",
                "source_span": "Chapter 83, Episode 32",
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
        assert text.index("Prologue") < text.index("7:00 P.M. Shibuya")

    def test_no_bare_retriever_markers_are_emitted(self):
        # The house rules forbid "[1]" in a script and the retired ComfyUI node
        # stripped them from the context; leaving them in the served prompt only
        # gave the writer something to copy.
        assert "[1] " not in render_prompt(bundle(), rules=False)

    def test_every_beat_states_the_chapters_it_came_from(self):
        # The writer has to end each block with its chapter and episode, and the
        # wiki cites once per paragraph. Without this the block is untaggable.
        text = render_prompt(bundle())
        assert "sourced: Chapter 145, Episode 50" in text
        assert "sourced: Chapter 83, Episode 32" in text

    def test_the_writing_rules_travel_with_the_context(self):
        # They used to live only in a ComfyUI file that is not in this repo, so
        # the direct path served research with no instructions attached.
        text = render_prompt(bundle(), intro=False, words=3000)
        assert "VOICE RULES" in text
        assert "CHAPTER/EPISODE ANNOTATION RULES" in text
        assert "Intro: OFF" in text
        assert "2,500 and 3,500 words" in text
        assert "VOICE RULES" not in render_prompt(bundle(), rules=False)

    def test_a_time_is_shown_when_known(self):
        assert "(7:00 PM)" in render_prompt(bundle())

    def test_facts_carry_their_citation(self):
        # A script whose claims cannot be traced back is one you fact-check by
        # hand, which defeats the point of the whole pipeline.
        text = render_prompt(bundle())
        assert "Grade: Grade 1" in text
        assert "Ref vol=5 page=26" in text

    def test_the_source_page_is_named_once_per_run_of_beats(self):
        # 128 consecutive beats from one page used to print
        # "source: Shibuya Incident" 128 times.
        text = render_prompt(bundle())
        assert text.count("### Shibuya Incident") == 1

    def test_truncation_is_stated_rather_than_silent(self):
        text = render_prompt(bundle(truncated=True, beats_available=17))
        assert "truncated" in text and "17" in text

    def test_qa_mode_labels_its_section_differently(self):
        assert "## Sources" in render_prompt(bundle(mode="qa"))
        assert "## Events in order" in render_prompt(bundle(mode="narrative"))

    def test_a_bundle_with_no_facts_still_renders(self):
        text = render_prompt(bundle(facts=[]))
        assert "Established facts" not in text
        assert "Prologue" in text

    def test_a_roster_renders_its_members_grouped(self):
        text = render_prompt(
            bundle(
                mode="roster",
                beats=[],
                basis="Cursed Spirits (class)",
                groups=["Grade 2", "Special Grade"],
                members=[
                    {
                        "name": "Ko-Guy", "group": "Grade 2",
                        "debut": "(Chapter 86, Episode 32)",
                        "facts": [{"field": "Grade", "value": "Grade 2"}],
                        "text": "A cursed spirit fought in Yasohachi Bridge.",
                        "source_span": "Chapter 86, Episode 32",
                    },
                    {
                        "name": "Jogo", "group": "Special Grade",
                        "debut": "(Chapter 10, Episode 5)",
                        "facts": [{"field": "Grade", "value": "Special Grade"}],
                        "text": "A volcanic cursed spirit.",
                        "source_span": "Chapter 10, Episode 5",
                    },
                ],
            )
        )
        assert "### Grade 2" in text and "### Special Grade" in text
        assert "debut: (Chapter 86, Episode 32)" in text
        assert text.index("Ko-Guy") < text.index("Jogo")

    def test_a_multiline_fact_value_stays_on_one_line(self):
        # Naoya Zenin's `relatives` is twelve names on twelve lines.
        text = render_prompt(
            bundle(facts=[{
                "entity": "Naoya Zenin", "field": "Relatives",
                "value": "Naobito Zenin\nMaki Zenin\nMai Zenin", "citation": "",
            }])
        )
        assert "Naobito Zenin / Maki Zenin / Mai Zenin" in text


class TestBeatSplitting:
    # A section cites itself once, in its last paragraph. Slicing the raw text
    # at paragraph ends is why 60 of 128 beats in a fetched bundle came back
    # with no citation at all: every earlier slice lost the reference.

    def long_beat(self, sentences: int = 200) -> dict:
        text = " ".join(f"Sentence number {n} of the account." for n in range(sentences))
        return {
            "order": 1, "title": "Prologue", "doc_title": "Shibuya Incident",
            "breadcrumb": "Prologue", "text": f"{text}(Chapter 145, Episode 50)",
        }

    def test_a_long_beat_is_split(self):
        parts = _capped_beats([self.long_beat()])
        assert len(parts) > 1
        assert all(len(part["text"]) <= MAX_BEAT_CHARS + 200 for part in parts)

    def test_every_part_of_a_split_beat_stays_sourced(self):
        parts = _capped_beats([self.long_beat()])
        assert all(part["source_span"] for part in parts)
        assert all("Chapter 145" in part["source_span"] for part in parts)

    def test_parts_are_renumbered_in_order(self):
        parts = _capped_beats([self.long_beat()])
        assert [part["order"] for part in parts] == list(range(1, len(parts) + 1))

    def test_a_short_beat_is_left_whole_and_still_sourced(self):
        beat = {
            "order": 1, "title": "Prologue", "doc_title": "Shibuya Incident",
            "breadcrumb": "Prologue", "text": "He was sealed.(Chapter 90)",
        }
        parts = _capped_beats([beat], EpisodeIndex({"90": "35"}))
        assert len(parts) == 1
        assert parts[0]["source_span"] == "Chapter 90, Episode 35"

    def test_a_beat_the_wiki_never_cited_reports_no_span(self):
        beat = {
            "order": 1, "title": "Trivia", "doc_title": "Shibuya Incident",
            "breadcrumb": "Trivia", "text": "The arc is popular.",
        }
        assert _capped_beats([beat])[0]["source_span"] == ""


class TestWritingRules:
    def test_the_script_format_block_is_served(self):
        rules = writing_rules(intro=True, words=6000)
        assert "=== SCRIPT FORMAT: a narrative script is a story, not a dump ===" in rules
        assert "through-line" in rules
        assert "flashback" in rules

    def test_the_choice_lines_still_render(self):
        rules = writing_rules(intro=False, words=3000)
        assert "Intro: OFF" in rules
        assert "Length contract: the script must be between" in rules
        assert "2,500 and 3,500 words" in rules


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


class TestBattleFactsReachTheQaBundle:
    """A named battle's infobox is in the qa bundle, rank or no rank.

    The battle title `Yuji Itadori vs. Panda` never links from the query
    (`link_entities` tokenises `vs.` apart from the stored alias), so its
    arc/place/outcome/chapters facts were missing from every bundle about the
    fight unless the vector rank happened to surface the page. The
    phrasing-robustness requirement (2026-08-24: every natural phrasing of a
    question must be answerable) pays for those facts up front.
    """

    def test_a_battle_field_answer_is_in_the_bundle(self):
        import pytest

        from scriptengine.api.context import build_context
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        out = build_context(
            paths, "Where did Yuji Itadori vs. Panda take place?", mode="qa"
        )
        rendered = [f"{f.get('field')} {f.get('value')}" for f in out["facts"]]
        assert any("Gachinko Fight Club" in line for line in rendered), rendered
