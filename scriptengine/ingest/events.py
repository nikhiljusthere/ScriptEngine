"""Extracted events: placed, time-ranked facts the wiki states as events.

A relation says how two characters stand to each other. An event says what
happened, to whom, and where on the story's time axis -- the data a script's
beat order needs and the wiki's section order does not carry: the Shibuya
Incident page writes `10:01 P.M.` before `9:22 P.M.`, because the article is
organized by stage, not by the clock.

Phase 1 (the door test) is hand-written: one batch for the Shibuya Incident
proves the read path -- beats reordered onto the events' time axis under a
flag that is off by default -- before Phase 2 builds the model extraction.

Phase 2 is the model extraction this module exists for: the arc, event and
battle pages are asked for the events they state, and every row still passes
the gates Phase 5 will make mechanical:

* the verb comes from a closed eventive set, not free text;
* both ends resolve to real nodes (the prose's name or alias, never a guess);
* the quote is verbatim in the section it came from;
* the arc the event is placed in is a page this wiki actually has;
* a multi-page event must agree on its placement, and a state the axis cannot
  place is stored with `temporal=0` rather than forced onto it.
"""

from __future__ import annotations

import json
import logging
import re
import sqlite3
from typing import Any

from scriptengine.config import SeriesPaths, Settings, get_settings
from scriptengine.ingest.abilities import _windows
from scriptengine.llm.client import LLMClient, LLMRateLimited, LLMUnavailable
from scriptengine.stores.facts import FactStore

logger = logging.getLogger(__name__)

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

# Section titles that are extraction-only furniture, on top of the narrative
# retriever's list set: they state times or links rather than events, and a
# row placed in one of them sits where the section sits, not where the
# event did.
_EXTRACTION_ONLY_EXCLUDED = {"timetable", "interactive map"}

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


# ── Phase 2: model extraction ─────────────────────────────────────────────────
#
# The same table, filled by a model over every page that states what happened:
# the arc, event and battle pages. It mirrors `ingest/relations.py`
# deliberately -- asked only where the prose is the only source, gated after
# the model answers, cached on (revid, prompt) -- with one difference the two
# tables force: a relation carries no time, but an event is a claim about the
# story's clock, so its `time_rank` is never the model's. The model says what
# happened; where on the axis it sits is looked up from the section it came
# from, and a number the model supplies is a number nobody verified.

# Bump to invalidate every stored event, exactly as `relations` does.
PROMPT_VERSION = "events-2026-09-05.2"

SYSTEM = (
    "You extract stated events from fiction-wiki prose. You answer with JSON "
    "only: no prose, no code fences. You never state an event the passage does "
    "not state, however well you know the series."
)

_TEMPLATE = """List the events this passage states: things that happen to somebody, or that somebody does, during {page}.

Series: {series}
Page: {page}
Section: {section}

Passage:
{passage}

Answer with JSON exactly in this shape:
{{"events": [{{"subject": "...", "verb": "...", "object": "...", "quote": "..."}}]}}

`verb` must be exactly one of these words, as written here, never a synonym
or a different tense of one: {verbs}.

Rules:
- An event is something the passage says happens: a fight, a killing, an
  awakening, a sealing, a betrayal, a rescue, an arrival, a departure. A
  description of who a character is, a list of who is present, or a rule the
  story follows is not an event.
- The subject does the verb, the object is the one it is done to, and both
  must be names the passage uses, given as the passage writes them. One name
  per role: if the passage says "Gojo and Nanami fight Mahito", that is two
  events, one for each subject. If the passage names no object -- "Mahito
  awakens" -- the subject is the object.
- `quote` must be copied from the passage word for word: the clause that
  states the event. Do not paraphrase it, shorten it or tidy it.
- If the passage states no event, answer {{"events": []}}. An empty answer is
  correct and useful.
- Only events the passage actually states. Two characters being in the same
  sentence is not a fight, and a character being present at a place is not an
  arrival there."""


