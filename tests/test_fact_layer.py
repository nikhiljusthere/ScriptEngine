"""Tests for the v2 fact layer (plan/EXTRACTION_PROCEDURE_V2.md).

Covers the gates in tools/train/fact_gate.py and the coverage reporter in
tools/train/fact_coverage.py, and pins the two invariants the council found load-bearing:

  * the event section of EXTRACTION_PROCEDURE_V2.md must stay byte-identical to
    plan/EXTRACTION_PROCEDURE.md, so v2 cannot silently change the 12 verbs or the gold;
  * a quote may not cover a sentence by CONTAINING it (the big_flags.py:197 `sent in q` loophole),
    and the segmenter may not drop short declaratives (the big_flags.py:88 `len(s) > 20` floor).

Run:  scriptengine/.venv/bin/python -m pytest tests/test_fact_layer.py -q
"""
import sys
from pathlib import Path

import pytest

CODE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE / "tools" / "train"))

import fact_coverage as fc  # noqa: E402
import fact_gate as fg  # noqa: E402

V2 = CODE / "plan/EXTRACTION_PROCEDURE_V2.md"
V1 = CODE / "plan/EXTRACTION_PROCEDURE.md"


def F(subject="Hope van Dyne", relation="trained", object_="Scott Lang", **kw):
    row = {"quote": kw.pop("quote", "Van Dyne had been tasked with training Scott Lang"),
           "subject": subject, "relation": relation, "object": object_,
           "modality": kw.pop("modality", "actual"), "certainty": kw.pop("certainty", "stated")}
    row.update(kw)
    return row


# --------------------------------------------------------------------------- schema doc
def test_event_section_is_verbatim():
    """v2 embeds the event procedure verbatim; the 12-verb gold must not drift."""
    doc = V2.read_text(encoding="utf-8")
    a = doc.index("# SECTION A — THE EVENT LAYER (unchanged)") + len(
        "# SECTION A — THE EVENT LAYER (unchanged)")
    b = doc.index("\n---\n\n# SECTION B —")
    assert doc[a:b].strip() == V1.read_text(encoding="utf-8").strip()


def test_twelve_verbs_unchanged_in_v2():
    for v in ("fought", "defeated", "killed", "captured", "escaped", "saved", "betrayed",
              "sealed", "met", "arrived", "departed", "awakened"):
        assert v in V2.read_text(encoding="utf-8")


def test_closed_enums_and_tag_set():
    assert fg.MODALITY == ("actual", "planned", "attempted", "ordered", "controlled", "claimed",
                           "dreamed", "hypothetical")
    assert fg.CERTAINTY == ("stated", "reported", "apparent", "denied")
    # 2026-10-08 council: the three coverage tags that make a catalogued "no row" sentence legal
    assert set(fg.TAGS) == {"dialogue", "list_header", "production", "citation", "apposition",
                            "attire", "capability", "deictic", "below_floor",
                            "no_doer", "crowd_end", "no_relation"}


# --------------------------------------------------------------------------- the gate
def test_a_good_row_has_no_flags():
    flags, ok = fg.check([F()], "Van Dyne had been tasked with training Scott Lang.")
    assert flags == []
    assert ok == ["Hope van Dyne|trained|Scott Lang"]


def test_non_actual_modality_needs_asserted_by():
    """B.4: a plan with nobody planning it is the bug that would make the brain assert lies."""
    flags, _ = fg.check([F(relation="joined", object_="Liberators", modality="planned",
                           quote="Morgan hoped to have Betsy join")],
                        "Morgan hoped to have Betsy join.")
    assert any("asserted_by" in f for f in flags)
    flags2, _ = fg.check([F(relation="joined", object_="Liberators", modality="planned",
                            asserted_by="Morgan", quote="Morgan hoped to have Betsy join")],
                         "Morgan hoped to have Betsy join.")
    assert not any("asserted_by" in f for f in flags2)


def test_modality_is_a_closed_enum():
    flags, _ = fg.check([F(modality="maybe")], "Van Dyne had been tasked with training Scott Lang.")
    assert any("modality 'maybe'" in f for f in flags)


def test_certainty_is_a_closed_enum():
    flags, _ = fg.check([F(certainty="sort of")], "Van Dyne had been tasked with training Scott Lang.")
    assert any("certainty 'sort of'" in f for f in flags)


