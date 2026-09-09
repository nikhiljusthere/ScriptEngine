"""The script-writing path: bundle -> prompt -> prose -> verified file.

This is the one place a model runs on the writing path. Everything upstream
(build_context) and downstream (verify_script) is deterministic, so the loop
is: fetch the bundle, render the rules inside the prompt, ask the writer for
the script, check every chapter/episode tag against the raw crawl, and when a
tag fails, send only the findings back for a repair pass. A number the model
invented is caught by `verify_script` the same way it catches one written by
hand; the repair pass is the automation of "fix the tags, keep the prose".

The length gate is separate from the tag gate and is enforced, not requested:
the contract is a band (target +/- LENGTH_TOLERANCE). Models write short, so a
draft is expanded in a loop until it clears the band's low edge or the pass
budget is spent, and trimmed once if a pass overshoots the high edge. Tags are
the hard gate; the band is the soft one, but a script that is still out of
band after the length passes saves with the report saying how far off it is.
The expansion and trim prompts forbid new facts the same way the repair prompt
forbids touching prose.

Two models are involved and they are deliberately different. The bundle is
assembled with no model at all. The *writer* uses `writer_*` settings, which
default to the large-context LM Studio model in `opencode.json`, because a
6,000-word script needs the big window. Extraction and research keep the
small fast model; nothing here touches `llm_*`.

The writer reuses `LLMClient` with the writer values folded into a copy of
the settings, never its own connection code: same two backends (local HTTP,
opencode subprocess), same error taxonomy, same rate-limit stop.
"""

from __future__ import annotations

import re
from typing import Any

from scriptengine.api.context import build_context, render_prompt
from scriptengine.config import (
    Settings,
    SeriesPaths,
    get_settings,
    script_destination,
    series_paths,
)
from scriptengine.eval.verify import TAG, verify_script
from scriptengine.llm.client import LLMClient
from scriptengine.retrieve.router import Route, route

WRITER_SYSTEM = """\
You are a video essay narrator writing a script from researched context. Write \
the way a fan explains this to a friend out loud, never like a wiki article or \
a trailer. Follow the rules in the research below exactly. Output only the \
script markdown, starting with the bold title line. No preamble, no summary of \
what you are about to write, no closing remarks outside the script itself.
"""

# The whole answer wrapped in a fence, which thinking models love to do.
_FENCE = re.compile(r"^```[^\n]*\n(.*?)\n```\s*$", re.S)

# First line is the title: `**A Clean Name**`.
_TITLE = re.compile(r"^\*\*(.+?)\*\*\s*$")

# Marker families a finished script may carry. verify_script reads only the
# round-bracket (Chapter/Episode) tags, so the square-bracket ones are free to
# use in the script and free to strip for the words-only companion.
_COVERS_BLOCK = re.compile(
    r"(?:^[ \t]*\[covers \d[\d\-]*\][^\n]*\n?|^[ \t]*·[^\n]*\n?)+", re.M
)
_TS = re.compile(r"\[E\d+(?:[ ,:][^\]]+)?\]")
_ANY_PAREN = re.compile(r"\([^()]*\)")

# The same budget rule as script_writer.ps1's Get-AutoBudget: words times
# eight, clamped so a short topic still gets a workable bundle and a huge one
# cannot ask for more than the engine will serve.
MIN_BUDGET = 6000
MAX_BUDGET = 60_000

# One repair pass per failing tag is plenty; past this the writer is guessing.
MAX_REPAIR_ATTEMPTS = 3

# The length contract is a band, not a floor: a 6,000-word ask must land at
# 6,000 +/- LENGTH_TOLERANCE. Drafts undershoot by half, expansion adds
# roughly half of current length, and trim removes only a tenth, so the loop
# converges from below and starves from above: one good trim (or two) after
# the last expansion overshoot is what lands in band. The cap is a safety
# valve against a model that writes the same script no matter what it is
# told, not the length the loop aims for.
LENGTH_TOLERANCE = 500
MAX_LENGTH_PASSES = 10

# Matches the request the API takes: 12 passages gives multi-entity topics
# enough recall without spending the budget on a tail of near-misses.
TOP_K = 12


def auto_budget(words: int) -> int:
    """The context budget a word count implies."""
    return max(MIN_BUDGET, min(words * 8, MAX_BUDGET))


