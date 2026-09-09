"""G-CSM-3 (red list R-4): section-scoped intruders on the roster door.

The miss queue's R-3 rows (`reports/csm/miss_queue_csm_iter1.jsonl`:
csm-set-17, csm-char-03, csm-set-02, csm-set-01) all read the same way: the
door returns the right members *plus* intruders -- form headings inside an
ability answer, prose-filed transformation rows inside a form answer, and the
open named roster of `Tokyo Special Division 4` where the wiki's own Members
section lists the closed seven. The intruders are real members of the declared
rosters; the debt was scoping, not missing members.

The class fix (this file's subject) is three opt-in per-wiki knobs in
`series/csm/overrides.yaml`, read by series-agnostic code in
`scriptengine/retrieve/roster.py`:

* `closed_members:` on a declared roster -- a plain "members of" question
  serves the closed membership; "named member" keeps the full roster
  (csm-set-17 vs csm-set-08).
* `ability_sections_umbrella:` -- the sections an umbrella question's
  ("Every ability of X") section pass reads, so the wiki's form headings stop
  diluting an ability answer (csm-set-02, csm-char-02, csm-char-03).
* `ability_row_sections:` -- the sections an explicit-kind question reads a
  kind's *extracted* rows from, so Denji's prose-filed `Hybrid/Devil
  Transformation` rows answer his abilities but not his forms
  (csm-set-01 vs csm-char-01, whose gold includes both rows).

Every knob is a no-op on a wiki that declares none of them, which is the
JJK-100% invariance argument: the JJK pins below are the standing check.
Zero GPU: everything here is model-free (declared-resolution + SQL store
reads through `build_roster`).

Documented residue, deliberately not encoded: csm-set-02's three trait rows
(`Enhanced Strength/Speed/Smell`) and csm-char-03's five (`Enhanced Reflexes`
+ the four `Devil Contracts` rows) are per-character bank curation calls --
the same `Enhanced X` family is *kept* in csm-char-04's gold and
csm-char-03's own gold (`Enhanced Durability/Speed`) sits in the same groups
-- so no mechanical scoping can green those two rows without hardcoding
per-character bank answers. They stay red with the reduced intruder counts.
"""

from __future__ import annotations

import pytest

from scriptengine.config import series_paths
from scriptengine.retrieve.roster import build_roster


def _paths(series: str):
    paths = series_paths(series)
    if not paths.facts_db.exists():
        pytest.skip(f"{series} is not indexed")
    return paths


def _names(paths, query: str) -> set[str]:
    return {m.name for m in build_roster(paths, query).members}


class TestClosedMembershipScoping:
    """csm-set-17 vs csm-set-08: one declared set, two question shapes.

    The wiki's Members section lists the closed Part-1 membership (seven
    humans); the declared `members:` list is the full named roster, later-arc
    fiends included. The door must serve both questions from one declaration.
    """

    def test_a_plain_members_question_serves_the_closed_core(self):
        # csm-set-17 verbatim.
        paths = _paths("csm")
        roster = build_roster(paths, "Who are the members of Tokyo Special Division 4?")
        assert {m.name for m in roster.members} == {
            "Makima", "Aki Hayakawa", "Denji", "Power", "Himeno",
            "Kobeni Higashiyama", "Hirokazu Arai",
        }
        assert roster.kind == "declared"
        # Report, don't hide: the full roster was read and the scoped-out
        # members say why they are not in the answer.
        assert roster.candidates == 14
        closed = [e for e in roster.rejected if e.get("rule") == "closed-members"]
        assert {e["name"] for e in closed} == {
            "Kishibe", "Angel Devil", "Beam", "Galgali", "Princi", "Fushi", "Madoka",
        }

    def test_a_named_members_question_keeps_the_full_roster(self):
        # csm-set-08 verbatim: the qualifier word `named` asks for the named
        # roster, and the closed scope must not fire.
        paths = _paths("csm")
        roster = build_roster(paths, "Every named member of Tokyo Special Division 4")
        assert len(roster.members) == 14
        assert all(e.get("rule") != "closed-members" for e in roster.rejected)


