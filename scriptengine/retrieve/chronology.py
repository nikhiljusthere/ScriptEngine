"""Story order, read out of the wiki's own arc chain.

"Every arc in order" returned nothing at all: it is set-shaped, so it reached
the roster path, which answered with the 84 chapters of a single arc. Order was
never something the engine could express.

It does not need a model to. Arc pages carry `previous` and `next` fields, and
that is a linked list:

    Amazon Lily Arc --next--> Impel Down Arc

Walked, restricted to arc pages, it reproduces canon exactly — One Piece from
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

Bleach has no arc pages at all — its arcs exist only inside episode titles — so
this declines there instead of inventing an order it cannot read.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from scriptengine.config import SeriesPaths
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

# One Piece stores the literal string `auto` — the wiki computes the range from
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
    # down a side branch and stops — 45 sagas became 21, with Cell and Buu
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
    # walked from wherever it starts — an answer of unknown phase beats none.
    seen = {part.lower() for chain in found for part in chain}
    for name in arcs:
        if name.lower() not in seen:
            chain = _walk(name, following)
            seen.update(part.lower() for part in chain)
            found.append(chain)

    # Chains can overlap where two arcs both lack a predecessor and rejoin —
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


def _counted(store: FactStore, arc: str, kind: str) -> str:
    """How many chapters or episodes the wiki files under this arc.

    One Piece writes `chapter = auto` and lets the template count the pages that
    link to the arc, so there is no range to read — but the category it files
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
# with the ordered list of arcs. Naming an arc is naming a subject — the thing
# a script gets written about — and asking for arcs is asking for the set.
_NAMES_AN_ARC = re.compile(r"\b(arc|saga)s\b", re.IGNORECASE)
_ASKS_FOR_ARCS = re.compile(
    r"\b(every|all|each|list|how many)\b[^.?!]{0,40}?\b(arc|saga)s?\b",
    re.IGNORECASE,
)


def build_chronology(paths: SeriesPaths, query: str, max_members: int = 200) -> Roster | None:
    """The story in order, or ``None`` where the wiki records no order.

    Members are built directly rather than through `_render_all`, which sorts —
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
                "reason": f"a separate run of {len(chain)} — filler or a spin-off",
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
    if any(word in lowered for word in ("in order", "chronolog", "timeline", "sequence")):
        return True
    # "Every arc of One Punch Man" is a list of arcs, and the useful list of
    # arcs is the ordered one. One arc by name is not a list of anything.
    return bool(_NAMES_AN_ARC.search(lowered) or _ASKS_FOR_ARCS.search(lowered))