def test_other_is_refused_and_other_verb_must_appear_in_the_quote():
    """B.3: 'other' collides with the engine's `other` COLUMN; the verb must be verbatim."""
    w = "He punched the wall and laughed"
    flags, _ = fg.check([F(relation="other", object_="punched")], w)
    assert any("use 'other_verb'" in f for f in flags)
    flags2, _ = fg.check([F(relation="other_verb", object_="laughed", quote="and laughed")], w)
    assert not any("literally" in f for f in flags2)
    flags3, _ = fg.check([F(relation="other_verb", object_="shouted", quote="and laughed")], w)
    assert any("literally" in f for f in flags3)


def test_quote_must_be_verbatim():
    flags, _ = fg.check([F(quote="Van Dyne trained Scott")], "Van Dyne had been tasked with training Scott Lang.")
    assert any("not verbatim" in f for f in flags)


def test_quote_must_lie_inside_one_sentence():
    """The anti-loophole rule. A paragraph quote games big_flags.py:197's `sent in q`."""
    w = "Hope trained Scott. Scott fought Kang. They left the Tower."
    para = "Hope trained Scott. Scott fought Kang. They left the Tower."
    flags, _ = fg.check([F(quote=para)], w)
    assert any("more than one sentence" in f for f in flags)


def test_quote_longer_than_the_store_truncation_is_flagged():
    """facts.py save_relations truncates quotes at 400 chars, silently."""
    w = "Van Dyne had been tasked with training Scott Lang " + "on the Ant-Man Suit " * 30
    flags, _ = fg.check([F(quote=w[:420])], w)
    assert any("truncates" in f for f in flags)


def test_short_quote_flagged():
    flags, _ = fg.check([F(quote="trained")], "Van Dyne had been tasked with training Scott Lang.")
    assert any("shorter than" in f for f in flags)


@pytest.mark.parametrize("end", ["she", "they", "him", "her father", "the villagers"])
def test_crowds_and_pronouns_are_refused_as_either_end(end):
    flags, _ = fg.check([F(subject=end)], "Van Dyne had been tasked with training Scott Lang.")
    assert flags, f"{end!r} should be refused as a subject"


@pytest.mark.parametrize("end", ["the Kree", "Skrulls", "mutants", "several Avengers"])
def test_species_ends_are_refused(end):
    flags, _ = fg.check([F(subject=end)], "Van Dyne had been tasked with training Scott Lang.")
    assert flags


def test_place_is_allowed_as_a_fact_object():
    """B.1/B.8: a place IS a legal fact end, unlike in the event layer."""
    w = "Van Dyne resides at a cottage in Maine"
    flags, _ = fg.check([F(subject="Van Dyne", relation="resides_at", object_="a cottage in Maine",
                           quote="Van Dyne resides at a cottage in Maine")], w)
    assert not any("object:" in f for f in flags), flags


def test_event_verb_in_a_fact_row_is_flagged():
    flags, _ = fg.check([F(relation="fought", object_="Kang")], "Hope fought Kang in the lab")
    assert any("EVENT verb" in f for f in flags)


def test_rank_prefix_is_flagged():
    flags, _ = fg.check([F(subject="General Werner Reinhardt", relation="trained")],
                        "General Werner Reinhardt trained them well")
    assert any("rank prefix" in f for f in flags)


def test_validate_catches_shape_problems():
    assert fg.validate(F()) == []
    assert any("asserted_by" in p for p in fg.validate(F(modality="planned")))
    assert any("asserted_by" in p for p in fg.validate(F(modality="claimed")))
    assert any("other" in p for p in fg.validate(F(relation="other", object_="punched")))
    assert any("vocabulary" in p for p in fg.validate(F(relation="sparred_with")))
    assert any("certainty" in p for p in fg.validate(F(certainty="probably")))


def test_other_share_is_a_metric():
    rows = [F(relation="other_verb", object_="wished") for _ in range(2)] + [F(), F()]
    assert fg.other_share(rows) == 0.5
    assert fg.other_share([]) == 0.0


# --------------------------------------------------------------------------- coverage
def test_segmenter_keeps_short_declaratives():
    """big_flags.py:88 drops spans under 20 chars; v2 must not, or it cannot see these facts."""
    out = fg.sentences("He is her student. Van Dyne had been tasked with training Scott Lang.")
    assert any(s.strip() == "He is her student." for s in out)


