"""Ask the running engine a sheet of questions and write down what it said.

Every answer is whatever the server returned — full member lists, the set it
resolved to, and its own confidence in that set. Nothing is filtered or
corrected on the way out, because the point of the sheet is to show what a
script writer would actually receive.
"""

import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Runnable as a bare script as well as `python -m`, where there is no package
# for the `scriptengine.config` import below to resolve against.
if __package__ in (None, ""):  # pragma: no cover - only on the script path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scriptengine.config import Settings  # noqa: E402

BASE = "http://127.0.0.1:8000"
BUDGET = 60000

# Series in the order the catalogue lists them, largest first, with the wiki's
# own display name.
SERIES = [
    ("db", "Dragon Ball"),
    ("onepiece", "One Piece"),
    ("bleach", "Bleach"),
    ("hxh", "Hunter x Hunter"),
    ("opm", "One-Punch Man"),
    ("jjk", "Jujutsu Kaisen"),
    ("berserk", "Berserk"),
    ("csm", "Chainsaw Man"),
]

# A second set, aimed at the two things the ontology layer was built for:
# abilities qualified by a race, and organisations whose categories mix members
# with the places they hold and the equipment they issue. Run with
# `python scriptengine/eval/question_sheet.py ontology`.
ONTOLOGY_QUESTIONS = {
    "db": [
        "Every Saiyan transformation",
        "Every Namekian transformation",
        "Every Frieza Race transformation",
        "Every Majin transformation",
        "Every God of Destruction",
        "Every member of the Red Ribbon Army",
        "Every member of the Galactic Frieza Army",
        "Every Kai",
        "Every technique Goku can use",
    ],
    "onepiece": [
        "Every Fish-Man",
        "Every member of the Mink Tribe",
        "Every member of the Straw Hat Pirates",
        "Every Marine Vice Admiral",
        "Every Logia user",
        "Every Giant",
        "Every Revolutionary Army commander",
    ],
    "bleach": [
        "Every Quincy technique",
        "Every Arrancar technique",
        "Every Shinigami technique",
        "Every Bankai",
        "Every member of the Espada",
        "Every Sternritter",
        "Every Vasto Lorde",
    ],
    "hxh": [
        "Every Nen type",
        "Every Chimera Ant Royal Guard",
        "Every member of the Phantom Troupe",
        "Every Zoldyck",
        "Every Hunter rank",
    ],
    "opm": [
        "Every S-Class hero",
        "Every member of the Monster Association",
        "Every Dragon level monster",
        "Every hero class",
    ],
    "jjk": [
        "Every Special Grade curse",
        "Every Domain Expansion",
        "Every member of the Zenin Family",
        "Every Cursed Tool",
        "Every Shikigami of the Ten Shadows Technique",
    ],
    "berserk": [
        "Every Apostle",
        "Every Pseudo-Apostle",
        "Every member of the God Hand",
        "Every member of the Band of the Hawk",
    ],
    "csm": [
        "Every Fiend",
        "Every Hybrid",
        "Every Primal Fear Devil",
        "Every Public Safety Devil Hunter",
    ],
}

