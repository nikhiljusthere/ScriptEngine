#!/usr/bin/env python3
"""Mechanical checks for the v2 FACT rows (plan/EXTRACTION_PROCEDURE_V2.md SECTION B).

The event layer's gate is unchanged and still runs `label_single.gate`; this file is the fact
layer's own gate. It reuses the event gate's end checks where they transfer and, where the fact
layer deliberately differs, says so and why:

  * a fact's object MAY be a place, an item, an organisation or a title. The event layer forbids
    that because `fought`/`arrived` need person ends; `resides_at San Francisco` and
    `used the Ant-Man Suit` are normal facts. So the "places only for arrived/departed/escaped"
    and species-page rules do NOT apply here (EXTRACTION_PROCEDURE_V2.md B.1/B.8).
  * crowds, species, indefinites and bare pronouns are still refused as EITHER end (B.6/B.7).

CLAUDE-OWNERSHIP (owner 2026-10-07, plan/WINDOW_METHOD.md): this is a NEW file, not
`tools/train/big_flags.py`. No check here changes the event layer or the review catalog; anything
that should live in those two files is written to plan/FACT_LAYER_PROPOSALS_FOR_CLAUDE.md instead.
"""
import json
import re
import sys
from pathlib import Path

CODE = Path(__file__).resolve().parents[2]
ROOT = Path(__import__("os").environ.get("SCRIPTENGINE_ROOT", CODE))
sys.path.insert(0, str(CODE / "tools" / "train"))
sys.path.insert(0, str(ROOT / "tools" / "train"))
import draft_v2  # noqa: E402
import verify_row_wiki as vrw  # noqa: E402

MODALITY = ("actual", "planned", "attempted", "ordered", "claimed", "dreamed", "hypothetical")
CERTAINTY = ("stated", "reported", "apparent", "denied")
CANON = ("mcu", "comics", "alternate", "anime", "production", None)
TAGS = ("dialogue", "list_header", "production", "citation", "apposition",
        "attire", "capability", "deictic", "below_floor")

# the closed relation vocabulary (EXTRACTION_PROCEDURE_V2.md B.2). `other_verb` is the escape
# hatch (B.3); `other` is deliberately NOT accepted: it collides with the engine's `other` COLUMN
# in scriptengine/stores/facts.py's relations table, and the council renamed it for that reason.
RELATIONS = (
    # relationship
    "trained", "mentored", "recruited", "allied_with", "joined", "left_group", "member_of",
    "leader_of", "friend_of", "rival_of", "parent_of", "child_of", "sibling_of", "married",
    "dated", "married_to",
    # interaction
    "helped", "assisted", "protected", "contacted", "warned", "persuaded", "tricked", "ordered",
    "hired", "paid", "gave", "took", "attacked", "interrogated", "apologised_to", "greeted",
    # possession / creation
    "created", "built", "stole", "used", "destroyed", "owns", "handed", "wielded", "wore",
    "piloted",
    # identity
    "alias_of", "disguise_as", "revealed_as", "codename_of", "also_known_as", "real_name_of",
    # state / change
    "gained_power", "lost_power", "transformed_into", "became", "resides_at", "located_at",
    "dies", "born", "aged", "wounded", "healed", "kidnapped",
    # knowledge
    "learned", "revealed", "discovered", "forgot", "remembered", "suspected",
)
# relations whose object is not a person: the event layer's person-end rules must not fire
NON_PERSON_OBJECT = {
    "resides_at": "place", "located_at": "place", "used": "item", "wore": "item",
    "wielded": "item", "piloted": "item", "owns": "item", "created": "thing", "built": "thing",
    "destroyed": "thing", "stole": "item", "gave": "thing", "handed": "thing", "took": "thing",
    "gained_power": None, "lost_power": None, "transformed_into": "form", "aged": None,
    "learned": "anything", "revealed": "anything", "discovered": "anything", "forgot": "anything",
    "remembered": "anything", "suspected": "anything", "revealed_as": "name",
    "alias_of": "name", "codename_of": "name", "also_known_as": "name", "real_name_of": "name",
    "disguise_as": "name", "became": "title", "married": "person", "dated": "person",
    "married_to": "person",
}
# symmetric relations: X friend_of Y is the same claim as Y friend_of X, so write it once
SYMMETRIC = {"friend_of", "rival_of", "married", "married_to", "dated", "sibling_of",
             "allied_with", "helped", "assisted", "protected", "contacted", "warned"}