def parse_events_response(text: str) -> list[dict[str, str]]:
    """The model's JSON, or nothing. Never raises on a bad answer."""
    body = (text or "").strip()
    if body.startswith("```"):
        body = re.sub(r"^```[a-z]*\n?|\n?```$", "", body).strip()
    start, end = body.find("{"), body.rfind("}")
    if start < 0 or end <= start:
        return []
    try:
        data = json.loads(body[start : end + 1])
    except ValueError:
        return []
    rows = data.get("events") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


# Page types an event cannot name. A battle, arc or chapter is the *container*
# of events, not a participant in one, and that is exactly where a model falls
# back when it cannot find a character's name: it names the page it read.
# `Jujutsu Sorcerers vs. Dagon fought Dagon` is a claim the wiki does not make,
# so those page types -- the placement set itself, plus the narrative divisions
# -- are kept out of the participant set rather than trusted to the gate.
NON_PARTICIPANT_TYPES = PLACEMENT_TYPES | {"chapter", "episode"}


def known_participants(store: FactStore) -> dict[str, tuple[str, int]]:
    """Every name this wiki has a resolved node for, folded, to (name, id).

    Events name places and things as well as people -- `arrived in Shibuya`,
    `killed with Playful Cloud` -- so the set is all resolved nodes and their
    aliases, not characters alone as `relations.known_names` keeps it. Only
    resolved nodes: the unresolved ones are link targets the wiki never gave a
    page, and placing an event on a guess is the failure the guard exists to
    stop. A page title always wins over an alias pointing elsewhere. And a node
    whose page is a container of events is left out: the set names
    participants, not the pages that hold them.

    Read once on the thread that owns the connection and handed to the workers
    as a plain dict, for the reason `relations.known_names` gives: a
    connection belongs to one thread.
    """
    placeholders = ",".join("?" * len(NON_PARTICIPANT_TYPES))
    # The ids of resolved nodes whose page is a container, to be skipped.
    container_ids = {
        int(row["id"])
        for row in store.connection.execute(
            f"SELECT n.id FROM nodes n"
            f" JOIN documents d ON d.id = n.document_id"
            f" WHERE n.is_resolved = 1 AND d.page_type IN ({placeholders})",
            tuple(sorted(NON_PARTICIPANT_TYPES)),
        )
    }
    canon: dict[str, tuple[str, int]] = {}
    for row in store.connection.execute(
        "SELECT id, name FROM nodes WHERE is_resolved = 1"
    ):
        name = (row["name"] or "").strip()
        if name and int(row["id"]) not in container_ids:
            canon[name.lower()] = (name, int(row["id"]))
    for row in store.connection.execute(
        "SELECT a.alias, n.id, n.name FROM aliases a"
        " JOIN nodes n ON n.id = a.node_id WHERE n.is_resolved = 1"
    ):
        if int(row["id"]) in container_ids:
            continue
        alias = (row["alias"] or "").strip().lower()
        target = (row["name"] or "").strip()
        # A page title always wins over an alias pointing elsewhere.
        if alias and target and alias not in canon:
            canon[alias] = (target, int(row["id"]))
    return canon


def _excluded_section_titles() -> set[str]:
    """The section titles that state no events: list furniture, and the
    extraction-only furniture on top of it."""
    from scriptengine.retrieve.narrative import _LIST_SECTION_TITLES

    return (
        set(_LIST_SECTION_TITLES) - {"summary", "synopsis", "plot"}
        | _EXTRACTION_ONLY_EXCLUDED
    )


def extractable_sections(store: FactStore, page: str) -> list[sqlite3.Row]:
    """The page's sections that state events: prose, not list furniture.

    The list set is the narrative retriever's, minus its scoring exclusions:
    `summary` and `synopsis` are on that list because a section every arc page
    carries would make every query look relevant to every arc. For extraction
    they are the opposite -- the one place an event is stated in full -- so
    they stay extractable. `timetable` goes the other way: it repeats the
    stages' clock entries as reference furniture, and a row placed in it reads
    as the page's end no matter what time it states, while the stage sections
    that state the same things in context come first in article order.
    """
    excluded = _excluded_section_titles()
    sections = []
    for section in store.document_sections(page):
        title = (section["title"] or "").strip()
        text = (section["text"] or "").strip()
        if title.lower() in excluded or not text or (section["word_count"] or 0) < 20:
            continue
        sections.append(section)
    return sections