QUESTIONS = {
    "db": [
        "Every Saiyan transformation",
        "Every transformation ever, including games",
        "Every race in Dragon Ball",
        "All types of Dragon Balls",
        "Every Dragon Ball movie",
        "Every Android",
        "Every Fusion",
        "Every Angel",
        "Every Z Fighter",
        "Every Majin",
        "Every Demon",
        "Every member of the Galactic Frieza Army",
        "Every Earthling",
        "Every Tournament Fighter",
    ],
    "onepiece": [
        "Every race in One Piece",
        "All officer ranks in the Marines",
        "Every type of Devil Fruit",
        "Every Haki type",
        "Every Warlord of the Sea",
        "Every Yonko",
        "Every Logia user",
        "Every Mythical Zoan user",
        "Every One Piece movie",
        "Every Marine Vice Admiral",
        "Every Revolutionary Army commander",
        "Every named sword",
        "Every Giant",
    ],
    "bleach": [
        "Every Division of the Gotei 13",
        "Every Espada",
        "Every Sternritter",
        "Every Captain of the Gotei 13",
        "Every Visored",
        "Every stage of Hollow evolution",
        "Every Kido spell",
        "Every member of the Royal Guard",
        "Every Quincy",
        "Every Arrancar",
        "Every Vasto Lorde",
        "Every Fullbringer",
        "Every Fraccion",
    ],
    "hxh": [
        "Every Nen type",
        "Every member of the Phantom Troupe",
        "Every Zoldyck",
        "Every Hunter rank",
        "Every member of the Zodiac Twelve",
        "Every rank in the Chimera Ant hierarchy",
        "Every Squadron Leader",
        "Every Chimera Ant",
        "Every member of the Kurta Clan",
        "Every member of the Kakin Royal Family",
        "Every Greed Island card",
    ],
    "opm": [
        "Every disaster level",
        "Every hero class",
        "Every S-Class hero",
        "Every A-Class hero",
        "Every Dragon level monster",
        "Every Demon level monster",
        "Every executive of the Monster Association",
        "Every Neo Hero",
        "Every martial artist",
        "Every ninja",
    ],
    "jjk": [
        "Every Rank of Curse in Jujutsu Kaisen",
        "Every Domain Expansion",
        "Every Cursed Tool",
        "Every Shikigami of the Ten Shadows Technique",
        "Every member of the Big Three Families",
        "Every Culling Game player",
        "Every Incarnation",
        "Every Cursed Technique of Sukuna",
        "Every member of the Zenin Family",
        "Every Curse User",
        "Every Jujutsu School",
    ],
    "berserk": [
        "Every Apostle",
        "Every member of the God Hand",
        "Every Pseudo-Apostle",
        "Every kind of Apostle",
        "Every army in Berserk",
        "Every member of the Holy See",
        "Every Elf",
        "Every magic in Berserk",
    ],
    "csm": [
        "Every Devil",
        "Every Fiend",
        "Every Hybrid",
        "Every Devil Hunter",
        "Every Horseman",
        "Every Primal Fear Devil",
        "Every Devil tier",
        "Every Public Safety division",
    ],
}