def route_script(
    paths: SeriesPaths, subject: str, settings: Settings | None = None
) -> tuple[str, Route]:
    """The mode a script on `subject` should use.

    `/context` answers questions, so a bare name ("Maki Zenin") is a lookup
    and routes to qa. A *script* on that name is a story, not a lookup, so the
    script path escalates exactly that one case to narrative. Every other
    topic keeps the router's verdict, and the two paths can only disagree
    where their jobs differ: one answers, one narrates.
    """
    routed = route(paths, subject, settings)
    mode = routed.mode
    signals = routed.signals or {}
    if (
        mode == "qa"
        and signals.get("subject")
        and not signals.get("interrogative")
        and not signals.get("story_verb")
    ):
        return "narrative", Route(
            "narrative",
            "a bare name becomes a story when a script is being written",
            signals,
        )
    return mode, routed


def _writer_settings(settings: Settings) -> Settings:
    """A copy of the settings with the writer's model folded in.

    `LLMClient` reads only `llm_*`; the writer values are the same fields with
    a different default, so the copy is how the client is reused rather than
    duplicated.
    """
    return settings.model_copy(
        update={
            "llm_backend": settings.writer_backend,
            "llm_model": settings.writer_model,
            "llm_base_url": settings.writer_base_url,
            "llm_api_key": settings.writer_api_key,
            "llm_timeout_seconds": settings.writer_timeout_seconds,
        }
    )


def _complete(
    prompt: str, settings: Settings, temperature: float
) -> str:
    client = LLMClient(_writer_settings(settings))
    return client.complete(
        prompt,
        system=WRITER_SYSTEM,
        temperature=temperature,
        max_tokens=settings.writer_max_tokens,
    )


def strip_fence(text: str) -> str:
    """Remove a code fence wrapping the whole answer, nothing else.

    A fence is the model's packaging, and a script that starts with a triple
    backtick line fails every downstream reader. Only a whole-document fence is
    stripped; a preamble before the fence means the answer is not the script,
    and guessing where the script starts inside it would drop the title.
    """
    match = _FENCE.match(text.strip())
    return match.group(1).strip() if match else text.strip()


def title_of(text: str) -> str:
    """The script's own title line, without the bold markers."""
    first = next((line.strip() for line in text.splitlines() if line.strip()), "")
    match = _TITLE.match(first)
    return match.group(1).strip() if match else ""


def _apply_title(text: str, title: str) -> str:
    """Make the script's first line the saved title.

    The writer invents its own title, and the folder a script lands in is
    chosen by exact title (`script_destination`), so a regenerate would spawn
    `Video 6 - ...` beside `Video 1 - ...` the moment the model chose a new
    name. The subject is the video's title; the script says the same. The
    model's bold first line is replaced, the prose is untouched.
    """
    lines = text.splitlines()
    first = next((i for i, line in enumerate(lines) if line.strip()), None)
    if first is not None and _TITLE.match(lines[first].strip()):
        lines[first] = f"**{title}**"
        return "\n".join(lines).strip()
    return f"**{title}**\n\n{text.strip()}"


def write_script(
    bundle: dict[str, Any],
    settings: Settings | None = None,
    words: int = 0,
    intro: bool = True,
) -> str:
    """One draft of a script from a bundle.

    The prompt is the bundle rendered with the rules appended, so the writer
    sees the research and the contract in the same message; there is no second
    document it might not read. With a length target, one more line stands
    alone at the end: the model skims rules, but a 6,000-word ask must not
    come back as a 2,000-word draft, because every thousand words it omits is
    an expansion pass later.
    """
    settings = settings or get_settings()
    prompt = render_prompt(bundle, intro=intro, words=words, rules=True)
    if words:
        low = words - LENGTH_TOLERANCE
        high = words + LENGTH_TOLERANCE
        prompt += (
            f"\n\nTHE LENGTH IS THE CONTRACT: the finished script must be "
            f"between {low} and {high} words. Do not hand in a short script: "
            "keep writing sections until the script reaches that length."
        )
    return strip_fence(_complete(prompt, settings, temperature=0.7))


def word_count(text: str) -> int:
    """Prose words, roughly: whitespace-separated tokens."""
    return len(text.split())


