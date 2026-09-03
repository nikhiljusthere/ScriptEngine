"""Constraints on `questions/` itself, not on what the engine answers.

The bank decides what counts as a wrong answer, so a defect in it moves the
score with no engine change at all. The previous gold sourced Meruem's
abilities to a powerscaling wiki and marked the engine down for not returning
techniques that One-Punch Man's wiki says do not exist. These tests are the
mechanical half of stopping that recurring.
"""

import pytest

from scriptengine.config import Settings
from scriptengine.eval import questions as Q
from scriptengine.eval.canon_gold import norm


@pytest.fixture(scope="module")
def banks():
    # Resolved from settings rather than a CWD-relative glob. `test_gold_hygiene`
    # globs `Path("scriptengine/eval")` and only passes when pytest is invoked
    # from the repo root; that is a latent bug, not a pattern to copy.
    return Q.load_all(Settings().questions_root)


def test_bank_loads_and_covers_every_indexed_series(banks):
    found = {b.series for b in banks}
    assert found == {"db", "onepiece", "bleach", "hxh",
                     "opm", "jjk", "berserk", "csm"}


def test_every_question_asserts_something(banks):
    for q in (q for b in banks for q in b.questions):
        assert q.answer, f"{q.id} has an empty answer"
        assert q.scored_items(), f"{q.id} has nothing solid enough to score"


def test_every_question_is_sourced_and_dated(banks):
    for q in (q for b in banks for q in b.questions):
        assert q.sources, f"{q.id} names no source"
        assert q.verified, f"{q.id} has no verified date"
        assert q.subject, f"{q.id} names no subject"


def test_every_source_is_an_absolute_url(banks):
    for q in (q for b in banks for q in b.questions):
        for url in list(q.sources) + [u for i in q.answer for u in i.sources]:
            assert url.startswith(("http://", "https://")), \
                f"{q.id} source {url!r} is not a URL"


def test_no_banned_source_anywhere(banks):
    """VS Battles and friends argue their entries rather than documenting them.

    A set scored against a powerscaling page measures the argument, not the
    series.
    """
    for q in (q for b in banks for q in b.questions):
        for url in list(q.sources) + [u for i in q.answer for u in i.sources]:
            for bad in Q.BLOCKED_DOMAINS:
                assert bad not in url.lower(), f"{q.id} cites {bad}"


def test_a_set_has_a_wiki_source(banks):
    """A set asserts completeness, and only the wiki maintains a complete list.

    An editorial ranking may corroborate a set; it may never carry one. A
    "top 10 forms" listicle omits and invents entries as a matter of format.
    """
    for q in Q.sets(banks):
        tiers = {q.tier} | {i.tier for i in q.answer if i.tier}
        assert "wiki" in tiers, f"{q.id} is a set with no wiki source"


def test_a_community_source_is_never_alone(banks):
    for q in (q for b in banks for q in b.questions):
        if q.tier == "community":
            assert len(q.sources) > 1, \
                f"{q.id} rests on a community source alone"


def test_items_are_distinct_after_normalisation(banks):
    """`Gear 4` and `Gear Fourth` are one item written twice.

    Left in, they inflate the canon count and depress recall for an engine
    that correctly returned it once.
    """
    for q in (q for b in banks for q in b.questions):
        keys: dict[str, str] = {}
        for i in q.answer:
            for key in [norm(i.item)] + [norm(a) for a in i.aliases]:
                assert key not in keys or keys[key] == i.item, \
                    f"{q.id}: {i.item!r} and {keys[key]!r} both normalise to {key!r}"
                keys[key] = i.item


def test_an_item_that_prefixes_another_is_deliberate(banks):
    """`Super Saiyan` sits inside `Super Saiyan 2` and both are real.

    Substring matching is deliberately out of the scorer for exactly this
    reason, so the pair is legitimate -- but it must be a decision someone
    made, recorded in the note, not an accident of transcription.
    """
    for q in (q for b in banks for q in b.questions):
        names = [norm(i.item) for i in q.answer]
        overlap = any(a != b and b.startswith(a + " ") for a in names for b in names)
        if overlap:
            assert q.note, f"{q.id} has prefix-overlapping items and no note"


def test_ids_are_unique_across_the_whole_bank(banks):
    seen: dict[str, str] = {}
    for b in banks:
        for q in b.questions:
            assert q.id not in seen, f"{q.id} reused ({seen.get(q.id)} and {b.series})"
            seen[q.id] = b.series


def test_question_texts_are_unique(banks):
    """Two questions may not share a string, even across series.

    Question text is a key in two places: `canon_report.render()` picks the
    subset comparable with earlier runs by matching it, and
    `diagnose_misses.py` resolves an item's canon list and series the same way.
    A duplicate silently pulled a new 16-item question into the comparable
    figure -- 37 questions and 229 items where the migration established 36 and
    213 -- and left bucketing ambiguous for both copies. An id collision is
    already refused above; this is the same defect one field over.
    """
    seen: dict[str, str] = {}
    for b in banks:
        for q in b.questions:
            assert q.question not in seen, (
                f"{q.id} and {seen.get(q.question)} both ask "
                f"{q.question!r}"
            )
            seen[q.question] = q.id