class TestUmbrellaAbilityQuestionsScopeTheSectionPass:
    """csm-set-02 / csm-char-02 / csm-char-03: the wiki files a character's
    forms under `Appearance`; the bank's ability gold carries no form
    heading, so an umbrella question's section pass must not read them."""

    def test_ability_of_power_drops_the_form_headings(self):
        # csm-set-02 verbatim: 18 -> 16 (the two `Appearance` form headings
        # leave; every extracted row stays).
        paths = _paths("csm")
        names = _names(paths, "Every ability of Power")
        assert "Fiend Form" not in names and "Devil Form" not in names
        assert {
            "Blood Manipulation", "Blood Spear", "Blood Hammer", "Blood Chainsaw",
            "Thousand Tera Blood Rain", "Blood Knife", "Blood Scythe",
            "Blood Dagger", "Blood Axe", "Blood Transfer",
        } <= names
        # The bank's remaining residue is the three trait rows (documented
        # curation calls, not a scoping debt).
        assert names == {
            "Enhanced Strength", "Enhanced Speed", "Enhanced Smell",
            "Blood Manipulation", "Blood Spear", "Blood Hammer",
            "Blood Chainsaw", "Thousand Tera Blood Rain", "Blood Knife",
            "Blood Scythe", "Blood Dagger", "Blood Axe", "Blood Transfer",
            "Blood Empowerment", "Knifemanship", "Acting Skills",
        }

    def test_documented_ability_of_power_is_the_full_gold_set(self):
        # csm-char-02 verbatim: its gold is exactly the 16 extracted rows, so
        # the section pass contributes nothing and the answer is the gold set.
        paths = _paths("csm")
        names = _names(paths, "Every documented ability of Power")
        assert names == {
            "Enhanced Strength", "Enhanced Speed", "Enhanced Smell",
            "Blood Manipulation", "Blood Spear", "Blood Hammer",
            "Blood Chainsaw", "Thousand Tera Blood Rain", "Blood Knife",
            "Blood Scythe", "Blood Dagger", "Blood Axe", "Blood Transfer",
            "Blood Empowerment", "Knifemanship", "Acting Skills",
        }

    def test_ability_of_aki_drops_the_form_headings(self):
        # csm-char-03 verbatim: 18 -> 16. The gold items filed in the
        # `Devil Contracts` group (`Summoning`, `Precognition`) must stay --
        # dropping the group would cost recall the bank counts.
        paths = _paths("csm")
        names = _names(paths, "Every ability of Aki Hayakawa")
        assert "Human Form" not in names and "Fiend Form" not in names
        assert {"Summoning", "Precognition", "Enhanced Speed", "Enhanced Durability"} <= names
        assert len(names) == 16


class TestExplicitKindQuestionsScopeTheExtractedPass:
    """csm-set-01 vs csm-char-01: the same two prose rows are an answer to
    one question and an intruder in the other."""

    def test_form_of_denji_reads_forms_from_the_declared_section_only(self):
        # csm-set-01 verbatim: the five `Appearance` form headings, and none
        # of the prose rows filed under `Abilities / Hybrid Powers`. Folded
        # through the bank's aliases these are its four gold items.
        paths = _paths("csm")
        names = _names(paths, "Every form of Denji")
        assert names == {
            "Human Form (Pre-Fusion)", "Human Form (Post-Fusion)",
            "Hybrid Form", "Devil Form", "Combined Form",
        }

    def test_ability_of_denji_keeps_the_extracted_transformation_rows(self):
        # csm-char-01 verbatim: the umbrella question keeps Denji's two
        # transformation *rows* (his gold includes both) while the *form
        # headings* under `Appearance` stay out of the ability answer.
        paths = _paths("csm")
        names = _names(paths, "Every ability of Denji")
        assert {"Hybrid Transformation", "Devil Transformation"} <= names
        assert "Hybrid Form" not in names and "Combined Form" not in names
        # All seventeen gold items sit in the answer (the residue is the five
        # documented curation rows, see the module docstring).
        assert {
            "Enhanced Human Condition", "Enhanced Endurance", "Augmented Strength",
            "Augmented Durability", "Augmented Stamina", "Chainsaw Manifestation",
            "Chainsaw Retraction", "Chain Entanglement", "Chain Grappling",
            "Blood Consumption", "Nigh-Immortality", "Body Duplication",
            "Hand-to-Hand Combat", "Strategic Intelligence", "Swimming",
        } <= names


class TestUntouchedRosterPaths:
    """The fix must not move what it did not aim at."""

    def test_declared_subject_rosters_are_unchanged(self):
        paths = _paths("csm")
        assert _names(paths, "Every ability of Himeno") == {
            "Ghost Devil Contract", "Hand-to-Hand Combat",
        }
        assert _names(paths, "Every devil contract of Aki Hayakawa") == {
            "Curse Devil", "Fox Devil", "Future Devil",
        }
        assert _names(paths, "Every devil Aki Hayakawa contracted with") == {
            "Control Devil", "Curse Devil", "Fox Devil", "Future Devil",
        }

    def test_makima_ability_question_keeps_its_members(self):
        # csm-char-04 is a documented D6-extraction floor row; the fix must
        # not lose any of what the door already reaches.
        paths = _paths("csm")
        names = _names(paths, "Every ability of Makima")
        assert {"Control", "Force Manipulation", "Enhanced Smell",
                "Immense Strength", "High Alcohol Tolerance",
                "High Intelligence", "Hand-to-Hand Combat"} <= names


