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
        "attire", "capability", "deictic", "below_floor",
        # the council (2026-10-08): a sentence the event layer legitimately refuses must
        # still be COVERABLE in v2, or the coverage rule is unsatisfiable for it.
        "no_doer",      # A8/R17 passive with no 'by', A39 item-as-doer, A47 tied with no captor
        "crowd_end",    # A5/A25/A52/A57: crowd, species, indefinite or descriptive-group ends
        "no_relation")  # A17/A27/A30/A42/A45: stated, but no legal event and no legal fact

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
    # "X of the Y" is a crowd only after a quantity word ("members of the Hand"); a named team or title
    # that contains "of the" ("Guardians of the Galaxy", "Masters of Evil") is a name (fixed 2026-10-10)
    r"|^(?:members?|some|many|most|all|one|two|three|several|rest|remnants?)\s+of the\b|\bs'\s", re.I)
ARTICLE = re.compile(r"^(?:a|an|the|his|her|their|its)\s", re.I)
SPECIES = re.compile(
    r"^(?:Kree|Skrulls?|Shi'ar|Inhumans|Chitauri|Brood|Builders|Frost Giants|Dwarves|Sovereign|"
    r"Atlanteans|mutants|humans|Kami|Olympians|Asgardians|Eternals|Deviants|Sentinels|"
    r"Quantumnauts|Wolf-Men|Elder Gods|Harpies|Asgardian|Mutant|Alien|Monster|"
    r"Demons?|Gods?|Gods|Elves|Dwarves|Orcs?)$", re.I)
PRONOUN = re.compile(
    r"^(?:he|she|it|they|him|her|them|his|hers|their|theirs|this|that|these|those|one|both|"
    r"the other|the other two|the two|the pair|everyone|someone|somebody|anyone|nobody)(?![\w'-])", re.I)
# (?![\w'-]) not \b: "She-Hulk" / "It-the-Living-Colossus" are names, not pronouns (b1029)
PLACE_LIKE = re.compile(r"\b(?:City|Town|Planet|Island|Mountain|Forest|Desert|River|Lake|Sea)\b")
RANK = re.compile(
    r"^(?:Dr\.|Doctor|Brigadier General|Brigadier|General|Agent|Officer|Senator|Prelate|Empress|"
    r"Emperor|Mayor|Detective|Sergeant|Colonel|Major|Lieutenant|Commander|Captain|Warlord|"
    r"Professor|Chancellor|Director|Lord|Lady|King|Queen|Sir|Dame|Madam|President)\s"
    r"(?!of\b|in\b|Chaos\b|Carter\b|Lotus\b|Dark Wind\b|Loki\b|Goblin\b|Anti-Venom\b|Commander\b|Sun\b|Bad Vibes\b|"
    r"Dazzler\b|Cutlass\b|Nemesis\b|Spectrum\b|Stilt-Man\b|Hawkman\b|Avalon\b|Americat\b|Minerva\b|Valkyrie\b|"
    r"Thor\b|Raptor\b|Ogun\b|Voodoo\b|Deathstrike\b|Mastermind\b|America\b|Marvel\b|Britain\b|Universe\b|Doom\b|Strange\b|Druid\b|Octopus\b|X\b|Xavier\b|Cobra\b|U\.K\.|Venom\b|Arthur\b|Hydra\b|Torch\b|\d)")
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


def _resolves(wiki, end):
    """Does the wiki know this end as a real page/alias? (A52's "a Space Phantom" does not.)"""
    try:
        return bool(wiki.resolve(end))
    except Exception:  # noqa: BLE001 - a wiki hiccup must not fail a labelling run
        return False


