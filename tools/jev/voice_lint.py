"""Lint a script draft against the voice contract with a local decision model.

Two kinds of rule, the snifftest / clarity-judge split:

* countable rules are regular expressions and run here, sending nothing;
* judgment rules are typed yes/no questions asked of the local Jev-compatible
  gateway (`POST /v1/systemone`, fast lane by default), one request per
  paragraph with every rule in it, so a paragraph costs one forward pass.

The rules are a compact, checkable projection of `VOICE_RULES` in
`scriptengine/api/rules.py` and of `docs/ANTI_AI_SCRIPTING.md`. They lint the
words; the structural HumanScope audit (Structure Sheet, Mode B) is still the
contract, and this does not replace it.

Stdlib only, so it runs from any interpreter the repo is opened with.

    python tools/jev/voice_lint.py "scripts output/Draft.md"
    python tools/jev/voice_lint.py draft.md --lane deep      # final audit on NInfer
    python tools/jev/voice_lint.py draft.md --dry-run        # countable rules only
    python tools/jev/voice_lint.py --emit-rules > rules.json # slop-grader ruleset
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field

DEFAULT_BASE = "http://127.0.0.1:8018"
# Jev answers about 0.5 on state it cannot read; a reading in this band is not
# an opinion and must never become a flag or stand in for a pass (snifftest).
NO_JUDGMENT = (0.4, 0.6)
MIN_JUDGED_CHARS = 60

AI_VOCAB = (
    "delve|realm|testament|pivotal|crucial|transformative|intricate|showcase[sd]?|"
    "underscore[sd]?|captivat\\w*|embark\\w*|unleash\\w*|tapestry|foster\\w*|seamless\\w*|"
    "empower\\w*|elevate[sd]?|revolutioni[sz]\\w*|landscape|nuanced"
)
BODY_SENSATION = (
    "tight(?:ening)? (?:in (?:his|her|their) )?chest|chest tighten\\w*|cold sweat|"
    "throat (?:closing|closed|tighten\\w*)|stomach (?:dropp\\w*|churn\\w*|knott\\w*)|"
    "heart (?:pounding|hammering|racing)|breath caught|blood ran cold|shiver ran"
)


@dataclass(frozen=True)
class Regex:
    id: str
    pattern: str
    message: str
    min_count: int = 1
    flags: int = re.IGNORECASE

    def hits(self, text: str) -> int:
        return len(re.findall(self.pattern, text, self.flags))


@dataclass(frozen=True)
class Judgment:
    id: str
    what: str
    true: str
    false: str
    not_for: tuple[str, ...] = ()
    examples: tuple[str, ...] = ()
    scope: str = "paragraph"  # paragraph | closing (last two paragraphs only)
    message: str = ""

    def question(self) -> dict:
        instructions: dict = {"what": self.what}
        if self.not_for:
            instructions["not_for"] = list(self.not_for)
        if self.examples:
            instructions["examples"] = list(self.examples)
        return {
            "type": "noul",
            "instructions": instructions,
            "criteria": {"true": self.true, "false": self.false},
        }


REGEX_RULES: tuple[Regex, ...] = (
    Regex("em_dash", "[—–]", "Long dash. VOICE_RULES: no em dashes; use a full stop."),
    Regex("ai_vocabulary", rf"\b(?:{AI_VOCAB})\b", "AI vocabulary doing PR for an idea (ANTI_AI tell 6)."),
    Regex(
        "not_x_its_y",
        r"\b(?:it|this|that)(?:'s| is|’s) not (?:just |only |merely )?[^.;!?]{1,60}[,;] (?:it|this|that)(?:'s| is|’s)\b",
        "\"It's not X, it's Y\" reframe (ANTI_AI tell 2). Make the direct claim.",
    ),
    Regex(
        "ing_tail",
        r",\s+(?:highlighting|underscoring|showcasing|emphasi[sz]ing|cementing|signal(?:l)?ing|"
        r"paving the way|marking|reflecting|illustrating|demonstrating)\b",
        "Superficial -ing tail analysis (ANTI_AI tell 3). Cut it or give it its own sentence.",
    ),
    Regex(
        "plain_word_dodge",
        r"\b(?:serves as|stands as|boasts|plays a (?:key |pivotal |crucial )?role in)\b",
        "Dodging the plain verb (ANTI_AI tell 5). Use is / has / does.",
    ),
    Regex(
        "weasel",
        r"\b(?:many|some) (?:fans|viewers|readers|people|critics) (?:believe|argue|think|consider|say)\b",
        "Weasel attribution (ANTI_AI tell 7). Name the source or drop it.",
    ),
    Regex("body_sensation", rf"\b(?:{BODY_SENSATION})\b", "Body-sensation emotion, the biggest AI tell. Say the feeling."),
    Regex("final_thoughts", r"^\W*(?:final thoughts|in conclusion|key takeaways)\b", "Banned closing section (STYLE_RULES).", flags=re.I | re.M),
    Regex("bare_marker", r"\[\d+\]", "Bare retriever marker like [1] (ANNOTATION_RULES)."),
    Regex(
        "filler_transition",
        r"\b(?:moving on to|next up|without further ado|let's dive in)\b",
        "Filler transition between sections (STYLE_RULES).",
    ),
)

JUDGMENT_RULES: tuple[Judgment, ...] = (
    Judgment(
        "significance_inflation",
        "The paragraph inflates importance with generic significance claims instead of stating what happened.",
        "It calls something pivotal, a turning point, forever changed, one of the most X, or similar, without the concrete fact that would earn it.",
        "It states concrete events, outcomes and names flatly; any importance is shown by the facts themselves.",
        not_for=("A plain factual superlative the story itself states, like 'the strongest sorcerer of the modern era' as a title.",),
        examples=("This battle marks a pivotal shift in the Shibuya arc.",),
        message="Significance inflation (ANTI_AI tell 1).",
    ),
    Judgment(
        "generic_not_specific",
        "The paragraph talks about the category rather than the thing: it could have been written about any anime.",
        "Mostly vague praise or description; few or no named characters, techniques, chapters or specific events.",
        "It names specific characters, techniques, chapters, episodes or exact events that only this series has.",
        message="Generic, not specific. Specificity is the moat (VOICE_RULES).",
    ),
    Judgment(
        "rule_of_three",
        "The paragraph packs claims or descriptors into symmetric groups of three for rhythm, not because there are three.",
        "It uses a rhythmic triple such as 'He trains, he fights, he wins' or three stacked adjectives or clauses.",
        "Lists have their real, uneven counts; no rhythmic triple packing.",
        message="Rule-of-three packing (ANTI_AI tell 4).",
    ),
    Judgment(
        "flat_rhythm",
        "The sentences in the paragraph all have about the same length and shape.",
        "Most sentences are similar in length and structure, so it reads with a flat, even cadence.",
        "Sentence lengths clearly vary, with some short and some long sentences.",
        message="Flat sentence rhythm. Vary sentence length (VOICE_RULES).",
    ),
    Judgment(
        "elegant_variation",
        "The paragraph refuses to repeat a name and swaps in epithets for the same person or thing.",
        "The same character is referred to by a chain of different epithets (the young sorcerer, the vessel, the boy) where a person would repeat the name.",
        "Names are repeated plainly; pronouns are used normally.",
        message="Elegant variation (ANTI_AI tell 10). Say the name again.",
    ),
    Judgment(
        "explains_the_moral",
        "This is one of the last paragraphs of a narration script. It explains what the story meant instead of ending on events.",
        "It tells the viewer what the story was about, sums up the lesson, or delivers a closing moral or assessment.",
        "It ends on concrete events, a line of dialogue, or a plain fact, without explaining the meaning.",
        scope="closing",
        message="Closing line explains the story. Cut it (VOICE_RULES).",
    ),
)


@dataclass
class Flag:
    rule: str
    paragraph: int
    message: str
    probability: float | None = None
    excerpt: str = ""


@dataclass
class Result:
    flags: list[Flag] = field(default_factory=list)
    no_judgment: int = 0
    judged: int = 0
    errors: list[str] = field(default_factory=list)


def paragraphs(text: str) -> list[str]:
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    return blocks


def is_prose(block: str) -> bool:
    first = block.splitlines()[0].strip()
    if first.startswith("#") or re.match(r"^\*\s+\*\*.+\*\*\s*$", first) or re.match(r"^\*\*.+\*\*$", first):
        return len(block.splitlines()) > 1
    if first.startswith("[covers"):
        return False
    return len(block) >= MIN_JUDGED_CHARS


def ask(base: str, lane: str, state: str, questions: dict, timeout: float) -> dict:
    body = json.dumps({"model": "jev-latest", "state": state, "questions": questions}).encode()
    request = urllib.request.Request(
        base.rstrip("/") + "/v1/systemone",
        data=body,
        method="POST",
        headers={
            "content-type": "application/json",
            "authorization": "Bearer " + os.environ.get("JEV_API_KEY", "local"),
            "x-jev-lane": lane,
        },
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as reply:
                return json.load(reply).get("answers", {})
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503) or attempt == 2:
                raise RuntimeError(f"HTTP {error.code}: {error.read(200).decode('utf-8', 'replace')}") from None
        time.sleep(2**attempt)
    return {}


def lint(text: str, *, base: str, lane: str, threshold: float, dry_run: bool, timeout: float) -> Result:
    result = Result()
    blocks = paragraphs(text)
    for index, block in enumerate(blocks, 1):
        for rule in REGEX_RULES:
            count = rule.hits(block)
            if count >= rule.min_count:
                match = re.search(rule.pattern, block, rule.flags)
                result.flags.append(Flag(rule.id, index, rule.message, excerpt=_around(block, match)))
    if dry_run:
        return result

    prose = [i for i, b in enumerate(blocks, 1) if is_prose(b)]
    closing = set(prose[-2:])
    for index in prose:
        rules = [r for r in JUDGMENT_RULES if r.scope == "paragraph" or index in closing]
        questions = {r.id: r.question() for r in rules}
        try:
            answers = ask(base, lane, blocks[index - 1], questions, timeout)
        except (RuntimeError, urllib.error.URLError, TimeoutError) as error:
            result.errors.append(f"paragraph {index}: {error}")
            continue
        result.judged += 1
        for rule in rules:
            p = (answers.get(rule.id) or {}).get("noul")
            if not isinstance(p, (int, float)):
                continue
            if NO_JUDGMENT[0] <= p <= NO_JUDGMENT[1]:
                result.no_judgment += 1
            elif p >= threshold:
                result.flags.append(Flag(rule.id, index, rule.message, round(float(p), 3), blocks[index - 1][:90]))
    return result


def _around(block: str, match: re.Match | None) -> str:
    if match is None:
        return block[:90]
    start = max(0, match.start() - 40)
    return block[start : match.end() + 40].replace("\n", " ")


def emit_rules(threshold: float) -> dict:
    return {
        "version": 1,
        "source": "ScriptEngine tools/jev/voice_lint.py (VOICE_RULES + docs/ANTI_AI_SCRIPTING.md)",
        "threshold": threshold,
        "rules": [
            {"id": r.id, "kind": "regex", "pattern": r.pattern, "ignore_case": bool(r.flags & re.I), "multiline": bool(r.flags & re.M), "message": r.message}
            for r in REGEX_RULES
        ]
        + [
            {
                "id": r.id,
                "kind": "judgment",
                "what": r.what,
                "not_for": list(r.not_for),
                "examples": list(r.examples),
                "criteria": {"true": r.true, "false": r.false},
                "scope": r.scope,
                "message": r.message,
            }
            for r in JUDGMENT_RULES
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("draft", nargs="?", help="script draft (markdown / text)")
    parser.add_argument("--base-url", default=os.environ.get("JEV_API_BASE_URL", DEFAULT_BASE))
    parser.add_argument("--lane", choices=("fast", "deep"), default="fast")
    parser.add_argument("--threshold", type=float, default=0.7)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--dry-run", action="store_true", help="countable rules only; no network")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--emit-rules", action="store_true", help="print the ruleset as slop-grader JSON/YAML")
    args = parser.parse_args(argv)

    if args.emit_rules:
        print(json.dumps(emit_rules(args.threshold), indent=2, ensure_ascii=False))
        return 0
    if not args.draft:
        parser.error("a draft path is required")

    with open(args.draft, encoding="utf-8") as handle:
        text = handle.read()
    result = lint(text, base=args.base_url, lane=args.lane, threshold=args.threshold, dry_run=args.dry_run, timeout=args.timeout)

    if args.json:
        print(json.dumps({"flags": [f.__dict__ for f in result.flags], "judged": result.judged, "no_judgment": result.no_judgment, "errors": result.errors}, indent=2, ensure_ascii=False))
    else:
        for f in result.flags:
            p = "" if f.probability is None else f" p={f.probability}"
            print(f"¶{f.paragraph:<3} {f.rule:<24}{p}  {f.message}\n      … {f.excerpt}")
        print(f"\n{len(result.flags)} flag(s); {result.judged} paragraph(s) judged ({args.lane} lane); "
              f"{result.no_judgment} no-judgment reading(s); {len(result.errors)} error(s)")
        for e in result.errors:
            print("error:", e, file=sys.stderr)
    if result.errors and not result.flags:
        return 2
    return 1 if result.flags else 0


if __name__ == "__main__":
    sys.exit(main())
