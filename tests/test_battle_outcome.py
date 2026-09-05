"""`battle_outcome`: a fight named by its fighters reaches its own `Outcome`.

`battle_facts` binds a battle only when the query spells its full title. The
natural phrasing names the fighters instead ("Nanami's fight against Mahito",
"the final battle against Sukuna") and the fight's page never links, so its
`Outcome` cell stayed out of the bundle. `battle_outcome` resolves that phrasing
to the one battle page whose sides name the fighters and pays for that page's
infobox, so the result of the fight the question actually means is what reaches
the script -- not a similar-but-wrong one.

The traps pinned down here, straight from the JJK oracle A-group:
* two fights share a pair of fighters (Nanami-Mahito is 1v1 in one and a
  team-fight in the other); the question names two fighters, so the tighter
  roster wins;
* "Sukuna is victorious." is the recorded outcome of seven of Sukuna's fights,
  so "the final battle" must resolve by manga chapter, not by sharing a side.
"""

from __future__ import annotations

import pytest

from scriptengine.retrieve.roster import asks_for_battle_outcome, battle_outcome
from scriptengine.stores.facts import FactStore


@pytest.fixture()
def store(tmp_path):
    with FactStore(tmp_path / "facts.db") as opened:
        opened.initialise()
        _add_battle(
            opened, "Kento Nanami vs. Mahito",
            side1="Kento Nanami", side2="Mahito",
            outcome="Nanami withdraws.", chapters="Chapter 22 - 23",
        )
        _add_battle(
            opened, "Yuji Itadori & Kento Nanami vs. Mahito",
            side1="Yuji Itadori Kento Nanami", side2="Mahito",
            outcome="Mahito withdraws.", chapters="Chapter 29 - 30",
        )
        _add_battle(
            opened, "Hajime Kashimo vs. Sukuna",
            side1="Hajime Kashimo", side2="Sukuna",
            outcome="Sukuna is victorious.", chapters="Chapter 237 - 238",
        )
        _add_battle(
            opened, "Kinji Hakari vs. Uraume",
            side1="Kinji Hakari", side2="Uraume",
            outcome="Uraume commits suicide.", chapters="Chapter 237 - 268",
        )
        _add_battle(
            opened, "Jujutsu Sorcerers vs. Sukuna",
            side1="Yuji Itadori Maki Zenin Nobara Kugisaki", side2="Sukuna",
            outcome="The jujutsu sorcerers are victorious.",
            chapters="Chapter 244 - 268",
        )
        _add_battle(
            opened, "Sukuna vs. Jogo",
            side1="Sukuna (16 Fingers)", side2="Jogo",
            outcome="Sukuna is victorious.", chapters="Chapter 114 - 116",
        )
        yield opened


def _add_battle(
    store: FactStore, title: str, *, side1: str, side2: str,
    outcome: str, chapters: str,
) -> None:
    node_id = store.connection.execute(
        "INSERT INTO nodes (name, label, is_resolved) VALUES (?, ?, 1)",
        (title, "battle"),
    ).lastrowid
    store.connection.execute(
        "INSERT INTO documents (title, page_type) VALUES (?, ?)",
        (title, "battle"),
    )
    for key, value in (
        ("side1", side1), ("side2", side2),
        ("outcome", outcome), ("chapters", chapters),
    ):
        store.connection.execute(
            "INSERT INTO facts (node_id, key, value) VALUES (?, ?, ?)",
            (node_id, key, value),
        )
    store.connection.commit()


def _outcome(facts: list[dict]) -> str | None:
    return next((f["value"] for f in facts if f["key"] == "outcome"), None)


def test_two_fighters_pick_the_tighter_roster(store):
    # "Nanami's fight against Mahito" names two fighters; the 1v1 is the tighter
    # roster and wins over the team-fight that also names both.
    facts = battle_outcome(store, "How did Nanami's fight against Mahito end?")
    assert facts
    assert facts[0]["entity"] == "Kento Nanami vs. Mahito"
    assert _outcome(facts) == "Nanami withdraws."


def test_final_battle_resolves_by_chapter_not_by_shared_outcome(store):
    # "Sukuna is victorious." is the outcome of several of his fights; "the
    # final battle" must take the latest by manga chapter, the sorcerers' win.
    facts = battle_outcome(
        store, "What was the result of the final battle against Sukuna?"
    )
    assert facts
    assert facts[0]["entity"] == "Jujutsu Sorcerers vs. Sukuna"
    assert _outcome(facts) == "The jujutsu sorcerers are victorious."


def test_named_pair_resolves_to_their_shared_fight(store):
    facts = battle_outcome(store, "Who won the fight between Kashimo and Sukuna?")
    assert facts
    assert facts[0]["entity"] == "Hajime Kashimo vs. Sukuna"
    assert _outcome(facts) == "Sukuna is victorious."


def test_unresolvable_pair_binds_no_outcome(store):
    # No single fight names both Kashimo and Mahito, so nothing is bound rather
    # than a wrong fight's result is surfaced.
    assert battle_outcome(store, "How did the fight between Kashimo and Mahito end?") == []


def test_single_fighter_without_an_ordering_word_binds_nothing(store):
    # "Sukuna" alone names seven fights and the question says none of them in
    # particular, so no outcome is bound.
    assert battle_outcome(store, "How did Sukuna's fight end?") == []


def test_battles_in_question_gets_no_outcome(store):
    # The whole-fight-list question is `battles_in`'s, not an outcome's.
    assert battle_outcome(store, "Every fight Mahoraga has ever been in") == []


def test_a_full_title_query_is_not_an_outcome_question(store):
    # Spelling the battle's full title is `battle_facts`'s path, not this one.
    assert asks_for_battle_outcome("Kento Nanami vs. Mahito") is False
    assert battle_outcome(store, "Kento Nanami vs. Mahito") == []


@pytest.mark.parametrize(
    "query",
    [
        "How did Nanami's fight against Mahito end?",
        "How did the confrontation between Hakari and Uraume end?",
        "Who won the fight between Kashimo and Sukuna?",
        "What was the result of the final battle against Sukuna?",
    ],
)
def test_outcome_questions_are_recognised(query):
    assert asks_for_battle_outcome(query) is True


@pytest.mark.parametrize(
    "query",
    [
        "Every fight Mahoraga has ever been in",
        "Who did Sukuna fight?",
        "What is Yuji Itadori's grade?",
    ],
)
def test_non_outcome_questions_are_not(query):
    assert asks_for_battle_outcome(query) is False