def test_segmenter_survives_a_dotted_place_name():
    out = fg.sentences("They fought in Washington, D.C. Kang fled afterwards. Nobody moved.")
    assert any("Washington, D.C." in s for s in out)
    assert not any(s.strip() == "D.C." for s in out)


def test_covered_requires_the_quote_inside_the_sentence():
    """The `sent in q` loophole, inverted: a paragraph quote must NOT cover every sentence.

    big_flags.py:197 accepts `sent in q` with no quote-length cap, so one paragraph quote makes
    every sentence look covered. Here a paragraph quote covers NOTHING.
    """
    text = "Hope trained Scott. Scott fought Kang. They left the Tower."
    rep = fc.report(text, [], [F(quote=text)], [])
    assert len(rep["uncovered"]) == 3
    assert rep["covered"] == 0
    assert rep["rate"] == 0.0


def test_coverage_counts_each_sentence_once_and_reports_the_misses():
    text = "Van Dyne had been tasked with training Scott Lang. Scott Lang punched van Dyne."
    rep = fc.report(text, [{"quote": "Scott Lang punched van Dyne"}], [F()], [])
    assert rep["narrative"] == 2
    assert rep["covered"] == 2
    assert rep["uncovered"] == []
    assert rep["rate"] == 1.0


def test_a_tag_excuses_a_sentence():
    # a sentence that does NOT start with a quote character is narrative, so it needs a tag
    text = ("Van Dyne had been tasked with training Scott Lang. "
            "The following morning nobody spoke of it.")
    rep = fc.report(text, [], [F()], [{"quote": "The following morning nobody spoke of it.",
                                       "tag": "deictic"}])
    assert rep["uncovered"] == []
    assert len(rep["tagged"]) == 1


def test_a_quote_leading_sentence_is_furniture_not_narrative():
    # a Quote page line is dialogue: it is not a narrative sentence, so it never counts as a miss
    text = ("Van Dyne had been tasked with training Scott Lang. "
            "\"I trained him,\" she said.")
    rep = fc.report(text, [], [F()], [])
    assert rep["uncovered"] == []
    assert rep["narrative"] == 1


def test_an_unknown_tag_does_not_excuse():
    text = "Van Dyne had been tasked with training Scott Lang. Scott Lang punched van Dyne."
    flags, _ = fg.check([], text, tags=[{"quote": "Scott Lang punched van Dyne.", "tag": "whatever"}])
    assert any("not in the allowed set" in f for f in flags)


def test_furniture_is_not_counted_as_narrative():
    assert fc.is_furniture("Chris Hemsworth | Thor | 2011")
    assert fc.is_furniture("\"A quote line from the film.\"")
    assert fc.is_furniture("Yes.")
    assert not fc.is_furniture("Van Dyne had been tasked with training Scott Lang on the suit.")


@pytest.mark.parametrize("entry", [
    "Frank Dean",
    "Brooks Watten †",
    "Magnistrate's Wife - Former Controller",
    "Morgan le Fay",
    "Sacrifice Victims",
    "(Hulk)",
    "(X-Men, Note: pre-secondary mutation appearance)",
    "{{Marvel Database:Character Template",
    "| CurrentAlias = Powerhouse",
    "Psi-Lord,{{Citation}}",
])
def test_link_lists_and_templates_are_furniture(entry):
    """The three worst windows in the v1 baseline were a cast list and two template dumps.

    Counting those as narrative sentences makes the coverage denominator meaningless, so they must
    be furniture -- and the gate must not report them as uncovered facts.
    """
    assert fc.is_furniture(entry)


def test_a_proper_noun_sentence_with_a_verb_is_still_narrative():
    assert not fc.is_furniture("Frank Dean was her mentor.")
    assert not fc.is_furniture("Hope van Dyne trained Scott Lang for three years.")


def test_uncovered_worklist_prints_the_sentence_text():
    text = "Van Dyne had been tasked with training Scott Lang. Nobody ever mentioned the suit."
    rep = fc.report(text, [], [F()], [])
    assert rep["uncovered"] and "Nobody ever mentioned" in rep["uncovered"][0]


