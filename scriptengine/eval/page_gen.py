"""page-gen: the deterministic structured half of a page-campaign batch.

The campaign's regular questions -- infobox identity, the per-battle
outcome/location/chapter/technique block, roster sets -- are a pure function
of `facts.db`: the fields are identical in shape across every page. This
module generates them with a provenance marker (`page-gen:<class>:<key>` in
`note`), emits the roster declarations, the section-coverage ledger and the
verify sheet, and merges its output into the one campaign batch without ever
touching a hand-authored question. Only the prose beats (battle "how",
synopsis, relationships, trivia) are left to a reader.
"""
from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date

from scriptengine.config import SeriesPaths
from scriptengine.ingest.crawler import load_manifest, sanitise_filename
from scriptengine.retrieve import citations as cite
from scriptengine.retrieve.roster import MEMBER_CHARS, battle_relations, battles_in
from scriptengine.stores.facts import FactStore

PROV = "page-gen:"

class PageGenError(Exception):
    """A page that cannot be generated: not crawled, not in the store, or a
    batch that would clobber a hand-authored question."""

@dataclass
class PageGenOutput:
    questions: list[dict] = field(default_factory=list)
    retires: list[dict] = field(default_factory=list)
    rosters: list[dict] = field(default_factory=list)
    coverage: dict = field(default_factory=dict)
    verify: list[dict] = field(default_factory=list)

# Field -> question. Keyed to the wiki's own infobox vocabulary (the fact
# keys), never to a series name: a wiki whose infobox calls a field `class`
# gets a "grade" question without the engine knowing which wiki it is.
IDENTITY_FIELDS: dict[str, str] = {
    "status": "What is the status of {name}?",
    "race": "What is {name}'s race?",
    "age": "How old is {name}?",
    "gender": "What is {name}'s gender?",
    "occupation": "What is {name}'s occupation?",
    "class": "What is {name}'s grade?",
    "debut": "In which manga chapter does {name} first appear?",
    "anime debut": "In which anime episode is {name} first depicted?",
    "debutanime": "In which anime episode is {name} first depicted?",
    "voice": "Who is {name}'s Japanese voice actor?",
    "eng voice": "Who is {name}'s English voice actor?",
    "creator": "Who created {name}?",
    "birthday": "What is {name}'s birthday?",
    "bloodtype": "What is {name}'s blood type?",
    "height": "What is {name}'s height?",
    "weight": "What is {name}'s weight?",
}

# Nihongo/Ruby shapes: the cell holds a script form the prose never repeats,
# so the value is not in any chunk and a gold would route to nothing. Golded
# only when chunked, else auto-retired (spec §8).
UNCHECKED_KEYS = frozenset({"kanji", "romaji", "japanese"})
UNCHECKED_QUESTIONS = {
    "kanji": "What are the kanji for {name}'s name?",
    "romaji": "What is the romaji of {name}'s name?",
    "japanese": "What is the Japanese spelling of {name}'s name?",
}

# `alias`/`affiliation` cells are lists. Split on newlines and the <br> the
# wiki writes between members; what is left is a closed set and a roster.
_LIST_SPLIT = re.compile(r"\n|<br\s*/?>", re.IGNORECASE)
LIST_FIELDS = {
    "alias": ("aliases", "alias"),
    "affiliation": ("affiliations", "affiliation"),
}

