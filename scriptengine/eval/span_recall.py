"""Line-level reachability: is every sentence in the corpus retrievable?

The gold question bank samples. At the prose pass's calibrated density it asks
about roughly one line in eight, which is excellent regression protection and
an expensive way to *discover* anything -- the whole campaign's hand-authored
bank has averaged one engine finding per few hundred questions written. It also
cannot, arithmetically, deliver the standing mandate of "down to a single line"
at a million words a series.

This module covers the complement mechanically, with no authoring, in two
tiers:

``index_coverage`` (tier 0)
    Is each sentence present, whole, inside some chunk? Pure SQLite, no server,
    a fraction of a second for a whole series. A miss is an indexing or
    chunking defect: the line is invisible to retrieval no matter what anyone
    asks. This is the family the campaign has repeatedly found by hand --
    colon truncation, the gallery body strip, the Trivia chunking gap.

``recall`` (tier 1)
    Does ``/context`` actually serve the line back? Needs the live server, so
    it is sampled rather than exhaustive.

The two tiers report separately on purpose. A tier 0 miss and a tier 1 miss
have different causes and different fixes, and a single blended number would
hide both.
"""

from __future__ import annotations

import json
import random
import re
import time
import unicodedata
import urllib.request
from pathlib import Path
from typing import Any, Callable

from scriptengine.config import Settings
from scriptengine.stores.facts import FactStore

BASE = "http://127.0.0.1:8000"

# Sentence boundaries the wiki's own prose style breaks. Splitting on
# `(?<=[.!?])\s+` alone silently welds sentences together, because the corpus
# hangs its citations directly off the full stop with no space:
# "...into a cliff.(Chapter 151) He thinks...". On the JJK corpus that single
# oversight hid roughly five thousand sentences inside their neighbours.
_SENT_END = re.compile(r'[.!?]["\')\]]*(?:\([^()]{1,80}\))*\s+')

ABBREV = frozenset({
    "mr", "mrs", "ms", "dr", "st", "vs", "jr", "sr", "prof", "lt", "capt",
    "no", "vol", "ch", "ep", "approx", "etc", "inc", "ltd", "co",
})

# The section store and the served beats do not render citations identically:
# a section says "(Chapter 143)" where the beat says "(Chapter 143, Episode
# 49)". Comparing raw text therefore fails on the citation rather than on the
# prose -- measured at 71% of apparent span-misses against under 10% of hits.
# Both sides are stripped before comparison so the test measures what it says.
_CITE = re.compile(
    r"\((?:Chapter|Episode|Volume|Fanbook|Modulo|Movie|OVA|Novel|Databook)"
    r"[^()]*\)"
)

# Link-list scaffolding the indexer leaves out on purpose: interwiki name
# lists, see-alsos, external links. A miss inside one is correct behaviour, and
# counting them buries real findings -- on JJK they alone moved the headline
# from 99.9959% to 99.875%. `References` is deliberately absent: on chapter
# pages it carries real trivia prose, and that is where a genuine gap surfaced.
BOILERPLATE = frozenset({
    "navigation", "site navigation", "see also", "external links",
    "external link", "navigation boxes",
})


class SpanRecallError(RuntimeError):
    """The run could not be trusted -- not merely a low score."""


def norm(text: str) -> str:
    """Whitespace- and unicode-normalised, for substring comparison only.

    Case is deliberately preserved: this engine's contract is verbatim text,
    so a case difference between the section store and the chunk store is a
    defect worth seeing rather than something to normalise away.
    """
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()


def decite(text: str) -> str:
    """Drop inline citation markers so prose is compared against prose."""
    return re.sub(r"\s+", " ", _CITE.sub("", text)).strip()


def is_boilerplate(breadcrumb: str | None) -> bool:
    return (breadcrumb or "").strip().lower() in BOILERPLATE


