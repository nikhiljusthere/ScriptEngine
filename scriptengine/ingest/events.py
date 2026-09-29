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
import threading
from pathlib import Path
from typing import Any

from scriptengine.config import SeriesPaths, Settings, get_settings
from scriptengine.ingest.abilities import _windows
from scriptengine.ingest.verbatim import fold as _fold, quoted_in as _quoted_in
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
        "met",
    }
)

# Page types an event may be placed in: the arc pages that name the arc, and
# the event/battle pages that are one arc each. A placement in anything else
# is a finding, not a row.
PLACEMENT_TYPES = {"arc", "saga", "event", "battle", "story_arcs"}


def eventive_verbs(store: FactStore) -> frozenset[str]:
    """The closed verb set this wiki's rows may use: the shared set plus the
    wiki's declared `events: extra_verbs` (inert default: none).

    The shared set records that a fight happened, not who won; a wiki whose
    brain answers match-ups declares the outcome verbs (`defeated`,
    `escaped`, `captured`), 2026-09-29 schema test: 0 of 30 "who would win"
    questions were answerable from the shared set's rows.
    """
    extra = {
        str(v).strip().lower()
        for v in _events_overrides(store).get("extra_verbs") or []
        if str(v).strip()
    }
    return EVENTIVE_VERBS | frozenset(extra)


def placement_types(store: FactStore) -> set[str]:
    """The page types an event may be placed in, for this store's wiki.

    The defaults are the type names the first wikis used. Other wikis file the
    same pages under their own infobox's name -- a fight is `conflict` on one,
    an arc `story_arc` on another -- and a name nothing here reads leaves those
    pages out of the placement set entirely (the 2026-09-28 C4 dry-run read 198
    of Marvel's pages and none of MCU's 870 `conflict` pages). So a wiki adds its
    own under `events: placement_types:` in `series/<name>/overrides.yaml`,
    which sits beside the store; the defaults always stay in.
    """
    extra: set[str] = set()
    overrides = Path(store.path).with_name("overrides.yaml")
    if overrides.exists():
        import yaml

        loaded = yaml.safe_load(overrides.read_text(encoding="utf-8")) or {}
        declared = ((loaded.get("events") or {}) if isinstance(loaded, dict)
                    else {}).get("placement_types") or []
        extra = {str(name) for name in declared}
    return PLACEMENT_TYPES | extra

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
    if arc_row is None or arc_row["label"] not in placement_types(store):
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
    stored, _dedup = store.save_events(PHASE1_ARC, rows, revid, prompt_version, model)
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
PROMPT_VERSION = "events-2026-09-29.9"

# What each verb means, for the model. The set a wiki may use is
# `eventive_verbs(store)`; only the verbs in that set are described to it.
# 2026-09-29 (council, COUNCIL_extraction_optimization_2026-09-29.md): the
# definitions carry the precision fixes (a place object for arrived/departed,
# a stated encounter for met) and the outcome verbs a match-up needs.
VERB_DEFINITIONS = {
    "fought": (
        "the subject fought or attacked the object: a clash, a blow, a "
        "strike, a throw, a technique used on them. Every exchange whose end "
        "the passage does not state is `fought`"
    ),
    "defeated": (
        "the passage says in words how the fight ENDED, with the object "
        "beaten: defeated, beat, bested, knocked out, subdued, lost to "
        "(write \"Y lost to X\" as X defeated Y). A hit, a wound, a throw, "
        "a dodge, a block, a restraint, landing an attack or having the upper "
        "hand for a moment is `fought`, never `defeated`"
    ),
    "killed": (
        "the passage states the object died by the subject's act. An "
        "attempt, a wound the object survives, or being \"eliminated\" from a "
        "game is not a kill"
    ),
    "captured": (
        "the passage says the subject took the object prisoner or hostage: "
        "captured, abducted, kidnapped, held captive -- a person or creature, "
        "never an item. Trapping someone in a domain, a barrier, ice or a "
        "sealing object is `sealed`. A passive sentence that does not say "
        "who did it (\"he was imprisoned\") is no event"
    ),
    "escaped": (
        "the subject got away from the object's captivity, trap or pursuit: "
        "escaped, fled, broke free. Dodging or evading an attack is `fought`"
    ),
    "saved": "the subject rescued, freed or protected the object from harm",
    "betrayed": (
        "the subject turned against an ally or broke faith with them: "
        "defected, double-crossed. Deceiving, misleading, punishing, "
        "resenting or leaving someone is not betrayal"
    ),
    "sealed": (
        "the subject sealed, trapped or banished the object: inside a "
        "domain, a barrier, ice, a sealing object or another world"
    ),
    "awakened": (
        "the subject woke up, revived or gained a new power (no object: use "
        "null); using or reactivating a technique they have is not awakening"
    ),
    "met": (
        "the subject met the object: a stated first meeting, visit, "
        "encounter or conversation; not merely being in the same place or "
        "sentence, and not noticing, sensing, helping, reporting about, "
        "working alongside or wishing to meet someone"
    ),
    "arrived": "the subject arrived at a PLACE (the object is the place reached, never a person)",
    "departed": (
        "the subject left a PLACE or a group (the object is the place or "
        "group left, never the destination)"
    ),
}

# Verbs whose missing object means the subject itself (Mahito awakens).
# Every other verb needs a stated object: a missing one is `incomplete`.
_SELF_VERBS = {"awakened"}


def system_prompt(verbs: frozenset[str]) -> str:
    """Everything a call shares, in one fixed prefix: role, rules, verb
    definitions and the answer shape. The page and passage come after it, in
    the user message, so a server's prefix cache reuses this on every call
    (the old template put the page name on line 1 and the rules after the
    passage, so no two calls shared a prefix)."""
    defs = "\n".join(
        f"- {verb}: {VERB_DEFINITIONS.get(verb, verb)}" for verb in sorted(verbs)
    )
    return f"""You extract the events a fiction-wiki passage states. Answer with JSON only: no prose, no code fences.

Answer exactly in this shape:
{{"events": [{{"quote": "...", "subject": "...", "verb": "...", "object": "..." or null}}]}}
Write each event's `quote` first, then read who does what in that quote, and only then fill subject, verb and object from it.

`verb` must be exactly one of these words, never a synonym or another tense:
{defs}

Rules:
- An event is something the passage says happened. A description of who a character is, their powers, a list of who is present, a rule of the story, a plan, an intention ("intends to", "plans to"), a hypothetical or a teaser ("a beatdown is coming") is not an event.
- The subject does the verb and the object is the one it is done to. Both are characters, creatures, groups or places -- never a technique or an item: when a technique or weapon does something, its user is the subject. Both must be names the passage uses; give the fullest name the passage uses for each (its real name or codename, not a pronoun). One name per role: "Gojo and Nanami fight Mahito" is two events.
- If a verb takes no object in the passage, set "object" to null. Never repeat the subject as the object unless the passage says the subject did it to themselves ("he shot himself").
- Pick the most specific verb the passage states: a fight whose winner the passage names in words is `defeated`, not `fought`. An outcome the passage does not state in words is not an outcome: use `fought`, or no event.
- Never supply a subject or an object the passage does not state. A passive sentence that does not say who did it, or a pronoun whose person the passage does not make clear, is no event: skip it rather than guess.
- `quote` is copied from the passage word for word: the clause that states the event. Do not paraphrase, shorten or tidy it.
- Only events the passage itself states, however well you know the series. If it states none, answer {{"events": []}}: an empty answer is correct and useful.

Examples (names invented; read the direction of each sentence carefully):
- "Mira was captured by the Order and imprisoned." -> {{"subject": "the Order", "verb": "captured", "object": "Mira", ...}} (passive voice: the doer is the one after "by")
- "Kade confronted the guards but met defeat." -> {{"subject": "the guards", "verb": "defeated", "object": "Kade", ...}} (Kade lost)
- "Vos was knocked out by Kade." -> {{"subject": "Kade", "verb": "defeated", "object": "Vos", ...}}
- "Before departing to the capital, Kade said goodbye to Mira." -> no event (a journey toward a place is not an arrival there, and a goodbye is not a meeting)
- "Vos tormented Mira in her dreams." -> no event (tormenting is not betrayal)
- "Mira identified Vos as the culprit." -> no event (identifying is not killing, capturing or fighting)
- "Kade dodged Vos's blade and drove a fist into his jaw." -> {{"subject": "Kade", "verb": "fought", "object": "Vos", ...}} (a dodge and a landed blow: the passage does not say the fight ended)
- "Mira's spear, Thorn, pierced the Wraith." -> {{"subject": "Mira", "verb": "fought", "object": "the Wraith", ...}} (the weapon's user is the subject)
- "Kade and Mira fought the Wraith, who fled." -> fought Kade/the Wraith, fought Mira/the Wraith, and {{"subject": "the Wraith", "verb": "escaped", "object": "Kade", ...}} only if the passage says whom it fled"""


_TEMPLATE = """Series: {series}
Page: {page}
Section: {section}

Passage:
{passage}"""


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


# P1 (2026-09-28 architect finding): a bare name can name several variants
# of the same character (a wiki's reality-suffixed titles, one name per
# world) and a disambiguation node is a container of names, not a
# participant. The resolver therefore works on candidate sets, and a
# passage page's reality (its declared reality fact, its title's declared
# pattern, or the wiki's declared default) picks the variant. An ambiguity
# no signal breaks is stored as an explicitly ambiguous participant, never
# pinned to a guess and never dropped. The naming convention itself is the
# wiki's, declared in its overrides (R8) -- this file carries the generic
# resolver only.


def reality_config(store: FactStore) -> dict[str, Any]:
    """The store's declared reality rules (R8): its `events: reality:` block.

    The only place a wiki's reality-naming convention may live:
    `title_pattern` (a title-suffix regex, its one capture group the
    reality), `value_patterns` (regexes tried in order against a fact
    value, the first match's capture group wins) and `fact_key` (the fact
    that carries the value, default `reality`). A wiki that declares
    nothing gets no reality partitioning -- no title match, no fact read:
    a wiki whose convention this file does not know stays unpartitioned
    instead of mis-partitioned.
    """
    block = _events_overrides(store).get("reality")
    if not isinstance(block, dict):
        return {}
    title = str(block.get("title_pattern") or "").strip()
    return {
        "title_pattern": re.compile(title) if title else None,
        "value_patterns": [
            re.compile(str(pattern).strip())
            for pattern in block.get("value_patterns") or []
            if str(pattern).strip()
        ],
        "fact_key": str(block.get("fact_key") or "reality").strip(),
    }


