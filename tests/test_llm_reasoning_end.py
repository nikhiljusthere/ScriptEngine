"""SCRIPTENGINE_LLM_REASONING_END: inline thinking is dropped up to the marker."""
from unittest import mock

from scriptengine.config import Settings
from scriptengine.llm.client import LLMClient


def _reply(content: str):
    response = mock.Mock()
    response.raise_for_status = lambda: None
    response.json = lambda: {"choices": [{"message": {"content": content},
                                          "finish_reason": "stop"}]}
    return response


def _answer(monkeypatch, content: str) -> str:
    client = LLMClient(Settings(llm_backend="local", llm_model="m"))
    with mock.patch("httpx.post", return_value=_reply(content)):
        return client.complete("p")


def test_marker_drops_the_inline_thinking(monkeypatch):
    monkeypatch.setenv("SCRIPTENGINE_LLM_REASONING_END", "</ifm|think>")
    assert _answer(monkeypatch, 'think {"no": 1}\n</ifm|think>\n{"x": 1}') == '{"x": 1}'


def test_unset_leaves_the_answer_alone(monkeypatch):
    monkeypatch.delenv("SCRIPTENGINE_LLM_REASONING_END", raising=False)
    assert _answer(monkeypatch, 'a </ifm|think> b') == 'a </ifm|think> b'
