"""Story order, read out of the wiki's own arc chain.

"Every arc in order" returned nothing at all: it is set-shaped, so it reached
the roster path, which answered with the 84 chapters of a single arc. Order was
never something the engine could express.

It does not need a model to. Arc pages carry `previous` and `next` fields, and
that is a linked list:

    Amazon Lily Arc --next--> Impel Down Arc

Walked, restricted to arc pages, it reproduces canon exactly: One Piece from
Romance Dawn through Orange Town, Syrup Village, Baratie and Arlong Park; Dragon
Ball from Emperor Pilaf through Tournament and Red Ribbon Army.

**The restriction is the whole trick.** There are 4,847 `previous`/`next` edges
across these eight wikis and most of them join songs, volumes, Blu-rays,
popularity polls and Greed Island cards. `Ash Crow --next--> Berserk (2016)
Original Soundtrack` is one of them, and following it would turn a story
timeline into a discography.

**Several chains is the normal case, not a defect.** One Piece has seven heads
and Dragon Ball six; the short ones are anime filler (`Goat Island Arc`, `Boss
Luffy Historical Special`) and Super Dragon Ball Heroes (`Dark Demon Realm
Saga`). The longest chain is the story, and the rest are reported beside it
rather than mixed into it.

Bleach has no arc pages at all (its arcs exist only inside episode titles) so
this declines there instead of inventing an order it cannot read.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from scriptengine.config import SeriesPaths
from scriptengine.retrieve import citations as cite
from scriptengine.retrieve.roster import Member, Roster
from scriptengine.stores.facts import FactStore

# The relations that order one instalment against the next. `prev` and
# `previous` are the same field spelled two ways across wikis.
_ORDER_RELATIONS = ("next", "previous", "prev")

# Fields naming the chapters and episodes an arc covers. Matched on tokens
# because every wiki names them differently: `chapters`, `manga chapters`,
# `Manga Chapter(s)`, `Webcomic Chapter(s)`.
_CHAPTER_TOKENS = ("chapter",)
_EPISODE_TOKENS = ("episode",)
# Read past these rather than through them: a volume range is not a chapter
# range, and the webcomic numbering is a different work's.
_SPAN_SKIP = ("volume", "webcomic")

# One Piece stores the literal string `auto`, and the wiki computes the range from
# the chapters that link to the arc, so there is nothing to read.
_COMPUTED = {"auto", "", "n/a", "none"}


@dataclass
class Arc:
    """One instalment of the story, and where it sits."""

    name: str
    chapters: str = ""
    episodes: str = ""

    def span(self) -> str:
        parts = [part for part in (self.chapters, self.episodes) if part]
        return ", ".join(parts)


def arc_pages(store: FactStore) -> list[str]:
    """Every page the wiki types as an arc or a saga."""
    return [
        row["title"]
        for row in store.connection.execute(
            "SELECT title FROM documents"
            " WHERE LOWER(page_type) LIKE '%arc%' OR LOWER(page_type) LIKE '%saga%'"
            " ORDER BY title"
        )
    ]


def chains(store: FactStore) -> list[list[str]]:
    """Every ordered run of arcs, longest first.

    Only edges whose *both* ends are arc pages are followed, which is what keeps
    soundtracks and Greed Island cards out of a story timeline.
    """
    arcs = arc_pages(store)
    if not arcs:
        return []
    known = {name.lower(): name for name in arcs}

    placeholders = ",".join("?" * len(_ORDER_RELATIONS))
    rows = [
        (row["a"], (row["rel"] or "").lower(), row["b"])
        for row in store.connection.execute(
            f"SELECT s.name AS a, LOWER(e.relation) AS rel, t.name AS b FROM edges e"
            f" JOIN nodes s ON s.id = e.source_id"
            f" JOIN nodes t ON t.id = e.target_id"
            f" WHERE LOWER(e.relation) IN ({placeholders})",
            _ORDER_RELATIONS,
        )
        if row["a"].lower() in known and row["b"].lower() in known
    ]

    # `next` first and alone, then `previous` only where it fills a gap.
    # Folding both in together cost Dragon Ball two thirds of its story: a
    # backwards link inserted before the forward one wins, and the walk turns
    # down a side branch and stops: 45 sagas became 21, with Cell and Buu
    # stranded in fragments.
    following: dict[str, str] = {}
    for first, relation, second in rows:
        if relation == "next":
            following.setdefault(known[first.lower()], known[second.lower()])
    for first, relation, second in rows:
        if relation != "next":
            following.setdefault(known[second.lower()], known[first.lower()])

    preceded = {name.lower() for name in following.values()}

    found: list[list[str]] = []
    for name in arcs:
        if name.lower() not in preceded:
            found.append(_walk(name, following))
    # A cycle has no head, so nothing above reaches it. Anything still unseen is
    # walked from wherever it starts, since an answer of unknown phase beats none.
    seen = {part.lower() for chain in found for part in chain}
    for name in arcs:
        if name.lower() not in seen:
            chain = _walk(name, following)
            seen.update(part.lower() for part in chain)
            found.append(chain)

    # Chains can overlap where two arcs both lack a predecessor and rejoin,
    # Berserk reported `Black Swordsman Arc` as its own run *and* as part of the
    # main one. A run wholly inside a longer run is not a separate run.
    found.sort(key=len, reverse=True)
    kept: list[list[str]] = []
    covered: set[str] = set()
    for chain in found:
        members = {part.lower() for part in chain}
        if members <= covered:
            continue
        covered |= members
        kept.append(chain)
    return kept


def _walk(head: str, following: dict[str, str]) -> list[str]:
    """Follow `next` from one arc, stopping if the wiki links in a circle."""
    chain = [head]
    seen = {head.lower()}
    while chain[-1] in following:
        step = following[chain[-1]]
        if step.lower() in seen:
            break
        chain.append(step)
        seen.add(step.lower())
    return chain


def spans(store: FactStore, arc: str) -> tuple[str, str]:
    """The chapter and episode range this arc covers, as the wiki writes it."""
    chapters = episodes = ""
    for fact in store.facts_for(arc):
        label = (fact["label"] or fact["key"] or "").strip().lower()
        value = (fact["value"] or "").strip()
        if not value or value.lower() in _COMPUTED:
            continue
        if any(skip in label for skip in _SPAN_SKIP):
            continue
        if not chapters and any(token in label for token in _CHAPTER_TOKENS):
            chapters = value
        elif not episodes and any(token in label for token in _EPISODE_TOKENS):
            episodes = value
    if not chapters:
        chapters = _counted(store, arc, "Chapters")
    if not episodes:
        episodes = _counted(store, arc, "Episodes")
    return chapters, episodes


def heading(store: FactStore, arc: str) -> str:
    """The arc's section heading, in the shape a script writes it.

        Saitama Introduction Arc | MANGA CHAPTERS 1-4, EPISODE 1

    `spans` returns what the wiki wrote, which is correct and four different
    shapes. Measured across the One Punch Man and Jujutsu Kaisen arcs, the same
    range arrives as `30 • 31 • 32 • 33 • 34 • 35 • 36 • 37`, as
    `Chapter 52 - 65` with the kind word already in the value, as
    `21 - Ongoing`, and as `193 (Online)`. A heading has to read as speech, so
    the run is collapsed to its bounds and the doubled kind word removed.

    An open or unnumbered end is kept as the wiki wrote it -- `Episode 48 - TBA`
    becomes `EPISODES 48-TBA`, not a number the anime has not reached. Inventing
    an end is exactly the misrepresentation this heading exists to avoid.
    """
    chapters, episodes = spans(store, arc)
    parts = [
        _said(chapters, "MANGA CHAPTER"),
        _said(episodes, "EPISODE"),
    ]
    tail = ", ".join(part for part in parts if part)
    return f"{arc} | {tail}" if tail else arc


def _said(value: str, kind: str) -> str:
    """One span, as a heading says it. Empty when the wiki gives nothing."""
    body = (value or "").strip()
    if not body or body.lower() in _COMPUTED:
        return ""
    # A count is not a span. These wikis write both into the same field, and the
    # 2026-08-16 re-crawl changed `Shinjuku Showdown Arc` from `222-271` to
    # `50 chapters`, which rendered as `MANGA CHAPTER 50 chapters`: a heading
    # naming no chapter while looking like it names one. A writer cannot cite
    # that and cannot tell it from a real locator, which is the misrepresentation
    # this function already refuses when it declines to invent the end of an
    # open range.
    if re.fullmatch(r"\d+\s+(chapters?|episodes?|volumes?)", body, re.IGNORECASE):
        return ""
    # `Chapter 52 - 65` already carries the word; saying it twice reads as
    # "MANGA CHAPTERS Chapter 52 - 65".
    body = re.sub(r"^(chapter|episode)s?\s*", "", body, flags=re.IGNORECASE).strip()
    # `30 • 31 • 32 … 37` is a run, not a list of eight citations, and
    # `22 - 24, 30` is a range with a straggler. Both are one span in a heading.
    pieces = [piece.strip() for piece in re.split(r"[•,]", body) if piece.strip()]
    # A *spaced* hyphen separates two bounds; an unspaced one belongs to the
    # identifier. Jujutsu Kaisen's prequel chapters really are called `0-1` and
    # `0-4`, so splitting on every hyphen would turn one range into four.
    bounds = [b.strip() for b in re.split(r"\s+-\s+", pieces[0]) if b.strip()]
    first = bounds[0] if bounds else pieces[0]
    bounds = [b.strip() for b in re.split(r"\s+-\s+", pieces[-1]) if b.strip()]
    last = bounds[-1] if bounds else pieces[-1]

    if first == last:
        return f"{kind} {first}"
    # `0-1-0-4` cannot be read. When a bound carries its own hyphen, say the
    # range in words instead of running two identifiers together.
    joiner = " to " if "-" in first or "-" in last else "-"
    return f"{kind}S {first}{joiner}{last}"


@dataclass
class Appearance:
    """One character's part in one arc, with the heading a script writes."""

    arc: str
    heading: str
    passages: list[str]

    @property
    def words(self) -> int:
        return sum(len(passage.split()) for passage in self.passages)