def slug_of(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")

def chunked(store: FactStore, value: str) -> bool:
    """True iff some chunk carries `value` -- the campaign's G3 check."""
    if not value:
        return False
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    row = store.connection.execute(
        "SELECT 1 FROM chunks WHERE text LIKE ? ESCAPE '\\' COLLATE NOCASE LIMIT 1",
        (f"%{escaped}%",),
    ).fetchone()
    return row is not None

def _question(
    question: str,
    kind: str,
    subject: str,
    golds: list[str],
    wiki: str,
    title: str,
    note: str,
    verified: str,
    expect_mode: str = "qa",
    extra_sources: tuple[str, ...] = (),
) -> dict:
    url = f"{wiki}/wiki/{title.replace(' ', '_')}"
    return {
        "id": "",
        "kind": kind,
        "question": question,
        "subject": subject,
        "tier": "wiki",
        "expect_mode": expect_mode,
        "scope": "closed",
        "answer": [{"item": g, "aliases": []} for g in golds],
        "sources": [url, *extra_sources],
        "verified": verified,
        "note": note,
    }

def _retire(out: PageGenOutput, question: str, value: str, reason: str, note: str) -> None:
    # Rows mirror the campaign's retired shape (id is numbered by write_batch);
    # the note is what `write_batch` uses to tell generated rows from hand rows.
    out.retires.append({
        "id": "",
        "item": value,
        "question": question,
        "reason": reason,
        "note": note,
        "retired": True,
    })

def _identity_builder(store, paths, title, aliases, overrides, wiki, out, verified):
    facts: dict[str, dict] = {}
    for row in store.facts_for(title):
        key = (row["key"] or "").lower()
        if key and key not in facts:
            facts[key] = row
    for key, row in facts.items():
        value = (row["value"] or "").strip()
        if key == "name":
            continue  # the name is the subject, not a question about it
        if key in UNCHECKED_KEYS:
            question = UNCHECKED_QUESTIONS[key].format(name=title)
            if not value:
                _retire(out, question, "", "field is empty on the page", f"{PROV}identity:{key}")
            elif not chunked(store, value):
                _retire(out, question, value,
                        "unchunked infobox cell (G3 Nihongo/Ruby shape)",
                        f"{PROV}identity:{key}")
            else:
                out.questions.append(_question(
                    question, "fact", title, [value], wiki, title,
                    f"{PROV}identity:{key}", verified))
            continue
        if key in IDENTITY_FIELDS:
            question = IDENTITY_FIELDS[key].format(name=title)
            if not value:
                _retire(out, question, "", "field is empty on the page", f"{PROV}identity:{key}")
            else:
                out.questions.append(_question(
                    question, "fact", title, [value], wiki, title,
                    f"{PROV}identity:{key}", verified))
            continue
        if key in LIST_FIELDS:
            plural, _ = LIST_FIELDS[key]
            members = [m.strip() for m in _LIST_SPLIT.split(value) if m.strip()] if value else []
            note = f"{PROV}{key}"
            if not members:
                _retire(out, f"What are all the {plural} of {title}?", "",
                        "field is empty on the page", note)
                continue
            s = title.lower()
            out.rosters.append({
                "name": f"{title}'s {plural}",
                "match": [f"all the {plural} of {s}", f"{plural} of {s}", f"{s}'s {plural}"],
                "subject": title,
                "members": members,
            })
            out.questions.append(_question(
                f"What are all the {plural} of {title}?", "set", title, members,
                wiki, title, note, verified, expect_mode="roster"))
            continue
        # Everything else (capabilities, hair, eye, ...) is prose: the ledger
        # leaves its section uncovered for the reader.

def _fold(value: str) -> str:
    return unicodedata.normalize("NFKC", value).lower()

# `Chapter 199 - 203` is a range: the campaign's precedent (Toji 014) asks for
# the start endpoint, not the span.
_CHAPTER_RANGE = re.compile(
    r"^\s*chapter\s+([\d.]+)\s*[-\u2013\u2014]\s*([\d.]+)\s*$", re.IGNORECASE)

def _split_list(value: str) -> list[str]:
    return [part.strip() for part in re.split(r"[\n,]", value) if part.strip()]

def _techniques_for(abilities: str, side: str, character: str) -> list[str]:
    """The technique lines under the character's marker.

    The wiki interleaves fighter lines with their technique lines in one cell
    (`Aoi Todo` newline `Boogie Woogie` newline `Arata Nitta` ...), so a
    fighter's kit is read as the lines under their own marker, in page order.
    Battle-scoped technique sets never close, so this is a fact, not a roster.
    """
    fighters = _split_list(side)
    lines = [line.strip() for line in abilities.splitlines() if line.strip()]

    def is_marker(line: str) -> bool:
        fl = _fold(line)
        return any(
            fl == _fold(fighter) or (
                _fold(fighter).split() and _fold(fighter).split()[-1] == fl)
            for fighter in fighters
        )

    char = _fold(character)
    char_last = char.split()[-1] if char.split() else ""
    techniques: list[str] = []
    under_character = False
    for line in lines:
        fl = _fold(line)
        if is_marker(line):
            under_character = fl == char or (bool(char_last) and char_last in fl)
            continue
        if under_character:
            techniques.append(line)
    return techniques

def _battle_builder(store, paths, title, aliases, overrides, wiki, out, verified):
    pairs = battle_relations(overrides)
    if not pairs:
        return
    episodes = cite.EpisodeIndex.from_store(store)

    # The character's battle pages name her by whichever of her names the
    # infobox side carries, so the union runs over the title and every alias.
    battles: dict[str, str] = {}          # battle title -> the name that matched
    for name in [title, *aliases]:
        result = battles_in(store, episodes, name, MEMBER_CHARS, overrides)
        if result is None:
            continue
        for member in result.members:
            battles.setdefault(member.name, name)
    if not battles:
        return

    # Store alias rows are lowercased; a crawl alias keeps its case. Show the
    # better-cased spelling in question text.
    display: dict[str, str] = {}
    for alias in sorted(aliases, key=lambda a: (a.islower(), a)):
        display.setdefault(_fold(alias), alias)

    def shown(name: str) -> str:
        if name == title:
            return title
        candidate = display.get(_fold(name))
        if candidate and not candidate.islower():
            return candidate
        return name.title()

    char_url = f"{wiki}/wiki/{title.replace(' ', '_')}"
    for battle in sorted(battles):
        matched = battles[battle]
        facts = {
            (row["key"] or "").lower(): (row["value"] or "").strip()
            for row in store.facts_for(battle)
        }
        battle_url = f"{wiki}/wiki/{battle.replace(' ', '_')}"

        # Which side (and abilities column) the character is on, off the
        # infobox's own words -- the owner-perspective the result is phrased from.
        words = [w for w in re.findall(r"[a-z']+", _fold(matched)) if len(w) > 3]
        word = words[-1] if words else _fold(matched)
        my_side = my_powers = ""
        for side, abilities in pairs:
            if (word and word in _fold(facts.get(side, ""))) or (
                    word and word in _fold(facts.get(abilities, ""))):
                my_side, my_powers = side, abilities
                break

        def emit(key: str, question: str, value: str) -> None:
            note = f"page-gen:battle:{battle}:{key}"
            if not value or not chunked(store, value):
                _retire(out, question, value,
                        f"value not chunked on any page (G3 shape) for {battle!r}",
                        note)
                return
            out.questions.append(_question(
                question, "fact", title, [value], wiki, title, note, verified,
                extra_sources=(battle_url,)))

        if facts.get("outcome"):
            emit("outcome", f"What is the outcome of {battle}?", facts["outcome"])
        if facts.get("place"):
            emit("place", f"Where did {battle} take place?", facts["place"])
        elif facts.get("event"):
            emit("event", f"Which event is {battle} part of?", facts["event"])
        if facts.get("date"):
            emit("date", f"When does {battle} take place?", facts["date"])
        if facts.get("chapters"):
            value = facts["chapters"]
            match = _CHAPTER_RANGE.match(value)
            if match:
                emit("chapters", f"In which manga chapter does {battle} begin?",
                     f"Chapter {match.group(1)}")
            else:
                emit("chapters", f"Which manga chapters cover {battle}?", value)
        if facts.get("episodes"):
            emit("episodes", f"In which episode is {battle} depicted?", facts["episodes"])
        if facts.get("arc"):
            emit("arc", f"In which arc does {battle} take place?", facts["arc"])

        techniques = (
            _techniques_for(facts.get(my_powers, ""), facts.get(my_side, ""), shown(matched))
            if my_powers else []
        )
        if techniques:
            question = f"Which techniques did {shown(matched)} use in {battle}?"
            if all(chunked(store, t) for t in techniques):
                out.questions.append(_question(
                    question, "fact", title, [", ".join(techniques)], wiki, title,
                    f"page-gen:battle:{battle}:techniques", verified,
                    extra_sources=(battle_url,)))
            else:
                _retire(out, question, ", ".join(techniques),
                        f"technique list not chunked on any page (G3 shape) for {battle!r}",
                        f"page-gen:battle:{battle}:techniques")

    battle_titles = sorted(battles)
    out.questions.append(_question(
        f"Every battle involving {title}", "set", title, battle_titles, wiki, title,
        "page-gen:battles", verified, expect_mode="roster",
        extra_sources=tuple(f"{wiki}/wiki/{b.replace(' ', '_')}" for b in battle_titles)))
    s = title.lower()
    out.rosters.append({
        "name": f"Every battle involving {title}",
        "match": [f"every battle involving {s}", f"all the battles involving {s}",
                  f"battles involving {s}", f"every battle of {s}"],
        "subject": title,
        "members": battle_titles,
    })

_BUILDERS = (_identity_builder, _battle_builder)

def _aliases_of(store: FactStore, paths: SeriesPaths, title: str) -> list[str]:
    """The page's alias rows plus the crawl's, best-effort.

    `battles_in` matches on a fighter's last content word, and a character's
    battle pages name her by the alias the page's own infobox carries, so the
    battle union has to be driven over every name, not just the title.
    """
    names: set[str] = set()
    node = store.node_by_name(title)
    if node is not None:
        for row in store.connection.execute(
            "SELECT alias FROM aliases WHERE node_id = ?", (node["id"],)
        ):
            names.add(row["alias"])
    crawl = paths.wikitext / f"{sanitise_filename(title)}.json"
    if crawl.exists():
        try:
            payload = json.loads(crawl.read_text(encoding="utf-8"))
            names.update(a for a in (payload.get("aliases") or []) if a)
        except (json.JSONDecodeError, OSError):
            pass  # best-effort: the store's alias rows stand alone
    return sorted(names)

def generate_structured(
    paths: SeriesPaths,
    title: str,
    overrides: dict | None = None,
    settings=None,
    extra_sections: dict | None = None,
) -> PageGenOutput:
    """The structured half of `title`'s campaign batch, straight from the store."""
    if not paths.facts_db.exists():
        raise PageGenError(f"no facts store for {paths.name!r} at {paths.facts_db}")
    store = FactStore(paths.facts_db)
    try:
        row = store.connection.execute(
            "SELECT 1 FROM documents WHERE title = ? COLLATE NOCASE", (title,)
        ).fetchone()
        if row is None:
            raise PageGenError(f"{title!r} is not in {paths.facts_db.name}: index the series first")

        manifest = load_manifest(paths)
        wiki = (manifest.get("wiki") or "").rstrip("/")
        if not wiki:
            crawl = paths.wikitext / f"{sanitise_filename(title)}.json"
            if crawl.exists():
                url = json.loads(crawl.read_text(encoding="utf-8")).get("url", "")
                wiki = url.split("/wiki/")[0] if "/wiki/" in url else ""
        if not wiki:
            raise PageGenError(f"no wiki base for {paths.name!r}: the manifest carries none")

        out = PageGenOutput()
        verified = date.today().isoformat()
        aliases = _aliases_of(store, paths, title)
        for builder in _BUILDERS:
            builder(store, paths, title, aliases, overrides, wiki, out, verified)
        return out
    finally:
        store.close()