def make_clean_version(text: str) -> str:
    """The script with every citation, timestamp and source-span marker removed.

    The words-only companion an editor records from: the chapter/episode tags,
    the [E<n> mm:ss] transcript timestamps and the [covers X-Y] source-span
    blocks (header lines plus their '·' event lines) are stripped, and the
    whitespace they leave behind is collapsed. The prose is never touched.
    """
    out = _COVERS_BLOCK.sub("", text)
    out = _TS.sub("", out)
    out = _ANY_PAREN.sub("", out)
    out = re.sub(r"[ \t]{2,}", " ", out)
    out = re.sub(r" ?\n", "\n", out)
    return re.sub(r"\n{3,}", "\n\n", out).strip() + "\n"


def _passage_tags(line: str) -> list[str]:
    """The distinct chapter/episode tags a line carries, in order."""
    seen: set[str] = set()
    out: list[str] = []
    for match in TAG.finditer(line):
        if match.group(0) not in seen:
            seen.add(match.group(0))
            out.append(match.group(0))
    return out


def _compact_tag(tag: str) -> str:
    """A tag in the covers shorthand: '(Chapter 66, Episode 25)' -> 'Ch 66, Ep 25'."""
    chapter = re.search(r"Chapter\s+([\d.\-]+)", tag)
    episode = re.search(r"Episode\s+([\d.\-]+)", tag)
    if not chapter and not episode:
        return ""
    text = f"Ch {chapter.group(1)}" if chapter else ""
    if episode:
        text = f"{text}, Ep {episode.group(1)}" if text else f"Ep {episode.group(1)}"
    return text


def ensure_covers_blocks(text: str) -> str:
    """Guarantee a [covers X-Y] source-span line after every three passages.

    rules.py asks the model to write them, labelled with the event names; this
    is the deterministic backstop and it only fires when the model wrote none,
    so a labelled set is never clobbered. When it does fire, each block lists
    the distinct chapter/episode spans the three passages already carry, so the
    locators are the real ones, never invented. A passage is a non-blank line
    that is neither a marker nor a section heading nor the title line.
    """
    if re.search(r"^\s*\[covers ", text, re.M):
        return text
    lines = text.splitlines()
    passages = [
        i for i, line in enumerate(lines)
        if line.strip() and not re.match(r"^\s*(\[covers |·|\*)", line.strip())
    ]
    passage_set = set(passages)
    out: list[str] = []
    number = 0
    for i, line in enumerate(lines):
        out.append(line)
        if i in passage_set:
            number += 1
            if number % 3 == 0:
                tags: list[str] = []
                for gi in passages[number - 3:number]:
                    for tag in _passage_tags(lines[gi]):
                        compact = _compact_tag(tag)
                        if compact and compact not in tags:
                            tags.append(compact)
                body = " · ".join(tags) if tags else "no locator in these three passages"
                out.append(f"[covers {number - 2}-{number}] {body}")
    return "\n".join(out)


def expand_script(
    text: str,
    target_words: int,
    bundle: dict[str, Any],
    settings: Settings | None = None,
) -> str:
    """One pass at closing the length shortfall, outputting only the delta.

    The contract is a band (target +/- LENGTH_TOLERANCE), so the prompt states
    the exact shortfall and demands the full target, not "a bit more": a model
    told "add some detail" adds a paragraph; one told it is 3,000 words short
    of a 6,000-word script adds sections. New words come from the same bundle
    with the same bans as the draft.

    The model outputs ONLY the sections it is adding, which are appended
    verbatim by the loop: a pass that wrote the whole script back out would
    cost as many tokens as the draft itself, and a 6,000-word script would
    take ten minutes of iterating the full text. A model that restates the
    whole script anyway is detected in the loop by its title line and treated
    as a replacement, never silently duplicated.
    """
    settings = settings or get_settings()
    now = word_count(text)
    low = target_words - LENGTH_TOLERANCE
    high = target_words + LENGTH_TOLERANCE
    shortfall = max(0, low - now)
    prompt = (
        f"The script below is {now} words; the target is {target_words} words "
        f"(the final script must end between {low} and {high} words). You must "
        f"add at least {shortfall} words of new sections: scenes, detail and "
        "explanation from the researched context.\n\n"
        "Rules: never state a fact the context does not carry; do not invent "
        "chapter, episode or page numbers; new sections use the same spoken, "
        "not written, voice; do not repeat what the script already says.\n\n"
        "Output ONLY the new sections, in the script's own format: each as a "
        "bold heading line `* **Heading**` followed by prose. Do not output "
        "the existing script and do not restate its title; the sections you "
        "output will be appended verbatim.\n\n"
        f"--- script so far ---\n{text}"
    )
    return strip_fence(_complete(prompt, settings, temperature=0.7))