def appearances(store: FactStore, character: str) -> list[Appearance]:
    """Which arcs this character appears in, in story order, with their part.

    The spine of a character-life script -- `The Entire Life of Killua Zoldyck`
    runs `Hunter Exam arc`, `Heavens Arena arc`, `Yorknew City arc`, one section
    per arc -- and it needs no inference at all. These wikis already file a
    character's history under arc-named headings: 1,093 chunks across the
    Jujutsu Kaisen pages, 1,859 across One Punch Man, with `Shibuya Incident
    Arc` appearing on 57 character pages.

    So this is a keyed read, ordered by the arc chain `chains()` already walks.
    Nothing here calls a model, which is what keeps a script's chronology the
    same on Tuesday as it was on Monday.
    """
    known = arc_pages(store)
    if not known:
        return []

    # Story order, from the wiki's own `previous`/`next` chain. Arcs the chain
    # does not reach keep their alphabetical position at the end rather than
    # being dropped -- an unlinked arc is still an arc the character was in.
    order: dict[str, int] = {}
    for chain in chains(store):
        for arc in chain:
            order.setdefault(arc, len(order))
    for arc in known:
        order.setdefault(arc, len(order))

    found: dict[str, list[str]] = {}
    for row in store.connection.execute(
        "SELECT c.breadcrumb, c.text, c.ordinal FROM chunks c"
        " JOIN documents d ON c.document_id = d.id"
        " WHERE d.title = ? COLLATE NOCASE OR d.title LIKE ? COLLATE NOCASE"
        " ORDER BY c.ordinal",
        (character, f"{character}/%"),
    ):
        breadcrumb = (row["breadcrumb"] or "").strip()
        text = (row["text"] or "").strip()
        if not breadcrumb or not text:
            continue
        parts = [part.strip() for part in breadcrumb.split("/")]
        for arc in parts:
            if arc in order:
                found.setdefault(arc, []).append(text)
                break

    out: list[Appearance] = []
    for arc in sorted(found, key=lambda name: order[name]):
        out.append(
            Appearance(arc=arc, heading=heading(store, arc),
                       passages=_undoubled(found[arc]))
        )
    return out


