"""Extracted events: placed, time-ranked facts the wiki states as events.

A relation says how two characters stand to each other. An event says what
happened, to whom, and where on the story's time axis -- the data a script's
beat order needs and the wiki's section order does not carry: the Shibuya
Incident page writes `10:01 P.M.` before `9:22 P.M.`, because the article is
organized by stage, not by the clock.

Phase 1 (the door test) is hand-written: one batch for the Shibuya Incident
proves the read path -- beats reordered onto the events' time axis under a
flag that is off by default -- before Phase 2 builds the model extraction.
Every row still passes the gates Phase 5 will make mechanical:

* the verb comes from a closed eventive set, not free text;
* both ends resolve to real nodes (the prose's name or alias, never a guess);
* the quote is verbatim in the section it came from;
* the arc the event is placed in is a page this wiki actually has;
* a multi-page event must agree on its placement, and a state the axis cannot
  place is stored with `temporal=0` rather than forced onto it.
"""

from __future__ import annotations

import re

from scriptengine.stores.facts import FactStore

# What a placed event may do. Closed on purpose: a verb outside the set is a
# description, not an event, and descriptions never order a timeline.
EVENTIVE_VERBS = frozenset(
    {
        "fought",
        "killed",
        "awakened",
        "sealed",
        "betrayed",
        "saved",
        "arrived",
        "departed",
    }
)

# Page types an event may be placed in: the arc pages that name the arc, and
# the event/battle pages that are one arc each. A placement in anything else
# is a finding, not a row.
PLACEMENT_TYPES = {"arc", "saga", "event", "battle", "story_arcs"}

PHASE1_ARC = "Shibuya Incident"