def trim_script(
    text: str,
    target_words: int,
    bundle: dict[str, Any],
    settings: Settings | None = None,
) -> str:
    """One pass at cutting an overshoot, outputting only what to delete.

    The model names the sections to drop; `cut_sections` deletes them by
    heading, so a trim pass costs a handful of tokens instead of a full
    rewrite. The remaining tags stay put and `verify_script` still guards them
    afterwards. If the model disobeys and writes a script back, that output is
    taken as the trimmed script, so a bad answer never silently drops content.
    """
    settings = settings or get_settings()
    now = word_count(text)
    low = target_words - LENGTH_TOLERANCE
    high = target_words + LENGTH_TOLERANCE
    excess = max(0, now - high)
    prompt = (
        f"The script below is {now} words; the target is {target_words} words "
        f"(it must end between {low} and {high} words). You are {excess} words "
        f"over. Pick the least essential sections and output ONLY their "
        "heading lines, exactly as written in the script, one per line, e.g. "
        "`* **The Wheel**`. Remove enough sections to cut at least "
        f"{excess} words; if in doubt, remove more. Do not output the script "
        "or anything but heading lines.\n\n"
        f"--- script to trim ---\n{text}"
    )
    answer = strip_fence(_complete(prompt, settings, temperature=0.2))
    lines = [line.strip() for line in answer.splitlines() if line.strip()]
    if lines and all(line.startswith("* **") for line in lines):
        return cut_sections(text, lines)
    return answer


def cut_sections(text: str, headings: list[str]) -> str:
    """Delete the named sections from a script, keeping everything else.

    A section runs from its bold heading line to the next one (or the end of
    the script). Unknown headings are ignored, so a model naming a section
    slightly differently only fails to delete that one section; the prose is
    never damaged by a near-miss.
    """
    wanted = {h.strip() for h in headings if h.strip()}
    if not wanted:
        return text
    out: list[str] = []
    skipping = False
    for line in text.splitlines():
        stripped = line.strip()
        if skipping and stripped.startswith("* **"):
            skipping = False
        if stripped in wanted:
            skipping = True
            continue
        if not skipping:
            out.append(line)
    return "\n".join(out).strip()


def repair_script(
    text: str,
    report: dict[str, Any],
    bundle: dict[str, Any],
    settings: Settings | None = None,
) -> str:
    """Fix the failing tags in a script, keeping the prose untouched.

    `verify_script` fails a tag, never a sentence: a wrong chapter number is a
    confident wrong fact, and the only sanctioned numbers are the ones the
    bundle states. The prompt shows the findings and the bundle's `sourced:`
    spans, which is exactly what the writer is allowed to tag with.
    """
    settings = settings or get_settings()
    findings = "\n".join(
        f"- {finding['tag']}: {'; '.join(finding['issues'])}"
        for finding in report["findings"]
    )
    sources = "\n".join(
        f"  {beat.get('title', '')} [{beat.get('doc_title', '')}]: "
        f"{beat.get('source_span', 'no locator')}"
        for beat in bundle.get("beats", [])
    )
    if not sources:
        sources = "\n  (no beats carried locators in this bundle)"
    prompt = (
        "A script's chapter/episode tags were checked against the wiki and "
        "these failed:\n"
        f"{findings}\n\n"
        "The only numbers you may use are these, from the researched context:\n"
        f"{sources}\n\n"
        "Fix ONLY the failing tags: replace each wrong number with one stated "
        "above, or remove the tag from that line when no number covers it. "
        "Keep every word of the prose unchanged. Output the full corrected "
        "script markdown and nothing else.\n\n"
        "--- script to fix ---\n"
        f"{text}"
    )
    return strip_fence(_complete(prompt, settings, temperature=0.2))