def placement_pages(store: FactStore) -> list[str]:
    """The pages an event may be placed in, ordered by how much prose there is.

    The arc, event and battle pages are where a wiki states what happened, and
    the order is by prose weight, as `relations.needs_relations`, so `--limit`
    means the pages that matter rather than the first alphabetically.
    """
    excluded = _excluded_section_titles()
    placeholders = ",".join("?" * len(PLACEMENT_TYPES))
    rows = store.connection.execute(
        f"SELECT d.title FROM documents d"
        f" WHERE d.page_type IN ({placeholders})",
        tuple(sorted(PLACEMENT_TYPES)),
    ).fetchall()
    weight: dict[str, int] = {}
    for row in rows:
        page = row["title"]
        total = 0
        for section in store.document_sections(page):
            title = (section["title"] or "").strip()
            if title.lower() in excluded:
                continue
            if (section["text"] or "").strip() and (section["word_count"] or 0) >= 20:
                total += int(section["word_count"] or 0)
        if total:
            weight[page] = total
    return sorted(weight, key=weight.get, reverse=True)  # type: ignore[arg-type]


# Section titles that narrate what happened, in story order. The complement of
# the list/reference/attribute furniture: a character's own history lives in
# its Synopsis/History and its per-arc sections, a chapter's in its
# Plot Details. A section under any other heading states traits or links, not
# events, and an event placed in one sits where the section sits, not where the
# event did.
NARRATIVE_SECTION_TITLES = {
    "synopsis", "summary", "plot", "plot details", "history",
    "overview", "story", "development", "background",
}


def is_narrative_heading(title: str) -> bool:
    """A heading that narrates: a narrative-family title, or a section the wiki
    named after the arc it walks (the character's `Culling Game Arc` section)."""
    lowered = (title or "").strip().lower()
    return lowered in NARRATIVE_SECTION_TITLES or lowered.endswith(" arc")


def corpus_scope(store: FactStore) -> dict[str, list[sqlite3.Row]]:
    """The sections an interaction may state, keyed by page.

    The placement set (arc/event/battle pages) is where a wiki states events in
    the round. Most of what a wiki says about a character sits OFF that
    character's page -- in the character's own Synopsis/History and in the
    chapter's Plot Details -- so the corpus pass reaches those. A section is in
    scope only when its heading narrates (see `is_narrative_heading`) AND the
    section's chunks name at least two of the wiki's own character nodes: one
    character is description, two is an interaction, the event candidate.

    Character-family page types are read off the wiki's own type names (any type
    whose name carries `character`), so nothing about which types count is a
    series name in this file.
    """
    char_types = sorted(
        str(row["page_type"])
        for row in store.connection.execute(
            "SELECT DISTINCT page_type FROM documents"
        )
        if row["page_type"] and "character" in str(row["page_type"]).lower()
    )
    if not char_types:
        return {}
    placeholders = ",".join("?" * len(char_types))
    counts = {
        int(row["sid"]): int(row["cn"])
        for row in store.connection.execute(
            "SELECT ch.section_id AS sid, COUNT(DISTINCT cn.node_id) AS cn"
            " FROM chunk_nodes cn"
            " JOIN chunks ch ON ch.id = cn.chunk_id"
            " JOIN nodes n ON n.id = cn.node_id AND n.is_resolved = 1"
            " JOIN documents d ON d.id = n.document_id"
            f" WHERE d.page_type IN ({placeholders})"
            " AND ch.section_id IS NOT NULL"
            " GROUP BY ch.section_id",
            char_types,
        )
    }
    multi = {sid for sid, cn in counts.items() if cn >= 2}
    if not multi:
        return {}
    by_doc: dict[int, list[sqlite3.Row]] = {}
    for row in store.connection.execute(
        "SELECT s.* FROM sections s"
        f" WHERE s.id IN ({','.join('?' * len(multi))})"
        " ORDER BY s.document_id, s.ordinal",
        tuple(multi),
    ):
        if is_narrative_heading(row["title"]):
            by_doc.setdefault(int(row["document_id"]), []).append(row)
    if not by_doc:
        return {}
    titles = {
        int(row["id"]): row["title"]
        for row in store.connection.execute("SELECT id, title FROM documents")
    }

    def weight(rows: list[sqlite3.Row]) -> int:
        return sum(int(row["word_count"] or 0) for row in rows)

    return {
        titles[doc_id]: by_doc[doc_id]
        for doc_id in sorted(by_doc, key=lambda d: weight(by_doc[d]), reverse=True)
    }