def test_review_hint_flags_a97_a99():
    w = ("Koenig gave him a S.H.I.E.L.D. Lanyard. Octopus assumed the alias of 'Elliot Tolliver'. "
         "Black Bolt's son Ahura was there. Tony decided to accept an offer Star-Lord made to him.")
    rows = [F("Koenig", "gave", "S.H.I.E.L.D. Lanyard", quote="Koenig gave him a S.H.I.E.L.D. Lanyard"),
            F("Otto", "alias_of", "Elliot Tolliver", quote="Octopus assumed the alias of 'Elliot Tolliver'"),
            F("Ahura", "child_of", "Black Bolt", quote="Black Bolt's son Ahura"),
            F("Black Bolt", "parent_of", "Ahura", quote="Black Bolt's son Ahura"),
            F("Tony", "other_verb", "accept", quote="Tony decided to accept an offer Star-Lord made to him",
              modality="planned", asserted_by="Tony")]
    flags, _ = fg.check(rows, w)
    text = "\n".join(flags)
    assert "(A97)" in text and "(A99)" in text
    assert sum("(A99)" in f for f in flags) == 2
    good, _ = fg.check([F("Koenig", "gave", "Ward", quote="Koenig gave him a S.H.I.E.L.D. Lanyard")], w)
    assert not any("(A97)" in f for f in good)


def test_a101_named_narration_tagged_is_flagged():
    w = "Masaryk watches the news report on her friends' arrest. The authorities arrive and declare it a fire."
    tags = [{"tag": "no_relation", "quote": "Masaryk watches the news report on her friends' arrest."},
            {"tag": "crowd_end", "quote": "The authorities arrive and declare it a fire."}]
    flags, _ = fg.check([], w, tags=tags)
    assert sum("(A101)" in f for f in flags) == 1
    ok = [{"tag": "no_relation", "quote": "The authorities arrive and declare it a fire."}]
    flags, _ = fg.check([], w, tags=ok)
    assert not any("(A101)" in f for f in flags)


def test_a101_doerless_passive_on_no_doer_tag_is_no_flag():
    w = "Finally, Lorna was calmed, though she blew Annie off. Lang was captured. Lorna freaked."
    flags, _ = fg.check([], w, tags=[{"tag": "no_doer", "quote": "Lang was captured."}])
    assert not any("(A101)" in f for f in flags)
    flags, _ = fg.check([], w, tags=[{"tag": "no_relation", "quote": "Lorna freaked."}])
    assert any("(A101)" in f for f in flags)


def test_dash_object_list_end_and_agent_number():
    w = "Stark remembered it. Agent 33 revealed that Phil Coulson had killed him. Reed, Ben and Johnny fought."
    r = fg.normalise({"subject": "Stark", "relation": "remembered", "object": "-", "quote": "Stark remembered it."}, w)
    assert r["object"] is None
    r = fg.normalise({"subject": "33", "relation": "revealed", "object": None,
                      "quote": "Agent 33 revealed that Phil Coulson had killed him."}, w)
    assert r["subject"] == "Agent 33"
    assert "list end" in (fg._end_ok("Reed, Ben and Johnny", "allied_with", False, "fact") or "")
    assert fg._end_ok("Goodman, Lieber, Kurtzberg & Holliway", "member_of", True, "fact") is None
    assert fg._end_ok("Oracle, Inc.", "owns", True, "fact") is None
    assert fg._end_ok("Avengers of 1,000,000 BC", "member_of", True, "fact") is None


def test_hyphenated_name_is_not_a_pronoun():
    assert fg._end_ok("She-Hulk", "member_of", False, "t") is None
    assert fg._end_ok("she", "member_of", False, "t")
    assert fg._end_ok("He Who Remains", "revealed", False, "t") is None
    assert fg._end_ok("the other two", "met", False, "t")


def test_rank_word_kept_when_the_window_names_the_codename():
    # b8007 (2026-10-13): 'the mantle of "Captain Krakoa"' was cut to "Krakoa", the island nation
    w = 'Steve Rogers was recruited and equipped with the mantle of "Captain Krakoa".'
    assert fg.strip_rank("Captain Krakoa", w) == "Captain Krakoa"
    assert fg._end_ok("Captain Krakoa", "alias_of", False, "t", None, w) is None
    # an ordinary title is still stripped / refused
    assert fg.strip_rank("General Ross", "General Ross ordered the strike.") == "Ross"
    assert fg._end_ok("General Ross", "ordered", False, "t", None, "General Ross ordered the strike.")