MIN_QUOTE = 12
MAX_QUOTE = 400  # the store truncates quotes at 400 chars (facts.py save_relations); see PROPOSALS

# B.6/B.7: never an end. Crowds and indefinites (R11/A5/A52/A57), species (A25), bare pronouns (B.7).
# Split in two on purpose: an ARTICLE ("his apartment", "the Bus") is a perfectly good fact end for a
# place/item/role (B.8), but a bare CROWD WORD ("the guards") is never an end, whatever the relation.
CROWD_WORDS = re.compile(
    r"(?<!-)\b(?:police|former|active|several|some|many|various|students|heroes|villains|guards|"
    r"soldiers|forces|army|armada|fleet|thugs|men|women|agents|allies|others|troops|civilians|"
    r"villagers|crowd|soldier|guard|people|staff|crew|staff)\b"
    r"|\b(?:men|women|ones|rest)\s+of\b"
    r"|\s+of the\b|\bs'\s", re.I)
ARTICLE = re.compile(r"^(?:a|an|the|his|her|their|its)\s", re.I)
SPECIES = re.compile(
    r"^(?:Kree|Skrulls?|Shi'ar|Inhumans|Chitauri|Brood|Builders|Frost Giants|Dwarves|Sovereign|"
    r"Atlanteans|mutants|humans|Kami|Olympians|Asgardians|Eternals|Deviants|Sentinels|"
    r"Quantumnauts|Wolf-Men|Elder Gods|Harpies|Asgardian|Mutant|Alien|Monster|Beast|"
    r"Demons?|Gods?|Gods|Elves|Dwarves|Orcs?)$", re.I)
PRONOUN = re.compile(
    r"^(?:he|she|it|they|him|her|them|his|hers|their|theirs|this|that|these|those|one|both|"
    r"the other|the other two|the two|the pair|everyone|someone|somebody|anyone|nobody)\b", re.I)
PLACE_LIKE = re.compile(r"\b(?:City|Town|Planet|Island|Mountain|Forest|Desert|River|Lake|Sea)\b")
RANK = re.compile(
    r"^(?:Dr\.|Doctor|Brigadier General|Brigadier|General|Agent|Officer|Senator|Prelate|Empress|"
    r"Emperor|Mayor|Detective|Sergeant|Colonel|Major|Lieutenant|Commander|Captain|Warlord|"
    r"Professor|Chancellor|Director|Lord|Lady|King|Queen|Sir|Dame|Madam|President)\s"
    r"(?!America\b|Marvel\b|Britain\b|Universe\b|Doom\b|Strange\b|Druid\b|Octopus\b|X\b|Xavier\b)")
COMPOSITE = re.compile(r"\s/|\(|\)|\[|\]")
# a quote must lie inside ONE sentence: the anti-loophole rule the council required, because
# big_flags.py:197 accepts `sent in q` with no quote-length cap and one paragraph quote would
# "cover" forty sentences. Sentence spans come from fact_coverage.segments().
SENT_END = re.compile(r"(?<=[.!?])[\"'”’)\]]*\s+(?=[\"'“‘(\[]*[A-Z0-9])")


def norm(t):
    return re.sub(r"\W+", " ", t or "").strip().lower()


def _quote_states(quote, relation):
    """Does the quote plainly state this relation? The OK line (a fast human confirm).

    A relation like `trained` appears in a quote as "training"/"trains", so this compares the
    relation's words as prefixes of the quote's words rather than for exact substrings.
    """
    words = norm(quote).split()
    for part in relation.split("_"):
        if len(part) < 4:
            continue
        stem = part[:max(4, len(part) - 3)]
        if any(w.startswith(stem) for w in words):
            return True
    return False


def sentences(text):
    """Segmenter used for the one-sentence rule and by fact_coverage.

    Deliberately NOT big_flags.sentences(), which drops every span under 20 chars (big_flags.py:88)
    and therefore cannot see the short declaratives that carry the person's own facts. This one has
    no length floor; only a 3-character floor to skip stray punctuation.
    """
    out = []
    for para in (text or "").split("\n"):
        para = para.strip()
        if not para:
            continue
        for s in SENT_END.split(para):
            s = s.strip()
            if len(s) >= 3:
                out.append(s)
    return out


