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
from pathlib import Path

import yaml

from scriptengine.config import SeriesPaths, identity_fields
from scriptengine.eval import questions as Q
from scriptengine.ingest.crawler import load_manifest, sanitise_filename
from scriptengine.retrieve.abilities import collect_abilities
from scriptengine.retrieve import citations as cite
from scriptengine.retrieve.roster import MEMBER_CHARS, battle_relations, battles_in
from scriptengine.stores.facts import FactStore

PROV = "page-gen:"
PROSE = "prose:"

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
    # Marvel DB (plan MARVEL_100_PLAN.md C1): the alias cell keys are
    # `currentalias` (the live alias) and `aliases` (a newline list) -- the
    # roster shape, not a single value (a whole-cell gold would match none of
    # the members). `nicknames` and `spouses` are closed lists of the same
    # shape.
    "currentalias": ("aliases", "alias"),
    "aliases": ("aliases", "alias"),
    "nicknames": ("nicknames", "nickname"),
    "spouses": ("spouses", "spouse"),
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
    # Per-wiki map (R-7) ahead of the engine dict: a wiki whose infobox
    # vocabulary the shared IDENTITY_FIELDS does not name still gets its
    # questions from series/<name>/overrides.yaml, not silent fall-through.
    fields = {**IDENTITY_FIELDS, **identity_fields(overrides)}
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
        if key in fields:
            question = fields[key].format(name=title)
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
            # One unsplit cell: the declared roster (if any) holds the verified
            # member split, and its members are what the runtime serves -- a
            # gold of the whole cell would match none of them.
            if len(members) == 1:
                declared = _declared_list(overrides, title, plural)
                if declared and len(declared) > 1:
                    members = declared
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
    # The side cell can list several fighters that the store keeps
    # space-flattened (the wiki's own `<br/>` separators, lost on parse), so
    # the fighters never become markers on their own: a fighter line is any
    # abilities line the side cell names. Technique lines never do.
    side_folded = _fold(side)

    def is_marker(line: str) -> bool:
        fl = _fold(line)
        return any(
            fl == _fold(fighter) or (
                _fold(fighter).split() and _fold(fighter).split()[-1] == fl)
            for fighter in fighters
        ) or (len(fl) > 2 and fl in side_folded)

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

def _page_type_is_battle(store, title: str) -> bool:
    """True when the page is itself a battle (the store's own `page_type`)."""
    row = store.connection.execute(
        "SELECT page_type FROM documents WHERE title = ? COLLATE NOCASE", (title,)
    ).fetchone()
    return bool(row and row["page_type"] and "battle" in row["page_type"].lower())

def _page_type_is_episode(store, title: str) -> bool:
    """True when the page is an episode (the store's own `page_type`)."""
    row = store.connection.execute(
        "SELECT page_type FROM documents WHERE title = ? COLLATE NOCASE", (title,)
    ).fetchone()
    return bool(row and row["page_type"] and "episode" in row["page_type"].lower())

# The words a roster match phrase must not contain, because the shared router
# would parse them as a route keyword. JJK's battle pages record an `arc`
# field (router.py's `_FIELD_ASKERS`: "In which arc does X..."), so a
# JJK story-arc page title like "Fearsome Womb Arc" would land the route
# keyword in every generated match phrase built from it. The router only
# routes on `arc` where the wiki records `arc` facts (a wiki that records
# none never routes on the word -- router.py, _FIELD_ASKERS comment), so the
# ban is series data, not engine truth: a wiki where the words are ordinary
# names (Marvel's "Arc (Hellbent)", "Jeanne d'Arc", "Saga") declares
# `roster_route_words: []` in its override and the guard goes quiet there.
_ROUTE_WORDS_DEFAULT = ("arc", "saga")


def _route_words(overrides: dict | None) -> tuple[str, ...]:
    """The series' banned roster-phrase words (the override owns the list)."""
    words = (overrides or {}).get(
        "roster_route_words", list(_ROUTE_WORDS_DEFAULT))
    return tuple(str(w).lower() for w in words)


def _route_word_pattern(words: tuple[str, ...]):
    """None when the series bans no word (the guard is disabled there)."""
    if not words:
        return None
    return re.compile(r"\b(" + "|".join(re.escape(w) for w in words) + r")s?\b")