def scope_plan(
    store: FactStore, scope: str
) -> tuple[list[str], dict[str, list[sqlite3.Row]]]:
    """`(pages, sections_by_page)` for the extraction scope.

    `placement` reads the arc/event/battle set, every extractable section of
    it; `corpus` reads the corpus rule only (the narrative sections that name
    two or more of the wiki's characters); `all` reads the union, and a page
    both rules cover reads the union of its sections, deduped.

    The union exists because the rules can be disjoint: on JJK no placement
    section satisfies the corpus rule, so a corpus-only re-extract would
    silently stop reading the 388 sections (165,941 words) that hold all 714
    placed events -- the scope-shrink check in reports/comprehension/GATE.md.
    """
    placement = placement_pages(store)
    corpus = corpus_scope(store) if scope in ("corpus", "all") else {}
    if scope == "placement":
        pages = list(placement)
    elif scope == "corpus":
        pages = list(corpus)
    else:
        seen = set(placement)
        pages = list(placement) + [p for p in corpus if p not in seen]

    base_pages = set(placement) if scope in ("placement", "all") else set()
    by_page: dict[str, list[sqlite3.Row]] = {}
    for page in pages:
        base = extractable_sections(store, page) if page in base_pages else []
        extra = list(corpus.get(page, [])) if scope in ("corpus", "all") else []
        if not base:
            by_page[page] = extra
        elif not extra:
            by_page[page] = base
        else:
            seen = {s["id"] for s in base}
            by_page[page] = base + [s for s in extra if s["id"] not in seen]
    return pages, by_page


def _time_to_hours(when: str) -> float:
    """`9:22 PM` -> 21.3667: the clock the wiki wrote in the heading, verbatim."""
    match = re.match(r"(\d{1,2}):(\d{2})\s*(AM|PM)", when, re.IGNORECASE)
    if not match:
        return 0.0
    hour = int(match.group(1)) % 12
    if match.group(3).upper() == "PM":
        hour += 12
    return hour + int(match.group(2)) / 60.0


def section_time_ranks(sections: list[sqlite3.Row]) -> dict[int, float]:
    """Where each section sits on the page's time axis: a lookup, not a guess.

    A heading that carries a clock time ("9:22 P.M. Shibuya Station") places
    its section at that time, which is what the Shibuya Incident page needs:
    its sections are organised by stage, and the 10:01 C Tower section is
    written before the 9:22 Shibuya Station one. A heading without a time
    carries the rank of the last timed section written before it -- the same
    inheritance the reorder path applies to unranked sections -- and a section
    written before the first timed one reads before it. A page whose headings
    carry no time at all keeps article order, which is how a wiki writes
    chronology when it has no clock.
    """
    from scriptengine.retrieve.narrative import extract_time

    timed: list[tuple[int, int, float]] = []
    for section in sections:
        when = extract_time((section["title"] or "").strip())
        if when:
            timed.append(
                (int(section["ordinal"]), int(section["id"]), _time_to_hours(when))
            )
    if not timed:
        return {int(s["id"]): float(s["ordinal"]) for s in sections}
    timed.sort()
    ranks: dict[int, float] = {}
    for section in sections:
        section_id, ordinal = int(section["id"]), int(section["ordinal"])
        for _, timed_id, hour in timed:
            if timed_id == section_id:
                ranks[section_id] = hour
                break
        else:
            before = [h for o, _, h in timed if o < ordinal]
            after = [h for o, _, h in timed if o > ordinal]
            if before:
                ranks[section_id] = before[-1]
            else:
                ranks[section_id] = after[0] - 1.0
    return ranks