def _end_ok(end, relation, is_object, tag, wiki=None):
    """B.6/B.7 end checks. Returns a reason string when the end is refused."""
    if end is None:
        if is_object and relation not in NON_PERSON_OBJECT:
            return "object is null; only relations in NON_PERSON_OBJECT may have no object"
        return None
    e = end.strip()
    if not e:
        return "empty end"
    if PRONOUN.match(e):
        return f"bare pronoun '{e}': resolve it to a named entity (B.7)"
    if COMPOSITE.search(e):
        return f"composite end '{e}': one entity, one name (A59)"
    if len(e) <= 2:
        return f"end '{e}' is too short to be a name"
    if RANK.match(e):
        return f"rank prefix in '{e}': strip it (step 6)"
    if SPECIES.match(re.sub(r"(?i)^(?:the|a|an)\s+", "", e)):
        return f"species/race end '{e}' (A25/R11)"
    if CROWD_WORDS.search(e):
        return f"crowd/indefinite end '{e}' (R11)"
    want = NON_PERSON_OBJECT.get(relation)
    # an article/possessive in front of a PLACE, ITEM, ROLE or NAME is legal (B.8: "his apartment",
    # "the Bus", "the Yellowjacket"); in front of a person end it is the R11 indefinite
    if is_object and want not in ("place", "item", "thing", "title", "name") and ARTICLE.match(e):
        return f"indefinite end '{e}' for a person relation: use the passage's name (R11)"
    if is_object and want is None and PLACE_LIKE.search(e) and wiki is not None:
        exact = [p for p in wiki.resolve(e) if p.lower() == e.lower()]
        lab = wiki.label.get(exact[0]) if exact else None
        if lab and vrw.PLACE_LIKE.search(lab):
            return f"'{e}' is a place but '{relation}' takes a person end"
    return None


def check(rows, window, wiki=None, tags=None):
    """Return (flags, ok) for one window's fact rows + tag rows.

    A flag is a PROMPT, never a verdict — exactly like big_flags.check, which the review reads and
    then decides by hand. `ok` lists rows whose quote states the relation plainly.
    """
    flags, ok = [], []
    quotes = []
    sents = sentences(window)
    for i, r in enumerate(rows or [], 1):
        if not isinstance(r, dict):
            flags.append(f"fact{i}: not an object")
            continue
        s, rel, o = r.get("subject"), r.get("relation"), r.get("object")
        q = r.get("quote") or ""
        mod, cert = r.get("modality", "actual"), r.get("certainty", "stated")
        tag = f"{s}|{rel}|{o}"
        if not s:
            flags.append(f"fact{i}: no subject")
        if rel == "other":
            flags.append(f"fact{i}: relation 'other' is not in the vocabulary; use 'other_verb' "
                         f"with the passage's verb as the object (B.3)")
        elif rel and rel != "other_verb" and rel not in RELATIONS:
            flags.append(f"fact{i}: '{rel}' not in the relation vocabulary (B.2)")
        if rel == "other_verb":
            if not o:
                flags.append(f"fact{i}: other_verb needs the passage's verb as the object (B.3)")
            elif q and norm(o) not in norm(q):
                flags.append(f"fact{i}: other_verb '{o}' does not appear literally in the quote (B.3)")
        if mod not in MODALITY:
            flags.append(f"fact{i}: modality '{mod}' not in {list(MODALITY)} (B.4)")
        if cert not in CERTAINTY:
            flags.append(f"fact{i}: certainty '{cert}' not in {list(CERTAINTY)} (B.5)")
        if mod != "actual" and mod in MODALITY and not (r.get("asserted_by") or "").strip():
            flags.append(f"fact{i}: modality '{mod}' with no asserted_by: who planned/claimed/ordered "
                         f"it? (B.4) a non-actual row is never world-truth")
        if r.get("asserted_by") and mod == "actual":
            flags.append(f"fact{i}: asserted_by set on an actual row (only for non-actual modality)")
        if "canon" in r and r.get("canon") not in CANON:
            flags.append(f"fact{i}: canon '{r.get('canon')}' not in {list(CANON)} (B.1)")
        # ---- quote checks (the anti-loophole rule) ----
        if len(q) < MIN_QUOTE:
            flags.append(f"{tag}: quote shorter than {MIN_QUOTE} chars")
        if len(q) > MAX_QUOTE:
            flags.append(f"{tag}: quote is {len(q)} chars; the store truncates at {MAX_QUOTE} "
                         f"and a paragraph quote games the coverage gate (B.1)")
        if q and q not in (window or ""):
            flags.append(f"{tag}: quote is not verbatim in the window")
        if q and sents and not any(q in s for s in sents):
            flags.append(f"{tag}: quote spans more than one sentence; quote the shortest clause "
                         f"that states the fact (B.1)")
        if q and sents and not any(norm(s) in norm(q) for s in sents) and q in (window or ""):
            flags.append(f"{tag}: quote crosses a sentence boundary (B.1)")
        quotes.append(q)
        # ---- ends ----
        why = _end_ok(s, rel, False, tag, wiki)
        if why:
            flags.append(f"{tag}: subject: {why}")
        why = _end_ok(o, rel, True, tag, wiki)
        if why:
            flags.append(f"{tag}: object: {why}")
        if s and o and norm(s) == norm(o):
            flags.append(f"{tag}: subject == object")
        # symmetry: one row per pair for a symmetric relation
        if rel in SYMMETRIC and s and o:
            flags.append(f"{tag}: '{rel}' is symmetric; write the pair once (hint, not an error)")
        # a fact row must not silently restate an event verb
        if rel in ("fought", "met", "killed", "defeated", "escaped", "captured", "saved",
                   "betrayed", "sealed", "arrived", "departed", "awakened"):
            flags.append(f"{tag}: '{rel}' is an EVENT verb; it belongs in `events`, not `facts` "
                         f"(use a fact relation for what the event cannot say)")
        if q and rel and rel != "other_verb" and _quote_states(q, rel):
            ok.append(tag)
    # ---- tag rows ----
    seen_tags = set()
    for i, t in enumerate(tags or [], 1):
        if not isinstance(t, dict):
            flags.append(f"tag{i}: not an object")
            continue
        tg, q = t.get("tag"), t.get("quote") or ""
        if tg not in TAGS:
            flags.append(f"tag{i}: tag '{tg}' not in the allowed set {list(TAGS)} (SECTION C)")
        if len(q) < 3:
            flags.append(f"tag{i}: tag row needs the exact text it excuses")
        elif q and q not in (window or ""):
            flags.append(f"tag{i}: tag quote is not verbatim in the window")
        elif q and sents and not any(q in s for s in sents) and "\n" not in q:
            flags.append(f"tag{i}: tag quote crosses a sentence boundary")
        seen_tags.add(tg)
        quotes.append(q)
    if tags and not seen_tags:
        flags.append("tags present but none named")
    return flags, ok