# (subject, object, verb, section_id, time_rank, quote, temporal)
#
# time_rank is the event's place on the incident's clock: the section's start
# time, with fractions for events inside one section. The order they produce
# is the wall-clock order of the incident -- 9:22 Shibuya Station and 9:27
# Fukutoshin land before 10:01 C Tower, which the article itself does not do.
# Section ids are the Shibuya Incident page's sections (facts.db):
#   6252  8:31-8:51 Fukutoshin     6258  10:01-10:04 C Tower
#   6253  8:51-9:15 Meiji-Jingumae 6259  9:27-10:02 between stations
#   6254  8:51-9:26 Fukutoshin     6260  9:22-9:40 Shibuya Station
#   6255  9:15-9:27 between        6261  9:40-10:10 outside the curtain
#   6256  9:22-10:01 Shibuya       6262  10:10-10:51 Shibuya Station
#                                6263  10:51-11:14 outside the station
#                                6265  11:14-11:36 Shibuya Station
#                                6266  11:36-end
PHASE1_ROWS: list[dict[str, object]] = [
    {
        "subject": "Satoru Gojo",
        "object": "Shibuya",
        "verb": "arrived",
        "section_id": 6252,
        "time_rank": 1.0,
        "quote": "At 8:31 PM, Satoru arrives in Shibuya and enters the curtain.",
        "temporal": True,
    },
    {
        "subject": "Satoru Gojo",
        "object": "Jogo",
        "verb": "fought",
        "section_id": 6252,
        "time_rank": 2.0,
        "quote": (
            "The strongest jujutsu sorcerer fights and overwhelms Jogo and"
            " Hanami with pure taijutsu, without the use of the Limitless."
        ),
        "temporal": True,
    },
    {
        "subject": "Satoru Gojo",
        "object": "Hanami",
        "verb": "killed",
        "section_id": 6252,
        "time_rank": 3.0,
        "quote": (
            "Satoru simply amplifies his technique to overpower Hanami and"
            " exorcises him completely."
        ),
        "temporal": True,
    },
    {
        "subject": "Yuji Itadori",
        "object": "Ko-Guy",
        "verb": "fought",
        "section_id": 6253,
        "time_rank": 4.0,
        "quote": (
            "He makes it his goal to break the cursed object projecting the"
            " barrier and fights Ko-Guy one-on-one."
        ),
        "temporal": True,
    },
    {
        "subject": "Mahito",
        "object": "Shibuya Station",
        "verb": "departed",
        "section_id": 6253,
        "time_rank": 5.0,
        "quote": (
            "Mahito gets ready to board a train going from Harajuku to"
            " Shibuya Station."
        ),
        "temporal": True,
    },
    {
        "subject": "Suguru Geto",
        "object": "Satoru Gojo",
        "verb": "sealed",
        "section_id": 6254,
        "time_rank": 6.0,
        "quote": (
            "Around 9:26 PM, Geto commands Prison Realm to close its gate,"
            " sealing Satoru inside the cubed form of the cursed object."
        ),
        "temporal": True,
    },
    {
        # The device's maker died on October 19th, weeks before the incident:
        # a real event the axis cannot place, stored with temporal=0 rather
        # than forced onto the incident's clock.
        "subject": "Mahito",
        "object": "Kokichi Muta",
        "verb": "killed",
        "section_id": 6255,
        "time_rank": 0.0,
        "quote": (
            "He explains this communication device is a contingency plan"
            " before he was killed by Mahito on October 19th."
        ),
        "temporal": False,
    },
    {
        "subject": "Mei Mei",
        "object": "Niji Ebina",
        "verb": "fought",
        "section_id": 6255,
        "time_rank": 7.0,
        "quote": (
            "the curse user, Niji Ebina, arrives shortly afterward and"
            " engages the Mei Mei Team."
        ),
        "temporal": True,
    },
    {
        "subject": "Kento Nanami",
        "object": "Shibuya",
        "verb": "arrived",
        "section_id": 6256,
        "time_rank": 8.0,
        "quote": (
            "At 9:22 PM, the Nanami, Zenin, and Kusakabe Teams all enter the"
            " battle at the same time."
        ),
        "temporal": True,
    },
    {
        "subject": "Haruta Shigemo",
        "object": "Kiyotaka Ijichi",
        "verb": "killed",
        "section_id": 6256,
        "time_rank": 8.5,
        "quote": (
            "Accompanied by Uraume, Haruta Shigemo cuts down Ijichi and"
            " continues on orders to hunt down all the managers."
        ),
        "temporal": True,
    },
    {
        "subject": "Yuji Itadori",
        "object": "Shibuya",
        "verb": "arrived",
        "section_id": 6256,
        "time_rank": 9.0,
        "quote": (
            "At 9:27 PM, Yuji reaches the curtain around Shibuya after"
            " leaving Harajuku on foot."
        ),
        "temporal": True,
    },
    {
        "subject": "Maki Zenin",
        "object": "Shibuya Station",
        "verb": "arrived",
        "section_id": 6260,
        "time_rank": 8.7,
        "quote": (
            "Sometime after 9:22 PM, the Zenin Team enters the curtain. They"
            " fight to suppress the aggressive transfigured human presence"
            " and rescue civilians in Shibuya Station."
        ),
        "temporal": True,
    },
    {
        "subject": "Mei Mei",
        "object": "Niji Ebina",
        "verb": "killed",
        "section_id": 6259,
        "time_rank": 9.5,
        "quote": (
            "Mei Mei doesn't see any value in his service potential and she"
            " cuts him down without a second thought."
        ),
        "temporal": True,
    },
    {
        "subject": "Kento Nanami",
        "object": "Haruta Shigemo",
        "verb": "killed",
        "section_id": 6261,
        "time_rank": 10.0,
        "quote": (
            "Nanami finishes the curse user off by smashing him clean through"
            " a subway wall."
        ),
        "temporal": True,
    },
    {
        "subject": "Toge Inumaki",
        "object": "Yuji Itadori",
        "verb": "saved",
        "section_id": 6261,
        "time_rank": 10.5,
        "quote": (
            "Toge Inumaki arrives and uses his cursed speech to immobilize"
            " all the transfigured humans. This allows Yuji to pass and enter"
            " Shibuya Station at 10:10 PM"
        ),
        "temporal": True,
    },
    {
        "subject": "Yuji Itadori",
        "object": "Jiro Awasaka",
        "verb": "fought",
        "section_id": 6258,
        "time_rank": 11.0,
        "quote": "Down below on the highway, Yuji and Megumi pummel Awasaka.",
        "temporal": True,
    },
    {
        "subject": "Toji Fushiguro",
        "object": "Ogami",
        "verb": "killed",
        "section_id": 6258,
        "time_rank": 11.5,
        "quote": (
            "He ironically follows her command to kill sorcerers and murders"
            " Ogami with a single strike."
        ),
        "temporal": True,
    },
    {
        "subject": "Mei Mei",
        "object": "Smallpox Deity",
        "verb": "killed",
        "section_id": 6262,
        "time_rank": 12.0,
        "quote": (
            "Mei Mei capitalizes and exorcises it using her signature move:"
            " Bird Strike!"
        ),
        "temporal": True,
    },
    {
        "subject": "Yuji Itadori",
        "object": "Choso",
        "verb": "fought",
        "section_id": 6262,
        "time_rank": 12.5,
        "quote": (
            "Yuji manages to get in close and land Divergent Fist on Choso's"
            " guard"
        ),
        "temporal": True,
    },
    {
        "subject": "Sukuna",
        "object": "Jogo",
        "verb": "awakened",
        "section_id": 6262,
        "time_rank": 13.0,
        "quote": (
            "Sukuna then awakens and demands Jogo get away from him"
            " immediately, severing the hand holding Yuji's face."
        ),
        "temporal": True,
    },
    {
        "subject": "Sukuna",
        "object": "Mimiko Hasaba",
        "verb": "killed",
        "section_id": 6262,
        "time_rank": 13.5,
        "quote": "he brutally murders Mimiko and then Nanako shortly after",
        "temporal": True,
    },
    {
        "subject": "Sukuna",
        "object": "Nanako Hasaba",
        "verb": "killed",
        "section_id": 6262,
        "time_rank": 14.0,
        "quote": (
            "he brutally murders Mimiko and then Nanako shortly after before"
            " she can retaliate and avenge her twin sister."
        ),
        "temporal": True,
    },
    {
        "subject": "Toji Fushiguro",
        "object": "Dagon",
        "verb": "killed",
        "section_id": 6262,
        "time_rank": 14.5,
        "quote": (
            "Noabito stops Dagon from getting away, allowing Toji to stab the"
            " cursed spirit through the face with Playful Cloud."
        ),
        "temporal": True,
    },
    {
        # Self-directed: the event is real and placed; the gate allows
        # subject == object and says so.
        "subject": "Toji Fushiguro",
        "object": "Toji Fushiguro",
        "verb": "killed",
        "section_id": 6263,
        "time_rank": 15.0,
        "quote": (
            "Toji stabs his own head with Playful Cloud to save his son, all"
            " unbeknownst to Megumi, who watches in shock."
        ),
        "temporal": True,
    },
    {
        "subject": "Haruta Shigemo",
        "object": "Megumi Fushiguro",
        "verb": "fought",
        "section_id": 6263,
        "time_rank": 15.5,
        "quote": (
            "Megumi is suddenly slashed in the back by Haruta Shigemo's"
            " bladed cursed tool."
        ),
        "temporal": True,
    },
    {
        "subject": "Sukuna",
        "object": "Jogo",
        "verb": "killed",
        "section_id": 6263,
        "time_rank": 16.0,
        "quote": "Sukuna is victorious, reducing Jogo to ash.",
        "temporal": True,
    },
    {
        "subject": "Yuji Itadori",
        "object": "Mahito",
        "verb": "fought",
        "section_id": 6265,
        "time_rank": 17.0,
        "quote": (
            "Yuji and Mahito come to blows once again, clashing throughout the"
            " station."
        ),
        "temporal": True,
    },
    {
        "subject": "Aoi Todo",
        "object": "Yuji Itadori",
        "verb": "saved",
        "section_id": 6265,
        "time_rank": 17.5,
        "quote": (
            "Mahito suddenly switches places with none other than Yuji's"
            ' "official best friend" Aoi Todo.'
        ),
        "temporal": True,
    },
    {
        "subject": "Mahito",
        "object": "Mahito",
        "verb": "awakened",
        "section_id": 6265,
        "time_rank": 18.0,
        "quote": (
            "Realizing the true essence of his soul, Mahito evolves into his"
            " final form using Idle Transfiguration: Instant Spirit Body of"
            " Distorted Killing."
        ),
        "temporal": True,
    },
    {
        "subject": "Yuji Itadori",
        "object": "Mahito",
        "verb": "killed",
        "section_id": 6265,
        "time_rank": 18.5,
        "quote": (
            "Todo's fake out gives Yuji the perfect opening to land full-power,"
            " fight-ending Black Flash that utterly defeats Mahito."
        ),
        "temporal": True,
    },
    {
        "subject": "Suguru Geto",
        "object": "Mahito",
        "verb": "killed",
        "section_id": 6266,
        "time_rank": 19.0,
        "quote": (
            "Shortly after he consumes Mahito, Pseudo-Geto is ambushed by the"
            " Kyoto sorcerers in one last attempt to retake Prison Realm."
        ),
        "temporal": True,
    },
    {
        "subject": "Yuki Tsukumo",
        "object": "Yuji Itadori",
        "verb": "saved",
        "section_id": 6266,
        "time_rank": 19.5,
        "quote": (
            "Before Uraume kills everyone, special grade jujutsu sorcerer"
            " Yuki Tsukumo suddenly arrives in time to rescue everyone."
        ),
        "temporal": True,
    },
    {
        "subject": "Choso",
        "object": "Yuji Itadori",
        "verb": "saved",
        "section_id": 6266,
        "time_rank": 20.0,
        "quote": (
            "using all his strength to protect Yuji, fighting alongside the"
            " sorcerers against Pseudo-Geto and Uraume."
        ),
        "temporal": True,
    },
]