def _end_ok(end, relation, is_object, tag, wiki=None, window=None):
    """B.6/B.7 end checks. Returns a reason string when the end is refused."""
    if end is None:
        if is_object and relation not in NON_PERSON_OBJECT:
            return "object is null; only relations in NON_PERSON_OBJECT may have no object"
        return None
    e = end.strip()
    if not e:
        return "empty end"
    if is_object and relation == "other_verb":
        return None  # the object is the passage's verb ("go", b5306); B.3 checks it, not the name rules
    # a capitalised end the window itself uses as a name mid-sentence ("the being known as Him",
    # "the Former Thrall", "Po", "MJ") is a name, whatever crowd/pronoun/length rule it trips (2026-10-12)
    named_here = bool(window) and e[:1].isupper() and bool(
        re.search(r"(?:[a-z,;:]|\b(?:named|called|as))\s+(?:\"|')?" + re.escape(e) + r"(?![\w-])", window))
    if PRONOUN.match(e) and not named_here and not (len(e.split()) > 1 and all(w[:1].isupper() for w in e.split())):
        # a multi-word capitalised name that starts like a pronoun is a name ("He Who Remains", b1286)
        return f"bare pronoun '{e}': resolve it to a named entity (B.7)"
    if COMPOSITE.search(e):
        return f"composite end '{e}': one entity, one name (A59)"
    # a short name the window itself introduces ("a young girl named Po", b5450) is a name
    if len(e) <= 2 and not (e[:1].isupper() and window and re.search(r"(?<![\w-])" + re.escape(e) + r"(?![\w-])", window)):
        return f"end '{e}' is too short to be a name"
    if RANK.match(e):
        return f"rank prefix in '{e}': strip it (step 6)"
    if SPECIES.match(re.sub(r"(?i)^(?:the|a|an)\s+", "", e)):
        return f"species/race end '{e}' (A25/R11)"
    m = CROWD_WORDS.search(e)
    # a capitalised crowd word inside a capitalised name is part of the name ("Young Allies",
    # "Avengers Academy Students"); "Hydra agents" / "the guards" stay crowds (fixed 2026-10-10)
    if m and not named_here and not (e[:1].isupper() and m.group(0)[:1].isupper() and m.group(0).lower() not in
                  ("former", "active", "several", "some", "many", "various", "others")):
        return f"crowd/indefinite end '{e}' (R11)"
    want = NON_PERSON_OBJECT.get(relation)
    # an article/possessive in front of a PLACE, ITEM, ROLE or NAME is legal (B.8: "his apartment",
    # "the Bus", "the Yellowjacket"); in front of a person end it is the R11 indefinite
    if is_object and want not in ("place", "item", "thing", "title", "name") and ARTICLE.match(e):
        # a NAMED group or organisation is legal with its article ("the X-Men", "the FBI",
        # "the Avengers"): v2 B.6, and the A3/A48/A65 joined/member_of routes depend on it.
        # The wiki decides: "a Space Phantom" / "an assailant" are indefinite (A52/R11) and
        # must still be refused, and neither resolves.
        tail = re.sub(r"(?i)^(?:a|an|the|his|her|their|its)\s+", "", e)
        named = bool(tail) and tail[:1].isupper()
        # "the X-Men" / "the Avengers" are one named thing; "a Space Phantom" is a description
        # that merely looks capitalised, so a multi-word end must be confirmed by the wiki.
        ok = named and (len(tail.split()) == 1 or named_here or (wiki is not None and _resolves(wiki, e)))
        if not ok:
            return f"indefinite end '{e}' for a person relation: use the passage's name (R11)"
    if is_object and want is None and PLACE_LIKE.search(e) and wiki is not None:
        exact = [p for p in wiki.resolve(e) if p.lower() == e.lower()]
        lab = wiki.label.get(exact[0]) if exact else None
        if lab and PLACE_LIKE.search(lab):
            return f"'{e}' is a place but '{relation}' takes a person end"
    return None


