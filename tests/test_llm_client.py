"""The model backend, spoken through opencode.

The subprocess is mocked throughout. These tests are about the three things
that went wrong when the backend changed, none of which need a real call:

* a newline in the message silently truncated it,
* the answer arrives as events rather than as a body,
* a throttled provider has to stop a batch rather than fail three hundred
  pages one at a time.
"""

from __future__ import annotations

import json
import subprocess

import pytest

from scriptengine.llm import client as llm


def _event(kind: str, text: str = "") -> str:
    payload = {"type": kind, "sessionID": "ses_x", "part": {"type": kind}}
    if text:
        payload["part"]["text"] = text
    return json.dumps(payload)


def _stream(*texts: str) -> str:
    lines = [_event("step_start")]
    lines += [_event("text", text) for text in texts]
    lines.append(_event("step_finish"))
    return "\n".join(lines)


class TestFlatten:
    def test_a_newline_would_have_truncated_the_message(self):
        """`opencode run [message..]` is variadic and drops the rest of the line.

        Every extraction prompt arrived as instructions with no passage, and the
        model answered "Provide the passage and I'll return the named abilities
        as JSON" — for every page, silently, as a successful call.
        """
        assert "\n" not in llm._flatten("first line\nsecond line")

    def test_paragraphs_do_not_run_together(self):
        assert llm._flatten("end of one.\n\nStart of two.") == "end of one. | Start of two."

    def test_windows_line_endings_too(self):
        assert "\r" not in llm._flatten("a\r\nb")

    def test_runs_of_spaces_collapse(self):
        assert llm._flatten("a   \t b") == "a b"

    def test_content_survives(self):
        long = "The quick brown fox. " * 200
        assert len(llm._flatten(long)) > 3000


class TestParsing:
    def test_the_answer_is_the_text_events(self):
        assert llm._text_of(_stream('{"abilities": []}')) == '{"abilities": []}'

    def test_several_text_events_join(self):
        assert llm._text_of(_stream("one", "two")) == "one\ntwo"

    def test_log_lines_are_skipped_not_fatal(self):
        noisy = "starting up\n" + _stream("answer") + "\nplugin loaded"
        assert llm._text_of(noisy) == "answer"

    def test_no_text_events_is_empty(self):
        assert llm._text_of(_event("step_start")) == ""
        assert llm._text_of("") == ""


class TestThrottling:
    @pytest.mark.parametrize(
        "output",
        ["Error: rate limit exceeded", "HTTP 429", "Too Many Requests", "quota exhausted"],
    )
    def test_a_throttle_is_recognised(self, output):
        assert llm._looks_throttled(output)

    def test_ordinary_output_is_not(self):
        assert not llm._looks_throttled(_stream('{"abilities": []}'))

    def test_a_throttle_raises_its_own_error(self, monkeypatch, tmp_path):
        """So a batch stops on the first one instead of recording every
        remaining page as a failure and reporting the run as complete."""
        client = llm.LLMClient(workdir=str(tmp_path))
        monkeypatch.setattr(client.__class__, "executable", property(lambda self: "opencode"))
        monkeypatch.setattr(
            subprocess, "run",
            lambda *a, **k: subprocess.CompletedProcess(a, 1, "", "rate limit exceeded"),
        )
        with pytest.raises(llm.LLMRateLimited):
            client.complete("anything")

    @pytest.mark.parametrize(
        "answer",
        [
            "Strength beyond human capacity",
            "his quota of cursed energy",
            "the system was overloaded by the blow",
        ],
    )
    def test_the_models_own_words_are_not_a_throttle(self, monkeypatch, tmp_path, answer):
        """This stopped a working batch on its first page, twice.

        Scanning the whole output for throttle wording caught the assistant's
        prose: an ability described as "beyond human capacity" reads exactly
        like a quota message to a substring match. A throttle appears in a
        failure, never in a successful answer.
        """
        client = llm.LLMClient(workdir=str(tmp_path))
        monkeypatch.setattr(client.__class__, "executable", property(lambda self: "opencode"))
        monkeypatch.setattr(
            subprocess, "run",
            lambda *a, **k: subprocess.CompletedProcess(a, 0, _stream(answer), ""),
        )
        assert client.complete("anything") == answer

    def test_an_error_event_on_a_zero_exit_still_counts(self, monkeypatch, tmp_path):
        """A run can exit 0 and have failed; the failure arrives as an event."""
        stream = "\n".join([
            _event("step_start"),
            json.dumps({"type": "error", "part": {"message": "429 too many requests"}}),
        ])
        client = llm.LLMClient(workdir=str(tmp_path))
        monkeypatch.setattr(client.__class__, "executable", property(lambda self: "opencode"))
        monkeypatch.setattr(
            subprocess, "run",
            lambda *a, **k: subprocess.CompletedProcess(a, 0, stream, ""),
        )
        with pytest.raises(llm.LLMRateLimited):
            client.complete("anything")

    def test_rate_limited_is_catchable_as_unavailable(self):
        """Callers that only know about `LLMUnavailable` must still degrade."""
        assert issubclass(llm.LLMRateLimited, llm.LLMUnavailable)


class TestInvocation:
    def test_the_call_is_shaped_the_way_opencode_expects(self, monkeypatch, tmp_path):
        seen: dict = {}

        def fake_run(command, **kwargs):
            seen["command"] = command
            return subprocess.CompletedProcess(command, 0, _stream("ok"), "")

        client = llm.LLMClient(workdir=str(tmp_path))
        monkeypatch.setattr(client.__class__, "executable", property(lambda self: "opencode"))
        monkeypatch.setattr(subprocess, "run", fake_run)

        assert client.complete("the prompt", system="the system") == "ok"
        command = seen["command"]
        assert command[1] == "run"
        assert "--format" in command and "json" in command
        assert "-m" in command
        # Pinned to a scratch directory: an agent will otherwise read and write
        # whatever is around it, and an index-time pass has no business in the
        # repository.
        assert "--dir" in command
        assert command[command.index("--dir") + 1] == str(tmp_path)
        assert "\n" not in command[-1]

    def test_a_missing_binary_is_reported_not_crashed(self, monkeypatch, tmp_path):
        client = llm.LLMClient(workdir=str(tmp_path))
        monkeypatch.setattr(client.__class__, "executable", property(lambda self: ""))
        assert client.available() is False
        with pytest.raises(llm.LLMUnavailable):
            client.complete("anything")

    def test_a_timeout_is_reported_not_crashed(self, monkeypatch, tmp_path):
        def fake_run(command, **kwargs):
            raise subprocess.TimeoutExpired(command, 1)

        client = llm.LLMClient(workdir=str(tmp_path))
        monkeypatch.setattr(client.__class__, "executable", property(lambda self: "opencode"))
        monkeypatch.setattr(subprocess, "run", fake_run)
        with pytest.raises(llm.LLMUnavailable):
            client.complete("anything")

    def test_an_empty_answer_is_a_failure_not_an_empty_string(self, monkeypatch, tmp_path):
        """Silence read as success is how the newline bug survived a whole run."""
        client = llm.LLMClient(workdir=str(tmp_path))
        monkeypatch.setattr(client.__class__, "executable", property(lambda self: "opencode"))
        monkeypatch.setattr(
            subprocess, "run",
            lambda *a, **k: subprocess.CompletedProcess(a, 0, _event("step_start"), ""),
        )
        with pytest.raises(llm.LLMUnavailable):
            client.complete("anything")
