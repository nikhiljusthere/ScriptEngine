"""Tests for the script-writing loop: bundle -> draft -> verify -> repair -> save."""

from __future__ import annotations

from pathlib import Path

import pytest

from scriptengine.api.context import render_prompt
from scriptengine.config import Settings, series_paths
from scriptengine.script import writer

CLEAN_SCRIPT = (
    "**Shibuya Incident Explained**\n\n"
    "* **The Sealing**\n\n"
    "The curtain falls on Shibuya and Gojo is sealed. (Chapter 1)"
)


MID = "**Mid Draft**\n\n" + ("word " * 3000)
LONG = "**Shibuya Incident**\n\n" + ("word " * 6000)
OVER = "**Over Draft**\n\n" + ("word " * 7000)
SEC_3000 = "* **A New Section**\n\n" + ("word " * 3000)
SEC_300 = "* **A Small Section**\n\n" + ("word " * 300)
SECTIONED_OVER = (
    "**Over Draft**\n\n"
    "* **Part One**\n\n"
    + ("word " * 3000)
    + "\n\n* **Part Two**\n\n"
    + ("word " * 2500)
    + "\n\n* **Part Three**\n\n"
    + ("word " * 2000)
)


class FakeClient:
    """Stand-in for LLMClient: returns canned answers, records the prompts."""

    def __init__(self, *answers: str) -> None:
        self.answers = list(answers)
        self.calls: list[str] = []

    def complete(self, prompt, system="", temperature=0.2, max_tokens=1024):
        self.calls.append(prompt)
        return self.answers.pop(0) if self.answers else CLEAN_SCRIPT


def bundle(**overrides) -> dict:
    base = {
        "series": "jjk",
        "mode": "narrative",
        "subject": "Shibuya Incident",
        "beats": [
            {
                "order": 1,
                "title": "The Sealing",
                "doc_title": "Shibuya Incident",
                "text": "A curtain is cast around Shibuya.",
                "source_span": "Chapter 83, Episode 32",
            }
        ],
        "participants": ["Satoru Gojo"],
        "facts": [],
        "truncated": False,
        "beats_available": 1,
        "tokens_used": 100,
    }
    base.update(overrides)
    return base


@pytest.fixture
def fake_client(monkeypatch):
    """Patch the module's LLMClient so no test touches a model."""
    client = FakeClient()
    monkeypatch.setattr(writer, "LLMClient", lambda *a, **k: client)
    return client


class TestStripFence:
    def test_whole_document_fence_is_removed(self):
        wrapped = "```markdown\n" + CLEAN_SCRIPT + "\n```"
        assert writer.strip_fence(wrapped) == CLEAN_SCRIPT

    def test_plain_text_passes_through(self):
        assert writer.strip_fence(CLEAN_SCRIPT) == CLEAN_SCRIPT

    def test_fence_with_preamble_is_left_alone(self):
        # A preamble means the answer is not just the script; guessing where
        # the script starts inside it would drop the title.
        text = "Here you go:\n```\n" + CLEAN_SCRIPT + "\n```"
        assert writer.strip_fence(text) != CLEAN_SCRIPT


class TestTitleOf:
    def test_extracts_bold_first_line(self):
        assert writer.title_of(CLEAN_SCRIPT) == "Shibuya Incident Explained"

    def test_falls_back_to_empty_without_a_title_line(self):
        assert writer.title_of("* **The Sealing**\n\nprose") == ""


class TestAutoBudget:
    def test_clamps_low(self):
        assert writer.auto_budget(100) == 6000

    def test_scales_with_words(self):
        assert writer.auto_budget(6000) == 48000

    def test_clamps_high(self):
        assert writer.auto_budget(20000) == 60000


class TestWriteScript:
    def test_returns_the_draft(self, fake_client):
        text = writer.write_script(bundle(), words=6000, intro=True)
        assert text == CLEAN_SCRIPT

    def test_prompt_carries_the_rules(self, fake_client):
        writer.write_script(bundle(), words=6000, intro=True)
        prompt = fake_client.calls[0]
        assert "=== VOICE RULES" in prompt
        assert "=== SCRIPT FORMAT" in prompt
        assert "5,500 and 6,500 words" in prompt
        assert "THE LENGTH IS THE CONTRACT" in prompt
        assert "Intro: ON" in prompt

    def test_prompt_states_the_no_intro_choice(self, fake_client):
        writer.write_script(bundle(), words=0, intro=False)
        assert "Intro: OFF" in fake_client.calls[0]


