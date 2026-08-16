"""Tests for index-time semantic classification.

Deterministic rules settle most of what a page is. What they cannot settle is
the handful that are *structurally identical* to the pages that belong: Spirit
Bomb Super Saiyan and Great Ape both read `Class = Transformation` and both sit
in `Saiyans`, and only one is a form a Saiyan body reaches.

The contract these tests hold: the model is asked once, at index time, and
retrieval only ever reads the stored answer.
"""

from __future__ import annotations

import pytest

from scriptengine.ingest.classify import PROPERTIES, parse_response
from scriptengine.retrieve import semantics
from scriptengine.retrieve.roster import _semantic_reason
from scriptengine.stores.facts import FactStore


@pytest.fixture()
def store(tmp_path):
    store = FactStore(tmp_path / "facts.db")
    store.initialise()
    store.ensure_semantics()
    yield store
    store.close()


class TestParseResponse:
    def test_it_reads_a_clean_answer(self):
        parsed = parse_response(
            '{"semantic_type": "transformation",'
            ' "properties": {"race_exclusive": true, "teachable": false},'
            ' "reason": "Only Saiyans reach it."}'
        )
        assert parsed is not None
        assert parsed.semantic_type == semantics.TRANSFORMATION
        assert parsed.properties == {"race_exclusive": True, "teachable": False}
        assert parsed.reason == "Only Saiyans reach it."

    def test_it_tolerates_the_fences_it_was_told_not_to_use(self):
        parsed = parse_response(
            'Sure!\n```json\n{"semantic_type": "technique", "properties": {}, '
            '"reason": "x"}\n```'
        )
        assert parsed is not None and parsed.semantic_type == semantics.TECHNIQUE

    def test_a_type_outside_the_vocabulary_becomes_unknown(self):
        """The model does not get to invent categories."""
        parsed = parse_response('{"semantic_type": "vibe", "properties": {}}')
        assert parsed is not None and parsed.semantic_type == semantics.UNKNOWN

    def test_only_declared_properties_survive(self):
        parsed = parse_response(
            '{"semantic_type": "technique",'
            ' "properties": {"teachable": true, "smells_nice": true}}'
        )
        assert parsed is not None
        assert "smells_nice" not in parsed.properties
        assert set(parsed.properties) <= set(PROPERTIES)

    @pytest.mark.parametrize("text", ["", "no json here", "{broken", "[1,2,3]"])
    def test_junk_is_refused_rather_than_guessed(self, text):
        assert parse_response(text) is None


class TestSemanticReason:
    """Stored classifications may reject a member. They may never add one."""

    def _save(self, store, title, properties, reason="because"):
        store.save_semantics(
            title=title, revid=1, prompt_version="test",
            semantic_type=semantics.TRANSFORMATION, properties=properties,
            reason=reason, model="test",
        )
        store.commit()

    def test_a_page_that_was_never_classified_falls_through(self, store):
        assert _semantic_reason(store, "Never Seen", "saiyan") == ""

    def test_externally_granted_is_rejected(self, store):
        """Dark Dragon Ball Enhancement comes from Dark Shenron, not from being
        a Saiyan."""
        self._save(store, "Dark Enhancement", {"externally_granted": True})
        assert "granted from outside" in _semantic_reason(store, "Dark Enhancement", "saiyan")

    def test_a_stacked_form_is_rejected(self, store):
        self._save(
            store, "Spirit Bomb Super Saiyan",
            {"stackable": True, "biologically_intrinsic": False},
        )
        reason = _semantic_reason(store, "Spirit Bomb Super Saiyan", "saiyan")
        assert "stacks on another form" in reason

    def test_an_intrinsic_form_that_stacks_is_kept(self, store):
        """Stacking alone is not disqualifying: Super Saiyan Blue stacks with
        Kaio-ken and is still a Saiyan form."""
        self._save(
            store, "Super Saiyan Blue",
            {"stackable": True, "biologically_intrinsic": True, "race_exclusive": True},
        )
        assert _semantic_reason(store, "Super Saiyan Blue", "saiyan") == ""

    def test_teachable_and_not_race_exclusive_is_rejected(self, store):
        self._save(store, "Kaio-ken", {"teachable": True, "race_exclusive": False})
        assert "teachable" in _semantic_reason(store, "Kaio-ken", "saiyan")

    def test_a_race_exclusive_form_is_kept(self, store):
        self._save(
            store, "Great Ape",
            {"race_exclusive": True, "biologically_intrinsic": True},
        )
        assert _semantic_reason(store, "Great Ape", "saiyan") == ""

    def test_race_exclusivity_outranks_an_external_trigger(self, store):
        """Great Ape needs a full moon and Super Saiyan God a ritual of five
        Saiyans. The classifier reads both as external grants; only a Saiyan
        answers either, so the exclusivity is what matters."""
        self._save(
            store, "Great Ape",
            {"race_exclusive": True, "externally_granted": True, "teachable": True},
        )
        assert _semantic_reason(store, "Great Ape", "saiyan") == ""

    def test_needing_an_artifact_is_disqualifying(self, store):
        self._save(store, "Spirit Bomb Super Saiyan", {"requires_artifact": True})
        assert "outside the body" in _semantic_reason(
            store, "Spirit Bomb Super Saiyan", "saiyan"
        )

    def test_the_stored_reason_is_reported(self, store):
        self._save(
            store, "Ultimate", {"externally_granted": True},
            reason="Elder Kai unlocks it for anyone.",
        )
        assert "Elder Kai unlocks it" in _semantic_reason(store, "Ultimate", "saiyan")


class TestCache:
    def test_a_classification_survives_a_store_reset(self, store):
        """`index` rebuilds every other table; this one costs real inference."""
        store.save_semantics(
            title="Beast", revid=3, prompt_version="test",
            semantic_type=semantics.TRANSFORMATION, properties={"race_exclusive": True},
            reason="", model="test",
        )
        store.commit()
        store.reset()
        store.ensure_semantics()
        assert store.semantics_of("Beast") is not None