def _roster_phrase_safe(
    title: str, route_words: tuple[str, ...] = _ROUTE_WORDS_DEFAULT,
) -> bool:
    """False when the title would put a banned word into a roster match phrase.

    The guard (below) rejects any roster match phrase containing a banned
    route word; the roster phrases are built from the page title, so a
    story-arc page like "Fearsome Womb Arc" would always trip it. Its
    per-battle facts stay; only the 'every battle' set is withheld.
    """
    pattern = _route_word_pattern(route_words)
    if pattern is None:
        return True
    return not pattern.search(title.lower())

def _declared_battles(overrides, title: str) -> list[str] | None:
    """Members of the declared `<title> Battles` roster, or None.

    A wiki that keeps a closed battle category (JJK, OPM) declares it; the
    battles-in discovery matches on a fighter's alias and drags in fights the
    subject is only named in prose for (e.g. "Megumi Fushiguro vs. Aoi Todo"
    for Yuji Itadori). When the roster exists, its members are the
    authoritative closed set -- the OPM "declare the closed set from the
    category" rule.
    """
    from scriptengine.retrieve.roster import load_rosters

    for roster in load_rosters(overrides):
        if roster.subject.lower() != title.lower() or not roster.members:
            continue
        if "battle" in " ".join([roster.name, *roster.match]).lower():
            return list(roster.members)
    return None


def _declared_list(overrides, title: str, plural: str) -> list[str] | None:
    """Members of the declared `<title> <plural>` roster (aliases, affiliations),
    or None.

    A declaration is the verified closed set (it went through the structured
    pass). When the raw infobox cell is one unsplit string -- Kento Nanami's
    alias cell reads `7:3 Sorcerer (By Mahito) Nanamin (By Gojo and Yuji)`,
    two aliases with no newline or <br> between them -- the declaration is the
    only place the member split is recorded, and a gold of the whole cell
    matches no member the roster serves.
    """
    from scriptengine.retrieve.roster import load_rosters

    for roster in load_rosters(overrides):
        if roster.subject.lower() != title.lower() or not roster.members:
            continue
        if plural in " ".join([roster.name, *roster.match]).lower():
            return list(roster.members)
    return None

def _battle_builder(store, paths, title, aliases, overrides, wiki, out, verified):
    pairs = battle_relations(overrides)
    if not pairs:
        return
    episodes = cite.EpisodeIndex.from_store(store)

    if _page_type_is_battle(store, title):
        # A battle page's structured half is its own infobox, not the union of
        # every fight each of its fighters is in elsewhere: `_fighter_words`
        # reduces a fight title to a surname word ("Choso vs. Naoya Zenin" ->
        # "zenin") and over-matches the whole family's battles. The subject is
        # the fight itself, and a one-battle "every battle" set is degenerate,
        # so the set/roster is skipped for battle pages.
        battles: dict[str, str] = {title: title}   # battle title -> the name that matched
        own_battle = True
    elif _page_type_is_episode(store, title):
        # An episode's battles are the ones *depicted in it*, not the career
        # fights of the character the episode is named after: `battles_in` on
        # "Ryomen Sukuna" (Episode 1's own alias) returns Sukuna's entire
        # Culling-Game list and lands it in Episode 1's batch. Only a declared
        # `<title> Battles` roster is authoritative for an episode; with none,
        # its battles are prose-coverage (the "Battles & Events" section), not
        # structured gold, so the builder produces nothing for the fight.
        declared = _declared_battles(overrides, title)
        battles = {m: title for m in declared} if declared else {}
        own_battle = False
        if not battles:
            return
    else:
        # The character's battle pages name her by whichever of her names the
        # infobox side carries, so the union runs over the title and every alias.
        # A wiki may keep the fighter and the name her battles use on separate
        # pages (the JJK wiki files the Angel's fights under her host body,
        # Hana Kurusu); that bridge is declared per-wiki in `battle_aliases`,
        # never inferred.
        extra = ((overrides or {}).get("battle_aliases") or {}).get(title) or []
        battles = {}          # battle title -> the name that matched
        for name in [title, *aliases, *extra]:
            result = battles_in(store, episodes, name, MEMBER_CHARS, overrides)
            if result is None:
                continue
            for member in result.members:
                battles.setdefault(member.name, name)
        declared = _declared_battles(overrides, title)
        if declared:
            # The wiki's own closed battle category (declared) wins over a
            # battles-in discovery that over-matches on an alias.
            battles = {m: title for m in declared}
        if not battles:
            return
        own_battle = False

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

        if not own_battle:
            # Per-fighter technique spans belong to the fighters' own pages; a
            # battle page's subject is the fight, so it carries no kit question.
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
    if not own_battle and _roster_phrase_safe(title, _route_words(overrides)):
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