@dataclass
class Beat:
    """One run of prose and the locator covering it."""

    text: str
    locator: str = ""

    @property
    def words(self) -> int:
        return len(self.text.split())


@dataclass
class Scaffold:
    """One section of a character-life script, ready to be written from.

    Everything here is retrieved and citable. The writing is not done and is
    not this module's job: the engine's half is the checkable claim, and the
    voice sits on top of it.
    """

    character: str
    arc: str
    heading: str
    beats: list[Beat]
    abilities: list[str]
    relations: list[str]

    @property
    def words(self) -> int:
        return sum(beat.words for beat in self.beats)


def beats(text: str, episodes: "cite.EpisodeIndex | None" = None) -> list[Beat]:
    """Cut a passage where its citations change.

    A wiki puts one ref at the end of the passage it supports, so a run of
    sentences sharing a locator is a beat -- the same reading
    `citations.attribute` already applies, reused rather than reinvented.

    This is what a script wants. The Hero Hunt Arc comes back as 864 words in
    two chunks; the hand-written script cuts the same material into eleven
    beats, and re-cutting prose someone has already written is the tedious half
    of the job.
    """
    out: list[Beat] = []
    for sentence in cite.attribute(text or "", episodes):
        said = sentence.locator.render() if sentence.locator else ""
        body = _MARKER.sub("", sentence.text).strip()
        if not body:
            continue
        if out and out[-1].locator == said:
            out[-1].text = f"{out[-1].text} {body}".strip()
        else:
            out.append(Beat(text=body, locator=said))
    return out


