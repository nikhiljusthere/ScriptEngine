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
   agrees — the `anime episode` field on the chapter page, or `adapted from` on
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

# "(Chapter 118, Episode 41)", "(Modulo Chapter 16)", "(Manga Episode 137)".
TAG = re.compile(
    r"\((?:([A-Z][A-Za-z']*)\s+)?Chapter\s+([\d.\-]+)(?:,\s*Episode\s+([\d.\-]+))?\)"
    r"|\((?:([A-Z][A-Za-z']*)\s+)?Episode\s+([\d.\-]+)\)"
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

        facts = {f["key"]: f["value"] for f in page.get("facts", [])}
        if page.get("page_type") == "chapter" and "anime episode" in facts:
            for episode in re.findall(r"Episode\s+([\d.\-]+)", facts["anime episode"]):
                adapted[page["title"]].add(episode)
        if page.get("page_type") == "episode" and "adapted from" in facts:
            number = re.search(r"([\d.\-]+)", page["title"])
            for chapter in re.findall(r"Chapter\s+([\d.\-]+)", facts["adapted from"]):
                if number:
                    adapted.setdefault(f"Chapter {chapter}", set()).add(number.group(1))

    return {"titles": titles, "cited": cited, "paired": paired, "adapted": adapted}


def verify_script(text: str, paths: SeriesPaths) -> dict[str, Any]:
    """Check every tag in `text`. Returns the findings, worst first."""
    corpus = _load(paths)
    findings: list[dict[str, Any]] = []
    seen: set[str] = set()

    for match in TAG.finditer(text):
        tag = match.group(0)
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
        if page not in corpus["titles"]:
            issues.append(f"no page {page!r} in the crawl")
        if (work, number) not in corpus["cited"]:
            issues.append(f"no reference in the corpus cites {page}")

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
