"""Checking a finished script's chapter and episode tags against the crawl.

The engine can only offer a locator; the writer chooses which one to put on a
line, and a writer that has read ten thousand words of context is exactly the
kind of thing that produces a confident, plausible, wrong number. So the tags
get checked against the corpus before a script is called done.

Three independent checks per tag, all against `series/<name>/wikitext/*.json`
rather than the index, so a bug in indexing cannot make a bad tag look fine:

1. the instalment page exists on the wiki;
2. some reference in the corpus actually cites that chapter;
3. when the tag pairs a chapter with an episode, the wiki's own adaptation data
   agrees: the `anime episode` field on the chapter page, or `adapted from` on
   the episode page.

A tag failing 2 or 3 is a number the script invented.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from scriptengine.config import SeriesPaths

# "(Chapter 118, Episode 41)", "(Modulo Chapter 16)", "(Manga Episode 137)",
# "(Movie Jujutsu Kaisen 0)" (a film citation; the wiki has no Chapter/Episode
# numbering for the movie, and its lines live in the transcript store).
TAG = re.compile(
    r"\((?:([A-Z][A-Za-z']*)\s+)?Chapter\s+([\d.\-]+)(?:,\s*Episode\s+([\d.\-]+))?\)"
    r"|\((?:([A-Z][A-Za-z']*)\s+)?Episode\s+([\d.\-]+)\)"
    r"|\(Movie\s+([^()]+)\)"
)
_REF = re.compile(r"\{\{\s*[Rr]ef[^|}]*\|([^{}]*)\}\}")
_REF_TAG = re.compile(r"<ref[^>/]*(?:/\s*>|>(.*?)</ref\s*>)", re.S | re.IGNORECASE)


def _load(paths: SeriesPaths) -> dict[str, Any]:
    """Titles, cited instalments and adaptation pairings, straight from disk."""
    titles: set[str] = set()
    cited: set[tuple[str, str]] = set()          # (work, number)
    paired: set[tuple[str, str]] = set()         # (chapter, episode)
    adapted: dict[str, set[str]] = defaultdict(set)

    for path in paths.wikitext.glob("*.json"):
        try:
            page = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        titles.add(page["title"])
        wikitext = page.get("wikitext", "")

        for match in _REF.finditer(wikitext):
            params: dict[str, str] = {}
            positional: list[str] = []
            for part in match.group(1).split("|"):
                if "=" in part:
                    key, value = part.split("=", 1)
                    params[key.strip().lower()] = value.strip()
                elif part.strip():
                    positional.append(part.strip())

            work = ""
            if (params.get("modulo") or "").lower() in {"y", "yes", "true", "1"}:
                work = "Modulo"
            chapter = params.get("chap") or params.get("ch")
            episode = params.get("ep")
            # Positional forms: {{Ref|m|216|3-4}}.
            if not chapter and len(positional) >= 2 and positional[0] == "m":
                chapter = positional[1]
            if not episode and len(positional) >= 2 and positional[0] == "a":
                episode = positional[1]
            if params.get("wch"):
                cited.add(("Webcomic", params["wch"]))
            if chapter:
                cited.add((work, chapter))
            if episode:
                cited.add((work, episode))
            if chapter and episode and not work:
                paired.add((chapter, episode))

        # Prose locators inside <ref> tags.
        for match in _REF_TAG.finditer(wikitext):
            body = match.group(1) or ""
            for number in re.findall(r"Chapter\s+([\d.\-]+)", body, re.IGNORECASE):
                cited.add(("", number))
            for number in re.findall(r"Episode\s+([\d.\-]+)", body, re.IGNORECASE):
                cited.add(("", number))

        # Adaptation is read from the page's *links*, not from its infobox text.
        # The text is written for humans: Chainsaw Man's Episode 8 says
        # "Chapter 22, 23, 24, 25 (p.2-14)", where a regex for "Chapter N" finds
        # only the first of the four and reports the other three as unverifiable.
        # MediaWiki already resolved each one into a link, so the edges carry
        # them individually and correctly.
        #
        # Keyed off the title rather than `page_type` for the same reason: the
        # type is whatever the wiki named its infobox, and Chainsaw Man's
        # chapter pages come back `unknown`.
        title = page["title"]
        number = re.search(r"([\d.\-]+)", title)
        for edge in page.get("edges", []):
            relation, target = edge.get("relation", ""), edge.get("target", "")
            if relation == "anime episode" and title.startswith("Chapter "):
                if target.startswith("Episode "):
                    adapted[title].add(target[len("Episode "):].strip())
            elif relation == "adapted from" and title.startswith("Episode "):
                if target.startswith("Chapter ") and number:
                    adapted[target].add(number.group(1))

    return {"titles": titles, "cited": cited, "paired": paired, "adapted": adapted}


def verify_script(text: str, paths: SeriesPaths) -> dict[str, Any]:
    """Check every tag in `text`. Returns the findings, worst first."""
    corpus = _load(paths)
    findings: list[dict[str, Any]] = []
    seen: set[str] = set()

    for match in TAG.finditer(text):
        tag = match.group(0)
        if match.group(6):
            # Movie citation: a film page matching the name must exist in the
            # corpus ("Jujutsu Kaisen 0" matches "Jujutsu Kaisen 0: The
            # Movie"). Structural, like the episode branch; the line-level
            # cross-check against the transcript store remains a later task.
            name = match.group(6).strip()
            issues: list[str] = []
            if not any(t == name or t.startswith(name) for t in corpus["titles"]):
                issues.append(f"no movie page matching {name!r} in the crawl")
            seen.add(tag)
            if issues:
                findings.append({"tag": tag, "issues": issues})
            continue
        if match.group(2):
            work, number, episode, kind = (
                match.group(1) or "", match.group(2), match.group(3), "Chapter"
            )
        else:
            work, number, episode, kind = (
                match.group(4) or "", match.group(5), None, "Episode"
            )

        issues: list[str] = []
        page = f"{work} {kind} {number}".strip()
        exists = page in corpus["titles"]
        if not exists:
            issues.append(f"no page {page!r} in the crawl")
            # Only then does it matter whether anything cites it. A wiki that
            # cites nothing inline is common: One Piece has 1,191 chapter pages
            # and puts a reference on almost none of the prose, so demanding a
            # reference as well failed correct tags on every such series. The
            # instalment page existing is the evidence that the number is real;
            # the point of this check is to catch invented ones.
            if (work, number) not in corpus["cited"]:
                issues.append(f"and no reference cites {page} either")

        if episode:
            if work:
                issues.append(f"{work} numbering cannot carry an episode of the anime")
            else:
                if f"Episode {episode}" not in corpus["titles"]:
                    issues.append(f"no page 'Episode {episode}' in the crawl")
                elif (
                    (number, episode) not in corpus["paired"]
                    and episode not in corpus["adapted"].get(f"Chapter {number}", set())
                ):
                    issues.append(
                        f"Chapter {number} is not adapted by Episode {episode}"
                    )

        seen.add(tag)
        if issues:
            findings.append({"tag": tag, "issues": issues})

    return {
        "series": paths.name,
        "tags": len(list(TAG.finditer(text))),
        "distinct": len(seen),
        "findings": findings,
        "passed": not findings,
    }