_STARTERS = {"The", "A", "An", "When", "After", "While", "As", "However", "Then", "But", "And", "Once",
             "Before", "During", "Following", "This", "That", "These", "Those", "It", "They", "He", "She",
             "His", "Her", "Their", "Its", "In", "On", "At", "With", "Without", "Despite", "Although",
             "Meanwhile", "Later", "Eventually", "Soon", "Suddenly", "Unbeknownst", "Due", "Since", "If",
             "Few", "Just", "Now", "Once", "Some", "Many", "Most", "All", "Every", "Each", "No", "Not"}


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
        if q and SENT_END.search(q):
            flags.append(f"{tag}: quote crosses a sentence boundary (B.1)")
        quotes.append(q)
        # ---- ends ----
        why = _end_ok(s, rel, False, tag, wiki, window)
        if why:
            flags.append(f"{tag}: subject: {why}")
        why = _end_ok(o, rel, True, tag, wiki, window)
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
        # review classes A97/A99 (plan/BIG_REVIEW_PATTERNS.md, b501-b700): repair hints only,
        # the keep-gate (validate/_end_ok) never drops a row for them
        if rel == "gave" and isinstance(o, str) and o and (
                o[:1].islower() or re.search(r"\b(?:a|an|the|his|her|their|its)\s+" + re.escape(o.split()[0]), q)) \
                and not re.search(r"\b(?:gave|give|gives|giving|provided|handed|offered|lent|sent)\s+(?:the\s+)?"
                                  + re.escape(o) + r"\s+\w", q) \
                and not re.search(r"\bto\s+(?:the\s+)?" + re.escape(o) + r"\b", q):
            # the object IS the recipient in "gave the Surfer his freedom" / "delivered the Tablet to Fisk"
            flags.append(f"{tag}: `gave` takes the RECIPIENT as object ('Koenig gave Ward', not the item) (A97)")
        if rel in ("alias_of", "real_name_of") and isinstance(o, str) and o and re.search(
                r"(?:alias(?: of)?|calling (?:him|her|them)sel(?:f|ves)|under the name|known as|a\.k\.a\.?|"
                r"assumed the (?:name|alias) of)\s+(?:the\s+)?\W?" + re.escape(o), q):
            flags.append(f"{tag}: the quote names '{o}' as the alias; `alias_of` subject = the alias, "
                         f"object = the real person (A99)")
        # review classes A125-A133 (b4747-b5466, three parallel reviewers): repair hints only
        if rel == "other_verb" and isinstance(o, str) and o and (
                o.lower() in ("was", "were", "is", "are", "be", "been", "being", "should", "would", "could",
                              "had", "has", "have", "did", "does", "do", "will", "can", "might", "must")
                or (o[:1].isupper() and not re.search(r"(?:ing|ed|s)$", o))):  # "Believing" is a verb
            flags.append(f"{tag}: other_verb object '{o}' is a copula/modal or a name, not the act: use the "
                         f"quote's real verb, or a no_relation tag if nothing is done (A125)")
        # A134 (b5747-b5846 reviewer; measured 2026-10-12: 80 of 92 approved attempt-word objects had a
        # "tried to <verb>" in the quote): the attempt word is the modality, the object is the verb tried
        if rel == "other_verb" and isinstance(o, str) and o.lower() in (
                "attempted", "tried", "attempt", "attempts", "trying", "tries"):
            m_try = re.search(r"\b(?:tried|attempted|attempts?|trying|tries)\s+(?:\w+ly\s+)?to\s+(\w+)", q, re.I)
            if m_try:
                flags.append(f"{tag}: other_verb object '{o}' is the attempt, not the act: object "
                             f"'{m_try.group(1)}' with modality attempted (A134)")
        # (A126 flag withdrawn 2026-10-12: forms are descriptions by nature, "being of solid sound")
        # (A128 "done speech act as claimed" was measured on 5,526 approved windows and dropped:
        #  "X insisted that ..." as claimed + asserted_by is the procedure's claim row, B.4)
        if rel in ("learned", "discovered", "suspected", "remembered", "revealed") and isinstance(o, str) and o \
                and ("_" in o or len(o.split()) >= 4):
            flags.append(f"{tag}: '{rel}' with a clause object: `learned|-` / `revealed|-`, or other_verb with "
                         f"the quote's verb (A133/A115)")
        if isinstance(s, str) and re.search(r"^(?:[Tt]he |[Aa] |[Aa]n )?(?:\w+'s )?(?:spell|curse|hologram|computer|"
                                            r"elevator|war|explosion|fire|blast|storm|device|machine|virus|"
                                            r"serum|ship|program|system|book|weapon|city|country|planet)$", s):
            flags.append(f"{tag}: subject '{s}' is no agent: name its user/caster as subject, or tag no_doer "
                         f"(A131/A110)")
        if q and rel and rel != "other_verb" and _quote_states(q, rel):
            ok.append(tag)
    # A99: one kinship, two rows (child_of + the inverse parent_of)
    kin = {(r.get("subject"), r.get("relation"), r.get("object")) for r in rows or [] if isinstance(r, dict)}
    for a, rel, b in kin:
        if rel == "child_of" and (b, "parent_of", a) in kin:
            flags.append(f"{a}|child_of|{b}: the same kinship is also written as {b}|parent_of|{a}; keep one row (A99)")
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
        # A101 (b807+ review): a narration line whose subject is a named person ("Masaryk watches the
        # news", "Johnny believed ...") tagged no_relation/deictic/no_doer instead of written as a fact
        # a leading participle phrase ("Having his memories erased, Nightcrawler returned") is no doer:
        # match the doer after its comma (measured 2026-10-12: 15/281 hits, the doer was misreported)
        q_d = q
        lead = re.match(r"([A-Z]\w+ing)\b[^,]*, ", q)
        if lead and lead.group(1).lower() not in ("king", "sting", "viking"):
            q_d = q[lead.end():]
        m = re.match(r"(?:[A-Z][\w'.-]+ ){0,2}?([A-Z][\w'.-]+) (?:\w+(?:ed|es|s)|was|had|began)\b", q_d)
        if tg in ("no_relation", "deictic", "no_doer") and m and m.group(0).split()[0] not in _STARTERS:
            flags.append(f"tag{i}: '{q[:40]}' names its doer ({m.group(1)}): write it as a fact row with the "
                         f"passage's verb, not a {tg} tag (A101)")
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



