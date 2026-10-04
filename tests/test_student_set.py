"""U-WP6 dataset checks on the BUILT student set (CPU-only, repo venv).

Not part of the standing pytest run: it pins the artefacts of the
U-WP6 build (series/jjk/training/student/), so it runs on demand:
    scriptengine/.venv/bin/python -m pytest tests/test_student_set.py
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools" / "train"))

from scriptengine.ingest.events import eventive_verbs, system_prompt, _TEMPLATE  # noqa: E402

STUDENT = ROOT / "series" / "jjk" / "training" / "student"


def _rows(name):
    return [json.loads(l) for l in open(STUDENT / name)]


def test_receipt_matches_files():
    receipt = json.load(open(STUDENT / "receipt.json"))
    train, dev = _rows("train.jsonl"), _rows("dev.jsonl")
    assert receipt["train_windows"] == len(train)
    assert receipt["dev_windows"] == len(dev)
    empties = sum(1 for r in train + dev if not r["events"])
    assert abs(empties - receipt["empty_windows"]) == 0
    assert receipt["pages"] == len({r["page"] for r in train + dev})
    vh = Counter()
    for r in train + dev:
        for e in r["events"]:
            vh[e["verb"]] += 1
    assert dict(vh) == receipt["verb_histogram"]


def test_unique_ids_and_page_disjoint_split():
    train, dev = _rows("train.jsonl"), _rows("dev.jsonl")
    ids = [r["id"] for r in train + dev]
    assert len(ids) == len(set(ids))
    tp = {r["page"] for r in train}
    dp = {r["page"] for r in dev}
    assert not (tp & dp), "a page must not straddle train/dev"


def test_quotes_verbatim_and_assistant_json():
    for r in _rows("train.jsonl") + _rows("dev.jsonl"):
        body = json.loads(r["messages"][2]["content"])
        assert set(body) == {"events"}
        for e in body["events"]:
            assert set(e) >= {"quote", "subject", "verb", "object"}
            assert e["quote"] in r["passage"], (r["id"], e["quote"][:40])
        assert body["events"] == r["events"]


def test_d5_prompt_fidelity():
    """System + user messages are byte-identical to the production render."""
    # system prompt is pure (verbs frozen into the set receipt):
    verbs = frozenset(json.load(open(STUDENT / "receipt.json"))["eventive_verbs"])
    sysmsg = system_prompt(verbs)
    for r in _rows("dev.jsonl")[:25]:
        assert r["messages"][0]["content"] == sysmsg
        assert r["messages"][1]["content"].startswith(f"Series: jjk")
        assert r["passage"] in r["messages"][1]["content"]
        assert r["section"] in r["messages"][1]["content"]


def test_no_holdout_and_no_test_ids():
    from emit_windows import holdout_pages
    hp = holdout_pages(ROOT / "series" / "jjk")
    test_ids = set()
    g2 = ROOT / "series" / "jjk" / "training" / "recall_gold_v3" / "gold_test_v4.gen2.json"
    for k, v in json.load(open(g2)).items():
        if isinstance(v, dict):
            for w in v.get("windows", []):
                test_ids.add(w["id"])
    probe_ids = set()
    for l in open(ROOT / "series" / "jjk" / "training" / "opencode" / "golden_probes.jsonl"):
        probe_ids.add(json.loads(l).get("id") or json.loads(l).get("window"))
    for r in _rows("train.jsonl") + _rows("dev.jsonl"):
        assert r["page"] not in hp
        assert r["id"] not in test_ids
        assert r["id"] not in probe_ids
