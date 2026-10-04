"""U-WP5 scorer tests: the gen-2 passage-unit test gold.

What is pinned here (plan/UNIVERSAL_DATASET_PLAN.md U-WP5):

* PASSAGE union scoring -- a prediction from ANY covering window counts
  for the passage (the student is run on every covering window and the
  predictions are unioned); a prediction whose quote is not inside the
  annotated slice is DISCARDED (never an FP); duplicates (same
  subject, verb, object) are collapsed before matching.
* The real test gold's totals -- 100 passage units carrying the
  UNCHANGED 173 core + 97 optional events, every unit's covering
  windows tiling the passage (first span at 0, last at the end, no
  non-whitespace gaps, every span verbatim in the passage).
* WINDOW-level scoring -- the per-wiki labeled test pools' shape
  (records whose gold events carry a `quote`): a prediction matches
  only while its quote's span in the window text overlaps the gold
  quote's span (the plan's event match).
* The legacy W-indexed v4 shape still loads behind the flag, and the
  new shape's report carries the per-wiki/per-verb numbers, the verb
  confusion (fought vs defeated first), JSON-validity and
  quote-verbatim rates.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from eval_extraction import load_gold, score  # noqa: E402

PASSAGE = ("Sukuna fought Hana Kurusu. "
           "Hana Kurusu defeated Sukuna. "
           "The battle ended at dawn.")
FQ = "Sukuna fought Hana Kurusu"
DQ = "Hana Kurusu defeated Sukuna"
TQ = "The battle ended at dawn"

# Two covering windows of the passage (a carry overlap, the second
# window partial: it extends past the slice).
UNIT = {
    "w": 0, "page": "Hana Kurusu", "section": "Battle",
    "passage": PASSAGE,
    "core": [["Sukuna", "fought", "Hana Kurusu"]],
    "optional": [["Hana Kurusu", "defeated", "Sukuna"]],
    "windows": [
        {"id": "w1", "span": [0, 27], "partial": False},
        {"id": "w2", "span": [25, 56], "partial": True},
    ],
}


def _ev(s, v, o, q):
    return {"subject": s, "verb": v, "object": o, "quote": q}


def test_passage_union_prediction_from_second_window_counts():
    """A prediction from covering window 2 (not 1) is the unit's
    prediction: the union spans every covering window."""
    gold = {"W0": UNIT}
    preds = {"w2": {"events": [_ev("Sukuna", "fought", "Hana Kurusu", FQ)]}}
    s, _ = score(gold, preds)
    assert s["kind"] == "passage"
    assert s["hit"] == 1
    assert s["fp"] == 0


def test_passage_out_of_slice_prediction_is_discarded_not_fp():
    """A prediction whose quote is not inside the annotated slice was
    made on text the annotator never read: it is dropped, and it
    counts neither as a hit nor as an FP."""
    gold = {"W0": UNIT}
    preds = {"w2": {"events": [
        _ev("Sukuna", "fought", "Hana Kurusu", FQ),
        _ev("Sukuna", "killed", "Hana Kurusu", "a line the slice never says"),
    ]}}
    s, per = score(gold, preds)
    assert s["hit"] == 1
    assert s["fp"] == 0            # the out-of-slice event is discarded
    assert s["pred"] == 1
    assert s["discarded_outside_slice"] == 1
    assert per["W0"]["discarded"] == 1


def test_passage_duplicates_collapse():
    """The same (subject, verb, object) reported by two covering
    windows is one prediction (case/trim-insensitive, the name rule
    is too): no double hit, no double FP."""
    gold = {"W0": UNIT}
    preds = {
        "w1": {"events": [_ev("Sukuna", "fought", "Hana Kurusu", FQ)]},
        "w2": {"events": [_ev("sukuna", "fought", "HANA KURUSU", FQ)]},
    }
    s, _ = score(gold, preds)
    assert s["hit"] == 1           # one hit, not two
    assert s["pred"] == 1          # collapsed, not two predictions
    assert s["fp"] == 0


def test_passage_confusion_matrix_fought_defeated_first():
    """A wrong-verb FP whose names match a gold event feeds the
    confusion matrix; fought vs defeated rows come first."""
    gold = {"W0": UNIT}
    preds = {"w1": {"events": [
        _ev("Sukuna", "defeated", "Hana Kurusu", FQ),   # gold is fought
        _ev("Sukuna", "killed", "Hana Kurusu", FQ),     # also wrong verb
    ]}}
    s, _ = score(gold, preds)
    assert s["fp"] == 2
    cf = {(a, b): n for a, b, n in s["confusion"]}
    assert cf.get(("defeated", "fought")) == 1
    assert cf.get(("killed", "fought")) == 1
    # the fought/defeated pair sorts before the rest:
    assert s["confusion"][0][0] == "defeated" and s["confusion"][0][1] == "fought"


def test_passage_json_validity_and_quote_verbatim():
    """JSON-validity is measured on the records' raw answers;
    quote-verbatim on each attributable prediction's quote vs the
    window text it came from (the window's READ span)."""
    unit3 = dict(UNIT, windows=[
        {"id": "w1", "span": [0, 27], "partial": False},
        {"id": "w2", "span": [27, 56], "partial": False},
        {"id": "w3", "span": [56, 81], "partial": True},
    ])
    gold = {"W0": unit3}
    preds = {
        "w1": {"events": [_ev("Sukuna", "fought", "Hana Kurusu", FQ)],
               "raw": '{"events": []}'},
        "w2": {"events": [
            _ev("Hana Kurusu", "defeated", "Sukuna", DQ),
            _ev("Sukuna", "killed", "Hana Kurusu", "zzz never in the window")],
               "raw": "not json at all"},
    }
    s, _ = score(gold, preds)
    assert s["hit"] == 1            # w1's FQ -> the core event
    assert s["fp"] == 0             # w2's DQ -> the optional tier
    assert s["pred"] == 2           # the zzz event is out-of-slice: dropped
    assert s["json_validity"] == 0.5          # one parseable raw of two
    assert s["quote_verbatim"] == 0.6667      # FQ + DQ of three (4 d.p.)
    # a prediction on a window no unit covers is unattributable:
    preds["wX"] = {"events": [_ev("Sukuna", "fought", "Hana Kurusu", FQ)]}
    s2, _ = score(gold, preds)
    assert s2["pred"] == 2          # the union is unchanged
    assert s2["quote_verbatim"] == 0.6667  # wX not counted


# ---------------------------------------------------------------------
# the real test gold: the U-WP5 file's totals must be preserved
# ---------------------------------------------------------------------

TESTGOLD_DIR = ROOT / "series" / "jjk" / "training" / "recall_gold_v3"


@pytest.fixture(scope="module")
def real_gold():
    if not (TESTGOLD_DIR / "gold_test_v4.gen2.json").exists():
        pytest.skip("the jjk test gold data is not in this tree")
    return load_gold(TESTGOLD_DIR)


def test_real_gold_is_the_passage_shape(real_gold):
    assert len(real_gold) == 100
    assert all(k.startswith("W") for k in real_gold)
    for unit in real_gold.values():
        assert unit["passage"]
        assert unit["windows"]


def test_real_gold_totals_173_97(real_gold):
    """The core + optional triples are UNCHANGED by the re-key: the
    annotation's 173 core + 97 optional events, no more, no less (the
    per-window re-key inflated them to 1,165 pairs -- that file is the
    .pre-u5 archive)."""
    core = sum(len(u["core"]) for u in real_gold.values())
    optional = sum(len(u["optional"]) for u in real_gold.values())
    assert core == 173
    assert optional == 97


def test_real_gold_windows_tile_the_passage(real_gold):
    """Every unit's covering windows: ordered, tiling the passage
    (first span at 0, last at the end, only whitespace between
    spans), every read span verbatim in the passage."""
    for unit in real_gold.values():
        passage = unit["passage"]
        ids = [w["id"] for w in unit["windows"]]
        assert len(set(ids)) == len(ids), f"dup window in {unit['w']}"
        prev_end = 0
        for w in unit["windows"]:
            a, b = w["span"]
            assert 0 <= a < b <= len(passage), (unit["w"], w)
            if a > prev_end:
                assert not passage[prev_end:a].strip(), \
                    f"non-whitespace gap in W{unit['w']}"
            prev_end = max(prev_end, b)
        assert prev_end == len(passage), f"spans do not reach the end: W{unit['w']}"


# ---------------------------------------------------------------------
# window-level units (the per-wiki labeled test pools' shape)
# ---------------------------------------------------------------------

def _window_record(wid, passage, core, optional=None):
    """A labeled test pool's record: the gold events (with quotes) under
    `events`, the borderline tier under `optional`."""
    return {"id": wid, "page": "P", "section": "S", "passage": passage,
            "events": core, "optional": optional or []}


def test_window_level_match_needs_quote_overlap():
    """The plan's event match: (subject, verb, object) AND the quote
    overlapping the gold quote. Right fact, wrong place -> no match."""
    gold = {"wA": _window_record("wA", PASSAGE,
                                 [{"quote": FQ, "subject": "Sukuna",
                                   "verb": "fought", "object": "Hana Kurusu"}])}
    # the right event stated at a different place in the window:
    s, _ = score(gold, {"wA": {"events": [
        _ev("Sukuna", "fought", "Hana Kurusu", TQ)]}})
    assert s["kind"] == "window"
    assert s["hit"] == 0
    assert s["fp"] == 1
    # the same event at the gold's place:
    s2, _ = score(gold, {"wA": {"events": [
        _ev("Sukuna", "fought", "Hana Kurusu", FQ)]}})
    assert s2["hit"] == 1
    assert s2["fp"] == 0
    # a quote the window never says: no span, no overlap, an FP:
    s3, _ = score(gold, {"wA": {"events": [
        _ev("Sukuna", "fought", "Hana Kurusu", "a line the window never says")]}})
    assert s3["fp"] == 1
    assert s3["quote_verbatim"] == 0.0


def test_window_level_jsonl_file(tmp_path):
    """The per-wiki labeled test pools load as JSONL records with
    quotes (one record per window)."""
    p = tmp_path / "hxh_test.jsonl"
    p.write_text(
        json.dumps(_window_record(
            "wA", PASSAGE,
            [{"quote": FQ, "subject": "Sukuna", "verb": "fought",
              "object": "Hana Kurusu"}])) + "\n",
        encoding="utf-8")
    gold = load_gold(p)
    assert gold["wA"]["core"][0]["quote"] == FQ
    s, _ = score(gold, {"wA": {"events": [
        _ev("Sukuna", "fought", "Hana Kurusu", FQ)]}})
    assert s["kind"] == "window"
    assert s["hit"] == 1


def test_window_level_optional_tier():
    """An optional gold event is not recall (like the legacy rule) but
    it shields its prediction from being an FP."""
    gold = {"wA": _window_record(
        "wA", PASSAGE, [],
        optional=[{"quote": DQ, "subject": "Hana Kurusu",
                   "verb": "defeated", "object": "Sukuna"}])}
    s, _ = score(gold, {"wA": {"events": [
        _ev("Hana Kurusu", "defeated", "Sukuna", DQ)]}})
    assert s["hit"] == 0        # optional: not a core hit
    assert s["fp"] == 0         # but shielded from FP
    assert s["precision"] == 1.0


# ---------------------------------------------------------------------
# the legacy W-indexed v4 shape, behind the flag
# ---------------------------------------------------------------------

def test_legacy_v4_shape_behind_flag(tmp_path):
    (tmp_path / "windows_100.json").write_text(
        json.dumps([{"id": "wA", "passage": PASSAGE}]))
    (tmp_path / "gold_test_v4.json").write_text(json.dumps({
        "version": 4, "windows": "windows_100.json",
        "W0": {"core": [["Sukuna", "fought", "Hana Kurusu"]],
               "optional": []}}))
    gold = load_gold(tmp_path, legacy=True)
    assert "wA" in gold
    assert gold["wA"]["core"] == [["Sukuna", "fought", "Hana Kurusu"]]
    s, _ = score(gold, {"wA": {"events": [
        _ev("Sukuna", "fought", "Hana Kurusu", FQ)]}})
    assert s["kind"] == "legacy"
    assert s["hit"] == 1


def test_dir_without_gen2_file_requires_the_flag(tmp_path):
    (tmp_path / "windows_100.json").write_text(
        json.dumps([{"id": "wA", "passage": PASSAGE}]))
    (tmp_path / "gold_test_v4.json").write_text(json.dumps({
        "version": 4, "windows": "windows_100.json",
        "W0": {"core": [], "optional": []}}))
    with pytest.raises(SystemExit):
        load_gold(tmp_path)          # no gen-2 file: the default refuses
    assert "wA" in load_gold(tmp_path, legacy=True)  # ... the flag reads it


def test_legacy_and_passage_shapes_are_distinguished():
    """A passage gold (units with covering windows) never scores as
    window-level, and vice versa: the kind drives the match rule."""
    s, _ = score({"W0": UNIT}, {})
    assert s["kind"] == "passage"
    s2, _ = score({"wA": _window_record("wA", PASSAGE, [])}, {})
    assert s2["kind"] == "window"
    s3, _ = score({"wA": {"core": [], "optional": []}}, {})
    assert s3["kind"] == "legacy"