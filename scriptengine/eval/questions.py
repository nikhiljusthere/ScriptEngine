"""The online-canon question bank: `questions/<series>.json`, loaded and checked.

The gold used to live as a Python literal inside `canon_gold.py`, with each
block's provenance surviving only as a `#` comment above it. That made the one
thing this measurement rests on -- where the answer came from -- unreadable to
everything except a human scrolling the file, and unextendable by anyone not
editing Python.

Here the answers are data. Every question names its sources and the tier they
sit in, and `validate()` refuses a bank that breaks the sourcing rules, so a
powerscaling wiki cannot quietly become the reason the engine is marked wrong.

The series list is discovered from the filenames rather than declared: a
`SERIES = (...)` tuple in a `.py` file is the per-series hardcoding this project
forbids, and `question_sheet.py` already carries one.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

# Absolute rather than relative, because `canon_gold.py` imports this and is
# still runnable as a bare script (`python scriptengine/eval/canon_gold.py`),
# where there is no package context for a relative import to resolve against.
# `diagnose_misses.py` next door resolves its imports the same way.
from scriptengine.config import Settings

# A source may sit in one of three tiers. `wiki` is the series' own Fandom wiki
# or official material; `editorial` is a bylined article; `community` is a
# forum, reddit or Q&A thread.
#
# A set question asserts *completeness*, and only the wiki maintains a complete
# list -- a ranked listicle routinely omits and invents entries -- so a set
# needs at least one `wiki` source. A fact asserts one thing and an editorial
# source can carry it alone.
TIERS = ("wiki", "editorial", "community")

# Never a source. These argue their entries rather than documenting them, which
# is the "speculation, not concrete answers" this bank exists to keep out. The
# previous gold sourced Meruem's abilities to vsbattles; that is a defect that
# was fixed during migration, not a precedent.
BLOCKED_DOMAINS = (
    "vsbattles",
    "vsbattlewiki",
    "powerscaling",
    "deathbattle",
    "fandom-powerscaling",
)

KINDS = ("set", "fact")


class QuestionsError(Exception):
    """A bank that cannot be trusted to score anything.

    Raised at load, and therefore at `canon_gold` import. That is deliberate:
    a malformed bank must stop a run rather than silently score fewer
    questions and report the smaller number as an improvement.
    """


@dataclass(frozen=True)
class AnswerItem:
    item: str
    aliases: tuple[str, ...] = ()
    sources: tuple[str, ...] = ()
    tier: str = ""

    def effective_tier(self, question_tier: str) -> str:
        return self.tier or question_tier

    def scored(self, question_tier: str) -> bool:
        """Whether a miss on this item may count against the engine.

        An item resting only on a forum post is not solid enough to mark the
        engine wrong. It stays in the bank -- it is still a real claim someone
        made, and worth revisiting -- but it is excluded from the score.
        """
        return self.effective_tier(question_tier) != "community"


@dataclass(frozen=True)
class Question:
    id: str
    series: str
    kind: str
    question: str
    subject: str
    answer: tuple[AnswerItem, ...]
    sources: tuple[str, ...]
    tier: str
    verified: str
    scope: str = "closed"
    expect_mode: str = ""
    absent: tuple[str, ...] = ()
    accept: str = "all"
    note: str = ""

    # One of the 36 questions migrated out of `canon_gold.py`'s inline literal.
    # The report scores these alone as a separate row, because they are the
    # only figure comparable to the 162/217 (74.7%) the old gold last recorded.
    # Without the flag the bank's growth would read as a collapse in the score.
    baseline: bool = False

    @property
    def recall_only(self) -> bool:
        """A curated core list, not the complete set the wiki keeps.

        Precision is meaningless on these: `Every technique Goku uses` names
        eight, and the Dragon Ball wiki really does record 194 techniques with
        Goku as a user, so a correct answer scores about 4% precision.
        """
        return self.scope == "core"

    def scored_items(self) -> tuple[AnswerItem, ...]:
        return tuple(i for i in self.answer if i.scored(self.tier))


@dataclass
class Bank:
    series: str
    path: Path
    wiki: str = ""
    updated: str = ""
    questions: list[Question] = field(default_factory=list)
    retired: list[dict] = field(default_factory=list)


def questions_root(settings: Settings | None = None) -> Path:
    """Resolved from settings, never from the current directory.

    `question_sheet.py`, `diagnose_misses.py` and `canon_gold.py` each resolve
    a path relative to the CWD, so all three only work when run from the repo
    root. That class of bug does not get another instance.
    """
    return (settings or Settings()).questions_root


def _blocked(url: str) -> str:
    low = url.lower()
    return next((d for d in BLOCKED_DOMAINS if d in low), "")


def _item(raw: dict | str, where: str) -> AnswerItem:
    if isinstance(raw, str):
        return AnswerItem(item=raw)
    name = (raw.get("item") or "").strip()
    if not name:
        raise QuestionsError(f"{where}: an answer entry has no 'item'")
    tier = raw.get("tier", "")
    if tier and tier not in TIERS:
        raise QuestionsError(f"{where}: item {name!r} has unknown tier {tier!r}")
    return AnswerItem(
        item=name,
        aliases=tuple(raw.get("aliases") or ()),
        sources=tuple(raw.get("sources") or ()),
        tier=tier,
    )


def _question(raw: dict, series: str, where: str) -> Question:
    qid = (raw.get("id") or "").strip()
    text = (raw.get("question") or "").strip()
    if not text:
        raise QuestionsError(f"{where}: a question has no 'question' text")
    if not qid:
        raise QuestionsError(f"{where}: question {text!r} has no 'id'")

    kind = raw.get("kind", "set")
    if kind not in KINDS:
        raise QuestionsError(f"{where}: {qid} has unknown kind {kind!r}")

    tier = raw.get("tier", "")
    if tier not in TIERS:
        raise QuestionsError(f"{where}: {qid} has unknown tier {tier!r}")

    sources = tuple(raw.get("sources") or ())
    if not sources:
        raise QuestionsError(f"{where}: {qid} names no sources")

    answer = tuple(_item(a, f"{where}:{qid}") for a in (raw.get("answer") or ()))
    if not answer:
        raise QuestionsError(f"{where}: {qid} asserts nothing")

    return Question(
        id=qid,
        series=series,
        kind=kind,
        question=text,
        subject=(raw.get("subject") or "").strip(),
        answer=answer,
        sources=sources,
        tier=tier,
        verified=(raw.get("verified") or "").strip(),
        scope=raw.get("scope", "closed"),
        expect_mode=raw.get("expect_mode", ""),
        absent=tuple(raw.get("absent") or ()),
        accept=raw.get("accept", "all"),
        note=raw.get("note", ""),
        baseline=bool(raw.get("baseline", False)),
    )


def load_bank(series: str, root: Path | None = None) -> Bank:
    path = (root or questions_root()) / f"{series}.json"
    if not path.exists():
        raise QuestionsError(f"no question bank for {series!r} at {path}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise QuestionsError(f"{path.name} is not valid JSON: {exc}") from exc

    declared = raw.get("series")
    if declared and declared != series:
        raise QuestionsError(
            f"{path.name} declares series {declared!r} but is filed as {series!r}"
        )

    bank = Bank(
        series=series,
        path=path,
        wiki=raw.get("wiki", ""),
        updated=raw.get("updated", ""),
        retired=list(raw.get("retired") or ()),
    )
    bank.questions = [
        _question(q, series, path.name) for q in (raw.get("questions") or ())
    ]
    return bank


def load_all(root: Path | None = None) -> list[Bank]:
    root = root or questions_root()
    if not root.exists():
        raise QuestionsError(f"no question bank at {root}")
    names = sorted(p.stem for p in root.glob("*.json") if not p.stem.startswith("_"))
    if not names:
        raise QuestionsError(f"{root} holds no question banks")
    banks = [load_bank(name, root) for name in names]
    validate(banks)
    return banks


def validate(banks: list[Bank]) -> None:
    """Refuse a bank that could produce a number nobody should trust."""
    seen_ids: dict[str, str] = {}
    for bank in banks:
        for q in bank.questions:
            if q.id in seen_ids:
                raise QuestionsError(
                    f"{bank.path.name}: id {q.id!r} already used in {seen_ids[q.id]}"
                )
            seen_ids[q.id] = bank.path.name

            if not q.subject:
                raise QuestionsError(f"{bank.path.name}: {q.id} names no subject")
            if not q.verified:
                raise QuestionsError(f"{bank.path.name}: {q.id} has no verified date")

            urls = list(q.sources) + [u for i in q.answer for u in i.sources]
            for url in urls:
                if not url.startswith(("http://", "https://")):
                    raise QuestionsError(
                        f"{bank.path.name}: {q.id} source {url!r} is not a URL"
                    )
                hit = _blocked(url)
                if hit:
                    raise QuestionsError(
                        f"{bank.path.name}: {q.id} cites {hit!r}, a banned source"
                    )

            # A set asserts completeness; only the wiki maintains a complete
            # list. An editorial ranking may corroborate one, never carry it.
            if q.kind == "set" and q.tier != "wiki":
                item_tiers = {i.tier for i in q.answer if i.tier}
                if "wiki" not in item_tiers:
                    raise QuestionsError(
                        f"{bank.path.name}: {q.id} is a set with no wiki source"
                    )

            if not q.scored_items():
                raise QuestionsError(
                    f"{bank.path.name}: {q.id} has no item solid enough to score"
                )


def sets(banks: list[Bank]) -> list[Question]:
    return [q for b in banks for q in b.questions if q.kind == "set"]


def facts(banks: list[Bank]) -> list[Question]:
    return [q for b in banks for q in b.questions if q.kind == "fact"]


def as_gold(questions: list[Question]) -> list[tuple[str, str, list[tuple[str, list[str]]]]]:
    """The shape `canon_gold.GOLD` has always had.

    `diagnose_misses.py` unpacks `(series, query, canon)` and indexes into the
    canon pairs, so this tuple shape is a compatibility contract rather than a
    convenience. Only scored items appear: an item nothing solid backs must not
    be able to mark the engine wrong.
    """
    return [
        (q.series, q.question, [(i.item, list(i.aliases)) for i in q.scored_items()])
        for q in questions
    ]


def recall_only(questions: list[Question]) -> set[str]:
    return {q.question for q in questions if q.recall_only}


def subjects(questions: list[Question]) -> dict[str, str]:
    return {q.question: q.subject for q in questions if q.subject}


def retired(banks: list[Bank]) -> dict[str, str]:
    """`"<question> :: <item>"` -> why it was retired.

    Keyed the way `diagnose_misses.GOLD_ERRORS` was, so a retired item is
    bucketed as a gold error rather than counted against the engine.
    """
    out: dict[str, str] = {}
    for bank in banks:
        for row in bank.retired:
            question = row.get("question", "")
            item = row.get("item", "")
            if question and item:
                out[f"{question} :: {item}"] = row.get("reason", "retired")
    return out