# Refs are said in the locator, not repeated inside the prose.
_MARKER = re.compile(r"\((?:Chapter|Episode|Volume)[^)]*\)", re.IGNORECASE)


def scaffold(
    store: FactStore, character: str, arc: str, overrides: dict | None = None
) -> Scaffold | None:
    """The retrieved half of one arc section, for one character.

    Heading, beats with their locators, and the two things a writer reaches for
    next: what this character can do, and who they are to other people in this
    arc. Relations are filtered to the arc where they carry one -- Garou is
    `rival`, `enemy` and `ally` to Saitama, and only the last belongs to the
    Ominous Future.
    """
    found = next(
        (one for one in appearances(store, character) if one.arc == arc), None
    )
    if found is None:
        return None

    episodes = cite.EpisodeIndex.from_store(store)
    # `_undoubled` drops a passage wholly contained in another, but two cuts of
    # the same section can overlap without either containing the other -- and
    # then the second one's beats repeat the first one's tail, out of order.
    # Garou's Hero Hunt Arc came back with `target Sweet Mask` twice and
    # Chapter 49 after Chapter 50. Deduplicated on the prose, so the first
    # telling keeps its place.
    cut: list[Beat] = []
    seen: set[str] = set()
    for passage in found.passages:
        for beat in beats(passage, episodes):
            key = " ".join(beat.text.split())[:120].lower()
            if key in seen:
                continue
            seen.add(key)
            cut.append(beat)

    kit = [row["name"] for row in store.abilities_of(character)]
    ties: list[str] = []
    for row in store.relations_of(character):
        era = (row["era"] or "").strip()
        # An unscoped relation holds for the whole story, so it belongs to
        # every arc. One scoped elsewhere does not belong to this one.
        if era and era != arc:
            continue
        said = f"{row['character']} / {row['relation']} / {row['other']}"
        ties.append(f"{said} [{era}]" if era else said)

    return Scaffold(
        character=character, arc=arc, heading=found.heading, beats=cut,
        abilities=kit, relations=sorted(set(ties)),
    )


