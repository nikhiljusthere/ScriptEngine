"""The extraction request's server fields (`_effort_body`)."""
from scriptengine.ingest.events import _effort_body


def test_default_is_the_low_reasoning_effort(monkeypatch):
    monkeypatch.delenv("SCRIPTENGINE_EVENTS_REASONING_EFFORT", raising=False)
    monkeypatch.delenv("SCRIPTENGINE_EVENTS_EXTRA_BODY", raising=False)
    assert _effort_body() == {"reasoning_effort": "low"}


def test_extra_body_carries_a_thinking_off_switch(monkeypatch):
    monkeypatch.setenv("SCRIPTENGINE_EVENTS_REASONING_EFFORT", "")
    monkeypatch.setenv(
        "SCRIPTENGINE_EVENTS_EXTRA_BODY",
        '{"chat_template_kwargs": {"enable_thinking": false}}',
    )
    assert _effort_body() == {"chat_template_kwargs": {"enable_thinking": False}}


def test_no_fields_sends_nothing(monkeypatch):
    monkeypatch.setenv("SCRIPTENGINE_EVENTS_REASONING_EFFORT", "")
    monkeypatch.delenv("SCRIPTENGINE_EVENTS_EXTRA_BODY", raising=False)
    assert _effort_body() is None