def _fold(text: str) -> str:
    """Lowercase and fold diacritics the way the passage's words would."""
    import unicodedata

    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if not unicodedata.combining(c)).lower()


def _quoted_in(quote: str, passage: str) -> bool:
    """The passage really contains the clause, word for word.

    Whitespace is normalised and diacritics folded, because a reflowed line
    is still the clause. Nothing else is relaxed: this is the check that
    stops a quote the section never says being stored as its evidence.
    """
    if len(quote.strip()) < 12:
        return False
    tidy = lambda s: re.sub(r"\s+", " ", _fold(s)).strip()
    return tidy(quote) in tidy(passage)


def _name_in(name: str, aliases: tuple[str, ...], passage: str) -> bool:
    """Whether the section names this participant -- as its name or an alias."""
    folded = _fold(passage)
    return any(_fold(candidate) in folded for candidate in (name, *aliases))


def resolve_participant(
    store: FactStore, name: str
) -> tuple[int, str, tuple[str, ...]] | None:
    """The node a participant's name (or alias) resolves to, with its aliases.

    Returns `(node_id, canonical_name, aliases)` or None. A participant the
    wiki has no node for is a finding, not a row: storing a guessed id would
    join this event to somebody it did not involve.
    """
    row = store.node_by_name(name)
    if row is not None:
        aliases = tuple(
            a["alias"]
            for a in store.connection.execute(
                "SELECT alias FROM aliases WHERE node_id = ?", (int(row["id"]),)
            )
        )
        return int(row["id"]), str(row["name"]), aliases
    alias_row = store.connection.execute(
        "SELECT node_id FROM aliases WHERE alias = ? COLLATE NOCASE",
        (name.strip().lower(),),
    ).fetchone()
    if alias_row is None:
        return None
    node = store.connection.execute(
        "SELECT * FROM nodes WHERE id = ?", (alias_row["node_id"],)
    ).fetchone()
    if node is None:
        return None
    aliases = tuple(
        a["alias"]
        for a in store.connection.execute(
            "SELECT alias FROM aliases WHERE node_id = ?", (int(node["id"]),)
        )
    )
    return int(node["id"]), str(node["name"]), aliases