def sentences(text: str, min_words: int = 6) -> list[str]:
    """Split into sentences, keeping trailing citations with their sentence.

    Boundaries are found rather than split on, so a citation hanging off a full
    stop stays attached to the sentence it cites. A boundary landing on a known
    abbreviation is not a boundary.

    Fragments and table rows are dropped: a three-word line carries too little
    signal to query with, and a pipe-delimited row is not prose. Both would
    yield false alarms rather than findings.
    """
    flat = norm(text)
    out: list[str] = []
    start = 0
    for match in _SENT_END.finditer(flat):
        candidate = flat[start:match.end()].strip()
        tail = candidate.rstrip(".\"')]").split()
        last = tail[-1].lower().rstrip(".") if tail else ""
        if last in ABBREV:
            continue
        out.append(candidate)
        start = match.end()
    if start < len(flat):
        out.append(flat[start:].strip())
    return [s for s in out if len(s.split()) >= min_words and s.count("|") < 3]


def _facts_path(series: str, settings: Settings | None = None) -> Path:
    settings = settings or Settings()
    return Path(settings.series_root) / series / "facts.db"


def _corpus(series: str, settings: Settings | None = None):
    """Documents, their non-empty sections, and their chunks."""
    path = _facts_path(series, settings)
    if not path.exists():
        raise SpanRecallError(
            f"No index for series {series!r} at {path}. Run `index` first."
        )
    with FactStore(path) as store:
        con = store.connection
        docs = {
            row["id"]: (row["title"], row["url"])
            for row in con.execute("SELECT id, title, url FROM documents")
        }
        secs = [
            (row["document_id"], row["breadcrumb"], row["text"])
            for row in con.execute(
                "SELECT document_id, breadcrumb, text FROM sections "
                "WHERE COALESCE(text,'') <> '' ORDER BY document_id, ordinal"
            )
        ]
        chunks: dict[int, list[str]] = {}
        for row in con.execute(
            "SELECT document_id, text FROM chunks WHERE COALESCE(text,'') <> ''"
        ):
            chunks.setdefault(row["document_id"], []).append(norm(row["text"]))
    return docs, secs, chunks


def index_coverage(series: str, settings: Settings | None = None,
                   min_words: int = 6,
                   include_boilerplate: bool = False) -> dict[str, Any]:
    """Tier 0: every sentence, is it whole inside some chunk of its document?

    Offline and exhaustive. Cheap enough to run after every re-index, which is
    the point -- it is the only check here that covers the whole corpus rather
    than a sample.
    """
    docs, secs, chunks = _corpus(series, settings)
    misses: list[dict[str, Any]] = []
    counted = skipped = 0
    started = time.time()

    for doc_id, breadcrumb, text in secs:
        boiler = is_boilerplate(breadcrumb)
        if boiler and not include_boilerplate:
            skipped += len(sentences(text, min_words))
            continue
        doc_chunks = chunks.get(doc_id, [])
        for sentence in sentences(text, min_words):
            counted += 1
            if not any(sentence in chunk for chunk in doc_chunks):
                title, url = docs.get(doc_id, ("?", ""))
                misses.append({
                    "doc_id": doc_id, "title": title, "url": url,
                    "breadcrumb": breadcrumb, "sentence": sentence,
                    "words": len(sentence.split()),
                    "boilerplate": boiler,
                    "doc_has_chunks": bool(doc_chunks),
                })

    return {
        "series": series,
        "sections": len(secs),
        "sentences": counted,
        "covered": counted - len(misses),
        "missing": len(misses),
        "coverage": (counted - len(misses)) / counted if counted else 1.0,
        "boilerplate_skipped": skipped,
        "elapsed": time.time() - started,
        "misses": misses,
    }


def _ask(query: str, series: str, timeout: float,
         base: str = BASE) -> dict[str, Any]:
    body = json.dumps({"series": series, "query": query}).encode()
    request = urllib.request.Request(
        f"{base}/context", data=body,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read())


def served_text(bundle: dict[str, Any]) -> str:
    """Everything the caller actually receives, flattened for the substring test."""
    parts: list[str] = []
    for key in ("beats", "facts", "relations", "participants"):
        value = bundle.get(key)
        if not isinstance(value, list):
            continue
        for item in value:
            if isinstance(item, dict):
                parts.extend(v for v in item.values() if isinstance(v, str))
            elif isinstance(item, str):
                parts.append(item)
    return norm(" \n ".join(parts))