def normalize_reality(
    value: str | None, cfg: dict[str, Any] | None = None
) -> str | None:
    """A declared reality value, normalized by the wiki's own rules (R8).

    The wiki's `value_patterns` are tried in order (the first match's
    capture group is the reality), else the value stands as-is; the result
    is folded for comparison, and a value that names nothing (`unknown`,
    `unspecified`, empty) is None.
    """
    if value is None:
        return None
    v = str(value).strip()
    if not v or v.lower() in ("unknown", "unspecified"):
        return None
    for pattern in (cfg or {}).get("value_patterns") or []:
        match = pattern.search(v)
        if match:
            v = match.group(1).strip()
            break
    if not v or v.lower() in ("unknown", "unspecified"):
        return None
    return v.casefold()


def _node_reality(
    name: str, fact: str | None, cfg: dict[str, Any] | None
) -> str | None:
    """A variant's reality: its title's declared pattern, else its declared
    reality fact. A wiki that declares no reality rules gets None (R8)."""
    cfg = cfg or {}
    title_pattern = cfg.get("title_pattern")
    if title_pattern:
        match = title_pattern.search((name or "").strip())
        if match:
            normalized = normalize_reality(match.group(1), cfg)
            if normalized is not None:
                return normalized
    fact_key = cfg.get("fact_key")
    if fact_key and fact is not None:
        return normalize_reality(fact, cfg)
    return None


# English pronouns and determiners an alias harvester can file as names; a
# language rule, not a wiki's.
_PRONOUN_ALIASES = frozenset(
    "i me my mine you your yours he him his she her hers it its we us our ours"
    " they them their theirs who whom whose which what that this these those"
    " someone somebody anyone everyone man woman boy girl".split()
)


def participant_candidates(
    store: FactStore,
) -> dict[str, list[tuple[int, str, str | None]]]:
    """Folded name -> candidate nodes: `(node_id, canonical name, reality)`.

    Disambiguation pages and the wiki's declared non-participant name
    prefixes (its `events: participant_excludes:` -- the mcu's `Hub:`
    index pages, 2026-09-28) never participate: their nodes are left out
    of every pool, so a bare name that folds over a hub resolves to the
    character page, never to the hub. A wiki that declares no prefixes
    is untouched."""
    containers = (
        NON_PARTICIPANT_TYPES | placement_types(store) | {"disambiguation"}
        | participant_exclude_types(store)
    )
    excluded_prefixes = participant_excludes(store)
    placeholders = ",".join("?" * len(containers))
    container_ids = {
        int(row["id"])
        for row in store.connection.execute(
            f"SELECT n.id FROM nodes n"
            f" JOIN documents d ON d.id = n.document_id"
            f" WHERE n.is_resolved = 1 AND d.page_type IN ({placeholders})",
            tuple(sorted(containers)),
        )
    }
    cfg = reality_config(store)
    reality: dict[int, str | None] = {}
    if cfg.get("fact_key"):
        # A wiki that declares no reality rules reads no reality fact: the
        # partitioning is the wiki's declaration, not this file's (R8).
        reality = {
            int(row["node_id"]): row["value"]
            for row in store.connection.execute(
                "SELECT node_id, value FROM facts WHERE LOWER(key) = ?",
                (str(cfg["fact_key"]).lower(),),
            )
        }

    def candidate(node_id: int, name: str) -> tuple[int, str, str | None] | None:
        if int(node_id) in container_ids or not (name or "").strip():
            return None
        if any((name or "").strip().casefold().startswith(p) for p in excluded_prefixes):
            return None
        return (
            int(node_id),
            name.strip(),
            _node_reality(name, reality.get(int(node_id)), cfg),
        )

    cands: dict[str, list[tuple[int, str, str | None]]] = {}

    def add(name: str, node_id: int, canonical: str) -> None:
        folded = (name or "").strip().lower()
        row = candidate(node_id, canonical)
        if not folded or row is None:
            return
        bucket = cands.setdefault(folded, [])
        if not any(existing[0] == row[0] for existing in bucket):
            bucket.append(row)

    for row in store.connection.execute(
        "SELECT id, name FROM nodes WHERE is_resolved = 1"
    ):
        add(row["name"], row["id"], row["name"])
    for row in store.connection.execute(
        "SELECT a.alias, n.id, n.name FROM aliases a"
        " JOIN nodes n ON n.id = a.node_id WHERE n.is_resolved = 1"
    ):
        alias = (row["alias"] or "").strip()
        # A pronoun is never a name, however an alias harvester filed it
        # (mcu aliases carry "he", "her", "who" -- 2026-09-29 shard 1).
        if alias.lower() in _PRONOUN_ALIASES:
            continue
        add(alias, row["id"], row["name"])
        # A slash-joined alias names the one entity several ways
        # ("skye/daisy johnson/quake" on the mcu's Quake page): each part is
        # a name of it. Without the split, "Daisy Johnson" reached only her
        # variant subpages and the main page's events were dropped as
        # unknown participants (MCU shard 1: 50% of proposals dropped).
        if "/" in alias:
            for part in alias.split("/"):
                part = part.strip()
                if len(part) > 2 and part.lower() not in _PRONOUN_ALIASES:
                    add(part, row["id"], row["name"])
    # A disambiguation page's `main_articleN` targets are participants the
    # page's own name should reach: the value's first field is the article,
    # the rest is citation noise.
    for row in store.connection.execute(
        "SELECT n.id AS nid, n.name AS disambig, f.value AS value FROM nodes n"
        " JOIN documents d ON d.id = n.document_id"
        " JOIN facts f ON f.node_id = n.id"
        " WHERE d.page_type = 'disambiguation' AND n.is_resolved = 1"
        " AND LOWER(f.key) LIKE 'main_article%'"
    ):
        target = re.sub(r"[\[\]{}]", "", (row["value"] or "").split(";")[0]).strip()
        node = store.node_by_name(target) if target else None
        if node is not None and int(node["is_resolved"]):
            add(row["disambig"], node["id"], node["name"])
    return cands


def _page_reality(
    store: FactStore, page: str, default: str | None, cfg: dict[str, Any]
) -> str | None:
    """The page-reality body, given a preloaded reality config (R8)."""
    fact_key = cfg.get("fact_key")
    row = None
    if fact_key:
        row = store.connection.execute(
            "SELECT f.value FROM facts f"
            " JOIN nodes n ON n.id = f.node_id"
            " WHERE n.name = ? COLLATE NOCASE AND LOWER(f.key) = ?"
            " LIMIT 1",
            (page, str(fact_key).lower()),
        ).fetchone()
    if row is not None:
        normalized = normalize_reality(row["value"], cfg)
        if normalized is not None:
            return normalized
    title_pattern = cfg.get("title_pattern")
    if title_pattern:
        match = title_pattern.search((page or "").strip())
        if match:
            normalized = normalize_reality(match.group(1), cfg)
            if normalized is not None:
                return normalized
    return normalize_reality(default, cfg)


def page_reality(
    store: FactStore, page: str, default: str | None = None
) -> str | None:
    """The passage page's reality: its declared reality fact, its title's
    declared pattern, else the wiki's declared default (`events:
    default_reality:` in the overrides, the only place a wiki-level rule may
    live). A wiki that declares no reality rules gets None (R8).

    `default` may be preloaded by the caller (`_wiki_default_reality`, once
    per run); absent, it is read here -- the batch path passes it, so a
    per-page call pays the override read only on its own."""
    if default is None:
        default = _wiki_default_reality(store)
    return _page_reality(store, page, default, reality_config(store))


def page_realities(
    store: FactStore, pages: list[str], default: str | None = None
) -> dict[str, str | None]:
    """`page_reality` for a queue, in one pass (the connection belongs to the
    calling thread; the result travels to workers as a plain dict)."""
    cfg = reality_config(store)
    if default is None:
        default = _wiki_default_reality(store)
    out: dict[str, str | None] = {}
    for page in pages:
        out[page] = _page_reality(store, page, default, cfg)
    return out


def participant_excludes(store: FactStore) -> list[str]:
    """The wiki's declared non-participant name prefixes, casefolded.

    The `events: participant_excludes:` block of its overrides (the mcu's
    `Hub:` index pages, 2026-09-28): the declared pages are never
    participants, and the declaration is what drives the repair of the rows
    filed on them -- a wiki that declares nothing is untouched."""
    return [
        str(prefix).strip().casefold()
        for prefix in _events_overrides(store).get("participant_excludes") or []
        if str(prefix).strip()
    ]


def declared_place_nodes(store: FactStore) -> set[int] | None:
    """The nodes a movement (arrived/departed) may take as its object: those
    whose page type is one of the wiki's declared `events: place_types:`.
    None -- the G4 shape gate is off -- for a wiki that declares none."""
    declared = [
        str(name).strip()
        for name in _events_overrides(store).get("place_types") or []
        if str(name).strip()
    ]
    if not declared:
        return None
    marks = ",".join("?" * len(declared))
    return {
        int(row[0])
        for row in store.connection.execute(
            "SELECT n.id FROM nodes n JOIN documents d ON d.id = n.document_id"
            f" WHERE d.page_type IN ({marks})",
            declared,
        )
    }


def participant_exclude_types(store: FactStore) -> set[str]:
    """The wiki's declared non-participant page types: its `events:
    participant_exclude_types:` (inert default: none). A page of one of them
    -- a song, a volume, a disc -- is a work about the story, never an actor
    in it, so its title never wins a name. 2026-09-29 JJK verification: the
    ending theme "Akari" took Akari Nitta's rows on every page that links to
    neither."""
    return {
        str(name).strip()
        for name in _events_overrides(store).get("participant_exclude_types") or []
        if str(name).strip()
    }


def _is_variant_of(canonical: str, name: str) -> bool:
    """`canonical` is the wiki's variant form of `name`: the same title with
    a `/subpage` or a space-then-`(` qualifier appended (`Conan/Earth-16356`,
    `The Avengers (comic)`). The bare name itself, a longer different title,
    or another name entirely are not variants. Case-insensitive: the model's
    casing is not the wiki's."""
    q = (name or "").strip().casefold()
    c = (canonical or "").strip().casefold()
    if not q or len(c) <= len(q) or not c.startswith(q):
        return False
    return c[len(q)] in "/(" or c[len(q):len(q) + 2] == " ("