def _plural(word: str) -> str:
    if word.endswith("y") and len(word) > 2 and word[-2] not in "aeiou":
        return word[:-1] + "ies"
    if word.endswith("s"):
        return word
    return word + "s"


def _technique_builder(store, paths, title, aliases, overrides, wiki, out, verified):
    # Names come from the wiki's own `user`-edge filing; the extracted
    # `abilities` table is the fallback when the crawl file is absent.
    names: list[str] = []
    result = collect_abilities(paths, title, max_abilities=200)
    if result:
        names = [a["name"] for a in (result.get("abilities") or []) if a.get("name")]
    if not names:
        names = [row["name"] for row in store.abilities_of(title)
                 if (row["name"] or "").strip()]
    if not names:
        return  # empty: no roster, no question -- the prose pass owns it
    s = title.lower()
    out.rosters.append({
        "name": f"Every named technique of {title}",
        "match": [f"every named technique of {s}", f"every named cursed technique of {s}",
                  f"all the named techniques of {s}", f"{s}'s named techniques"],
        "subject": title,
        "members": names,
    })
    out.questions.append(_question(
        f"What are all the named techniques of {title}?", "set", title, names,
        wiki, title, "page-gen:techniques", verified, expect_mode="roster"))


# Directional relations and their inverse. A stored row (A, B, mentor) means A
# mentors B, so B is A's student: "Every mentor of X" lists X's mentors (the A's
# in (A, X, mentor)) and "Every student of X" lists X's students (the B's in
# (X, B, mentor)). Symmetric relations have no inverse and map to themselves.
_RELATION_INVERSE = {
    "mentor": "student", "student": "mentor",
    "superior": "subordinate", "subordinate": "superior",
    "creator": "creation", "creation": "creator",
}


def _relation_members(label: str, title: str, rows) -> list[str]:
    """The people who are `label` to `title`, reading the correct side.

    A row (character, other, rel) says `character` is `rel` to `other`. So `Y`
    is `label` to `title` when there is a row (Y, title, label), or -- for a
    directional label -- a row (title, Y, inverse(label)). Grouping by label and
    taking the counterpart (the old code) mixed both sides: "Every mentor of
    Gojo" listed his students, because (Gojo, Yuji, mentor) was read as "Yuji is
    Gojo's mentor".
    """
    inverse = _RELATION_INVERSE.get(label, label)
    symmetric = inverse == label
    members: list[str] = []
    for row in rows:
        rel = (row["relation"] or "").strip().lower()
        character = (row["character"] or "").strip()
        other = (row["other"] or "").strip()
        if rel == label:
            if other.lower() == title.lower():
                candidate = character          # (Y, title, label): Y is label to title
            elif symmetric and character.lower() == title.lower():
                candidate = other              # (title, Y, label), symmetric
            else:
                continue
        elif rel == inverse:
            if character.lower() == title.lower():
                candidate = other              # (title, Y, inverse): Y is label to title
            else:
                continue
        else:
            continue
        if not candidate or candidate.lower() == title.lower():
            continue  # never a member of its own roster
        if candidate not in members:
            members.append(candidate)
    return members


def _relations_builder(store, paths, title, aliases, overrides, wiki, out, verified):
    rows = store.relations_of(title)
    # A mentor row feeds both the "mentor" and the "student" roster, so the
    # labels to emit are every relation present plus its inverse.
    labels: set[str] = set()
    for row in rows:
        relation = (row["relation"] or "").strip().lower()
        if relation:
            labels.add(relation)
            labels.add(_RELATION_INVERSE.get(relation, relation))
    for relation in sorted(labels):
        members = _relation_members(relation, title, rows)
        if len(members) < 2:
            continue  # a one-line relation is prose, not a closed set
        s = title.lower()
        out.rosters.append({
            "name": f"Every {relation} of {title}",
            "match": [f"every {relation} of {s}", f"all the {_plural(relation)} of {s}"],
            "subject": title,
            "members": members,
        })
        out.questions.append(_question(
            f"What are all the {_plural(relation)} of {title}?", "set", title, members,
            wiki, title, f"page-gen:relation:{relation}", verified, expect_mode="roster"))


_BUILDERS = (_identity_builder, _battle_builder, _technique_builder, _relations_builder)

# Section headings that never carry prose: the ledger retires them with a
# reason instead of leaving them as prose-pass targets.
_NON_PROSE_HEADINGS = {
    "references", "navigation", "site navigation", "external links",
    "see also", "gallery",
}