def cast(store: FactStore, arc: str, overrides: dict | None = None) -> list[str]:
    """Which characters this arc's story is written on, busiest first.

    The inverse of `appearances`, and it exists because the two wikis disagree
    about recording it: One Punch Man arcs carry 172 `characters` edges and
    Jujutsu Kaisen arcs carry none, so "who was in the Shibuya Incident" was
    answerable on one wiki and not the other. Reading it back off the character
    pages works on both, because both file history under arc-named headings.

    `mentions` is deliberately not consulted. There are 1,517 of them on the
    Jujutsu Kaisen arc pages, and being named in a paragraph is not being in the
    arc -- a script built on that would put the whole cast in every arc.
    """
    from scriptengine.retrieve import semantics as ontology

    counted: dict[str, int] = {}
    for row in store.connection.execute(
        "SELECT d.title, c.breadcrumb, LENGTH(c.text) AS weight FROM chunks c"
        " JOIN documents d ON c.document_id = d.id"
        " WHERE c.breadcrumb LIKE ? COLLATE NOCASE",
        (f"%{arc}%",),
    ):
        breadcrumb = (row["breadcrumb"] or "").strip()
        if arc not in [part.strip() for part in breadcrumb.split("/")]:
            continue
        page = (row["title"] or "").split("/")[0]
        if not page or page == arc:
            continue
        counted[page] = counted.get(page, 0) + int(row["weight"] or 0)

    return [
        page
        for page, _ in sorted(counted.items(), key=lambda kv: -kv[1])
        if ontology.semantic_type(store, page, overrides) == "character"
    ]


def _undoubled(passages: list[str]) -> list[str]:
    """Drop the copies the chunker makes of the same prose.

    A section is chunked at more than one level, so the level-1 card and the
    level-2 card under it carry the same sentences. Counted raw, Yuji's part in
    the Shibuya Incident reads as 7,190 words when the page holds about half
    that, and a script built on the doubled text would say everything twice.

    Compared on a normalised prefix rather than the whole string, because the
    two copies differ in trailing whitespace and in where the chunker cut them.
    """
    kept: list[str] = []
    seen: set[str] = set()
    for passage in passages:
        key = re.sub(r"\s+", " ", passage)[:160].lower()
        if key in seen:
            continue
        # A chunk wholly contained in one already kept is the shorter cut of it.
        if any(passage in longer for longer in kept):
            continue
        seen.add(key)
        kept.append(passage)
    return kept


def _counted(store: FactStore, arc: str, kind: str) -> str:
    """How many chapters or episodes the wiki files under this arc.

    One Piece writes `chapter = auto` and lets the template count the pages that
    link to the arc, so there is no range to read, but the category it files
    them under is populated (`Wano Country Arc Chapters` holds 149), and a count
    is a truer answer than the word "auto".
    """
    row = store.connection.execute(
        "SELECT COUNT(*) AS n FROM categories WHERE category = ? COLLATE NOCASE",
        (f"{arc} {kind}",),
    ).fetchone()
    total = int(row["n"] if row else 0)
    return f"{total} {kind.lower()}" if total else ""


# A *set* of arcs, which is what wants ordering. Plural on its own qualifies;
# the singular only when something asks for all of them.
#
# `\b(arc|saga)s?\b` was the whole test, and it made every topic that names an
# arc a chronology: `Fearsome Womb Arc` is one arc's story and was answered
# with the ordered list of arcs. Naming an arc is naming a subject, the thing
# a script gets written about, and asking for arcs is asking for the set.
_NAMES_AN_ARC = re.compile(r"\b(arc|saga)s\b", re.IGNORECASE)
_ASKS_FOR_ARCS = re.compile(
    r"\b(every|all|each|list|how many)\b[^.?!]{0,40}?\b(arc|saga)s?\b",
    re.IGNORECASE,
)

# Order cues at word boundaries (G8c, release R1): the previous test was a
# substring scan, so "consequences" -- which carries "sequence" inside it --
# sent a condition question down the order path to a roster that rendered
# nothing. One live hit in the bank (`jjk-pg-suguru_geto-073`); the family is
# latent corpus-wide in `consequence(s)`, `consequently` and `subsequent`.
# `in order` also fires on the purpose clause "in order to ...", which is not an
# ordering cue (found on the episode pass, Ep 2 `jjk-pg-episode_2-008`); the
# lookahead keeps "in order to" out while "in order" / "in order of" still match.
# Standalone `sequence` likewise is not an ordering cue: the episode pass found
# it naming common-noun segments ("the opening sequence", "the shikigami
# sequence", "the short sequence the anime adds", Ep 3/4/6), which sent
# descriptive Trivia questions down the order path. Only the ordering phrase
# `in sequence` / `in the sequence` still qualifies.
_CHRONOLOGY_CUES = re.compile(
    r"\b(?:in order\b(?! to)|chronolog\w*|timeline|in (?:the )?sequence)\b",
    re.IGNORECASE,
)