def validate_phase1_rows(store: FactStore) -> list[str]:
    """Run every gate over the Phase-1 batch. Returns one finding per failure.

    An empty list is the pass: every verb in the closed set, both ends real
    nodes, the quote verbatim in its section, and the placement a page this
    wiki actually has.
    """
    findings: list[str] = []
    arc_row = store.node_by_name(PHASE1_ARC)
    if arc_row is None or arc_row["label"] not in PLACEMENT_TYPES:
        findings.append(
            f"arc {PHASE1_ARC!r} is not a page of a placement type"
            f" ({arc_row['label'] if arc_row else 'unresolved'})"
        )
    sections = {
        section["id"]: section["text"]
        for section in store.document_sections(PHASE1_ARC)
    }
    for index, raw in enumerate(PHASE1_ROWS):
        label = f"row {index} ({raw['subject']} {raw['verb']} {raw['object']})"
        verb = str(raw["verb"]).strip().lower()
        if verb not in EVENTIVE_VERBS:
            findings.append(f"{label}: verb {verb!r} is not in the closed set")
        section_id = int(raw["section_id"])
        passage = sections.get(section_id)
        if passage is None:
            findings.append(f"{label}: section {section_id} not on the arc page")
            continue
        for end in ("subject", "object"):
            resolved = resolve_participant(store, str(raw[end]))
            if resolved is None:
                findings.append(
                    f"{label}: {end} {str(raw[end])!r} resolves to no node"
                )
            elif not _name_in(str(raw[end]), resolved[2], passage):
                findings.append(
                    f"{label}: {end} {str(raw[end])!r} is not named in"
                    f" section {section_id}"
                )
        if not _quoted_in(str(raw["quote"]), passage):
            findings.append(f"{label}: quote is not verbatim in section {section_id}")
    return findings