def _battle_search_phrases(store, battle, overrides, char_names: set[str]) -> list[str]:
    """What to search the page's sections for, to find the one that narrates `battle`.

    The battle title and the sides' own words, minus the character's names:
    her own name sits in every section and would point at `Appearance`
    instead of the synopsis beat that tells the fight.
    """
    pairs = battle_relations(overrides)
    facts = {
        (row["key"] or "").lower(): (row["value"] or "").strip()
        for row in store.facts_for(battle)
    }
    raw = [battle]
    for side, abilities in pairs:
        for key in (side, abilities):
            raw.extend(_split_list(facts.get(key, "")))
    phrases: list[str] = []
    for phrase in raw:
        folded = _fold(phrase)
        if not folded or folded in phrases and phrase in phrases:
            continue
        if folded in char_names:
            continue
        # a bare word that is part of a longer character name ("hana" in
        # "hana kurusu") names the character, not an opponent
        if " " not in folded and any(folded in cn for cn in char_names):
            continue
        phrases.append(folded)
    return phrases

def _coverage(store, paths, title, aliases, overrides, out, extra_sections):
    """The section-coverage ledger: where each generated question confirms on
    the page, what the prose pass still owns, and what is retired with a reason."""
    section_rows = [
        (row["breadcrumb"] or row["title"] or "", (row["text"] or ""))
        for row in store.document_sections(title)
    ]
    section_paths = [path for path, _ in section_rows]
    all_paths = ["lead", "infobox", *section_paths]

    covered: dict[str, list[str]] = {}

    def add_cover(path: str, *notes: str) -> None:
        bucket = covered.setdefault(path, [])
        for note in notes:
            if note and note not in bucket:
                bucket.append(note)

    # 1. The virtual rows. `infobox` is covered by the identity and list-field
    # questions; `lead` when the page has a lead with words.
    if store.document_lead(title).strip():
        add_cover("lead", "page-gen:lead")
    add_cover(
        "infobox",
        *[q["note"] for q in out.questions
          if q["note"].startswith(("page-gen:identity:", "page-gen:alias",
                                   "page-gen:affiliation", "page-gen:battles"))],
    )

    # 2. A battle's questions confirm on the first section (page order) that
    # mentions the fight or an opponent; a fight the page never narrates
    # confirms on its own battle page, which the question's `sources` name.
    char_names = {_fold(title), *(_fold(a) for a in aliases if a)}
    battle_titles: list[str] = []
    for q in out.questions:
        note = q["note"]
        if note.startswith("page-gen:battle:"):
            battle = note[len("page-gen:battle:"):].rsplit(":", 1)[0]
            if battle not in battle_titles:
                battle_titles.append(battle)
    for battle in sorted(battle_titles):
        notes = [q["note"] for q in out.questions
                 if q["note"].startswith(f"page-gen:battle:{battle}:")]
        if not notes:
            continue
        phrases = _battle_search_phrases(store, battle, overrides, char_names)
        for path, text in section_rows:
            if any(p in _fold(text) for p in phrases):
                add_cover(path, *notes)
                break

    # 3. The named-technique set confirms on the first abilities/technique section.
    if any(q["note"] == "page-gen:techniques" for q in out.questions):
        for path, _ in section_rows:
            folded = path.lower()
            if "cursed technique" in folded or "abilities" in folded:
                add_cover(path, "page-gen:techniques")
                break

    # 5. Non-prose sections retire with a reason, not silence.
    retired = [
        {"path": path, "reason": f"no prose: {path.split('/')[-1].lower()}"}
        for path in section_paths
        if path.split("/")[-1].lower() in _NON_PROSE_HEADINGS
    ]
    retired_paths = {row["path"] for row in retired}

    # 6. Prose-pass registrations: sections the reader covered, by section path.
    for path, questions in (extra_sections or {}).items():
        add_cover(path, *[str(q.get("note") or q.get("id") or "prose") for q in questions])

    # 7. Everything left is the prose scaffold.
    covered_paths = {p for p in all_paths if covered.get(p)}
    uncovered = [p for p in all_paths if p not in covered_paths and p not in retired_paths]

    out.coverage = {
        "sections": [{"path": p, "covered_by": covered.get(p, [])} for p in all_paths],
        "uncovered": uncovered,
        "retired_sections": retired,
    }