class TestScopingLeavesJjkUnchanged:
    """JJK-100% invariance: JJK declares none of the three knobs, so every
    JJK question answers byte-identically to pre-fix. These pins are the
    standing check that the opt-in gates (the `umbrella` flag, the per-kind
    row-section filter, the closed-members scope) stay no-ops on a wiki that
    declares the field nowhere (the four standing gates re-run at gate time)."""

    def test_umbrella_ability_question_reads_the_union_of_kind_sections(self):
        # JJK maps both technique and transformation onto the same two
        # sections, and declares no umbrella override: the section pass reads
        # the union, exactly as before the knob existed.
        paths = _paths("jjk")
        names = _names(paths, "Every ability of Satoru Gojo")
        assert len(names) == 23
        assert {"Limitless", "Unlimited Void", "Hollow Purple", "Black Flash",
                "Immense Speed & Reflexes", "Cursed Energy Manipulation"} <= names

    def test_explicit_kind_question_reads_rows_from_subpages(self):
        # JJK's `Divine Dogs` / `Nue` rows are extracted from related-
        # techniques subpages, i.e. sections no wiki declares for the kind.
        # Without the opt-in gate the row-section filter would drop them; the
        # pin states the gate.
        paths = _paths("jjk")
        names = _names(paths, "Every technique of Sukuna")
        assert len(names) == 21
        assert {"Divine Dogs", "Nue", "Totality", "Dismantle", "Cleave"} <= names

    def test_declared_roster_keeps_every_member(self):
        # JJK declares no `closed_members` anywhere: a declared set serves its
        # full membership, `named` qualifier or not.
        paths = _paths("jjk")
        roster = build_roster(paths, "Every cursed technique")
        assert roster.kind == "declared"
        assert len(roster.members) == 38
        assert all(e.get("rule") != "closed-members" for e in roster.rejected)

    def test_form_question_keeps_the_extracted_rows(self):
        paths = _paths("jjk")
        names = _names(paths, "Every form of Satoru Gojo")
        assert len(names) == 14
        assert {"Limitless", "Unlimited Void", "Hollow Purple", "Curtain"} <= names


class TestClosedMembershipEmptyIntersection:
    """The documented data-error path: `closed_members:` disjoint from `members:`.

    Council R-2+R-3 (2026-09-09): the scoping path records the scoped-out
    members in `rejected` (report, don't hide), but on the documented data
    error -- the wiki declared a closed membership that intersects the named
    roster in nothing -- every served member would be logged as rejected
    while being served, and the warning would mis-report "the closed
    membership is served, 14 of 14". The policy, pinned here: serve the full
    list, record nothing as scoped-out, and keep the plain wording.
    Synthetic (a tmp store + a tmp overrides.yaml), so it never touches the
    CSM corpus.
    """

    MEMBERS = ("Alpha One", "Alpha Two", "Alpha Three")

    def _fixture(self, tmp_path):
        import yaml

        from scriptengine.config import SeriesPaths
        from scriptengine.stores.facts import FactStore

        store = FactStore(tmp_path / "facts.db")
        store.initialise()
        for name in self.MEMBERS:
            document = store.add_document(
                title=name, url="", page_type="character", infobox_template="",
                lead=f"{name} is a thing.", word_count=5, revid=1, fetched_at="",
            )
            node = store.add_node(name, "character", document)
            store.add_aliases(node, [name])
        store.commit()
        store.close()
        (tmp_path / "overrides.yaml").write_text(
            yaml.safe_dump({"rosters": [{
                "name": "Test Squad",
                "match": ["test squad"],
                "members": list(self.MEMBERS),
                # Deliberately disjoint from `members:` -- the data error.
                "closed_members": ["Beta One", "Beta Two"],
            }]}),
            encoding="utf-8",
        )
        return SeriesPaths(name="test", root=tmp_path)

    def test_a_disjoint_closed_membership_serves_the_full_list(self, tmp_path):
        paths = self._fixture(tmp_path)
        roster = build_roster(paths, "Who are the members of Test Squad?")
        assert {m.name for m in roster.members} == set(self.MEMBERS), (
            "the documented policy: an empty intersection serves the full list"
        )
        assert all(e.get("rule") != "closed-members" for e in roster.rejected), (
            "nothing was actually scoped out, so nothing is recorded as rejected"
        )
        assert "closed membership" not in roster.warning, (
            "the warning must not claim the closed membership was served"
        )