def build_chronology(paths: SeriesPaths, query: str, max_members: int = 200) -> Roster | None:
    """The story in order, or ``None`` where the wiki records no order.

    Members are built directly rather than through `_render_all`, which sorts,
    and sorting is the one thing that would destroy the only property this
    answer has.
    """
    with FactStore(paths.facts_db) as store:
        found = chains(store)
        if not found:
            return None
        main, rest = found[0], found[1:]
        if len(main) < 2:
            return None

        members: list[Member] = []
        for position, name in enumerate(main[:max_members], start=1):
            chapters, episodes = spans(store, name)
            arc = Arc(name=name, chapters=chapters, episodes=episodes)
            members.append(
                Member(
                    name=name,
                    group=f"{position}",
                    debut=arc.span(),
                    text=_lead(store, name),
                )
            )

        # The side chains, named rather than merged. A reader can see that
        # `Goat Island Arc` exists and was left out, which is a different thing
        # from it having been missed.
        rejected = [
            {
                "name": chain[0],
                "reason": f"a separate run of {len(chain)}: filler or a spin-off",
                "rule": "chronology",
            }
            for chain in rest
        ]

    return Roster(
        subject=paths.name,
        basis=f"{main[0]} → {main[-1]}",
        kind="chronology",
        members=members,
        confidence="exact" if len(main) > 2 else "partial",
        candidates=sum(len(chain) for chain in found),
        rejected=rejected,
        capped=len(main) if len(main) > max_members else 0,
    )


def _lead(store: FactStore, title: str, limit: int = 400) -> str:
    row = store.connection.execute(
        "SELECT lead FROM documents WHERE title = ? COLLATE NOCASE", (title,)
    ).fetchone()
    return ((row["lead"] if row else "") or "").strip()[:limit]


def wants_chronology(query: str) -> bool:
    """Whether a topic is asking for order rather than membership.

    Checked before the enumeration test, because "Every arc in order" is
    set-shaped and reaching the roster path is exactly what went wrong.
    """
    lowered = (query or "").lower()
    if _CHRONOLOGY_CUES.search(lowered):
        return True
    # "Every arc of One Punch Man" is a list of arcs, and the useful list of
    # arcs is the ordered one. One arc by name is not a list of anything.
    return bool(_NAMES_AN_ARC.search(lowered) or _ASKS_FOR_ARCS.search(lowered))


# A timeline or a chronology *of* something is that thing's own chain -- a set,
# rendered in order. "In order" alone is not: it modifies whatever was asked.
_TIMELINE_ASK = re.compile(r"\b(?:timeline|chronolog\w*)\b", re.IGNORECASE)


def wants_chronology_set(query: str) -> bool:
    """Whether an ordered ask wants *the set* in order, or one subject's story.

    R-8. `wants_chronology` answers "is order being asked for", and the router
    sent every yes to the roster door. That is right for "Every arc in order"
    and "Timeline of X" -- a list whose only useful property is its order -- and
    wrong for "What happened to Hirokazu Arai during the Eternity Devil arc, in
    order?", which is one character's beats inside one arc and is exactly what
    the narrative door is for. Hand-labelling the 21 CSM floor rows found the
    router correct on 13 and wrong on 8, every miss this one case
    (`reports/csm/floor_door_labels_vs_routed.json`).

    The split follows the distinction `_NAMES_AN_ARC` already draws: naming an
    arc names a subject, asking for arc*s* asks for the set. A bare `in order`
    cue carries no set on its own.
    """
    lowered = (query or "").lower()
    if _ASKS_FOR_ARCS.search(lowered) or _NAMES_AN_ARC.search(lowered):
        return True
    return bool(_TIMELINE_ASK.search(lowered))