# House style fronts a wh-question with a preposition ("In which manga
# chapter does..."), so the guard reads the first *content* word.
_LEAD_PREPS = ("in", "on", "at", "by", "to")
_WH_WORDS = {"what", "which", "who", "where", "when", "how"}
_SET_LEADS = {"every", "what", "which"}   # set questions: "Every battle involving..."


def route_safe(question_text: str, kind: str = "fact") -> list[str]:
    """The routing-trap audit as a function. Empty means the question is clean.

    Set questions open with `Every`/`What are all the`; fact questions with a
    wh-word (possibly preposition-fronted). Both forbid `Whom`, `in order to`,
    `how many`, and an `According to X` lead.
    """
    text = (question_text or "").strip()
    low = text.lower()
    words = low.split()
    violations: list[str] = []
    if low.startswith("according to"):
        violations.append("according-to")
    content = words[1] if len(words) > 1 and words[0] in _LEAD_PREPS else (
        words[0] if words else "")
    if content == "whom":
        violations.append("whom")
    elif content not in (_WH_WORDS if kind != "set" else _SET_LEADS):
        violations.append("wh-word")
    if "in order to" in low:
        violations.append("in order to")
    if "how many" in low:
        violations.append("how many")
    return violations


def _verify(out: PageGenOutput) -> None:
    """One sheet row per generated question: what it is, its source field, the
    verbatim page span, and where the page confirms it."""
    note_to_section: dict[str, str] = {}
    for section in out.coverage.get("sections", []):
        for note in section.get("covered_by", []):
            note_to_section[note] = section["path"]
    rows: list[dict] = []
    for q in out.questions:
        note = q.get("note", "")
        key = note[len(PROV):] if note.startswith(PROV) else note
        items = [a["item"] for a in q.get("answer", [])]
        rows.append({
            "question": q["question"],
            "kind": q["kind"],
            "answer": items,
            "source": key,
            "page_span": ", ".join(items),
            "section": note_to_section.get(note, ""),
        })
    out.verify = rows


def _guard(
    out: PageGenOutput,
    route_words: tuple[str, ...] = _ROUTE_WORDS_DEFAULT,
) -> None:
    """The generator cannot emit a trap question or a trap match phrase."""
    problems: list[str] = []
    for q in out.questions:
        for violation in route_safe(q["question"], q.get("kind", "fact")):
            problems.append(f"{q.get('note', '?')}: {violation} in {q['question']!r}")
    pattern = _route_word_pattern(route_words)
    if pattern is not None:
        for roster in out.rosters:
            for phrase in roster.get("match", []):
                if pattern.search(phrase.lower()):
                    problems.append(
                        f"roster {roster['name']!r}: banned route word in match "
                        f"phrase {phrase!r}")
    if problems:
        raise PageGenError(
            "route-unsafe generated material:\n" + "\n".join(problems))

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

def wiki_base(paths: SeriesPaths, title: str) -> str:
    """The wiki's base URL: the manifest's own record, else the crawl's source."""
    manifest = load_manifest(paths)
    wiki = (manifest.get("wiki") or "").rstrip("/")
    if not wiki:
        crawl = paths.wikitext / f"{sanitise_filename(title)}.json"
        if crawl.exists():
            url = json.loads(crawl.read_text(encoding="utf-8")).get("url", "")
            wiki = url.split("/wiki/")[0] if "/wiki/" in url else ""
    if not wiki:
        raise PageGenError(f"no wiki base for {paths.name!r}: the manifest carries none")
    return wiki

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

        wiki = wiki_base(paths, title)

        out = PageGenOutput()
        verified = date.today().isoformat()
        aliases = _aliases_of(store, paths, title)
        for builder in _BUILDERS:
            builder(store, paths, title, aliases, overrides, wiki, out, verified)
        _coverage(store, paths, title, aliases, overrides, out, extra_sections)
        _verify(out)
        _guard(out, _route_words(overrides))
        return out
    finally:
        store.close()

def _norm_text(text: str) -> str:
    """The reconciliation fold: NFKD, lowercase, punctuation stripped."""
    text = unicodedata.normalize("NFKD", text or "").lower()
    return " ".join(re.sub(r"[^\w\s]", " ", text).split())

# Numbering order within a batch: identity first, then the per-battle block,
# techniques, relations, the list-field sets, and the battles set last.
_CLASS_ORDER = {
    "identity": 0, "battle": 1, "techniques": 2, "relation": 3,
    "alias": 4, "affiliation": 4, "battles": 5,
}

def _class_of(note: str) -> str:
    key = note[len(PROV):] if note.startswith(PROV) else ""
    return key.split(":", 1)[0]