def pick_candidate(
    cands: list[tuple[int, str, str | None]],
    name: str | None,
    page_real: str | None = None,
    linked: set[int] | None = None,
    self_page: str | None = None,
) -> tuple[int, str, str | None] | dict | None:
    """The one candidate a passage names, an explicit ambiguity, or None.

    An exact title match wins over the wiki's variant forms of the same
    name (`(qualifier)` and `/subpage`): the bare name names the page,
    never a spin-off. Where the exact page is absent, a variant is a
    candidate only where the passage itself points at it -- the page links
    to the variant, or the passage's own page is that variant (architect
    2026-09-28): the bare name never names a subpage, and a pool of
    unpointed variants alone resolves to nothing.

    A page reality filters the survivors to its own reality; where no
    candidate carries that reality the base variant (no known reality) wins,
    and what no signal breaks is returned as `{"ambiguous": cands}` for the
    store to file as a counted class. None means the wiki has no node for the
    name at all: a finding, not a row.

    `linked` is the set of nodes the passage's page itself links to -- the
    wiki's pre-resolved wikilinks (architect 2026-09-28). An ambiguous set
    with exactly one linked member is the wiki's own answer and resolves
    deterministically; zero or several linked members leave it a counted
    ambiguity.
    """
    if not cands:
        return None
    # The exact page, not the wiki's variant forms of its title: the bare
    # name names the page, never a spin-off.
    folded = (name or "").strip().casefold()
    exact = [c for c in cands if c[1].casefold() == folded]
    self_folded = (self_page or "").strip().casefold()
    if len(exact) == 1:
        hit = exact[0]
        # ...unless the page never links to the exact page and points at
        # exactly one other entity the name reaches by alias: its own link,
        # or the page itself (a page never links to itself; a `/subpage`
        # points at its base). 2026-09-29 JJK verification: bare "Akari"
        # resolved to the ending-theme song and "Ryu" to Takuma Ino's
        # shikigami on pages that link only to Akari Nitta / Ryu Ishigori
        # (35 misfiled rows). A variant of the name itself is never the
        # diversion: "Sukuna" never slides to "Sukuna/Synopsis".
        own = {self_folded, self_folded.split("/", 1)[0].strip()} - {""}
        if hit[0] not in (linked or ()) and hit[1].casefold() not in own:
            pointed = [
                c for c in cands
                if c[0] != hit[0]
                and not _is_variant_of(c[1], name)
                and (c[0] in (linked or ()) or c[1].casefold() in own)
            ]
            if len(pointed) == 1:
                return pointed[0]
        return hit
    # The page's own entity wins for its own names: the page is a candidate
    # for this name only because the name is one of its subject's names, and
    # a page never links to itself, so the link signal below would otherwise
    # pick a sibling. 2026-09-28 pilot: "Beast" on Henry McCoy (Earth-616)
    # resolved to Henry McCoy (Clone) (Earth-616), the page's only linked
    # namesake (review R12 fix 2).
    if self_folded:
        own = [c for c in cands if c[1].casefold() == self_folded]
        # A subpage's subject is its base page, which it never links either:
        # "Gojo" on Satoru Gojo/Synopsis went to the Sorcerer Clan page, the
        # synopsis's only linked namesake (2026-09-29 JJK judged set).
        if not own and "/" in self_folded:
            base = self_folded.split("/", 1)[0].strip()
            own = [c for c in cands if c[1].casefold() == base]
        if len(own) == 1:
            return own[0]
    # A variant form of the name is a candidate only where the passage
    # points at it: the page links to it, or the passage's own page is that
    # variant (architect 2026-09-28) -- the bare name never names a
    # subpage, with or without a link set.
    cands = [
        c for c in cands
        if not _is_variant_of(c[1], name)
        or c[0] in (linked or ())
        or (self_folded and c[1].casefold() == self_folded)
    ]
    if not cands:
        return None
    # A subpage never outranks its own base page for a shared name: with
    # "Quake" and "Quake/Destroyed Earth" both reached by "Daisy Johnson"
    # (the slash-alias split, 2026-09-29), the name names the page, not the
    # variant -- unless the passage points at the subpage.
    bases = {c[1].casefold() for c in cands}
    cands = [
        c for c in cands
        if "/" not in c[1]
        or c[1].split("/", 1)[0].strip().casefold() not in bases
        or c[0] in (linked or ())
        or (self_folded and c[1].casefold() == self_folded)
    ]
    if len(cands) == 1:
        return cands[0]

    def broken(ambiguous: list[tuple[int, str, str | None]]):
        if linked:
            hits = [c for c in ambiguous if c[0] in linked]
            if len(hits) == 1:
                return hits[0]
        # Where no link decides, the one candidate whose own title carries
        # the name as a word owns it; the others reach it only as an alias.
        # 2026-09-29 JJK verification: bare "Gojo" tied Satoru Gojo with the
        # Sorcerer Clan page (whose aliases list each clan's name), so every
        # "Gojo" row on a page linking both was filed ambiguous.
        word = re.compile(rf"\b{re.escape((name or '').strip())}\b", re.I)
        titled = [c for c in ambiguous if (name or "").strip() and word.search(c[1])]
        if len(titled) == 1:
            return titled[0]
        return {"ambiguous": ambiguous}

    if page_real:
        matching = [c for c in cands if c[2] == page_real]
        if len(matching) == 1:
            return matching[0]
        if len(matching) > 1:
            return broken(matching)
        base = [c for c in cands if c[2] is None]
        if len(base) == 1:
            return base[0]
        return broken(cands)
    base = [c for c in cands if c[2] is None]
    if len(base) == 1:
        return base[0]
    return broken(cands)


