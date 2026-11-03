"""Stage 8b (2026-11-03): the v2 composer's record rules and the v2 layer scorer, on a tiny fixture.

CPU only, no tokenizer, no model: compose_big_set_v2.latest/answer (void lines, vocabulary, B.4 asserter
rule), score_layers_v2 (raw-first loading, fact/tag match rules, end-to-end layer F1 with the event layer
equal to eval_extraction's own number) and eval_base_v2.parse.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "train"))

import compose_big_set_v2 as cb  # noqa: E402
import eval_base_v2 as eb  # noqa: E402
import eval_extraction as ee  # noqa: E402
import score_layers_v2 as sl  # noqa: E402

P1 = ("Hope van Dyne trained Scott Lang at the lab. Hope van Dyne fought Darren Cross on the roof. "
      "Scott Lang and Luis were friends. \"I trained him,\" she said.")
P2 = "Loki planned to steal the Tesseract. Thor arrived at Asgard."


def fact(q, s, rel, o, modality="actual", certainty="stated", asserted_by=None, canon=None):
    return {"quote": q, "subject": s, "relation": rel, "object": o, "modality": modality,
            "certainty": certainty, "asserted_by": asserted_by, "canon": canon}


GOLD = [
    {"id": "w1", "series": "mcu", "page": "Hope", "section": "s", "passage": P1,
     "events": [{"quote": "Hope van Dyne fought Darren Cross on the roof", "subject": "Hope van Dyne",
                 "verb": "fought", "object": "Darren Cross"}],
     "facts": [fact("Hope van Dyne trained Scott Lang at the lab", "Hope van Dyne", "trained", "Scott Lang"),
               fact("Scott Lang and Luis were friends", "Scott Lang", "friend_of", "Luis")],
     "tags": [{"quote": "\"I trained him,\" she said.", "tag": "dialogue"}]},
    {"id": "w2", "series": "jjk", "page": "Loki", "section": "s", "passage": P2,
     "events": [{"quote": "Thor arrived at Asgard", "subject": "Thor", "verb": "arrived", "object": "Asgard"}],
     "facts": [fact("Loki planned to steal the Tesseract", "Loki", "stole", "Tesseract",
                    modality="planned", asserted_by="Loki")],
     "tags": []},
]


def write(tmp_path, name, rows):
    p = tmp_path / name
    p.write_text("".join(json.dumps(r) + "\n" for r in rows))
    return p


def layers(r):
    return {k: r[k] for k in ("events", "facts", "tags")}


# ---- composer record rules ---------------------------------------------------------------------------

def test_latest_void_withdraws_the_record_before_it(tmp_path):
    p = write(tmp_path, "a.jsonl", [{"id": "x", "b": 1, "events": [], "why": "first"},
                                    {"id": "x", "b": 1, "events": [], "why": "bad edit"},
                                    {"id": "x", "void": True, "why": "withdraw"},
                                    {"id": "y", "b": 2, "events": [], "why": "only"},
                                    {"id": "z", "b": 3, "why": "z1"}, {"id": "z", "void": True}])
    got = cb.latest(p)
    assert got["x"]["why"] == "first" and got["y"]["why"] == "only" and "z" not in got


def test_answer_shape_order_and_rules():
    rec = {"events": GOLD[0]["events"],
           "facts": [{"canon": None, **fact("Scott Lang and Luis were friends", "Luis", "child_of", "Scott Lang")}],
           "tags": [{"tag": "dialogue", "quote": "\"I trained him,\" she said."}]}
    errs = []
    ans = cb.answer(rec, P1, "w1", errs)
    assert errs == []
    assert list(ans) == ["events", "facts", "tags"]
    f = ans["facts"][0]
    assert tuple(f) == cb.FACT_KEYS and (f["subject"], f["relation"], f["object"]) == ("Scott Lang", "parent_of", "Luis")
    assert tuple(ans["tags"][0]) == ("quote", "tag")


def test_answer_refuses_bad_rows():
    bad = {"events": [{"quote": "not in the text", "subject": "A", "verb": "punched", "object": "B"}],
           "facts": [fact("Scott Lang and Luis were friends", "Scott Lang", "became", "Luis"),
                     fact("Scott Lang and Luis were friends", "Scott Lang", "friend_of", "Luis", asserted_by="Hope"),
                     fact("Scott Lang and Luis were friends", "Scott Lang", "friend_of", "Luis", modality="claimed")],
           "tags": [{"tag": "opinion", "quote": "Scott Lang and Luis were friends"}]}
    errs = []
    cb.answer(bad, P1, "w1", errs)
    text = "\n".join(errs)
    for needle in ("event quote not verbatim", "bad verb", "retired", "actual with asserted_by",
                   "claimed without asserted_by", "tag 'opinion'"):
        assert needle in text, needle
    # B.4: a hypothetical may have no asserter
    ok = []
    cb.answer({"facts": [fact("Scott Lang and Luis were friends", "Scott Lang", "friend_of", "Luis",
                              modality="hypothetical", certainty="apparent")]}, P1, "w1", ok)
    assert ok == []


def test_empty_definitions():
    tags_only = {"events": [], "facts": [], "tags": [{"quote": "q", "tag": "deictic"}]}
    facts_only = {"events": [], "facts": [{}], "tags": []}
    nothing = {"events": [], "facts": [], "tags": []}
    assert [cb.EMPTY["all"](x) for x in (tags_only, facts_only, nothing)] == [False, False, True]
    assert [cb.EMPTY["events+facts"](x) for x in (tags_only, facts_only, nothing)] == [True, False, True]
    assert [cb.EMPTY["events"](x) for x in (tags_only, facts_only, nothing)] == [True, True, True]


# ---- scorer -----------------------------------------------------------------------------------------

def test_load_reads_the_full_raw_first(tmp_path):
    # sft_qwen.dev_generate's shape: `events` holds the parsed event layer only, the rest is in raw
    raw = "<think>\n\n</think>\n\n" + json.dumps(layers(GOLD[0]))
    p = write(tmp_path, "p.jsonl", [{"id": "w1", "events": GOLD[0]["events"], "raw": raw}])
    got = sl.load(p)["w1"]
    assert len(got["facts"]) == 2 and len(got["tags"]) == 1 and got["valid"] is True


def test_load_falls_back_on_a_cut_raw(tmp_path):
    # the old eval_base.py keeps raw[-3000:]: the head is gone, the record's own events are used
    raw = json.dumps(layers(GOLD[0]))[25:]
    p = write(tmp_path, "p.jsonl", [{"id": "w1", "events": GOLD[0]["events"], "raw": raw},
                                    {"id": "w2", **layers(GOLD[1])}])
    got = sl.load(p)
    assert got["w1"]["events"] == GOLD[0]["events"] and got["w1"]["facts"] == [] and got["w1"]["valid"] is False
    assert len(got["w2"]["facts"]) == 1 and got["w2"]["valid"] is None


def test_fact_match_rules():
    g = fact("q", "Scott Lang", "friend_of", "Luis")
    assert sl.fact_match(fact("q", "Luis", "friend_of", "Scott Lang"), g)          # symmetric
    t = fact("q", "Hope van Dyne", "trained", "Scott Lang")
    assert not sl.fact_match(fact("q", "Scott Lang", "trained", "Hope van Dyne"), t)  # directed
    assert sl.fact_match(fact("q", "Hope", "trained", "Lang"), t)                  # shared name word
    assert not sl.fact_match(fact("q", "Hope van Dyne", "trained", "Scott Lang", modality="planned",
                                  asserted_by="Hope van Dyne"), t)                 # modality is part of the match
    ov = fact("q", "Loki", "other_verb", "attacked")
    assert sl.fact_match(fact("q", "Loki", "other_verb", "attack"), ov)
    assert not sl.fact_match(fact("q", "Loki", "other_verb", "fought"), ov)


def test_tag_match_rules():
    g = {"quote": "\"I trained him,\" she said.", "tag": "dialogue"}
    assert sl.tag_match({"quote": "I trained him", "tag": "dialogue"}, g)
    assert not sl.tag_match({"quote": "I trained him", "tag": "production"}, g)
    assert not sl.tag_match({"quote": "", "tag": "dialogue"}, g)


def test_score_layers_end_to_end(tmp_path):
    gpath = write(tmp_path, "gold.jsonl", GOLD)
    ee_gold = ee.load_gold(gpath)
    # perfect predictions: every layer F1 1.0, the event layer equal to the existing scorer's number
    perfect = write(tmp_path, "perfect.jsonl", [{"id": r["id"], "raw": json.dumps(layers(r))} for r in GOLD])
    s = sl.score_layers(GOLD, ee_gold, sl.load(perfect), "all")
    assert s["n"] == 2 and s["valid"] == 1.0
    assert [round(sl.prf(s[k])[0], 3) for k in ("events", "facts", "tags")] == [1.0, 1.0, 1.0]
    assert s["summary"]["f1"] == 1.0
    assert s["attrs"]["certainty"] == [3, 3]
    # one fact with the wrong certainty, one invented fact, the tag missed, the w2 event missed
    w1 = layers(GOLD[0])
    w1["facts"] = [dict(w1["facts"][0], certainty="apparent"), w1["facts"][1],
                   fact("Hope van Dyne fought Darren Cross on the roof", "Hope van Dyne", "wore", "suit")]
    w1["tags"] = []
    w2 = dict(layers(GOLD[1]), events=[])
    pred = write(tmp_path, "pred.jsonl", [{"id": "w1", "raw": json.dumps(w1)}, {"id": "w2", "raw": json.dumps(w2)}])
    s = sl.score_layers(GOLD, ee_gold, sl.load(pred), "all")
    f, p, r = sl.prf(s["facts"])
    assert (round(p, 3), round(r, 3)) == (0.75, 1.0)
    assert sl.prf(s["tags"]) == (0.0, 0.0, 0.0)
    ef, ep, er = sl.prf(s["events"])
    assert (ep, er) == (1.0, 0.5)
    summary, _ = ee.score(ee_gold, {"w1": {"events": w1["events"]}, "w2": {"events": []}})
    assert round(ef, 3) == summary["f1"]
    assert s["attrs"]["certainty"] == [2, 3]
    # subsets: the JJK window alone
    sj = sl.score_layers(GOLD, ee_gold, sl.load(pred), "jjk")
    assert sj["n"] == 1 and sl.prf(sj["facts"])[0] == 1.0


def test_eval_base_v2_parse():
    good = "<think>x</think>\n```json\n" + json.dumps(layers(GOLD[1])) + "\n```"
    out, valid = eb.parse(good)
    assert valid and out["facts"][0]["relation"] == "stole"
    out, valid = eb.parse('{"events": []}')
    assert not valid and out == {"events": [], "facts": [], "tags": []}
    assert eb.parse("no json here") == ({"events": [], "facts": [], "tags": []}, False)