def test_title_that_is_part_of_the_name_is_kept():
    # gold b893/b1014/b3543 (2026-11-04): the bare rest is another person or never used alone
    for name in ("King Kai", "King Vegeta", "King Cold", "King Piccolo", "King Kong", "Captain Mizuki"):
        assert fg.strip_rank(name, name + " appears.") == name
        assert fg._end_ok(name, "met", False, "t") is None
    assert fg.strip_rank("King T'Chaka", "King T'Chaka ruled.") == "T'Chaka"


def test_crowd_word_inside_a_thing_object_is_no_crowd():
    # b8055 (2026-10-13): a power/item description is no person end; measured 57 historical drops recovered
    assert fg._end_ok("ability to entrance others with music", "gained_power", True, "t") is None
    assert fg._end_ok("Book of the Darkhold", "used", True, "t") is None
    # people stay crowds: quantity-led objects, gave's recipient, person relations
    assert fg._end_ok("many deities", "created", True, "t")
    assert fg._end_ok("army", "gave", True, "t")
    assert fg._end_ok("heroes", "disguise_as", True, "t")


def test_modality_written_as_relation_becomes_other_verb():
    # gate audit 2026-10-13: "Strange|planned|learn magic" was dropped; 39 of 94 such rows are repaired
    r = fg.normalise({"subject": "Strange", "relation": "planned", "object": "learn magic",
                      "quote": "the only way to stop Mordo was to learn magic himself"})
    assert (r["relation"], r["object"], r["modality"], r["asserted_by"]) == ("other_verb", "learn", "planned", "Strange")
    r = fg.normalise({"subject": "Peter Parker", "relation": "claimed", "object": "knife",
                      "quote": "Peter claimed ownership of the knife with a concocted story"})
    assert (r["object"], r["modality"]) == ("claimed", "claimed")
    # a noun is no verb: "his own claim" stays unrepaired
    r = fg.normalise({"subject": "Pythagoras Dupree", "relation": "claimed", "object": "6th_Smartest_Man",
                      "quote": "Pythagoras, by his own claim, was the 6th"})
    assert r["relation"] != "other_verb"


def test_race_as_classifying_object_and_god_as_name():
    # gate audit 2026-10-13 (27B): races classify an individual; "God" is a named deity
    assert fg._end_ok("Inhumans", "leader_of", True, "t") is None
    assert fg._end_ok("Skrull", "revealed_as", True, "t") is None
    assert fg._end_ok("God", "contacted", True, "t") is None
    # a race is still no actor or person end
    assert fg._end_ok("Skrulls", "attacked", False, "t")
    assert fg._end_ok("Kree", "contacted", True, "t")


def test_knowledge_relation_with_clause_object_becomes_dash():
    # gate audit 2026-10-13 (27B): the A115/A133 route `learned|-` instead of dropping the row
    r = fg.normalise({"subject": "Avengers", "relation": "learned", "object": "the X-Men's X-Mansion had been attacked",
                      "quote": "the Avengers learned that the X-Men's X-Mansion had been attacked"})
    assert r["object"] is None
    r = fg.normalise({"subject": "Ghost Rider", "relation": "discovered", "object": "Zarathos",
                      "quote": "Ghost Rider discovered Zarathos"})
    assert r["object"] == "Zarathos"  # a proper name stays


def test_short_quote_whole_list_line_passes():
    import label_single as ls
    w = "| Affiliation =\nAvengers\nNed Leeds\nHe was lost. Tai died."
    kept, dropped = ls.fact_gate_keep([{"subject": "Happy Hogan", "relation": "member_of", "object": "Avengers",
                                        "quote": "Avengers"}], w)
    assert kept and not dropped
    kept, dropped = ls.fact_gate_keep([{"subject": "Happy Hogan", "relation": "lost_power", "object": None,
                                        "quote": "lost"}], w)
    assert dropped and "shorter than 12" in dropped[0]["why"]


def test_possessive_thing_object_is_no_bare_pronoun():
    assert fg._end_ok("his father's cufflinks", "wore", True, "fact") is None
    assert fg._end_ok("his apartment", "located_at", True, "fact") is None
    assert "pronoun" in (fg._end_ok("his abusive father", "resides_at", True, "fact") or "")
    assert "pronoun" in (fg._end_ok("his son", "helped", True, "fact") or "")


