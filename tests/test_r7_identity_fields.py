"""R-7 (CSM iter1, 2026-09-10): the per-wiki identity_fields map.

The T0 pilot (reports/csm/T0_PILOT_CSM.md) found 61 CSM infobox keys outside
the engine's IDENTITY_FIELDS + UNCHECKED_KEYS vocabulary, silently left
uncovered by the page-sweep identity builder (fix class R-7). The fix is a
per-wiki key -> question-template map in series/csm/overrides.yaml, consulted
ahead of the engine dict (config.identity_fields): model-free, no series name
in .py, no reindex.
"""
from scriptengine.config import identity_fields, load_overrides, series_paths


def test_identity_fields_config_shape():
    assert identity_fields(None) == {}
    m = identity_fields({"identity_fields": {
        "Species": "What species is {name}?",
        "JNAME": "What is the Japanese title of {name}?",
    }})
    assert m == {
        "species": "What species is {name}?",
        "jname": "What is the Japanese title of {name}?",
    }


def test_csm_identity_fields_covers_the_t0_vocabulary_gap():
    m = identity_fields(load_overrides(series_paths("csm")))
    # 57 keys: the 61 unmatched T0 keys minus the four handled elsewhere by
    # design -- `name` (the subject, the builder skips it), `alias` /
    # `affiliation` (roster path, LIST_FIELDS), `image1` (a media filename,
    # prose-unreachable; G3 could never chunk a .png).
    assert len(m) == 57
    # The four T0 near-miss spellings reuse the engine's canonical questions
    # verbatim (underscore/space + CSM naming vs the engine vocabulary):
    assert m["anime_debut"] == "In which anime episode is {name} first depicted?"
    assert m["manga_debut"] == "In which manga chapter does {name} first appear?"
    assert m["japanese voice"] == "Who is {name}'s Japanese voice actor?"
    assert m["english voice"] == "Who is {name}'s English voice actor?"
    for excluded in ("name", "alias", "affiliation", "image1"):
        assert excluded not in m