def re_resolve_participants(store: FactStore) -> dict:
    """Re-point the stored rows' participants through the reality-aware
    resolver. The quotes are kept -- no re-extraction -- so a store extracted
    before the resolver existed is repaired in place. A row whose name no
    candidate set reaches keeps its old pointers (a finding, counted, never
    destroyed) and an unbreakable ambiguity takes the explicit-ambiguous
    form: the node goes NULL and the candidate list goes in the name field.

    Two signals break a set the wiki's own pages carry. The page's reality
    picks the variant that belongs to it. And the page's links -- the
    wiki's pre-resolved wikilinks, one set per page from `chunk_nodes`
    (architect 2026-09-28) -- break what reality leaves: an ambiguous set
    with exactly one linked member is the wiki's own answer and is filed;
    zero or several linked members stay a counted ambiguity.

    Returns the before/after tally the receipt reports: rows on a
    disambiguation node, rows cross-reality, rows filed ambiguous, and how
    many rows the link signal alone re-pointed.
    """
    cands = participant_candidates(store)
    cfg = reality_config(store)
    default = _wiki_default_reality(store)
    titles = {
        row["doc_title"]
        for row in store.connection.execute("SELECT DISTINCT doc_title FROM events")
    }
    realities = page_realities(store, sorted(titles), default)
    node_facts: dict[int, str | None] = {}
    if cfg.get("fact_key"):
        node_facts = {
            int(row["node_id"]): row["value"]
            for row in store.connection.execute(
                "SELECT node_id, value FROM facts WHERE LOWER(key) = ?",
                (str(cfg["fact_key"]).lower(),),
            )
        }
    # The wiki's own pre-resolved wikilinks (architect 2026-09-28): per page,
    # the nodes its chunks link to. A same-reality ambiguity the reality
    # signal cannot break is broken by them when exactly one candidate is
    # linked -- the wiki answered; the rows the links do not answer stay a
    # counted ambiguity.
    linked_by_page: dict[str, set[int]] = {}
    for title, node_id in store.connection.execute(
        "SELECT c.doc_title, cn.node_id"
        " FROM chunk_nodes cn JOIN chunks c ON c.id = cn.chunk_id"
    ):
        linked_by_page.setdefault(title, set()).add(int(node_id))

    def page_real(doc_title: str) -> str | None:
        return realities.get(doc_title)

    def is_disambig(node_id: int | None) -> bool:
        if node_id is None:
            return False
        row = store.connection.execute(
            "SELECT d.page_type FROM nodes n"
            " JOIN documents d ON d.id = n.document_id"
            " WHERE n.id = ?",
            (int(node_id),),
        ).fetchone()
        return row is not None and row["page_type"] == "disambiguation"

    def crossed(node_id: int | None, name: str | None, doc_title: str) -> bool:
        if node_id is None:
            return False
        real = _node_reality(
            name or "", node_facts.get(int(node_id)), cfg
        )
        if real is None:
            return False
        page_real_ = page_real(doc_title)
        return page_real_ is not None and real != page_real_

    def tally() -> dict:
        rows = store.connection.execute(
            "SELECT subject_node, subject_name, object_node, object_name, doc_title"
            " FROM events"
        ).fetchall()
        return {
            "rows": len(rows),
            "on_disambiguation_node": sum(
                1
                for r in rows
                if is_disambig(r["subject_node"]) or is_disambig(r["object_node"])
            ),
            "cross_reality": sum(
                1
                for r in rows
                if crossed(r["subject_node"], r["subject_name"], r["doc_title"])
                or crossed(r["object_node"], r["object_name"], r["doc_title"])
            ),
            "ambiguous": sum(
                1
                for r in rows
                if r["subject_node"] is None or r["object_node"] is None
            ),
        }

    before = tally()
    moved = ambiguous_new = unresolved_kept = link_broken = merged = 0

    def repoint(role: str, row_id: int, node: int, name_out: str) -> None:
        """Re-point one row. Where the new pointer pair duplicates a row the
        page already stores, the re-pointed row is the duplicate -- the
        wiki's answer, recorded once (the store's own dedup rule) -- and is
        merged away, counted."""
        nonlocal merged
        other = "object" if role == "subject" else "subject"
        key = store.connection.execute(
            f"SELECT {other}_node, verb, section_id, time_rank, passage"
            f" FROM events WHERE rowid = ?",
            (row_id,),
        ).fetchone()
        if key[f"{other}_node"] is not None and key["section_id"] is not None:
            duplicate = store.connection.execute(
                f"SELECT 1 FROM events WHERE rowid != ?"
                f" AND {role}_node = ? AND {other}_node = ?"
                " AND verb = ? AND section_id = ? AND time_rank = ?"
                " AND passage = ? LIMIT 1",
                (row_id, node, key[f"{other}_node"], key["verb"],
                 key["section_id"], key["time_rank"], key["passage"]),
            ).fetchone()
            if duplicate:
                store.connection.execute(
                    "DELETE FROM events WHERE rowid = ?", (row_id,)
                )
                merged += 1
                return
        store.connection.execute(
            f"UPDATE events SET {role}_node = ?, {role}_name = ? WHERE rowid = ?",
            (node, name_out, row_id),
        )

    for role in ("subject", "object"):
        # A row that stores the model's own mention (R12, 2026-09-29) is
        # re-resolved from the mention, not from the name an earlier resolver
        # picked -- including a row filed ambiguous, which a better resolver
        # may now break. Rows without a mention keep the name path.
        rows = store.connection.execute(
            f"SELECT DISTINCT doc_title, {role}_name, {role}_mention FROM events"
            f" WHERE ({role}_node IS NOT NULL AND {role}_name IS NOT NULL)"
            f" OR {role}_mention IS NOT NULL"
        ).fetchall()
        for row in rows:
            name = (row[f"{role}_name"] or "").strip()
            mention = (row[f"{role}_mention"] or "").strip()
            same = (
                f"doc_title = ? AND {role}_name = ? COLLATE NOCASE"
                f" AND {role}_mention IS ?"
            )
            same_args = (row["doc_title"], name, row[f"{role}_mention"])
            name_key = mention or name
            # The extraction's own pool (2026-09-29): a name part the page
            # links, or the page itself, reaches its entity here too, so a
            # repair never disagrees with the read that stored the row.
            pool = name_pool(
                cands, name_key, linked_by_page.get(row["doc_title"]),
                row["doc_title"],
            )
            # The pools refuse a name the wiki declared a non-participant
            # (`participant_excludes:` -- the mcu's `Hub:` index pages,
            # 2026-09-28): a row filed on the hub is re-resolved under the
            # bare name the hub indexes. The declaration drives the repair;
            # a name no pool carries stays a finding, kept as filed.
            resolve_name = name_key
            if not pool:
                for prefix in participant_excludes(store):
                    if name_key.casefold().startswith(prefix):
                        resolve_name = name_key[len(prefix):].strip()
                        pool = cands.get(resolve_name.lower(), [])
                        break
            real = page_real(row["doc_title"])
            linked = linked_by_page.get(row["doc_title"])
            pick = pick_candidate(pool, resolve_name, real, linked, row["doc_title"])
            if pick is None:
                unresolved_kept += 1
                continue
            if isinstance(pick, dict):
                # Re-filing ambiguous: a NULL node can never collide with a
                # stored row (NULLs keep the unique key distinct), so the
                # pair updates wholesale.
                name_out = " | ".join(sorted(c[1] for c in pick["ambiguous"]))
                ambiguous_new += 1
                store.connection.execute(
                    f"UPDATE events SET {role}_node = NULL, {role}_name = ?"
                    f" WHERE {same}",
                    (name_out, *same_args),
                )
                continue
            node, name_out = pick[0], pick[1]
            moved += 1
            # The probe strips both page signals -- links and the page
            # itself: a row the signals left ambiguous on their own is
            # what the link signal alone broke.
            if linked and isinstance(pick_candidate(pool, resolve_name, real), dict):
                link_broken += 1
            for r in store.connection.execute(
                f"SELECT rowid FROM events WHERE {same}"
                + ("" if mention else f" AND {role}_node IS NOT NULL"),
                same_args,
            ):
                repoint(role, r["rowid"], node, name_out)

    # The listed names are node names (the resolver's canonical form). Map
    # them back through the candidate pools, not the node table: a name the
    # pools refuse -- a hub or a disambiguation page (2026-09-28) -- is never
    # a re-point target. Exactly one of the listed nodes linked from the
    # page is the wiki's answer (architect 2026-09-28). Zero or several linked
    # members keep the row a counted ambiguity; a name no pool carries is a
    # finding, and the row is left as filed.
    name_to_node: dict[str, int] = {}
    for pool in cands.values():
        for node_id, canonical, _ in pool:
            name_to_node.setdefault(canonical.strip().lower(), int(node_id))
    for role in ("subject", "object"):
        pairs = store.connection.execute(
            f"SELECT DISTINCT doc_title, {role}_name FROM events"
            f" WHERE {role}_node IS NULL AND {role}_name LIKE '% | %'"
        ).fetchall()
        for pair in pairs:
            listed = pair[f"{role}_name"]
            linked = linked_by_page.get(pair["doc_title"]) or set()
            hits = [
                (part, name_to_node[part.strip().lower()])
                for part in listed.split(" | ")
                if part.strip().lower() in name_to_node
                and name_to_node[part.strip().lower()] in linked
            ]
            if len(hits) != 1:
                continue
            part, node = hits[0]
            row_ids = [
                r["rowid"]
                for r in store.connection.execute(
                    f"SELECT rowid FROM events"
                    f" WHERE doc_title = ? AND {role}_name = ? COLLATE NOCASE"
                    f" AND {role}_node IS NULL",
                    (pair["doc_title"], listed),
                )
            ]
            for row_id in row_ids:
                repoint(role, row_id, node, part)
            link_broken += len(row_ids)
    store.connection.commit()
    after = tally()
    after["moved"] = moved
    after["ambiguous_new"] = ambiguous_new
    after["unresolved_kept"] = unresolved_kept
    after["link_broken"] = link_broken
    after["merged"] = merged
    return {"before": before, "after": after}