class TestRepairScript:
    def test_findings_reach_the_prompt(self, fake_client):
        report = {
            "findings": [
                {"tag": "(Chapter 999)", "issues": ["no page 'Chapter 999' in the crawl"]}
            ]
        }
        writer.repair_script(CLEAN_SCRIPT, report, bundle())
        prompt = fake_client.calls[0]
        assert "Chapter 999" in prompt
        assert "Chapter 83, Episode 32" in prompt
        assert "Keep every word of the prose unchanged" in prompt


class TestGenerateScript:
    def test_happy_path_verifies_and_reports(self, fake_client):
        # 16 words after the title swap (Explained drops out), then two
        # appended 3,004-word sections: 16 + 3,004 + 3,004 = 6,024, which sits
        # inside the 5,500-6,500 band.
        fake_client.answers = [CLEAN_SCRIPT, SEC_3000, SEC_3000]
        result = writer.generate_script(
            "Shibuya Incident", series="jjk", words=6000, write=False
        )
        assert result["attempts"] == 1
        assert result["title"] == "Shibuya Incident"
        assert result["script"].splitlines()[0] == "**Shibuya Incident**"
        assert result["path"] is None
        assert result["report"]["passed"] is True
        assert result["bundle"]["subject"] == "Shibuya Incident"
        assert result["words"] == 6024
        assert result["target_words"] == 6000
        assert result["expanded"] is True
        assert result["trimmed"] is False
        assert result["length_passes"] == 2

    def test_repairs_until_the_tags_pass(self, fake_client):
        broken = CLEAN_SCRIPT.replace("(Chapter 1)", "(Chapter 999)")
        fake_client.answers = [broken, CLEAN_SCRIPT]
        result = writer.generate_script(
            "Shibuya Incident", series="jjk", words=20, write=False
        )
        assert result["attempts"] == 2
        assert result["report"]["passed"] is True
        assert "no page 'Chapter 999'" in fake_client.calls[1]

    def test_stops_at_max_attempts(self, fake_client):
        broken = CLEAN_SCRIPT.replace("(Chapter 1)", "(Chapter 999)")
        fake_client.answers = [broken, broken, broken, broken]
        result = writer.generate_script(
            "Shibuya Incident", series="jjk", words=20, write=False,
            max_attempts=3,
        )
        assert result["attempts"] == 3
        assert result["report"]["passed"] is False

    def test_writes_to_the_scripts_root(self, fake_client, tmp_path: Path):
        settings = Settings(scripts_root=tmp_path)
        result = writer.generate_script(
            "Shibuya Incident", series="jjk", words=20, settings=settings
        )
        assert result["path"] is not None
        assert result["path"].exists()
        saved = result["path"].read_text(encoding="utf-8").strip()
        assert saved.splitlines()[0] == "**Shibuya Incident**"
        assert "The curtain falls on Shibuya and Gojo is sealed. (Chapter 1)" in saved
        assert result["path"].parent.parent.name.startswith("Video 1 -")

    def test_rewrites_reuse_the_same_folder(self, fake_client, tmp_path: Path):
        settings = Settings(scripts_root=tmp_path)
        first = writer.generate_script(
            "Shibuya Incident", series="jjk", words=20, settings=settings
        )
        second = writer.generate_script(
            "Shibuya Incident", series="jjk", words=20, settings=settings
        )
        assert first["path"] == second["path"]

    def test_title_override_renames_the_script_and_destination(self, fake_client, tmp_path: Path):
        # A regenerate under a new title is a new video; the subject default
        # is what keeps an ordinary regenerate in the same folder.
        settings = Settings(scripts_root=tmp_path)
        result = writer.generate_script(
            "Shibuya Incident", series="jjk", words=20, title="The Night Shibuya Fell",
            settings=settings,
        )
        assert result["title"] == "The Night Shibuya Fell"
        assert result["script"].splitlines()[0] == "**The Night Shibuya Fell**"
        assert "The Night Shibuya Fell" in str(result["path"])

    def test_the_resolved_subject_does_not_rename_the_video(self, fake_client, monkeypatch):
        # The bundle subject is the engine's entity ("Eight-Handled Sword
        # ..."), but the video is the user's topic; the folder must follow the
        # topic, or every regenerate spawns a new video under the entity name.
        def fake_bundle(paths, subject, mode="qa", token_budget=6000, top_k=None, settings=None):
            return {
                "series": "jjk",
                "mode": "narrative",
                "subject": "Eight-Handled Sword Divergent Sila Divine General Mahoraga",
                "beats": [],
                "participants": [],
                "facts": [],
                "truncated": False,
                "beats_available": 0,
                "tokens_used": 1,
            }

        monkeypatch.setattr(writer, "build_context", fake_bundle)
        result = writer.generate_script(
            "Every Fight Mahoraga Has Ever Been In", series="jjk", words=20, write=False
        )
        assert result["title"] == "Every Fight Mahoraga Has Ever Been In"
        assert result["script"].splitlines()[0] == "**Every Fight Mahoraga Has Ever Been In**"

    def test_unindexed_series_raises(self, fake_client):
        with pytest.raises(ValueError, match="not indexed"):
            writer.generate_script(
                "Anything", series="not-a-series", words=6000, write=False
            )

    def test_roster_fallback_to_narrative(self, fake_client):
        # A roster with nothing in it is not an answer; the auto path falls
        # back to narrative, exactly as /context does.
        fake_client.answers = [CLEAN_SCRIPT, LONG]
        result = writer.generate_script(
            "Every Rank of Curse", series="jjk", words=6000, write=False
        )
        assert result["bundle"]["mode"] == "roster" or result["bundle"]["beats"]
        assert render_prompt(result["bundle"]).startswith(f"# {result['bundle']['subject']}")

    def test_bare_character_name_routes_narrative(self, fake_client):
        # A bare name is a lookup for /context but a story for a script: the
        # script path escalates that one case to narrative.
        result = writer.generate_script(
            "Maki Zenin", series="jjk", words=20, write=False
        )
        assert result["bundle"]["mode"] == "narrative"
        assert result["bundle"]["subject"] == "Maki Zenin"

    def test_a_question_stays_a_lookup(self, fake_client):
        # "What is the Prison Realm" is a question; the router's qa verdict
        # survives the script path unchanged.
        mode, routed = writer.route_script(series_paths("jjk"), "What is the Prison Realm")
        assert mode == "qa"
        assert routed.mode == "qa"