def seed_phase1_rows(
    store: FactStore,
    model: str = "hand-written",
    prompt_version: str = "phase1-door-test",
) -> tuple[int, list[str]]:
    """Gate the Phase-1 batch and store it under the arc's key.

    Returns `(stored_rows, findings)`. A non-empty findings list stores
    nothing: a half-validated batch in the table would reorder beats on
    evidence that failed its own checks.
    """
    findings = validate_phase1_rows(store)
    if findings:
        return 0, findings
    revid_row = store.connection.execute(
        "SELECT revid FROM documents WHERE title = ? COLLATE NOCASE", (PHASE1_ARC,)
    ).fetchone()
    revid = int(revid_row["revid"]) if revid_row and revid_row["revid"] is not None else None
    store.ensure_events()
    rows = []
    for raw in PHASE1_ROWS:
        subject = resolve_participant(store, str(raw["subject"]))
        object_ = resolve_participant(store, str(raw["object"]))
        rows.append(
            {
                "subject_node": subject[0],
                "subject_name": subject[1],
                "object_node": object_[0],
                "object_name": object_[1],
                "verb": raw["verb"],
                "section_id": raw["section_id"],
                "quote": raw["quote"],
                "temporal": raw.get("temporal", True),
                "time_rank": raw["time_rank"],
            }
        )
    stored = store.save_events(PHASE1_ARC, rows, revid, prompt_version, model)
    return stored, []