def generate_script(
    subject: str,
    series: str = "jjk",
    words: int = 6000,
    intro: bool = True,
    mode: str = "auto",
    token_budget: int = 0,
    max_attempts: int = MAX_REPAIR_ATTEMPTS,
    write: bool = True,
    title: str | None = None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """The whole loop: bundle -> draft -> length passes -> verify -> repair -> save.

    Mirrors `/context`'s own decisions (auto routing, the roster-empty
    fallback) with one exception: a bare name that the router would answer as
    a lookup becomes narrative here, because a script on that name is a story
    (`route_script`). The draft is pushed toward the length band by whichever
    pass the band needs -- expand while under the low edge, trim while over the
    high edge -- until it lands inside or the pass budget is spent; tags are
    the hard gate, so verification and repair run after the length passes.

    The saved title defaults to the subject so a regenerate reuses the video's
    folder instead of spawning a new one next to it (`script_destination`
    reuses by exact title); pass `title` to save under a different name. The
    script's own title line is normalised to that title so the file's contents
    agree with its name. Returns the script, where it went, the final
    verification report and the length facts; `write=False` returns the same
    without touching disk.
    """
    settings = settings or get_settings()
    paths = series_paths(series, settings)
    if not paths.facts_db.exists():
        raise ValueError(
            f"Series {series!r} is not indexed. Run: "
            f"python -m scriptengine.cli index --series {series}"
        )

    asked = mode
    routed = None
    if mode == "auto":
        mode, routed = route_script(paths, subject, settings)

    budget = token_budget or auto_budget(words)
    bundle = build_context(
        paths, subject, mode=mode, token_budget=budget, top_k=TOP_K
    )
    if mode == "roster" and not bundle.get("members") and asked == "auto":
        bundle = build_context(
            paths, subject, mode="narrative", token_budget=budget, top_k=TOP_K
        )
    # A relations bundle with no rows is not an answer (a pair the wiki never
    # recorded): fall back to the qa passage search. Auto-gated, matching the
    # local roster block (council_r5 amendment A4).
    if mode == "relations" and not bundle.get("relations") and asked == "auto":
        bundle = build_context(
            paths, subject, mode="qa", token_budget=budget, top_k=TOP_K
        )
    if routed is not None:
        bundle["routed"] = routed.as_dict()

    text = write_script(bundle, settings, words=words, intro=intro)
    expanded = trimmed = False
    passes = 0
    if words:
        while passes < MAX_LENGTH_PASSES:
            count = word_count(text)
            if count < words - LENGTH_TOLERANCE:
                addition = expand_script(text, words, bundle, settings)
                expanded = True
                # An expansion must return only new sections. A model that
                # restates the whole script announces it by repeating the
                # title line; treat that as a replacement instead of
                # duplicating the script under itself.
                if title_of(addition) and title_of(addition) == title_of(text):
                    text = addition
                else:
                    text = f"{text.strip()}\n\n{addition.strip()}"
            elif count > words + LENGTH_TOLERANCE:
                text = trim_script(text, words, bundle, settings)
                trimmed = True
            else:
                break
            passes += 1
    report = verify_script(text, paths)
    attempts = 1
    while not report["passed"] and attempts < max_attempts:
        text = repair_script(text, report, bundle, settings)
        report = verify_script(text, paths)
        attempts += 1

    # The video's title is the topic the user asked for, not the entity the
    # engine resolved it to: "Every Fight Mahoraga Has Ever Been In" is a
    # folder name, `Eight-Handled Sword Divergent Sila Divine General
    # Mahoraga` is not. The bundle's resolved subject would rename the video
    # on every regenerate; the user's own subject is the one that stays.
    saved_title = title or subject
    text = _apply_title(text, saved_title)
    prose_words = word_count(text)
    text = ensure_covers_blocks(text)
    clean = make_clean_version(text)
    path = None
    clean_path = None
    if write:
        path = script_destination(saved_title, settings)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n", encoding="utf-8")
        clean_path = path.with_name(path.stem + "-clean.md")
        clean_path.write_text(clean, encoding="utf-8")

    return {
        "script": text,
        "title": saved_title,
        "path": path,
        "clean_script": clean,
        "clean_path": clean_path,
        "bundle": bundle,
        "report": report,
        "attempts": attempts,
        "words": prose_words,
        "target_words": words,
        "expanded": expanded,
        "trimmed": trimmed,
        "length_passes": passes,
    }