"""overrides.yaml `episode_map`: a wiki's own chapter<->episode relations.

The default reads JJK's `anime episode` / `adapted from` edges between pages
titled "Chapter N" / "Episode M". Other wikis link the two under other
relation names and title instalments by name, with the number in the infobox
(Bleach `episodenumber`, One Piece `#`); a number is read, never inferred.
"""
from scriptengine.retrieve.citations import EpisodeIndex, declared_episode_map

FACTS = {
    "The Man who Hates Shinigami": {"episodenumber": "22"},
    "14 Days Before Rukia's Execution": {"episodenumber": "23"},
    "Recap Special": {"#": "Recap 1"},
    "Fillers Galore": {"episodenumber": "64"},
}
LABELS = {
    "The Man who Hates Shinigami": "ep", "14 Days Before Rukia's Execution": "ep",
    "Recap Special": "ep", "Fillers Galore": "tybw",
}
SPEC = {
    "links": [{"relation": "chapters", "from": "episode"}],
    "chapter_number": ["title"],
    "episode_number": ["title", "episodenumber", "#"],
    "episode_labels": ["ep"],
}


def _map(edges, spec=SPEC):
    return declared_episode_map(spec, edges, lambda n: FACTS.get(n, {}), lambda n: LABELS.get(n, ""))


def test_numbers_come_from_the_infobox_when_the_title_has_none():
    m = _map([("14 Days Before Rukia's Execution", "chapters", "Chapter 78"),
              ("14 Days Before Rukia's Execution", "chapters", "Chapter 79")])
    assert m == {"78": "23", "79": "23"}


def test_first_adaptation_wins_and_unreadable_numbers_map_nothing():
    m = _map([("The Man who Hates Shinigami", "chapters", "Chapter 78"),
              ("14 Days Before Rukia's Execution", "chapters", "Chapter 78"),
              ("Recap Special", "chapters", "Chapter 1")])
    assert m == {"78": "22"}  # "Recap 1" is not a number: never guessed


def test_episode_labels_keep_one_anime():
    assert _map([("Fillers Galore", "chapters", "Chapter 500")]) == {}


def test_link_direction_and_relation_filter():
    spec = {"links": [{"relation": "anime episode", "from": "chapter"}]}
    m = _map([("Chapter 5", "anime episode", "Episode 2"), ("Chapter 6", "mentions", "Episode 9")], spec)
    assert m == {"5": "2"}


def test_without_a_declaration_the_store_path_is_the_default():
    class Store:
        def edges_by_relation(self, rel, limit=2000):
            return [{"source": "Chapter 3", "target": "Episode 1"}] if rel == "anime episode" else []
    assert EpisodeIndex.from_store(Store()).episode_for("3") == "1"
    assert EpisodeIndex.from_store(Store(), {}).episode_for("3") == "1"