def test_citation_titles_raise_no_name_flags():
    """b8933: {{r|Peter Parker, The Spectacular Spider-Man Vol 1 100}} is a citation, not a second name."""
    import big_flags as bf
    text = ("First crossing paths with Spider-Man while attempting to free her father,"
            "{{r|Amazing Spider-Man Vol 1 194}} a romance blossomed."
            "{{r|Peter Parker, The Spectacular Spider-Man Vol 1 100}}")
    ev = [{"subject": "Felicia Hardy", "verb": "met", "object": "Spider-Man", "quote": "First crossing paths with Spider-Man"}]
    flags = bf.check(ev, text)[0]
    assert not [f for f in flags if "window has both" in f or "fuller name" in f]


def test_comma_before_two_letter_initialism_is_one_place():
    """b8951: "Washington, D.C." split into "Washington" + "D.C." arrivals; "Hydra, A.I.M." is still a list."""
    import importlib.util
    import verify_row_wiki as vrw
    # series/ is gitignored: a worktree reads the main checkout's corpus
    dbs = [p for p in (CODE / "series/marvel/facts.db", CODE.parents[2] / "series/marvel/facts.db") if p.exists()]
    if not dbs:
        pytest.skip("no marvel facts.db on disk")
    spec = importlib.util.spec_from_file_location("label_single", CODE / "tools/train/label_single.py")
    ls = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ls)
    wiki = vrw.Wiki(str(dbs[0]))
    w = "John and Lemar had to head to Washington, D.C. because Hydra, A.I.M. and Viper fought them."
    kept, dropped = ls.gate([{"subject": "John", "verb": "arrived", "object": "Washington, D.C.",
                              "quote": "John and Lemar had to head to Washington, D.C."}], w, wiki)
    assert [r["object"] for r in kept] == ["Washington, D.C."], dropped
    kept, _ = ls.gate([{"subject": "Hydra, A.I.M. and Viper", "verb": "fought", "object": "John",
                        "quote": "Hydra, A.I.M. and Viper fought them"}], w, wiki)
    assert sorted(r["subject"] for r in kept) == ["A.I.M.", "Hydra", "Viper"]


def test_reunited_is_no_joining_flag():
    """'reunited with X' is a meeting; 'united with' matched inside it (131 approved met rows flagged)."""
    import big_flags as bf
    ev = [{"subject": "Brian", "verb": "met", "object": "Psylocke", "quote": "Brian reunited with Psylocke"}]
    assert not [f for f in bf.check(ev, "Brian reunited with Psylocke.")[0] if "R4" in f]
    ev = [{"subject": "Thor", "verb": "met", "object": "Loki", "quote": "Thor united with Loki"}]
    assert [f for f in bf.check(ev, "Thor united with Loki.")[0] if "R4" in f]


def test_short_capitalised_end_is_a_name():
    """MJ, Ox, Wu, Li (and Po) are names: the <=2-char 'garbage end' flag hit 26 approved rows, all kept."""
    import big_flags as bf
    ev = [{"subject": "Peter", "verb": "met", "object": "MJ", "quote": "Peter later sought out MJ"}]
    assert not [f for f in bf.check(ev, "Peter later sought out MJ.")[0] if "garbage" in f]


def test_torture_and_controlled_acts_are_in_the_vocabulary():
    # owner 2026-11-04: torture of a captive is no fight; an act under mind control names its controller
    w = "The Black Queen cruelly chained and tortured the X-Men. Under Mastermind's control, Phoenix attacked Cyclops."
    rows = [{"quote": "The Black Queen cruelly chained and tortured the X-Men", "subject": "Phoenix",
             "relation": "tortured", "object": "X-Men", "modality": "actual", "certainty": "stated",
             "asserted_by": None, "canon": None},
            {"quote": "Under Mastermind's control, Phoenix attacked Cyclops", "subject": "Phoenix",
             "relation": "attacked", "object": "Cyclops", "modality": "controlled", "certainty": "stated",
             "asserted_by": "Mastermind", "canon": None}]
    for r in rows:
        assert fg.validate(r) == []
    bad = dict(rows[1], asserted_by=None)
    assert fg.validate(bad)  # a controlled act must name its controller