class TestWordCount:
    def test_counts_whitespace_tokens(self):
        assert writer.word_count("a b\n\ncc") == 3

    def test_empty_is_zero(self):
        assert writer.word_count("") == 0


class TestExpandScript:
    def test_expansion_prompt_carries_band_shortfall_and_ban(self, fake_client):
        writer.expand_script(CLEAN_SCRIPT, 3000, bundle())
        prompt = fake_client.calls[0]
        assert f"is {writer.word_count(CLEAN_SCRIPT)} words" in prompt
        assert "the target is 3000 words" in prompt
        assert "between 2500 and 3500 words" in prompt
        assert "add at least" in prompt
        assert "never state a fact the context does not carry" in prompt
        assert "Output ONLY the new sections" in prompt

    def test_fenced_expansion_is_stripped(self, fake_client):
        wrapped = "```markdown\n" + CLEAN_SCRIPT + "\n```"
        fake_client.answers = [wrapped]
        result = writer.expand_script(CLEAN_SCRIPT, 3000, bundle())
        assert result == CLEAN_SCRIPT

    def test_no_target_leaves_the_draft_alone(self, fake_client):
        # words=0 means no length ask at all; the loop must not expand.
        result = writer.generate_script(
            "Shibuya Incident", series="jjk", words=0, write=False
        )
        assert result["expanded"] is False
        assert len(fake_client.calls) == 1

    def test_inside_the_band_no_length_pass(self, fake_client):
        fake_client.answers = [LONG]
        result = writer.generate_script(
            "Shibuya Incident", series="jjk", words=6000, write=False
        )
        assert result["expanded"] is False
        assert result["trimmed"] is False
        assert len(fake_client.calls) == 1
        assert result["length_passes"] == 0

    def test_short_draft_is_expanded_until_it_clears_the_band(self, fake_client):
        # 16 words vs 6,000: two appended sections land at 6,024, inside the
        # band. No trim on the way out.
        fake_client.answers = [CLEAN_SCRIPT, SEC_3000, SEC_3000]
        result = writer.generate_script(
            "Shibuya Incident", series="jjk", words=6000, write=False
        )
        assert result["expanded"] is True
        assert result["trimmed"] is False
        assert result["words"] == 6024
        assert len(fake_client.calls) == 3
        assert "script so far" in fake_client.calls[1]
        assert "script so far" in fake_client.calls[2]
        assert result["length_passes"] == 2

    def test_a_model_restating_the_whole_script_is_not_appended(self, fake_client):
        # The expansion contract is "new sections only"; a model that writes
        # the whole script back repeats the title line, which the loop reads
        # as "this is a replacement, not an addition", so the script is never
        # duplicated under itself.
        fake_client.answers = [CLEAN_SCRIPT, CLEAN_SCRIPT]
        result = writer.generate_script(
            "Shibuya Incident", series="jjk", words=6000, write=False
        )
        assert result["script"].count("The curtain falls on Shibuya") == 1
        assert result["expanded"] is True

    def test_still_short_after_the_pass_budget_saves_anyway(self, fake_client):
        # Ten 304-word appended sections reach only ~3,056 of 6,000 and the
        # budget is spent: the script saves out of band, and the report says
        # how far off it is.
        fake_client.answers = [CLEAN_SCRIPT] + [SEC_300] * 10
        result = writer.generate_script(
            "Shibuya Incident", series="jjk", words=6000, write=False
        )
        assert result["expanded"] is True
        assert result["report"]["passed"] is True
        assert result["words"] < result["target_words"]
        assert result["length_passes"] == 10