def extract_from_sections(
    client: LLMClient,
    series: str,
    page: str,
    sections: list[sqlite3.Row],
    known: dict[str, tuple[str, int]],
) -> list[dict[str, Any]]:
    """Events the page states, over its prose sections.

    `known` is the set of names this wiki has a resolved node for, resolved by
    the caller. Everything here is prompt-building, network and string work,
    so it is safe on a worker thread.

    `time_rank` is not the model's: the section's place on the page's axis is
    looked up from its heading and position, and a number the model supplies
    is a number nobody verified.
    """
    ranks = section_time_ranks(sections)
    found: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for section in sections:
        section_id = int(section["id"])
        text = (section["text"] or "").strip()
        for window in _windows(text):
            prompt = _TEMPLATE.format(
                series=series,
                page=page,
                section=(section["title"] or "").strip(),
                passage=window,
                verbs=", ".join(sorted(EVENTIVE_VERBS)),
            )
            answer = client.complete(
                prompt,
                system=SYSTEM,
                temperature=0.0,
                max_tokens=_answer_budget(),
                extra_body=_effort_body(),
            )
            for entry in parse_events_response(answer):
                subject = str(entry.get("subject") or "").strip()
                verb = str(entry.get("verb") or "").strip().lower()
                object_ = str(entry.get("object") or "").strip()
                quote = str(entry.get("quote") or "").strip()
                if not subject or not object_ or verb not in EVENTIVE_VERBS:
                    continue
                # Both ends have to be somebody or somewhere this wiki actually
                # has a page for, or a model supplies a plausible name from the
                # series it has read and nothing in the row shows it.
                subject_resolved = known.get(subject.lower())
                object_resolved = known.get(object_.lower())
                if not subject_resolved or not object_resolved:
                    logger.info(
                        "unknown participant %r/%r for %s",
                        subject, object_, page,
                    )
                    continue
                # Self-directed events are real: Toji kills himself, Mahito
                # awakens. The gate allows subject == object and says so.
                if not _quoted_in(quote, text):
                    logger.info("unquoted %s->%s for %s", verb, object_, page)
                    continue
                key = (
                    subject_resolved[0].lower(), verb, object_resolved[0].lower()
                )
                if key in seen:
                    continue
                seen.add(key)
                found.append(
                    {
                        "subject_node": subject_resolved[1],
                        "subject_name": subject_resolved[0],
                        "object_node": object_resolved[1],
                        "object_name": object_resolved[0],
                        "verb": verb,
                        "section_id": section_id,
                        "quote": quote,
                        "temporal": True,
                        "time_rank": ranks[section_id],
                    }
                )
    return found


def _effort_body() -> dict[str, str] | None:
    """The server field that keeps a thinking model from spending ~20k tokens
    (a hundred seconds) on a passage one pass would read in eight.

    `reasoning_effort` exists only on servers that validate it -- the one on
    :18080 does, and rejects efforts its chat template does not know -- so it
    travels as an opt-out, not a default: a run against a model without the
    knob sets `SCRIPTENGINE_EVENTS_REASONING_EFFORT=""` and answers the full
    price, which the budget env var then has to cover.
    """
    import os

    effort = os.environ.get("SCRIPTENGINE_EVENTS_REASONING_EFFORT", "low").strip()
    return {"reasoning_effort": effort} if effort else None


def _answer_budget() -> int:
    import os

    # The answer is small JSON, but a reasoning model spends its budget
    # thinking before it answers; 2048 was entirely consumed on thinking and
    # never produced a reply. A too-small budget is safe -- a truncated answer
    # is rejected loudly, not stored -- so the default is the size proven to
    # clear the thinking, not a guess.
    return int(os.environ.get("SCRIPTENGINE_ANSWER_TOKENS", "8192"))