def validate(row):
    """Shape check for one fact row, no window needed. Returns a list of problems."""
    problems = []
    for k in ("quote", "subject", "relation", "modality", "certainty"):
        if k not in row:
            problems.append(f"missing field '{k}'")
    if row.get("relation") == "other":
        problems.append("relation 'other' is not in the vocabulary; use 'other_verb' (B.3)")
    elif row.get("relation") not in RELATIONS + ("other_verb",):
        problems.append(f"relation '{row.get('relation')}' not in the vocabulary (B.2)")
    if row.get("modality") not in MODALITY:
        problems.append(f"modality '{row.get('modality')}' not in the closed enum (B.4)")
    if row.get("certainty") not in CERTAINTY:
        problems.append(f"certainty '{row.get('certainty')}' not in the closed enum (B.5)")
    if row.get("modality") not in (None, "actual") and not (row.get("asserted_by") or "").strip():
        problems.append("non-actual modality with no asserted_by (B.4)")
    if "canon" in row and row["canon"] not in CANON:
        problems.append(f"canon '{row['canon']}' not in the allowed set (B.1)")
    return problems


def other_share(rows):
    """B.3 vocabulary-failure metric: share of fact rows using other_verb (target < 10%)."""
    rows = rows or []
    if not rows:
        return 0.0
    return sum(1 for r in rows if r.get("relation") == "other_verb") / len(rows)


def main():
    """`python fact_gate.py FILE.jsonl [FILE2 ...]` — flags every window of a v2 labels file."""
    if len(sys.argv) < 2:
        print(__doc__)
        return
    for path in sys.argv[1:]:
        n = nf = tot = other = tags_n = 0
        for line in open(path):
            r = json.loads(line)
            n += 1
            facts = r.get("facts") or []
            tot += len(facts)
            other += sum(1 for x in facts if x.get("relation") == "other_verb")
            tags_n += len(r.get("tags") or [])
            fl, _ = check(facts, "", tags=r.get("tags") or [])
            # without the window only the field-level checks are meaningful
            nf += len(fl)
        print(f"{Path(path).name}: windows={n} facts={tot} other_verb={other} "
              f"({other / tot * 100 if tot else 0:.1f}%) tags={tags_n} field_flags={nf}")


if __name__ == "__main__":
    main()
