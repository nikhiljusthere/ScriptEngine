"""Movie citation tags: (Movie <name>) must match a film page in the corpus."""

from scriptengine.config import series_paths
from scriptengine.eval.verify import TAG, verify_script


def test_movie_tag_passes_for_a_filmed_series():
    # "Jujutsu Kaisen 0" resolves to the corpus page "Jujutsu Kaisen 0: The Movie".
    result = verify_script("The movie ends here. (Movie Jujutsu Kaisen 0)", series_paths("jjk"))
    assert result["passed"] is True


def test_movie_tag_fails_for_an_invented_film():
    result = verify_script("A film. (Movie Dune)", series_paths("jjk"))
    assert result["passed"] is False
    assert result["findings"][0]["tag"] == "(Movie Dune)"


def test_movie_tag_does_not_shadow_chapter_or_episode_tags():
    # The new alternative must not steal or break the existing branches.
    assert TAG.search("(Chapter 1)")
    assert TAG.search("(Episode 1)")
    assert TAG.search("(Movie Jujutsu Kaisen 0)")
    assert TAG.match("(Movie Jujutsu Kaisen 0)").group(6) == "Jujutsu Kaisen 0"