def _wiki_default_reality(store: FactStore) -> str | None:
    """The wiki-level default reality, declared in the overrides only."""
    overrides = Path(store.path).with_name("overrides.yaml")
    if not overrides.exists():
        return None
    import yaml

    loaded = yaml.safe_load(overrides.read_text(encoding="utf-8")) or {}
    declared = ((loaded.get("events") or {}) if isinstance(loaded, dict) else {}).get(
        "default_reality"
    )
    return str(declared) if declared else None


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
    types = placement_types(store)
    placeholders = ",".join("?" * len(types))
    rows = store.connection.execute(
        f"SELECT d.title FROM documents d"
        f" WHERE d.page_type IN ({placeholders})",
        tuple(sorted(types)),
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


# T2 (C4, R1): the furniture the prose scope excludes -- the ONLY exclusion.
# The generic default is wiki-agnostic (heading names, no series names): the
# extractor's list set (the narrative retriever's, minus the narrative
# plot/summary/synopsis, plus the extraction-only furniture) extended with the
# link/image families no wiki writes prose under. A wiki extends it with
# `events: furniture:` in its overrides -- the only place a per-wiki rule may
# live -- and every excluded section is counted per heading, with the named
# cause, in the dry-run and the receipt.
_FURNITURE_LINK_FAMILIES = {
    "external links", "see also", "further reading", "bibliography",
    "references", "screenshots", "cover art", "interior art", "media",
    "gallery",
}

# R1.3: the list-shaped headings are text, never silently skipped. Where they
# carry a panel-eligible sentence the extractor reads them (rows land as
# standing-state, `temporal=0`); in the receipt they are counted per heading
# as the `list_class` class, and their relational content is the plan-C5
# `relations` work the council rules on with the counts in hand.
LIST_CLASS_TITLES = {
    "allies", "enemies", "appearances", "family", "equipment",
    "vehicles", "relationships", "dialogue",
}


def _events_overrides(store: FactStore) -> dict[str, Any]:
    """This store's `events:` override block, `{}` when the file is absent.

    The only place a per-wiki event rule may live: `placement_types`,
    `furniture`, `narrative_fact_keys`, the `axis` declaration and
    `default_reality` all read off this one block.
    """
    overrides = Path(store.path).with_name("overrides.yaml")
    if not overrides.exists():
        return {}
    import yaml

    loaded = yaml.safe_load(overrides.read_text(encoding="utf-8")) or {}
    block = (loaded.get("events") or {}) if isinstance(loaded, dict) else {}
    return block if isinstance(block, dict) else {}


def events_axis_config(store: FactStore) -> dict[str, Any]:
    """The store's declared store-axis (R3): its `events: axis:` block.

    A wiki declares the order signals it records -- `date_keys`,
    `chain_keys`, `order_keys`, `partition_key` -- and the store axis
    (``timeaxis.store_time_axis``) places its pages by them, strongest
    first: the chain, then the date, then a citation that inherits the
    cited page's rank. A wiki that declares nothing sees ``{}``, and the
    manga signals stand alone.
    """
    axis = _events_overrides(store).get("axis")
    return axis if isinstance(axis, dict) else {}


def generic_furniture() -> set[str]:
    """The wiki-agnostic furniture headings, folded (R1)."""
    return _excluded_section_titles() | _FURNITURE_LINK_FAMILIES


def furniture_titles(store: FactStore) -> dict[str, str]:
    """Folded furniture heading -> cause, `generic` or `wiki` (R1).

    A heading both lists carry is caused by the generic default: the wiki
    declaration only extends the set, it does not re-cause what it repeats.
    """
    causes = {heading: "generic" for heading in generic_furniture()}
    for heading in _events_overrides(store).get("furniture") or []:
        folded = str(heading).strip().lower()
        if folded:
            causes.setdefault(folded, "wiki")
    return causes


def panel_sentences(text: str | None) -> list[str]:
    """The panel-eligible sentences a stretch of text carries (R7).

    The D3 panel's own line definition -- `span_recall.sentences` at
    `min_words=6`, the tier-1 denominator -- so a passage the extractor reads
    is exactly a line the panel counts. A section, lead or fact value holding
    none of them (pure markup, a link stub, an empty template) is the counted
    `below_floor` class: accounted for the council, never silently dropped.
    """
    from scriptengine.eval.span_recall import sentences

    return sentences(text or "", 6)


def prose_sections(store: FactStore, page: str) -> list[sqlite3.Row]:
    """The page's prose sections, heading-agnostic (R1, R7).

    The extractable-prose test is decided on content, not title: a section is
    read when it holds a panel-eligible sentence and its heading is not
    furniture. The heading allow-list cannot reach the story-named
    sub-sections a character biography is split into, which is why the test
    lives here instead of on the title.
    """
    furniture = furniture_titles(store)
    out: list[sqlite3.Row] = []
    for section in store.document_sections(page):
        heading = (section["title"] or "").strip().lower()
        if heading in furniture:
            continue
        if panel_sentences((section["text"] or "").strip()):
            out.append(section)
    return out


def prose_scope(
    store: FactStore,
) -> tuple[list[str], dict[str, list[sqlite3.Row]]]:
    """`(pages, sections_by_page)`: every prose section in the store (R1).

    One pass over `sections`, heading-agnostic: a section is prose when it
    holds a panel-eligible sentence (R7) and its heading is not furniture.
    The page queue is ordered by the prose it carries, as `placement_pages`
    is, so `--limit` reaches the densest pages first.
    """
    furniture = furniture_titles(store)
    titles = {
        int(row["id"]): row["title"]
        for row in store.connection.execute("SELECT id, title FROM documents")
    }
    by_doc: dict[int, list[sqlite3.Row]] = {}
    weight: dict[int, int] = {}
    for section in store.connection.execute(
        "SELECT s.* FROM sections s ORDER BY s.document_id, s.ordinal"
    ):
        heading = (section["title"] or "").strip().lower()
        if heading in furniture:
            continue
        if not panel_sentences((section["text"] or "").strip()):
            continue
        doc_id = int(section["document_id"])
        by_doc.setdefault(doc_id, []).append(section)
        weight[doc_id] = weight.get(doc_id, 0) + int(section["word_count"] or 0)
    ordered = sorted(by_doc, key=lambda d: (weight[d], d), reverse=True)
    return (
        [titles[d] for d in ordered],
        {titles[d]: by_doc[d] for d in ordered},
    )


def _section_passage(section: sqlite3.Row) -> dict[str, Any]:
    """A section row as a passage: the row's own prose, its own time rank.

    The row's `passage` field stays '' -- the committed section-row marker:
    the row's anchor is the section itself, re-keyed on a rebuild by
    (doc_title, section_ordinal). The section title travels separately, for
    the prompt, and must not leak into `passage`: a non-empty, non-lead,
    non-`fact:` passage reads as a section-less row, and its quote
    verifies against nothing, so the next rebuild drops the row
    unverified (2026-09-28 pilot finding)."""
    title = (section["title"] or "").strip()
    return {
        "kind": "section",
        "id": int(section["id"]),
        "ordinal": int(section["ordinal"]),
        "passage": "",
        "title": title,
        "text": (section["text"] or "").strip(),
    }


def lead_passage(store: FactStore, page: str) -> dict[str, Any] | None:
    """The page lead as a passage (R2, R7), or None when it holds no
    panel-eligible sentence -- the counted `lead_dropped` class.

    The lead is stored raw wikitext, so the test strips first; the strip is a
    no-op on a clean lead and the test is the panel's, not a word floor.
    """
    from scriptengine.ingest.wikitext import strip_markup

    row = store.connection.execute(
        "SELECT lead FROM documents WHERE title = ? COLLATE NOCASE", (page,)
    ).fetchone()
    text = strip_markup((row["lead"] if row else "") or "").strip()
    if not panel_sentences(text):
        return None
    return {
        "kind": "lead",
        "id": None,
        "passage": "lead",
        "title": "",
        "text": text,
    }


def narrative_fact_keys(store: FactStore) -> list[str]:
    """The wiki's declared narrative fact keys (design 1): fnmatch patterns,
    case-insensitive, in the overrides only -- the keys whose values are
    prose the extractor reads (a `history` beat, a `synopsis*` instalment)."""
    return [
        str(pattern).strip()
        for pattern in _events_overrides(store).get("narrative_fact_keys") or []
        if str(pattern).strip()
    ]


def excluded_fact_keys(store: FactStore) -> list[dict[str, str]]:
    """The wiki's declared-but-excluded fact keys (R10): fnmatch patterns,
    each with a one-line reason, in the overrides only.

    Inert by default -- no extraction behaviour reads them -- but counted:
    the dry-run census reports each, so a key the council later wants read
    is a one-line move to `narrative_fact_keys`, never a silence. An entry
    is ``{"key": <pattern>, "reason": <text>}``; a bare string is a pattern
    with no reason.
    """
    out: list[dict[str, str]] = []
    for entry in _events_overrides(store).get("excluded_fact_keys") or []:
        if isinstance(entry, dict):
            key = str(entry.get("key") or "").strip()
            reason = str(entry.get("reason") or "").strip()
        else:
            key = str(entry).strip()
            reason = ""
        if key:
            out.append({"key": key, "reason": reason})
    return out


def fact_key_census(
    store: FactStore, pages: set[str] | None
) -> list[dict[str, Any]]:
    """The per-key census of the wiki's declared narrative fact keys (R9,
    100% scope) and its counted exclusions (R10).

    One row per concrete key the wiki's patterns reach: how many fact values
    the key carries in the store (`total`), how many of those hold a
    panel-eligible sentence (`prose`), and how many of those sit on a page of
    the queue (`queue`, `None` counts the whole store). Each row carries a
    `status` -- `declared` (read under `--scope all`) or `excluded`
    (deliberately not read, with the `reason` the wiki recorded) -- so the
    dry run reports both: a declared key the corpus no longer backs, or prose
    a scope cannot reach, is a number the council can rule on, never a
    silence.
    """
    import fnmatch

    from scriptengine.ingest.wikitext import strip_markup

    declared = narrative_fact_keys(store)
    excluded = excluded_fact_keys(store)
    if not declared and not excluded:
        return []
    distinct = {
        row["key"]
        for row in store.connection.execute(
            "SELECT DISTINCT LOWER(key) AS key FROM facts"
        )
    }

    def row_for(key: str, status: str, reason: str) -> dict[str, Any]:
        rows = store.connection.execute(
            "SELECT f.value AS value, d.title AS title FROM facts f"
            " JOIN nodes n ON n.id = f.node_id"
            " JOIN documents d ON d.id = n.document_id"
            " WHERE LOWER(f.key) = ?",
            (key,),
        ).fetchall()
        prose = 0
        in_queue = 0
        for row in rows:
            if not panel_sentences(strip_markup(row["value"] or "")):
                continue
            prose += 1
            if pages is None or row["title"] in pages:
                in_queue += 1
        return {
            "key": key,
            "total": len(rows),
            "prose": prose,
            "queue": in_queue,
            "status": status,
            "reason": reason,
        }

    out: list[dict[str, Any]] = []
    declared_keys: set[str] = set()
    for key in sorted(distinct):
        if any(fnmatch.fnmatch(key, p) for p in declared):
            declared_keys.add(key)
            out.append(row_for(key, "declared", ""))
    for entry in excluded:
        for key in sorted(distinct):
            if key in declared_keys or not fnmatch.fnmatch(key, entry["key"]):
                continue
            out.append(row_for(key, "excluded", entry["reason"]))
    return out


def fact_pages(store: FactStore) -> list[str]:
    """The pages a declared narrative fact value reaches (R10), ordered by the
    prose they carry, densest first.

    A page whose story lives only in fact values -- a `history` beat with no
    prose section -- is in no other rule's queue: placement, the corpus rule
    and the R1 prose scope all key on sections. Its declared fact values hold
    the panel-eligible sentences the extractor reads, so the page joins the
    `all` queue on them. Generic: keyed on the wiki's declared
    `narrative_fact_keys` only -- a wiki that declares none (JJK, CSM) sees
    `[]` and its `all` page list is byte-identical to the pre-fix tree.
    """
    import fnmatch

    from scriptengine.ingest.wikitext import strip_markup

    patterns = narrative_fact_keys(store)
    if not patterns:
        return []
    distinct = {
        row["key"]
        for row in store.connection.execute(
            "SELECT DISTINCT LOWER(key) AS key FROM facts"
        )
    }
    keys = [
        key
        for key in sorted(distinct)
        if any(fnmatch.fnmatch(key, p) for p in patterns)
    ]
    if not keys:
        return []
    placeholders = ",".join("?" * len(keys))
    weight: dict[str, int] = {}
    for row in store.connection.execute(
        "SELECT d.title AS title, f.value AS value FROM facts f"
        " JOIN nodes n ON n.id = f.node_id"
        " JOIN documents d ON d.id = n.document_id"
        f" WHERE LOWER(f.key) IN ({placeholders})",
        keys,
    ):
        text = strip_markup(row["value"] or "").strip()
        if not panel_sentences(text):
            continue
        weight[row["title"]] = weight.get(row["title"], 0) + len(text.split())
    return sorted(weight, key=lambda t: (weight[t], t), reverse=True)


def _fact_key_order(key: str) -> tuple[str, int]:
    """`synopsis2` < `synopsis10`: the trailing numeral orders, not sorts."""
    match = re.match(r"^(.*?)(\d+)$", (key or "").strip().lower())
    if match:
        return match.group(1), int(match.group(2))
    return (key or "").strip().lower(), 0


def fact_passages(
    store: FactStore, page: str
) -> list[dict[str, Any]]:
    """The page's declared narrative fact values as passages (design 1).

    Only the keys the wiki declared read: the values of `history`, of
    `synopsis*`, in the in-value order. A value holding no panel-eligible
    sentence is junk (a `synopsis    header` residue) and stays out -- the
    counted `fact_key_dropped` class, accounted in the dry-run per key.
    """
    import fnmatch

    from scriptengine.ingest.wikitext import strip_markup

    patterns = narrative_fact_keys(store)
    if not patterns:
        return []
    rows = store.connection.execute(
        "SELECT f.key AS key, f.value AS value FROM facts f"
        " JOIN nodes n ON n.id = f.node_id"
        " JOIN documents d ON d.id = n.document_id"
        " WHERE d.title = ? COLLATE NOCASE",
        (page,),
    ).fetchall()
    matches: dict[str, list[str]] = {}
    for row in rows:
        key = (row["key"] or "").strip()
        if not any(fnmatch.fnmatch(key.lower(), p) for p in patterns):
            continue
        matches.setdefault(key, []).append(row["value"] or "")
    out: list[dict[str, Any]] = []
    for key in sorted(matches, key=_fact_key_order):
        for value in matches[key]:
            text = strip_markup(value).strip()
            if not panel_sentences(text):
                continue
            out.append(
                {
                    "kind": "fact",
                    "id": None,
                    "passage": f"fact:{key}",
                    "title": key,
                    "text": text,
                }
            )
    return out


def build_passages(
    store: FactStore,
    page: str,
    sections: list[sqlite3.Row],
    scope: str,
    axis_rank: float | None,
) -> list[dict[str, Any]]:
    """The passages one page is read over (R1, R2, R7).

    `placement` and `corpus` read their sections exactly as today. `all`
    reads the union -- the page's prose sections, its lead and its declared
    narrative fact values -- and the lead / fact passages carry the page's
    store-axis rank (R3) where the page sits on the axis, else the in-value
    ordinal: the lead opens the page, the fact values follow in in-value
    order.
    """
    passages = [_section_passage(section) for section in sections]
    if scope != "all":
        return passages
    ordinal = 0.0
    lead = lead_passage(store, page)
    if lead is not None:
        lead["rank"] = axis_rank if axis_rank is not None else ordinal
        passages.append(lead)
        ordinal += 1.0
    for fact in fact_passages(store, page):
        fact["rank"] = axis_rank if axis_rank is not None else ordinal
        passages.append(fact)
        ordinal += 1.0
    return passages


def _store_axis_ranks(store: FactStore) -> dict[str, float]:
    """The store time axis' page -> rank (R3): the fallback every lead and
    fact passage inherits. A wiki that declares no axis sees `{}`, which is
    the rev-1 in-value-ordinal rule standing alone."""
    from scriptengine.ingest.timeaxis import store_time_axis

    ranks: dict[str, float] = {}
    for page, axis in store_time_axis(store).pages.items():
        if axis.index is not None:
            ranks[page] = float(axis.index)
    return ranks


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
    two or more of the wiki's characters); `all` reads the union of the two
    plus the R1 prose scope -- every prose section of every page type,
    heading-agnostic (R1 applies to page types as well as headings: an
    episode, location, organization or character page states story too) --
    and the R10 fact scope: a page whose declared narrative fact values hold a
    panel-eligible sentence joins the queue even when it has no prose section
    at all (`fact_pages`), so a story that lives only in a `history` /
    `synopsis*` value is read, not skipped. A page several rules cover reads
    the union of its sections, deduped.

    The union exists because the rules can be disjoint: on JJK no placement
    section satisfies the corpus rule, so a corpus-only re-extract would
    silently stop reading the 388 sections (165,941 words) that hold all 714
    placed events -- the scope-shrink check in reports/comprehension/GATE.md.
    The fact scope is a no-op for a wiki that declares no narrative fact keys
    (JJK, CSM), so their `all` page list is unchanged.
    """
    placement = placement_pages(store)
    corpus = corpus_scope(store) if scope in ("corpus", "all") else {}
    prose_pages, prose_by_page = prose_scope(store) if scope == "all" else ([], {})
    # R10: the pages a declared narrative fact value reaches. A fact-only page
    # (no prose section) is in no other rule's queue, so only this reaches it.
    fact_page_list = fact_pages(store) if scope == "all" else []
    if scope == "placement":
        pages = list(placement)
    elif scope == "corpus":
        pages = list(corpus)
    else:
        seen = set(placement)
        pages = list(placement) + [p for p in corpus if p not in seen]
        seen.update(pages)
        pages += [p for p in prose_pages if p not in seen]
        seen.update(pages)
        pages += [p for p in fact_page_list if p not in seen]

    base_pages = set(placement) if scope in ("placement", "all") else set()
    by_page: dict[str, list[sqlite3.Row]] = {}
    for page in pages:
        # Order: the page's own extractable sections first, then the corpus
        # rule, then the R1 prose sections; a section several rules name is
        # read once (deduped by id across all three, which the old two-rule
        # merge could not need).
        parts: list[list[sqlite3.Row]] = []
        if page in base_pages:
            parts.append(extractable_sections(store, page))
        if scope in ("corpus", "all"):
            parts.append(list(corpus.get(page, [])))
        if scope == "all":
            parts.append(list(prose_by_page.get(page, [])))
        merged: list[sqlite3.Row] = []
        seen_ids: set[int] = set()
        for part in parts:
            for section in part:
                section_id = int(section["id"])
                if section_id not in seen_ids:
                    seen_ids.add(section_id)
                    merged.append(section)
        by_page[page] = merged
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


_MOVEMENT_VERBS = {"arrived", "departed"}
_REFLEXIVE = re.compile(
    r"\b(himself|herself|itself|themselves|themself|oneself|own life)\b", re.I
)
_BY_ID: list[Any] = [None, {}, {}]

# A clause can refer to a handful of people it does not name ("they", "the
# group"); it cannot refer to a crowd. 2026-09-29 JJK pilot: "Yuji, Megumi and
# Nobara then enter the room" became 42 `met` rows pairing them with everyone
# the scene mentioned; the largest honest group reference in the whole .7
# corpus ("Master Tengen ... greeting the group") has 6 unnamed ends.
_FANOUT_UNNAMED = 6


def _named_in(quote: str, *names: str | None) -> bool:
    """Whether the quote names this end: its mention or its canonical name,
    whole, or any word of them (three letters or more)."""
    folded = quote.casefold()
    for name in names:
        name = (name or "").strip().casefold()
        if not name:
            continue
        if name in folded:
            return True
        for word in re.findall(r"[\w'-]+", name):
            if len(word) >= 3 and word not in {"the", "and"} \
                    and re.search(rf"\b{re.escape(word)}\b", folded):
                return True
    return False


def _fanout(found: list[dict[str, Any]]) -> set[int]:
    """The ids of the rows a fanned-out clause produced: within one (quote,
    verb), more than `_FANOUT_UNNAMED` distinct ends the quote does not name
    means the model paired the clause with the scene, not with what the
    clause says. Only the rows with an unnamed end go; a row whose two ends
    the quote names stands on its own."""
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in found:
        groups.setdefault((row["quote"], row["verb"]), []).append(row)
    out: set[int] = set()
    for rows in groups.values():
        unnamed = set()
        for row in rows:
            for role in ("subject", "object"):
                if not _named_in(row["quote"], row[f"{role}_mention"], row[f"{role}_name"]):
                    unnamed.add(row[f"{role}_name"])
        if len(unnamed) > _FANOUT_UNNAMED:
            out |= {
                id(row) for row in rows
                if not (_named_in(row["quote"], row["subject_mention"], row["subject_name"])
                        and _named_in(row["quote"], row["object_mention"], row["object_name"]))
            }
    return out


def name_pool(
    known: dict[str, list[tuple[int, str, str | None]]],
    mention: str,
    linked: set[int] | None,
    self_page: str | None = None,
) -> list[tuple[int, str, str | None]]:
    """The candidates a mention can resolve to: its folded name's pool, or --
    where the wiki has no page and no alias under that name -- the entities
    the page itself links whose title carries the mention as a word.

    The 2026-09-29 JJK pilot dropped 32% of proposals as unknown
    participants, and the top misses were characters the page links but
    the prose names by one part of the name ("Kiyotaka", "Chizuru",
    "Takako", "Itadori"). The page's link is the wiki's own answer for which
    Kiyotaka; the pool is still resolved by `pick_candidate`, so two linked
    Itadoris stay a counted ambiguity. The page's own entity (a subpage's
    base) joins the linked set: a page never links to itself, and "Chizuru"
    on Chizuru Hari's own page was the pilot's second-largest miss. Only a
    capitalised mention qualifies: "the curse" names no page."""
    pool = known.get(mention.lower(), [])
    words = mention.strip()
    if pool or len(words) < 3 or not words[0].isupper() \
            or words.split()[0].lower() in {"the", "a", "an"}:
        return pool
    if _BY_ID[0] is not known:
        _BY_ID[0] = known
        _BY_ID[1] = {c[0]: c for cands in known.values() for c in cands}
        _BY_ID[2] = {c[1].casefold(): c[0] for c in _BY_ID[1].values()}
    by_id, by_name = _BY_ID[1], _BY_ID[2]
    pointed = set(linked or ())
    own = (self_page or "").strip().casefold()
    # A subpage's subject is its base page: "Kiyotaka" on Kiyotaka Ijichi's
    # Synopsis names Kiyotaka Ijichi, never the Synopsis.
    base = own.split("/", 1)[0].strip()
    title = base if base in by_name else own
    if title in by_name:
        pointed.add(by_name[title])
    word = re.compile(rf"\b{re.escape(words)}\b", re.I)
    return [by_id[n] for n in sorted(pointed) if n in by_id and word.search(by_id[n][1])]


def extract_from_sections(
    client: LLMClient,
    series: str,
    page: str,
    passages: list[dict[str, Any]],
    known: dict[str, list[tuple[int, str, str | None]]],
    page_real: str | None = None,
    linked: set[int] | None = None,
    verbs: frozenset[str] = EVENTIVE_VERBS,
    place_nodes: set[int] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Events the page states, over its read passages.

    A passage is a wiki section (``kind="section"``, the row's own prose),
    the page lead (``kind="lead"``), or a declared narrative fact value
    (``kind="fact"``, ``passage="fact:<key>"``). Section passages carry the
    section's own ``time_rank``; lead and fact passages carry the page's
    axis rank, or their in-value ordinal where the page sits off the axis.

    `known` maps a folded name to its candidate nodes (P1); `page_real` is
    the page's reality, the signal that picks the variant; `linked` is the
    set of nodes the page itself links to, the wiki's pre-resolved wikilinks
    (architect 2026-09-28), which break an ambiguity the reality signal
    leaves: exactly one linked candidate is the wiki's own answer. A candidate no
    signal breaks is stored as an explicitly ambiguous participant -- the
    node goes NULL and the candidate list goes in the name field -- so the
    receipt can separate "the wiki has no such entity" from "the wiki has
    several and none is determined".

    The candidate pools carry the wiki's shape rules (2026-09-28): an exact
    title match wins over the name's `(qualifier)` and `/subpage` variants;
    a variant is a candidate only where the page links to it or is itself
    that variant; and the wiki's declared non-participants (its
    `events: participant_excludes:`, e.g. the mcu's `Hub:` index pages)
    plus disambiguation pages never appear in a pool.

    `known` is the set of names this wiki has resolved nodes for, resolved
    by the caller. Everything here is prompt-building, network and string
    work, so it is safe on a worker thread.

    The second return is the page's P3 accounting: candidates proposed,
    kept, and dropped by named reason, so a zero-event page is a number
    with a cause, not a silence.
    """
    sections = [p for p in passages if p["kind"] == "section"]
    ranks = section_time_ranks(
        [
            {**p, "id": p["id"]}
            for p in sections
        ]
    ) if sections else {}
    for p in passages:
        if p["kind"] == "section":
            p["rank"] = ranks[int(p["id"])]
    found: list[dict[str, Any]] = []
    seen: set[tuple[str, object, str, object]] = set()
    stats: dict[str, Any] = {
        "proposed": 0,
        "kept": 0,
        "ambiguous": 0,
        "cross_reality": 0,
        "dropped": {
            "incomplete": 0,
            "verb": 0,
            "unknown_participant": 0,
            "unquoted": 0,
            "dedup": 0,
            "self_object": 0,
            "shape": 0,
            "fanout": 0,
        },
    }
    # The calls this page costs: one per window of each passage, or -- a page
    # whose passages together fit `_pack_chars()` (owner 2026-09-29: "smaller
    # pages can be read in whole") -- one call over all of them. Each answer
    # row is anchored to the passage that holds its quote, so a packed read
    # stores the same row shape as a per-passage one.
    readable = [p for p in passages if (p["text"] or "").strip()]
    pack = _pack_chars()
    units: list[tuple[str, str, list[dict[str, Any]]]] = []
    if (
        pack
        and len(readable) > 1
        and sum(len(p["text"].strip()) for p in readable) <= pack
    ):
        joined = "\n\n".join(
            f"[{(p['title'] or p['passage'] or 'lead').strip()}]\n{p['text'].strip()}"
            for p in readable
        )
        units.append((joined, "", readable))
    else:
        for passage in readable:
            for window in _windows(passage["text"].strip()):
                units.append(
                    (window, (passage["title"] or "").strip(), [passage])
                )
    system = system_prompt(verbs)

    def ask(unit: tuple[str, str, list[dict[str, Any]]]) -> str:
        # An empty reply is intermittent under batched decoding (2026-09-29
        # MCU shard: 22/1,000 pages "returned no content"; the same windows
        # replayed alone answered normally), so it is retried twice before the
        # page is failed. A truncation or an unreachable server is not retried.
        for attempt in range(3):
            try:
                return ask_once(unit)
            except LLMUnavailable as error:
                if "no content" not in str(error) or attempt == 2:
                    raise
        raise AssertionError("unreachable")

    def ask_once(unit: tuple[str, str, list[dict[str, Any]]]) -> str:
        window, section_title, _ = unit
        return client.complete(
            _TEMPLATE.format(
                series=series,
                page=page,
                section=section_title,
                passage=window,
            ),
            system=system,
            temperature=0.0,
            max_tokens=_answer_budget(),
            extra_body=_effort_body(),
        )

    # One huge page (Marvel's Henry McCoy: a 129k-char history value, ~35
    # windows) used to hold one slot for the whole run's tail while the
    # others idled (2026-09-29 model trials, council lever 9). Its windows
    # may now be asked concurrently; the answers are still read in window
    # order below, so the rows, dedup and accounting are the serial ones.
    window_workers = _window_workers()
    if window_workers > 1 and len(units) > 1:
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=window_workers) as pool:
            answers = list(pool.map(ask, units))
    else:
        answers = (ask(unit) for unit in units)
    for (window, section_title, holders), answer in zip(units, answers):
        _trace({
            "series": series, "page": page, "section": section_title,
            "holders": [
                {"kind": h["kind"], "id": h["id"], "passage": h["passage"]}
                for h in holders
            ],
            "window": window, "answer": answer,
            "prompt_version": PROMPT_VERSION,
            "model": getattr(getattr(client, "settings", None), "llm_model", None),
        })
        for entry in parse_events_response(answer):
            subject = str(entry.get("subject") or "").strip()
            verb = str(entry.get("verb") or "").strip().lower()
            object_ = str(entry.get("object") or "").strip()
            quote = str(entry.get("quote") or "").strip()
            stats["proposed"] += 1
            if not object_ and verb in _SELF_VERBS:
                object_ = subject
            if not subject or not object_:
                stats["dropped"]["incomplete"] += 1
                continue
            if verb not in verbs:
                stats["dropped"]["verb"] += 1
                continue
            # Both ends have to be somebody or somewhere this wiki actually
            # has a page for, or a model supplies a plausible name from the
            # series it has read and nothing in the row shows it.
            sub_pick = pick_candidate(
                name_pool(known, subject, linked, page), subject,
                page_real, linked, page,
            )
            obj_pick = pick_candidate(
                name_pool(known, object_, linked, page), object_,
                page_real, linked, page,
            )
            if sub_pick is None or obj_pick is None:
                stats["dropped"]["unknown_participant"] += 1
                logger.info(
                    "unknown participant %r/%r for %s",
                    subject, object_, page,
                )
                continue
            sub_id = None if isinstance(sub_pick, dict) else sub_pick[0]
            obj_id = None if isinstance(obj_pick, dict) else obj_pick[0]
            # G3 (2026-09-29 JJK verification): the prompt forbids a row
            # whose object is its own subject unless the act was
            # self-directed; the old corpus held 807 of them (29.4%), and
            # `.7` still writes a few ("Mei Mei captured Mei Mei"). Legal
            # only for a self verb, or a quote that says so -- and never for
            # a movement, whose object is a place.
            if (
                sub_id is not None and sub_id == obj_id
                and verb not in _SELF_VERBS
                and (verb in _MOVEMENT_VERBS or not _REFLEXIVE.search(quote))
            ):
                stats["dropped"]["self_object"] += 1
                continue
            # G4: a movement's object is a place or a group -- a node of one
            # of the wiki's declared `events: place_types:` (inert when the
            # wiki declares none). The JJK `.7` pilot: 23 of 34 movement rows
            # named a person ("Shoko Ieiri arrived Satoru Gojo").
            obj_ids = (
                {c[0] for c in obj_pick["ambiguous"]} if obj_id is None
                else {obj_id}
            )
            if (
                place_nodes is not None and verb in _MOVEMENT_VERBS
                and not obj_ids <= place_nodes
            ):
                stats["dropped"]["shape"] += 1
                continue
            # Self-directed events are real: Toji kills himself, Mahito
            # awakens. The gate allows subject == object and says so.
            passage = next(
                (h for h in holders
                 if _quoted_in(quote, (h["text"] or "").strip())),
                None,
            )
            if passage is None:
                stats["dropped"]["unquoted"] += 1
                logger.info("unquoted %s->%s for %s", verb, object_, page)
                continue
            label = passage["passage"]
            section_id = (
                int(passage["id"]) if passage["kind"] == "section" else None
            )

            def filed(pick):
                # (node_id_or_None, name, candidate_list_or_None)
                if isinstance(pick, dict):
                    names = " | ".join(sorted(c[1] for c in pick["ambiguous"]))
                    return None, names
                return pick[0], pick[1]

            sub_node, sub_name = filed(sub_pick)
            obj_node, obj_name = filed(obj_pick)
            ambiguous = (
                isinstance(sub_pick, dict) or isinstance(obj_pick, dict)
            )
            if ambiguous:
                stats["ambiguous"] += 1
            if (
                not ambiguous
                and page_real
                and sub_pick[2] is not None
                and sub_pick[2] != page_real
                and obj_pick[2] is not None
                and obj_pick[2] != page_real
            ):
                stats["cross_reality"] += 1
            key = (
                label,
                (sub_node if sub_node is not None else sub_name),
                verb,
                (obj_node if obj_node is not None else obj_name),
            )
            if key in seen:
                stats["dropped"]["dedup"] += 1
                continue
            seen.add(key)
            stats["kept"] += 1
            found.append(
                {
                    "subject_node": sub_node,
                    "subject_name": sub_name,
                    "object_node": obj_node,
                    "object_name": obj_name,
                    "subject_mention": subject,
                    "object_mention": object_,
                    "verb": verb,
                    "section_id": section_id,
                    "quote": quote,
                    "temporal": True,
                    "time_rank": passage["rank"],
                    "passage": label,
                }
            )
    dropped = _fanout(found)
    if dropped:
        stats["dropped"]["fanout"] += len(dropped)
        stats["kept"] -= len(dropped)
        found = [row for row in found if id(row) not in dropped]
    stats["read"] = sorted({p["passage"] for p in readable})
    return found, stats


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

    import json

    effort = os.environ.get("SCRIPTENGINE_EVENTS_REASONING_EFFORT", "low").strip()
    body: dict[str, Any] = {"reasoning_effort": effort} if effort else {}
    # A server whose thinking switch is not `reasoning_effort` (SGLang's
    # `chat_template_kwargs: {"enable_thinking": false}`, 2026-09-29 owner
    # trial of a thinking-off model) takes its fields as a JSON object here.
    # Unset, the request is byte-identical to before.
    extra = os.environ.get("SCRIPTENGINE_EVENTS_EXTRA_BODY", "").strip()
    if extra:
        body.update(json.loads(extra))
    return body or None