def ask(series: str, query: str) -> dict:
    request = urllib.request.Request(
        BASE + "/context",
        data=json.dumps(
            {"series": series, "query": query, "mode": "auto", "token_budget": BUDGET}
        ).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    started = time.time()
    with urllib.request.urlopen(request, timeout=900) as response:
        body = json.loads(response.read())
    body["_seconds"] = round(time.time() - started, 2)
    return body


def render(series: str, label: str, query: str, body: dict) -> list[str]:
    members = body.get("members") or []
    beats = body.get("beats") or []
    available = body.get("members_available", len(members))
    confidence = body.get("confidence", "")

    lines = [f"### {query}", ""]
    facts = [f"**mode** `{body.get('mode')}`"]
    if body.get("basis"):
        facts.append(f"**set** `{body['basis']}`")
    if confidence:
        facts.append(f"**confidence** `{confidence}`")
    if members:
        shown = f"{len(members)}" if len(members) == available else f"{len(members)} of {available}"
        facts.append(f"**members** {shown}")
    elif beats:
        facts.append(f"**beats** {len(beats)}")
    facts.append(f"**{body['_seconds']}s**")
    lines += [" · ".join(facts), ""]

    if body.get("warning"):
        lines += [f"> ⚠ {body['warning']}", ""]

    if not members and not beats:
        lines += ["*No set and no narrative — the engine declined to answer.*", ""]
        return lines

    if members:
        grouped: dict[str, list[str]] = {}
        for member in members:
            entry = member.get("name", "")
            if member.get("debut"):
                entry += f" {member['debut']}"
            grouped.setdefault(member.get("group") or "", []).append(entry)

        # Numbered, because a set has a size and a reader should be able to see
        # it without counting commas.
        for group, names in grouped.items():
            if group:
                lines += [f"**{group}** — {len(names)}", ""]
            lines += [f"{index}. {name}" for index, name in enumerate(names, 1)]
            lines += [""]

        rejected = body.get("rejected") or []
        if rejected:
            lines += [
                f"<details><summary>{len(rejected)} rejected — "
                f"{body.get('candidates', 0)} candidates, "
                f"{body.get('scope', 'canon')} scope</summary>",
                "",
            ]
            lines += [
                f"{index}. {entry['name']} — *{entry['reason']}*"
                for index, entry in enumerate(rejected, 1)
            ]
            lines += ["", "</details>", ""]
    else:
        lines += [
            f"{index}. **{beat.get('title', '')}**"
            + (f" {beat['source_span']}" if beat.get("source_span") else "")
            for index, beat in enumerate(beats[:14], 1)
        ]
        lines += [""]
    return lines


# Real script topics, written the way a video title is rather than the way a
# database query is. Several are not enumerable sets at all — "Every Unsolved
# Mystery", "Every Way Sorcerers Can Die", "Daily Life in Every City" — which is
# the point: the engine has to say so instead of answering anyway.
TOPIC_QUESTIONS = {
    "db": [
        "Every Wish in Dragon Ball",
        "Every Type of Dragon Ball",
    ],
    "onepiece": [
        "Every Unsolved Mystery in One Piece",
        "Every Possible Devil Fruit Awakening",
    ],
    "bleach": [],
    "hxh": [
        "Every Nen Ability Used on the Black Whale 1 (So Far)",
        'Every "ULTIMATE" Class Nen User in HunterxHunter',
        "Every Unsolved HunterxHunter Mystery",
        "Every Succesion War Prince in HxH",
    ],
    "opm": [
        "Daily Life in Every City of One Punch Man",
        "Every Unsolved Mystery in One Punch Man",
        "Every S Class Hero Origin | One Punch Man",
        "Every Dragon Level Threat in One Punch Man",
        "Every S-Class Hero in One Punch Man",
    ],
    "jjk": [
        "Every Way Sorcerers Can Die in the Culling Game",
        "Every Sorcerer Forced to Fight in the Culling Game",
        "Every Instant Kill Domain Expansion in Jujutsu Kaisen",
        "Every Major Death in Jujutsu Kaisen",
    ],
    "berserk": [
        "Every Mystical Race in Berserk",
        "Every Apostle in Berserk",
    ],
    "csm": [
        "Every Apocalypse Level Devil in Chainsaw Man (UPDATED)",
        "Every Apocalyptic Devil in Chainsaw Man",
    ],
}

# Sets scoped to one character rather than to a race or a category — "every form
# of Goku", "every Saitama technique". A different axis from the other sheets:
# the qualifier is a person, so the answer has to be what *they* have rather
# than everything of that kind in the series.
CHARACTER_QUESTIONS = {
    "db": [
        "Every form of Goku",
        "Every form of Vegeta",
        "Every technique Goku uses",
        "Every transformation of Frieza",
    ],
    "onepiece": [
        "Every form of Luffy",
        "Every Gear of Luffy",
        "Every technique of Zoro",
    ],
    "opm": [
        "Every Saitama technique",
        "Every technique of Genos",
    ],
    "jjk": [
        "How many 1v1 battles did Yuji Itadori have with named characters",
        "Every battle of Yuji Itadori",
        "Every cursed technique of Sukuna",
    ],
    "bleach": [
        "Every form of Ichigo Kurosaki",
        "Every technique of Ichigo Kurosaki",
    ],
    "hxh": [
        "Every Nen ability of Killua",
        "Every Nen ability of Kurapika",
    ],
    "csm": [
        "Every form of Denji",
    ],
    "berserk": [
        "Every armor of Guts",
    ],
}

SHEETS = {
    "default": (QUESTIONS, "Engine Answer Sheet 2.md"),
    "ontology": (ONTOLOGY_QUESTIONS, "Engine Answer Sheet 3 - Ontology.md"),
    "topics": (TOPIC_QUESTIONS, "Engine Answer Sheet 4 - Real Topics.md"),
    "character": (CHARACTER_QUESTIONS, "Engine Answer Sheet 5 - Character Scoped.md"),
}


def main() -> None:
    choice = sys.argv[1] if len(sys.argv) > 1 else "default"
    if choice not in SHEETS:
        raise SystemExit(f"Unknown sheet {choice!r}. Choose from: {', '.join(SHEETS)}")
    questions_for, filename = SHEETS[choice]

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = [
        "# What the engine answers",
        "",
        f"Every question below was put to the running ScriptEngine server on "
        f"{stamp} through `POST /context` with `mode=\"auto\"` and a 60,000-token "
        "budget, and the answers are exactly what came back — full member lists, "
        "the set each question resolved to, and the engine's own confidence in "
        "that set. Nothing was corrected on the way out.",
        "",
        "**Read `confidence` before trusting a list.** `declared` means the series "
        "declares that set by name and `exact` means every word of the set's name "
        "was asked for; `partial` and `weak` are flagged inline and are usually "
        "the wrong set. A count that looks too small is the one thing confidence "
        "cannot see — see `docs/RETRIEVAL_SCENARIOS.md`.",
        "",
        "Each answer also records what was **rejected** and why. A category is "
        "what the wiki keeps, not what the question asked for: `Transformations` "
        "holds Black Frieza because it is one, and only the question knows that "
        "\"Saiyan\" was the point. Scope is canon by default — game and spin-off "
        "entries stay in the store and return when a question asks for them.",
        "",
        "---",
        "",
    ]

    counts: list[tuple[str, int, int]] = []
    for series, label in SERIES:
        questions = questions_for.get(series) or []
        if not questions:
            continue
        print(f"== {label}")
        out += [f"## {label} — `{series}`", ""]
        answered = 0
        for query in questions:
            body = ask(series, query)
            members = len(body.get("members") or [])
            beats = len(body.get("beats") or [])
            if members or beats:
                answered += 1
            print(
                f"   {str(body.get('confidence', '-')):9} n={members:<4} "
                f"{query[:42]:44} {body['_seconds']}s"
            )
            out += render(series, label, query, body)
        counts.append((label, answered, len(questions)))
        out += ["---", ""]

    out += ["## Coverage", "", "| series | answered | asked |", "|---|---:|---:|"]
    for label, answered, total in counts:
        out.append(f"| {label} | {answered} | {total} |")
    out += [
        "",
        "## Read these before using a list",
        "",
        "`declared` means the series declares that set by name. It does **not**",
        "mean every member is what the question described — check the count",
        "against the size you expect, and open the rejections when it surprises",
        "you. Known limits, all visible above:",
        "",
        "- **A set can be short rather than wrong.** `Every island in the Grand",
        "  Line` returns four and reports `exact`, because the name matches",
        "  exactly; the wiki files most islands elsewhere. Confidence cannot see",
        "  an incomplete category — only the count can.",
        "- **Every rank in the Chimera Ant hierarchy** returns two tiers, because",
        "  the wiki keeps categories for Squadron Leaders and Chimera Ants and",
        "  none for the King, the Queen or the Royal Guards.",
        "- **Every disaster level** returns four, not five: this wiki keeps no",
        "  `God` category, because essentially one being has ever been rated there.",
        "- **Ability classification needs user and inventor links.** Dragon Ball",
        "  has them, so \"Saiyan transformation\" means one only Saiyans reach —",
        "  Kaio-ken is excluded because King Kai taught it and Krillin knows it.",
        "  Bleach and One Piece record no such links for abilities, so the same",
        "  reasoning cannot run there and those sets are unfiltered.",
        "",
        "None of these is a retrieval failure — each is the wiki's own shape",
        "showing through. They are listed because a script written straight off a",
        "member count would get them wrong.",
        "",
    ]

    # Resolved through settings rather than as a CWD-relative literal. The
    # previous `Path("scripts output")` only worked when this was run from the
    # repo root, and it wrote measurement output into a gitignored folder --
    # which is how six earlier answer sheets were lost. Measurement artifacts
    # belong under `reports/`, with everything else that describes a run.
    destination = Settings().reports_root / filename
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(out), encoding="utf-8")
    print(f"\nwrote {destination}")


if __name__ == "__main__":
    main()