class TestTrimScript:
    def test_trim_prompt_carries_band_excess_and_ban(self, fake_client):
        writer.trim_script(OVER, 6000, bundle())
        prompt = fake_client.calls[0]
        assert f"is {writer.word_count(OVER)} words" in prompt
        assert "between 5500 and 6500 words" in prompt
        assert "words over" in prompt
        assert "least essential sections" in prompt
        assert "heading lines" in prompt

    def test_overshoot_is_trimmed_once(self, fake_client):
        # 7,000 words clears the low edge so no expansion runs; it exceeds the
        # high edge, so the one trim pass brings it back into the band.
        fake_client.answers = [OVER, LONG]
        result = writer.generate_script(
            "Shibuya Incident", series="jjk", words=6000, write=False
        )
        assert result["expanded"] is False
        assert result["trimmed"] is True
        assert result["words"] == writer.word_count(LONG)
        assert len(fake_client.calls) == 2
        assert "script to trim" in fake_client.calls[1]
        assert result["length_passes"] == 1

    def test_a_trim_that_misses_trims_again(self, fake_client):
        # The first trim undershoots its own job (7,000 stays 7,000); the loop
        # trims again rather than saving an 8,000-word script out of band.
        fake_client.answers = [OVER, OVER, LONG]
        result = writer.generate_script(
            "Shibuya Incident", series="jjk", words=6000, write=False
        )
        assert result["expanded"] is False
        assert result["trimmed"] is True
        assert result["words"] == writer.word_count(LONG)
        assert result["length_passes"] == 2

    def test_trim_deletes_sections_by_heading(self, fake_client):
        # The trim names a section, the loop cuts it out mechanically: 7,511
        # minus Part Three (2,003 words) lands at 5,508, just inside the band,
        # and the surviving sections are untouched.
        fake_client.answers = [SECTIONED_OVER, "* **Part Three**"]
        result = writer.generate_script(
            "Shibuya Incident", series="jjk", words=6000, write=False
        )
        assert result["trimmed"] is True
        assert result["words"] == 5508
        assert "Part Three" not in result["script"]
        assert "Part One" in result["script"]
        assert result["length_passes"] == 1