def prose_extra_sections(batch: dict) -> dict:
    """Group the batch's prose-pass questions by section path.

    A re-run must see the prose the previous pass registered, or those
    sections stay `uncovered` in the ledger and the section-coverage gate can
    never pass: `note: "prose:<section-path>"` feeds `generate_structured`'s
    `extra_sections`, which the coverage ledger merges into `covered_by`.
    """
    extra: dict[str, list[dict]] = {}
    for q in (batch.get("questions") or []):
        note = str(q.get("note", ""))
        if note.startswith(PROSE):
            path = note[len(PROSE):].strip()
            if path:
                extra.setdefault(path, []).append(q)
    return extra

# The campaign's page tiers, by the store's own `page_type` (never a series
# name): characters get the full pipeline, the character-centric non-character
# pages get the structured half.
_TIER_TYPES: dict[str, tuple[str, ...]] = {
    "a": ("character",),
    "b": ("character_synopsis", "battle", "technique", "story_arcs", "event"),
}

def page_set(store, tier: str, include: list[str] | None = None) -> list[str]:
    """The campaign's page list for a tier.

    The store's `page_type` set, plus any explicitly included titles (the redos
    the store types `unknown`, which no tier filter reaches). Deduped, stable
    order.
    """
    types = _TIER_TYPES.get(tier)
    if not types:
        raise PageGenError(f"unknown tier {tier!r}: expected one of {sorted(_TIER_TYPES)}")
    placeholders = ",".join("?" * len(types))
    rows = store.connection.execute(
        f"SELECT title FROM documents WHERE page_type IN ({placeholders}) "
        "AND TRIM(title) <> '' ORDER BY title COLLATE NOCASE",
        types,
    ).fetchall()
    titles = [row["title"] for row in rows]
    seen = set(titles)
    for title in (include or []):
        title = (title or "").strip()
        if title and title not in seen:
            titles.append(title)
            seen.add(title)
    return titles

def run_page_gen(
    paths: SeriesPaths,
    page: str,
    overrides: dict | None,
    batch_path: Path,
    decl_path: Path,
    coverage_path: Path,
    verify_path: Path,
    no_prose_scaffold: bool = False,
) -> dict:
    """Generate `page`'s structured half and write the four campaign artifacts.

    Returns a per-page status dict for the sweep report (structured counts,
    rosters, retires, supersessions, uncovered sections). Raises
    `PageGenError` / `QuestionsError` on failure; the caller records or
    re-raises.
    """
    from scriptengine.eval import questions as Q  # noqa: F401  (validation lives in write_batch)

    batch_path = Path(batch_path)
    existing_batch = (
        json.loads(batch_path.read_text(encoding="utf-8-sig"))
        if batch_path.exists() else {})
    series = paths.name
    slug = slug_of(page)
    result = generate_structured(
        paths, page, overrides, None, prose_extra_sections(existing_batch))
    batch = write_batch(
        batch_path, series, slug, wiki_base(paths, page), result,
        existing=existing_batch)
    decl_path.write_text(
        render_decl(result, page, date.today().isoformat()), encoding="utf-8")
    if not no_prose_scaffold:
        coverage_path.write_text(
            json.dumps(result.coverage, indent=2, ensure_ascii=False),
            encoding="utf-8")
        verify_path.write_text(
            json.dumps(result.verify, indent=2, ensure_ascii=False),
            encoding="utf-8")

    generated = [q for q in batch["questions"]
                 if str(q.get("note", "")).startswith(PROV)]
    by_class: dict[str, int] = {}
    for question in generated:
        cls = question["note"].split(":", 2)[1]
        by_class[cls] = by_class.get(cls, 0) + 1
    return {
        "page": page,
        "structured": len(generated),
        "by_class": by_class,
        "rosters": len(result.rosters),
        "auto_retires": len(result.retires),
        "retires": result.retires,
        "hand_kept": len(batch["questions"]) - len(generated),
        "superseded": sum(
            1 for r in batch["retired"] if "superseded" in str(r.get("reason", ""))),
        "uncovered": list(result.coverage.get("uncovered") or [])
        if not no_prose_scaffold else [],
    }

