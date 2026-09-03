"""The page-driven accuracy campaign's runner, without a live server.

`page-run` scores one `_*.json` batch against the running API; these tests pin
the parts that must hold before anything is asked of a GPU: where batches live,
that an invalid or missing batch stops the run rather than scoring fewer
questions, and that the triage report names what each failure missed. The HTTP
half is faked by patching `canon_gold.ask`, which is the only place this module
touches the network.
"""

import json

import pytest

from datetime import datetime, timezone

from scriptengine.config import Settings
from scriptengine.eval import canon_gold
from scriptengine.eval.canon_run import CanonRunError
from scriptengine.eval import page_campaign
from scriptengine.eval.page_campaign import batch_path, run


def _fake_health():
    """A server that started just now and serves jjk: passes both refusals."""
    return {"status": "ok", "series": ["jjk"],
            "started": datetime.now(timezone.utc).isoformat()}


def _batch_text() -> str:
    return (
        '{"series": "jjk", "updated": "2026-08-19", "questions": ['
        # A closed set of two.
        '{"id": "jjk-pg-test-001", "kind": "set", '
        '"question": "Every test creature in the campaign?", '
        '"subject": "Test Creature", "scope": "closed", "expect_mode": "roster", '
        '"tier": "wiki", "verified": "2026-08-19", '
        '"sources": ["https://jujutsu-kaisen.fandom.com/wiki/Test_Creatures"], '
        '"answer": [{"item": "Alpha Beast"}, {"item": "Beta Beast"}]},'
        # A fact whose answer must be present in the bundle.
        '{"id": "jjk-pg-test-002", "kind": "fact", '
        '"question": "Who feeds the test creatures?", '
        '"subject": "Test Creature", "scope": "closed", "expect_mode": "qa", '
        '"tier": "wiki", "verified": "2026-08-19", '
        '"sources": ["https://jujutsu-kaisen.fandom.com/wiki/Test_Keepers"], '
        '"answer": [{"item": "Gamma Keeper"}], "accept": "any"}'
        ']}'
    )


@pytest.fixture()
def campaign(tmp_path):
    settings = Settings(questions_root=tmp_path / "questions",
                        reports_root=tmp_path / "reports")
    (tmp_path / "questions").mkdir()
    (tmp_path / "questions" / "_jjk_page_test.json").write_text(
        _batch_text(), encoding="utf-8")
    return settings


def test_batch_path_names_the_file(campaign):
    path = batch_path(campaign, "jjk", "test")
    assert path.name == "_jjk_page_test.json"
    assert path.parent == campaign.questions_root


def test_missing_batch_is_refused(campaign):
    with pytest.raises(CanonRunError, match="no campaign batch"):
        run(series="jjk", slug="absent", settings=campaign)


def test_series_mismatch_is_refused(campaign):
    """A batch filed under the wrong series' name is refused before any call."""
    (campaign.questions_root / "_opm_page_test.json").write_text(
        _batch_text(), encoding="utf-8")  # declares "jjk" inside
    with pytest.raises(CanonRunError, match="declares series"):
        run(series="opm", slug="test", settings=campaign)


def test_dry_run_validates_and_calls_nothing(campaign, monkeypatch):
    def no_network(*args, **kwargs):  # pragma: no cover - must not be reached
        raise AssertionError("dry-run asked the server")

    monkeypatch.setattr(canon_gold, "ask", no_network)
    result = run(series="jjk", slug="test", dry_run=True, settings=campaign)
    assert result["dry_run"] is True
    assert result["sets"] == 1 and result["facts"] == 1


def test_a_malformed_batch_is_refused_before_any_call(campaign, monkeypatch):
    (campaign.questions_root / "_jjk_page_bad.json").write_text(
        '{"series": "jjk", "questions": [{"id": "x"}]}', encoding="utf-8")

    def no_network(*args, **kwargs):  # pragma: no cover - must not be reached
        raise AssertionError("an invalid batch asked the server")

    monkeypatch.setattr(canon_gold, "ask", no_network)
    with pytest.raises(CanonRunError):
        run(series="jjk", slug="bad", settings=campaign)


def _fake_ask_complete():
    """The engine answers both questions exactly right."""
    def ask(series, query, subject=None, top_k=8):
        if query.startswith("Every test creature"):
            return {"members": ["Alpha Beast", "Beta Beast"],
                    "confidence": "declared", "basis": "Test Creatures"}
        return {"context": "Gamma Keeper feeds them.", "confidence": "exact"}
    return ask


def _fake_ask_one_miss():
    """The set comes back with an intruder and one canon item missing."""
    def ask(series, query, subject=None, top_k=8):
        if query.startswith("Every test creature"):
            return {"members": ["Alpha Beast", "Gamma Keeper"],
                    "confidence": "declared", "basis": "Test Creatures"}
        return {"context": "Gamma Keeper feeds them.", "confidence": "exact"}
    return ask


def test_a_complete_batch_reports_complete(campaign, monkeypatch):
    monkeypatch.setattr(page_campaign, "health", lambda: _fake_health())
    monkeypatch.setattr(canon_gold, "ask", _fake_ask_complete())
    result = run(series="jjk", slug="test", settings=campaign)

    assert result["complete"] is True
    assert all(r["passed"] for r in result["results"])
    folder = result["folder"]
    assert (folder / "REPORT.md").exists()
    meta = json.loads((folder / "run.json").read_text(encoding="utf-8"))
    assert meta["complete"] is True and meta["slug"] == "test"


def test_the_report_names_what_each_failure_missed(campaign, monkeypatch):
    monkeypatch.setattr(page_campaign, "health", lambda: _fake_health())
    monkeypatch.setattr(canon_gold, "ask", _fake_ask_one_miss())
    result = run(series="jjk", slug="test", settings=campaign)

    assert result["complete"] is False
    failed = [r for r in result["results"] if not r["passed"]]
    assert len(failed) == 1
    assert failed[0]["missing"] == ["Beta Beast"]

    report = (result["folder"] / "REPORT.md").read_text(encoding="utf-8")
    # The triage sheet must carry the missing item, the intruder that came back
    # in its place, and the source a gold correction would be checked against.
    assert "Beta Beast" in report
    assert "Gamma Keeper" in report
    assert "https://jujutsu-kaisen.fandom.com/wiki/Test_Creatures" in report