def _revid(store: FactStore, title: str) -> str:
    row = store.connection.execute(
        "SELECT revid FROM documents WHERE title = ? COLLATE NOCASE", (title,)
    ).fetchone()
    return str(row["revid"] or "") if row else ""


def extract_events_series(
    paths: SeriesPaths,
    settings: Settings | None = None,
    limit: int | None = None,
    refresh: bool = False,
    progress: Any = None,
    workers: int = 1,
    scope: str = "placement",
) -> dict[str, Any]:
    """Extract this series' placed events, skipping what is current.

    Chunked and threaded exactly as `relations.extract_series` is, and for the
    same reason: the store belongs to this thread, the network wait does not.
    A page is current when it was read under the same `PROMPT_VERSION` and the
    document has not been re-crawled since, which is what `refresh` overrides.

    `scope` chooses which pages to read, via `scope_plan`. `placement` (the
    default) is the arc/event/battle set, where a wiki states events in the
    round. `corpus` reaches the rest of the story: the narrative-family
    sections that name two or more of the wiki's characters (a character's own
    Synopsis/History, a chapter's Plot Details), which is where most of what a
    wiki says about a character actually lives. `all` is the union of the two,
    the complete-coverage path for a `--refresh` run.
    """
    from concurrent.futures import ThreadPoolExecutor

    from scriptengine.ingest.abilities import _guarded

    settings = settings or get_settings()
    client = LLMClient(settings)
    if not client.available():
        raise LLMUnavailable(f"No model at {client.settings.llm_base_url}.")

    report = {
        "considered": 0, "extracted": 0, "cached": 0, "failed": 0, "events": 0,
    }
    with FactStore(paths.facts_db) as store:
        store.ensure_events()
        # Resolved here, on the thread that owns the connection.
        known = known_participants(store)
        pages, by_page = scope_plan(store, scope)
        report["considered"] = len(pages)
        wanted = pages[:limit] if limit else pages

        todo: list[tuple[str, str]] = []
        for page in wanted:
            revid = _revid(store, page)
            state = store.event_state(page)
            # `revid` is 0 on a wiki that stores none: `0 or ""` would read as
            # missing and re-extract the whole corpus on every run.
            state_revid = (
                "" if state is None or state["revid"] is None
                else str(state["revid"])
            )
            current = (
                state is not None
                and not refresh
                and state["prompt_version"] == PROMPT_VERSION
                and state_revid == revid
            )
            if current:
                report["cached"] += 1
                continue
            todo.append((page, revid))

        def store_result(page: str, revid: str, found: list[dict[str, Any]]):
            stored = store.save_events(
                page, found,
                revid=int(revid) if revid.isdigit() else None,
                prompt_version=PROMPT_VERSION, model=settings.llm_model,
            )
            report["extracted"] += 1
            report["events"] += stored
            if progress is not None:
                progress(page, stored)

        if workers <= 1:
            for page, revid in todo:
                try:
                    found = extract_from_sections(
                        client, paths.name, page,
                        by_page[page], known,
                    )
                except LLMUnavailable:
                    raise
                except Exception as error:  # noqa: BLE001 - one page must not stop the run
                    logger.warning("Events for %r failed: %s", page, error)
                    report["failed"] += 1
                    continue
                store_result(page, revid, found)
            return report

        for start in range(0, len(todo), workers * 4):
            chunk = todo[start : start + workers * 4]
            work = [
                (page, revid, by_page[page])
                for page, revid in chunk
            ]

            def run(job):
                page, _, sections = job
                return extract_from_sections(
                    client, paths.name, page, sections, known,
                )

            with ThreadPoolExecutor(max_workers=workers) as pool:
                for (page, revid, _), outcome in zip(
                    work, pool.map(_guarded(run), work)
                ):
                    if isinstance(outcome, BaseException):
                        if isinstance(outcome, LLMRateLimited):
                            raise outcome
                        logger.warning(
                            "Events for %r failed: %s", page, outcome
                        )
                        report["failed"] += 1
                        continue
                    store_result(page, revid, outcome)
    return report