_TRACE_LOCK = threading.Lock()


def _trace(record: dict[str, Any]) -> None:
    """Append one model call -- the exact window the model read and its raw
    answer -- to `SCRIPTENGINE_EVENTS_TRACE` (a JSONL path; inert when
    unset, the request and the rows are unchanged either way).

    The store keeps only rows that survive the gates, anchored to whole
    sections, so it holds neither the input a row was read from (the model
    reads overlapping windows) nor the calls that answered no events: a
    training set built from the store alone has no exact inputs and no
    negatives (plan/JJK_STUDENT_TRAINING.md, 2026-09-29)."""
    import os

    path = os.environ.get("SCRIPTENGINE_EVENTS_TRACE", "").strip()
    if not path:
        return
    line = json.dumps(record, ensure_ascii=False)
    with _TRACE_LOCK, open(path, "a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def _window_workers() -> int:
    """How many of one page's window calls may be in flight at once; 1 =
    serial (the default, byte-for-byte the old loop)."""
    import os

    return max(1, int(os.environ.get("SCRIPTENGINE_EVENTS_WINDOW_WORKERS", "1") or 1))


def _pack_chars() -> int:
    """The largest page (total passage chars) read in one call; 0 = off.

    Off by default: a packed read is a different prompt, so it is adopted
    only on a row-set diff against the per-passage read (review R11)."""
    import os

    return int(os.environ.get("SCRIPTENGINE_EVENTS_PACK_CHARS", "0") or 0)


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
    page_filter: list[str] | None = None,
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
    wiki says about a character actually lives. `all` is the union of the two
    plus the R1 prose scope -- every prose section of every page type -- the
    complete-coverage path for a `--refresh` run. `page_filter`
    intersects the scope queue with a frozen slug list (the D6
    targeted-extraction flag); `None` leaves the native path untouched.
    """
    from concurrent.futures import ThreadPoolExecutor

    from scriptengine.ingest.abilities import _guarded

    settings = settings or get_settings()
    client = LLMClient(settings)
    if not client.available():
        raise LLMUnavailable(f"No model at {client.settings.llm_base_url}.")

    report = {
        "considered": 0, "extracted": 0, "cached": 0, "failed": 0, "events": 0,
        "dedup_dropped": 0,
        # P3: the rejection accounting, so a zero-event page is a number with
        # a cause, not a silence.
        "proposed": 0, "kept": 0, "ambiguous": 0, "cross_reality": 0,
        "dropped": {
            "incomplete": 0, "verb": 0, "unknown_participant": 0,
            "unquoted": 0, "dedup": 0, "self_object": 0, "shape": 0,
            "fanout": 0,
        },
    }
    with FactStore(paths.facts_db) as store:
        store.ensure_events()
        # Resolved here, on the thread that owns the connection, and handed to
        # the workers as plain dicts: the candidate set (P1), the page reality
        # that picks the variant, and the store-axis rank the lead and fact
        # passages inherit (R3).
        known = participant_candidates(store)
        default_real = _wiki_default_reality(store)
        pages, by_page = scope_plan(store, scope)
        real_by_page = page_realities(store, pages, default_real)
        axis_ranks = _store_axis_ranks(store)
        if page_filter is not None:
            allowed = set(page_filter)
            pages = [page for page in pages if page in allowed]
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

        # The wiki's pre-resolved wikilinks, for the pages this run reads:
        # exactly one linked candidate in an ambiguous set is the wiki's
        # own answer (architect 2026-09-28). One full scan, filtered to the
        # run's pages, so a `limit` run stays small.
        # Read on this thread (the store's), handed to the workers as a value.
        run_verbs = eventive_verbs(store)
        place_nodes = declared_place_nodes(store)
        linked_by_page: dict[str, set[int]] = {}
        if wanted:
            wanted_titles = set(wanted)
            for title, node_id in store.connection.execute(
                "SELECT c.doc_title, cn.node_id"
                " FROM chunk_nodes cn JOIN chunks c ON c.id = cn.chunk_id"
            ):
                if title in wanted_titles:
                    linked_by_page.setdefault(title, set()).add(int(node_id))

        def store_result(
            page: str, revid: str, found: list[dict[str, Any]],
            stats: dict[str, Any],
        ):
            stored, dedup_dropped = store.save_events(
                page, found,
                revid=int(revid) if revid.isdigit() else None,
                prompt_version=PROMPT_VERSION, model=settings.llm_model,
                read_passages=stats.get("read"),
            )
            report["extracted"] += 1
            report["events"] += stored
            report["dedup_dropped"] += dedup_dropped
            report["proposed"] += stats["proposed"]
            report["kept"] += stats["kept"]
            report["ambiguous"] += stats["ambiguous"]
            report["cross_reality"] += stats["cross_reality"]
            for key, n in stats["dropped"].items():
                report["dropped"][key] += n
            if progress is not None:
                progress(page, stored)

        if workers <= 1:
            for page, revid in todo:
                try:
                    passages = build_passages(
                        store, page, by_page[page], scope,
                        axis_ranks.get(page),
                    )
                    found, stats = extract_from_sections(
                        client, paths.name, page,
                        passages, known, real_by_page.get(page),
                        linked_by_page.get(page), run_verbs, place_nodes,
                    )
                except LLMUnavailable:
                    raise
                except Exception as error:  # noqa: BLE001 - one page must not stop the run
                    logger.warning("Events for %r failed: %s", page, error)
                    report["failed"] += 1
                    continue
                store_result(page, revid, found, stats)
            return report

        # A sliding window, not chunk-and-wait: the old loop mapped
        # `workers * 4` pages and waited for the slowest before starting the
        # next chunk, so one long page idled every other LLM slot (2026-09-29,
        # the full-scope run's throughput wall, review R11). Passages are
        # still built, and results still stored, on this thread -- the one
        # that owns the connection -- and each page's rows are the same; only
        # the order pages finish in changes.
        from concurrent.futures import FIRST_COMPLETED, wait

        def run(job):
            page, _, passages = job
            return extract_from_sections(
                client, paths.name, page, passages, known,
                real_by_page.get(page), linked_by_page.get(page), run_verbs,
                place_nodes,
            )

        guarded = _guarded(run)
        pending_pages = iter(todo)
        in_flight: dict[Any, tuple[str, str]] = {}
        with ThreadPoolExecutor(max_workers=workers) as pool:

            def submit_next() -> None:
                for page, revid in pending_pages:
                    job = (
                        page, revid,
                        build_passages(
                            store, page, by_page[page], scope,
                            axis_ranks.get(page),
                        ),
                    )
                    in_flight[pool.submit(guarded, job)] = (page, revid)
                    return

            # Two jobs per slot: a slot that finishes never waits on this
            # thread building the next page's passages.
            for _ in range(workers * 2):
                submit_next()
            while in_flight:
                done, _ = wait(in_flight, return_when=FIRST_COMPLETED)
                for future in done:
                    page, revid = in_flight.pop(future)
                    outcome = future.result()
                    if isinstance(outcome, BaseException):
                        if isinstance(outcome, LLMRateLimited):
                            for other in in_flight:
                                other.cancel()
                            raise outcome
                        logger.warning(
                            "Events for %r failed: %s", page, outcome
                        )
                        report["failed"] += 1
                    else:
                        found, stats = outcome
                        store_result(page, revid, found, stats)
                    submit_next()
    return report

# ── Verification pass (2026-09-29) ──────────────────────────────────────────
# A second, cheap read of each stored row: the quote in its passage, and one
# yes/no question. Measured on the 160-page Marvel sample (thinking off,
# COUNCIL_extraction_optimization_2026-09-29.md): the rows it confirms are
# ~95% correct, but it rejects about half the true rows, so the verdict is a
# confidence tier on the row (`verified` 1/0), never a filter.

VERIFY_PROMPT_VERSION = "verify-2026-09-29.1"

VERIFY_SYSTEM = """You check one extracted event against the passage it was taken from. Answer with one word: yes or no.
The quote is a clause from the passage shown; use the passage to tell whom a pronoun or group word (he, him, she, they, them, the team) refers to.
Say yes if the quote states that the SUBJECT did the VERB to the OBJECT, in that direction (the subject is the doer).
Say no only if: the roles are reversed (the object is the doer); the doer is not stated at all (a passive sentence with no "by ..." and no doer named); a different person or thing than the SUBJECT is the doer; the event is only planned, attempted, intended or hypothetical; or the verb does not fit what the quote says happened.
Verb meanings:
{defs}"""

_VERIFY_CONTEXT = 1800


def _row_passage_text(store: FactStore, row: sqlite3.Row) -> str:
    """The text a stored row was read from: its section, its declared fact
    value (the one holding the quote), or its page lead."""
    from scriptengine.ingest.wikitext import strip_markup

    passage = row["passage"] or ""
    if row["section_id"] is not None and not passage:
        hit = store.connection.execute(
            "SELECT text FROM sections WHERE id = ?", (row["section_id"],)
        ).fetchone()
        return (hit["text"] if hit else "") or ""
    if passage.startswith("fact:"):
        quote = (row["quote"] or "")[:60]
        for (value,) in store.connection.execute(
            "SELECT f.value FROM facts f JOIN nodes n ON n.id = f.node_id"
            " JOIN documents d ON d.id = n.document_id"
            " WHERE d.title = ? COLLATE NOCASE AND f.key = ?",
            (row["doc_title"], passage[5:]),
        ):
            text = strip_markup(value or "")
            if quote in text:
                return text
        return ""
    hit = store.connection.execute(
        "SELECT lead FROM documents WHERE title = ? COLLATE NOCASE",
        (row["doc_title"],),
    ).fetchone()
    return strip_markup((hit["lead"] if hit else "") or "")


def verify_events(
    paths: SeriesPaths,
    settings: Settings | None = None,
    workers: int = 8,
    limit: int | None = None,
    redo: bool = False,
) -> dict[str, int]:
    """Set `verified` on this series' event rows (NULL rows only, unless
    `redo`). The store is read and written on this thread; the model calls
    run on `workers` threads."""
    from concurrent.futures import ThreadPoolExecutor

    settings = settings or get_settings()
    client = LLMClient(settings, workdir=str(paths.root))
    tally = {"checked": 0, "yes": 0, "no": 0, "unanswered": 0, "no_passage": 0}
    with FactStore(paths.facts_db) as store:
        store.ensure_events()
        verbs = eventive_verbs(store)
        system = VERIFY_SYSTEM.format(defs="\n".join(
            f"- {verb}: {VERB_DEFINITIONS.get(verb, verb)}" for verb in sorted(verbs)
        ))
        where = "" if redo else " WHERE verified IS NULL"
        rows = store.connection.execute(
            "SELECT rowid AS rid, * FROM events" + where
            + " ORDER BY doc_title, passage, section_id"
            + (f" LIMIT {int(limit)}" if limit else "")
        ).fetchall()
        jobs = []
        for row in rows:
            text = _row_passage_text(store, row)
            at = text.find((row["quote"] or "")[:60])
            if at < 0:
                tally["no_passage"] += 1
                continue
            subject = row["subject_mention"] or row["subject_name"]
            object_ = row["object_mention"] or row["object_name"]
            jobs.append((row["rid"], (
                f"Passage:\n{text[max(0, at - _VERIFY_CONTEXT): at + _VERIFY_CONTEXT]}"
                f"\n\nQuote (from the passage): \"{row['quote']}\""
                f"\nEvent: SUBJECT={subject} VERB={row['verb']} OBJECT={object_}"
                "\nUsing the passage to tell who \"he\", \"they\" etc. are,"
                " does the quote state this event?"
            )))

        def ask(job):
            try:
                answer = client.complete(
                    job[1], system=system, temperature=0.0, max_tokens=4,
                    extra_body=_effort_body(),
                )
            except Exception:  # noqa: BLE001 - one row must not stop the pass
                return job[0], None
            answer = answer.strip().lower()
            if answer.startswith("yes"):
                return job[0], 1
            if answer.startswith("no"):
                return job[0], 0
            return job[0], None

        with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
            for start in range(0, len(jobs), 512):
                verdicts = list(pool.map(ask, jobs[start : start + 512]))
                for rid, verdict in verdicts:
                    tally["checked"] += 1
                    if verdict is None:
                        tally["unanswered"] += 1
                        continue
                    tally["yes" if verdict else "no"] += 1
                    store.connection.execute(
                        "UPDATE events SET verified = ? WHERE rowid = ?",
                        (verdict, rid),
                    )
                store.connection.commit()
    return tally