# Fact rows the 35B wrote with a fixable shape were DROPPED by validate() (2026-10-12 audit of all
# 14,000 windows: 201 'died' deaths, ~690 plans with no asserted_by, 134 certainty words in the
# modality slot, 226 rank-prefixed ends). normalise() repairs the shape; the gate still judges content.
EVENT_VERBS = {"saved", "captured", "killed", "defeated", "escaped", "betrayed", "sealed", "met", "arrived",
               "departed", "awakened", "fought", "rescued"}
REL_FIX = {"died": "dies", "rescued": None, "uses": "used", "planned": None, "claimed": None}


def strip_rank(end):
    if isinstance(end, str) and RANK.match(end.strip()):
        rest = RANK.sub("", end.strip(), count=1).strip()
        if rest and not re.match(r"(?i)of\b", rest):
            return rest
    return end


def normalise(row):
    """Return a repaired copy of one fact row (shape only)."""
    r = dict(row)
    rel = r.get("relation")
    if rel in REL_FIX and REL_FIX[rel]:
        r["relation"] = REL_FIX[rel]
    mod, cert = r.get("modality"), r.get("certainty")
    if mod in CERTAINTY and mod not in MODALITY:
        r["certainty"], r["modality"] = mod, "actual"
    if r.get("modality") in (None, "", "None"):
        r["modality"] = "actual"
    if r.get("certainty") in (None, "", "None") or r.get("certainty") not in CERTAINTY:
        r["certainty"] = "stated"
    if r.get("modality") != "actual" and not (r.get("asserted_by") or "").strip():
        r["asserted_by"] = r.get("subject")
    for k in ("subject", "object", "asserted_by"):
        if r.get(k):
            r[k] = strip_rank(r[k])
    return r


def split_event_facts(facts):
    """Facts written with an event verb belong in the event layer: (facts, events)."""
    keep, moved = [], []
    for f in facts or []:
        rel = f.get("relation") if isinstance(f, dict) else None
        if rel in EVENT_VERBS:
            v = "saved" if rel == "rescued" else rel
            moved.append({"quote": f.get("quote"), "subject": f.get("subject"), "verb": v,
                          "object": None if v == "awakened" else f.get("object")})
        else:
            keep.append(f)
    return keep, moved

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