class TestCutSections:
    def test_deletes_named_sections(self):
        text = "* **A**\n\none\n\n* **B**\n\ntwo\n\n* **C**\n\nthree"
        out = writer.cut_sections(text, ["* **B**"])
        assert out == "* **A**\n\none\n\n* **C**\n\nthree"

    def test_unknown_headings_leave_the_text_alone(self):
        text = "* **A**\n\none\n\n* **B**\n\ntwo"
        assert writer.cut_sections(text, ["* **Nope**"]) == text

    def test_a_section_runs_to_the_end_of_the_script(self):
        text = "* **A**\n\none\n\n* **B**\n\ntwo"
        assert writer.cut_sections(text, ["* **B**"]) == "* **A**\n\none"


class TestApplyTitle:
    def test_replaces_the_models_title_line(self):
        text = writer._apply_title(CLEAN_SCRIPT, "Shibuya Incident")
        assert text.splitlines()[0] == "**Shibuya Incident**"
        assert "The curtain falls on Shibuya" in text

    def test_prepends_when_there_is_no_title_line(self):
        text = writer._apply_title("* **The Sealing**\n\nprose", "Shibuya Incident")
        assert text.splitlines()[0] == "**Shibuya Incident**"
        assert "prose" in text


class TestMakeCleanVersion:
    def test_strips_tags_timestamps_and_covers(self):
        text = (
            "**Title**\n\n"
            "* **The Sealing**\n\n"
            "Gojo is sealed. (Chapter 83, Episode 32) [E32 01:02]\n"
            "He says it plain. [E32 01:10, 01:15]\n\n"
            "[covers 1-3] Ch 83, Ep 32\n"
            "  · the sealing, Ch 83, Ep 32\n"
            "The end. (Chapter 84)\n"
        )
        out = writer.make_clean_version(text)
        assert "(Chapter" not in out
        assert "[E32" not in out
        assert "[covers" not in out
        assert "·" not in out
        assert "Gojo is sealed." in out
        assert "He says it plain." in out
        assert "The end." in out

    def test_prose_is_untouched(self):
        text = "A line. (Chapter 1)\nAnother line. [E1 00:05]\n"
        assert writer.make_clean_version(text) == "A line.\nAnother line.\n"


class TestEnsureCoversBlocks:
    def test_adds_a_block_after_every_three_passages(self):
        text = (
            "**Title**\n\n"
            "one (Chapter 1)\n\ntwo (Chapter 2)\n\nthree (Chapter 3)\n\n"
            "four (Chapter 4)\n\nfive (Chapter 5)\n\nsix (Chapter 6)\n"
        )
        out = writer.ensure_covers_blocks(text)
        assert "[covers 1-3] Ch 1 · Ch 2 · Ch 3" in out
        assert "[covers 4-6] Ch 4 · Ch 5 · Ch 6" in out

    def test_existing_covers_blocks_are_not_clobbered(self):
        text = "**Title**\n\none (Chapter 1)\n\n[covers 1-3] Ch 1\n\ntwo (Chapter 2)\n"
        assert writer.ensure_covers_blocks(text) == text

    def test_repeated_tags_within_a_group_are_deduplicated(self):
        text = (
            "**Title**\n\n"
            "a (Chapter 5, Episode 3)\n\nb (Chapter 5, Episode 3)\n\n"
            "c (Chapter 5, Episode 3)\n"
        )
        out = writer.ensure_covers_blocks(text)
        block = next(line for line in out.splitlines() if line.startswith("[covers"))
        assert block.count("Ch 5") == 1

    def test_generate_script_writes_the_clean_companion(self, fake_client, tmp_path: Path):
        fake_client.answers = [CLEAN_SCRIPT]
        settings = Settings(scripts_root=tmp_path)
        result = writer.generate_script("Shibuya Incident", series="jjk", words=20, settings=settings)
        assert result["clean_path"] is not None
        assert result["clean_path"].name == "Shibuya Incident-clean.md"
        saved_clean = result["clean_path"].read_text(encoding="utf-8")
        assert "(Chapter" not in saved_clean
        assert "The curtain falls on Shibuya" in saved_clean