def make_query(sentence: str, mode: str, title: str | None = None) -> str:
    """`verbatim` is the reachability floor; the others isolate one variable.

    `scoped` is the control for this corpus's redundancy -- a wiki narrates the
    same event on the chapter page, the episode page, the character synopsis
    and the battle page, so a bare sentence is genuinely ambiguous about which
    page is wanted. Naming the page separates "cannot find this line" from
    "found the event, picked a sibling page".
    """
    if mode == "scoped":
        return f"{title}: {sentence}" if title else sentence
    if mode == "verbatim":
        return sentence
    keep = [t for t in re.findall(r"[A-Za-z0-9'\-]+", sentence)
            if t.lower() not in _STOP]
    return " ".join(keep[:18]) or sentence


_STOP = frozenset("""a an the of in on at to for with by from as is are was were be been
being and or but if then than that this these those it its his her their our your my he
she they we you i had has have do does did not no so such very can could will would shall
should may might must who whom whose which what when where why how there here also into
out up down over under after before""".split())


def recall(series: str, settings: Settings | None = None, mode: str = "verbatim",
           sample: int = 400, every: int | None = None, seed: int = 7,
           timeout: float = 120.0, min_words: int = 6, base: str = BASE,
           done: set[str] | None = None,
           on_row: Callable[[dict[str, Any]], None] | None = None,
           on_progress: Callable[[int, int, dict[str, int]], None] | None = None,
           ) -> dict[str, Any]:
    """Tier 1: does the served bundle actually contain the line?

    Verdicts are split so a number is actionable. ``MISS_DOC`` (the line's own
    page never reached the bundle) is a ranking problem; ``MISS_SPAN`` (the page
    came back without the line) is chunk selection inside the document. Lumping
    them produces a figure nobody can act on.

    Only sentences tier 0 has already cleared are probed -- otherwise an
    indexing gap would be counted twice, once in each tier.
    """
    docs, secs, chunks = _corpus(series, settings)
    probes: list[tuple[str, str, str]] = []
    for doc_id, breadcrumb, text in secs:
        if is_boilerplate(breadcrumb):
            continue
        doc_chunks = chunks.get(doc_id, [])
        title = docs.get(doc_id, ("?", ""))[0]
        for sentence in sentences(text, min_words):
            if any(sentence in chunk for chunk in doc_chunks):
                probes.append((title, breadcrumb, sentence))

    random.Random(seed).shuffle(probes)
    if sample:
        probes = probes[:sample]

    done = done or set()
    counts = {"HIT": 0, "MISS_DOC": 0, "MISS_SPAN": 0, "TRUNCATED": 0, "ERROR": 0}
    rows: list[dict[str, Any]] = []
    started = time.time()

    for index, (title, breadcrumb, sentence) in enumerate(probes, 1):
        if sentence in done:
            continue
        query = make_query(sentence, mode, title)
        returned: list[str] = []
        error = None
        bundle: dict[str, Any] = {}
        try:
            bundle = _ask(query, series, timeout, base)
            text = served_text(bundle)
            returned = [b.get("doc_title") for b in bundle.get("beats", [])
                        if isinstance(b, dict)]
            if sentence in text or decite(sentence) in decite(text):
                verdict = "HIT"
            elif bundle.get("truncated"):
                verdict = "TRUNCATED"
            elif title not in returned:
                verdict = "MISS_DOC"
            else:
                verdict = "MISS_SPAN"
        except Exception as exc:  # a probe failing must not end the sweep
            verdict, error = "ERROR", str(exc)[:200]

        counts[verdict] += 1
        row = {
            "verdict": verdict, "title": title, "breadcrumb": breadcrumb,
            "query": query, "sentence": sentence,
            "mode_routed": bundle.get("mode"),
            "truncated": bundle.get("truncated"),
            "returned_docs": returned[:8], "error": error,
        }
        rows.append(row)
        if on_row:
            on_row(row)
        if on_progress and every and index % every == 0:
            on_progress(index, len(probes), counts)

    total = sum(counts.values())
    return {
        "series": series, "mode": mode, "probes": total,
        "counts": counts,
        "hit_rate": counts["HIT"] / total if total else 1.0,
        "elapsed": time.time() - started,
        "rows": rows,
    }