def write_batch(
    batch_path: Path,
    series: str,
    slug: str,
    wiki: str,
    out: PageGenOutput,
    existing: dict | None = None,
) -> dict:
    """Merge the generated half into the campaign batch, idempotently.

    Hand-authored questions (no `page-gen:` marker in `note`) are never
    renumbered or dropped; a hand question duplicating a generated one is
    moved to `retired` as `superseded`, not clobbered. Generated rows take
    the lowest free ids. The serialized batch must pass `questions.validate`
    before the file is touched.
    """
    batch_path = Path(batch_path)
    existing_batch = existing
    if existing_batch is None:
        existing_batch = (
            json.loads(batch_path.read_text(encoding="utf-8-sig"))
            if batch_path.exists() else {}
        )
    kept_questions = [
        q for q in (existing_batch.get("questions") or [])
        if not str(q.get("note", "")).startswith(PROV)
    ]
    kept_retired = [
        r for r in (existing_batch.get("retired") or [])
        if not str(r.get("note", "")).startswith(PROV)
    ]

    decorated = sorted(
        enumerate(out.questions),
        key=lambda pair: (
            _CLASS_ORDER.get(_class_of(str(pair[1].get("note", ""))), 99),
            pair[0],
        ),
    )
    ordered = [q for _, q in decorated]

    gen_by_norm = {_norm_text(q["question"]): q for q in ordered}
    surviving: list[dict] = []
    superseded: list[dict] = []
    for q in kept_questions:
        gen = gen_by_norm.get(_norm_text(q.get("question", "")))
        if gen is not None:
            superseded.append({
                "id": q.get("id", ""),
                "item": "",
                "question": q.get("question", ""),
                "reason": f"superseded by {gen.get('note', PROV)} "
                          "(page-gen reconciliation)",
                "retired": True,
            })
        else:
            surviving.append(q)

    qid = re.compile(rf"^{re.escape(f'{series}-pg-{slug}-')}(\d+)$")
    used: set[int] = set()
    for row in [*surviving, *kept_retired]:
        match = qid.match(str(row.get("id", "")))
        if match:
            used.add(int(match.group(1)))
    next_num = 1
    for q in ordered:
        while next_num in used:
            next_num += 1
        q["id"] = f"{series}-pg-{slug}-{next_num:03d}"
        used.add(next_num)
        next_num += 1

    rid = re.compile(rf"^{re.escape(f'{series}-pg-{slug}-retired-')}(\d+)$")
    used_ret: set[int] = set()
    for row in kept_retired:
        match = rid.match(str(row.get("id", "")))
        if match:
            used_ret.add(int(match.group(1)))
    kept_keys = {
        (_norm_text(r.get("question", "")), str(r.get("item", "")))
        for r in kept_retired
    }
    gen_retired: list[dict] = []
    next_ret = 1
    for r in out.retires:
        # A hand-retire of the same (question, value) says more; keep it.
        if (_norm_text(r.get("question", "")), str(r.get("item", ""))) in kept_keys:
            continue
        while next_ret in used_ret:
            next_ret += 1
        r["id"] = f"{series}-pg-{slug}-retired-{next_ret:02d}"
        used_ret.add(next_ret)
        gen_retired.append(r)
        next_ret += 1

    batch = {
        "series": series,
        "wiki": wiki,
        "updated": date.today().isoformat(),
        "note": (
            f"page-gen {date.today().isoformat()}: {len(ordered)} structured "
            f"questions (note page-gen:-marked), {len(gen_retired)} auto-retires, "
            f"{len(surviving)} hand-authored kept, {len(superseded)} superseded"
        ),
        "retired": kept_retired + superseded + gen_retired,
        "questions": surviving + ordered,
    }

    payload = json.dumps(batch, ensure_ascii=False, indent=2)
    tmp = batch_path.with_name(batch_path.name + ".tmp")
    try:
        # G10 (Mei Mei Q001, 2026-08-27): the batch once stored a kanji answer
        # garbled -- `冥冥` as `å†¥å†¥`, UTF-8 bytes read as cp1252 in a path
        # that did not name its encoding -- and the question became
        # unanswerable by construction. The BOM marks the file self-describing
        # UTF-8, and the round-trip below proves the content made the trip
        # before the file becomes the batch.
        tmp.write_text(payload, encoding="utf-8-sig")
        assert json.loads(tmp.read_text(encoding="utf-8-sig")) == batch
        Q.validate([Q.load_file(tmp)])
        tmp.replace(batch_path)
    except Q.QuestionsError as exc:
        tmp.unlink(missing_ok=True)
        raise PageGenError(f"generated batch fails validation: {exc}") from exc
    return batch

