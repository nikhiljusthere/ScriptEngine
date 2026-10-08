"""The worked examples in the v2 prompt must pass the fact gate — and the routing must not drift.

Three jobs, one file:
  1. every SECTION D worked example's exact answer is legal to the fact gate (this is what caught
     the inverted sentence-boundary rule, which fired on 88% of real rows, and Example 3's
     out-of-vocabulary `killed` on a crowd object);
  2. the catalog's 13 fact routes name relations that exist, and its "keep verbatim" rulings name none;
  3. SECTION F of the prompt is the GENERATED block (tools/train/build_prompt.py --check), so the
     catalog and the served prompt can never drift again.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "train"))
# this worktree OWNS the catalog, the prompt and the gate; the data checkout only owns series/*.
# SCRIPTENGINE_ROOT may point elsewhere (the data), so the repo files are read from HERE.
WORKTREE = Path(__file__).resolve().parents[1]
os.environ.setdefault("SCRIPTENGINE_ROOT", str(WORKTREE))
import fact_gate  # noqa: E402

ROOT = WORKTREE
PROMPT = ROOT / "plan" / "EXTRACTION_PROCEDURE_V2.md"
CATALOG = ROOT / "plan" / "BIG_REVIEW_PATTERNS.md"

EDIT_CODES = ("A3 A12 A13 A19 A23 A31 A36 A48 A60 A64 A65 A67 A71").split()
KEEP_CODES = ("A5 A8 A10 A17 A24 A25 A27 A30 A39 A42 A45 A47 A52 A57").split()
# hints a symmetric relation once (a note, not an error) and B.9 refusals that are intentional
ALLOWED_FLAG_PREFIXES = ("fact0:", "tags present")
# a symmetric relation hinted once, and `member_of`/`leader_of` on a named group are correct


def _examples():
    text = PROMPT.read_text()
    for block in text.split("## Example ")[1:]:
        title = block.splitlines()[0]
        m = re.search(r"Passage: (\"|')(.+?)\1\n", block, re.S)
        ans = re.search(r"Answer:\n```\n(.+?)\n```", block, re.S)
        if not (m and ans):
            continue
        passage = m.group(2).replace("\n", " ")
        rows = ans.group(1)
        # the prompt wraps long rows; join continuation fragments before parsing
        rows = re.sub(r"\]\s*\n\s*", "],", rows)
        rows = re.sub(r"\}\s*\n\s*", "},", rows)
        try:
            d = json.loads(rows)
        except ValueError as e:  # pragma: no cover - a malformed example is itself a failure
            raise AssertionError(f"Example {title} does not parse as JSON: {e}")
        yield title, passage, d


def test_worked_examples_pass_the_fact_gate():
    n = 0
    for title, passage, d in _examples():
        facts, tags = d.get("facts") or [], d.get("tags") or []
        flags, _ = fact_gate.check(facts, passage, None, tags=tags)
        bad = [f for f in flags
               if not f.startswith(ALLOWED_FLAG_PREFIXES)
               and "symmetric" not in f
               and "below_floor" not in f
               and "refused" not in f]
        assert not bad, f"Example {title} teaches illegal fact rows: {bad}"
        n += 1
    assert n >= 4, f"only {n} worked examples parsed — the doc shape changed"


def test_prompt_event_section_is_still_verbatim():
    a = (ROOT / "plan" / "EXTRACTION_PROCEDURE.md").read_text()
    b = PROMPT.read_text()
    assert a in b, "SECTION A of the v2 prompt is no longer a verbatim copy of the event procedure"


def test_fact_routes_name_real_relations():
    text = CATALOG.read_text()
    for code in EDIT_CODES:
        m = re.search(rf"^\| {code} \| [^|]*\| ([^|]*)\|", text, re.M)
        assert m, f"{code} missing from the catalog"
        cell = m.group(1)
        rels = set(re.findall(r"`([a-z_]+)`", cell))
        named = {r for r in rels if r in fact_gate.RELATIONS} | ({"other_verb"} & rels)
        # a modality-only route (A19, A23) is legal: the relation depends on the clause
        mods = {r for r in rels if r in fact_gate.MODALITY}
        assert named or mods, f"{code} names no relation in the vocabulary: {cell}"
        if any(w in cell for w in ("planned", "claimed", "ordered", "attempted", "hypothetical", "dreamed")):
            assert "asserted_by" in cell, f"{code} routes a non-actual modality without asserted_by"


def test_keep_codes_name_no_relation():
    text = CATALOG.read_text()
    for code in KEEP_CODES:
        m = re.search(rf"^\| {code} \| [^|]*\| ([^|]*)\|", text, re.M)
        assert m, f"{code} missing from the catalog"
        cell = m.group(1)
        assert "fact:" not in cell and "facts:" not in cell, \
            f"{code} is a KEEP ruling but now carries a fact route: {cell}"


def test_new_tags_are_documented_and_legal():
    doc = PROMPT.read_text()
    for tag in ("no_doer", "crowd_end", "no_relation"):
        assert tag in fact_gate.TAGS, f"{tag} missing from the gate's closed tag set"
        assert f"| `{tag}` |" in doc, f"{tag} missing from the prompt's tag table"
    for tag in fact_gate.TAGS:
        flags, _ = fact_gate.check([], "a sentence that exists in the window", None,
                                   tags=[{"tag": tag, "quote": "a sentence that exists in the window"}])
        assert not [f for f in flags if f.startswith("tag1:")], f"{tag} is refused by its own gate"


def test_section_f_is_generated_not_hand_copied():
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "train" / "build_prompt.py"), "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"SECTION F is stale: {r.stdout}{r.stderr}"


def test_named_group_with_article_is_a_legal_fact_end():
    # the A3/A48/A65 joined/member_of routes depend on this (council 2026-10-08)
    assert fact_gate._end_ok("the X-Men", "joined", True, "fact", None) is None
    # ... and an indefinite end is still refused
    assert fact_gate._end_ok("an assailant", "fought", True, "fact", None)
    assert fact_gate._end_ok("a Space Phantom", "fought", True, "fact", None)


def test_quote_inside_one_sentence_is_not_flagged():
    text = "Hope van Dyne tasked Scott Lang with training him. He punched her in the lesson."
    flags, _ = fact_gate.check(
        [{"quote": "tasked Scott Lang with training", "subject": "Hope van Dyne",
          "relation": "trained", "object": "Scott Lang", "modality": "actual", "certainty": "stated"}],
        text, None)
    assert not [f for f in flags if "sentence" in f], flags
    flags2, _ = fact_gate.check(
        [{"quote": "tasked Scott Lang with training him. He punched her in the lesson.",
          "subject": "Hope van Dyne", "relation": "trained", "object": "Scott Lang",
          "modality": "actual", "certainty": "stated"}], text, None)
    assert [f for f in flags2 if "sentence" in f], flags2