def test_diagnosis_knows_the_subject_of_every_question(banks):
    """`diagnose_misses.SUBJECT` must cover the bank, not a snapshot of it.

    It was a 37-entry literal keyed on question text. When the bank grew to 135
    every new question diagnosed with `character = ""`, and with no subject the
    ownership, stored-row and heading checks all read empty -- so those misses
    could only ever bucket as `unlinked page` or `corpus gap`. The run's bucket
    table reported `corpus gap` at 31% and `extraction gap` at 2%; with the
    subject actually resolving they are 10% and 27%. The bug inverted the
    remediation ordering the report exists to produce, while every test passed.
    """
    from scriptengine.eval.diagnose_misses import SUBJECT

    for q in (q for b in banks for q in b.questions):
        assert q.question in SUBJECT, \
            f"{q.id} is not in diagnose_misses.SUBJECT -- it would diagnose " \
            f"with no subject and mis-bucket every miss"


def test_retired_items_carry_a_reason(banks):
    for b in banks:
        for row in b.retired:
            assert row.get("question"), f"{b.series}: a retired row names no question"
            assert row.get("item"), f"{b.series}: a retired row names no item"
            assert row.get("reason"), f"{b.series}: a retired row gives no reason"


def test_as_gold_reproduces_the_shape_diagnose_misses_unpacks(banks):
    """`diagnose_misses.py` does `for series, query, _ in GOLD`.

    That tuple shape is a compatibility contract, not a convenience.
    """
    gold = Q.as_gold(Q.sets(banks))
    assert gold
    for series, query, canon in gold:
        assert isinstance(series, str) and series
        assert isinstance(query, str) and query
        assert isinstance(canon, list) and canon
        for item, aliases in canon:
            assert isinstance(item, str) and item
            assert isinstance(aliases, list)


def test_canon_gold_still_exports_what_its_importer_needs():
    from scriptengine.eval import canon_gold

    assert callable(canon_gold.norm)
    assert canon_gold.GOLD
    assert isinstance(canon_gold.RECALL_ONLY, set)


def test_a_malformed_bank_is_refused(tmp_path):
    (tmp_path / "db.json").write_text(
        '{"series": "db", "questions": [{"id": "x", "question": "q"}]}',
        encoding="utf-8",
    )
    with pytest.raises(Q.QuestionsError):
        Q.load_all(tmp_path)


def test_an_empty_bank_is_refused(tmp_path):
    with pytest.raises(Q.QuestionsError):
        Q.load_all(tmp_path)


# ── load_file: the campaign batches' loader ───────────────────────────────────


def _campaign_batch_text() -> str:
    return (
        '{"series": "jjk", "updated": "2026-08-19", "questions": ['
        '{"id": "jjk-pg-x-001", "kind": "fact", '
        '"question": "What is the test question?", "subject": "Test Subject", '
        '"scope": "closed", "expect_mode": "qa", "tier": "wiki", '
        '"verified": "2026-08-19", '
        '"sources": ["https://jujutsu-kaisen.fandom.com/wiki/Test_Page"], '
        '"answer": [{"item": "Test Answer"}], "accept": "any"}'
        ']}'
    )


def test_load_file_reads_an_underscore_prefixed_batch(tmp_path):
    """Campaign batches sit under `_*.json` names that `load_all` skips.

    `load_file` is how they get loaded instead: the declared `series` field
    wins over the stem, so the file may live anywhere it says whose it is.
    """
    path = tmp_path / "_jjk_page_test.json"
    path.write_text(_campaign_batch_text(), encoding="utf-8")

    bank = Q.load_file(path)
    assert bank.series == "jjk"
    assert len(bank.questions) == 1
    assert bank.questions[0].id == "jjk-pg-x-001"
    Q.validate([bank])


def test_load_all_still_skips_underscore_prefixed_files(tmp_path):
    """A campaign in progress must never move the official bank's number."""
    (tmp_path / "_jjk_page_test.json").write_text(
        _campaign_batch_text(), encoding="utf-8")
    with pytest.raises(Q.QuestionsError):
        Q.load_all(tmp_path)  # no non-underscore bank at all


def test_load_file_refuses_a_malformed_batch(tmp_path):
    path = tmp_path / "_jjk_page_test.json"
    path.write_text('{"series": "jjk", "questions": [{"id": "x"}]}',
                    encoding="utf-8")
    with pytest.raises(Q.QuestionsError):
        Q.load_file(path)


def test_load_file_refuses_a_missing_path(tmp_path):
    with pytest.raises(Q.QuestionsError):
        Q.load_file(tmp_path / "_jjk_page_absent.json")


def test_load_bank_still_checks_the_declared_series(tmp_path):
    """`load_bank` derives the filename from the series name, so a file that
    declares a different one is filed wrong and must be refused as before."""
    (tmp_path / "db.json").write_text(
        '{"series": "opm", "questions": ['
        '{"id": "x-1", "kind": "fact", "question": "q?", "subject": "s", '
        '"tier": "wiki", "verified": "2026-08-19", '
        '"sources": ["https://onepunchman.fandom.com/wiki/X"], '
        '"answer": [{"item": "a"}]}]}' ,
        encoding="utf-8",
    )
    with pytest.raises(Q.QuestionsError):
        Q.load_bank("db", tmp_path)


def test_norm_keeps_cjk_intact():
    """A kanji gold must survive the fold.

    The 2026-08-24 campaign retired every JJK kanji question ("the scorer's
    normalization strips CJK, so it never passes in any phrasing"). The wiki
    records the kanji and a corpus of correct data has to be able to answer
    them: the ASCII-only character class in `norm` was erasing the answer
    before scoring ever saw it.
    """
    assert norm("虎杖悠仁") == "虎杖悠仁"
    # The ASCII folds the class was doing stay unchanged.
    assert norm("Machine Gun Blows") == "machine gun blow"
    assert norm("Shūsuke") == "shusuke"