# ── decl fragment + text-insert merge ────────────────────────────────────────
# The scalar/flow-list rendering is ported verbatim from the campaign's
# assembler (jjk_assemble.py): plain scalars stay bare, anything carrying a
# YAML-meaningful character is JSON-quoted so the fragment always parses.

def _needs_quote(s: str) -> bool:
    if s == "":
        return True
    if any(c in s for c in ":[],{}&*#!|>%@`\"'"):
        return True
    if s[0] in "-?" or s != s.strip():
        return True
    return False

def _q(s: str) -> str:
    return json.dumps(s, ensure_ascii=False) if _needs_quote(s) else s

def _flow_list(items) -> str:
    return "[" + ", ".join(_q(str(x)) for x in items) + "]"

def _roster_entry(roster: dict) -> list[str]:
    lines = [f"  - name: {_q(str(roster['name']))}"]
    if "match" in roster:
        lines.append(f"    match: {_flow_list(roster['match'])}")
    if "subject" in roster:
        lines.append(f"    subject: {_q(str(roster['subject']))}")
    if "members" in roster:
        lines.append(f"    members: {_flow_list(roster['members'])}")
    if "category" in roster:
        lines.append(f"    category: {_q(str(roster['category']))}")
    if "groups" in roster:
        lines.append(f"    groups: {_flow_list(roster['groups'])}")
    return lines

def _decl_block_lines(rosters: list[dict], header: str) -> list[str]:
    lines = []
    if header:
        lines.append(f"  {header.strip()}")
    for roster in rosters:
        lines.extend(_roster_entry(roster))
    return lines

def _decl_rosters(decl_path: Path) -> list[dict]:
    data = yaml.safe_load(Path(decl_path).read_text(encoding="utf-8"))
    if data is None:
        return []
    if isinstance(data, list):
        return data
    return data.get("rosters", []) or []

def render_decl(out: PageGenOutput, title: str, date: str) -> str:
    """The `decl.yaml` fragment: a `rosters:` top key with the generated rosters."""
    header = f"# ── page-gen: {title} ({date}) ──"
    lines = ["rosters:"] + _decl_block_lines(out.rosters, header)
    return "\n".join(lines) + "\n"

def _existing_roster_names(text: str) -> set[str]:
    data = yaml.safe_load(text)
    return {r.get("name") for r in ((data or {}).get("rosters") or [])}

def _insert_into_rosters(text: str, block_lines: list[str]) -> str:
    lines = text.split("\n")
    roster_idx = next((i for i, l in enumerate(lines) if re.match(r"^rosters:", l)), None)
    if roster_idx is None:
        if lines and lines[-1].strip():
            lines.append("")
        lines.extend(["rosters:"] + block_lines)
        return "\n".join(lines)
    next_top = next(
        (j for j in range(roster_idx + 1, len(lines))
         if re.match(r"^[A-Za-z_][\w-]*:", lines[j])),
        None)
    if next_top is not None:
        at = next_top
    else:
        at = len(lines)
        while at > roster_idx + 1 and lines[at - 1].strip() == "":
            at -= 1
    return "\n".join(lines[:at] + block_lines + lines[at:])

def merge_decl(decl_path: Path, overrides_path: Path, header: str) -> int:
    """Text-insert the decl's rosters into `overrides.yaml`'s `rosters:` block.

    String surgery only — the file is never YAML round-tripped, so house
    comments survive. Duplicates (by name) are skipped. The merged text is
    parsed and checked before it is written; a mismatch raises and leaves the
    file untouched.
    """
    decl_path = Path(decl_path)
    overrides_path = Path(overrides_path)
    original = overrides_path.read_text(encoding="utf-8")
    fresh = [r for r in _decl_rosters(decl_path)
             if r.get("name") not in _existing_roster_names(original)]
    if not fresh:
        return 0

    new_text = _insert_into_rosters(original, _decl_block_lines(fresh, header))

    before_names = _existing_roster_names(original)
    after = (yaml.safe_load(new_text) or {}).get("rosters") or []
    after_by_name = {r.get("name"): r for r in after}
    if not before_names.issubset(after_by_name):
        raise PageGenError("merge dropped a pre-existing roster; file left unchanged")
    for roster in fresh:
        got = after_by_name.get(roster.get("name"))
        if got is None:
            raise PageGenError(f"merged roster {roster.get('name')!r} is missing")
        if roster.get("members") and set(roster["members"]) != set(got.get("members") or []):
            raise PageGenError(f"merged roster {roster.get('name')!r} lost members")

    overrides_path.write_text(new_text, encoding="utf-8")
    return len(fresh)